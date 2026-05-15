#!/usr/bin/env python3
"""
Extract key financial metrics from all MCD 10-K annual reports.
"""
from bs4 import BeautifulSoup
import re, os

BASE_DIR = 'companies/MCD/raw_reports'

annual_files = sorted([f for f in os.listdir(BASE_DIR) if f.startswith('10-K') and f.endswith('.html')])

key_patterns = [
    r'total revenues?',
    r'net income',
    r'operating income',
    r'comparable sales',
    r'systemwide sales',
    r'system-wide sales',
    r'franchised restaurants',
    r'company-operated restaurants',
    r'restaurant count',
    r'number of restaurants',
    r'refranchis',
    r'return to shareholders',
    r'dividends paid',
    r'share repurchas',
    r'long-?term debt',
    r'operating margin',
    r'free cash flow',
    r'general and admin',
    r'income from operations',
    r'effective tax rate',
    r'diluted earnings per share',
    r'earnings per share',
    r'cash provided by operations',
    r'capital expenditures',
]

def get_key_lines(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    results = []
    seen_starts = set()
    for i, line in enumerate(lines):
        ll = line.lower()
        for pat in key_patterns:
            if re.search(pat, ll):
                ctx = ' | '.join(lines[i:min(i+4, len(lines))])
                key = ctx[:80]
                if key not in seen_starts:
                    seen_starts.add(key)
                    results.append(ctx[:250])
                break
    return results

for fname in annual_files:
    path = os.path.join(BASE_DIR, fname)
    filed_year = fname.split('_')[1][:4]
    fy = int(filed_year) - 1
    print(f'\n{"="*60}')
    print(f'FY{fy} Annual Report (10-K filed {filed_year})')
    print(f'{"="*60}')
    for r in get_key_lines(path):
        print(r)
