#!/usr/bin/env python3
"""
Playwright script to check text contrast on the Fletcher workshop archive banner.
This script will navigate to the site, take screenshots, and analyze colors.
"""

import asyncio
import colorsys
import math
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
import json

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_relative_luminance(r, g, b):
    """Calculate relative luminance for a color."""
    def gamma_correct(c):
        c = c / 255.0
        if c <= 0.03928:
            return c / 12.92
        else:
            return math.pow((c + 0.055) / 1.055, 2.4)

    r_gamma = gamma_correct(r)
    g_gamma = gamma_correct(g)
    b_gamma = gamma_correct(b)

    return 0.2126 * r_gamma + 0.7152 * g_gamma + 0.0722 * b_gamma

def calculate_contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors."""
    if isinstance(color1, str):
        color1 = hex_to_rgb(color1)
    if isinstance(color2, str):
        color2 = hex_to_rgb(color2)

    lum1 = rgb_to_relative_luminance(*color1)
    lum2 = rgb_to_relative_luminance(*color2)

    # Ensure lighter color is in numerator
    if lum1 < lum2:
        lum1, lum2 = lum2, lum1

    return (lum1 + 0.05) / (lum2 + 0.05)

def meets_wcag_aa(contrast_ratio, large_text=False):
    """Check if contrast ratio meets WCAG AA standards."""
    threshold = 3.0 if large_text else 4.5
    return contrast_ratio >= threshold

def meets_wcag_aaa(contrast_ratio, large_text=False):
    """Check if contrast ratio meets WCAG AAA standards."""
    threshold = 4.5 if large_text else 7.0
    return contrast_ratio >= threshold

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Set viewport for consistent screenshots
        await page.set_viewport_size({"width": 1280, "height": 720})

        print("Navigating to Fletcher workshop site...")
        await page.goto("https://sdspieg.github.io/rubase-workshop-fletcher-2603/")

        # Wait for page to load
        await page.wait_for_load_state("networkidle")

        # Take full page screenshot first
        print("Taking full page screenshot...")
        await page.screenshot(path="/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/full_page.png")

        # Look for the archive banner - first try finding by style attributes
        banner_element = await page.query_selector('div[style*="linear-gradient"][style*="accent-yellow"]')

        if not banner_element:
            # Try finding by text content
            banner_element = await page.query_selector('text="⚠️ This is an archived workshop"')
            if not banner_element:
                banner_element = await page.query_selector('text="This is an archived workshop"')

        if not banner_element:
            # Try other selectors
            banner_selectors = [
                'div:has-text("archived workshop")',
                'div:has-text("This is an archived")',
                '[style*="sticky"]',
                '[style*="z-index: 1002"]'
            ]

            for selector in banner_selectors:
                try:
                    banner_element = await page.query_selector(selector)
                    if banner_element:
                        print(f"Found banner with selector: {selector}")
                        break
                except:
                    continue

        if not banner_element:
            print("Looking for banner by traversing all divs...")
            # Get all divs and find the one with archive text
            all_divs = await page.query_selector_all('div')
            for div in all_divs:
                try:
                    text = await div.text_content()
                    if text and "archived workshop" in text.lower():
                        banner_element = div
                        print(f"Found banner by text content: {text[:100]}...")
                        break
                except:
                    continue

        if banner_element:
            print("Found archive banner, analyzing...")

            # Take screenshot of just the banner
            await banner_element.screenshot(path="/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/banner.png")

            # Get computed styles for the banner and its parent
            banner_styles = await page.evaluate("""
                (element) => {
                    const styles = window.getComputedStyle(element);
                    const parentStyles = element.parentElement ? window.getComputedStyle(element.parentElement) : null;
                    const bodyStyles = window.getComputedStyle(document.body);

                    return {
                        backgroundColor: styles.backgroundColor,
                        color: styles.color,
                        fontSize: styles.fontSize,
                        fontWeight: styles.fontWeight,
                        padding: styles.padding,
                        margin: styles.margin,
                        parentBackgroundColor: parentStyles ? parentStyles.backgroundColor : null,
                        bodyBackgroundColor: bodyStyles.backgroundColor,
                        tagName: element.tagName,
                        className: element.className,
                        textContent: element.textContent?.substring(0, 100)
                    };
                }
            """, banner_element)

            print("Banner styles:", json.dumps(banner_styles, indent=2))

            # Look for link elements within the banner
            link_element = await banner_element.query_selector('a')
            link_styles = None
            if link_element:
                link_styles = await page.evaluate("""
                    (element) => {
                        const styles = window.getComputedStyle(element);
                        return {
                            color: styles.color,
                            backgroundColor: styles.backgroundColor,
                            textDecoration: styles.textDecoration
                        };
                    }
                """, link_element)
                print("Link styles:", json.dumps(link_styles, indent=2))

            # Get banner bounding box for more detailed analysis
            bbox = await banner_element.bounding_box()
            if bbox:
                print(f"Banner dimensions: {bbox['width']}x{bbox['height']}")
        else:
            print("Could not find archive banner. Taking screenshot of top of page...")
            # Take screenshot of top portion of page
            await page.evaluate("window.scrollTo(0, 0)")
            await page.screenshot(path="/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/top_section.png", clip={"x": 0, "y": 0, "width": 1280, "height": 200})

        # Get page HTML to analyze structure
        html_content = await page.content()

        # Save HTML for analysis
        with open("/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/page_source.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        await browser.close()

        # Analyze colors if we found the banner
        if banner_element and banner_styles:
            print("\n=== COLOR ANALYSIS ===")
            bg_color = banner_styles['backgroundColor']
            text_color = banner_styles['color']

            print(f"Background color: {bg_color}")
            print(f"Text color: {text_color}")

            # Convert RGB/RGBA colors for analysis
            def parse_color(color_str):
                if not color_str:
                    return None
                if color_str.startswith('rgba'):
                    # Parse rgba(r, g, b, a) format
                    values = color_str.replace('rgba(', '').replace(')', '').split(',')
                    r, g, b, a = [float(x.strip()) for x in values]
                    # If alpha is 0, this is transparent
                    if a == 0:
                        return None  # Transparent
                    return (int(r), int(g), int(b))
                elif color_str.startswith('rgb'):
                    # Parse rgb(r, g, b) format
                    values = color_str.replace('rgb(', '').replace(')', '').split(',')
                    return tuple(int(x.strip()) for x in values)
                else:
                    return (255, 255, 255)  # Default white

            # Determine actual background color
            bg_rgb = parse_color(bg_color)
            if bg_rgb is None:
                # Element is transparent, check parent
                bg_rgb = parse_color(banner_styles.get('parentBackgroundColor'))
                if bg_rgb is None:
                    # Parent is also transparent, check body
                    bg_rgb = parse_color(banner_styles.get('bodyBackgroundColor'))
                    if bg_rgb is None:
                        # Default to white
                        bg_rgb = (255, 255, 255)
                        print("Using default white background (all elements transparent)")
                    else:
                        print("Using body background color")
                else:
                    print("Using parent element background color")
            else:
                print("Using banner element background color")

            text_rgb = parse_color(text_color)

            print(f"Background RGB: {bg_rgb}")
            print(f"Text RGB: {text_rgb}")

            # Calculate contrast ratio
            contrast_ratio = calculate_contrast_ratio(bg_rgb, text_rgb)
            print(f"\nContrast ratio: {contrast_ratio:.2f}:1")

            # Check WCAG compliance
            wcag_aa = meets_wcag_aa(contrast_ratio)
            wcag_aaa = meets_wcag_aaa(contrast_ratio)

            print(f"WCAG AA compliant: {wcag_aa} (requires 4.5:1)")
            print(f"WCAG AAA compliant: {wcag_aaa} (requires 7:1)")

            if link_styles:
                print("\n=== LINK COLOR ANALYSIS ===")
                link_color = link_styles['color']
                print(f"Link color: {link_color}")

                link_rgb = parse_color(link_color)
                link_contrast = calculate_contrast_ratio(bg_rgb, link_rgb)
                print(f"Link RGB: {link_rgb}")
                print(f"Link contrast ratio: {link_contrast:.2f}:1")
                print(f"Link WCAG AA compliant: {meets_wcag_aa(link_contrast)}")
                print(f"Link WCAG AAA compliant: {meets_wcag_aaa(link_contrast)}")

if __name__ == "__main__":
    asyncio.run(main())