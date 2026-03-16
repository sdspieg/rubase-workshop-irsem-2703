#!/usr/bin/env python3
"""
Navigate to resources page and check the presentations section.
"""

from playwright.sync_api import sync_playwright
import time

def check_resources_page():
    """Navigate to resources and find the presentations section."""

    with sync_playwright() as p:
        print("=== CHECKING RESOURCES PAGE ===\n")
        browser = p.chromium.launch(headless=False)  # Show browser to see what's happening
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Go to main analyze module page
        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/index.html'
        print(f"Loading: {url}")
        page.goto(url, wait_until='networkidle')
        time.sleep(2)

        # Click on Resources in the sidebar
        print("\nLooking for Resources link in sidebar...")
        resource_links = page.query_selector_all('.sidebar-item')

        for link in resource_links:
            text = link.inner_text()
            print(f"Found sidebar item: {text}")
            if 'Resources' in text or 'resources' in text.lower():
                print(f"\nClicking on: {text}")
                link.click()
                time.sleep(2)
                break

        # Now check what's on the resources page
        print("\n=== RESOURCES PAGE CONTENT ===")

        # Look for presentations section/card
        presentations_section = page.query_selector_all('[class*="presentation"], [class*="Presentation"]')
        if presentations_section:
            print(f"Found {len(presentations_section)} presentation sections")
            for section in presentations_section:
                print(f"Section content: {section.inner_text()[:200]}...")

        # Check for any cards
        cards = page.query_selector_all('.card, .resource-card, [class*="card"]')
        print(f"\nFound {len(cards)} cards on the page")
        for i, card in enumerate(cards[:5]):  # Check first 5 cards
            title = card.query_selector('h3, h4, .card-title')
            if title:
                print(f"Card {i+1} title: {title.inner_text()}")

        # Check page structure
        main_content = page.query_selector('.main-content')
        if main_content:
            print("\n=== Main Content Structure ===")
            # Get all headings in main content
            headings = main_content.query_selector_all('h2, h3, h4')
            for h in headings:
                print(f"{h.evaluate('el => el.tagName')}: {h.inner_text()}")

        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    check_resources_page()