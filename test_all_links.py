#!/usr/bin/env python3
"""
Test that all slidedeck links work after renaming
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_all_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Go to main page
        page.goto('file:///mnt/c/Users/Stephan/Dropbox/Presentations/2603%20-%20Boston_instructors/rubase-workshop-fletcher-2603/index.html')
        page.wait_for_load_state('networkidle')

        print("=== TESTING ALL SLIDEDECK LINKS ===\n")

        # Test Day 1 links
        print("DAY 1 - DISCOVER:")
        page.evaluate('loadDay(1)')
        time.sleep(1)

        # Test welcome link
        welcome_link = page.query_selector('[href*="welcome/welcome-setup.html"]')
        if welcome_link:
            print("  ✓ Welcome setup link found")
            # Check if file exists
            if os.path.exists('modules/welcome/welcome-setup.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ Welcome link NOT FOUND")

        # Test OpenAlex link
        openalex_link = page.query_selector('[href*="openalex/openalex-explorer.html"]')
        if openalex_link:
            print("  ✓ OpenAlex explorer link found")
            if os.path.exists('modules/openalex/openalex-explorer.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ OpenAlex link NOT FOUND")

        # Test Day 2 links
        print("\nDAY 2 - FRAME:")
        page.evaluate('loadDay(2)')
        time.sleep(1)

        cartography_link = page.query_selector('[href*="cartography/knowledge-cartography.html"]')
        if cartography_link:
            print("  ✓ Knowledge cartography link found")
            if os.path.exists('modules/cartography/knowledge-cartography.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ Cartography link NOT FOUND")

        frame_link = page.query_selector('[href*="frame/building-taxonomies.html"]')
        if frame_link:
            print("  ✓ Building taxonomies link found")
            if os.path.exists('modules/frame/building-taxonomies.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ Frame link NOT FOUND")

        exercise_link = page.query_selector('[href*="exercise/hands-on-exercise.html"]')
        if exercise_link:
            print("  ✓ Hands-on exercise link found")
            if os.path.exists('modules/exercise/hands-on-exercise.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ Exercise link NOT FOUND")

        # Test Day 3 links
        print("\nDAY 3 - ANALYZE:")
        page.evaluate('loadDay(3)')
        time.sleep(1)

        ottoman_link = page.query_selector('[href*="ottoman-bank-case-study.html"]')
        if ottoman_link:
            print("  ✓ Ottoman bank link found")
            if os.path.exists('modules/analyze/ottoman-bank-case-study.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ Ottoman link NOT FOUND")

        cli_link = page.query_selector('[href*="cli-llms-guide.html"]')
        if cli_link:
            print("  ✓ CLI LLMs guide link found")
            if os.path.exists('modules/analyze/cli-llms-guide.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ CLI link NOT FOUND")

        deep_link = page.query_selector('[href*="deep-research-guide.html"]')
        if deep_link:
            print("  ✓ Deep research link found")
            if os.path.exists('modules/analyze/deep-research-guide.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ Deep research link NOT FOUND")

        wacko_link = page.query_selector('[href*="wacko-presentation.html"]')
        if wacko_link:
            print("  ✓ WACKO presentation link found")
            if os.path.exists('modules/analyze/wacko-presentation.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ WACKO link NOT FOUND")

        llm_select_link = page.query_selector('[href*="llm-selection-guide.html"]')
        if llm_select_link:
            print("  ✓ LLM selection guide link found")
            if os.path.exists('modules/analyze/llm-selection-guide.html'):
                print("    ✓ File exists")
            else:
                print("    ❌ FILE MISSING!")
        else:
            print("  ❌ LLM selection link NOT FOUND")

        # Now test clicking a few key links
        print("\n=== TESTING LINK CLICKS ===")

        # Test Day 2 cartography link
        page.evaluate('loadDay(2)')
        time.sleep(1)
        cartography_element = page.query_selector('[onclick*="knowledge-cartography.html"]')
        if cartography_element:
            print("\nClicking Knowledge Cartography...")
            cartography_element.click()
            time.sleep(2)

            # Check if we navigated correctly
            if 'knowledge-cartography.html' in page.url:
                print("  ✓ Successfully navigated to Knowledge Cartography")
            else:
                print(f"  ❌ Navigation failed. URL: {page.url}")

            # Go back
            page.go_back()
            time.sleep(1)

        # Test Day 3 ottoman link
        page.evaluate('loadDay(3)')
        time.sleep(1)
        ottoman_element = page.query_selector('[onclick*="ottoman-bank-case-study.html"]')
        if ottoman_element:
            print("\nClicking Ottoman Bank Case Study...")
            ottoman_element.click()
            time.sleep(2)

            if 'ottoman-bank-case-study.html' in page.url:
                print("  ✓ Successfully navigated to Ottoman Bank")
            else:
                print(f"  ❌ Navigation failed. URL: {page.url}")

        browser.close()
        print("\n✅ Link testing complete!")

if __name__ == "__main__":
    test_all_links()