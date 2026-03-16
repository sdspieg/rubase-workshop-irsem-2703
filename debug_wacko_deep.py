#!/usr/bin/env python3
"""
Deep debugging of WACKO presentation - test all functionality
"""

from playwright.sync_api import sync_playwright
import time

def deep_debug_wacko():
    """Comprehensive WACKO debugging."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for debugging
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        print("🔍 Loading WACKO presentation...")
        page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/modules/analyze/wacko-presentation.html")

        # Wait longer for full load
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Check console errors
        print("\n📋 Console messages:")
        page.on("console", lambda msg: print(f"   CONSOLE: {msg.type}: {msg.text}"))

        # Check network failures
        print("\n🌐 Network issues:")
        page.on("requestfailed", lambda req: print(f"   FAILED: {req.url} - {req.failure}"))

        # Check current state
        state = page.evaluate("""
            () => {
                return {
                    title: document.title,
                    slidesCount: document.querySelectorAll('.slide').length,
                    activeSlides: document.querySelectorAll('.slide.active').length,
                    currentSlide: window.currentSlide || 'undefined',
                    totalSlides: window.totalSlides || 'undefined',
                    imagesLoaded: Array.from(document.querySelectorAll('img')).map(img => ({
                        src: img.src,
                        complete: img.complete,
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight
                    })),
                    buttonsPresent: {
                        prev: !!document.getElementById('prevBtn'),
                        next: !!document.getElementById('nextBtn')
                    },
                    cssLoaded: !!document.querySelector('link[href="slides.css"]'),
                    bodyClass: document.body.className,
                    containerPresent: !!document.querySelector('.presentation-container')
                };
            }
        """)

        print(f"\n📊 Page State:")
        print(f"   Title: {state['title']}")
        print(f"   Slides: {state['slidesCount']} total, {state['activeSlides']} active")
        print(f"   Current/Total: {state['currentSlide']}/{state['totalSlides']}")
        print(f"   CSS Loaded: {state['cssLoaded']}")
        print(f"   Container: {state['containerPresent']}")
        print(f"   Buttons: Prev={state['buttonsPresent']['prev']}, Next={state['buttonsPresent']['next']}")

        print(f"\n🖼️ Images Status:")
        for i, img in enumerate(state['imagesLoaded']):
            status = "✅ LOADED" if img['complete'] and img['naturalWidth'] > 0 else "❌ FAILED"
            print(f"   Image {i+1}: {status} - {img['src']}")

        # Take screenshot of current state
        page.screenshot(path='wacko-debug-full.png')
        print(f"\n📸 Screenshot saved: wacko-debug-full.png")

        # Test navigation
        print(f"\n🔄 Testing Navigation:")

        # Try clicking next button
        try:
            next_btn = page.locator('#nextBtn')
            if next_btn.is_visible():
                print("   Clicking Next button...")
                next_btn.click()
                time.sleep(1)

                new_state = page.evaluate("() => window.currentSlide || 'undefined'")
                print(f"   After next click: currentSlide = {new_state}")

                page.screenshot(path='wacko-after-next.png')
                print("   Screenshot after next: wacko-after-next.png")
            else:
                print("   ❌ Next button not visible")
        except Exception as e:
            print(f"   ❌ Next button error: {e}")

        # Try keyboard navigation
        try:
            print("   Testing arrow key navigation...")
            page.keyboard.press('ArrowRight')
            time.sleep(1)

            arrow_state = page.evaluate("() => window.currentSlide || 'undefined'")
            print(f"   After arrow right: currentSlide = {arrow_state}")
        except Exception as e:
            print(f"   ❌ Keyboard navigation error: {e}")

        # Check slide content
        slide_content = page.evaluate("""
            () => {
                const activeSlide = document.querySelector('.slide.active');
                if (!activeSlide) return 'No active slide';

                const img = activeSlide.querySelector('img');
                return {
                    hasImage: !!img,
                    imageSrc: img ? img.src : 'none',
                    slideNumber: activeSlide.querySelector('.slide-number')?.textContent || 'none',
                    loadingVisible: activeSlide.classList.contains('loading')
                };
            }
        """)

        print(f"\n🎯 Active Slide Content:")
        print(f"   Has Image: {slide_content.get('hasImage', False)}")
        print(f"   Image Src: {slide_content.get('imageSrc', 'none')}")
        print(f"   Slide Number: {slide_content.get('slideNumber', 'none')}")
        print(f"   Still Loading: {slide_content.get('loadingVisible', False)}")

        browser.close()

    print(f"\n🎯 WACKO Deep Debug Complete!")

if __name__ == "__main__":
    deep_debug_wacko()