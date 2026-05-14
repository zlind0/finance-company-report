#!/usr/bin/env python3
from bs4 import BeautifulSoup
import re
import sys

files = [
    ('Q1 2024', 'reports/RDDT/10-Q_2024-05-08.html'),
    ('Q2 2024', 'reports/RDDT/10-Q_2024-08-07.html'),
    ('Q3 2024', 'reports/RDDT/10-Q_2024-10-30.html'),
    ('FY2024 10-K', 'reports/RDDT/10-K_2025-02-13.html'),
    ('Q1 2025', 'reports/RDDT/10-Q_2025-05-02.html'),
    ('Q2 2025', 'reports/RDDT/10-Q_2025-08-01.html'),
    ('Q3 2025', 'reports/RDDT/10-Q_2025-10-31.html'),
    ('FY2025 10-K', 'reports/RDDT/10-K_2026-02-06.html'),
    ('Q1 2026', 'reports/RDDT/10-Q_2026-05-01.html'),
]

# Keywords for sections we care about
KEY_SECTIONS = [
    'revenue', 'net loss', 'net income', 'operating', 'cost of revenue',
    'gross profit', 'research and development', 'sales and marketing',
    'general and administrative', 'stock-based compensation',
    'adjusted ebitda', 'daily active', 'DAU', 'ARPU', 'average revenue',
    'advertising', 'data licensing', 'international', 'risk factor',
    'liquidity', 'capital resources', 'segment', 'headcount', 'employees',
    'restructuring', 'impairment', 'income tax', 'interest', 'cash flow',
]

def extract_financial_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Find lines relevant to financial analysis
    relevant = []
    context_window = 3
    matched_indices = set()
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for kw in KEY_SECTIONS:
            if kw.lower() in line_lower:
                for j in range(max(0, i-context_window), min(len(lines), i+context_window+1)):
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

for label, path in files:
    sep = '=' * 80
    print()
    print(sep)
    print(f'FILE: {label} ({path})')
    print(sep)
    lines = extract_financial_text(path)
    for line in lines[:2000]:
        print(line)
    print(f'[Total relevant lines: {len(lines)}]')
