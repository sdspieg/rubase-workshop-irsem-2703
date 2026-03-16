#!/usr/bin/env python3
"""
Comprehensive test of EVERY link in the entire app
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_every_single_link():
    results = {
        'working': [],
        'broken': [],
        'not_found': []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Use live site for testing
        base_url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/'
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("="*60)
        print("COMPREHENSIVE LINK TEST - EVERY LINK IN THE APP")
        print("="*60)

        # ===========================================
        # 1. TEST HEADER NAVIGATION
        # ===========================================
        print("\n🔷 TESTING HEADER NAVIGATION:")

        # Resources button
        resources_btn = page.query_selector('button:has-text("Resources")')
        if resources_btn:
            resources_btn.click()
            time.sleep(2)
            if 'resources' in page.url:
                print("  ✅ Header Resources button works")
                results['working'].append("Header: Resources")
            else:
                print(f"  ❌ Header Resources button broken - URL: {page.url}")
                results['broken'].append("Header: Resources")
            page.go_back()
            time.sleep(1)

        # Help button
        help_btn = page.query_selector('button:has-text("Help")')
        if help_btn:
            help_btn.click()
            time.sleep(2)
            if 'techhelp' in page.url:
                print("  ✅ Header Help button works")
                results['working'].append("Header: Help")
            else:
                print(f"  ❌ Header Help button broken - URL: {page.url}")
                results['broken'].append("Header: Help")
            page.go_back()
            time.sleep(1)

        # Home button
        home_btn = page.query_selector('button:has-text("Home")')
        if home_btn:
            # First navigate away
            page.evaluate('loadDay(1)')
            time.sleep(1)
            home_btn.click()
            time.sleep(1)
            # Check if welcome screen is visible
            welcome = page.query_selector('.welcome-screen')
            if welcome and welcome.is_visible():
                print("  ✅ Header Home button works")
                results['working'].append("Header: Home")
            else:
                print("  ❌ Header Home button doesn't return to welcome")
                results['broken'].append("Header: Home")

        # ===========================================
        # 2. TEST LANDING PAGE QUICK-START CARDS
        # ===========================================
        print("\n🔷 TESTING LANDING PAGE CARDS:")

        # Make sure we're on landing page
        page.goto(base_url)
        time.sleep(2)

        landing_cards = [
            ("Workshop Schedule", "workshop-overview"),
            ("Resources", "resources"),
            ("Tech Help", "techhelp")
        ]

        for card_name, expected_url in landing_cards:
            card = page.query_selector(f'.quick-start-card:has-text("{card_name}")')
            if card:
                card.click()
                time.sleep(2)
                if expected_url in page.url:
                    print(f"  ✅ Landing: {card_name} card works")
                    results['working'].append(f"Landing: {card_name}")
                else:
                    print(f"  ❌ Landing: {card_name} card broken - URL: {page.url}")
                    results['broken'].append(f"Landing: {card_name}")
                page.go_back()
                time.sleep(1)

        # ===========================================
        # 3. TEST DAY 1 LINKS
        # ===========================================
        print("\n🔷 TESTING DAY 1 - DISCOVER:")
        page.evaluate('loadDay(1)')
        time.sleep(2)

        # Test sidebar links
        day1_sidebar = [
            ("Welcome & Setup", "welcome-setup"),
            ("Workshop Overview", "Workshop_Fletcher_Program"),
            ("OpenAlex Discovery", "openalex-explorer"),
            ("Resources & Guides", "resources")
        ]

        for link_text, expected in day1_sidebar:
            element = page.query_selector(f'.module-header:has-text("{link_text}")')
            if element:
                element.click()
                time.sleep(2)
                if expected in page.url:
                    print(f"  ✅ Day 1 Sidebar: {link_text}")
                    results['working'].append(f"Day 1 Sidebar: {link_text}")
                else:
                    print(f"  ❌ Day 1 Sidebar: {link_text} - Got: {page.url}")
                    results['broken'].append(f"Day 1 Sidebar: {link_text}")
                page.go_back()
                time.sleep(1)
                page.evaluate('loadDay(1)')  # Reload Day 1
                time.sleep(1)

        # Test content area cards
        day1_cards = [
            ("Welcome & Setup", "welcome-setup"),
            ("OpenAlex Explorer", "openalex-explorer"),
            ("Resources & Guides", "resources")
        ]

        for card_text, expected in day1_cards:
            card = page.query_selector(f'.quick-start-card:has-text("{card_text}")')
            if card:
                card.click()
                time.sleep(2)
                if expected in page.url:
                    print(f"  ✅ Day 1 Card: {card_text}")
                    results['working'].append(f"Day 1 Card: {card_text}")
                else:
                    print(f"  ❌ Day 1 Card: {card_text} - Got: {page.url}")
                    results['broken'].append(f"Day 1 Card: {card_text}")
                page.go_back()
                time.sleep(1)
                page.evaluate('loadDay(1)')
                time.sleep(1)

        # ===========================================
        # 4. TEST DAY 2 LINKS
        # ===========================================
        print("\n🔷 TESTING DAY 2 - FRAME:")
        page.evaluate('loadDay(2)')
        time.sleep(2)

        # Test sidebar links
        day2_sidebar = [
            ("Reflections From Yesterday", "Day2_Schedule"),
            ("Deep Research Methods", "Day2_Schedule"),
            ("Demo: Russia-Ukraine", "rumilspace.app"),
            ("Knowledge Cartography", "knowledge-cartography"),
            ("Building Taxonomies", "building-taxonomies"),
            ("Hands-On Exercise", "hands-on-exercise"),
            ("Quality Control", "Day2_Schedule"),
            ("Resources", "resources"),
            ("RuBase Dashboard", "rumilspace.app")
        ]

        for link_text, expected in day2_sidebar:
            element = page.query_selector(f'.module-header:has-text("{link_text}")')
            if element:
                # Skip dinner break
                if "Dinner" in link_text:
                    continue

                element.click()
                time.sleep(2)

                # Handle external links
                if "rumilspace" in expected:
                    # Check if new tab opened
                    if len(page.context.pages) > 1:
                        print(f"  ✅ Day 2 Sidebar: {link_text} (external)")
                        results['working'].append(f"Day 2 Sidebar: {link_text}")
                        # Close the new tab
                        page.context.pages[-1].close()
                    else:
                        print(f"  ❌ Day 2 Sidebar: {link_text} - No new tab")
                        results['broken'].append(f"Day 2 Sidebar: {link_text}")
                elif expected in page.url:
                    print(f"  ✅ Day 2 Sidebar: {link_text}")
                    results['working'].append(f"Day 2 Sidebar: {link_text}")
                    page.go_back()
                    time.sleep(1)
                    page.evaluate('loadDay(2)')
                    time.sleep(1)
                else:
                    print(f"  ❌ Day 2 Sidebar: {link_text} - Got: {page.url}")
                    results['broken'].append(f"Day 2 Sidebar: {link_text}")
                    page.go_back()
                    time.sleep(1)
                    page.evaluate('loadDay(2)')
                    time.sleep(1)

        # Test content area cards
        day2_cards = [
            ("Knowledge Cartography", "knowledge-cartography"),
            ("Building Taxonomies", "building-taxonomies"),
            ("Hands-On Exercise", "hands-on-exercise")
        ]

        for card_text, expected in day2_cards:
            card = page.query_selector(f'.quick-start-card:has-text("{card_text}")')
            if card:
                card.click()
                time.sleep(2)
                if expected in page.url:
                    print(f"  ✅ Day 2 Card: {card_text}")
                    results['working'].append(f"Day 2 Card: {card_text}")
                else:
                    print(f"  ❌ Day 2 Card: {card_text} - Got: {page.url}")
                    results['broken'].append(f"Day 2 Card: {card_text}")
                page.go_back()
                time.sleep(1)
                page.evaluate('loadDay(2)')
                time.sleep(1)

        # ===========================================
        # 5. TEST DAY 3 LINKS
        # ===========================================
        print("\n🔷 TESTING DAY 3 - ANALYZE:")
        page.evaluate('loadDay(3)')
        time.sleep(2)

        # Test sidebar links
        day3_sidebar = [
            ("Day 3 Welcome", "Day3_Schedule"),
            ("Ottoman Bank Case Study", "ottoman-bank-case-study"),
            ("CLI LLMs Guide", "cli-llms-guide"),
            ("Deep Research Guide", "deep-research-guide"),
            ("WACKO Presentation", "wacko-presentation"),
            ("LLM Selection Guide", "llm-selection-guide"),
            ("Data Visualization", "Day3_Schedule"),
            ("Workshop Package", "Day3_Workshop_Package"),
            ("CLI Setup Guide", "CLI_LLM_Setup_Guide"),
            ("All Resources", "resources"),
            ("Technical Help", "techhelp")
        ]

        for link_text, expected in day3_sidebar:
            element = page.query_selector(f'.module-header:has-text("{link_text}")')
            if element:
                element.click()
                time.sleep(2)
                if expected in page.url:
                    print(f"  ✅ Day 3 Sidebar: {link_text}")
                    results['working'].append(f"Day 3 Sidebar: {link_text}")
                else:
                    print(f"  ❌ Day 3 Sidebar: {link_text} - Got: {page.url}")
                    results['broken'].append(f"Day 3 Sidebar: {link_text}")
                page.go_back()
                time.sleep(1)
                page.evaluate('loadDay(3)')
                time.sleep(1)

        # Test content area cards
        day3_cards = [
            ("Ottoman Bank Case Study", "ottoman-bank-case-study"),
            ("CLI LLMs Guide", "cli-llms-guide"),
            ("Deep Research Guide", "deep-research-guide")
        ]

        for card_text, expected in day3_cards:
            card = page.query_selector(f'.quick-start-card:has-text("{card_text}")')
            if card:
                card.click()
                time.sleep(2)
                if expected in page.url:
                    print(f"  ✅ Day 3 Card: {card_text}")
                    results['working'].append(f"Day 3 Card: {card_text}")
                else:
                    print(f"  ❌ Day 3 Card: {card_text} - Got: {page.url}")
                    results['broken'].append(f"Day 3 Card: {card_text}")
                page.go_back()
                time.sleep(1)
                page.evaluate('loadDay(3)')
                time.sleep(1)

        browser.close()

        # ===========================================
        # FINAL REPORT
        # ===========================================
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60)

        print(f"\n✅ WORKING LINKS: {len(results['working'])}")
        print(f"❌ BROKEN LINKS: {len(results['broken'])}")

        if results['broken']:
            print("\n⚠️  BROKEN LINKS DETAILS:")
            for link in results['broken']:
                print(f"  - {link}")
        else:
            print("\n🎉 ALL LINKS ARE WORKING PERFECTLY!")

        total = len(results['working']) + len(results['broken'])
        success_rate = (len(results['working']) * 100 / total) if total > 0 else 0
        print(f"\n📊 Success Rate: {len(results['working'])}/{total} = {success_rate:.1f}%")

if __name__ == "__main__":
    test_every_single_link()