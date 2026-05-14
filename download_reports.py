#!/usr/bin/env python3
"""
Download quarterly (10-Q) and annual (10-K) financial reports from SEC EDGAR
for specified US stock tickers. Reports are saved as HTML files in
subdirectories named after each company ticker.

Usage:
    python download_reports.py
    python download_reports.py --tickers AAPL MSFT GOOG
    python download_reports.py --output-dir ./my_reports
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_TICKERS = ["RDDT", "MNSO", "RKLB", "AMD", "MCD"]
DEFAULT_OUTPUT_DIR = Path("reports")
FILING_TYPES = ["10-Q", "10-K"]          # quarterly + annual reports for domestic filers
# Foreign private issuers file 20-F (annual) instead of 10-K, and 6-K instead of 10-Q
FPI_FILING_TYPES = ["20-F", "6-K"]
FPI_TICKERS = {"MNSO"}                   # tickers known to be foreign private issuers
REQUEST_DELAY = 0.5                       # seconds between EDGAR requests (be polite)

# SEC EDGAR requires a descriptive User-Agent with contact info
HEADERS = {
    "User-Agent": "FinanceReportDownloader contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}

EDGAR_BASE = "https://data.sec.gov"
EDGAR_SUBMISSIONS_URL = EDGAR_BASE + "/submissions/CIK{cik}.json"
EDGAR_FILING_INDEX_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{accession}-index.htm"
EDGAR_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get(url: str, **kwargs) -> requests.Response:
    """Wrapper around requests.get with retries and polite delay."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, **kwargs)
            resp.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return resp
        except requests.HTTPError as exc:
            if exc.response.status_code == 429:
                wait = 10 * (attempt + 1)
                log.warning("Rate limited – waiting %ds before retry…", wait)
                time.sleep(wait)
            elif exc.response.status_code == 404:
                raise
            else:
                log.warning("HTTP %s on attempt %d: %s", exc.response.status_code, attempt + 1, url)
                time.sleep(2)
        except requests.RequestException as exc:
            log.warning("Request error on attempt %d: %s", attempt + 1, exc)
            time.sleep(2)
    raise RuntimeError(f"Failed to fetch {url} after 3 attempts")


def load_company_tickers() -> Dict[str, str]:
    """Return a mapping of UPPER-CASE ticker -> zero-padded 10-digit CIK string."""
    log.info("Loading company ticker ↔ CIK mapping from SEC EDGAR…")
    data = _get(EDGAR_COMPANY_TICKERS_URL).json()
    ticker_to_cik: Dict[str, str] = {}
    for entry in data.values():
        ticker = entry["ticker"].upper()
        cik = str(entry["cik_str"]).zfill(10)
        ticker_to_cik[ticker] = cik
    return ticker_to_cik


def get_all_filings(cik: str, filing_types: List[str]) -> List[dict]:
    """
    Retrieve all filings of the given types for a company from EDGAR submissions API.
    Handles paginated /submissions/CIK{cik}.json responses.
    """
    url = EDGAR_SUBMISSIONS_URL.format(cik=cik)
    data = _get(url).json()

    filings: List[dict] = []
    company_name = data.get("name", cik)

    def _extract(filings_block: dict) -> None:
        form_list = filings_block.get("form", [])
        acc_list  = filings_block.get("accessionNumber", [])
        date_list = filings_block.get("filingDate", [])
        pdoc_list = filings_block.get("primaryDocument", [])
        for form, acc, date, pdoc in zip(form_list, acc_list, date_list, pdoc_list):
            if form in filing_types:
                filings.append({"form": form, "accession": acc, "date": date, "primaryDocument": pdoc})

    _extract(data.get("filings", {}).get("recent", {}))

    # EDGAR may paginate older filings into separate JSON files
    for extra_file in data.get("filings", {}).get("files", []):
        extra_url = EDGAR_BASE + "/submissions/" + extra_file["name"]
        try:
            extra_data = _get(extra_url).json()
            _extract(extra_data)
        except Exception as exc:
            log.warning("Could not fetch extra filings file %s: %s", extra_url, exc)

    log.info("  Found %d %s filings for %s (%s)", len(filings), "/".join(filing_types), company_name, cik)
    return filings


