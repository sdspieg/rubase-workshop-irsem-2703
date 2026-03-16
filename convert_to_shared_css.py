#!/usr/bin/env python3
"""
Convert all slideshow HTML files to use shared CSS stylesheet
instead of embedded styles.
"""

import os
import re
from pathlib import Path

def convert_html_to_shared_css(file_path):
    """Convert a single HTML file to use shared CSS."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the title for reference
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else 'Unknown'
    print(f"Converting: {title}")

    # Find the <style> block and remove it
    style_pattern = r'<style>.*?</style>'
    content_without_styles = re.sub(style_pattern, '', content, flags=re.DOTALL)

    # Add the CSS link in the <head> section
    css_link = '    <link rel="stylesheet" href="slides.css">'

    # Find the </head> tag and insert CSS link before it
    head_pattern = r'(\s*)</head>'
    replacement = r'\1' + css_link + '\n\\1</head>'

    final_content = re.sub(head_pattern, replacement, content_without_styles)

    # Write the converted content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"✅ Converted {file_path}")

def main():
    """Convert all slideshow files in the analyze module."""

    analyze_dir = Path("modules/analyze")

    # Find all HTML files that are slideshows
    html_files = [
        "cli-llms-guide.html",
        "deep-research-guide.html",
        "ottoman-bank-case-study.html",
        "wacko-presentation.html",
        "welcome-day3.html"
    ]

    print("=== Converting Slideshows to Shared CSS ===\n")

    for html_file in html_files:
        file_path = analyze_dir / html_file
        if file_path.exists():
            convert_html_to_shared_css(file_path)
        else:
            print(f"❌ File not found: {file_path}")

    print(f"\n✅ Conversion complete! All slideshows now use slides.css")
    print("🎯 Benefits:")
    print("  • Consistent styling across all presentations")
    print("  • Easy global style updates")
    print("  • Smaller file sizes")
    print("  • Maintainable codebase")

if __name__ == "__main__":
    main()