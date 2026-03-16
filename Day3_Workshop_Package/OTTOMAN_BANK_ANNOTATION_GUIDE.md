# Ottoman Bank Taxonomy Annotation System

## Overview

This system annotates text chunks about the Imperial Ottoman Bank using a comprehensive 6-HLTP taxonomy developed using the Multi-Dimensional Taxonomy Development Framework (MDTDF). It's based on the advanced "transparent battlefield" annotation approach used for the Russian-Ukrainian War corpus.

## Components

### 1. Taxonomy Structure (`ottoman_bank_taxonomy.tsv`)

The taxonomy consists of **6 High-Level Topic Pillars (HLTPs)** with **66 specific taxa**:

1. **Financial Operations** (11 taxa)
   - Banking Services: Lending, Currency, Deposits
   - Investment Activities: Securities, Trade Finance

2. **Institutional Structure** (10 taxa)
   - Governance: Ownership, Management
   - Operations: Branches, Staff

3. **Historical Context** (12 taxa)
   - Founding Period (1854-1870s)
   - Imperial Era (1876-1918)
   - Republican Transition (1918-1930s)

4. **Economic Impact** (13 taxa)
   - Public Finance: Debt, Revenue
   - Development Finance: Infrastructure, Industry
   - Trade Relations: Commerce, Monetary System

5. **Political Dimensions** (12 taxa)
   - Imperial Relations: Foreign Influence, Diplomacy
   - State Functions: Treasury, Monetary Authority
   - Reform Movements: Tanzimat, Constitutional Periods

6. **Social and Cultural** (12 taxa)
   - Modernization: Western Influence, Economic Culture
   - Community Relations: Ethnic Banking, Religious Issues
   - Knowledge Transfer: Education, Documentation

### 2. Annotation System (`ottoman_bank_annotate.py`)

Features:
- Multi-LLM support (Claude, OpenAI, Gemini)
- Batch processing with rate limiting
- Test mode for safe experimentation
- Fallback keyword matching
- Detailed statistics and coverage analysis

### 3. Annotation Prompt (`ottoman_bank_annotation_prompt.txt`)

A sophisticated prompt that:
- Provides historical context about the Ottoman Bank
- Defines clear relevance criteria
- Presents the full taxonomy with explanations
- Guides classification decisions

## Usage

### Basic Annotation

```bash
# Annotate all chunks
python ottoman_bank_annotate.py --input ottoman_bank_chunks_ALL.json --output annotated.json

# Test mode (10 chunks only)
python ottoman_bank_annotate.py --input chunks.json --test --output test.json

# Without LLM (keyword matching only)
python ottoman_bank_annotate.py --input chunks.json --no-llm --output keyword.json
```

### Data Pipeline

```bash
# 1. Fetch data from OpenAlex
python fetch_openalex.py "Ottoman Bank" --type fulltext -o ottoman_raw.json

# 2. Extract and chunk abstracts
python 01_extract_chunks.py --input ottoman_raw.json --output chunks.json

# 3. Filter for relevance (optional)
python 02_relevance_filter.py --topic "banking history" --input chunks.json

# 4. Apply Ottoman Bank taxonomy
python ottoman_bank_annotate.py --input chunks_filtered.json --output annotated.json

# 5. Analyze results
python 04_analyze_results.py --input annotated.json --export-all
```

## Dataset Statistics

From the full OpenAlex corpus:
- **Total papers found**: 21,397
- **Papers with abstracts**: 19,477 (91%)
- **Total chunks created**: 67,238
- **Average chunks per paper**: 3.5
- **Year range**: 1766-2026

## Relevance Criteria

### Directly Relevant
- The Imperial Ottoman Bank itself
- Its operations, governance, policies
- Its role in Ottoman/Turkish economy
- Relationships with governments and communities

### Contextually Relevant
- Ottoman public debt where Bank played a role
- European financial imperialism
- Banking modernization in late Ottoman period
- Tanzimat economic reforms

### Not Relevant
- Separate mentions of "Ottoman" or "Bank"
- Other Ottoman institutions without banking connection
- Pure political/military history
- Fragmentary text or metadata

## Advanced Features

### Tiered Relevance Filtering

Similar to the transparent battlefield approach, you can implement tiered filtering:

**Tier 1 (Core)**: Financial Operations, Institutional Structure
**Tier 2 (High)**: Historical Context, Economic Impact
**Tier 3 (Partial)**: Select Political and Social taxa

### Batch Processing

For large corpora, process in batches:
```python
# In the script, adjust:
BATCH_SIZE = 10  # Chunks per LLM call
CONCURRENCY = 5  # Parallel processing
```

### Cost Management

Estimated costs for full corpus:
- 67,238 chunks × ~200 tokens = ~13.4M tokens
- Claude Haiku: ~$20
- GPT-3.5: ~$27
- Gemini: Similar

Use test mode and relevance filtering to reduce costs.

## Comparison with Transparent Battlefield

| Aspect | Transparent Battlefield | Ottoman Bank |
|--------|------------------------|--------------|
| Domain | Military/Strategic | Financial/Economic |
| HLTPs | 6 (ISR, Kill Chains, etc.) | 6 (Financial, Historical, etc.) |
| Taxa | ~50 | 66 |
| Corpus | RUW documents | OpenAlex papers |
| Languages | Russian, English | Multiple |
| Pre-filtering | 3-tier military relevance | Ottoman Bank mentions |

## Workshop Integration

This system demonstrates:
1. **Domain Adaptation**: Taking military annotation approach to financial history
2. **MDTDF Application**: Systematic taxonomy development
3. **Scale Management**: Handling 67,000+ chunks efficiently
4. **Cost Optimization**: Test modes and filtering strategies
5. **Multi-LLM Support**: Flexibility across providers

## Next Steps

1. **Refinement**: Test with domain experts
2. **Expansion**: Add temporal and geographic dimensions
3. **Visualization**: Create taxonomy coverage heatmaps
4. **Validation**: Inter-annotator agreement studies
5. **Integration**: Link to document retrieval systems

## Files Created

- `ottoman_bank_taxonomy.tsv` - 6-HLTP taxonomy with 66 taxa
- `ottoman_bank_annotation_prompt.txt` - Detailed classification prompt
- `ottoman_bank_annotate.py` - Annotation script
- `ottoman_bank_chunks_ALL.json` - 67,238 chunks from OpenAlex
- `ottoman_bank_test_subset.json` - 10 chunks for testing

## Credits

Based on the transparent battlefield annotation system developed for the Russian-Ukrainian War corpus by HCSS (The Hague Centre for Strategic Studies).