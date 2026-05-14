#!/usr/bin/env python3
"""
Download MNSO quarterly/annual earnings 6-K filings from SEC EDGAR.

MNSO is a Chinese company listed in the US as a Foreign Private Issuer.
It files 6-K (not 10-Q/10-K) reports. Each earnings 6-K contains multiple
HTML exhibits (ex99-1, ex99-2, …) with the actual financial statements.

The list of earnings filings was identified by keyword-matching the 6-K
cover pages for financial result terms across all 211 MNSO 6-K filings.
"""

import logging
import re
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("reports/MNSO")
REQUEST_DELAY = 0.5
HEADERS = {"User-Agent": "FinanceReportDownloader contact@example.com"}
CIK = "1815846"

# Earnings 6-K filings identified by probe_mnso.py (date, accession)
EARNINGS_FILINGS = [
    ("2026-04-01", "0001104659-26-038269"),   # FY2025 annual
    ("2026-03-13", "0001104659-26-027395"),   # Q4 FY2025 supplemental
    ("2025-11-24", "0001104659-25-115178"),   # Q3 FY2025
    ("2025-08-22", "0001104659-25-081665"),   # Q2 FY2025
    ("2025-05-23", "0001104659-25-052246"),   # Q1 FY2025
    ("2025-03-24", "0001104659-25-026880"),   # FY2024 annual
    ("2024-12-02", "0001104659-24-124322"),   # Q3 FY2024
    ("2024-08-30", "0001104659-24-095717"),   # Q2 FY2024
    ("2024-05-14", "0001104659-24-060795"),   # Q1 FY2024
    ("2024-03-12", "0001104659-24-033279"),   # FY2023 annual
    ("2024-01-17", "0001104659-24-004238"),   # Q3 FY2023
    ("2023-11-22", "0001104659-23-120504"),   # Q3 FY2023 (supplemental)
    ("2023-09-15", "0001104659-23-100972"),   # Q2 FY2023
    ("2023-08-23", "0001104659-23-094370"),   # Q2 FY2023 supplemental
    ("2023-05-16", "0001104659-23-061112"),   # Q1 FY2023
    ("2023-02-28", "0001104659-23-026346"),   # FY2022 annual
    ("2022-11-15", "0001104659-22-118985"),   # Q3 FY2022
    ("2022-09-29", "0001104659-22-103891"),   # Q2 FY2022
    ("2022-08-25", "0001104659-22-094242"),   # Q1 FY2022 / Q2
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _get(url: str) -> requests.Response:
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return r
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(10 * (attempt + 1))
            elif e.response.status_code == 404:
                raise
            else:
                time.sleep(2)
        except requests.RequestException:
            time.sleep(2)
    raise RuntimeError(f"Failed to fetch {url}")


def get_exhibit_urls(acc: str) -> list[tuple[str, str]]:
    """Return list of (exhibit_name, url) for all ex99-* HTM files."""
    acc_nodash = acc.replace("-", "")
    idx_url = (
        f"https://www.sec.gov/Archives/edgar/data/{CIK}"
        f"/{acc_nodash}/{acc}-index.htm"
    )
    r = _get(idx_url)
    files = re.findall(
        r'href="(/Archives/edgar/data/[^"]+\.htm[l]?)"',
        r.text, re.I,
    )
    result = []
    for f in files:
        fname = f.split("/")[-1]
        if "ex99" in fname.lower():
            # Extract exhibit number for clean naming
            m = re.search(r"ex99-(\d+)", fname, re.I)
            ex_num = m.group(1) if m else "1"
            result.append((ex_num, f"https://www.sec.gov{f}"))
    return result


def download_mnso(skip_existing: bool = True) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Downloading MNSO earnings 6-K reports → %s", OUTPUT_DIR.resolve())

    for date, acc in EARNINGS_FILINGS:
        log.info("── %s (%s) ──", date, acc)
        try:
            exhibits = get_exhibit_urls(acc)
        except Exception as e:
            log.error("  Could not get exhibit list: %s", e)
            continue

        if not exhibits:
            log.warning("  No ex99-* exhibits found")
            continue

        for ex_num, url in exhibits:
            out_path = OUTPUT_DIR / f"6-K_{date}_ex{ex_num}.html"
            if skip_existing and out_path.exists():
                log.debug("  Skipping %s (already exists)", out_path.name)
                continue
            try:
                log.info("  Downloading exhibit %s…", ex_num)
                content = _get(url).content
                out_path.write_bytes(content)
                log.info("    Saved → %s", out_path)
            except Exception as e:
                log.error("    Error: %s", e)

    log.info("Done.")


if __name__ == "__main__":
    download_mnso()
