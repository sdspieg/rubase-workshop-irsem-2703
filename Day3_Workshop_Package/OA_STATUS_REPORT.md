# Open Access Status Report: Ottoman Bank Dataset

## Executive Summary

**Outstanding Result: 98.9% of papers are Open Access!**

Out of 21,397 papers mentioning "Ottoman Bank" in full-text:
- **21,153 papers (98.9%) are Open Access**
- **21,148 papers have downloadable OA URLs**
- **Only 244 papers (1.1%) are closed access**

## Detailed Breakdown

### OA Status Types

| Status | Count | Percentage | Description |
|--------|-------|------------|-------------|
| Green | 7,500 | 35.1% | Repository/self-archived |
| Diamond | 5,143 | 24.0% | Free journal, no author fees |
| Gold | 3,199 | 15.0% | Publisher OA |
| Bronze | 2,996 | 14.0% | Free to read (no license) |
| Hybrid | 2,315 | 10.8% | OA option in subscription journal |
| Closed | 244 | 1.1% | No OA version available |

### Repository Coverage

- **12,038 papers (56.3%)** are available in repositories
- This includes institutional repositories, preprint servers, and subject repositories

### Temporal Trends

Recent years show near-universal OA availability:
- 2023: 99.3% OA (1,912 of 1,926 papers)
- 2024: 99.6% OA (1,757 of 1,764 papers)
- 2025: 99.4% OA (1,538 of 1,547 papers)

## Implications for Full-Text Analysis

### Current Situation
- We extracted **abstracts only** → 67,238 chunks
- Only **18 chunks (0.03%)** mention "Ottoman Bank" directly

### Opportunity for Enhancement
With 98.9% OA availability, we could:
1. **Download full-text PDFs** for 21,148 papers
2. **Extract full content** instead of just abstracts
3. **Find many more relevant passages** about Ottoman Bank

### Why This Matters
The full-text search found these papers because "Ottoman Bank" appears somewhere in:
- Main text
- Literature reviews
- Footnotes
- References
- Tables/figures

But these mentions rarely appear in abstracts, hence our 0.03% direct mention rate.

## Recommended Next Steps

### Option 1: Full-Text Extraction (Advanced)
```python
# Pseudocode for full-text pipeline
for paper in papers_with_oa_urls:
    pdf_url = paper['open_access']['oa_url']
    pdf_content = download_pdf(pdf_url)
    full_text = extract_text_from_pdf(pdf_content)
    chunks = create_chunks(full_text)
    # Now chunks will contain the actual Ottoman Bank mentions
```

### Option 2: Targeted PDF Analysis
Focus on papers most likely to have substantial Ottoman Bank content:
1. Papers with "Ottoman" in title (426 papers)
2. Papers from economic/history journals
3. Papers with multiple Ottoman-related keywords

### Option 3: Workshop Simplification
For the workshop, explain:
1. **Why abstracts miss content**: Full-text search ≠ abstract content
2. **OA opportunity**: 98.9% could be fully analyzed
3. **Cost-benefit**: Full-text extraction vs. abstract-only analysis

## Cost Considerations

### Abstract-Only (Current)
- 67,238 chunks from abstracts
- Cost: ~$27 for full classification
- Ottoman Bank mentions: 0.03%

### Full-Text (Potential)
- Estimated 500-1000 chunks per paper
- ~10-20 million total chunks
- Cost: $4,000-8,000 for full classification
- Ottoman Bank mentions: Likely 5-10%

### Hybrid Approach
1. Use tiered datasets for workshop
2. Demonstrate full-text extraction on subset
3. Show relevance filtering importance

## Technical Requirements for Full-Text

To implement full-text extraction:
```bash
pip install pypdf2 pdfplumber requests
```

Key challenges:
- PDF parsing complexity
- Rate limiting for downloads
- Storage requirements (~10GB for PDFs)
- Processing time (hours to days)

## Workshop Recommendation

Present this as a **success story with a lesson**:

1. **Success**: Amazing 98.9% OA rate enables full analysis
2. **Challenge**: Abstract-only extraction misses most content
3. **Lesson**: Always verify extraction matches search method
4. **Opportunity**: Full-text extraction possible but resource-intensive

This perfectly illustrates the importance of:
- Understanding your data pipeline
- Matching extraction to search methodology
- Considering cost-benefit tradeoffs
- Leveraging OA resources effectively