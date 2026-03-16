#!/usr/bin/env python3
"""
Fast comprehensive test of every link in the app
"""

from playwright.sync_api import sync_playwright
import time

def test_all_links_quickly():
    results = {'working': 0, 'broken': [], 'total': 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        base_url = 'https://sdspieg.github.io/rubase-workshop-fletcher-2603/'
        page.goto(base_url)
        page.wait_for_load_state('networkidle')

        print("=" * 60)
        print("TESTING EVERY LINK IN THE APP")
        print("=" * 60)

        # Collect all links to test
        all_tests = []

        # Header links
        all_tests.extend([
            ('Header', 'Resources', 'button:has-text("Resources")', 'resources', False),
            ('Header', 'Help', 'button:has-text("Help")', 'techhelp', False),
        ])

        # Landing page cards
        all_tests.extend([
            ('Landing', 'Workshop Schedule', '.quick-start-card:has-text("Workshop Schedule")', 'workshop-overview', False),
            ('Landing', 'Resources', '.quick-start-card:has-text("Resources")', 'resources', False),
            ('Landing', 'Tech Help', '.quick-start-card:has-text("Tech Help")', 'techhelp', False),
        ])

        # Day 1 sidebar - must load day first
        day1_sidebar = [
            ('Day1-Sidebar', 'Welcome & Setup', '.module-header:has-text("Welcome & Setup")', 'welcome-setup', False),
            ('Day1-Sidebar', 'Workshop Overview', '.module-header:has-text("Workshop Overview")', 'Workshop_Fletcher_Program', False),
            ('Day1-Sidebar', 'OpenAlex Discovery', '.module-header:has-text("OpenAlex Discovery")', 'openalex-explorer', False),
            ('Day1-Sidebar', 'Resources', '.module-header:has-text("Resources & Guides")', 'resources', False),
        ]

        # Day 1 cards
        day1_cards = [
            ('Day1-Card', 'Welcome & Setup', '.quick-start-card:has-text("Welcome & Setup")', 'welcome-setup', False),
            ('Day1-Card', 'OpenAlex Explorer', '.quick-start-card:has-text("OpenAlex Explorer")', 'openalex-explorer', False),
            ('Day1-Card', 'Resources', '.quick-start-card:has-text("Resources & Guides")', 'resources', False),
        ]

        # Day 2 sidebar
        day2_sidebar = [
            ('Day2-Sidebar', 'Reflections', '.module-header:has-text("Reflections")', 'Day2_Schedule', False),
            ('Day2-Sidebar', 'Deep Research', '.module-header:has-text("Deep Research")', 'Day2_Schedule', False),
            ('Day2-Sidebar', 'Russia-Ukraine', '.module-header:has-text("Russia-Ukraine")', 'rumilspace', True),
            ('Day2-Sidebar', 'Cartography', '.module-header:has-text("Cartography")', 'knowledge-cartography', False),
            ('Day2-Sidebar', 'Taxonomies', '.module-header:has-text("Building Taxonomies")', 'building-taxonomies', False),
            ('Day2-Sidebar', 'Exercise', '.module-header:has-text("Hands-On Exercise")', 'hands-on-exercise', False),
            ('Day2-Sidebar', 'Resources', '.module-header:has-text("Resources"):not(:has-text("All"))', 'resources', False),
        ]

        # Day 2 cards
        day2_cards = [
            ('Day2-Card', 'Cartography', '.quick-start-card:has-text("Knowledge Cartography")', 'knowledge-cartography', False),
            ('Day2-Card', 'Taxonomies', '.quick-start-card:has-text("Building Taxonomies")', 'building-taxonomies', False),
            ('Day2-Card', 'Exercise', '.quick-start-card:has-text("Hands-On Exercise")', 'hands-on-exercise', False),
        ]

        # Day 3 sidebar
        day3_sidebar = [
            ('Day3-Sidebar', 'Welcome', '.module-header:has-text("Day 3 Welcome")', 'Day3_Schedule', False),
            ('Day3-Sidebar', 'Ottoman', '.module-header:has-text("Ottoman Bank")', 'ottoman-bank-case-study', False),
            ('Day3-Sidebar', 'CLI LLMs', '.module-header:has-text("CLI LLMs Guide")', 'cli-llms-guide', False),
            ('Day3-Sidebar', 'Deep Research', '.module-header:has-text("Deep Research Guide")', 'deep-research-guide', False),
            ('Day3-Sidebar', 'WACKO', '.module-header:has-text("WACKO")', 'wacko-presentation', False),
            ('Day3-Sidebar', 'LLM Selection', '.module-header:has-text("LLM Selection")', 'llm-selection-guide', False),
            ('Day3-Sidebar', 'Workshop Package', '.module-header:has-text("Workshop Package")', 'Day3_Workshop_Package', False),
            ('Day3-Sidebar', 'All Resources', '.module-header:has-text("All Resources")', 'resources', False),
            ('Day3-Sidebar', 'Tech Help', '.module-header:has-text("Technical Help")', 'techhelp', False),
        ]

        # Day 3 cards
        day3_cards = [
            ('Day3-Card', 'Ottoman', '.quick-start-card:has-text("Ottoman Bank")', 'ottoman-bank-case-study', False),
            ('Day3-Card', 'CLI LLMs', '.quick-start-card:has-text("CLI LLMs Guide")', 'cli-llms-guide', False),
            ('Day3-Card', 'Deep Research', '.quick-start-card:has-text("Deep Research Guide")', 'deep-research-guide', False),
        ]

        # Test header and landing
        print("\n🔷 Testing Header & Landing Page...")
        for category, name, selector, expected, is_external in all_tests[:5]:
            element = page.query_selector(selector)
            if element:
                element.click()
                time.sleep(1)

                if is_external:
                    if len(page.context.pages) > 1:
                        print(f"  ✅ {category}: {name}")
                        results['working'] += 1
                        page.context.pages[-1].close()
                    else:
                        print(f"  ❌ {category}: {name} - No new tab")
                        results['broken'].append(f"{category}: {name}")
                elif expected in page.url:
                    print(f"  ✅ {category}: {name}")
                    results['working'] += 1
                else:
                    print(f"  ❌ {category}: {name}")
                    results['broken'].append(f"{category}: {name}")

                results['total'] += 1
                page.goto(base_url)
                page.wait_for_load_state('networkidle')

        # Test Day 1
        print("\n🔷 Testing Day 1...")
        page.evaluate('loadDay(1)')
        time.sleep(0.5)

        for category, name, selector, expected, is_external in day1_sidebar + day1_cards:
            element = page.query_selector(selector)
            if element:
                element.click()
                time.sleep(0.8)

                if expected in page.url:
                    print(f"  ✅ {category}: {name}")
                    results['working'] += 1
                else:
                    print(f"  ❌ {category}: {name}")
                    results['broken'].append(f"{category}: {name}")

                results['total'] += 1
                page.go_back()
                page.evaluate('loadDay(1)')
                time.sleep(0.3)

        # Test Day 2
        print("\n🔷 Testing Day 2...")
        page.evaluate('loadDay(2)')
        time.sleep(0.5)

        for category, name, selector, expected, is_external in day2_sidebar + day2_cards:
            element = page.query_selector(selector)
            if element:
                element.click()
                time.sleep(0.8)

                if is_external:
                    if len(page.context.pages) > 1:
                        print(f"  ✅ {category}: {name}")
                        results['working'] += 1
                        page.context.pages[-1].close()
                    else:
                        print(f"  ❌ {category}: {name} - No new tab")
                        results['broken'].append(f"{category}: {name}")
                elif expected in page.url:
                    print(f"  ✅ {category}: {name}")
                    results['working'] += 1
                else:
                    print(f"  ❌ {category}: {name}")
                    results['broken'].append(f"{category}: {name}")

                results['total'] += 1

                if not is_external:
                    page.go_back()

                page.evaluate('loadDay(2)')
                time.sleep(0.3)

        # Test Day 3
        print("\n🔷 Testing Day 3...")
        page.evaluate('loadDay(3)')
        time.sleep(0.5)

        for category, name, selector, expected, is_external in day3_sidebar + day3_cards:
            element = page.query_selector(selector)
            if element:
                element.click()
                time.sleep(0.8)

                if expected in page.url:
                    print(f"  ✅ {category}: {name}")
                    results['working'] += 1
                else:
                    print(f"  ❌ {category}: {name}")
                    results['broken'].append(f"{category}: {name}")

                results['total'] += 1
                page.go_back()
                page.evaluate('loadDay(3)')
                time.sleep(0.3)

        browser.close()

        # Final Report
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(f"\n✅ Working: {results['working']}")
        print(f"❌ Broken: {len(results['broken'])}")
        print(f"📊 Total: {results['total']}")

        if results['broken']:
            print("\n⚠️  BROKEN LINKS:")
            for link in results['broken']:
                print(f"  - {link}")
        else:
            print("\n🎉 ALL LINKS WORKING!")

        success_rate = (results['working'] * 100 / results['total']) if results['total'] > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    test_all_links_quickly()