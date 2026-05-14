#!/usr/bin/env python3
from bs4 import BeautifulSoup
import re
import sys

files = [
    ('Q3 2020 (IPO era)', 'reports/RKLB/10-Q_2020-11-16.html'),
    ('Q1 2021', 'reports/RKLB/10-Q_2021-05-24.html'),
    ('Q2 2021', 'reports/RKLB/10-Q_2021-08-03.html'),
    ('Q3 2021', 'reports/RKLB/10-Q_2021-11-15.html'),
    ('FY2021 10-K', 'reports/RKLB/10-K_2021-03-31.html'),
    ('FY2022 10-K', 'reports/RKLB/10-K_2022-03-24.html'),
    ('Q1 2022', 'reports/RKLB/10-Q_2022-05-16.html'),
    ('Q2 2022', 'reports/RKLB/10-Q_2022-08-11.html'),
    ('Q3 2022', 'reports/RKLB/10-Q_2022-11-09.html'),
    ('FY2023 10-K', 'reports/RKLB/10-K_2023-03-07.html'),
    ('Q1 2023', 'reports/RKLB/10-Q_2023-05-09.html'),
    ('Q2 2023', 'reports/RKLB/10-Q_2023-08-08.html'),
    ('Q3 2023', 'reports/RKLB/10-Q_2023-11-08.html'),
    ('FY2024 10-K', 'reports/RKLB/10-K_2024-02-28.html'),
    ('Q1 2024', 'reports/RKLB/10-Q_2024-05-06.html'),
    ('Q2 2024', 'reports/RKLB/10-Q_2024-08-08.html'),
    ('Q3 2024', 'reports/RKLB/10-Q_2024-11-12.html'),
    ('FY2025 10-K', 'reports/RKLB/10-K_2025-02-27.html'),
    ('Q1 2025', 'reports/RKLB/10-Q_2025-05-08.html'),
    ('Q2 2025', 'reports/RKLB/10-Q_2025-08-07.html'),
    ('Q3 2025', 'reports/RKLB/10-Q_2025-11-10.html'),
    ('FY2026 10-K', 'reports/RKLB/10-K_2026-02-26.html'),
    ('Q1 2026', 'reports/RKLB/10-Q_2026-05-07.html'),
]

KEY_SECTIONS = [
    'revenue', 'net loss', 'net income', 'operating', 'cost of revenue',
    'gross profit', 'gross margin', 'research and development', 'r&d',
    'general and administrative', 'stock-based compensation', 'sbc',
    'adjusted ebitda', 'backlog', 'launch', 'electron', 'neutron',
    'photon', 'space systems', 'launch services', 'spacecraft',
    'components', 'solar', 'satellite', 'constellation',
    'risk factor', 'liquidity', 'capital resources',
    'guidance', 'outlook', 'milestone', 'contract',
    'income tax', 'interest', 'cash flow', 'cash and cash equivalents',
    'headcount', 'employees', 'restructuring', 'impairment',
    'depreciation', 'amortization', 'capex', 'capital expenditure',
    'debt', 'convertible', 'dilution', 'shares outstanding',
    'defense', 'government', 'nasa', 'dod', 'nro',
    'reusability', 'reusable', 'recovery', 'catch', 'helicopter',
    'neutron', 'medium lift', 'large launch',
    'space power', 'solar cells', 'reaction wheels', 'star tracker',
    'acquisition', 'acquire', 'merger', 'sinclair', 'planetary systems',
    'advanced space', 'mynaric', 'solero',
    'total assets', 'total liabilities', 'stockholders equity',
    'operating loss', 'ebitda',
]

def extract_financial_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    relevant = []
    context_window = 4
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

output_path = '/tmp/rklb_extracted.txt'
with open(output_path, 'w', encoding='utf-8') as out:
    for label, path in files:
        sep = '=' * 80
        out.write('\n')
        out.write(sep + '\n')
        out.write(f'FILE: {label} ({path})\n')
        out.write(sep + '\n')
        try:
            lines = extract_financial_text(path)
            for line in lines[:3000]:
                out.write(line + '\n')
            out.write(f'[Total relevant lines: {len(lines)}]\n')
        except Exception as e:
            out.write(f'[ERROR: {e}]\n')

print(f'Extraction complete. Output: {output_path}')
