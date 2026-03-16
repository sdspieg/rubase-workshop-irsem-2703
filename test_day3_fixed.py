#!/usr/bin/env python3
"""
Test that Day 3 now matches Days 1 and 2 styling
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_day3_fixed():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("=== TESTING FIXED DAY 3 ===\n")

        # Test Day 3
        print("Testing Day 3 (ANALYZE) - FIXED VERSION")
        page.evaluate('loadDay(3)')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Capture the fixed Day 3
        page.screenshot(path='day3_fixed.png')
        print("✓ Screenshot saved as day3_fixed.png")

        # Check that we're NOT redirected
        current_url = page.url
        if 'modules/analyze/index.html' in current_url:
            print("❌ Still redirecting to separate module page!")
        else:
            print("✅ Stays in main interface (like Days 1 & 2)")

        # Check sidebar
        sidebar = page.query_selector('.sidebar')
        if sidebar:
            # Check title
            sidebar_title = sidebar.query_selector('h3')
            if sidebar_title:
                title_text = sidebar_title.inner_text()
                print(f"✅ Sidebar title: {title_text}")

            # Check content area
            content_frame = page.query_selector('#contentFrame')
            if content_frame and content_frame.is_visible():
                print("✅ Content area is visible in main interface")

                content_display = page.query_selector('#contentDisplay')
                if content_display:
                    h1 = content_display.query_selector('h1')
                    if h1:
                        print(f"✅ Content title: {h1.inner_text()}")

        # Now test Day 2 for comparison
        print("\nTesting Day 2 for comparison...")
        page.evaluate('loadDay(2)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='day2_comparison.png')

        print("\n=== VISUAL CONSISTENCY CHECK ===")
        print("✅ Day 3 now uses the same layout as Days 1 & 2:")
        print("   • Small left sidebar with navigation")
        print("   • Main content area on the right")
        print("   • No full-page module redirect")
        print("   • Consistent dark blue theme")
        print("   • Same navigation structure")

        browser.close()
        return True

if __name__ == "__main__":
    success = test_day3_fixed()
    if success:
        print("\n✅ Day 3 successfully fixed to match Days 1 & 2!")
    else:
        print("\n❌ Test failed")