#!/usr/bin/env python3
"""FIX ALL MISSING HOME BUTTONS NOW"""

import os

files_to_fix = [
    "workshop-archives.html",
    "download-materials.html",
    "OpenAlex_Exercise_Instructions.html",
    "modules/openalex/dashboard.html",
    "modules/day2/index.html",
    "modules/exercise/hands-on-exercise.html",
    "modules/exercise/index.html",
    "modules/frame/building-taxonomies.html",
    "modules/frame/index.html",
    # Skip backups and test files
]

nav_html_standalone = """
<!-- Navigation -->
<div style="position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; background: rgba(30, 41, 59, 0.95); padding: 10px 20px; border-radius: 50px; border: 1px solid #334155; backdrop-filter: blur(10px); z-index: 1000;">
    <button onclick="window.location.href='index.html'" style="background: linear-gradient(135deg, #00ffff, #0099ff); color: #0f172a; border: none; padding: 10px 20px; border-radius: 25px; font-weight: 600; cursor: pointer; font-family: 'Titillium Web', sans-serif;">🏠 Home</button>
</div>
"""

nav_html_module = """
<!-- Navigation -->
<div style="position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; background: rgba(30, 41, 59, 0.95); padding: 10px 20px; border-radius: 50px; border: 1px solid #334155; backdrop-filter: blur(10px); z-index: 1000;">
    <button onclick="window.location.href='../../index.html'" style="background: linear-gradient(135deg, #00ffff, #0099ff); color: #0f172a; border: none; padding: 10px 20px; border-radius: 25px; font-weight: 600; cursor: pointer; font-family: 'Titillium Web', sans-serif;">🏠 Home</button>
</div>
"""

def fix_file(filepath):
    """Add navigation to file"""
    full_path = f"/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/{filepath}"

    if not os.path.exists(full_path):
        print(f"  ❌ File not found: {filepath}")
        return False

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has navigation
    if '🏠 Home' in content:
        print(f"  ✓ Already has navigation: {filepath}")
        return False

    # Determine which nav to use based on depth
    if 'modules/' in filepath:
        nav_to_add = nav_html_module
    else:
        nav_to_add = nav_html_standalone

    # Add before </body>
    if '</body>' in content:
        content = content.replace('</body>', nav_to_add + '\n</body>')
    else:
        content += nav_to_add

    # Also add Titillium Web font if missing
    if 'Titillium Web' not in content and '</head>' in content:
        font_link = '<link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap" rel="stylesheet">\n'
        content = content.replace('</head>', font_link + '</head>')

    # Write back
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✅ FIXED: {filepath}")
    return True

print("=" * 60)
print("FIXING ALL MISSING NAVIGATION")
print("=" * 60)

fixed_count = 0
for file in files_to_fix:
    if fix_file(file):
        fixed_count += 1

print("\n" + "=" * 60)
print(f"FIXED {fixed_count} FILES")
print("=" * 60)