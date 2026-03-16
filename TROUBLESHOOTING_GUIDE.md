# Troubleshooting Guide & Common Issues

## Critical Reminders for Claude

### 1. ALWAYS VERIFY FIRST!
- **Problem**: Claiming changes work without testing
- **Solution**: Use Playwright to verify on live GitHub Pages site
- **Example**:
```python
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://sdspieg.github.io/rubase-workshop-fletcher-2603/...')
    # Verify changes are live
"
```

### 2. Iterate Until 100% Correct
- Don't stop at "good enough"
- If user says something isn't right, verify and fix immediately
- Keep working until exactly as requested

## GitHub Pages Issues

### .nojekyll File
- **Problem**: GitHub Pages doesn't serve directories starting with underscore (_)
- **Solution**: Add `.nojekyll` file to repository root
```bash
touch .nojekyll
git add .nojekyll
git commit -m "Add .nojekyll for GitHub Pages"
```

### 404 Errors After Push
- **Problem**: Files show 404 even after pushing to GitHub
- **Solution**:
  1. Wait 1-2 minutes for GitHub Pages to update
  2. Ensure `.nojekyll` file exists
  3. Check file paths are correct (case-sensitive!)

## File Handling Errors

### Glob Pattern Errors
- **Problem**: `ls *.html` fails with "cannot access 'glob': No such file or directory"
- **Solution**: Quote the pattern or use proper escaping
```bash
# Wrong
ls /path/*.html

# Right
ls /path/ | grep "\.html$"
# Or
find /path -name "*.html"
```

### Converting PowerPoint to Individual PNG Slides
- **Problem**: LibreOffice creates one combined image instead of individual slides
- **Solution**: Convert to PDF first, then use pdf2image
```python
# Step 1: Convert to PDF
soffice --headless --convert-to pdf --outdir /tmp "presentation.pptx"

# Step 2: Convert PDF to PNGs
from pdf2image import convert_from_path
images = convert_from_path('/tmp/presentation.pdf')
for i, image in enumerate(images, 1):
    image.save(f'slide-{i}.png', 'PNG')
```

## Project Structure

### Application Architecture
```
rubase-workshop-fletcher-2603/
├── index.html                 # Main landing page with module grid
├── modules/
│   ├── workshop-overview/     # Overview module
│   │   └── index.html        # Navigation hub with schedule cards
│   ├── build/                # Day 1 module
│   ├── collect/              # Day 2 module
│   │   └── openalex/        # OpenAlex presentations
│   └── analyze/              # Day 3 module
│       ├── index.html        # Module hub with sidebar + resources
│       └── *.html           # Individual presentations
└── Day3_Workshop_Package/     # Workshop materials and scripts
```

### Key UI Components

#### Module Schedule Cards (workshop-overview/index.html)
- Located in the center content area
- Each day has its own card with schedule details
- Cards link to respective module pages

#### Module Index Pages
- **Left Sidebar**: Navigation within module
- **Center Content**: Main content area
- **Right Resources Panel**: Related materials and links

#### Slide Presentations
- Full-screen slides with navigation
- Dark blue gradient backgrounds
- Cyan/green/yellow/orange color scheme
- Navigation: Previous/Next buttons + keyboard arrows

## CSS/Styling Issues

### Split-Pane Display Problem
- **Problem**: Slides showing side-by-side instead of individual
- **Solution**: Fix CSS display properties
```css
/* Wrong */
.slide { display: none; }
.slide.title-slide { display: flex; }  /* Overrides active state! */

/* Right */
.slide { display: none; }
.slide.active { display: block; }
.slide.title-slide.active { display: flex; }
```

### Dark Theme Not Applying
- **Problem**: Dark background not showing after push
- **Solution**:
  1. Clear browser cache
  2. Wait for GitHub Pages to update
  3. Verify CSS gradient syntax is correct

## Git Issues

### Large File Errors
- **Problem**: Files over 100MB can't be pushed to GitHub
- **Solution**:
  1. Remove large files from git
  2. Add to .gitignore
