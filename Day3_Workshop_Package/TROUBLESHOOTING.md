# Troubleshooting Guide for Day 3 Workshop Scripts

## Common Problems and Solutions

### 1. Script Errors

#### Problem: `SyntaxError: name 'CHUNK_SIZE' is used prior to global declaration`
**Cause:** Trying to declare variables as global after they've been referenced
**Solution:** Fixed in latest version - parameters are passed properly through functions

#### Problem: `ZeroDivisionError: division by zero`
**Cause:** No papers were processed (usually because abstracts weren't found)
**Solution:** Script now checks if papers_processed > 0 before division

#### Problem: No abstracts found from OpenAlex
**Cause:** OpenAlex uses `abstract_inverted_index` instead of `abstract` field
**Solution:** Script now handles inverted index format:
```python
# The script automatically reconstructs abstracts from inverted index
if 'abstract_inverted_index' in paper:
    # Converts position-word mapping back to text
```

### 2. API Search Issues

#### Problem: Not getting expected results from OpenAlex
**Cause:** Using wrong search endpoint
**Solutions:**

| Search Type | API Endpoint | What it Searches |
|------------|--------------|------------------|
| Basic Search | `search=query` | Titles and abstracts only |
| Full-Text Search | `filter=fulltext.search:query` | Entire paper content |
| Title Only | `filter=title.search:query` | Just paper titles |

**Correct usage:**
```bash
# Full-text search (what you usually want)
python fetch_openalex.py "Ottoman Bank" --type fulltext

# Title search only
python fetch_openalex.py "Ottoman Bank" --type title

# Basic search (titles + abstracts)
python fetch_openalex.py "Ottoman Bank" --type basic
```

### 3. Pagination Limits

#### Problem: Can only get 10,000 results with standard pagination
**Cause:** OpenAlex limits page parameter to 50 (50 × 200 = 10,000 max)
**Solution:** Use cursor-based pagination (implemented in fetch_openalex.py)

```python
# Cursor pagination can fetch ALL results
cursor = '*'  # Start cursor
while data['meta'].get('next_cursor'):
    cursor = data['meta']['next_cursor']
    # Fetch next page with cursor
```

### 4. Large Dataset Issues

#### Problem: Script times out or crashes with large datasets
**Solutions:**
1. Use the robust fetcher: `python fetch_openalex.py`
2. Set max results limit: `python fetch_openalex.py "query" --max 1000`
3. Process in batches if needed

#### Problem: Memory issues with 20,000+ papers
**Solutions:**
1. Process chunks incrementally rather than loading all at once
2. Use test mode first: `python 01_extract_chunks.py --test`

### 5. Missing Data Issues

#### Problem: Papers without abstracts
**What to expect:**
- ~9-10% of papers may not have abstracts
- Older papers (pre-1990) often lack abstracts
- Some paper types (editorials, corrections) don't have abstracts

**Solution:** Script now reports statistics clearly:
```
Papers with abstracts: 19,477
Papers without abstracts: 1,920
```

### 6. Lens vs OpenAlex Format Differences

| Field | Lens.org | OpenAlex |
|-------|----------|----------|
| Paper ID | `lens_id` | `id` |
| Title | `title` | `display_name` or `title` |
| Abstract | `abstract` | `abstract_inverted_index` |
| Year | `year_published` | `publication_year` |

The extraction script handles both formats automatically.

### 7. Cost Estimation for LLM Processing

**Quick Reference:**
- 67,238 chunks × ~200 tokens/chunk = ~13.4M tokens
- Claude Haiku: ~$3.35 input + $16.75 output = ~$20
- GPT-3.5: ~$6.70 input + $20.10 output = ~$27
- Gemini Pro: Similar pricing

**Reduce costs:**
1. Use relevance filtering first
2. Process in test mode: `--test` flag
3. Use smaller chunk sizes if appropriate

### 8. Rate Limiting

#### Problem: API returns 429 (Too Many Requests)
**Solution:** Scripts include automatic rate limiting (50ms between requests)

#### Problem: Still getting rate limited
**Solutions:**
1. Increase delay in script
2. Use smaller batch sizes
3. Run during off-peak hours

### 9. Quick Diagnostic Commands

```bash
# Check if OpenAlex is accessible
curl "https://api.openalex.org/works?filter=fulltext.search:test&per_page=1"

# Test your data file has correct format
python -c "import json; d=json.load(open('your_file.json')); print(f'Papers: {len(d.get(\"results\", []))}'); print(f'Has abstracts: {sum(1 for r in d[\"results\"] if r.get(\"abstract_inverted_index\"))}')"

# Check chunk file
python -c "import json; d=json.load(open('chunks.json')); print(f'Chunks: {d[\"metadata\"][\"total_chunks\"]}'); print(f'Avg length: {sum(c[\"chunk_length\"] for c in d[\"chunks\"])/len(d[\"chunks\"]):.0f}')"
```

### 10. Emergency Fixes

If all else fails:
1. Use the example files provided
2. Reduce dataset size: `--max 100`
3. Use keyword filtering instead of LLM: `--no-llm`
4. Contact instructor with error message

## Updated Script Capabilities

### fetch_openalex.py
- ✅ Handles all three search types
- ✅ Cursor pagination for unlimited results
- ✅ Progress tracking with ETA
- ✅ Automatic rate limiting
- ✅ Saves metadata with results

### 01_extract_chunks.py
- ✅ Handles OpenAlex inverted index format
- ✅ Handles Lens.org format
- ✅ Safe division (no divide by zero)
- ✅ Test mode for safety
- ✅ Progress indicators

### Usage Examples

```bash
# Fetch full dataset
python fetch_openalex.py "Ottoman Bank" --type fulltext -o ottoman_all.json

# Extract with test mode
python 01_extract_chunks.py --input ottoman_all.json --test

# Extract everything
python 01_extract_chunks.py --input ottoman_all.json --output chunks.json

# Filter for relevance
python 02_relevance_filter.py --topic "banking history" --input chunks.json

# Annotate with taxonomy (test mode)
python 03_annotate_taxonomy.py --taxonomy my_taxonomy.tsv --chunks chunks_filtered.json --test
```

## Contact

If you encounter issues not covered here:
1. Check error message carefully
2. Try with smaller dataset first
3. Verify your API access works
4. Ask instructor for help