#!/usr/bin/env python3
"""Verify the app redirects to Ingest module"""

from playwright.sync_api import sync_playwright
import time

def verify_redirect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        print("1. Loading main app (should redirect to Ingest)...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/")

        # Wait for redirect
        time.sleep(3)

        page.screenshot(path="ingest_landing.png")
        print(f"   Current URL: {page.url}")
        print("   Screenshot saved: ingest_landing.png")

        browser.close()

if __name__ == "__main__":
    verify_redirect()