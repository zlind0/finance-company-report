#!/usr/bin/env python3
"""Extract clean financial text from RKLB 10-K and 10-Q HTML filings."""
from bs4 import BeautifulSoup
import re
import os

files = [
    ('FY2022 10K', 'reports/RKLB/10-K_2022-03-24.html'),
    ('Q1 2022', 'reports/RKLB/10-Q_2022-05-16.html'),
    ('Q2 2022', 'reports/RKLB/10-Q_2022-08-11.html'),
    ('Q3 2022', 'reports/RKLB/10-Q_2022-11-09.html'),
    ('FY2023 10K', 'reports/RKLB/10-K_2023-03-07.html'),
    ('Q1 2023', 'reports/RKLB/10-Q_2023-05-09.html'),
    ('Q2 2023', 'reports/RKLB/10-Q_2023-08-08.html'),
    ('Q3 2023', 'reports/RKLB/10-Q_2023-11-08.html'),
    ('FY2024 10K', 'reports/RKLB/10-K_2024-02-28.html'),
    ('Q1 2024', 'reports/RKLB/10-Q_2024-05-06.html'),
    ('Q2 2024', 'reports/RKLB/10-Q_2024-08-08.html'),
    ('Q3 2024', 'reports/RKLB/10-Q_2024-11-12.html'),
    ('FY2025 10K', 'reports/RKLB/10-K_2025-02-27.html'),
    ('Q1 2025', 'reports/RKLB/10-Q_2025-05-08.html'),
    ('Q2 2025', 'reports/RKLB/10-Q_2025-08-07.html'),
    ('Q3 2025', 'reports/RKLB/10-Q_2025-11-10.html'),
    ('FY2026 10K', 'reports/RKLB/10-K_2026-02-26.html'),
    ('Q1 2026', 'reports/RKLB/10-Q_2026-05-07.html'),
]

KEY_SECTIONS = [
    'revenue', 'launch services', 'space systems', 'cost of revenue',
    'gross profit', 'gross margin', 'operating loss', 'net loss', 'net income',
    'research and development', 'general and administrative',
    'stock-based compensation', 'backlog', 'electron', 'neutron',
    'guidance', 'outlook', 'employees', 'headcount', 'cash and cash',
    'total assets', 'total liabilities', 'adjusted ebitda',
    'spacecraft', 'satellite', 'components', 'solar cell',
    'acquisition', 'sinclair', 'planetary systems', 'advanced space',
    'nasa', 'nro', 'defense', 'government contract',
    'reusab', 'recovery', 'catch', 'helicopter',
    'medium lift', 'neutron', 'capital expenditure',
    'interest expense', 'convertible', 'dilut', 'shares outstanding',
    'launch vehicle', 'photon', 'space power',
    'depreciation', 'amortization', 'operating cash', 'free cash',
    'segment', 'concentration', 'customer', 'contract',
    'milestones', 'launch cadence', 'manifest', 'constellation',
]

def extract_clean_text(path):
    """Extract clean text from HTML, filtering for relevant financial content."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    # Remove script and style
    for tag in soup(['script', 'style', 'head']):
        tag.decompose()
    # Remove XBRL-only content (lines that are pure metadata)
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Filter out pure XBRL metadata lines
    filtered = []
    for line in lines:
        # Skip short XBRL-style identifiers (no spaces, mostly IDs)
        if re.match(r'^[a-z0-9\-_:]+$', line) and len(line) < 80 and ' ' not in line:
            continue
        # Skip pure date lines like 2021-01-01 or 2021-12-31
        if re.match(r'^\d{4}-\d{2}-\d{2}$', line):
            continue
        # Skip pure number lines
        if re.match(r'^[\d,\.\-\(\)\s]+$', line) and len(line) < 30:
            continue
        filtered.append(line)

    # Find sections with keywords
    matched_indices = set()
    context_window = 5
    for i, line in enumerate(filtered):
        ll = line.lower()
        for kw in KEY_SECTIONS:
            if kw.lower() in ll:
                for j in range(max(0, i-context_window), min(len(filtered), i+context_window+1)):
                    matched_indices.add(j)
                break

    result = []
    prev_idx = -1
    for idx in sorted(matched_indices):
        if prev_idx >= 0 and idx > prev_idx + 1:
            result.append('...')
        result.append(filtered[idx])
        prev_idx = idx
    return result

output_path = '/tmp/rklb_clean.txt'
with open(output_path, 'w', encoding='utf-8') as out:
    for label, path in files:
        sep = '=' * 80
        out.write('\n')
        out.write(sep + '\n')
        out.write(f'FILE: {label} ({path})\n')
        out.write(sep + '\n')
        try:
            lines = extract_clean_text(path)
            # Limit to most relevant 4000 lines per file
            for line in lines[:4000]:
                out.write(line + '\n')
            out.write(f'[Total relevant lines: {len(lines)}]\n')
        except Exception as e:
            out.write(f'[ERROR: {e}]\n')

print(f'Done. Output: {output_path}')
import subprocess
result = subprocess.run(['wc', '-l', output_path], capture_output=True, text=True)
print(result.stdout.strip())
