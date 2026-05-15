#!/usr/bin/env python3
from bs4 import BeautifulSoup
import re
import sys

files = [
    ('FY2025 10-K', 'companies/WMT/raw_reports/10-K_2026-03-13.html'),
    ('Q1 FY2026', 'companies/WMT/raw_reports/10-Q_2025-06-06.html'),
    ('Q2 FY2026', 'companies/WMT/raw_reports/10-Q_2025-08-29.html'),
    ('Q3 FY2026', 'companies/WMT/raw_reports/10-Q_2025-12-03.html'),
    ('FY2024 10-K', 'companies/WMT/raw_reports/10-K_2025-03-14.html'),
    ('FY2023 10-K', 'companies/WMT/raw_reports/10-K_2024-03-15.html'),
    ('FY2022 10-K', 'companies/WMT/raw_reports/10-K_2023-03-17.html'),
    ('FY2021 10-K', 'companies/WMT/raw_reports/10-K_2022-03-18.html'),
    ('FY2020 10-K', 'companies/WMT/raw_reports/10-K_2021-03-19.html'),
    ('FY2019 10-K', 'companies/WMT/raw_reports/10-K_2020-03-20.html'),
    ('FY2018 10-K', 'companies/WMT/raw_reports/10-K_2019-03-28.html'),
    ('FY2017 10-K', 'companies/WMT/raw_reports/10-K_2018-03-30.html'),
    ('FY2016 10-K', 'companies/WMT/raw_reports/10-K_2017-03-31.html'),
    ('FY2015 10-K', 'companies/WMT/raw_reports/10-K_2016-03-30.html'),
    ('FY2014 10-K', 'companies/WMT/raw_reports/10-K_2015-04-01.html'),
    ('FY2013 10-K', 'companies/WMT/raw_reports/10-K_2014-03-21.html'),
    ('FY2012 10-K', 'companies/WMT/raw_reports/10-K_2013-03-26.html'),
    ('FY2011 10-K', 'companies/WMT/raw_reports/10-K_2012-03-27.html'),
    ('FY2010 10-K', 'companies/WMT/raw_reports/10-K_2011-03-30.html'),
    ('FY2009 10-K', 'companies/WMT/raw_reports/10-K_2010-03-30.html'),
    ('FY2008 10-K', 'companies/WMT/raw_reports/10-K_2009-04-01.html'),
    ('FY2007 10-K', 'companies/WMT/raw_reports/10-K_2008-03-31.html'),
    ('FY2006 10-K', 'companies/WMT/raw_reports/10-K_2007-03-27.html'),
    ('FY2005 10-K', 'companies/WMT/raw_reports/10-K_2006-03-29.html'),
    ('FY2004 10-K', 'companies/WMT/raw_reports/10-K_2005-03-31.html'),
    ('FY2003 10-K', 'companies/WMT/raw_reports/10-K_2004-04-09.html'),
    ('FY2002 10-K', 'companies/WMT/raw_reports/10-K_2003-04-15.html'),
    ('FY2001 10-K', 'companies/WMT/raw_reports/10-K_2002-04-15.html'),
    ('FY2000 10-K', 'companies/WMT/raw_reports/10-K_2001-04-10.html'),
    ('FY1999 10-K', 'companies/WMT/raw_reports/10-K_2000-04-17.html'),
]

KEY_SECTIONS = [
    'revenue', 'net sales', 'net income', 'operating income', 'operating expense',
    'cost of sales', 'gross profit', 'gross margin', 'operating margin',
    'earnings per share', 'diluted', 'segment', 'walmart u.s.', 'walmart international',
    'sam\'s club', 'sams club', 'e-commerce', 'ecommerce', 'comparable sales',
    'comp sales', 'same-store', 'grocery', 'general merchandise',
    'membership', 'walmart+', 'walmart plus', 'advertising', 'walmart connect',
    'marketplace', 'fulfillment', 'supply chain', 'automation',
    'capital expenditure', 'capex', 'free cash flow', 'cash flow',
    'dividend', 'share repurchase', 'buyback', 'debt', 'long-term debt',
    'risk factor', 'competition', 'competitor', 'amazon', 'costco', 'kroger', 'target',
    'price', 'low price', 'everyday low', 'edlp', 'edlc',
    'employee', 'associate', 'wage', 'minimum wage',
    'international', 'china', 'mexico', 'india', 'flipkart',
    'curbside', 'pickup', 'delivery', 'last mile',
    'private brand', 'private label', 'great value',
    'inventory', 'shrinkage', 'shrink', 'theft',
    'esg', 'sustainability', 'climate', 'renewable',
    'real estate', 'property', 'lease', 'store count', 'unit count',
    'tax', 'effective tax rate', 'income tax',
    'goodwill', 'intangible', 'impairment', 'restructuring',
    'liquidity', 'capital resources', 'working capital',
    'membership fee', 'plus membership', 'scan and go',
    'phonepe', 'flipkart', 'jd.com', 'vizio',
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

# Process all files or a subset
if len(sys.argv) > 1:
    # Filter files by label pattern
    pattern = sys.argv[1]
    selected = [(l, p) for l, p in files if pattern.lower() in l.lower()]
else:
    selected = files

for label, path in selected:
    sep = '=' * 80
    print()
    print(sep)
    print(f'FILE: {label} ({path})')
    print(sep)
    try:
        lines = extract_financial_text(path)
        for line in lines[:3000]:
            print(line)
        print(f'[Total relevant lines: {len(lines)}]')
    except Exception as e:
        print(f'ERROR: {e}')
