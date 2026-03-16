# Technical Issues & Solutions

## Issues Encountered and Resolved

### 1. Dataset Confusion - Ottoman Bank Papers
**Issue**: Using wrong dataset with 21,388 papers instead of correct 511
**Root Cause**: Used unquoted search "Ottoman Bank" vs quoted "Ottoman Bank"
**Solution**:
- Always use quoted searches for exact phrases
- Verify data counts before analysis
- Final correct dataset: 596 papers (511 Ottoman + 85 unique Galata)

### 2. Color Contrast on Dark Backgrounds
**Issue**: Text illegible with dark colors on dark blue backgrounds
**Examples**:
- List items: rgb(52, 73, 94) on #1a2a4a
- Table cells: rgb(0, 0, 0) on dark blue
- Paragraphs: #333, #444, #555 on gradient backgrounds

**Solution**:
```css
/* All text should be white or cyan on dark backgrounds */
p, li { color: #ffffff; opacity: 0.95; }
td { color: #ffffff; }
h2 { color: #00ffff; }
```

### 3. EOF Error with input() in Scripts
**Issue**: `EOFError: EOF when reading a line` when using input() with timeout
**Cause**: The timeout command closes stdin
**Solution**:
```python
# Wrong
input("Press Enter to close browser...")

# Right - for debugging
import os
if os.environ.get('DEBUG'):
    input("Press Enter to close browser...")
else:
    browser.close()
```

### 4. PowerPoint to PNG Conversion
**Issue**: LibreOffice creates one combined image instead of individual slides
**Solution**: Convert to PDF first, then use pdf2image
```python
# Step 1: Convert to PDF
soffice --headless --convert-to pdf --outdir /tmp "presentation.pptx"

# Step 2: Convert PDF to PNGs
from pdf2image import convert_from_path
images = convert_from_path('/tmp/presentation.pdf')
for i, image in enumerate(images, 1):
    image.save(f'slide-{i}.png', 'PNG')
```

### 5. GitHub Pages 404 Errors
**Issue**: Files show 404 even after pushing to GitHub
**Solutions**:
1. Wait 1-2 minutes for GitHub Pages to update
2. Ensure `.nojekyll` file exists in root
3. Check file paths are correct (case-sensitive!)

### 6. Glob Pattern Errors in Bash
**Issue**: `ls *.html` fails with "cannot access 'glob': No such file or directory"
**Solution**:
```bash
# Wrong
ls /path/*.html

# Right
ls /path/ | grep "\.html$"
# Or
find /path -name "*.html"
```

### 7. Split-Pane Display Problem
**Issue**: Slides showing side-by-side instead of individual
**Solution**: Fix CSS display properties
```css
/* Wrong */
.slide { display: none; }
.slide.title-slide { display: flex; }  /* Overrides active state! */

/* Right */
.slide { display: none; }
.slide.active { display: block; }
.slide.title-slide.active { display: flex; }
```

### 8. python-pptx Shape Iteration
**Issue**: `for shape in slide.shapes[:3]` causes AttributeError
**Solution**: Iterate directly without slicing
```python
# Wrong
for shape in slide.shapes[:3]:

# Right
for i, shape in enumerate(slide.shapes):
    if i >= 3: break
```

### 9. Screen Real Estate Issues
**Issue**: Content overflows, requires scrolling, poor space usage
**Solution**:
- Increase slide dimensions: `width: 95%`, `height: 92vh`
- Reduce padding: `padding: 35px 45px`
- Decrease font sizes appropriately
- Tighten margins throughout

### 10. Color Contrast vs Luminance Contrast
**Issue**: Colors can have good luminance ratios but poor visual distinction
**Example**: Sky blue (#87ceeb) on dark blue (#1a2a4a) = 8.18:1 ratio but hard to read
**Solution**: Use colors with different hues, white/cyan on dark backgrounds

## Voice Input for CLI Tools

### How to "Send Voice Messages" from a Computer
**Issue**: Documentation says "just send voice messages" but doesn't explain HOW
**Solution**: Use your OS's built-in voice-to-text features

#### Platform-Specific Methods:
1. **macOS**:
   - Press Fn key twice to activate dictation
   - Speak naturally
   - Text appears in terminal
   - Press Enter to send to CLI

2. **Windows**:
   - Press Win+H for voice typing
   - Dictate your command
   - Windows converts speech to text
   - Send to CLI tool

3. **Linux**:
   - Install tools like `nerd-dictation` or `whisper.cpp`
   - Configure hotkeys for voice input
   - Or use browser-based speech-to-text

4. **Universal Alternative**:
   - Use phone's voice-to-text in any app
   - Copy the transcribed text
   - Paste into terminal

**Important**: This is voice-to-text conversion, not actual audio. The CLI tools receive text input that was generated from your voice.

## Testing & Verification Commands

### Verify Slides Work
```bash
python verify_final.py     # Full verification
python verify_buttons.py   # Button verification
```

### Quick GitHub Pages Check
```python
import requests
response = requests.get('https://sdspieg.github.io/rubase-workshop-fletcher-2603/page.html')
print(f"Status: {response.status_code}")
```

### Playwright Verification
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com')
    # Verify content, capture screenshots, test functionality
```