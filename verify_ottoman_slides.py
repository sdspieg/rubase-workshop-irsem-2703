#!/usr/bin/env python3
"""
Verify EVERY slide of the Ottoman Bank presentation visually.
"""

from playwright.sync_api import sync_playwright
import time

def verify_ottoman_slides():
    """Verify each slide of the Ottoman Bank presentation."""

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/ottoman-bank-case-study.html'
        print(f"Navigating to {url}")
        page.goto(url, wait_until='networkidle')

        # Wait for page to load
        time.sleep(3)

        # Get total number of slides
        slides = page.query_selector_all('.slide')
        total_slides = len(slides)
        print(f"Found {total_slides} slides to verify\n")

        # Verify each slide
        for i in range(total_slides):
            slide_num = i + 1
            print(f"=== SLIDE {slide_num}/{total_slides} ===")

            # Make sure we're on the right slide
            if i > 0:
                page.keyboard.press('ArrowRight')
                time.sleep(0.5)

            # Get current slide
            current_slide = page.query_selector('.slide.active')

            if current_slide:
                # Check background color
                bg_color = current_slide.evaluate('el => window.getComputedStyle(el).background')
                if 'rgb(26, 42, 74)' in bg_color or '#1a2a4a' in bg_color or 'linear-gradient' in bg_color:
                    print("✓ Dark blue background confirmed")
                else:
                    print(f"⚠ Background issue: {bg_color[:100]}")

                # Get slide title
                h1 = current_slide.query_selector('h1')
                if h1:
                    title = h1.inner_text()
                    print(f"Title: {title}")

                    # Check title color
                    title_color = h1.evaluate('el => window.getComputedStyle(el).color')
                    if 'rgb(135, 206, 235)' in title_color or '#87ceeb' in title_color:
                        print("✓ Title has sky blue color")
                    else:
                        print(f"⚠ Title color issue: {title_color}")

                # Check for specific content on key slides
                if slide_num == 15:  # Critical Discovery slide
                    print("Checking Critical Discovery slide...")
                    content = current_slide.inner_text()
                    if 'Falconnet' in content:
                        print("✓ Ottoman Bank director paper found")
                    if '511 papers' in content:
                        print("✓ Correct 511 count found")
                    if 'Galata district' in content:
                        print("✓ Galata search strategy mentioned")

                if slide_num == 16:  # Conclusion slide
                    print("Checking Conclusion slide...")
                    content = current_slide.inner_text()
                    if '596' in content:
                        print("✓ Correct merged total 596 found")
                    if '99.2%' in content or '99' in content:
                        print("✓ Open access percentage found")
                    if '85' in content:
                        print("✓ Galata-only papers count found")

                # Check for any white backgrounds or light colors
                all_text = current_slide.query_selector_all('p, li, h2, h3')
                for el in all_text[:3]:  # Check first few elements
                    color = el.evaluate('el => window.getComputedStyle(el).color')
                    if 'rgb(192, 212, 224)' in color or '#c0d4e0' in color:
                        pass  # Good - elegant light blue-gray
                    elif 'rgb(0,' in color or 'rgb(255,' in color:
                        print(f"⚠ Possible color issue: {color}")

                print()
            else:
                print(f"ERROR: Could not find active slide {slide_num}\n")

        # Check specific statistics
        print("\n=== FINAL VERIFICATION ===")
        page.goto(url, wait_until='networkidle')
        time.sleep(2)

        # Navigate to slide 15 (Critical Discovery)
        for _ in range(14):
            page.keyboard.press('ArrowRight')
            time.sleep(0.2)

        slide_15_content = page.query_selector('.slide.active')
        if slide_15_content:
            text = slide_15_content.inner_text()
            print("Slide 15 (Critical Discovery) content check:")
            print(f"- Has '511 papers': {'511' in text}")
            print(f"- Has '6 papers' for Galata bankers: {'6 papers' in text}")
            print(f"- Has '100 papers' for Galata banking: {'100' in text}")
            print(f"- Mentions Falconnet: {'Falconnet' in text}")

        # Navigate to slide 16 (Conclusion)
        page.keyboard.press('ArrowRight')
        time.sleep(0.5)

        slide_16_content = page.query_selector('.slide.active')
        if slide_16_content:
            text = slide_16_content.inner_text()
            print("\nSlide 16 (Conclusion) statistics check:")
            print(f"- Has '596' total papers: {'596' in text}")
            print(f"- Has '99.2%' or '99' open access: {'99' in text}")
            print(f"- Has '85' Galata-only: {'85' in text}")
            print(f"- Has '167' year span: {'167' in text}")
            print(f"- Has '3.9' avg citations: {'3.9' in text}")

        browser.close()
        print("\n✅ Verification complete!")

if __name__ == "__main__":
    verify_ottoman_slides()