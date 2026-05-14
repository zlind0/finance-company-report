import re, os

files = [
    ('FY2021', '/tmp/rklb_fy2021.txt'),
    ('FY2022 10K', '/tmp/rklb_fy2022_10k.txt'),
    ('Q1 2022', '/tmp/rklb_q1_2022.txt'),
    ('Q2 2022', '/tmp/rklb_q2_2022.txt'),
    ('Q3 2022', '/tmp/rklb_q3_2022.txt'),
    ('FY2023 10K', '/tmp/rklb_fy2023_10k.txt'),
    ('Q1 2023', '/tmp/rklb_q1_2023.txt'),
    ('Q2 2023', '/tmp/rklb_q2_2023.txt'),
    ('Q3 2023', '/tmp/rklb_q3_2023.txt'),
    ('FY2024 10K', '/tmp/rklb_fy2024_10k.txt'),
    ('Q1 2024', '/tmp/rklb_q1_2024.txt'),
    ('Q2 2024', '/tmp/rklb_q2_2024.txt'),
    ('Q3 2024', '/tmp/rklb_q3_2024.txt'),
    ('FY2025 10K', '/tmp/rklb_fy2025_10k.txt'),
    ('Q1 2025', '/tmp/rklb_q1_2025.txt'),
    ('Q2 2025', '/tmp/rklb_q2_2025.txt'),
    ('Q3 2025', '/tmp/rklb_q3_2025.txt'),
    ('FY2026 10K', '/tmp/rklb_fy2026_10k.txt'),
    ('Q1 2026', '/tmp/rklb_q1_2026.txt'),
]

KEYWORDS = [
    'revenue', 'launch services', 'space systems', 'cost of revenue',
    'gross profit', 'gross margin', 'operating loss', 'net loss', 'net income',
    'research and development', 'general and administrative',
    'stock-based compensation', 'backlog', 'electron', 'neutron',
    'guidance', 'outlook', 'employees', 'headcount', 'cash and cash',
    'total assets', 'total liabilities', 'adjusted ebitda',
    'spacecraft', 'components', 'solar cell',
    'acquisition', 'sinclair', 'planetary systems', 'advanced space',
    'nasa', 'nro', 'defense', 'government contract',
    'reusab', 'recovery', 'catch', 'helicopter',
    'medium lift', 'neutron development', 'capital expenditure',
    'interest expense', 'convertible', 'dilut', 'shares outstanding',
]

output = []
for label, path in files:
    output.append('\n' + '='*70)
    output.append('=== ' + label + ' ===')
    output.append('='*70)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    shown = set()
    for i, line in enumerate(lines):
        ll = line.lower()
        for kw in KEYWORDS:
            if kw in ll and len(line.strip()) > 3:
                start = max(0, i-1)
                end = min(len(lines), i+3)
                for j in range(start, end):
                    if j not in shown:
                        output.append(lines[j].rstrip())
                        shown.add(j)
                break

with open('/tmp/rklb_fin.txt', 'w') as f:
    f.write('\n'.join(output))
print('Done. ' + str(len(output)) + ' lines written.')
