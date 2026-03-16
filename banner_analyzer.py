#!/usr/bin/env python3
"""
Simple banner color analyzer for the Fletcher workshop archive banner.
"""

import asyncio
from playwright.async_api import async_playwright

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

        # Take a screenshot focused on the banner area
        await page.screenshot(path="/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-generic/banner_focused.png",
                            clip={"x": 0, "y": 0, "width": 1280, "height": 60})

        # Get all the CSS variables and computed values
        banner_analysis = await page.evaluate("""
            () => {
                // Find the banner element with inline styles
                const banners = Array.from(document.querySelectorAll('div')).filter(div => {
                    const style = div.getAttribute('style') || '';
                    const text = div.textContent || '';
                    return style.includes('linear-gradient') && text.includes('archived workshop');
                });

                if (banners.length === 0) {
                    return { error: 'Banner not found' };
                }

                const banner = banners[0];
                const computedStyle = window.getComputedStyle(banner);

                // Get CSS variables from root
                const root = document.documentElement;
                const rootStyle = window.getComputedStyle(root);

                // Try to get the actual rendered colors
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = banner.offsetWidth;
                canvas.height = banner.offsetHeight;

                return {
                    element: {
                        tagName: banner.tagName,
                        innerHTML: banner.innerHTML.substring(0, 200),
                        style: banner.getAttribute('style'),
                        textContent: banner.textContent.trim()
                    },
                    computed: {
                        backgroundColor: computedStyle.backgroundColor,
                        background: computedStyle.background,
                        backgroundImage: computedStyle.backgroundImage,
                        color: computedStyle.color,
                        fontSize: computedStyle.fontSize,
                        fontWeight: computedStyle.fontWeight
                    },
                    cssVariables: {
                        primaryBg: rootStyle.getPropertyValue('--primary-bg').trim(),
                        accentYellow: rootStyle.getPropertyValue('--accent-yellow').trim(),
                        accentOrange: rootStyle.getPropertyValue('--accent-orange').trim(),
                        textPrimary: rootStyle.getPropertyValue('--text-primary').trim()
                    },
                    dimensions: {
                        width: banner.offsetWidth,
                        height: banner.offsetHeight,
                        top: banner.offsetTop,
                        left: banner.offsetLeft
                    }
                };
            }
        """)

        print("=== BANNER ANALYSIS ===")
        print(f"Banner element found: {banner_analysis.get('element', {}).get('tagName', 'Not found')}")
        if 'element' in banner_analysis:
            print(f"Text content: {banner_analysis['element']['textContent']}")
            print(f"Inline style: {banner_analysis['element']['style']}")
            print(f"Dimensions: {banner_analysis['dimensions']['width']}x{banner_analysis['dimensions']['height']}")

            print(f"\n=== CSS VARIABLES ===")
            css_vars = banner_analysis['cssVariables']
            print(f"--primary-bg: {css_vars['primaryBg']}")
            print(f"--accent-yellow: {css_vars['accentYellow']}")
            print(f"--accent-orange: {css_vars['accentOrange']}")
            print(f"--text-primary: {css_vars['textPrimary']}")

            print(f"\n=== COMPUTED STYLES ===")
            computed = banner_analysis['computed']
            print(f"Background: {computed['background']}")
            print(f"Background Image: {computed['backgroundImage']}")
            print(f"Background Color: {computed['backgroundColor']}")
            print(f"Text Color: {computed['color']}")
            print(f"Font Size: {computed['fontSize']}")
            print(f"Font Weight: {computed['fontWeight']}")

        # Now analyze the link within the banner
        link_analysis = await page.evaluate("""
            () => {
                const banners = Array.from(document.querySelectorAll('div')).filter(div => {
                    const style = div.getAttribute('style') || '';
                    const text = div.textContent || '';
                    return style.includes('linear-gradient') && text.includes('archived workshop');
                });

                if (banners.length === 0) {
                    return { error: 'Banner not found' };
                }

                const banner = banners[0];
                const link = banner.querySelector('a');

                if (!link) {
                    return { error: 'Link not found in banner' };
                }

                const linkStyle = window.getComputedStyle(link);

                return {
                    element: {
                        href: link.href,
                        textContent: link.textContent.trim(),
                        style: link.getAttribute('style')
                    },
                    computed: {
                        color: linkStyle.color,
                        backgroundColor: linkStyle.backgroundColor,
                        textDecoration: linkStyle.textDecoration
                    }
                };
            }
        """)

        if 'element' in link_analysis:
            print(f"\n=== LINK ANALYSIS ===")
            print(f"Link text: '{link_analysis['element']['textContent']}'")
            print(f"Link href: {link_analysis['element']['href']}")
            print(f"Inline style: {link_analysis['element']['style']}")
            print(f"Computed color: {link_analysis['computed']['color']}")
            print(f"Text decoration: {link_analysis['computed']['textDecoration']}")

        await browser.close()

        # Based on the HTML analysis, calculate actual contrast
        print(f"\n=== CONTRAST CALCULATION ===")

        # From the CSS variables we found:
        primary_bg = css_vars.get('primaryBg', '#0a0e27')  # Dark blue background
        accent_yellow = css_vars.get('accentYellow', '#ffd700')  # Gold/yellow

        # The banner uses a linear gradient from yellow to orange
        # For contrast calculation, we'll use the lighter color (yellow) as worst case
        print(f"Banner background uses gradient from {accent_yellow} (--accent-yellow)")
        print(f"Text color appears to be {primary_bg} (--primary-bg)")

        # Calculate contrast ratio
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_luminance(r, g, b):
            def gamma_correct(c):
                c = c / 255.0
                if c <= 0.03928:
                    return c / 12.92
                else:
                    return ((c + 0.055) / 1.055) ** 2.4

            r_gamma = gamma_correct(r)
            g_gamma = gamma_correct(g)
            b_gamma = gamma_correct(b)

            return 0.2126 * r_gamma + 0.7152 * g_gamma + 0.0722 * b_gamma

        def contrast_ratio(rgb1, rgb2):
            lum1 = rgb_to_luminance(*rgb1)
            lum2 = rgb_to_luminance(*rgb2)

            if lum1 < lum2:
                lum1, lum2 = lum2, lum1

            return (lum1 + 0.05) / (lum2 + 0.05)

        # Calculate actual contrast
        yellow_rgb = hex_to_rgb(accent_yellow)
        dark_bg_rgb = hex_to_rgb(primary_bg)

        ratio = contrast_ratio(yellow_rgb, dark_bg_rgb)

        print(f"Yellow background RGB: {yellow_rgb}")
        print(f"Dark text RGB: {dark_bg_rgb}")
        print(f"Contrast ratio: {ratio:.2f}:1")
        print(f"WCAG AA compliance (4.5:1): {'✅ PASS' if ratio >= 4.5 else '❌ FAIL'}")
        print(f"WCAG AAA compliance (7:1): {'✅ PASS' if ratio >= 7.0 else '❌ FAIL'}")

if __name__ == "__main__":
    asyncio.run(main())