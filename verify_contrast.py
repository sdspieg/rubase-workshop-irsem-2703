#!/usr/bin/env python3
"""
Verify color contrast improvements on Ottoman Bank presentation.
"""

from playwright.sync_api import sync_playwright
import time

def verify_contrast():
    """Check that all text is now highly visible."""

    print("=== VERIFYING COLOR CONTRAST IMPROVEMENTS ===\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/ottoman-bank-case-study.html'
        print(f"Loading {url}")
        page.goto(url, wait_until='networkidle')
        time.sleep(3)

        # Check key slides
        test_slides = [
            (1, "Title Slide"),
            (3, "Critical Discovery"),
            (15, "Galata Discovery"),
            (16, "Conclusion")
        ]

        for slide_num, slide_name in test_slides:
            print(f"\n=== SLIDE {slide_num}: {slide_name} ===")

            # Navigate to slide
            for _ in range(slide_num - 1):
                page.keyboard.press('ArrowRight')
                time.sleep(0.2)

            slide = page.query_selector('.slide.active')
            if slide:
                # Check h1
                h1 = slide.query_selector('h1')
                if h1:
                    h1_color = h1.evaluate('el => window.getComputedStyle(el).color')
                    h1_text = h1.inner_text()[:50]
                    print(f"H1: {h1_color} - '{h1_text}...'")

                    # Check if white or bright
                    if 'rgb(255, 255, 255)' in h1_color:
                        print("  ✅ H1 is pure white - maximum contrast!")
                    elif 'rgb(0, 255, 255)' in h1_color:
                        print("  ✅ H1 is bright cyan - high visibility!")
                    else:
                        print(f"  ⚠️ H1 color may need adjustment: {h1_color}")

                # Check h2
                h2 = slide.query_selector('h2')
                if h2:
                    h2_color = h2.evaluate('el => window.getComputedStyle(el).color')
                    if 'rgb(0, 255, 255)' in h2_color:
                        print(f"  ✅ H2 is bright cyan: {h2_color}")
                    else:
                        print(f"  ⚠️ H2 color: {h2_color}")

                # Check paragraphs
                paragraphs = slide.query_selector_all('p')[:2]
                for i, p in enumerate(paragraphs, 1):
                    p_color = p.evaluate('el => window.getComputedStyle(el).color')
                    if 'rgb(255, 255, 255)' in p_color or 'rgba(255, 255, 255' in p_color:
                        print(f"  ✅ Paragraph {i} is white/near-white")
                    else:
                        print(f"  ⚠️ Paragraph {i} color: {p_color}")

                # Check slide number
                slide_num_el = slide.query_selector('.slide-number')
                if slide_num_el:
                    num_color = slide_num_el.evaluate('el => window.getComputedStyle(el).color')
                    if 'rgb(0, 255, 127)' in num_color:
                        print(f"  ✅ Slide number is bright green")
                    else:
                        print(f"  Slide number color: {num_color}")

            # Reset for next slide
            page.reload()
            time.sleep(1)

        # Special check for Galata discovery slide elements
        print("\n=== SPECIAL CHECK: Galata Discovery Content ===")
        for _ in range(14):
            page.keyboard.press('ArrowRight')
            time.sleep(0.2)

        slide = page.query_selector('.slide.active')
        if slide:
            # Check alert box text
            alert_text = slide.query_selector('.alert-box p')
            if alert_text:
                text_color = alert_text.evaluate('el => window.getComputedStyle(el).color')
                print(f"Alert box text: {text_color}")
                if 'rgb(255, 255, 255)' in text_color:
                    print("  ✅ Alert text is white - excellent contrast!")

            # Check statistics boxes
            stat_boxes = slide.query_selector_all('h4')
            for box in stat_boxes[:2]:
                color = box.evaluate('el => window.getComputedStyle(el).color')
                shadow = box.evaluate('el => window.getComputedStyle(el).textShadow')
                if 'rgb(0, 255, 255)' in color:
                    print(f"  ✅ Stats header is bright cyan with shadow: {shadow[:30]}...")

        browser.close()

        print("\n" + "="*50)
        print("CONTRAST VERIFICATION COMPLETE")
        print("="*50)

if __name__ == "__main__":
    verify_contrast()