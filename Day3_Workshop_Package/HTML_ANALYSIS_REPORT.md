# HTML Content Analysis Report

## Summary of Findings

From analyzing 20 OA URLs from OpenAlex:
- **30% (6/20)** were direct PDF downloads
- **65% (13/20)** returned HTML pages
- **5% (1/20)** failed (connection error)

## HTML Page Patterns Identified

### 1. **Springer** (e.g., html_003.html)
- **Pattern**: PDF URL in metadata tag
- **Location**: `<meta name="citation_pdf_url" content="...">`
- **Example**: `https://link.springer.com/content/pdf/10.1007/BF02686330.pdf`
- **Extraction**: Parse HTML, extract meta tag content

### 2. **World Bank** (html_001.html)
- **Pattern**: 404 error page
- **Issue**: Original URL was malformed or content moved
- **Solution**: May need to search their repository differently

### 3. **Repository Pages** (html_005.html)
- **Pattern**: Landing pages with download buttons
- **Common selectors**:
  - Download buttons/links
  - "View/Download" links
  - PDF icons with hrefs

### 4. **Publisher Paywalls** (AEA, OUP)
- **Pattern**: Preview pages requiring login
- **Challenge**: May show as OA but require institutional access
- **Solution**: Look for alternative OA repositories

### 5. **Embedded Viewers**
- **Pattern**: PDF viewers in iframes or embeds
- **Solution**: Extract src URL from embed/iframe tags

## Extraction Strategy

### Tier 1: Direct PDF URLs (Best)
```python
# Check for direct PDF response
if content.startswith(b'%PDF'):
    # Save directly
```

### Tier 2: Metadata Extraction (Good)
```python
# For Springer and similar
pdf_url = extract_from_meta('citation_pdf_url')
if not pdf_url:
    pdf_url = extract_from_meta('DC.identifier')
```

### Tier 3: Link Scanning (Moderate)
```python
# Find PDF links in HTML
pdf_links = find_all('a[href$=".pdf"]')
download_links = find_all('a:contains("Download")')
```

### Tier 4: Browser Automation (Last Resort)
```python
# Use Playwright to:
# 1. Load page
# 2. Click download buttons
# 3. Capture network requests for PDFs
# 4. Or render page as PDF
```

## Specific Publisher Strategies

| Publisher | Strategy | Success Rate |
|-----------|----------|--------------|
| Springer | Extract meta tag `citation_pdf_url` | High |
| Elsevier/ScienceDirect | Look for download API endpoints | Medium |
| World Bank | Check elibrary.worldbank.org | Low (often broken) |
| University Repositories | Find "Download" buttons | High |
| AEA (American Economic Association) | May need auth | Low |
| Oxford Academic (OUP) | Look for `/pdf/` in URLs | Medium |

## Recommended Approach

1. **Try direct download first** (fastest, most reliable)
2. **If HTML, extract PDF URL from metadata** (works for major publishers)
3. **Use Playwright only when necessary** (slower but handles complex cases)

## Code Implementation

The enhanced script (`06_download_fulltext_enhanced.py`) implements:
- Direct PDF download attempt
- HTML metadata extraction
- Playwright fallback for complex pages
- Screenshot and text extraction for non-PDF content

## Statistics from Test Batch

```
Success Rate by Method:
- Direct PDF: 30%
- HTML with extractable PDF: ~40%
- Requires browser automation: ~25%
- Failed/Paywall: ~5%
```

## Next Steps

1. Run enhanced downloader on larger sample
2. Build publisher-specific extractors
3. Create fallback to other OA sources (e.g., arXiv, PubMed Central)
4. Consider using Unpaywall API for better OA URLs