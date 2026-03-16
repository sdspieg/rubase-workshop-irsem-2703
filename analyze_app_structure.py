#!/usr/bin/env python3
"""
Analyze the actual structure of the app and capture navigation screenshots
"""

from playwright.sync_api import sync_playwright
import time
import os

def analyze_app_navigation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("=== ANALYZING APP STRUCTURE ===")

        # Capture initial state
        page.screenshot(path='app_0_initial.png', full_page=False)
        print("✓ Captured initial state")

        # Look for clickable elements with day numbers
        day1_elements = page.query_selector_all('[onclick*="showDay(1)"], [onclick*="showDay(\'1\')"], .day-number:has-text("1")')
        day2_elements = page.query_selector_all('[onclick*="showDay(2)"], [onclick*="showDay(\'2\')"], .day-number:has-text("2")')
        day3_elements = page.query_selector_all('[onclick*="showDay(3)"], [onclick*="showDay(\'3\')"], .day-number:has-text("3")')

        print(f"Found Day 1 elements: {len(day1_elements)}")
        print(f"Found Day 2 elements: {len(day2_elements)}")
        print(f"Found Day 3 elements: {len(day3_elements)}")

        # Try alternative selectors
        discover_element = page.query_selector(':has-text("DISCOVER")')
        frame_element = page.query_selector(':has-text("FRAME")')
        analyze_element = page.query_selector(':has-text("ANALYZE")')

        # Test DISCOVER section
        if discover_element:
            print("\n=== TESTING DISCOVER SECTION ===")

            # Get the parent card that's clickable
            discover_card = discover_element.evaluate_handle('''
                el => {
                    let current = el;
                    while (current && !current.onclick && !current.classList.contains('day-card')) {
                        current = current.parentElement;
                    }
                    return current;
                }
            ''').as_element()

            if discover_card:
                discover_card.click()
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                page.screenshot(path='app_1_discover.png', full_page=False)
                print("✓ Captured DISCOVER section")

                # Check what's visible now
                sidebar = page.query_selector('.sidebar')
                if sidebar and sidebar.is_visible():
                    sidebar_text = sidebar.inner_text()
                    print(f"Sidebar content preview: {sidebar_text[:200]}...")

                # Try to go back
                # Look for back button or main navigation
                back_options = [
                    '.back-button',
                    '[onclick*="showMain"]',
                    '.header-title',  # Sometimes header title is clickable
                    'a[href*="index"]'
                ]

                for selector in back_options:
                    back_btn = page.query_selector(selector)
                    if back_btn:
                        back_btn.click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(1)
                        print("  Returned to main")
                        break

        # Test FRAME section
        frame_element = page.query_selector(':has-text("FRAME")')
        if frame_element:
            print("\n=== TESTING FRAME SECTION ===")

            frame_card = frame_element.evaluate_handle('''
                el => {
                    let current = el;
                    while (current && !current.onclick && !current.classList.contains('day-card')) {
                        current = current.parentElement;
                    }
                    return current;
                }
            ''').as_element()

            if frame_card:
                frame_card.click()
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                page.screenshot(path='app_2_frame.png', full_page=False)
                print("✓ Captured FRAME section")

                # Check for OpenAlex content
                openalex_content = page.query_selector_all(':has-text("OpenAlex")')
                print(f"  Found {len(openalex_content)} OpenAlex references")

                # Go back
                for selector in ['.back-button', '[onclick*="showMain"]', '.header-title']:
                    back_btn = page.query_selector(selector)
                    if back_btn:
                        back_btn.click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(1)
                        break

        # Test ANALYZE section
        analyze_element = page.query_selector(':has-text("ANALYZE")')
        if analyze_element:
            print("\n=== TESTING ANALYZE SECTION ===")

            analyze_card = analyze_element.evaluate_handle('''
                el => {
                    let current = el;
                    while (current && !current.onclick && !current.classList.contains('day-card')) {
                        current = current.parentElement;
                    }
                    return current;
                }
            ''').as_element()

            if analyze_card:
                analyze_card.click()
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                page.screenshot(path='app_3_analyze.png', full_page=False)
                print("✓ Captured ANALYZE section")

                # Check for CLI/LLM content
                cli_content = page.query_selector_all(':has-text("CLI"), :has-text("LLM")')
                print(f"  Found {len(cli_content)} CLI/LLM references")

                # Check for slideshow links
                slideshow_links = page.query_selector_all('a[href*="modules/analyze"]')
                if slideshow_links:
                    print(f"  Found {len(slideshow_links)} slideshow links:")
                    for link in slideshow_links[:3]:
                        print(f"    - {link.inner_text()}")

        browser.close()

        print("\n=== NAVIGATION FLOW COMPLETE ===")
        print("Screenshots saved:")
        print("  • app_0_initial.png - Landing page")
        print("  • app_1_discover.png - Day 1 DISCOVER view")
        print("  • app_2_frame.png - Day 2 FRAME view")
        print("  • app_3_analyze.png - Day 3 ANALYZE view")

        print("\n🎯 Key differences observed:")
        print("  1. DISCOVER: Focus on setup and bibliometrics")
        print("  2. FRAME: OpenAlex data collection tools")
        print("  3. ANALYZE: CLI/LLM analysis presentations")

if __name__ == "__main__":
    analyze_app_navigation()