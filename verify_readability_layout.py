#!/usr/bin/env python3
"""
Comprehensive verification of readability AND layout for Ottoman Bank presentation.
Checks:
1. Text legibility (actual contrast on rendered page)
2. Content fits on one screen (no scrolling needed)
3. Screen real estate usage
"""

from playwright.sync_api import sync_playwright
import time

def verify_slide_readability_and_layout():
    """Verify each slide for readability and proper layout."""

    with sync_playwright() as p:
        print("=== COMPREHENSIVE SLIDE VERIFICATION ===\n")
        browser = p.chromium.launch(headless=False)  # Set to False to actually SEE the issues
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/ottoman-bank-case-study.html'
        print(f"Loading {url}\n")
        page.goto(url, wait_until='networkidle')
        time.sleep(3)

        # Get total slides
        slides = page.query_selector_all('.slide')
        total_slides = len(slides)
        print(f"Total slides to verify: {total_slides}\n")

        issues = []

        for i in range(total_slides):
            slide_num = i + 1
            print(f"{'='*60}")
            print(f"SLIDE {slide_num}/{total_slides}")
            print(f"{'='*60}")

            # Navigate to slide
            if i > 0:
                page.keyboard.press('ArrowRight')
                time.sleep(0.5)

            # Get current slide
            current_slide = page.query_selector('.slide.active')

            if current_slide:
                # 1. CHECK SCROLLABILITY
                slide_height = current_slide.evaluate('el => el.scrollHeight')
                client_height = current_slide.evaluate('el => el.clientHeight')
                has_overflow = slide_height > client_height

                if has_overflow:
                    overflow_px = slide_height - client_height
                    print(f"❌ OVERFLOW: Content exceeds viewport by {overflow_px}px")
                    issues.append(f"Slide {slide_num}: Overflow {overflow_px}px")
                else:
                    print(f"✅ Content fits: {slide_height}px content in {client_height}px viewport")

                # 2. CHECK SCREEN REAL ESTATE USAGE
                viewport_height = page.evaluate('() => window.innerHeight')
                usage_percent = (client_height / viewport_height) * 100

                if usage_percent < 70:
                    print(f"⚠️ LOW USAGE: Only using {usage_percent:.1f}% of screen height")
                    issues.append(f"Slide {slide_num}: Low screen usage {usage_percent:.1f}%")
                elif usage_percent > 95:
                    print(f"⚠️ TOO FULL: Using {usage_percent:.1f}% - may overflow on smaller screens")
                else:
                    print(f"✅ Good usage: {usage_percent:.1f}% of viewport")

                # 3. CHECK TEXT READABILITY (actual computed colors)
                # Get background
                bg_computed = current_slide.evaluate('''el => {
                    const style = window.getComputedStyle(el);
                    return {
                        bg: style.backgroundColor,
                        bgImage: style.backgroundImage
                    };
                }''')

                print(f"\nBackground: {bg_computed['bg'][:50]}...")

                # Check text elements
                text_elements = [
                    ('h1', 'Main heading'),
                    ('h2', 'Subheading'),
                    ('h3', 'Section heading'),
                    ('p', 'Body text'),
                    ('li', 'List item'),
                    ('td', 'Table cell')
                ]

                for selector, name in text_elements:
                    elements = current_slide.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        # Check first element
                        el = elements[0]
                        computed = el.evaluate('''el => {
                            const style = window.getComputedStyle(el);
                            return {
                                color: style.color,
                                fontSize: style.fontSize,
                                fontWeight: style.fontWeight,
                                opacity: style.opacity,
                                textShadow: style.textShadow
                            };
                        }''')

                        # Parse RGB values
                        import re
                        color_match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', computed['color'])
                        if color_match:
                            r, g, b = map(int, color_match.groups())

                            # Check for low contrast combinations
                            is_dark_on_dark = r < 150 and g < 150 and b < 150
                            is_blue_on_blue = b > 150 and r < 200 and g < 200

                            status = "✅"
                            if is_dark_on_dark:
                                status = "❌ DARK ON DARK"
                                issues.append(f"Slide {slide_num}: {name} is too dark")
                            elif is_blue_on_blue:
                                status = "⚠️ BLUE ON BLUE"
                                issues.append(f"Slide {slide_num}: {name} lacks contrast")

                            print(f"{name}: {computed['color']} {status}")
                            if computed['textShadow'] != 'none':
                                print(f"  Shadow: {computed['textShadow'][:30]}...")

                # 4. CHECK SPECIFIC PROBLEM AREAS
                # Tables
                tables = current_slide.query_selector_all('table')
                if tables:
                    for table in tables:
                        table_width = table.evaluate('el => el.scrollWidth')
                        table_container = table.evaluate('el => el.parentElement.clientWidth')
                        if table_width > table_container:
                            print(f"❌ TABLE OVERFLOW: {table_width}px table in {table_container}px container")
                            issues.append(f"Slide {slide_num}: Table overflow")

                # Code blocks
                code_blocks = current_slide.query_selector_all('pre, code')
                if code_blocks:
                    for code in code_blocks:
                        code_width = code.evaluate('el => el.scrollWidth')
                        code_container = code.evaluate('el => el.parentElement.clientWidth')
                        if code_width > code_container:
                            print(f"❌ CODE OVERFLOW: {code_width}px code in {code_container}px container")
                            issues.append(f"Slide {slide_num}: Code overflow")

                print()

        # SUMMARY
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)

        if issues:
            print(f"\n❌ FOUND {len(issues)} ISSUES:\n")
            for issue in issues:
                print(f"  • {issue}")

            print("\n📋 RECOMMENDATIONS:")
            print("1. For overflow issues:")
            print("   - Reduce font sizes")
            print("   - Decrease padding/margins")
            print("   - Split content across multiple slides")
            print("\n2. For readability issues:")
            print("   - Use pure white (#ffffff) for body text")
            print("   - Use bright colors (cyan #00ffff, lime #00ff00) for accents")
            print("   - Add stronger text shadows")
            print("\n3. For screen usage:")
            print("   - Increase slide height to 94-95vh")
            print("   - Reduce top/bottom padding")
        else:
            print("\n✅ All slides pass readability and layout checks!")

        input("\nPress Enter to close browser...")
        browser.close()

        return issues

if __name__ == "__main__":
    issues = verify_slide_readability_and_layout()

    if issues:
        print(f"\n\n⚠️ Action needed: {len(issues)} issues require fixes")