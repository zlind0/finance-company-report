"""
Extract key financial data from MNSO HTML reports for analysis.
Reads 20-F annual reports and quarterly 6-K earnings exhibits.
"""
import os
import re
import sys
from pathlib import Path

REPORTS_DIR = Path("reports/MNSO")

def strip_html(text):
    """Remove HTML tags and decode common entities."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>') \
               .replace('&nbsp;', ' ').replace('&#160;', ' ') \
               .replace('&ldquo;', '"').replace('&rdquo;', '"') \
               .replace('&#8220;', '"').replace('&#8221;', '"') \
               .replace('&#8217;', "'").replace('&rsquo;', "'") \
               .replace('&#8212;', '—').replace('&mdash;', '—') \
               .replace('&#xA0;', ' ')
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def read_html_text(filepath):
    """Read an HTML file and return its plain text."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return strip_html(content)
    except Exception as e:
        return f"[ERROR reading {filepath}: {e}]"

def extract_section(text, keywords, max_chars=8000):
    """Extract text around the first keyword match."""
    for kw in keywords:
        idx = text.lower().find(kw.lower())
        if idx != -1:
            start = max(0, idx - 200)
            end = min(len(text), idx + max_chars)
            return text[start:end]
    return ""

# ─── Print each key file with a separator ────────────────────────────────────

files_to_analyze = [
    # Annual reports (most comprehensive)
    ("20-F_2021-09-17.html", "FY2020 Annual Report"),
    ("20-F_2022-10-19.html", "FY2021 Annual Report"),
    ("20-F_2023-10-19.html", "FY2022 Annual Report"),
    ("20-F_2024-04-16.html", "FY2023 Annual Report"),
    ("20-F_2025-04-24.html", "FY2024 Annual Report"),
    ("20-F_2026-04-24.html", "FY2025 Annual Report"),
    # Quarterly earnings (6-K exhibits)
    ("6-K_2022-08-25_ex1.html", "Q1/Q2 FY2022 Earnings"),
    ("6-K_2022-08-25_ex2.html", "Q1/Q2 FY2022 Earnings ex2"),
    ("6-K_2022-09-29_ex1.html", "Q2 FY2022 Earnings"),
    ("6-K_2022-09-29_ex2.html", "Q2 FY2022 Earnings ex2"),
    ("6-K_2022-11-15_ex1.html", "Q3 FY2022 Earnings"),
    ("6-K_2022-11-15_ex2.html", "Q3 FY2022 Earnings ex2"),
    ("6-K_2023-02-28_ex1.html", "FY2022 Annual Results"),
    ("6-K_2023-02-28_ex2.html", "FY2022 Annual Results ex2"),
    ("6-K_2023-02-28_ex3.html", "FY2022 Annual Results ex3"),
    ("6-K_2023-05-16_ex1.html", "Q1 FY2023 Earnings"),
    ("6-K_2023-05-16_ex2.html", "Q1 FY2023 Earnings ex2"),
    ("6-K_2023-08-23_ex1.html", "Q2 FY2023 Earnings"),
    ("6-K_2023-08-23_ex2.html", "Q2 FY2023 Earnings ex2"),
    ("6-K_2023-09-15_ex2.html", "Q2 FY2023 Supplemental"),
    ("6-K_2023-09-15_ex3.html", "Q2 FY2023 Supplemental ex3"),
    ("6-K_2023-11-22_ex1.html", "Q3 FY2023 Earnings"),
    ("6-K_2023-11-22_ex2.html", "Q3 FY2023 Earnings ex2"),
    ("6-K_2024-01-17_ex1.html", "Q3 FY2023 Results"),
    ("6-K_2024-01-17_ex2.html", "Q3 FY2023 Results ex2"),
    ("6-K_2024-01-17_ex3.html", "Q3 FY2023 Results ex3"),
    ("6-K_2024-01-17_ex4.html", "Q3 FY2023 Results ex4"),
    ("6-K_2024-03-12_ex1.html", "FY2023 Annual Results"),
    ("6-K_2024-03-12_ex2.html", "FY2023 Annual Results ex2"),
    ("6-K_2024-03-12_ex3.html", "FY2023 Annual Results ex3"),
    ("6-K_2024-05-14_ex1.html", "Q1 FY2024 Earnings"),
    ("6-K_2024-05-14_ex2.html", "Q1 FY2024 Earnings ex2"),
    ("6-K_2024-08-30_ex1.html", "Q2 FY2024 Earnings"),
    ("6-K_2024-08-30_ex2.html", "Q2 FY2024 Earnings ex2"),
    ("6-K_2024-08-30_ex3.html", "Q2 FY2024 Earnings ex3"),
    ("6-K_2024-08-30_ex4.html", "Q2 FY2024 Earnings ex4"),
    ("6-K_2024-08-30_ex5.html", "Q2 FY2024 Earnings ex5"),
    ("6-K_2024-12-02_ex1.html", "Q3 FY2024 Earnings"),
    ("6-K_2024-12-02_ex2.html", "Q3 FY2024 Earnings ex2"),
    ("6-K_2024-12-02_ex3.html", "Q3 FY2024 Earnings ex3"),
    ("6-K_2025-03-24_ex1.html", "FY2024 Annual Results"),
    ("6-K_2025-03-24_ex2.html", "FY2024 Annual Results ex2"),
    ("6-K_2025-03-24_ex3.html", "FY2024 Annual Results ex3"),
    ("6-K_2025-03-24_ex4.html", "FY2024 Annual Results ex4"),
    ("6-K_2025-05-23_ex1.html", "Q1 FY2025 Earnings"),
    ("6-K_2025-05-23_ex2.html", "Q1 FY2025 Earnings ex2"),
    ("6-K_2025-08-22_ex1.html", "Q2 FY2025 Earnings"),
    ("6-K_2025-08-22_ex2.html", "Q2 FY2025 Earnings ex2"),
    ("6-K_2025-08-22_ex3.html", "Q2 FY2025 Earnings ex3"),
    ("6-K_2025-08-22_ex4.html", "Q2 FY2025 Earnings ex4"),
    ("6-K_2025-08-22_ex5.html", "Q2 FY2025 Earnings ex5"),
    ("6-K_2025-11-24_ex1.html", "Q3 FY2025 Earnings"),
    ("6-K_2025-11-24_ex2.html", "Q3 FY2025 Earnings ex2"),
    ("6-K_2025-11-24_ex3.html", "Q3 FY2025 Earnings ex3"),
    ("6-K_2025-11-24_ex4.html", "Q3 FY2025 Earnings ex4"),
    ("6-K_2026-03-13_ex1.html", "Q4 FY2025 Supplemental"),
    ("6-K_2026-03-13_ex2.html", "Q4 FY2025 Supplemental ex2"),
    ("6-K_2026-03-13_ex3.html", "Q4 FY2025 Supplemental ex3"),
    ("6-K_2026-03-13_ex4.html", "Q4 FY2025 Supplemental ex4"),
    ("6-K_2026-03-13_ex5.html", "Q4 FY2025 Supplemental ex5"),
    ("6-K_2026-04-01_ex1.html", "FY2025 Annual Results"),
    ("6-K_2026-04-01_ex2.html", "FY2025 Annual Results ex2"),
    ("6-K_2026-04-01_ex3.html", "FY2025 Annual Results ex3"),
    ("6-K_2026-04-01_ex4.html", "FY2025 Annual Results ex4"),
    ("6-K_2026-04-01_ex5.html", "FY2025 Annual Results ex5"),
    ("6-K_2026-04-01_ex6.html", "FY2025 Annual Results ex6"),
    ("6-K_2026-04-01_ex7.html", "FY2025 Annual Results ex7"),
    ("6-K_2026-04-01_ex8.html", "FY2025 Annual Results ex8"),
]

