#!/usr/bin/env python3
from bs4 import BeautifulSoup
import re
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'my_reports', 'DUOL')

files = [
    ('Q2 2021 (first public quarter)', os.path.join(BASE, '10-Q_2021-08-12.html')),
    ('Q3 2021', os.path.join(BASE, '10-Q_2021-11-12.html')),
    ('FY2021 10-K', os.path.join(BASE, '10-K_2022-03-04.html')),
    ('Q1 2022', os.path.join(BASE, '10-Q_2022-05-13.html')),
    ('Q2 2022', os.path.join(BASE, '10-Q_2022-08-05.html')),
    ('Q3 2022', os.path.join(BASE, '10-Q_2022-11-14.html')),
    ('FY2022 10-K', os.path.join(BASE, '10-K_2023-03-01.html')),
    ('Q1 2023', os.path.join(BASE, '10-Q_2023-05-10.html')),
    ('Q2 2023', os.path.join(BASE, '10-Q_2023-08-09.html')),
    ('Q3 2023', os.path.join(BASE, '10-Q_2023-11-09.html')),
    ('FY2023 10-K', os.path.join(BASE, '10-K_2024-02-29.html')),
    ('Q1 2024', os.path.join(BASE, '10-Q_2024-05-09.html')),
    ('Q2 2024', os.path.join(BASE, '10-Q_2024-08-08.html')),
    ('Q3 2024', os.path.join(BASE, '10-Q_2024-11-07.html')),
    ('FY2024 10-K', os.path.join(BASE, '10-K_2025-02-28.html')),
    ('Q1 2025', os.path.join(BASE, '10-Q_2025-05-02.html')),
    ('Q2 2025', os.path.join(BASE, '10-Q_2025-08-07.html')),
    ('Q3 2025', os.path.join(BASE, '10-Q_2025-11-06.html')),
    ('FY2025 10-K', os.path.join(BASE, '10-K_2026-02-27.html')),
    ('Q1 2026', os.path.join(BASE, '10-Q_2026-05-05.html')),
]

# Keywords for sections we care about
KEY_SECTIONS = [
    'revenue', 'net loss', 'net income', 'operating', 'cost of revenue',
    'gross profit', 'research and development', 'sales and marketing',
    'general and administrative', 'stock-based compensation',
    'adjusted ebitda', 'daily active', 'DAU', 'MAU', 'monthly active',
    'ARPU', 'average revenue', 'paid subscriber', 'subscription',
    'advertising', 'in-app purchase', 'international', 'risk factor',
    'liquidity', 'capital resources', 'headcount', 'employees',
    'restructuring', 'impairment', 'income tax', 'interest', 'cash flow',
    'streak', 'leaderboard', 'gamification', 'duolingo plus', 'super duolingo',
    'duolingo max', 'AI', 'artificial intelligence', 'language learning',
    'total bookings', 'bookings', 'free cash flow', 'retention',
    'conversion', 'user growth', 'engagement',
]

def extract_financial_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Find lines relevant to financial analysis
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

output_path = '/tmp/duol_extracted.txt'
with open(output_path, 'w', encoding='utf-8') as out:
    for label, path in files:
        sep = '=' * 80
        out.write('\n')
        out.write(sep + '\n')
        out.write(f'FILE: {label} ({path})\n')
        out.write(sep + '\n')
        if not os.path.exists(path):
            out.write(f'[FILE NOT FOUND: {path}]\n')
            print(f'WARNING: not found: {path}')
            continue
        lines = extract_financial_text(path)
        for line in lines[:3000]:
            out.write(line + '\n')
        out.write(f'[Total relevant lines: {len(lines)}]\n')
        print(f'Done: {label} ({len(lines)} relevant lines)')

print(f'\nExtracted to {output_path}')
