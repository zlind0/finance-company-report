#!/usr/bin/env python3
"""Extract key financial and strategic text from Micron SEC filings."""

from bs4 import BeautifulSoup
import os


BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw_reports')


all_files = sorted(
    [name for name in os.listdir(BASE_DIR) if name.endswith('.html')],
    key=lambda name: name.split('_')[1].replace('.html', '')
)


files = []
for filename in all_files:
    form_type, filing_date = filename.replace('.html', '').split('_', 1)
    year = filing_date[:4]
    if form_type == '10-K':
        label = f'FY{int(year) - 1} Annual (10-K filed {filing_date})'
    else:
        label = f'Quarterly {filing_date} (10-Q)'
    files.append((label, os.path.join(BASE_DIR, filename)))


KEY_SECTIONS = [
    'revenue', 'net sales', 'gross margin', 'gross profit', 'operating income',
    'operating loss', 'net income', 'net loss', 'cash flow', 'operating cash flow',
    'free cash flow', 'capital expenditures', 'capex', 'inventory', 'days of inventory',
    'bit shipments', 'average selling price', 'asp', 'wafer', 'wafer starts',
    'utilization', 'underutilization', 'cost of goods sold', 'impairment', 'restructuring',
    'research and development', 'selling general and administrative', 'sg&a',
    'dram', 'nand', 'nor', '3d nand', 'ssds', 'ssd', 'managed nand', 'hbm',
    'ddr5', 'lpddr', 'gddr', 'high bandwidth memory', 'high-bandwidth memory',
    'data center', 'cloud', 'server', 'pc', 'client', 'mobile', 'automotive',
    'industrial', 'consumer', 'enterprise', 'graphics', 'embedded', 'networking',
    'segment', 'compute and networking', 'storage', 'mobile business unit',
    'business units', 'trade restrictions', 'china', 'taiwan', 'singapore', 'japan',
    'competition', 'competitive', 'samsung', 'sk hynix', 'western digital', 'kioxia',
    'supply chain', 'pricing', 'cyclical', 'cycle', 'downturn', 'recovery',
    'ai', 'artificial intelligence', 'hpc', 'high performance computing',
    'share repurchase', 'dividend', 'debt', 'convertible', 'liquidity',
    'capital resources', 'risk factor', 'risk factors', 'tax', 'income tax',
    'customer', 'customers', 'concentration', 'geopolitical', 'export control',
    'sanctions', 'tariff', 'packaging', 'assembly', 'test', 'advanced packaging',
    'technology node', '1-alpha', '1-beta', '1-gamma', '176-layer', '232-layer',
    '1z', '1a', '1b', '1c', 'euv', 'yield', 'mix', 'pricing environment',
    'automotive qualified', 'long-term agreement', 'lta', 'hbm3e', 'ddr4', 'ddr5',
]


def extract_financial_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as handle:
        soup = BeautifulSoup(handle.read(), 'html.parser')

    for tag in soup(['script', 'style']):
        tag.decompose()

    text = soup.get_text(separator='\n', strip=True)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    context_window = 4
    matched_indices = set()

    for index, line in enumerate(lines):
        lower_line = line.lower()
        for keyword in KEY_SECTIONS:
            if keyword.lower() in lower_line:
                start = max(0, index - context_window)
                end = min(len(lines), index + context_window + 1)
                for match_index in range(start, end):
                    matched_indices.add(match_index)
                break

    result = []
    previous_index = -1
    for index in sorted(matched_indices):
        if previous_index >= 0 and index > previous_index + 1:
            result.append('...')
        result.append(lines[index])
        previous_index = index

    return result


OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'mu_extracted.txt')
with open(OUT_PATH, 'w', encoding='utf-8') as out:
    for label, path in files:
        separator = '=' * 80
        out.write('\n')
        out.write(separator + '\n')
        out.write(f'FILE: {label}\n')
        out.write(f'PATH: {path}\n')
        out.write(separator + '\n')
        try:
            lines = extract_financial_text(path)
            cap = 350000
            for line in lines[:cap]:
                out.write(line + '\n')
            if len(lines) > cap:
                out.write(f'[... truncated, {len(lines) - cap} more lines ...]\n')
            out.write(f'[Total relevant lines: {len(lines)}]\n')
        except Exception as exc:
            out.write(f'ERROR: {exc}\n')

print(f'Done. Output written to {OUT_PATH}')
print(f'File size: {os.path.getsize(OUT_PATH):,} bytes')