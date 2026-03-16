#!/usr/bin/env python3
"""Test buttons locally with force click"""

from playwright.sync_api import sync_playwright
import time

def test_local():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Test with local file
        print("1. Loading local OpenAlex presentation...")
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/modules/openalex/index.html")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="local_openalex.png")
        print("   Screenshot saved: local_openalex.png")

        # Force click the button
        print("2. Force clicking 'Back to Workshop' button...")
        page.locator("text=Back to Workshop").click(force=True)
        time.sleep(2)
        page.screenshot(path="after_back_local.png")
        print("   Screenshot saved: after_back_local.png")
        print(f"   Current URL: {page.url}")

        browser.close()

if __name__ == "__main__":
    test_local()