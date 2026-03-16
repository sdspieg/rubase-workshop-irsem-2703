#!/usr/bin/env python3
"""Check EVERY SINGLE HTML FILE for Home button"""

import os
import glob

def check_file(filepath):
    """Check if file has Home button"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            has_home = '🏠 Home' in content or 'Home</button>' in content or 'Home</a>' in content
            return has_home
    except:
        return False

print("=== CHECKING EVERY HTML FILE ===\n")

# Get ALL HTML files
all_files = glob.glob("/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/**/*.html", recursive=True)
all_files.extend(glob.glob("/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/*.html"))

missing = []
has_nav = []

for filepath in sorted(set(all_files)):
    # Skip node_modules
    if 'node_modules' in filepath:
        continue

    filename = filepath.replace('/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/', '')

    if check_file(filepath):
        has_nav.append(filename)
        print(f"✅ {filename}")
    else:
        missing.append(filename)
        print(f"❌ {filename}")

print("\n" + "="*60)
print(f"MISSING HOME BUTTON ({len(missing)} files):")
print("="*60)
for f in missing:
    print(f"  ❌ {f}")

print("\n" + "="*60)
print(f"SUMMARY: {len(missing)} files MISSING navigation, {len(has_nav)} have it")
print("="*60)