#!/usr/bin/env python3
"""
Debug WACKO presentation by taking a screenshot and checking functionality
"""

from playwright.sync_api import sync_playwright
import time

def debug_wacko():
    """Debug the WACKO presentation."""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        print("🔍 Loading WACKO presentation...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/wacko-presentation.html")
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Take initial screenshot
        page.screenshot(path='wacko-debug.png')
        print("📸 WACKO screenshot saved as wacko-debug.png")

        # Check for error messages
        errors = page.evaluate("""
            () => {
                const errors = [];
                // Check for failed image loads
                const images = document.querySelectorAll('img');
                images.forEach((img, index) => {
                    if (!img.complete || img.naturalWidth === 0) {
                        errors.push(`Image ${index + 1} failed to load: ${img.src}`);
                    }
                });
                return errors;
            }
        """)

        if errors:
            print("❌ Found errors:")
            for error in errors:
                print(f"   {error}")
        else:
            print("✅ No image loading errors found")

        # Check if slides are present and visible
        slide_info = page.evaluate("""
            () => {
                const slides = document.querySelectorAll('.slide');
                const activeSlides = document.querySelectorAll('.slide.active');
                const images = document.querySelectorAll('img');

                return {
                    totalSlides: slides.length,
                    activeSlides: activeSlides.length,
                    totalImages: images.length,
                    firstImageSrc: images.length > 0 ? images[0].src : 'none'
                };
            }
        """)

        print(f"📊 Slide info: {slide_info}")

        # Test navigation
        print("🔄 Testing navigation...")
        next_btn = page.locator('#nextBtn')
        if next_btn.is_visible():
            next_btn.click()
            time.sleep(1)
            page.screenshot(path='wacko-slide2.png')
            print("📸 Slide 2 screenshot saved")
        else:
            print("❌ Next button not found")

        browser.close()

    print("\n🎯 WACKO debugging complete!")

if __name__ == "__main__":
    debug_wacko()