#!/usr/bin/env python3
"""Extract key financial data from AVGO (Broadcom) SEC filings."""
from bs4 import BeautifulSoup
import re
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')

files = [
    ('FY2018 10-K', '10-K_2018-12-21.html'),
    ('Q1 FY2019', '10-Q_2019-03-15.html'),
    ('Q2 FY2019', '10-Q_2019-06-14.html'),
    ('Q3 FY2019', '10-Q_2019-09-13.html'),
    ('FY2019 10-K', '10-K_2019-12-20.html'),
    ('Q1 FY2020', '10-Q_2020-03-13.html'),
    ('Q2 FY2020', '10-Q_2020-06-12.html'),
    ('Q3 FY2020', '10-Q_2020-09-11.html'),
    ('FY2020 10-K', '10-K_2020-12-18.html'),
    ('Q1 FY2021', '10-Q_2021-03-12.html'),
    ('Q2 FY2021', '10-Q_2021-06-11.html'),
    ('Q3 FY2021', '10-Q_2021-09-09.html'),
    ('FY2021 10-K', '10-K_2021-12-17.html'),
    ('Q1 FY2022', '10-Q_2022-03-10.html'),
    ('Q2 FY2022', '10-Q_2022-06-09.html'),
    ('Q3 FY2022', '10-Q_2022-09-08.html'),
    ('FY2022 10-K', '10-K_2022-12-16.html'),
    ('Q1 FY2023', '10-Q_2023-03-08.html'),
    ('Q2 FY2023', '10-Q_2023-06-07.html'),
    ('Q3 FY2023', '10-Q_2023-09-06.html'),
    ('FY2023 10-K', '10-K_2023-12-14.html'),
    ('Q1 FY2024', '10-Q_2024-03-14.html'),
    ('Q2 FY2024', '10-Q_2024-06-13.html'),
    ('Q3 FY2024', '10-Q_2024-09-11.html'),
    ('FY2024 10-K', '10-K_2024-12-20.html'),
    ('Q1 FY2025', '10-Q_2025-03-12.html'),
    ('Q2 FY2025', '10-Q_2025-06-11.html'),
    ('Q3 FY2025', '10-Q_2025-09-10.html'),
    ('FY2025 10-K', '10-K_2025-12-18.html'),
    ('Q1 FY2026', '10-Q_2026-03-11.html'),
    # Note: Q1 FY2018 and Q2 FY2018 available too
    ('Q1 FY2018', '10-Q_2018-06-14.html'),
    ('Q2 FY2018', '10-Q_2018-09-13.html'),
]

KEY_SECTIONS = [
    # Revenue and P&L
    'net revenue', 'net sales', 'revenue', 'net income', 'net loss',
    'operating income', 'operating loss', 'gross profit', 'gross margin',
    'cost of revenue', 'cost of products', 'cost of services',
    # Segment info
    'semiconductor solutions', 'infrastructure software', 'networking', 'storage',
    'broadband', 'wireless', 'industrial', 'vmware', 'ca technologies',
    'symantec', 'brocade', 'mainframe',
    # Operating expenses
    'research and development', 'selling, general', 'restructuring',
    'amortization of acquisition', 'stock-based compensation',
    # Acquisitions
    'acquisition', 'merger', 'purchase price', 'goodwill', 'intangible',
    # Cash flow and balance sheet
    'cash and cash equivalents', 'free cash flow', 'capital expenditure',
    'operating cash', 'debt', 'long-term debt', 'credit facility', 'notes',
    # Shareholder returns
    'dividend', 'share repurchase', 'buyback', 'repurchase',
    # Customers and market
    'customer concentration', 'apple', 'hyperscaler', 'cloud', 'ai',
    'artificial intelligence', 'custom accelerator', 'xpu',
    # Guidance and outlook
    'guidance', 'outlook', 'fiscal', 'backlog', 'design win',
    # Risk and competition
    'competition', 'competitive', 'risk factor', 'tariff', 'export',
    'china', 'huawei', 'supply chain', 'fab', 'foundry',
    # Financial metrics
    'adjusted ebitda', 'non-gaap', 'free cash', 'leverage ratio',
    'interest expense', 'income tax', 'effective tax',
    # Employees
    'employee', 'headcount', 'workforce',
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


output_path = os.path.join(os.path.dirname(__file__), '..', 'avgo_extracted.txt')
with open(output_path, 'w', encoding='utf-8') as out:
    for label, filename in files:
        path = os.path.join(BASE, filename)
        if not os.path.exists(path):
            print(f"SKIPPING (not found): {filename}", file=sys.stderr)
            continue
        sep = '=' * 80
        header = f'\nFILING: {label} ({filename})\n{sep}\n'
        out.write(header)
        print(header.strip())
        lines = extract_financial_text(path)
        for line in lines[:3000]:
            out.write(line + '\n')
        out.write(f'[Total relevant lines: {len(lines)}]\n')
        print(f'  -> {len(lines)} relevant lines extracted')

print(f'\nOutput written to: {output_path}')
