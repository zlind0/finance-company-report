#!/usr/bin/env python3
"""
Improved extraction for Marvell Technology SEC filings.
Extracts full narrative text, filtering out XBRL metadata.
"""
from bs4 import BeautifulSoup
import re
import os
import sys

BASE = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')

files = [
    ('Q1 FY2022', '10-Q_2021-06-09.html'),
    ('Q2 FY2022', '10-Q_2021-08-27.html'),
    ('Q3 FY2022', '10-Q_2021-12-03.html'),
    ('FY2022 10-K', '10-K_2022-03-10.html'),
    ('Q1 FY2023', '10-Q_2022-05-27.html'),
    ('Q2 FY2023', '10-Q_2022-08-26.html'),
    ('Q3 FY2023', '10-Q_2022-12-02.html'),
    ('FY2023 10-K', '10-K_2023-03-09.html'),
    ('Q1 FY2024', '10-Q_2023-05-26.html'),
    ('Q2 FY2024', '10-Q_2023-08-25.html'),
    ('Q3 FY2024', '10-Q_2023-12-01.html'),
    ('FY2024 10-K', '10-K_2024-03-13.html'),
    ('Q1 FY2025', '10-Q_2024-05-31.html'),
    ('Q2 FY2025', '10-Q_2024-08-30.html'),
    ('Q3 FY2025', '10-Q_2024-12-04.html'),
    ('FY2025 10-K', '10-K_2025-03-12.html'),
    ('Q1 FY2026', '10-Q_2025-05-30.html'),
    ('Q2 FY2026', '10-Q_2025-08-29.html'),
    ('Q3 FY2026', '10-Q_2025-12-03.html'),
    ('FY2026 10-K', '10-K_2026-03-11.html'),
]

def is_xbrl_noise(line):
    """Filter out XBRL metadata, URLs, and pure data tags."""
    if not line:
        return True
    if line.startswith('http://') or line.startswith('https://'):
        return True
    if line.startswith('us-gaap:') or line.startswith('mrvl:') or line.startswith('srt:'):
        return True
    if line.startswith('xbrli:') or line.startswith('dei:'):
        return True
    # Pure numbers or dates
    if re.match(r'^[\d\.\-/]+$', line):
        return True
    # XBRL context IDs
    if re.match(r'^\d{4}-\d{2}-\d{2}$', line):
        return True
    if re.match(r'^[A-Fa-f0-9]{10,}$', line):
        return True
    # Member/axis tags
    if 'Member' in line and ('us-gaap' in line or 'mrvl' in line or 'srt' in line):
        return True
    if 'Axis' in line and ('us-gaap' in line or 'mrvl' in line):
        return True
    if 'Domain' in line and ('us-gaap' in line or 'mrvl' in line):
        return True
    if 'Table' in line and ('us-gaap' in line or 'mrvl' in line):
        return True
    if 'LineItems' in line:
        return True
    # CIK numbers
    if re.match(r'^000\d{7}$', line):
        return True
    return False

def extract_text(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        return [f"[FILE NOT FOUND: {path}]"]

    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()

    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Filter out XBRL noise
    filtered = []
    for line in lines:
        if not is_xbrl_noise(line):
            filtered.append(line)

    # Merge lines that are clearly part of the same paragraph
    merged = []
    for line in filtered:
        if merged and not line[0].isupper() and not line.startswith('(') and len(merged[-1]) > 80:
            merged[-1] += ' ' + line
        else:
            merged.append(line)

    return merged

output_path = os.path.join(os.path.dirname(__file__), '..', 'mrvl_extracted_v2.txt')
with open(output_path, 'w') as out:
    for label, filename in files:
        path = os.path.join(BASE, filename)
        sep = '=' * 80
        out.write(f'\n{sep}\n')
        out.write(f'FILING: {label} ({filename})\n')
        out.write(f'{sep}\n\n')
        lines = extract_text(path)
        for line in lines:
            out.write(line + '\n')
        out.write(f'\n[Total lines: {len(lines)}]\n')

print(f'Extraction complete. Output: {output_path}')
print(f'Total files processed: {len(files)}')
