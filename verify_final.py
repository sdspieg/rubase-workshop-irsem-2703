#!/usr/bin/env python3
"""Verify final state of the workshop app"""

from playwright.sync_api import sync_playwright
import time

def verify_final():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Test main hub (landing page)
        print("1. Loading main hub...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/")
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        page.screenshot(path="final_main_hub.png")
        print("   Screenshot saved: final_main_hub.png")
        print(f"   Current URL: {page.url}")

        # Click on Resources
        print("2. Clicking Resources...")
        page.click("text=Resources")
        time.sleep(2)
        page.screenshot(path="final_resources.png")
        print("   Screenshot saved: final_resources.png")

        # Go back and click Day 1 INGEST
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/")
        time.sleep(2)
        print("3. Clicking Day 1 INGEST...")
        page.click(".day1")
        time.sleep(2)
        page.screenshot(path="final_ingest.png")
        print("   Screenshot saved: final_ingest.png")

        # Click on OpenAlex from ingest page
        print("4. Clicking OpenAlex Explorer...")
        page.click("text=OpenAlex Explorer")
        time.sleep(3)
        page.screenshot(path="final_openalex.png")
        print("   Screenshot saved: final_openalex.png")

        browser.close()

if __name__ == "__main__":
    verify_final()