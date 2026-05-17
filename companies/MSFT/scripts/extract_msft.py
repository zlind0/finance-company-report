#!/usr/bin/env python3
"""Extract key financial data from Microsoft SEC filings (10-K and 10-Q)."""
from bs4 import BeautifulSoup
import os
import glob

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')

files = sorted(glob.glob(os.path.join(RAW_DIR, '*.html')))

KEY_SECTIONS = [
    # Revenue & Profitability
    'revenue', 'net income', 'net loss', 'operating income', 'operating loss',
    'gross margin', 'gross profit', 'cost of revenue', 'cost of goods',
    'earnings per share', 'diluted', 'basic',
    # Segments (historical and current)
    'intelligent cloud', 'more personal computing', 'productivity and business processes',
    'azure', 'office 365', 'linkedin', 'dynamics', 'windows', 'xbox', 'surface',
    'server products', 'enterprise services', 'search advertising',
    # Cloud & AI
    'cloud', 'artificial intelligence', 'ai', 'openai', 'copilot', 'gpt',
    'azure', 'commercial cloud', 'intelligent cloud',
    # Operating expenses
    'research and development', 'sales and marketing', 'general and administrative',
    'stock-based compensation', 'restructuring', 'impairment',
    # Cash & Capital
    'cash flow', 'operating activities', 'capital expenditure', 'capital expenditure',
    'dividend', 'share repurchase', 'buyback', 'treasury stock',
    'debt', 'long-term debt', 'commercial paper',
    # Risk factors
    'risk factor', 'antitrust', 'regulation', 'litigation', 'competition',
    'competition', 'competitor', 'market share',
    # Other
    'subscription', 'license', 'unearned revenue', 'remaining performance obligation',
    'deferred revenue', 'backlog', 'headcount', 'employees', 'workforce',
    'acquisition', 'linkedin', 'activision', 'blizzard', 'nuance',
    'foreign currency', 'exchange rate', 'tax rate', 'effective tax rate',
]

def extract_financial_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

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

for path in files:
    label = os.path.basename(path).replace('.html', '')
    sep = '=' * 80
    print()
    print(sep)
    print(f'FILE: {label} ({path})')
    print(sep)
    lines = extract_financial_text(path)
    for line in lines[:3000]:
        print(line)
    print(f'[Total relevant lines: {len(lines)}]')
