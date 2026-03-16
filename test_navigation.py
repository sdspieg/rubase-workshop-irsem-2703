#!/usr/bin/env python3
"""Test navigation and capture screenshots of the workshop app"""

from playwright.sync_api import sync_playwright
import time

def test_workshop_navigation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Test the main workshop app
        print("1. Loading main workshop app...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="main_app.png")
        print("   Screenshot saved: main_app.png")

        # Click on OpenAlex Explorer in the sidebar
        print("2. Clicking on OpenAlex Explorer...")
        page.click("text=OpenAlex Explorer")
        time.sleep(3)
        page.screenshot(path="after_openalex_click.png")
        print("   Screenshot saved: after_openalex_click.png")
        print(f"   Current URL: {page.url}")

        # Now test the direct OpenAlex URL
        print("3. Loading OpenAlex directly...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/openalex/index.html")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="openalex_direct.png")
        print("   Screenshot saved: openalex_direct.png")
        print(f"   Current URL: {page.url}")

        browser.close()

if __name__ == "__main__":
    test_workshop_navigation()