#!/usr/bin/env python3
"""
Extract key financial data from Marvell Technology (MRVL) SEC filings.
Usage: python extract_mrvl.py > ../mrvl_extracted.txt
"""
from bs4 import BeautifulSoup
import re
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')

files = [
    ('Q1 FY2022', os.path.join(BASE, '10-Q_2021-06-09.html')),
    ('Q2 FY2022', os.path.join(BASE, '10-Q_2021-08-27.html')),
    ('Q3 FY2022', os.path.join(BASE, '10-Q_2021-12-03.html')),
    ('FY2022 10-K', os.path.join(BASE, '10-K_2022-03-10.html')),
    ('Q1 FY2023', os.path.join(BASE, '10-Q_2022-05-27.html')),
    ('Q2 FY2023', os.path.join(BASE, '10-Q_2022-08-26.html')),
    ('Q3 FY2023', os.path.join(BASE, '10-Q_2022-12-02.html')),
    ('FY2023 10-K', os.path.join(BASE, '10-K_2023-03-09.html')),
    ('Q1 FY2024', os.path.join(BASE, '10-Q_2023-05-26.html')),
    ('Q2 FY2024', os.path.join(BASE, '10-Q_2023-08-25.html')),
    ('Q3 FY2024', os.path.join(BASE, '10-Q_2023-12-01.html')),
    ('FY2024 10-K', os.path.join(BASE, '10-K_2024-03-13.html')),
    ('Q1 FY2025', os.path.join(BASE, '10-Q_2024-05-31.html')),
    ('Q2 FY2025', os.path.join(BASE, '10-Q_2024-08-30.html')),
    ('Q3 FY2025', os.path.join(BASE, '10-Q_2024-12-04.html')),
    ('FY2025 10-K', os.path.join(BASE, '10-K_2025-03-12.html')),
    ('Q1 FY2026', os.path.join(BASE, '10-Q_2025-05-30.html')),
    ('Q2 FY2026', os.path.join(BASE, '10-Q_2025-08-29.html')),
    ('Q3 FY2026', os.path.join(BASE, '10-Q_2025-12-03.html')),
    ('FY2026 10-K', os.path.join(BASE, '10-K_2026-03-11.html')),
]

KEY_SECTIONS = [
    'net revenue', 'total net revenue', 'total revenue',
    'net income', 'net loss', 'operating income', 'operating loss',
    'cost of revenue', 'gross profit', 'gross margin',
    'research and development', 'selling, general', 'general and administrative',
    'stock-based compensation', 'restructuring',
    'data center', 'carrier infrastructure', 'enterprise networking',
    'consumer', 'automotive', 'storage',
    'cloud', 'artificial intelligence', 'AI', 'custom silicon',
    'inphi', 'innovium', 'avera', 'cavium', 'aquantia',
    'acquisition', 'goodwill', 'impairment',
    'income tax', 'effective tax rate',
    'cash and cash equivalents', 'free cash flow', 'operating cash flow',
    'capital expenditure', 'capex',
    'share repurchase', 'buyback', 'dividend',
    'debt', 'senior notes', 'term loan', 'revolving credit',
    'diluted', 'earnings per share', 'eps',
    'headcount', 'employee',
    'risk factor', 'competition', 'competitive',
    'customer concentration', 'samsung', 'amazon', 'microsoft', 'google', 'alphabet',
    'broadcom', 'nvidia', 'intel', 'qualcomm', 'xilinx', 'amd',
    'market share', 'design win',
    'inventory', 'supply chain', 'backlog',
    'guidance', 'outlook', 'next quarter',
    'segment', 'end market',
    'optical', 'electro-optics', 'dsp', 'coherent',
    'switching', 'routing', 'ethernet',
    'security', 'arm', 'processor',
    '5g', 'base station', 'wireless',
    'hyperscaler', 'hyperscale',
    'interconnect', 'serdes',
    'amortization', 'depreciation',
    'operating leverage', 'margin expansion',
]

def extract_financial_text(path):
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
    
    context_window = 5
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
    print(f'FILING: {label} ({os.path.basename(path)})')
    print(sep)
    lines = extract_financial_text(path)
    for line in lines[:5000]:
        print(line)
    print(f'\n[Total relevant lines extracted: {len(lines)}]')
