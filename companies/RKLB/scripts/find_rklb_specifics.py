#!/usr/bin/env python3
"""Find specific financial data sentences from RKLB filings."""
import re

with open('/tmp/rklb_clean.txt', 'r') as f:
    lines = f.readlines()

# Patterns for actual financial sentences with numbers
PATTERNS = [
    r'revenue (?:was|were|increased|decreased|grew|of|totaled)',
    r'revenues (?:were|increased|decreased|grew|of|totaled)',
    r'\$\d+[\.,]\d+ million',
    r'\$\d{1,3}(?:,\d{3})+ (?:million|billion)',
    r'backlog (?:totaled|was|of)',
    r'net loss (?:was|of|totaled)',
    r'gross (?:profit|margin) (?:was|of|increased|decreased)',
    r'(?:launched|launch) \d+ (?:vehicles|missions|rockets)',
    r'\d+ launches? (?:in|for|during)',
    r'\d+,?\d* (?:full.time|employees|headcount)',
    r'cash and cash equivalents.{0,30}\$',
    r'(?:expect|guidance|outlook).{0,50}\$\d+',
    r'Q[1-4] 20\d\d.{0,30}(?:revenue|guidance)',
    r'second quarter|first quarter|third quarter|fourth quarter.{0,50}\$',
    r'adjusted ebitda',
    r'operating cash flow',
    r'capital expenditure',
    r'neutron (?:first|launch|development|expect)',
    r'reusab.{0,50}stage',
    r'catch.{0,30}stage',
    r'acquisition of .{0,50}(?:million|billion)',
]

current_section = 'Unknown'
results = []
for i, line in enumerate(lines):
    if line.startswith('FILE:'):
        current_section = line.strip()
        continue
    if line.startswith('==='):
        current_section = line.strip()
        continue
    
    ll = line.lower()
    for p in PATTERNS:
        if re.search(p, ll):
            results.append(f"[{current_section}] {line.strip()}")
            break

with open('/tmp/rklb_specifics.txt', 'w') as f:
    f.write('\n'.join(results))

print(f"Found {len(results)} specific financial sentences")
