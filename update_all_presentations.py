#!/usr/bin/env python3
"""Update all presentations to use the unified presentation-styles.css"""

import os
import glob
import re

def update_presentation(filepath):
    """Update a single presentation HTML file to use the unified CSS"""

    # Skip if already using presentation-styles.css
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'presentation-styles.css' in content:
        print(f"  ✓ Already updated: {os.path.basename(filepath)}")
        return False

    # Calculate relative path to CSS file
    depth = filepath.count(os.sep) - filepath.replace('rubase-workshop-fletcher-2603/', '').count(os.sep)
    if 'modules/welcome' in filepath:
        css_path = '../../presentation-styles.css'
    elif 'modules/openalex' in filepath:
        css_path = '../../presentation-styles.css'
    elif 'modules/analyze' in filepath:
        css_path = '../../presentation-styles.css'
    else:
        css_path = 'presentation-styles.css'

    # Add link to presentation-styles.css before </head>
    if '</head>' in content:
        # Add the CSS link
        css_link = f'    <link rel="stylesheet" href="{css_path}">\n'

        # Also add Titillium Web font import if not present
        if 'Titillium Web' not in content:
            font_link = '    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap" rel="stylesheet">\n'
            content = content.replace('</head>', font_link + css_link + '</head>')
        else:
            content = content.replace('</head>', css_link + '</head>')

        # Update any inline font-family declarations to use Titillium Web
        content = re.sub(
            r'font-family:\s*["\']?(?:Times New Roman|Arial|Georgia|Verdana|Comic Sans)["\']?[^;]*;',
            "font-family: 'Titillium Web', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
            content,
            flags=re.IGNORECASE
        )

        # Write the updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ Updated: {os.path.basename(filepath)}")
        return True
    else:
        print(f"  ⚠️  No </head> tag found: {os.path.basename(filepath)}")
        return False

def main():
    presentations = [
        # Day 1 - Welcome
        "modules/welcome/welcome-slides.html",
        "modules/welcome/welcome-setup.html",
        "modules/welcome/index.html",

        # Day 2 - OpenAlex
        "modules/openalex/index.html",
        "modules/openalex/openalex-explorer.html",
        "modules/openalex/dashboard.html",

        # Day 3 - Analyze
        "modules/analyze/welcome-day3.html",
        "modules/analyze/llm-selection-guide.html",
        "modules/analyze/ottoman-bank-case-study.html",
        "modules/analyze/wacko-presentation.html",
        "modules/analyze/cli-llms-guide.html",
        "modules/analyze/deep-research-guide.html",
        "modules/analyze/index.html",
    ]

    print("=" * 60)
    print("UPDATING ALL PRESENTATIONS TO USE presentation-styles.css")
    print("=" * 60)

    updated_count = 0

    print("\n📚 DAY 1 - WELCOME MODULE:")
    for pres in presentations[:3]:
        if os.path.exists(pres):
            if update_presentation(pres):
                updated_count += 1
        else:
            print(f"  ❌ File not found: {pres}")

    print("\n📚 DAY 2 - OPENALEX MODULE:")
    for pres in presentations[3:6]:
        if os.path.exists(pres):
            if update_presentation(pres):
                updated_count += 1
        else:
            print(f"  ❌ File not found: {pres}")

    print("\n📚 DAY 3 - ANALYZE MODULE:")
    for pres in presentations[6:]:
        if os.path.exists(pres):
            if update_presentation(pres):
                updated_count += 1
        else:
            print(f"  ❌ File not found: {pres}")

    print("\n" + "=" * 60)
    print(f"SUMMARY: {updated_count} presentations updated")
    print("=" * 60)

    if updated_count > 0:
        print("\n✨ All presentations now use unified Titillium Web styling!")
        print("Remember to commit and push these changes.")

if __name__ == "__main__":
    main()