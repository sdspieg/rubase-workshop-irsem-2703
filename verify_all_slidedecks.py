#!/usr/bin/env python3
"""
Comprehensive verification of ALL slidedecks in the analyze module.
Checks styling consistency and readability across all presentations.
"""

from playwright.sync_api import sync_playwright
import time

def verify_all_slidedecks():
    """Verify all slidedecks for consistency and readability."""

    slidedecks = [
        ("ottoman-bank-case-study.html", "Ottoman Bank Case Study"),
        ("cli-llms-guide.html", "CLI LLMs Guide"),
        ("deep-research-guide.html", "Deep Research Guide"),
        ("wacko-presentation.html", "WACKO Presentation")
    ]

    base_url = "https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/"

    with sync_playwright() as p:
        print("=== COMPREHENSIVE SLIDEDECK VERIFICATION ===\n")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        all_issues = []

        for filename, title in slidedecks:
            print(f"\n{'='*60}")
            print(f"CHECKING: {title}")
            print(f"File: {filename}")
            print(f"{'='*60}\n")

            url = base_url + filename
            page.goto(url, wait_until='networkidle')
            time.sleep(2)

            # Get total slides
            slides = page.query_selector_all('.slide')
            total_slides = len(slides)
            print(f"Total slides: {total_slides}\n")

            presentation_issues = []

            # Check first, middle, and last slides
            check_slides = [0, total_slides//2, total_slides-1] if total_slides > 2 else range(total_slides)

            for slide_idx in check_slides:
                slide_num = slide_idx + 1

                # Navigate to slide
                for _ in range(slide_idx):
                    page.keyboard.press('ArrowRight')
                    time.sleep(0.2)

                slide = page.query_selector('.slide.active')

                if slide:
                    print(f"Slide {slide_num}/{total_slides}:")

                    # 1. CHECK BACKGROUND COLOR
                    bg = slide.evaluate('el => window.getComputedStyle(el).background')
                    if 'rgb(26, 42, 74)' in bg or '#1a2a4a' in bg or 'linear-gradient' in bg:
                        print("  ✅ Dark blue background")
                    else:
                        print(f"  ❌ WRONG BACKGROUND: {bg[:80]}...")
                        presentation_issues.append(f"Slide {slide_num}: Wrong background")

                    # 2. CHECK TEXT COLORS
                    # Check h1
                    h1 = slide.query_selector('h1')
                    if h1:
                        h1_color = h1.evaluate('el => window.getComputedStyle(el).color')
                        if 'rgb(255, 255, 255)' in h1_color or 'rgb(0, 255, 255)' in h1_color:
                            print("  ✅ H1 is white/cyan")
                        else:
                            print(f"  ❌ H1 COLOR: {h1_color}")
                            presentation_issues.append(f"Slide {slide_num}: H1 not white/cyan")

                    # Check h2
                    h2 = slide.query_selector('h2')
                    if h2:
                        h2_color = h2.evaluate('el => window.getComputedStyle(el).color')
                        if 'rgb(0, 255, 255)' in h2_color or 'rgb(255, 255, 255)' in h2_color:
                            print("  ✅ H2 is cyan/white")
                        else:
                            print(f"  ❌ H2 COLOR: {h2_color}")
                            presentation_issues.append(f"Slide {slide_num}: H2 not cyan")

                    # Check paragraphs
                    paragraphs = slide.query_selector_all('p')
                    if paragraphs and len(paragraphs) > 0:
                        p_color = paragraphs[0].evaluate('el => window.getComputedStyle(el).color')
                        if 'rgb(255, 255, 255)' in p_color or 'rgba(255, 255, 255' in p_color:
                            print("  ✅ Text is white")
                        else:
                            print(f"  ❌ TEXT COLOR: {p_color}")
                            presentation_issues.append(f"Slide {slide_num}: Text not white")

                    # Check lists
                    lists = slide.query_selector_all('li')
                    if lists and len(lists) > 0:
                        li_color = lists[0].evaluate('el => window.getComputedStyle(el).color')
                        if 'rgb(255, 255, 255)' in li_color or 'rgba(255, 255, 255' in li_color:
                            print("  ✅ Lists are white")
                        elif 'rgb(34,' in li_color or 'rgb(52,' in li_color:
                            print(f"  ❌ LISTS ARE DARK: {li_color}")
                            presentation_issues.append(f"Slide {slide_num}: Lists are dark gray")

                    # Check tables
                    tables = slide.query_selector_all('td')
                    if tables and len(tables) > 0:
                        td_color = tables[0].evaluate('el => window.getComputedStyle(el).color')
                        if 'rgb(255, 255, 255)' in td_color or 'rgb(0, 255, 255)' in td_color:
                            print("  ✅ Table cells are white/cyan")
                        elif 'rgb(0, 0, 0)' in td_color:
                            print(f"  ❌ TABLE CELLS ARE BLACK")
                            presentation_issues.append(f"Slide {slide_num}: Table cells are black")

                    # 3. CHECK CONTENT FIT
                    scroll_height = slide.evaluate('el => el.scrollHeight')
                    client_height = slide.evaluate('el => el.clientHeight')
                    if scroll_height > client_height:
                        overflow = scroll_height - client_height
                        print(f"  ⚠️ Content overflows by {overflow}px")
                        presentation_issues.append(f"Slide {slide_num}: Overflow {overflow}px")
                    else:
                        print("  ✅ Content fits")

                    # 4. CHECK SCREEN USAGE
                    viewport_height = page.evaluate('() => window.innerHeight')
                    usage = (client_height / viewport_height) * 100
                    if usage < 75:
                        print(f"  ⚠️ Low screen usage: {usage:.1f}%")
                    else:
                        print(f"  ✅ Screen usage: {usage:.1f}%")

                    print()

                # Reset for next check
                page.reload()
                time.sleep(1)

            if presentation_issues:
                print(f"\n❌ ISSUES FOUND in {title}:")
                for issue in presentation_issues:
                    print(f"  - {issue}")
                all_issues.extend([(title, issue) for issue in presentation_issues])
            else:
                print(f"\n✅ {title} is properly styled!")

        browser.close()

        # FINAL SUMMARY
        print("\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)

        if all_issues:
            print(f"\n❌ FOUND {len(all_issues)} TOTAL ISSUES:\n")
            for presentation, issue in all_issues:
                print(f"  [{presentation}] {issue}")

            print("\n📋 REQUIRED FIXES:")
            print("1. Ensure all slides have dark blue background (#1a2a4a)")
            print("2. Make all h1 white, h2 cyan")
            print("3. Make all text white with opacity")
            print("4. Fix any dark gray lists or black table cells")
            print("5. Adjust content to fit without scrolling")
        else:
            print("\n✅ ALL SLIDEDECKS ARE CONSISTENT AND PROPERLY STYLED!")

        return len(all_issues) == 0

if __name__ == "__main__":
    result = verify_all_slidedecks()
    exit(0 if result else 1)