#!/usr/bin/env python3
"""
Extract key financial data from Oracle (ORCL) HTML reports.
Covers all 10-K annual reports (2006-2025) and recent 10-Q quarterly reports.
Oracle fiscal year ends May 31.
"""
from bs4 import BeautifulSoup
import re
import os

REPORTS_DIR = 'my_reports/ORCL'

# All 10-K annual reports
ANNUAL_FILES = [
    ('FY2006 10-K', '10-K_2006-07-21.html'),
    ('FY2007 10-K', '10-K_2007-06-29.html'),
    ('FY2008 10-K', '10-K_2008-07-02.html'),
    ('FY2009 10-K', '10-K_2009-06-29.html'),
    ('FY2010 10-K', '10-K_2010-07-01.html'),
    ('FY2011 10-K', '10-K_2011-06-28.html'),
    ('FY2012 10-K', '10-K_2012-06-26.html'),
    ('FY2013 10-K', '10-K_2013-06-26.html'),
    ('FY2014 10-K', '10-K_2014-06-26.html'),
    ('FY2015 10-K', '10-K_2015-06-25.html'),
    ('FY2016 10-K', '10-K_2016-06-22.html'),
    ('FY2017 10-K', '10-K_2017-06-27.html'),
    ('FY2018 10-K', '10-K_2018-06-22.html'),
    ('FY2019 10-K', '10-K_2019-06-21.html'),
    ('FY2020 10-K', '10-K_2020-06-22.html'),
    ('FY2021 10-K', '10-K_2021-06-21.html'),
    ('FY2022 10-K', '10-K_2022-06-21.html'),
    ('FY2023 10-K', '10-K_2023-06-20.html'),
    ('FY2024 10-K', '10-K_2024-06-20.html'),
    ('FY2025 10-K', '10-K_2025-06-18.html'),
]

# Key quarterly reports - recent years focus + milestone years
QUARTERLY_FILES = [
    # FY2010
    ('FY2010 Q1', '10-Q_2009-09-21.html'),
    ('FY2010 Q3', '10-Q_2010-03-29.html'),
    # FY2013
    ('FY2013 Q1', '10-Q_2012-09-24.html'),
    ('FY2013 Q3', '10-Q_2013-03-22.html'),
    # FY2016
    ('FY2016 Q1', '10-Q_2015-09-18.html'),
    ('FY2016 Q3', '10-Q_2016-03-18.html'),
    # FY2019
    ('FY2019 Q1', '10-Q_2018-09-19.html'),
    ('FY2019 Q3', '10-Q_2019-03-18.html'),
    # FY2022 - cloud transformation inflection
    ('FY2022 Q1', '10-Q_2021-09-13.html'),
    ('FY2022 Q2', '10-Q_2021-12-10.html'),
    ('FY2022 Q3', '10-Q_2022-03-11.html'),
    # FY2023 - Cerner acquisition closes
    ('FY2023 Q1', '10-Q_2022-09-13.html'),
    ('FY2023 Q2', '10-Q_2022-12-13.html'),
    ('FY2023 Q3', '10-Q_2023-03-10.html'),
    # FY2024
    ('FY2024 Q1', '10-Q_2023-09-12.html'),
    ('FY2024 Q2', '10-Q_2023-12-12.html'),
    ('FY2024 Q3', '10-Q_2024-03-12.html'),
    # FY2025
    ('FY2025 Q1', '10-Q_2024-09-10.html'),
    ('FY2025 Q2', '10-Q_2024-12-10.html'),
    ('FY2025 Q3', '10-Q_2025-03-11.html'),
    # FY2026
    ('FY2026 Q1', '10-Q_2025-09-10.html'),
    ('FY2026 Q2', '10-Q_2025-12-11.html'),
    ('FY2026 Q3', '10-Q_2026-03-11.html'),
]

# Keywords for sections relevant to Oracle's business
KEY_SECTIONS = [
    # Revenue categories
    'cloud services', 'cloud license', 'on-premise license', 'license', 'support',
    'hardware', 'services', 'total revenues', 'total revenue',
    # Cloud metrics
    'remaining performance obligation', 'RPO', 'cloud backlog', 'deferred revenue',
    'cloud infrastructure', 'OCI', 'autonomous database', 'cloud at customer',
    # Profitability
    'operating income', 'operating margin', 'net income', 'earnings per share',
    'gross profit', 'gross margin', 'cost of revenues', 'cost of support',
    'research and development', 'sales and marketing', 'general and administrative',
    # Capital allocation
    'stock repurchase', 'share repurchase', 'dividends', 'buyback',
    'long-term debt', 'capital expenditure', 'capex',
    # Segments
    'cloud and license', 'hardware', 'services segment',
    # Growth metrics
    'constant currency', 'organic growth', 'headcount', 'employees',
    # Acquisitions
    'cerner', 'sun microsystems', 'peoplesoft', 'siebel', 'netsuite',
    'eloqua', 'responsys', 'datalogix', 'moat', 'grapeshot', 'aconex',
    'acquisition', 'acquired',
    # Risk factors and strategy
    'competition', 'competitive', 'artificial intelligence', 'AI',
    'generative AI', 'machine learning', 'GPU', 'data center',
    'multicloud', 'hyperscaler',
    # Cash flow and balance sheet
    'free cash flow', 'operating cash flow', 'capital expenditures',
    'cash and cash equivalents', 'total assets',
    # Liquidity
    'liquidity', 'leverage', 'interest expense', 'income tax',
    'effective tax rate',
]

def extract_financial_text(path, max_lines=3000):
    """Extract relevant financial text from an HTML file."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return [f'[ERROR: {e}]']
    
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
    
    return result[:max_lines]


def process_files(file_list, label_prefix=''):
    for label, filename in file_list:
        path = os.path.join(REPORTS_DIR, filename)
        sep = '=' * 80
        print()
        print(sep)
        print(f'FILE: {label} ({filename})')
        print(sep)
        
        if not os.path.exists(path):
            print(f'[FILE NOT FOUND: {path}]')
            continue
        
        lines = extract_financial_text(path)
        for line in lines:
            print(line)
        print(f'\n[Total relevant lines extracted: {len(lines)}]')


if __name__ == '__main__':
    print('ORACLE CORPORATION (ORCL) - FINANCIAL DATA EXTRACTION')
    print('Fiscal Year ends May 31')
    print('=' * 80)
    
    print('\n\n### ANNUAL REPORTS (10-K) ###\n')
    process_files(ANNUAL_FILES)
    
    print('\n\n### QUARTERLY REPORTS (10-Q) ###\n')
    process_files(QUARTERLY_FILES)