SEPARATOR = "\n" + "="*80 + "\n"

for fname, label in files_to_analyze:
    fpath = REPORTS_DIR / fname
    if not fpath.exists():
        print(f"{SEPARATOR}[MISSING] {label} ({fname})")
        continue
    text = read_html_text(fpath)
    # For 20-F files (very large), extract key sections
    if fname.startswith("20-F"):
        # Get first 3000 chars (overview/highlights) + financial results sections
        overview = text[:3000]
        fin_section = extract_section(text, [
            "revenue", "net income", "gross profit", "operating income",
            "number of stores", "store count", "financial highlights"
        ], max_chars=12000)
        risk_section = extract_section(text, ["risk factors", "principal risks"], max_chars=6000)
        strategy_section = extract_section(text, ["our strategy", "business strategy", "growth strategy"], max_chars=6000)
        print(f"{SEPARATOR}### {label} ({fname})\n")
        print("--- OVERVIEW ---")
        print(overview[:2000])
        print("\n--- FINANCIAL DATA ---")
        print(fin_section[:6000])
        print("\n--- RISK FACTORS (excerpt) ---")
        print(risk_section[:3000])
        print("\n--- STRATEGY (excerpt) ---")
        print(strategy_section[:3000])
    else:
        # For 6-K exhibits, print full text (they're usually shorter)
        print(f"{SEPARATOR}### {label} ({fname})\n")
        print(text[:15000])
