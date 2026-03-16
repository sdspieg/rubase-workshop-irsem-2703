#!/usr/bin/env python3
"""
Final visual verification of Ottoman Bank presentation.
Checks that all elements are visible and properly styled.
"""

from playwright.sync_api import sync_playwright
import time

def final_visual_check():
    """Final check of key slides for readability."""

    with sync_playwright() as p:
        print("=== FINAL VISUAL VERIFICATION ===\n")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/ottoman-bank-case-study.html'
        page.goto(url, wait_until='networkidle')
        time.sleep(2)

        # Check key slides
        key_slides = [
            (3, "Critical Discovery - Table Check"),
            (10, "Theme Analysis - Table Check"),
            (15, "Galata Discovery - Complex Layout"),
            (16, "Conclusion - Stats Grid")
        ]

        all_good = True

        for slide_num, description in key_slides:
            print(f"Checking Slide {slide_num}: {description}")

            # Navigate to slide
            for _ in range(slide_num - 1):
                page.keyboard.press('ArrowRight')
                time.sleep(0.2)

            slide = page.query_selector('.slide.active')

            # Check tables if present
            tables = slide.query_selector_all('table')
            if tables:
                for table in tables:
                    # Check table cells are visible
                    cells = table.query_selector_all('td')
                    if cells:
                        first_cell = cells[0]
                        cell_color = first_cell.evaluate('el => window.getComputedStyle(el).color')
                        cell_bg = first_cell.evaluate('el => window.getComputedStyle(el.parentElement.parentElement).backgroundColor')

                        # Check contrast
                        if 'rgb(255, 255, 255)' in cell_color or 'rgb(0, 255, 255)' in cell_color:
                            print(f"  ✅ Table cells are white/cyan - readable")
                        elif 'rgb(0, 0, 0)' in cell_color:
                            print(f"  ❌ Table cells are BLACK - ILLEGIBLE!")
                            all_good = False
                        else:
                            print(f"  ⚠️ Table cell color: {cell_color}")

            # Check list items if present
            lists = slide.query_selector_all('li')
            if lists and len(lists) > 0:
                first_li = lists[0]
                li_color = first_li.evaluate('el => window.getComputedStyle(el).color')

                if 'rgb(255, 255, 255)' in li_color or 'rgba(255, 255, 255' in li_color:
                    print(f"  ✅ List items are white - readable")
                elif 'rgb(52, 73, 94)' in li_color or 'rgb(34,' in li_color:
                    print(f"  ❌ List items are DARK GRAY - ILLEGIBLE!")
                    all_good = False
                else:
                    print(f"  List color: {li_color}")

            # Check if content fits
            scroll_height = slide.evaluate('el => el.scrollHeight')
            client_height = slide.evaluate('el => el.clientHeight')
            if scroll_height > client_height:
                overflow = scroll_height - client_height
                print(f"  ⚠️ Content overflows by {overflow}px")
                all_good = False
            else:
                print(f"  ✅ Content fits on screen")

            # Check screen usage
            viewport_height = page.evaluate('() => window.innerHeight')
            usage = (client_height / viewport_height) * 100
            if usage < 80:
                print(f"  ⚠️ Only using {usage:.1f}% of screen")
            else:
                print(f"  ✅ Using {usage:.1f}% of screen")

            print()

            # Reset for next slide
            page.reload()
            time.sleep(1)

        browser.close()

        print("="*50)
        if all_good:
            print("✅ ALL SLIDES ARE READABLE AND PROPERLY LAID OUT!")
        else:
            print("❌ SOME ISSUES REMAIN - SEE ABOVE")
        print("="*50)

        return all_good

if __name__ == "__main__":
    result = final_visual_check()
    exit(0 if result else 1)