#!/usr/bin/env python3
"""Extract actual financial numbers from RKLB clean text."""
import re

# Read the clean file
with open('/tmp/rklb_clean.txt', 'r') as f:
    content = f.read()

# Split by FILE sections
sections = re.split(r'={80}\nFILE: ([^\n]+)\n={80}', content)

# sections[0] is before first FILE, then alternating: label, content
results = {}
for i in range(1, len(sections), 2):
    if i+1 < len(sections):
        label = sections[i]
        text = sections[i+1]
        results[label] = text

# For each section, find lines with actual financial data
NUMBER_PATTERNS = [
    r'\$\s*[\d,]+',   # dollar amounts
    r'[\d,]+\s*million',  # n million
    r'[\d,]+\s*billion',  # n billion
    r'[\d.]+%',           # percentages
]

KEY_TERMS = [
    'revenue', 'revenues', 'launch services revenue', 'space systems revenue',
    'cost of revenues', 'gross profit', 'gross margin',
    'operating loss', 'net loss', 'net income',
    'research and development', 'general and administrative',
    'stock-based compensation', 'adjusted ebitda',
    'backlog', 'employees', 'headcount', 'cash and cash equivalents',
    'total assets', 'capital expenditure', 'interest expense',
    'guidance', 'outlook', 'launch cadence', 'launches',
    'electron launch', 'neutron', 'photon',
    'revenue increased', 'revenue decreased', 'revenue grew',
    'operating cash', 'depreciation', 'amortization',
    'diluted shares', 'shares outstanding',
]

with open('/tmp/rklb_numbers.txt', 'w') as out:
    for label, text in results.items():
        out.write(f"\n{'='*70}\n=== {label} ===\n{'='*70}\n")
        lines = text.split('\n')
        for line in lines:
            ll = line.lower().strip()
            if not ll or len(ll) < 5:
                continue
            # Skip XBRL metadata
            if re.match(r'^[a-z0-9\-_:\.]+$', ll) and ':' in ll:
                continue
            if re.match(r'^\d{4}-\d{2}-\d{2}$', ll):
                continue
            # Check if it contains a number pattern AND a key term
            has_number = any(re.search(p, ll) for p in NUMBER_PATTERNS)
            has_term = any(t in ll for t in KEY_TERMS)
            if has_term or has_number:
                out.write(line.strip() + '\n')

print("Done.")
import subprocess
r = subprocess.run(['wc', '-l', '/tmp/rklb_numbers.txt'], capture_output=True, text=True)
print(r.stdout.strip())
