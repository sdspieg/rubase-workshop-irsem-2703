#!/usr/bin/env python3
"""Verify the Back to Workshop button is working"""

from playwright.sync_api import sync_playwright
import time

def verify_buttons():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Load OpenAlex directly to see the buttons
        print("1. Loading OpenAlex presentation...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/openalex/index.html")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="openalex_with_buttons.png")
        print("   Screenshot saved: openalex_with_buttons.png")

        # Click Back to Workshop button
        print("2. Clicking 'Back to Workshop' button...")
        page.click("text=Back to Workshop")
        time.sleep(2)
        page.screenshot(path="after_back_button.png")
        print("   Screenshot saved: after_back_button.png")
        print(f"   Current URL: {page.url}")

        browser.close()

if __name__ == "__main__":
    verify_buttons()