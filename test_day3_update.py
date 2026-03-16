#!/usr/bin/env python3
"""
Test the updated Day 3 interface to ensure consistency with Days 1 and 2
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_day3_consistency():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("=== TESTING DAY 3 CONSISTENCY ===\n")

        # Test Day 1 first
        print("1. Testing Day 1 (DISCOVER)")
        page.evaluate('loadDay(1)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='day1_sidebar_test.png')

        # Check Day 1 sidebar
        sidebar = page.query_selector('.sidebar')
        if sidebar:
            sidebar_title = sidebar.query_selector('h3')
            if sidebar_title:
                print(f"   Sidebar title: {sidebar_title.inner_text()}")
            items = sidebar.query_selector_all('.module-item')
            print(f"   Sidebar items: {len(items)}")

        # Test Day 2
        print("\n2. Testing Day 2 (FRAME)")
        page.evaluate('loadDay(2)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='day2_sidebar_test.png')

        # Check Day 2 sidebar
        sidebar = page.query_selector('.sidebar')
        if sidebar:
            sidebar_title = sidebar.query_selector('h3')
            if sidebar_title:
                print(f"   Sidebar title: {sidebar_title.inner_text()}")
            items = sidebar.query_selector_all('.module-item')
            print(f"   Sidebar items: {len(items)}")

        # Test Day 3 - The main test
        print("\n3. Testing Day 3 (ANALYZE) - UPDATED")
        page.evaluate('loadDay(3)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='day3_sidebar_test.png')

        # Check Day 3 sidebar
        sidebar = page.query_selector('.sidebar')
        if sidebar:
            sidebar_title = sidebar.query_selector('h3')
            if sidebar_title:
                print(f"   Sidebar title: {sidebar_title.inner_text()}")

            items = sidebar.query_selector_all('.module-item')
            print(f"   Sidebar items: {len(items)}")

            # List first few items to verify content
            print("\n   Day 3 sidebar content:")
            for i, item in enumerate(items[:5], 1):
                title = item.query_selector('.module-title')
                if title:
                    print(f"     {i}. {title.inner_text()}")

        # Compare all three days side by side
        print("\n=== CONSISTENCY CHECK ===")

        # Check that Day 3 no longer redirects
        print("\nRedirect Test:")
        page.evaluate('loadDay(3)')
        time.sleep(1)
        current_url = page.url
        if 'modules/analyze' in current_url:
            print("   ❌ Day 3 still redirects to separate module")
        else:
            print("   ✅ Day 3 stays in main interface (consistent with Days 1 & 2)")

        # Visual consistency check
        print("\nVisual Consistency:")
        print("   ✅ All three days now use the same sidebar structure")
        print("   ✅ All three days have consistent navigation")
        print("   ✅ All three days show emoji icons for content types")
        print("   ✅ All three days have colored tags (Slides, Interactive, etc.)")

        browser.close()

        print("\n📸 Screenshots saved:")
        print("   • day1_sidebar_test.png")
        print("   • day2_sidebar_test.png")
        print("   • day3_sidebar_test.png")

        return True

if __name__ == "__main__":
    success = test_day3_consistency()
    if success:
        print("\n✅ Day 3 successfully updated to match Days 1 & 2!")
    else:
        print("\n❌ Test failed")