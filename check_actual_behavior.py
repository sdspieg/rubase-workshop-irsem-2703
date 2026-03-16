#!/usr/bin/env python3
"""
Check what ACTUALLY happens when clicking Day 3
"""

from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    # Go to the main index.html
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_url = f"file://{base_path}/index.html"

    print(f"Opening: {file_url}")
    page.goto(file_url)
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("\nBEFORE clicking Day 3:")
    print(f"Current URL: {page.url}")

    # Try to click Day 3 card
    print("\nLooking for Day 3 card...")
    day3_card = page.query_selector('.day-item.day3')
    if day3_card:
        print("Found Day 3 card, clicking...")
        day3_card.click()
        time.sleep(3)
    else:
        print("ERROR: No Day 3 card found!")

    print("\nAFTER clicking Day 3:")
    print(f"Current URL: {page.url}")

    # Take screenshot
    page.screenshot(path='what_user_sees.png')
    print("\nScreenshot saved as what_user_sees.png")

    # Check if we're on the old module page
    if 'modules/analyze' in page.url:
        print("\n❌ PROBLEM: Still redirecting to modules/analyze/index.html!")
        print("This is the OLD 3-column layout!")
    else:
        print("\n✅ Good: Staying on main page")

        # But let's check what's actually visible
        title = page.query_selector('h1')
        if title:
            title_text = title.inner_text()
            print(f"Page title: {title_text}")

            if 'DAY 3: ANALYZE' in title_text:
                print("WARNING: Still seeing the old Day 3 layout!")

    # Check for the 3-column layout elements
    module_contents = page.query_selector('.content-wrapper')
    if module_contents:
        print("\n❌ FOUND 3-COLUMN LAYOUT ELEMENTS!")

    sidebar = page.query_selector('.sidebar')
    if sidebar:
        print("\n✓ Found sidebar")

    browser.close()