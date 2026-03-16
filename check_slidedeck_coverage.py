#!/usr/bin/env python3
"""
Check if all slidedecks are properly linked
"""

import os
import re
from pathlib import Path

# All module HTML files found
all_modules = [
    'modules/analyze/cli-llms-guide.html',
    'modules/analyze/deep-research-guide.html',
    'modules/analyze/llm-selection-guide.html',
    'modules/analyze/ottoman-bank-case-study.html',
    'modules/analyze/wacko-presentation.html',
    'modules/analyze/welcome-day3.html',
    'modules/cartography/index.html',
    'modules/discover/index.html',
    'modules/exercise/index.html',
    'modules/frame/index.html',
    'modules/mdtdf-guide/index.html',
    'modules/openalex/index.html',
    'modules/resources/index.html',
    'modules/techhelp/index.html',
    'modules/welcome/index.html',
    'modules/welcome/welcome-slides.html',
    'modules/workshop-overview/index.html'
]

# Read index.html to find what's linked
with open('index.html', 'r') as f:
    content = f.read()

# Find all module links
linked_modules = re.findall(r'href=[\'"]modules/([^\'"\s]+)[\'"]', content)
linked_modules += re.findall(r'window\.location\.href=[\'"]modules/([^\'"\s]+)[\'"]', content)

# Normalize paths
linked_paths = [f'modules/{path}' for path in linked_modules if not path.startswith('mdviewer')]

print("=== SLIDEDECK COVERAGE ANALYSIS ===\n")

print("📚 ALL SLIDEDECKS/MODULES FOUND:")
for module in all_modules:
    if 'backup' not in module and 'old-do-not-use' not in module:
        print(f"  • {module}")

print("\n✅ CURRENTLY LINKED IN INDEX.HTML:")
unique_linked = sorted(set(linked_paths))
for link in unique_linked:
    if os.path.exists(link):
        print(f"  • {link}")

print("\n❌ NOT LINKED (MISSING):")
missing = []
for module in all_modules:
    if 'backup' not in module and 'old-do-not-use' not in module and 'index-' not in module:
        if module not in unique_linked:
            missing.append(module)
            print(f"  • {module}")

if not missing:
    print("  None - all modules are linked!")

print("\n📊 SUMMARY BY DAY:\n")

# Day 1 modules
print("Day 1 - DISCOVER:")
day1_linked = [l for l in unique_linked if 'welcome' in l or 'openalex' in l or 'resources' in l or 'workshop-overview' in l]
for link in day1_linked:
    print(f"  ✓ {link}")

print("\nDay 2 - FRAME:")
day2_linked = [l for l in unique_linked if 'cartography' in l or 'frame' in l or 'exercise' in l]
for link in day2_linked:
    print(f"  ✓ {link}")

print("\nDay 3 - ANALYZE:")
day3_linked = [l for l in unique_linked if 'analyze/' in l]
for link in day3_linked:
    print(f"  ✓ {link}")

print("\n🔍 SPECIFIC MISSING SLIDEDECKS:")
critical_missing = [
    ('modules/analyze/llm-selection-guide.html', 'LLM Selection Guide - Important for Day 3'),
    ('modules/analyze/welcome-day3.html', 'Day 3 Welcome Slides'),
    ('modules/welcome/welcome-slides.html', 'Welcome Slides for Day 1'),
    ('modules/mdtdf-guide/index.html', 'MD-TDF Guide'),
    ('modules/discover/index.html', 'Discover Module')
]

for path, description in critical_missing:
    if path in missing:
        print(f"  ⚠️  {description}: {path}")

print("\n📝 RECOMMENDATION:")
if missing:
    print("  Add the missing slidedecks to the appropriate day's sidebar or content cards.")