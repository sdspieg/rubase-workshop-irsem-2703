#!/usr/bin/env python3
"""
Contrast analysis report for Fletcher workshop archive banner
"""

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

# Data collected from browser analysis
accent_yellow = "#ffd700"  # --accent-yellow CSS variable
primary_bg = "#0a0e27"     # --primary-bg CSS variable (text color)

print("=== FLETCHER WORKSHOP ARCHIVE BANNER CONTRAST ANALYSIS ===")
print()

print("Banner Details:")
print("- Text: '⚠️ This is an archived workshop from March 2026 - Fletcher School'")
print("- Link: '→ View Latest Version' (href: https://sdspieg.github.io/rubase-workshop/)")
print("- Background: Linear gradient from --accent-yellow to --accent-orange")
print("- Text Color: --primary-bg (dark blue)")
print()

print("Colors Found:")
print(f"- Background (gradient start): {accent_yellow} (Gold/Yellow)")
print(f"- Text Color: {primary_bg} (Dark Blue)")
print(f"- Link Color: {primary_bg} (Same as text, with underline)")
print()

# Calculate contrast ratio
yellow_rgb = hex_to_rgb(accent_yellow)
dark_bg_rgb = hex_to_rgb(primary_bg)

ratio = contrast_ratio(yellow_rgb, dark_bg_rgb)

print("Contrast Analysis:")
print(f"- Background RGB: {yellow_rgb}")
print(f"- Text RGB: {dark_bg_rgb}")
print(f"- Contrast Ratio: {ratio:.2f}:1")
print()

print("WCAG Compliance:")
print(f"- WCAG AA (Normal Text 4.5:1): {'✅ PASS' if ratio >= 4.5 else '❌ FAIL'}")
print(f"- WCAG AA (Large Text 3:1): {'✅ PASS' if ratio >= 3.0 else '❌ FAIL'}")
print(f"- WCAG AAA (Normal Text 7:1): {'✅ PASS' if ratio >= 7.0 else '❌ FAIL'}")
print(f"- WCAG AAA (Large Text 4.5:1): {'✅ PASS' if ratio >= 4.5 else '❌ FAIL'}")
print()

print("Assessment:")
if ratio >= 7.0:
    print("🟢 EXCELLENT: Text contrast exceeds all WCAG requirements")
elif ratio >= 4.5:
    print("🟡 GOOD: Text contrast meets WCAG AA requirements but not AAA")
elif ratio >= 3.0:
    print("🟠 MARGINAL: Only suitable for large text under WCAG AA")
else:
    print("🔴 POOR: Text contrast fails WCAG requirements")

print()
print("Readability Assessment:")
print("- The dark blue text on yellow/gold background provides strong contrast")
print("- Warning emoji (⚠️) is clearly visible")
print("- Link text with underline is distinguishable from main text")
print("- Banner is sticky-positioned at top for visibility")
print("- Bold font weight enhances readability")
print()

print("Potential Issues:")
if ratio < 4.5:
    print("- ❌ Contrast ratio below WCAG AA minimum")
    print("- ❌ May be difficult to read for users with vision impairments")
else:
    print("- ✅ No significant contrast issues detected")
    print("- ✅ Text should be easily readable by all users")

print()
print("Technical Details:")
print(f"- Banner uses CSS variables for consistent theming")
print(f"- Gradient background may vary in contrast across the banner width")
print(f"- Font: System font stack with 700 weight (bold)")
print(f"- Font size: 16px (standard readable size)")
print(f"- Banner dimensions: ~1265x39 pixels")