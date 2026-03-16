#!/usr/bin/env python3
"""
Test that switching between days updates the content properly
"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    page.goto('file:///mnt/c/Users/Stephan/Dropbox/Presentations/2603%20-%20Boston_instructors/rubase-workshop-fletcher-2603/index.html')
    page.wait_for_load_state('networkidle')

    print("=== TESTING DAY SWITCHING ===\n")

    # Test Day 2 first
    print("1. Clicking Day 2...")
    page.evaluate('loadDay(2)')
    time.sleep(1)
    title = page.query_selector('.welcome-title')
    if title:
        print(f"   Content shows: {title.inner_text()}")
    page.screenshot(path='test_day2.png')

    # Switch to Day 1
    print("\n2. Switching to Day 1...")
    page.evaluate('loadDay(1)')
    time.sleep(1)
    title = page.query_selector('.welcome-title')
    if title:
        title_text = title.inner_text()
        print(f"   Content shows: {title_text}")
        if "Day 1" in title_text:
            print("   ✅ Day 1 content loaded correctly!")
        else:
            print(f"   ❌ PROBLEM: Still showing {title_text}")
    page.screenshot(path='test_day1.png')

    # Switch to Day 3
    print("\n3. Switching to Day 3...")
    page.evaluate('loadDay(3)')
    time.sleep(1)
    title = page.query_selector('.welcome-title')
    if title:
        title_text = title.inner_text()
        print(f"   Content shows: {title_text}")
        if "Day 3" in title_text:
            print("   ✅ Day 3 content loaded correctly!")
        else:
            print(f"   ❌ PROBLEM: Still showing {title_text}")
    page.screenshot(path='test_day3.png')

    # Back to Day 2
    print("\n4. Back to Day 2...")
    page.evaluate('loadDay(2)')
    time.sleep(1)
    title = page.query_selector('.welcome-title')
    if title:
        title_text = title.inner_text()
        print(f"   Content shows: {title_text}")
        if "Day 2" in title_text:
            print("   ✅ Day 2 content loaded correctly!")
        else:
            print(f"   ❌ PROBLEM: Still showing {title_text}")

    browser.close()
    print("\n✓ Test complete!")