```bash
git rm --cached large_file.json
echo "large_file.json" >> .gitignore
```

### Permission Errors on Push
- **Problem**: "unable to unlink" warnings
- **Solution**: Usually harmless if push succeeds (check commit hash)

## Python/Library Issues

### EOF Error with input() in Scripts
- **Problem**: `EOFError: EOF when reading a line` when using `input()` in scripts run with timeout
- **Cause**: The `timeout` command closes stdin, so `input()` can't read user input
- **Solution**:
  1. Don't use `input()` in automated scripts
  2. Use a flag or environment variable to control browser visibility
  3. Or just let the script complete normally without waiting
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

### python-pptx Shape Iteration
- **Problem**: `for shape in slide.shapes[:3]` causes AttributeError
- **Solution**: Iterate directly without slicing
```python
# Wrong
for shape in slide.shapes[:3]:

# Right
for i, shape in enumerate(slide.shapes):
    if i >= 3: break
```

### Playwright Timeout Errors
- **Problem**: Element not found within timeout
- **Solution**:
  1. Check if page loaded correctly
  2. Verify selector is correct
  3. Add wait conditions
```python
page.wait_for_load_state('networkidle')
page.wait_for_selector('.slide', timeout=10000)
```

## Common Workflow Mistakes

### Not Using Project Root
- **Problem**: Running commands from wrong directory
- **Solution**: Always `cd` to project root first
```bash
cd /mnt/c/Users/Stephan/Dropbox/Presentations/2603\ -\ Boston_instructors/rubase-workshop-fletcher-2603
```

### Forgetting to Add Files to Git
- **Problem**: Changes not appearing on GitHub Pages
- **Solution**: Always check `git status` and add all needed files
```bash
git add -A  # Add all files
git status  # Verify what will be committed
```

### Not Checking File Paths
- **Problem**: Links broken due to incorrect paths
- **Solution**:
  1. Use relative paths in HTML
  2. Verify paths are case-sensitive
  3. Test locally before pushing

## Slide Presentation Guidelines

