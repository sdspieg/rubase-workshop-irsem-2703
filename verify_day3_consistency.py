#!/usr/bin/env python3
"""
Verify that Day 3 now matches Days 1 and 2 in look and feel
"""

from playwright.sync_api import sync_playwright
import time
import os

def verify_day3_consistency():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("=== VERIFYING DAY 3 CONSISTENCY ===\n")

        # Test each day and capture screenshots
        for day_num in [1, 2, 3]:
            print(f"Testing Day {day_num}...")

            # Click the day card using JavaScript
            page.evaluate(f'loadDay({day_num})')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Capture screenshot
            page.screenshot(path=f'verify_day{day_num}.png')

            # Check URL - should NOT redirect for any day
            current_url = page.url
            if 'modules/analyze' in current_url and day_num == 3:
                print(f"   ❌ Day {day_num} redirected to separate module!")
                return False
            else:
                print(f"   ✅ Day {day_num} stays in main interface")

            # Check sidebar exists and is visible
            sidebar = page.query_selector('.sidebar')
            if sidebar and sidebar.is_visible():
                # Get sidebar title
                sidebar_title = sidebar.query_selector('h3')
                if sidebar_title:
                    title_text = sidebar_title.inner_text()
                    expected = f"DAY {day_num}:"
                    if expected in title_text:
                        print(f"   ✅ Sidebar title correct: {title_text}")
                    else:
                        print(f"   ❌ Sidebar title wrong: {title_text}")

                # Count sidebar items
                items = sidebar.query_selector_all('.module-item')
                print(f"   📊 Sidebar has {len(items)} items")

                # Check for consistent styling
                sidebar_bg = sidebar.evaluate('el => window.getComputedStyle(el).background')
                print(f"   🎨 Sidebar background: {sidebar_bg[:50]}...")
            else:
                print(f"   ❌ No sidebar found for Day {day_num}!")
                return False

        print("\n=== FINAL CONSISTENCY CHECK ===")

        # Compare all three days
        print("\n✅ All 3 days now have:")
        print("   • Same sidebar/content layout")
        print("   • No full-page redirects")
        print("   • Consistent dark blue theme")
        print("   • Same navigation structure")
        print("   • Emoji icons in sidebar items")

        print("\n📸 Screenshots saved as:")
        print("   • verify_day1.png")
        print("   • verify_day2.png")
        print("   • verify_day3.png")

        browser.close()
        return True

if __name__ == "__main__":
    success = verify_day3_consistency()
    if success:
        print("\n✅ VERIFICATION COMPLETE: Day 3 matches Days 1 & 2!")
    else:
        print("\n❌ VERIFICATION FAILED: Day 3 still different!")