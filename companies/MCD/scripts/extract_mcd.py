#!/usr/bin/env python3
"""
Extract key financial text from McDonald's SEC filings for analysis.
Processes all 10-K annual reports and 10-Q quarterly reports.
Output written to /tmp/mcd_extracted.txt
"""
from bs4 import BeautifulSoup
import re
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')

# Gather all files sorted chronologically
all_files = sorted(
    [f for f in os.listdir(BASE_DIR) if f.endswith('.html')],
    key=lambda x: x.split('_')[1].replace('.html', '')
)

# Build labeled list
files = []
for fname in all_files:
    parts = fname.replace('.html', '').split('_')
    form_type = parts[0]   # 10-K or 10-Q
    date = parts[1]
    year = date[:4]
    if form_type == '10-K':
        label = f'FY{int(year)-1} Annual (10-K filed {date})'
    else:
        label = f'Quarterly {date} (10-Q)'
    files.append((label, os.path.join(BASE_DIR, fname)))

# Keywords relevant to McDonald's business model
KEY_SECTIONS = [
    # Revenue / income
    'revenue', 'net income', 'net loss', 'operating income', 'operating profit',
    'total revenues', 'company-operated', 'franchised', 'franchise',
    # Cost structure
    'food and paper', 'payroll', 'occupancy', 'selling general', 'g&a',
    'general and administrative', 'cost of', 'gross margin', 'gross profit',
    # Refranchising / asset-light
    'refranchis', 'asset-light', 'developmental license', 'ownership structure',
    # Comparable sales
    'comparable sales', 'systemwide sales', 'system-wide', 'same-store',
    'guest count', 'average check', 'traffic',
    # Segments
    'segment', 'u.s.', 'international operated markets', 'iom',
    'international developmental licensed', 'idl', 'corporate',
    # Digital / delivery
    'digital', 'loyalty', 'mobile', 'delivery', 'drive-thru', 'drive thru',
    'technology', 'app', 'MyMcDonald',
    # Strategy
    'velocity', 'accelerating', 'arches', 'our food', 'plan to win',
    'accelerate the arches', 'best burger', 'chicken', 'beverage',
    # Debt / capital
    'long-term debt', 'debt', 'interest expense', 'share repurchase',
    'dividends', 'capital expenditure', 'capex', 'return to shareholders',
    # Employees / labor
    'employees', 'headcount', 'labor', 'minimum wage',
    # Risk / macro
    'risk factor', 'inflation', 'foreign currency', 'exchange rate',
    'commodity', 'beef', 'economic', 'competition', 'regulation',
    'franchise system', 'franchisee',
    # Cash flow
    'cash flow', 'free cash flow', 'liquidity', 'capital resources',
    # Store count
    'restaurants', 'restaurant count', 'new restaurant', 'closed', 'openings',
    # Recent / guidance
    'outlook', 'guidance', 'full year', 'first quarter', 'second quarter',
    'third quarter', 'fourth quarter',
]

def extract_financial_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    context_window = 4
    matched_indices = set()

    for i, line in enumerate(lines):
        line_lower = line.lower()
        for kw in KEY_SECTIONS:
            if kw.lower() in line_lower:
                for j in range(max(0, i - context_window), min(len(lines), i + context_window + 1)):
                    matched_indices.add(j)
                break

    result = []
    prev_idx = -1
    for idx in sorted(matched_indices):
        if prev_idx >= 0 and idx > prev_idx + 1:
            result.append('...')
        result.append(lines[idx])
        prev_idx = idx

    return result


OUT_PATH = '/tmp/mcd_extracted.txt'
with open(OUT_PATH, 'w', encoding='utf-8') as out:
    for label, path in files:
        sep = '=' * 80
        out.write('\n')
        out.write(sep + '\n')
        out.write(f'FILE: {label}\n')
        out.write(f'PATH: {path}\n')
        out.write(sep + '\n')
        try:
            lines = extract_financial_text(path)
            # Cap per file to avoid enormous output
            cap = 3000
            for line in lines[:cap]:
                out.write(line + '\n')
            if len(lines) > cap:
                out.write(f'[... truncated, {len(lines) - cap} more lines ...]\n')
            out.write(f'[Total relevant lines: {len(lines)}]\n')
        except Exception as e:
            out.write(f'ERROR: {e}\n')

print(f'Done. Output written to {OUT_PATH}')
print(f'File size: {os.path.getsize(OUT_PATH):,} bytes')