### Visual Consistency
- Dark blue gradient backgrounds (#0a192f → #1e3c72 → #2a5298)
- Bright accent colors:
  - Cyan (#00ffff) for primary highlights
  - Green (#00ff7f) for success/positive
  - Yellow (#ffff00) for attention
  - Orange (#ffa500) for warnings
- Glowing text shadows for neon effect
- 92% width, 88vh height for slides

### Semantic Emojis (Not Excited!)
- 📊 for data/statistics
- 🔬 for research
- 📅 for dates/timeline
- 🌍/🌎/🌏 for global/geographic
- 🎯 for goals/targets
- ⚠️ for warnings
- ✅ for completed/success
- 🚫 for limitations/cannot do

## Testing Commands

### Verify Slides Work
```bash
python verify_final.py     # Full verification
python verify_buttons.py   # Button verification
```

### Quick GitHub Pages Check
```python
# Check if a page is live
import requests
response = requests.get('https://sdspieg.github.io/rubase-workshop-fletcher-2603/page.html')
print(f"Status: {response.status_code}")
```

## Slide Presentation Issues

### Content Not Fitting on Screen
- **Problem**: Content overflows, requires scrolling, poor screen real estate usage
- **Solution**:
  1. Increase slide dimensions: `width: 95%`, `height: 92vh`
  2. Reduce padding: `padding: 35px 45px` instead of `50px 60px`
  3. Decrease font sizes:
     - h1: `2em` instead of `2.2em`
     - h2: `1.4em` instead of `1.6em`
     - p: `0.9em` instead of `0.95em`
     - li: `0.88em` with `line-height: 1.4`
  4. Tighten margins throughout
  5. Use grid with smaller gaps: `gap: 12px` instead of `15px`

### Title Slide Illegibility
- **Problem**: Title text hard to read on background
- **Solution**:
  1. Use high contrast colors
  2. Add text shadows: `text-shadow: 0 3px 6px rgba(0,0,0,0.5)`
  3. Ensure sufficient size: `font-size: 2.8em` for main title

### White Background in Dark Theme
- **Problem**: Slides have white background while body has dark gradient
- **Solution**: Match slide background to theme
```css
/* Wrong */
.slide {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

/* Right - Elegant Dark Blue */
.slide {
    background: linear-gradient(135deg, #1a2a4a 0%, #243655 100%);
    border: 1px solid rgba(100, 150, 200, 0.3);
}
```

### Screaming vs Elegant Colors
- **Problem**: Bright neon colors (#00ffff, #00ff7f) too harsh
- **Solution**: Use muted, elegant tones
  - Sky blue: #87ceeb (instead of cyan #00ffff)
  - Light blue: #7db8da (instead of green #00ff7f)
  - Soft gray-blue: #c0d4e0 (for body text)
  - Teal accents: #4a7c8c → #5a8c9c (for buttons)

### Missing Navigation Buttons
- **Problem**: Inconsistent navigation across presentations
- **Solution**: All presentations should have:
  - 🏠 Home button → `../../index.html`
  - 📚 Module/Resources button → `index.html`
  - ← Previous and Next → buttons

## Workshop Philosophy

### "Teaching to Fish" Approach
**Key Principle**: The workshop provides scripts and tools, BUT the main goal is teaching YOU how to use CLI tools independently.

**Example**: Ottoman Bank Case Study
- Instead of just providing data, we show HOW to:
  1. Query OpenAlex with specific terms
  2. Understand the importance of quotes in searches (21,388 vs 511 results)
  3. Build your own data collection pipelines
  4. Analyze and process results

**The Real Value**:
- Not the scripts themselves, but understanding how to modify them
- Not the specific data, but knowing how to get your own
- Not following instructions, but learning to give instructions to CLI tools

## LLM Interaction Methods

### Two Ways to Interact with LLMs
1. **Programmatically**: API calls, structured data processing, automated workflows
   - Use for: Bulk analysis, data pipeline integration, systematic processing
   - Example: OpenAlex API → JSON processing → LLM analysis via API

2. **As an LLM**: Direct text/image interaction, conversational analysis
   - Use for: Exploratory research, nuanced interpretation, visual analysis
   - Example: Upload screenshots, paste text excerpts, ask interpretive questions

### Verification Strategies
1. **Citation Verification**:
   - Cross-reference DOIs against original sources
   - Check author names and publication years
   - Verify abstracts match claimed content

2. **Webpage Verification (Playwright)**:
   ```python
   from playwright.sync_api import sync_playwright
   with sync_playwright() as p:
       browser = p.chromium.launch(headless=True)
       page = browser.new_page()
       page.goto('https://example.com')
       # Verify content, capture screenshots, test functionality
   ```

## Lessons Learned (For Us - Not Students)

### Color Contrast vs Luminance Contrast
- **Issue**: Colors can have good luminance contrast ratios but poor visual distinction
- **Example**: Sky blue (#87ceeb) on dark blue (#1a2a4a) = 8.18:1 ratio (passes WCAG) but still hard to read
- **Solution**: Use colors with different hues, not just different brightness levels
- **Better approach**: White/very light colors on dark backgrounds for maximum readability

### Dataset Confusion
- **Issue**: Using wrong dataset (21,000+ papers from unquoted search vs 511 from quoted)
- **Solution**: Always verify data sources and search parameters before analysis
- **Impact**: Completely different conclusions and statistics

### Verification Methodology
- **Not enough**: Just checking if changes were made
- **Required**: Visual verification of EVERY slide on live site
- **Tool**: Playwright scripts to systematically check each element

## Remember: The Three Golden Rules

1. **ALWAYS VERIFY** - Test on live site, not just local files
2. **ITERATE TO 100%** - Don't stop until exactly right
3. **CHECK GITHUB PAGES** - Wait for updates, ensure .nojekyll exists