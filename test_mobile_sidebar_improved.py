#!/usr/bin/env python3
"""
Improved Playwright test script for mobile sidebar functionality
Addresses issues found in initial testing and provides more comprehensive checks
"""

import asyncio
from playwright.async_api import async_playwright
import os

class ImprovedMobileSidebarTester:
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

    async def test_mobile_sidebar_comprehensive(self):
        """Comprehensive test of mobile sidebar functionality"""
        async with async_playwright() as playwright:
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
                await self.wait_for_animations(page, 1500)

                # Take initial mobile view screenshot
                await page.screenshot(path=f"{self.screenshots_dir}/mobile_01_initial.png")
                await self.log_test_result(
                    "Page loads in mobile viewport",
                    True,
                    f"Successfully loaded {self.base_url}"
                )

                # Test 2: Find and verify sidebar toggle button
                print("\n=== TEST 2: Locating sidebar toggle button ===")
                toggle_button = None
                toggle_selectors = [
                    '.sidebar-toggle',
                    'button[onclick*="toggleSidebar"]',
                    '.menu-button',
                    '.hamburger',
                    '#sidebarToggle',
                    '[data-toggle="sidebar"]',
                    'button:has-text("☰")',
                    'button:has-text("≡")',
                    '.toggle-btn'
                ]

                for selector in toggle_selectors:
                    try:
                        candidate = page.locator(selector)
                        if await candidate.count() > 0 and await candidate.is_visible():
                            toggle_button = candidate.first
                            await self.log_test_result(
                                "Sidebar toggle button found",
                                True,
                                f"Found with selector: {selector}"
                            )
                            break
                    except:
                        continue

                if not toggle_button:
                    await self.log_test_result(
                        "Sidebar toggle button found",
                        False,
                        "No toggle button found with any common selector"
                    )
                    await page.screenshot(path=f"{self.screenshots_dir}/mobile_debug_no_toggle.png")
                    return

                # Test 3: Analyze initial sidebar state
                print("\n=== TEST 3: Analyzing sidebar initial state ===")
                sidebar_selectors = ['.sidebar', '#sidebar', '.side-nav', '.navigation-sidebar']
                sidebar_element = None

                for selector in sidebar_selectors:
                    try:
                        candidate = page.locator(selector)
                        if await candidate.count() > 0:
                            sidebar_element = candidate.first
                            break
                    except:
                        continue

                if sidebar_element:
                    # Check initial visibility and position
                    is_initially_visible = await sidebar_element.is_visible()
                    await self.log_test_result(
                        "Sidebar element found",
                        True,
                        f"Initial visibility: {'visible' if is_initially_visible else 'hidden'}"
                    )
                else:
                    await self.log_test_result(
                        "Sidebar element found",
                        False,
                        "No sidebar element found"
                    )

                # Test 4: Click toggle and verify sidebar behavior
                print("\n=== TEST 4: Testing sidebar toggle functionality ===")
                try:
                    # Get page state before toggle
                    initial_state = await page.evaluate('''() => {
                        const sidebar = document.querySelector('.sidebar, #sidebar, .side-nav');
                        const body = document.body;
                        return {
                            sidebarDisplay: sidebar ? window.getComputedStyle(sidebar).display : 'none',
                            sidebarTransform: sidebar ? window.getComputedStyle(sidebar).transform : 'none',
                            bodyClass: body.className,
                            sidebarClass: sidebar ? sidebar.className : ''
                        };
                    }''')

                    print(f"Initial state: {initial_state}")

                    # Click toggle button
                    await toggle_button.click()
                    await self.wait_for_animations(page, 1000)

                    # Get state after toggle
                    toggled_state = await page.evaluate('''() => {
                        const sidebar = document.querySelector('.sidebar, #sidebar, .side-nav');
                        const body = document.body;
                        return {
                            sidebarDisplay: sidebar ? window.getComputedStyle(sidebar).display : 'none',
                            sidebarTransform: sidebar ? window.getComputedStyle(sidebar).transform : 'none',
                            bodyClass: body.className,
                            sidebarClass: sidebar ? sidebar.className : ''
                        };
                    }''')

                    print(f"Toggled state: {toggled_state}")

                    # Check if state changed (indicating sidebar opened)
                    state_changed = (
                        initial_state['sidebarClass'] != toggled_state['sidebarClass'] or
                        initial_state['bodyClass'] != toggled_state['bodyClass'] or
                        initial_state['sidebarTransform'] != toggled_state['sidebarTransform']
                    )

                    # Take screenshot of open state
                    await page.screenshot(path=f"{self.screenshots_dir}/mobile_02_sidebar_opened.png")

                    await self.log_test_result(
                        "Sidebar opens when toggle clicked",
                        state_changed,
                        f"State change detected: {state_changed}"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Sidebar opens when toggle clicked",
                        False,
                        f"Error during toggle test: {str(e)}"
                    )

                # Test 5: Check for overlay or backdrop
                print("\n=== TEST 5: Checking for overlay/backdrop ===")
                try:
                    overlay_found = await page.evaluate('''() => {
                        const overlaySelectors = [
                            '.overlay', '.sidebar-overlay', '.modal-backdrop',
                            '.backdrop', '#overlay', '.menu-overlay'
                        ];

                        for (const selector of overlaySelectors) {
                            const element = document.querySelector(selector);
                            if (element) {
                                const style = window.getComputedStyle(element);
                                if (style.display !== 'none' && style.opacity !== '0') {
                                    return {found: true, selector: selector, visible: true};
                                }
                            }
                        }

                        // Check for any element with overlay-like styling
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            const style = window.getComputedStyle(el);
                            if (style.position === 'fixed' &&
                                style.zIndex > 100 &&
                                style.backgroundColor &&
                                style.backgroundColor.includes('rgba')) {
                                return {found: true, selector: 'dynamic', visible: true};
                            }
                        }

                        return {found: false};
                    }''')

                    await self.log_test_result(
                        "Overlay/backdrop appears",
                        overlay_found['found'] if overlay_found else False,
                        f"Overlay status: {overlay_found}"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Overlay/backdrop appears",
                        False,
                        f"Error checking overlay: {str(e)}"
                    )

                # Test 6: Test sidebar navigation elements
                print("\n=== TEST 6: Testing sidebar navigation elements ===")
                try:
                    # Look for clickable elements in sidebar
                    nav_elements = await page.evaluate('''() => {
                        const sidebar = document.querySelector('.sidebar, #sidebar, .side-nav');
                        if (!sidebar) return {found: false, elements: []};

                        const clickables = sidebar.querySelectorAll('a, button, [onclick], .clickable, .nav-item');
                        const elements = Array.from(clickables).map((el, index) => ({
                            tag: el.tagName,
                            text: el.textContent.trim(),
                            href: el.href || null,
                            onclick: el.onclick ? 'has onclick' : null,
                            index: index
                        })).filter(el => el.text.length > 0);

                        return {found: elements.length > 0, elements: elements};
                    }''')

                    if nav_elements['found']:
                        nav_count = len(nav_elements['elements'])
                        await self.log_test_result(
                            "Navigation elements found in sidebar",
                            True,
                            f"Found {nav_count} navigation elements: {[el['text'][:20] for el in nav_elements['elements'][:3]]}"
                        )

                        # Test clicking first navigation element
                        if nav_elements['elements']:
                            first_nav = nav_elements['elements'][0]
                            try:
                                if first_nav['href']:
                                    nav_selector = f'a[href="{first_nav["href"]}"]'
                                else:
                                    nav_selector = f'.sidebar :nth-child({first_nav["index"] + 1})'

                                await page.locator(nav_selector).first.click()
                                await self.wait_for_animations(page, 1000)

                                await self.log_test_result(
                                    "Navigation element clickable",
                                    True,
                                    f"Successfully clicked: {first_nav['text'][:30]}"
                                )
                            except Exception as e:
                                await self.log_test_result(
                                    "Navigation element clickable",
                                    False,
                                    f"Error clicking navigation: {str(e)}"
                                )
                    else:
                        await self.log_test_result(
                            "Navigation elements found in sidebar",
                            False,
                            "No navigation elements found in sidebar"
                        )

                except Exception as e:
                    await self.log_test_result(
                        "Navigation elements found in sidebar",
                        False,
                        f"Error testing navigation: {str(e)}"
                    )

                # Test 7: Test closing sidebar
                print("\n=== TEST 7: Testing sidebar closing ===")
                try:
                    # Try clicking toggle button again to close
                    await toggle_button.click()
                    await self.wait_for_animations(page, 1000)

                    # Check if sidebar closed
                    final_state = await page.evaluate('''() => {
                        const sidebar = document.querySelector('.sidebar, #sidebar, .side-nav');
                        const body = document.body;
                        return {
                            sidebarDisplay: sidebar ? window.getComputedStyle(sidebar).display : 'none',
                            sidebarClass: sidebar ? sidebar.className : '',
                            bodyClass: body.className
                        };
                    }''')

                    # Take screenshot of closed state
                    await page.screenshot(path=f"{self.screenshots_dir}/mobile_03_sidebar_closed.png")

                    # Compare with initial state to see if it returned to original
                    closed_properly = (
                        final_state['sidebarClass'] == initial_state['sidebarClass'] or
                        final_state['bodyClass'] == initial_state['bodyClass']
                    )

                    await self.log_test_result(
                        "Sidebar closes properly",
                        closed_properly,
                        f"Sidebar returned to initial state: {closed_properly}"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Sidebar closes properly",
                        False,
                        f"Error testing sidebar close: {str(e)}"
                    )

                # Test 8: Mobile responsiveness check
                print("\n=== TEST 8: Mobile responsiveness verification ===")
                try:
                    responsive_check = await page.evaluate(f'''() => {{
                        const viewport = {self.mobile_viewport['width']};
                        const body = document.body;
                        const main = document.querySelector('main, .main-content, .content');

                        return {{
                            bodyWidth: body.scrollWidth,
                            viewportWidth: viewport,
                            hasHorizontalScroll: body.scrollWidth > viewport,
                            mainFontSize: main ? window.getComputedStyle(main).fontSize : 'not found',
                            bodyFontSize: window.getComputedStyle(body).fontSize
                        }};
                    }}''')

                    is_responsive = not responsive_check['hasHorizontalScroll']
                    font_size = float(responsive_check['bodyFontSize'].replace('px', ''))
                    is_readable = font_size >= 14

                    await self.log_test_result(
                        "Mobile responsive (no horizontal scroll)",
                        is_responsive,
                        f"Body width: {responsive_check['bodyWidth']}px, Viewport: {responsive_check['viewportWidth']}px"
                    )

                    await self.log_test_result(
                        "Text readable on mobile",
                        is_readable,
                        f"Font size: {font_size}px (minimum 14px recommended)"
                    )

                except Exception as e:
                    await self.log_test_result(
                        "Mobile responsiveness check",
                        False,
                        f"Error in responsiveness check: {str(e)}"
                    )

                # Final screenshot
                await page.screenshot(path=f"{self.screenshots_dir}/mobile_04_final_state.png")

            except Exception as e:
                print(f"Critical error during testing: {str(e)}")
                await page.screenshot(path=f"{self.screenshots_dir}/mobile_error_state.png")

            finally:
                await browser.close()

    def generate_detailed_report(self):
        """Generate detailed test report with actionable insights"""
        print("\n" + "="*90)
        print("COMPREHENSIVE MOBILE SIDEBAR FUNCTIONALITY REPORT")
        print("="*90)
        print(f"Test URL: {self.base_url}")
        print(f"Mobile Viewport: {self.mobile_viewport['width']}x{self.mobile_viewport['height']} (iPhone size)")
        print(f"Screenshots Location: {self.screenshots_dir}")

        passed_tests = 0
        total_tests = len(self.test_results)
        critical_failures = []
        warnings = []

        print("\nDETAILED TEST RESULTS:")
        print("-" * 90)

        for result in self.test_results:
            status_symbol = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_symbol} {result['test']}")
            print(f"   Status: {result['status']}")
            print(f"   Details: {result['details']}")

            if result["status"] == "PASSED":
                passed_tests += 1
            else:
                # Categorize failures
                if any(keyword in result['test'].lower() for keyword in ['toggle', 'sidebar opens', 'found']):
                    critical_failures.append(result['test'])
                else:
                    warnings.append(result['test'])
            print()

        # Summary and recommendations
        print("="*90)
        print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")

        if passed_tests == total_tests:
            print("🎉 EXCELLENT! All mobile sidebar functionality tests passed!")
            print("✨ Your mobile sidebar implementation is working perfectly.")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed")

            if critical_failures:
                print(f"\n🚨 CRITICAL ISSUES:")
                for failure in critical_failures:
                    print(f"   - {failure}")
                print("   → These issues prevent core sidebar functionality")

            if warnings:
                print(f"\n⚡ ENHANCEMENT OPPORTUNITIES:")
                for warning in warnings:
                    print(f"   - {warning}")
                print("   → These are nice-to-have features for better UX")

        print(f"\n📸 SCREENSHOTS CAPTURED:")
        print("   - mobile_01_initial.png: Initial mobile page view")
        print("   - mobile_02_sidebar_opened.png: Sidebar in open state")
        print("   - mobile_03_sidebar_closed.png: Sidebar after closing")
        print("   - mobile_04_final_state.png: Final test state")

        print("\n🔧 RECOMMENDATIONS:")
        if passed_tests >= total_tests * 0.75:
            print("   ✓ Mobile sidebar functionality is largely working")
            print("   ✓ Focus on fixing minor issues for optimal experience")
        else:
            print("   ⚠ Significant mobile sidebar issues detected")
            print("   → Review toggle button implementation")
            print("   → Check CSS media queries for mobile breakpoints")
            print("   → Verify JavaScript event handlers for touch devices")

        print("="*90)
        return passed_tests == total_tests

async def main():
    """Run the comprehensive mobile sidebar tests"""
    tester = ImprovedMobileSidebarTester()

    print("🧪 Starting comprehensive mobile sidebar functionality analysis...")
    print(f"🌐 Testing URL: {tester.base_url}")
    print(f"📱 Mobile viewport: {tester.mobile_viewport['width']}x{tester.mobile_viewport['height']} (iPhone)")

    try:
        await tester.test_mobile_sidebar_comprehensive()
        success = tester.generate_detailed_report()
        return success
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)