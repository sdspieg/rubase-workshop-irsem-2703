#!/usr/bin/env python3
"""Verify final state locally"""

from playwright.sync_api import sync_playwright
import time

def verify_local():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Test main hub
        print("1. Loading main hub...")
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/index.html")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="local_hub_final.png")
        print("   Screenshot saved: local_hub_final.png")

        # Click Day 1
        print("2. Clicking Day 1 INGEST...")
        page.click(".day1")
        time.sleep(2)
        page.screenshot(path="local_ingest_final.png")
        print("   Screenshot saved: local_ingest_final.png")

        # Go to Resources
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/modules/resources/index.html")
        time.sleep(2)
        page.screenshot(path="local_resources_final.png")
        print("3. Resources page loaded")
        print("   Screenshot saved: local_resources_final.png")

        # Go to OpenAlex
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/modules/openalex/index.html")
        time.sleep(2)
        page.screenshot(path="local_openalex_final.png")
        print("4. OpenAlex loaded")
        print("   Screenshot saved: local_openalex_final.png")

        browser.close()

if __name__ == "__main__":
    verify_local()