def find_primary_html_document(cik: str, accession: str, primary_doc: str = "") -> Optional[str]:
    """
    Return URL of the primary HTML document for a filing.
    Uses primaryDocument from the submissions JSON when available;
    otherwise scrapes the filing index .htm page.
    """
    accession_nodash = accession.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_nodash}/"

    # Fast path: primaryDocument field supplied by submissions API
    if primary_doc and primary_doc.lower().endswith((".htm", ".html")):
        return base + primary_doc

    # Fallback: scrape the human-readable index page
    index_url = base + accession + "-index.htm"
    try:
        text = _get(index_url).text
    except Exception:
        return None

    for line in text.splitlines():
        ls = line.strip()
        lo = ls.lower()
        if not lo.endswith((".htm", ".html")):
            continue
        if any(x in lo for x in ["ex-", "exhibit", "ex99", "ex 9"]):
            continue
        for tok in ls.split():
            if tok.lower().endswith((".htm", ".html")):
                return base + tok
    return None


def download_filing_html(url: str) -> bytes:
    """Download the raw HTML bytes of a filing document."""
    resp = _get(url)
    return resp.content


def save_report(ticker: str, form: str, date: str, html_bytes: bytes, output_dir: Path) -> Path:
    """Save report HTML to <output_dir>/<TICKER>/<FORM>_<DATE>.html."""
    company_dir = output_dir / ticker.upper()
    company_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{form}_{date}.html"
    filepath = company_dir / filename
    filepath.write_bytes(html_bytes)
    return filepath


# ---------------------------------------------------------------------------
# Main download routine
# ---------------------------------------------------------------------------

def download_reports_for_ticker(
    ticker: str,
    cik: str,
    output_dir: Path,
    filing_types: List[str],
    skip_existing: bool = True,
) -> None:
    """Download all historical reports for one ticker."""
    log.info("── Processing %s (CIK %s) ──", ticker.upper(), cik)
    filings = get_all_filings(cik, filing_types)

    if not filings:
        log.warning("No filings found for %s", ticker)
        return

    for filing in filings:
        form = filing["form"]
        date = filing["date"]
        accession = filing["accession"]

        out_path = output_dir / ticker.upper() / f"{form}_{date}.html"
        if skip_existing and out_path.exists():
            log.debug("  Skipping %s %s (already downloaded)", form, date)
            continue

        log.info("  Downloading %s %s (%s)…", form, date, accession)
        try:
            html_url = find_primary_html_document(cik, accession, filing.get("primaryDocument", ""))
            if html_url is None:
                log.warning("    Could not locate HTML document for %s %s", form, date)
                continue
            html_bytes = download_filing_html(html_url)
            saved = save_report(ticker, form, date, html_bytes, output_dir)
            log.info("    Saved → %s", saved)
        except Exception as exc:
            log.error("    Error downloading %s %s: %s", form, date, exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download SEC EDGAR quarterly/annual reports as HTML")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=DEFAULT_TICKERS,
        metavar="TICKER",
        help=f"List of tickers to download (default: {' '.join(DEFAULT_TICKERS)})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        metavar="DIR",
        help=f"Root output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--filing-types",
        nargs="+",
        default=FILING_TYPES,
        metavar="TYPE",
        help=f"Filing types to download (default: {' '.join(FILING_TYPES)})",
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Re-download files even if they already exist",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info("Output directory: %s", output_dir.resolve())

    # Build ticker → CIK mapping
    try:
        ticker_to_cik = load_company_tickers()
    except Exception as exc:
        log.error("Failed to load ticker/CIK mapping: %s", exc)
        return

    tickers = [t.upper() for t in args.tickers]
    not_found = [t for t in tickers if t not in ticker_to_cik]
    if not_found:
        log.warning("Tickers not found in EDGAR: %s", ", ".join(not_found))

    for ticker in tickers:
        cik = ticker_to_cik.get(ticker)
        if cik is None:
            log.error("Skipping %s – no CIK found", ticker)
            continue
        try:
            # Foreign private issuers file 20-F/6-K instead of 10-K/10-Q
            effective_types = FPI_FILING_TYPES if ticker in FPI_TICKERS else args.filing_types
            download_reports_for_ticker(
                ticker=ticker,
                cik=cik,
                output_dir=output_dir,
                filing_types=effective_types,
                skip_existing=not args.no_skip,
            )
        except Exception as exc:
            log.error("Unexpected error processing %s: %s", ticker, exc)

    log.info("Done.")


if __name__ == "__main__":
    main()
