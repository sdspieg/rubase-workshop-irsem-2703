#!/usr/bin/env python3
"""Test clicking on Workshop Schedule and Documentation cards"""

from playwright.sync_api import sync_playwright
import time

def test_cards():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Load main hub
        print("1. Loading main hub...")
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/index.html")
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Click on Workshop Schedule card
        print("2. Clicking Workshop Schedule card...")
        try:
            page.click("text=Workshop Schedule")
            time.sleep(2)
            page.screenshot(path="click_schedule_card.png")
            print(f"   Current URL: {page.url}")
            print("   Screenshot saved: click_schedule_card.png")
        except Exception as e:
            print(f"   Error clicking schedule: {e}")

        # Go back to main hub
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/index.html")
        time.sleep(2)

        # Click on Documentation card
        print("3. Clicking Documentation card...")
        try:
            page.click("text=Documentation")
            time.sleep(2)
            page.screenshot(path="click_documentation_card.png")
            print(f"   Current URL: {page.url}")
            print("   Screenshot saved: click_documentation_card.png")
        except Exception as e:
            print(f"   Error clicking documentation: {e}")

        browser.close()

if __name__ == "__main__":
    test_cards()