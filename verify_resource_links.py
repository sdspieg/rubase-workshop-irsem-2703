#!/usr/bin/env python3
"""
Verify all slidedeck links in the resources page work correctly.
"""

from playwright.sync_api import sync_playwright
import time

def verify_resource_links():
    """Check that all presentation links in resources page work."""

    slidedecks = [
        ("📊 Ottoman Bank Case Study", "ottoman-bank-case-study.html"),
        ("🤖 CLI LLMs Guide", "cli-llms-guide.html"),
        ("🔍 Deep Research", "deep-research-guide.html"),
        ("🎯 WACKO", "wacko-presentation.html")
    ]

    with sync_playwright() as p:
        print("=== VERIFYING RESOURCE LINKS ===\n")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Load the resources page
        url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/index.html'
        print(f"Loading resources page: {url}")
        page.goto(url, wait_until='networkidle')
        time.sleep(2)

        print("\n1. Checking Resources Section:")
        print("-" * 40)

        # Check each slidedeck link
        all_good = True
        for title, filename in slidedecks:
            # Find the link in resources
            resource_links = page.query_selector_all('.resource-item')
            found = False

            for link in resource_links:
                text = link.inner_text()
                if title in text or filename.replace('.html', '') in text.lower():
                    found = True
                    href = link.get_attribute('href')

                    # Click the link and verify it loads
                    link.click()
                    time.sleep(2)

                    # Check if we're on the right page
                    current_url = page.url
                    if filename in current_url:
                        print(f"✅ {title}: Link works correctly")

                        # Check if slides load
                        slides = page.query_selector_all('.slide')
                        if slides:
                            print(f"   └─ Found {len(slides)} slides")
                    else:
                        print(f"❌ {title}: Link failed - wrong page")
                        all_good = False

                    # Go back to resources page
                    page.go_back()
                    time.sleep(1)
                    break

            if not found:
                print(f"❌ {title}: NOT FOUND in resources!")
                all_good = False

        print("\n2. Checking Sidebar Links:")
        print("-" * 40)

        # Check sidebar links too
        sidebar_links = page.query_selector_all('.sidebar-item.highlight')
        for link in sidebar_links:
            text = link.inner_text()
            href = link.get_attribute('href')
            if href and href.endswith('.html'):
                for title, filename in slidedecks:
                    if filename in href:
                        print(f"✅ Sidebar: {text} → {filename}")
                        break

        print("\n3. Checking New Content Banner:")
        print("-" * 40)

        # Check if new content banner has all links
        banner = page.query_selector('.available-banner')
        if banner:
            banner_text = banner.inner_text()
            for title, _ in slidedecks:
                if title in banner_text:
                    print(f"✅ Banner includes: {title}")

        browser.close()

        print("\n" + "="*50)
        if all_good:
            print("✅ ALL SLIDEDECK LINKS ARE WORKING!")
        else:
            print("❌ SOME LINKS NEED FIXING")
        print("="*50)

        return all_good

if __name__ == "__main__":
    result = verify_resource_links()
    exit(0 if result else 1)