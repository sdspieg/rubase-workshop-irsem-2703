# Critical Discovery: Ottoman Bank Dataset Analysis

## The Problem

We fetched 21,397 papers from OpenAlex using full-text search for "Ottoman Bank", but after chunking the abstracts, only 18 chunks (0.03%) actually contain the phrase "Ottoman Bank".

## Why This Happened

1. **Full-text vs Abstract Mismatch**: OpenAlex's full-text search finds papers that mention "Ottoman Bank" ANYWHERE in the paper (introduction, literature review, footnotes, references, etc.), not necessarily in the abstract.

2. **Abstract Extraction**: Our chunking script (`01_extract_chunks.py`) only extracts and chunks the abstracts, not the full paper text.

3. **Result**: We have a massive corpus where 99.97% of chunks don't actually mention the Ottoman Bank directly.

## Dataset Statistics

```
Total papers found: 21,397
Papers with abstracts: 18,516
Total chunks created: 67,238
Chunks mentioning "Ottoman Bank": 18 (0.03%)
Chunks mentioning "Ottoman": 2,762 (4.11%)
Chunks mentioning "Bank": 1,782 (2.65%)
Papers with "Ottoman" in title: 426
```

## Implications for the Workshop

### Option 1: Use As-Is (Challenging Classification Task)
- **Pro**: Realistic scenario - most chunks will be irrelevant
- **Pro**: Tests the relevance filtering capability
- **Con**: Very expensive - paying to classify 67,000+ mostly irrelevant chunks
- **Con**: Poor demonstration of taxonomy application

### Option 2: Pre-Filter for Relevance
Create a subset of chunks that are more likely to be relevant:
- Chunks from papers with "Ottoman" in the title (1,525 chunks)
- Chunks that mention "Ottoman" anywhere (2,762 chunks)
- Chunks that mention both "Ottoman" and "Bank" separately

### Option 3: Different Search Strategy
- Search for papers about "Ottoman Empire" + "banking" or "finance"
- Search for "Imperial Ottoman Bank" specifically
- Search for "Banque Impériale Ottomane"

### Option 4: Use Full-Text Data
- OpenAlex doesn't provide full-text content directly
- Would need to use a different data source or API

## Recommended Solution for Workshop

Create multiple dataset tiers for demonstration:

1. **Tier 1 - Highly Relevant** (18 chunks)
   - Chunks that explicitly mention "Ottoman Bank"
   - Use for initial taxonomy testing

2. **Tier 2 - Potentially Relevant** (~500 chunks)
   - Chunks mentioning "Ottoman" AND "bank" (separately)
   - Chunks from papers with Ottoman banking-related titles

3. **Tier 3 - Broader Context** (2,762 chunks)
   - All chunks mentioning "Ottoman"
   - Use to demonstrate relevance filtering

## Quick Fix Script

```python
# Create tiered datasets
import json

with open('ottoman_bank_chunks_ALL.json') as f:
    data = json.load(f)

chunks = data['chunks']

# Tier 1: Direct mentions
tier1 = [c for c in chunks if 'ottoman bank' in c.get('chunk_text', '').lower()]

# Tier 2: Ottoman + financial terms
financial_terms = ['bank', 'finance', 'credit', 'loan', 'debt', 'monetary', 'economic']
tier2 = [c for c in chunks
         if 'ottoman' in c.get('chunk_text', '').lower()
         and any(term in c.get('chunk_text', '').lower() for term in financial_terms)]

# Tier 3: All Ottoman mentions
tier3 = [c for c in chunks if 'ottoman' in c.get('chunk_text', '').lower()]

print(f"Tier 1 (Direct): {len(tier1)} chunks")
print(f"Tier 2 (Ottoman + Finance): {len(tier2)} chunks")
print(f"Tier 3 (Any Ottoman): {len(tier3)} chunks")

# Save tiered datasets
for tier, chunks, name in [
    (1, tier1, 'ottoman_bank_tier1_direct.json'),
    (2, tier2, 'ottoman_bank_tier2_finance.json'),
    (3, tier3, 'ottoman_bank_tier3_ottoman.json')
]:
    with open(name, 'w') as f:
        json.dump({
            'metadata': {
                'tier': tier,
                'total_chunks': len(chunks),
                'description': f'Tier {tier} Ottoman Bank dataset'
            },
            'chunks': chunks
        }, f, indent=2)
```

## Lessons Learned

1. **Always verify the data matches your extraction method** - full-text search ≠ abstract content
2. **Test with small samples first** - we could have caught this with 100 chunks
3. **Relevance filtering is critical** - especially with broad corpus searches
4. **Document the data pipeline clearly** - each step can filter differently

## For the Workshop

Explain this as a **realistic challenge** in working with large corpora:
- Full-text search casts a wide net
- Abstracts may not contain the specific terms
- Relevance filtering becomes essential
- Tiered approaches help manage costs