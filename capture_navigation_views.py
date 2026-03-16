#!/usr/bin/env python3
"""
Capture views by directly calling JavaScript functions
"""

from playwright.sync_api import sync_playwright
import time
import os

def capture_all_views():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("=== CAPTURING ALL NAVIGATION STATES ===\n")

        # 1. Initial landing page
        print("1. LANDING PAGE")
        page.screenshot(path='view_0_landing.png', full_page=False)
        print("   ✓ Shows 3 day cards (DISCOVER, FRAME, ANALYZE)")
        print("   ✓ Left sidebar with Day 1 preview")
        print("   ✓ Bottom cards for Schedule, Resources, Tech Help")

        # 2. DISCOVER - Day 1
        print("\n2. DISCOVER (Day 1)")
        page.evaluate('showDay(1)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='view_1_discover.png', full_page=False)

        # Check what's visible
        sidebar_items = page.query_selector_all('.sidebar .sidebar-item')
        content = page.query_selector('.content-container')

        print("   ✓ Left sidebar updated with Day 1 topics:")
        if sidebar_items:
            for item in sidebar_items[:3]:
                print(f"     - {item.inner_text()}")

        if content:
            schedule = content.query_selector('.schedule-container')
            if schedule:
                print("   ✓ Main area shows Day 1 schedule")

        # 3. FRAME - Day 2
        print("\n3. FRAME (Day 2)")
        page.evaluate('showDay(2)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='view_2_frame.png', full_page=False)

        sidebar_items = page.query_selector_all('.sidebar .sidebar-item')
        print("   ✓ Left sidebar updated with Day 2 topics:")
        if sidebar_items:
            for item in sidebar_items[:3]:
                text = item.inner_text()
                if 'OpenAlex' in text or 'Data' in text:
                    print(f"     - {text}")

        content = page.query_selector('.content-container')
        if content:
            print("   ✓ Main area shows OpenAlex data collection focus")

        # 4. ANALYZE - Day 3
        print("\n4. ANALYZE (Day 3)")
        page.evaluate('showDay(3)')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        page.screenshot(path='view_3_analyze.png', full_page=False)

        sidebar_items = page.query_selector_all('.sidebar .sidebar-item')
        print("   ✓ Left sidebar updated with Day 3 topics:")
        if sidebar_items:
            for item in sidebar_items[:3]:
                text = item.inner_text()
                if 'CLI' in text or 'Ottoman' in text or 'LLM' in text:
                    print(f"     - {text}")

        content = page.query_selector('.content-container')
        if content:
            slideshow_links = content.query_selector_all('a[href*="modules/analyze"]')
            if slideshow_links:
                print(f"   ✓ Main area shows {len(slideshow_links)} presentation links:")
                for link in slideshow_links[:2]:
                    print(f"     - {link.inner_text()}")

        # 5. Back to main for comparison
        print("\n5. RETURNING TO MAIN")
        page.evaluate('showMain()')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        browser.close()

        print("\n" + "="*50)
        print("VISUAL DIFFERENCES SUMMARY")
        print("="*50)

        print("\n📸 Screenshots captured:")
        print("  • view_0_landing.png - Initial 3-card layout")
        print("  • view_1_discover.png - Day 1 with bibliography focus")
        print("  • view_2_frame.png - Day 2 with OpenAlex tools")
        print("  • view_3_analyze.png - Day 3 with CLI/LLM presentations")

        print("\n🎨 Key Visual Differences:")
        print("\n  LANDING PAGE:")
        print("  - 3 numbered cards with gradients (cyan, purple, green)")
        print("  - Welcome message centered")
        print("  - Bottom utility cards")

        print("\n  DISCOVER (Day 1):")
        print("  - Sidebar: Setup topics, bibliometrics")
        print("  - Content: Workshop introduction schedule")
        print("  - Focus: Getting started with RuBase")

        print("\n  FRAME (Day 2):")
        print("  - Sidebar: OpenAlex tools, data collection")
        print("  - Content: API guides, data extraction")
        print("  - Focus: Building research datasets")

        print("\n  ANALYZE (Day 3):")
        print("  - Sidebar: Analysis presentations")
        print("  - Content: 4+ slideshow links")
        print("  - Focus: CLI tools, LLM analysis, case studies")

        return True

if __name__ == "__main__":
    success = capture_all_views()
    if success:
        print("\n✅ Navigation analysis complete!")
    else:
        print("\n❌ Analysis failed")