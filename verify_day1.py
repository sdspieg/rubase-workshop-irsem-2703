#!/usr/bin/env python3
"""Verify Day 1 click redirects to OpenAlex"""

from playwright.sync_api import sync_playwright
import time

def verify_day1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})

        # Load main workshop app
        print("1. Loading main workshop app...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="main_before_day1.png")
        print("   Screenshot saved: main_before_day1.png")

        # Click on Day 1 DISCOVER box
        print("2. Clicking on Day 1 DISCOVER...")
        page.click("text=DISCOVER")
        time.sleep(3)
        page.screenshot(path="after_day1_click.png")
        print("   Screenshot saved: after_day1_click.png")
        print(f"   Current URL: {page.url}")

        browser.close()

if __name__ == "__main__":
    verify_day1()