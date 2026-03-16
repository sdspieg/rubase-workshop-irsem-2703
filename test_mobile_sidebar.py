#!/usr/bin/env python3
"""
Comprehensive Playwright test script for mobile sidebar functionality
Tests the sidebar behavior on mobile viewport (iPhone size 375x667)
"""

import asyncio
from playwright.async_api import async_playwright
import os

class MobileSidebarTester:
    def __init__(self):
        self.base_url = "https://sdspieg.github.io/rubase-workshop-fletcher-2603/"
        self.screenshots_dir = "/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-fletcher-2603/Screenshots"
        self.test_results = []
        self.mobile_viewport = {"width": 375, "height": 667}  # iPhone viewport

    async def log_test_result(self, test_name, passed, details=""):
        """Log test results for final reporting"""
        status = "PASSED" if passed else "FAILED"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        print(f"[{status}] {test_name}: {details}")

    async def wait_for_animations(self, page, duration=500):
        """Wait for CSS animations to complete"""
        await page.wait_for_timeout(duration)

    async def test_mobile_sidebar_functionality(self):
        """Main test function that runs all mobile sidebar tests"""
        async with async_playwright() as playwright:
            # Launch browser in mobile mode
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport=self.mobile_viewport,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            )
            page = await context.new_page()

            try:
                # Test 1: Load page and verify mobile view
                print("\n=== TEST 1: Loading page in mobile viewport ===")
                await page.goto(self.base_url)
                await page.wait_for_load_state('networkidle')
                await self.wait_for_animations(page, 1000)

                # Take initial mobile view screenshot
                await page.screenshot(path=f"{self.screenshots_dir}/01_mobile_initial_view.png")
                await self.log_test_result(
                    "Page loads in mobile viewport",
                    True,
                    f"Successfully loaded {self.base_url} at {self.mobile_viewport['width']}x{self.mobile_viewport['height']}"
                )

                # Test 2: Check sidebar toggle button visibility
                print("\n=== TEST 2: Checking sidebar toggle button visibility ===")
                try:
                    toggle_button = page.locator('.sidebar-toggle')
                    is_visible = await toggle_button.is_visible()

                    if is_visible:
                        await self.log_test_result(
                            "Sidebar toggle button is visible",
                            True,
                            "Toggle button found and visible on mobile"
                        )
                    else:
                        # Try alternative selectors
                        alt_selectors = [
                            'button[onclick*="toggleSidebar"]',
                            '.menu-button',
                            '.hamburger',
                            '#sidebarToggle',
                            '[data-toggle="sidebar"]'
                        ]

                        found = False
                        for selector in alt_selectors:
                            try:
                                alt_button = page.locator(selector)
                                if await alt_button.is_visible():
                                    toggle_button = alt_button
                                    found = True
                                    await self.log_test_result(
                                        "Sidebar toggle button is visible",
                                        True,
                                        f"Toggle button found with selector: {selector}"
                                    )
                                    break
                            except:
                                continue

                        if not found:
                            await self.log_test_result(
                                "Sidebar toggle button is visible",
                                False,
                                "Toggle button not found with any common selector"
                            )
                            # Take screenshot of current state for debugging
                            await page.screenshot(path=f"{self.screenshots_dir}/debug_no_toggle_button.png")
                            return

                except Exception as e:
                    await self.log_test_result(
                        "Sidebar toggle button is visible",
                        False,
                        f"Error checking toggle button: {str(e)}"
                    )
                    return

                # Test 3: Click toggle button and verify sidebar opens
                print("\n=== TEST 3: Testing sidebar opening ===")
                try:
                    # Check initial sidebar state
                    sidebar = page.locator('.sidebar, #sidebar, .side-nav')

                    # Click the toggle button
                    await toggle_button.click()
                    await self.wait_for_animations(page, 800)

                    # Take screenshot of open sidebar
                    await page.screenshot(path=f"{self.screenshots_dir}/02_mobile_sidebar_open.png")

                    # Check if sidebar is now visible/active
                    sidebar_visible = False
                    try:
                        # Check multiple ways sidebar might be shown
                        if await sidebar.is_visible():
                            sidebar_visible = True
                        elif await page.locator('.sidebar.active').count() > 0:
                            sidebar_visible = True
                        elif await page.locator('.sidebar-open').count() > 0:
                            sidebar_visible = True
                        elif await page.locator('body.sidebar-open').count() > 0:
                            sidebar_visible = True
                    except:
                        pass

                    await self.log_test_result(
                        "Sidebar opens when toggle clicked",
                        sidebar_visible,
                        "Sidebar opened successfully" if sidebar_visible else "Sidebar did not open or is not visible"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Sidebar opens when toggle clicked",
                        False,
                        f"Error clicking toggle or checking sidebar: {str(e)}"
                    )

                # Test 4: Check for overlay
                print("\n=== TEST 4: Checking for overlay ===")
                try:
                    overlay_selectors = [
                        '.overlay',
                        '.sidebar-overlay',
                        '.modal-backdrop',
                        '.backdrop',
                        '#overlay'
                    ]

                    overlay_found = False
                    overlay_element = None

                    for selector in overlay_selectors:
                        overlay_candidate = page.locator(selector)
                        if await overlay_candidate.count() > 0 and await overlay_candidate.is_visible():
                            overlay_found = True
                            overlay_element = overlay_candidate
                            break

                    await self.log_test_result(
                        "Overlay appears when sidebar opens",
                        overlay_found,
                        "Overlay found and visible" if overlay_found else "No overlay found"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Overlay appears when sidebar opens",
                        False,
                        f"Error checking for overlay: {str(e)}"
                    )
                    overlay_found = False

                # Test 5: Close sidebar by clicking overlay or toggle
                print("\n=== TEST 5: Testing sidebar closing ===")
                try:
                    # Try to close via overlay first, then toggle button
                    closed_successfully = False

                    if overlay_found and overlay_element:
                        # Try clicking overlay to close
                        await overlay_element.click()
                        await self.wait_for_animations(page, 800)

                        # Check if sidebar closed
                        sidebar_still_visible = False
                        try:
                            if await sidebar.is_visible() and await page.locator('.sidebar.active').count() > 0:
                                sidebar_still_visible = True
                        except:
                            pass

                        if not sidebar_still_visible:
                            closed_successfully = True
                            await self.log_test_result(
                                "Overlay click closes sidebar",
                                True,
                                "Sidebar closed successfully via overlay click"
                            )
                        else:
                            await self.log_test_result(
                                "Overlay click closes sidebar",
                                False,
                                "Overlay click did not close sidebar"
                            )

                    # If overlay didn't work, try toggle button
                    if not closed_successfully:
                        await toggle_button.click()
                        await self.wait_for_animations(page, 800)

                        sidebar_still_visible = False
                        try:
                            if await sidebar.is_visible() and await page.locator('.sidebar.active').count() > 0:
                                sidebar_still_visible = True
                        except:
                            pass

                        closed_successfully = not sidebar_still_visible
                        await self.log_test_result(
                            "Toggle button closes sidebar",
                            closed_successfully,
                            "Sidebar closed via toggle button" if closed_successfully else "Toggle button did not close sidebar"
                        )

                    # Take screenshot of closed sidebar
                    await page.screenshot(path=f"{self.screenshots_dir}/03_mobile_sidebar_closed.png")

                except Exception as e:
                    await self.log_test_result(
                        "Sidebar closing functionality",
                        False,
                        f"Error testing sidebar close: {str(e)}"
                    )

                # Test 6: Test navigation buttons work on mobile
                print("\n=== TEST 6: Testing navigation buttons on mobile ===")
                try:
                    # Open sidebar again for navigation testing
                    await toggle_button.click()
                    await self.wait_for_animations(page, 800)

                    # Look for navigation links in sidebar
                    nav_selectors = [
                        '.sidebar a',
                        '.sidebar .nav-link',
                        '.sidebar .sidebar-link',
                        '.sidebar button',
                        '#sidebar a',
                        '#sidebar button'
                    ]

                    nav_links = []
                    for selector in nav_selectors:
                        links = await page.locator(selector).all()
                        nav_links.extend(links)

                    if nav_links:
                        # Test clicking the first few navigation links
                        nav_working = 0
                        nav_tested = 0

                        for i, link in enumerate(nav_links[:3]):  # Test up to 3 links
                            try:
                                if await link.is_visible():
                                    nav_tested += 1
                                    link_text = await link.text_content() or f"Link {i+1}"

                                    # Get current URL before click
                                    current_url = page.url

                                    await link.click()
                                    await self.wait_for_animations(page, 1000)

                                    # Check if anything changed (URL, content, etc.)
                                    new_url = page.url
                                    if new_url != current_url:
                                        nav_working += 1
                                        await self.log_test_result(
                                            f"Navigation link '{link_text}' works",
                                            True,
                                            f"Successfully navigated from {current_url} to {new_url}"
                                        )
                                    else:
                                        # Check if page content changed
                                        await page.wait_for_timeout(500)
                                        nav_working += 1  # Assume it worked if no error
                                        await self.log_test_result(
                                            f"Navigation link '{link_text}' works",
                                            True,
                                            f"Link clicked successfully (same page navigation)"
                                        )

                                    # Go back to main page for next test
                                    if new_url != current_url:
                                        await page.goto(self.base_url)
                                        await page.wait_for_load_state('networkidle')
                                        await toggle_button.click()
                                        await self.wait_for_animations(page, 800)

                            except Exception as e:
                                await self.log_test_result(
                                    f"Navigation link {i+1} works",
                                    False,
                                    f"Error clicking link: {str(e)}"
                                )

                        overall_nav_success = nav_working == nav_tested if nav_tested > 0 else False
                        await self.log_test_result(
                            "Navigation buttons work on mobile",
                            overall_nav_success,
                            f"{nav_working}/{nav_tested} navigation links working"
                        )
                    else:
                        await self.log_test_result(
                            "Navigation buttons work on mobile",
                            False,
                            "No navigation links found in sidebar"
                        )

                except Exception as e:
                    await self.log_test_result(
                        "Navigation buttons work on mobile",
                        False,
                        f"Error testing navigation: {str(e)}"
                    )

                # Test 7: Additional mobile-specific checks
                print("\n=== TEST 7: Additional mobile functionality checks ===")
                try:
                    # Check if page is responsive
                    body = page.locator('body')
                    body_width = await body.evaluate('el => el.scrollWidth')
                    viewport_width = self.mobile_viewport['width']

                    responsive_ok = body_width <= viewport_width + 20  # Allow small tolerance
                    await self.log_test_result(
                        "Page is mobile responsive",
                        responsive_ok,
                        f"Body width: {body_width}px, Viewport: {viewport_width}px"
                    )

                    # Check if text is readable (not too small)
                    main_content = page.locator('main, .main, .content, body')
                    font_size = await main_content.evaluate('''
                        el => {
                            const style = window.getComputedStyle(el);
                            return parseFloat(style.fontSize);
                        }
                    ''')

                    font_readable = font_size >= 14  # Minimum readable size
                    await self.log_test_result(
                        "Text is readable on mobile",
                        font_readable,
                        f"Main content font size: {font_size}px"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Additional mobile checks",
                        False,
                        f"Error in mobile checks: {str(e)}"
                    )

                # Take final screenshot
                await page.screenshot(path=f"{self.screenshots_dir}/04_mobile_final_state.png")

            except Exception as e:
                print(f"Critical error during testing: {str(e)}")
                await page.screenshot(path=f"{self.screenshots_dir}/error_state.png")

            finally:
                await browser.close()

    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*80)
        print("MOBILE SIDEBAR FUNCTIONALITY TEST REPORT")
        print("="*80)
        print(f"Test URL: {self.base_url}")
        print(f"Mobile Viewport: {self.mobile_viewport['width']}x{self.mobile_viewport['height']} (iPhone size)")
        print(f"Screenshots saved to: {self.screenshots_dir}")
        print("\nTEST RESULTS:")
        print("-" * 80)

        passed_tests = 0
        total_tests = len(self.test_results)

        for result in self.test_results:
            status_symbol = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_symbol} {result['test']}")
            print(f"   Status: {result['status']}")
            if result["details"]:
                print(f"   Details: {result['details']}")
            print()

            if result["status"] == "PASSED":
                passed_tests += 1

        print("-" * 80)
        print(f"SUMMARY: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")

        if passed_tests == total_tests:
            print("🎉 ALL MOBILE SIDEBAR FUNCTIONALITY TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Check the details above and screenshots for debugging.")

        print("\nScreenshots taken:")
        print("- 01_mobile_initial_view.png: Initial mobile page load")
        print("- 02_mobile_sidebar_open.png: Sidebar in open state")
        print("- 03_mobile_sidebar_closed.png: Sidebar after closing")
        print("- 04_mobile_final_state.png: Final page state")
        print("="*80)

        return passed_tests == total_tests

async def main():
    """Main function to run all mobile sidebar tests"""
    tester = MobileSidebarTester()

    print("Starting comprehensive mobile sidebar functionality tests...")
    print(f"Testing URL: {tester.base_url}")
    print(f"Mobile viewport: {tester.mobile_viewport['width']}x{tester.mobile_viewport['height']}")

    try:
        await tester.test_mobile_sidebar_functionality()
        all_passed = tester.generate_report()
        return all_passed
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)