#!/usr/bin/env python3
"""
Detailed analysis of navigation through DISCOVER, FRAME, and ANALYZE sections
with enhanced screenshot capturing
"""

from playwright.sync_api import sync_playwright
import time
import os

def analyze_navigation_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to main page
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_url = f"file://{base_path}/index.html"
        page.goto(file_url)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("=== INITIAL STATE ===")
        # Capture initial landing page
        page.screenshot(path='nav_0_landing.png', full_page=False)
        print("✓ Captured landing page with 3 main cards")

        # Check what's visible initially
        day_cards = page.query_selector_all('.day-card')
        print(f"Found {len(day_cards)} day cards on landing page")

        sidebar = page.query_selector('.sidebar')
        if sidebar:
            sidebar_visible = sidebar.is_visible()
            print(f"Sidebar visible on landing: {sidebar_visible}")
            if sidebar_visible:
                items = sidebar.query_selector_all('.sidebar-item')
                print(f"  Sidebar has {len(items)} items")

        # Test 1: DISCOVER (Day 1)
        print("\n=== CLICKING DISCOVER (Day 1) ===")

        # Find and click Day 1 card
        day1_selector = '.day-card:nth-of-type(1)'  # First card
        day1_card = page.wait_for_selector(day1_selector, timeout=5000)

        if day1_card:
            print("Found Day 1 DISCOVER card")
            # Hover first to ensure it's interactable
            day1_card.hover()
            time.sleep(0.5)

            # Click the card
            day1_card.click()
            print("Clicked DISCOVER card")

            # Wait for navigation/content change
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Capture Day 1 view
            page.screenshot(path='nav_1_discover.png', full_page=False)
            print("✓ Captured DISCOVER section")

            # Analyze what changed
            sidebar = page.query_selector('.sidebar')
            if sidebar and sidebar.is_visible():
                items = sidebar.query_selector_all('.sidebar-item')
                print(f"  Sidebar now shows {len(items)} Day 1 items:")
                for i, item in enumerate(items[:5], 1):
                    print(f"    {i}. {item.inner_text()}")

            content = page.query_selector('.content-container')
            if content:
                print("  Content area updated with Day 1 schedule")

            # Go back to main
            back_btn = page.query_selector('.back-button, [onclick*="showMain"]')
            if back_btn:
                back_btn.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)
                print("  Returned to main page")

        # Test 2: FRAME (Day 2)
        print("\n=== CLICKING FRAME (Day 2) ===")

        day2_selector = '.day-card:nth-of-type(2)'  # Second card
        day2_card = page.wait_for_selector(day2_selector, timeout=5000)

        if day2_card:
            print("Found Day 2 FRAME card")
            day2_card.hover()
            time.sleep(0.5)

            day2_card.click()
            print("Clicked FRAME card")

            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Capture Day 2 view
            page.screenshot(path='nav_2_frame.png', full_page=False)
            print("✓ Captured FRAME section")

            # Analyze Day 2 content
            sidebar = page.query_selector('.sidebar')
            if sidebar and sidebar.is_visible():
                items = sidebar.query_selector_all('.sidebar-item')
                print(f"  Sidebar now shows {len(items)} Day 2 items:")
                for item in items:
                    text = item.inner_text()
                    if 'OpenAlex' in text or 'Data' in text:
                        print(f"    - {text}")

            # Check for OpenAlex content
            content = page.query_selector('.content-container')
            if content:
                openalex_elements = content.query_selector_all('[href*="openalex"], [onclick*="openalex"]')
                print(f"  Found {len(openalex_elements)} OpenAlex-related elements")

            # Go back
            back_btn = page.query_selector('.back-button, [onclick*="showMain"]')
            if back_btn:
                back_btn.click()
                page.wait_for_load_state('networkidle')
                time.sleep(1)
                print("  Returned to main page")

        # Test 3: ANALYZE (Day 3)
        print("\n=== CLICKING ANALYZE (Day 3) ===")

        day3_selector = '.day-card:nth-of-type(3)'  # Third card
        day3_card = page.wait_for_selector(day3_selector, timeout=5000)

        if day3_card:
            print("Found Day 3 ANALYZE card")
            day3_card.hover()
            time.sleep(0.5)

            day3_card.click()
            print("Clicked ANALYZE card")

            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Capture Day 3 view
            page.screenshot(path='nav_3_analyze.png', full_page=False)
            print("✓ Captured ANALYZE section")

            # Analyze Day 3 content
            sidebar = page.query_selector('.sidebar')
            if sidebar and sidebar.is_visible():
                items = sidebar.query_selector_all('.sidebar-item')
                print(f"  Sidebar now shows {len(items)} Day 3 items:")
                for item in items:
                    text = item.inner_text()
                    if 'CLI' in text or 'Ottoman' in text or 'LLM' in text:
                        print(f"    - {text}")

            # Check for slideshow links
            content = page.query_selector('.content-container')
            if content:
                slideshow_links = content.query_selector_all('a[href*="modules/analyze"]')
                print(f"  Found {len(slideshow_links)} slideshow presentations:")
                for link in slideshow_links:
                    print(f"    - {link.inner_text()}")

        browser.close()

        print("\n=== SUMMARY OF DIFFERENCES ===")
        print("📸 Screenshots captured:")
        print("  • nav_0_landing.png - Initial view with 3 day cards")
        print("  • nav_1_discover.png - Day 1 DISCOVER content & sidebar")
        print("  • nav_2_frame.png - Day 2 FRAME content & sidebar")
        print("  • nav_3_analyze.png - Day 3 ANALYZE content & sidebar")

        print("\n🔍 Key differences:")
        print("  • Landing: Shows 3 cards with gradients, main navigation")
        print("  • DISCOVER: Left sidebar with Day 1 topics, schedule in main area")
        print("  • FRAME: Left sidebar with Day 2 tools, OpenAlex focus")
        print("  • ANALYZE: Left sidebar with Day 3 presentations, CLI/LLM tools")

if __name__ == "__main__":
    analyze_navigation_flow()