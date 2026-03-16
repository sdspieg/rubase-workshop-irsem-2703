#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    # Enable console logging
    page.on("console", lambda msg: print(f"Console: {msg.text}"))

    # Start fresh
    page.goto('file:///mnt/c/Users/Stephan/Dropbox/Presentations/2603%20-%20Boston_instructors/rubase-workshop-fletcher-2603/index.html')
    page.wait_for_load_state('networkidle')

    print("Initial URL:", page.url)

    # Test Day 1
    print("\n=== TESTING DAY 1 ===")
    day1 = page.query_selector('.day-item.day1')
    day1.click()
    time.sleep(2)
    print("After Day 1 click:", page.url)
    if "index.html" in page.url:
        print("✓ Day 1 stays in index.html")

    # Test Day 2
    print("\n=== TESTING DAY 2 ===")
    day2 = page.query_selector('.day-item.day2')
    day2.click()
    time.sleep(2)
    print("After Day 2 click:", page.url)
    if "index.html" in page.url:
        print("✓ Day 2 stays in index.html")

    # Test Day 3
    print("\n=== TESTING DAY 3 ===")
    day3 = page.query_selector('.day-item.day3')

    # Check onclick attribute
    onclick = day3.get_attribute('onclick')
    print(f"Day 3 onclick attribute: {onclick}")

    day3.click()
    time.sleep(3)

    print("After Day 3 click:", page.url)

    if "modules/analyze" in page.url:
        print("❌ PROBLEM: Day 3 redirected to modules/analyze!")
    elif "index.html" in page.url:
        print("✓ Day 3 stays in index.html")
    else:
        print("? Unexpected URL")

    # Take screenshot
    page.screenshot(path='day3_actual_result.png')
    print("\nScreenshot saved as day3_actual_result.png")

    browser.close()