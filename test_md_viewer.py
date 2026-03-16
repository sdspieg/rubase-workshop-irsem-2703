#!/usr/bin/env python3
"""Test MD viewer functionality"""

from playwright.sync_api import sync_playwright
import time

def test_md_viewer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Test viewing an MD file
        print("1. Testing MD viewer with DAY_1_ACTION_PLAN.md...")
        page.goto("file:///home/stephan/rubase-workshop-fletcher-2603/modules/mdviewer/index.html?file=DAY_1_ACTION_PLAN.md")
        time.sleep(3)
        page.screenshot(path="md_viewer_test.png")
        print("   Screenshot saved: md_viewer_test.png")

        # Check if content loaded
        content = page.content()
        if "Error loading document" in content:
            print("   ERROR: Document failed to load!")
        else:
            print("   Document loaded successfully")

        browser.close()

if __name__ == "__main__":
    test_md_viewer()