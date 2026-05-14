"""
Identify MNSO quarterly earnings 6-K filings on EDGAR.

Strategy:
- Fetch the 6-K cover HTML (always small) and look for financial keywords
- Candidates are filed in Feb/Mar (Q4/FY), May (Q1), Aug (Q2), Nov (Q3)
- Print identified earnings filings and their exhibits
"""
import re
import time
import requests

HEADERS = {"User-Agent": "FinanceReportDownloader contact@example.com"}
CIK_PADDED = "0001815846"
CIK_RAW = "1815846"

# Keywords that indicate financial results in the 6-K cover text
FINANCIAL_KEYWORDS = [
    "financial results", "unaudited", "quarterly results",
    "fiscal", "revenue", "net income", "net revenue",
    "fourth quarter", "third quarter", "second quarter", "first quarter",
    "full year", "annual results",
]


def _get(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            time.sleep(0.4)
            return r
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise
            time.sleep(2)
        except Exception:
            time.sleep(2)
    raise RuntimeError(f"Failed: {url}")


def get_all_6k_filings():
    data = _get(f"https://data.sec.gov/submissions/CIK{CIK_PADDED}.json").json()
    recent = data["filings"]["recent"]
    rows = list(zip(
        recent["filingDate"],
        recent["form"],
        recent["accessionNumber"],
        recent["size"],
    ))
    for extra in data["filings"].get("files", []):
        extra_data = _get("https://data.sec.gov/submissions/" + extra["name"]).json()
        rows += list(zip(
            extra_data["filingDate"],
            extra_data["form"],
            extra_data["accessionNumber"],
            extra_data["size"],
        ))
    return sorted(
        [(d, a, s) for d, f, a, s in rows if f == "6-K"],
        reverse=True
    )


def get_filing_docs(acc):
    """Return (cover_url, [exhibit_urls]) for a 6-K filing."""
    acc_nodash = acc.replace("-", "")
    idx_url = (
        f"https://www.sec.gov/Archives/edgar/data/{CIK_RAW}"
        f"/{acc_nodash}/{acc}-index.htm"
    )
    r = _get(idx_url)
    files = re.findall(
        r'href="(/Archives/edgar/data/[^"]+\.htm[l]?)"',
        r.text, re.I,
    )
    cover = None
    exhibits = []
    for f in files:
        fname = f.split("/")[-1]
        if "-index.htm" in fname:
            continue
        url = "https://www.sec.gov" + f
        if "_6k.htm" in fname.lower():
            cover = url
        elif "ex99" in fname.lower():
            exhibits.append((fname, url))
    return cover, exhibits


def is_earnings_filing(cover_url):
    """Return True if the 6-K cover page mentions financial results."""
    if not cover_url:
        return False
    r = _get(cover_url)
    text = re.sub(r"<[^>]+>", " ", r.text).lower()
    text = re.sub(r"\s+", " ", text)
    return any(kw in text for kw in FINANCIAL_KEYWORDS)


def main():
    print("Fetching all MNSO 6-K filings…")
    filings = get_all_6k_filings()
    print(f"Total 6-K filings: {len(filings)}\n")

    earnings = []
    for date, acc, size in filings:
        try:
            cover_url, exhibits = get_filing_docs(acc)
            is_earn = is_earnings_filing(cover_url)
            marker = " *** EARNINGS ***" if is_earn else ""
            print(f"{date}  {acc}  size={size:>10,}  exs={len(exhibits)}{marker}")
            if is_earn:
                earnings.append((date, acc, cover_url, exhibits))
        except Exception as e:
            print(f"  ERROR {acc}: {e}")

    print(f"\n{'='*60}")
    print(f"Identified {len(earnings)} earnings 6-K filings:")
    for date, acc, cover, exs in earnings:
        names = [n for n, u in exs]
        print(f"  {date}  {acc}  exhibits={names}")


if __name__ == "__main__":
    main()
