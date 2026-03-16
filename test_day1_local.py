#!/usr/bin/env python3
"""Test Day 1 locally"""

from playwright.sync_api import sync_playwright
import time

def test_day1_local():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Load local main app
        print("1. Loading local main app...")
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/index.html")
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Click on Day 1 DISCOVER box
        print("2. Clicking on Day 1 DISCOVER...")
        page.click(".day1")  # Click the day1 div
        time.sleep(2)
        page.screenshot(path="local_day1_result.png")
        print("   Screenshot saved: local_day1_result.png")
        print(f"   Current URL: {page.url}")

        browser.close()

if __name__ == "__main__":
    test_day1_local()