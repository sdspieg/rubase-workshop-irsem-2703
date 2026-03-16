#!/usr/bin/env python3
"""
Analyze contrast ratios for all text elements in Ottoman Bank presentation.
WCAG AA requires 4.5:1 for normal text, 3:1 for large text.
"""

from playwright.sync_api import sync_playwright
import time
import re

def rgb_to_hex(rgb_string):
    """Convert rgb(r, g, b) or rgba(r, g, b, a) string to hex."""
    match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', rgb_string)
    if match:
        r, g, b = map(int, match.groups()[:3])
        return f"#{r:02x}{g:02x}{b:02x}"
    return rgb_string

def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def calculate_luminance(rgb):
    """Calculate relative luminance."""
    r, g, b = [x/255.0 for x in rgb]
    r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
    g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
    b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calculate_contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors."""
    # Convert to RGB if needed
    if isinstance(color1, str):
        if color1.startswith('#'):
            rgb1 = hex_to_rgb(color1)
        elif color1.startswith('rgb'):
            hex1 = rgb_to_hex(color1)
            rgb1 = hex_to_rgb(hex1)
        else:
            return 0
    else:
        rgb1 = color1

    if isinstance(color2, str):
        if color2.startswith('#'):
            rgb2 = hex_to_rgb(color2)
        elif color2.startswith('rgb'):
            hex2 = rgb_to_hex(color2)
            rgb2 = hex_to_rgb(hex2)
        else:
            return 0
    else:
        rgb2 = color2

    l1 = calculate_luminance(rgb1)
    l2 = calculate_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)

def analyze_contrast():
    """Analyze contrast ratios for all text elements."""

    # Expected colors based on our design
    backgrounds = {
        'slide_bg': '#1a2a4a',  # Dark blue slide background
        'slide_bg_light': '#243655',  # Lighter part of gradient
        'box_bg': '#2a4a5a',  # Box backgrounds
        'alert_bg': '#4a7c8c'  # Alert box background
    }

    text_colors = {
        'h1': '#87ceeb',  # Sky blue
        'h2': '#7db8da',  # Light blue
        'h3': '#c0d4e0',  # Soft gray-blue
        'p': '#c0d4e0',   # Body text
        'white': '#ffffff',
        'black': '#000000'
    }

    print("=== CONTRAST ANALYSIS ===\n")
    print("WCAG AA Requirements:")
    print("- Normal text: 4.5:1 minimum")
    print("- Large text (18pt+): 3:1 minimum")
    print("- WCAG AAA: 7:1 for normal, 4.5:1 for large\n")

    issues = []

    # Analyze main text combinations
    combos = [
        ('h1 on dark blue', text_colors['h1'], backgrounds['slide_bg'], 3.0),  # Large text
        ('h2 on dark blue', text_colors['h2'], backgrounds['slide_bg'], 3.0),  # Large text
        ('h3 on dark blue', text_colors['h3'], backgrounds['slide_bg'], 4.5),  # Normal text
        ('body text on dark blue', text_colors['p'], backgrounds['slide_bg'], 4.5),  # Normal text
        ('h3 on box bg', text_colors['h3'], backgrounds['box_bg'], 4.5),
        ('body text on box bg', text_colors['p'], backgrounds['box_bg'], 4.5),
        ('h1 on alert bg', text_colors['h1'], backgrounds['alert_bg'], 3.0),
    ]

    for name, fg, bg, required in combos:
        ratio = calculate_contrast_ratio(fg, bg)
        status = "✅ PASS" if ratio >= required else "❌ FAIL"

        print(f"{name}:")
        print(f"  Foreground: {fg}")
        print(f"  Background: {bg}")
        print(f"  Contrast: {ratio:.2f}:1 (required: {required}:1) {status}")

        if ratio < required:
            issues.append({
                'element': name,
                'fg': fg,
                'bg': bg,
                'ratio': ratio,
                'required': required
            })
        print()

    # Now check live site
    print("\n=== LIVE SITE ANALYSIS ===\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/ottoman-bank-case-study.html'
        page.goto(url, wait_until='networkidle')
        time.sleep(2)

        # Sample a few slides
        for slide_num in [1, 3, 15, 16]:
            print(f"Slide {slide_num}:")

            # Navigate to slide
            for _ in range(slide_num - 1):
                page.keyboard.press('ArrowRight')
                time.sleep(0.2)

            # Get slide background
            slide = page.query_selector('.slide.active')
            if slide:
                computed_bg = slide.evaluate('el => window.getComputedStyle(el).backgroundColor')

                # Check key elements
                elements = [
                    ('h1', 'h1'),
                    ('h2', 'h2'),
                    ('h3', 'h3'),
                    ('paragraph', 'p'),
                ]

                for name, selector in elements:
                    el = slide.query_selector(selector)
                    if el:
                        color = el.evaluate('el => window.getComputedStyle(el).color')
                        font_size = el.evaluate('el => window.getComputedStyle(el).fontSize')

                        # Calculate actual contrast
                        if 'rgb' in color and 'rgb' in computed_bg:
                            actual_ratio = calculate_contrast_ratio(color, computed_bg)

                            # Determine requirement based on size
                            size_px = float(font_size.replace('px', ''))
                            required = 3.0 if size_px >= 18 else 4.5

                            status = "✅" if actual_ratio >= required else "❌"
                            print(f"  {name}: {actual_ratio:.2f}:1 {status} (size: {font_size})")

                            if actual_ratio < required:
                                issues.append({
                                    'slide': slide_num,
                                    'element': name,
                                    'ratio': actual_ratio,
                                    'required': required
                                })

            # Reset to first slide
            page.reload()
            time.sleep(1)
            print()

        browser.close()

    # Recommendations
    print("\n=== RECOMMENDATIONS ===\n")

    if issues:
        print("⚠️ CONTRAST ISSUES FOUND:\n")
        for issue in issues:
            print(f"- {issue.get('element', 'Unknown')}: {issue['ratio']:.2f}:1 (needs {issue['required']}:1)")

        print("\nSUGGESTED FIXES:")
        print("1. Lighten text colors for better contrast:")
        print("   - h1: #87ceeb → #a0d8ef (lighter sky blue)")
        print("   - h2: #7db8da → #9dc8e8 (lighter blue)")
        print("   - h3/p: #c0d4e0 → #e0e8f0 (lighter gray)")
        print("\n2. Or darken backgrounds:")
        print("   - Slide bg: #1a2a4a → #0f1a2a (darker blue)")
        print("\n3. Consider using pure white (#ffffff) for critical text")
    else:
        print("✅ All text elements meet WCAG AA contrast requirements!")

    return issues

if __name__ == "__main__":
    issues = analyze_contrast()

    if issues:
        print(f"\n❌ Found {len(issues)} contrast issues that need fixing.")
    else:
        print("\n✅ All contrast ratios are acceptable!")