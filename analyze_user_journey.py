#!/usr/bin/env python3
"""
Analyze user journey through DISCOVER, FRAME, and ANALYZE sections
Captures screenshots and documents interface changes
"""

from playwright.sync_api import sync_playwright
import time
import os

def analyze_section_journey():
    with sync_playwright() as p:
        # Launch browser with viewport
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to the main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Capture initial state
        print("Capturing initial landing page...")
        page.screenshot(path='journey_0_initial.png', full_page=False)

        # Get initial sidebar state
        initial_sidebar = page.query_selector('.sidebar')
        initial_sidebar_html = initial_sidebar.inner_html() if initial_sidebar else "No sidebar"

        # 1. DISCOVER Section (Day 1)
        print("\n1. CLICKING DISCOVER (Day 1)...")
        discover_card = page.query_selector('.day-card:has-text("DISCOVER")')
        if discover_card:
            # Capture before click
            discover_bbox = discover_card.bounding_box()
            print(f"   DISCOVER card position: {discover_bbox}")

            # Click the card
            discover_card.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Capture after DISCOVER click
            page.screenshot(path='journey_1_discover_clicked.png', full_page=False)

            # Check what changed
            current_content = page.query_selector('.content-container')
            if current_content:
                print("   ✓ Content container updated")

            # Check sidebar changes
            sidebar = page.query_selector('.sidebar')
            if sidebar:
                sidebar_items = sidebar.query_selector_all('.sidebar-item')
                print(f"   ✓ Sidebar now has {len(sidebar_items)} items")
                for item in sidebar_items[:3]:  # Show first 3 items
                    print(f"     - {item.inner_text()}")

            # Go back to main
            back_btn = page.query_selector('.back-button')
            if back_btn:
                back_btn.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

        # 2. FRAME Section (Day 2)
        print("\n2. CLICKING FRAME (Day 2)...")
        frame_card = page.query_selector('.day-card:has-text("FRAME")')
        if frame_card:
            # Click the card
            frame_card.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Capture after FRAME click
            page.screenshot(path='journey_2_frame_clicked.png', full_page=False)

            # Check content changes
            current_content = page.query_selector('.content-container')
            if current_content:
                # Look for specific Day 2 content
                schedule_items = current_content.query_selector_all('.schedule-item')
                if schedule_items:
                    print(f"   ✓ Schedule shows {len(schedule_items)} items")

                resources = current_content.query_selector_all('.resource-item')
                if resources:
                    print(f"   ✓ Resources section has {len(resources)} items")

            # Check sidebar
            sidebar = page.query_selector('.sidebar')
            if sidebar:
                sidebar_items = sidebar.query_selector_all('.sidebar-item')
                print(f"   ✓ Sidebar updated with {len(sidebar_items)} items")
                # Check for Day 2 specific items
                for item in sidebar_items:
                    text = item.inner_text()
                    if 'OpenAlex' in text or 'Data' in text:
                        print(f"     - Found Day 2 item: {text}")

            # Go back to main
            back_btn = page.query_selector('.back-button')
            if back_btn:
                back_btn.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

        # 3. ANALYZE Section (Day 3)
        print("\n3. CLICKING ANALYZE (Day 3)...")
        analyze_card = page.query_selector('.day-card:has-text("ANALYZE")')
        if analyze_card:
            # Click the card
            analyze_card.click()
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Capture after ANALYZE click
            page.screenshot(path='journey_3_analyze_clicked.png', full_page=False)

            # Check content changes
            current_content = page.query_selector('.content-container')
            if current_content:
                # Look for Day 3 specific content
                slidedecks = current_content.query_selector_all('a[href*="modules/analyze"]')
                if slidedecks:
                    print(f"   ✓ Found {len(slidedecks)} slideshow links:")
                    for deck in slidedecks:
                        print(f"     - {deck.inner_text()}")

                workshop_links = current_content.query_selector_all('a[href*="Day3_Workshop"]')
                if workshop_links:
                    print(f"   ✓ Found {len(workshop_links)} workshop package links")

            # Check sidebar for Day 3 items
            sidebar = page.query_selector('.sidebar')
            if sidebar:
                sidebar_items = sidebar.query_selector_all('.sidebar-item')
                print(f"   ✓ Sidebar has {len(sidebar_items)} items")
                # Look for analysis-specific items
                for item in sidebar_items:
                    text = item.inner_text()
                    if 'CLI' in text or 'Ottoman' in text or 'WACKO' in text:
                        print(f"     - Found Day 3 item: {text}")

        # Final comparison summary
        print("\n=== VISUAL DIFFERENCES SUMMARY ===")
        print("Screenshots saved:")
        print("  • journey_0_initial.png - Landing page with 3 cards")
        print("  • journey_1_discover_clicked.png - Day 1 DISCOVER content")
        print("  • journey_2_frame_clicked.png - Day 2 FRAME content")
        print("  • journey_3_analyze_clicked.png - Day 3 ANALYZE content")

        # Check for visual consistency
        print("\n=== ANALYZING INTERFACE PATTERNS ===")

        # Go back to each section quickly to analyze
        for day_num, section in [(1, "DISCOVER"), (2, "FRAME"), (3, "ANALYZE")]:
            card = page.query_selector(f'.day-card:has-text("{section}")')
            if card:
                card.click()
                page.wait_for_load_state('networkidle')
                time.sleep(0.5)

                # Analyze color scheme
                sidebar = page.query_selector('.sidebar')
                if sidebar:
                    sidebar_style = sidebar.evaluate('el => window.getComputedStyle(el).background')
                    print(f"\nDay {day_num} ({section}) sidebar background: {sidebar_style[:50]}...")

                # Check content area
                content = page.query_selector('.content-container')
                if content:
                    content_style = content.evaluate('el => window.getComputedStyle(el).background')
                    has_schedule = content.query_selector('.schedule-container') is not None
                    has_resources = content.query_selector('.resources-grid') is not None

                    print(f"  • Has schedule: {has_schedule}")
                    print(f"  • Has resources: {has_resources}")

                # Go back
                back_btn = page.query_selector('.back-button')
                if back_btn:
                    back_btn.click()
                    time.sleep(0.5)

        browser.close()

        print("\n✓ Analysis complete! Check the journey_*.png files to see the differences.")
        return True

if __name__ == "__main__":
    success = analyze_section_journey()
    if success:
        print("\n🎯 User journey analysis completed successfully!")
    else:
        print("\n❌ Analysis failed")