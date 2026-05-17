#!/usr/bin/env python3
from bs4 import BeautifulSoup
import glob
import os
import re

# Auto-discover all HTML files in raw_reports/
raw_dir = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')
files_10k = sorted(glob.glob(os.path.join(raw_dir, '10-K_*.html')))
files_10q = sorted(glob.glob(os.path.join(raw_dir, '10-Q_*.html')))

files = []
for f in files_10k:
    date = os.path.basename(f).replace('10-K_', '').replace('.html', '')
    files.append((f'FY{date[:4]} 10-K ({date})', f))
for f in files_10q:
    date = os.path.basename(f).replace('10-Q_', '').replace('.html', '')
    year = date[:4]
    month = int(date[5:7])
    if month <= 3:
        q = 'Q4'
        yr = str(int(year) - 1)
    elif month <= 6:
        q = 'Q1'
        yr = year
    elif month <= 9:
        q = 'Q2'
        yr = year
    else:
        q = 'Q3'
        yr = year
    files.append((f'{q} {yr} ({date})', f))

# Extensive keywords for Take-Two Interactive / gaming industry
KEY_SECTIONS = [
    # Core financials
    'revenue', 'net income', 'net loss', 'operating income', 'operating loss',
    'cost of revenue', 'gross profit', 'gross margin',
    'research and development', 'sales and marketing',
    'general and administrative', 'stock-based compensation',
    'depreciation and amortization', 'impairment', 'goodwill',
    'income tax', 'interest income', 'interest expense',
    'cash flow', 'liquidity', 'capital resources',
    'earnings per share', 'diluted', 'weighted average',
    'balance sheet', 'total assets', 'total liabilities',
    'shareholders', 'equity', 'deficit',

    # Gaming-specific business metrics
    'bookings', 'deferred revenue', 'revenue recognized',
    'recurrent consumer spending', 'virtual currency', 'in-game',
    'downloadable content', 'DLC', 'microtransaction',
    'digitally delivered', 'digital revenue', 'digital sales',
    'packaged goods', 'physical', 'physical retail',
    'engagement', 'monthly active', 'MAU', 'daily active', 'DAU',
    'average revenue per user', 'ARPU', 'lifetime value',
    'user acquisition', 'advertising revenue', 'advertising',
    'free-to-play', 'free to play', 'F2P', 'premium',

    # Games and franchises
    'Grand Theft Auto', 'GTA', 'Red Dead Redemption',
    'NBA 2K', 'WWE 2K', 'Borderlands', 'Civilization',
    'XCOM', 'BioShock', 'Max Payne', 'L.A. Noire',
    'Kerbal Space Program', 'PGA Tour',
    'Zynga', 'FarmVille', 'Words With Friends',
    'Empires & Puzzles', 'CSR Racing', 'Toon Blast', 'Toy Blast',
    'Rollic', 'Hypercasual', 'Merge Dragons', 'Zynga Poker',

    # Business segments and platforms
    'segment', 'reporting segment',
    'console', 'PC', 'mobile', 'handheld',
    'PlayStation', 'Xbox', 'Nintendo', 'Switch', 'Steam',
    'iOS', 'Android', 'Google Play', 'App Store',
    'Rockstar Games', '2K', 'Private Division',

    # Corporate strategy
    'acquisition', 'acquired', 'merger', 'integration',
    'licensing', 'intellectual property', 'IP',
    'development', 'pipeline', 'title', 'release',
    'studio', 'headcount', 'employees', 'workforce',
    'restructuring', 'cost reduction', 'efficiency',
    'share repurchase', 'buyback', 'dividend',
    'debt', 'credit facility', 'term loan', 'revolving',
    'risk factor', 'competition', 'seasonal',

    # Zynga-specific (post-acquisition)
    'Zynga', 'mobile gaming', 'mobile revenue',
    'user acquisition cost', 'UAC', 'return on ad spend', 'ROAS',
    'network effects', 'social gaming', 'live services',
    'platform fees', 'Apple', 'Google', 'platform commission',

    # Financial metrics
    'adjusted', 'non-GAAP', 'EBITDA', 'adjusted EBITDA',
    'operating margin', 'net margin', 'return on',
    'capital expenditure', 'capex', 'intangible',
    'amortization of acquisition', 'purchase price allocation',
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

# Write output to file
output_path = os.path.join(os.path.dirname(__file__), '..', 'ttwo_extracted.txt')
with open(output_path, 'w', encoding='utf-8') as out:
    for label, path in files:
        sep = '=' * 80
        out.write(f'\n{sep}\n')
        out.write(f'FILE: {label} ({path})\n')
        out.write(f'{sep}\n')
        try:
            lines = extract_financial_text(path)
            for line in lines[:3000]:
                out.write(line + '\n')
            out.write(f'[Total relevant lines: {len(lines)}]\n')
        except Exception as e:
            out.write(f'[ERROR: {e}]\n')

print(f'Extraction complete. Output: {output_path}')
print(f'Processed {len(files)} files.')
