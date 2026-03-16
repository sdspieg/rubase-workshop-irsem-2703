#!/usr/bin/env python3
"""
Verify CLI LLMs slideshow for:
1. Color contrast issues
2. Content fitting on one slide
3. Screen real estate usage
"""

from playwright.sync_api import sync_playwright
import time

def verify_cli_slides():
    """Check all slides in CLI presentation for issues."""

    with sync_playwright() as p:
        print("=== VERIFYING CLI SLIDES ===\n")
        browser = p.chromium.launch(headless=False)  # Show browser to visually verify
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Load the CLI slideshow
        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/cli-llms-guide.html'
        print(f"Loading: {url}")
        page.goto(url, wait_until='networkidle')
        time.sleep(2)

        # Total slides
        total_slides = 16
        issues_found = []

        for slide_num in range(1, total_slides + 1):
            print(f"\n--- Slide {slide_num}/{total_slides} ---")

            # Get current slide
            current_slide = page.query_selector('.slide.active')
            if current_slide:
                # Check 1: Is content scrollable (doesn't fit)?
                slide_height = current_slide.evaluate('el => el.scrollHeight')
                viewport_height = current_slide.evaluate('el => el.clientHeight')

                if slide_height > viewport_height:
                    issue = f"Slide {slide_num}: Content overflows! Scrollable height: {slide_height}px > Viewport: {viewport_height}px"
                    print(f"❌ {issue}")
                    issues_found.append(issue)
                else:
                    print(f"✅ Content fits: {slide_height}px <= {viewport_height}px")

                # Check 2: Screen real estate usage
                content_elements = current_slide.query_selector_all('h1, h2, h3, p, ul, .tool-section, .best-practice, table')
                if len(content_elements) < 3 and slide_num != 1:  # Title slide can be minimal
                    issue = f"Slide {slide_num}: Potentially underutilized (only {len(content_elements)} content elements)"
                    print(f"⚠️ {issue}")
                    issues_found.append(issue)

                # Check 3: Color contrast on dark backgrounds
                # Look for text elements
                text_elements = current_slide.query_selector_all('p, li, td, h3, h4')
                for elem in text_elements[:3]:  # Sample first 3
                    color = elem.evaluate('el => window.getComputedStyle(el).color')
                    bg = elem.evaluate('el => window.getComputedStyle(el).backgroundColor')
                    if 'rgb' in color:
                        # Parse RGB values
                        rgb = color.replace('rgb(', '').replace(')', '').split(',')
                        r, g, b = [int(x.strip()) for x in rgb]
                        # Check if text is too dark (low luminance)
                        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
                        if luminance < 180:  # Dark text on dark background
                            issue = f"Slide {slide_num}: Dark text detected ({color}) - may have contrast issues"
                            print(f"⚠️ {issue}")
                            issues_found.append(issue)
                            break

                # Visual pause to check
                time.sleep(1)

            # Go to next slide
            if slide_num < total_slides:
                page.keyboard.press('ArrowRight')
                time.sleep(0.5)

        print("\n=== SUMMARY ===")
        if issues_found:
            print(f"Found {len(issues_found)} issues:")
            for issue in issues_found:
                print(f"  • {issue}")
        else:
            print("✅ All slides pass verification!")

        print("\n=== VISUAL CHECK ===")
        print("Please visually verify:")
        print("1. No large empty spaces")
        print("2. Text is readable on all slides")
        print("3. Tables and code snippets are visible")

        # Navigate through slides again for visual check
        page.keyboard.press('Home')  # Go to first slide
        for i in range(total_slides):
            print(f"\nSlide {i+1}: Press Enter to continue...")
            input()
            if i < total_slides - 1:
                page.keyboard.press('ArrowRight')

        browser.close()

        return len(issues_found) == 0

if __name__ == "__main__":
    verify_cli_slides()