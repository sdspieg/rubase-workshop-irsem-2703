#!/usr/bin/env python3
"""
Screenshot the left sidebars of Day 1, 2, and 3 landing pages for comparison
"""

from playwright.sync_api import sync_playwright
import time

def take_sidebar_screenshots():
    """Take screenshots of the sidebars for each day's landing page."""

    base_url = "https://sdspieg.github.io/rubase-workshop-fletcher-2603"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        # Day 1 - Main page (shows Day 1 sidebar by default)
        print("📸 Taking Day 1 sidebar screenshot...")
        page.goto(f"{base_url}")
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Screenshot just the sidebar area
        sidebar = page.locator('.sidebar')
        sidebar.screenshot(path='day1-sidebar.png')
        print("✅ Day 1 sidebar screenshot saved")

        # Day 2 - Click Day 2 to load Day 2 sidebar
        print("📸 Taking Day 2 sidebar screenshot...")
        page.click('.day2')
        page.wait_for_timeout(1000)

        sidebar = page.locator('.sidebar')
        sidebar.screenshot(path='day2-sidebar.png')
        print("✅ Day 2 sidebar screenshot saved")

        # Day 3 - Go to analyze landing page
        print("📸 Taking Day 3 sidebar screenshot...")
        page.goto(f"{base_url}/modules/analyze/")
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        sidebar = page.locator('.sidebar')
        sidebar.screenshot(path='day3-sidebar.png')
        print("✅ Day 3 sidebar screenshot saved")

        browser.close()

    print("\n🎯 All sidebar screenshots complete!")
    print("Files: day1-sidebar.png, day2-sidebar.png, day3-sidebar.png")

if __name__ == "__main__":
    take_sidebar_screenshots()