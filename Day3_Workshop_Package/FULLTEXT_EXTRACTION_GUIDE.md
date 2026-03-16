# Full-Text Extraction Pipeline Guide

## Overview

This guide explains how to extract and process full-text content from 21,000+ Ottoman Bank papers using OpenAlex, GROBID, and custom chunking algorithms.

## Pipeline Architecture

```
OpenAlex API → PDF Download → GROBID Parsing → Text Chunking → Taxonomy Annotation
     ↓             ↓              ↓                ↓                    ↓
21,397 papers  21,148 PDFs   Full text XML   Smart chunks    Classified chunks
```

## Prerequisites

### 1. Software Requirements

```bash
# Python 3.8+
pip install requests

# GROBID (choose one):
# Option A: Docker (recommended)
docker pull lfoppiano/grobid:0.7.3

# Option B: Local installation
git clone https://github.com/kermitt2/grobid.git
cd grobid
./gradlew run
```

### 2. Hardware Requirements

- **Storage**: 20-30 GB for PDFs + 5-10 GB for extracted text
- **RAM**: 8 GB minimum (16 GB recommended for GROBID)
- **Network**: Stable connection for downloading ~21,000 PDFs

## Step-by-Step Execution

### Step 1: Verify Open Access Availability

```bash
python3 analyze_open_access.py --input ottoman_bank_ALL.json
```

Expected output:
- 98.9% papers are Open Access
- 21,148 papers have downloadable URLs

### Step 2: Download PDFs

```bash
# Start download (will resume if interrupted)
python3 download_all_pdfs.py --input ottoman_bank_ALL.json --workers 5

# Monitor progress (in another terminal)
tail -f pdf_download.log
```

**Time estimate**: 4-8 hours depending on connection
**Storage needed**: 10-20 GB

The script features:
- Automatic retry on failure (3 attempts)
- Resume capability (won't re-download existing files)
- Progress tracking and ETA
- Concurrent downloads (5 workers by default)

### Step 3: Start GROBID Server

```bash
# Using Docker (recommended)
docker run -d --rm -p 8070:8070 --name grobid lfoppiano/grobid:0.7.3

# Verify it's running
curl http://localhost:8070/api/isalive
```

### Step 4: Parse PDFs with GROBID

```bash
# Start parsing (will resume if interrupted)
python3 grobid_parse_pdfs.py --workers 3

# Monitor progress
tail -f grobid_parsing.log
```

**Time estimate**: 6-12 hours
**Output**: JSON files with structured text in `ottoman_fulltext/`

GROBID extracts:
- Title and abstract
- Section headings and content
- References and citations
- Structured full text

### Step 5: Extract and Chunk Full Text

```bash
python3 extract_fulltext_chunks.py
```

This creates:
- Smart chunks centered around Ottoman Bank mentions
- Regular overlapping chunks for full coverage
- Tiered datasets for different use cases

**Output files**:
- `ottoman_bank_fulltext_chunks.json` - All chunks
- `ottoman_fulltext_tier1_mentions.json` - Direct mentions only
- `ottoman_fulltext_tier2_papers.json` - Papers with mentions
- `ottoman_fulltext_tier3_sample.json` - Representative sample

### Step 6: Apply Taxonomy Annotation

```bash
# Test with 10 chunks
python3 ottoman_bank_annotate.py \
    --input ottoman_fulltext_tier1_mentions.json \
    --output test_annotated.json \
    --test

# Full annotation (costs ~$5-50 depending on tier)
python3 ottoman_bank_annotate.py \
    --input ottoman_fulltext_tier1_mentions.json \
    --output ottoman_fulltext_annotated.json
```

## Automated Pipeline

Run the entire pipeline with one command:

```bash
./run_fulltext_pipeline.sh
```

This script:
1. Checks prerequisites
2. Analyzes OA availability
3. Downloads PDFs (with confirmation)
4. Parses with GROBID
5. Extracts chunks
6. Runs test annotation

## Expected Results

### From Abstracts Only (Original Approach)
- 67,238 chunks from abstracts
- 18 chunks (0.03%) mention "Ottoman Bank"
- Cost: ~$27 for full annotation

### From Full Text (New Approach)
- Estimated 10-20 million chunks from full text
- Estimated 5-10% mention "Ottoman Bank"
- ~1-2 million relevant chunks
- Cost: $400-800 for Tier 1 only

## Optimization Strategies

### 1. Tiered Processing
Start with Tier 1 (direct mentions) for:
- Highest relevance
- Lowest cost
- Best for taxonomy testing

### 2. Smart Chunking
Our algorithm:
- Centers Ottoman Bank mentions in chunks
- Preserves context (1000 char chunks)
- Creates overlapping chunks for coverage
- Marks high-relevance chunks

### 3. Resume Capability
All scripts support resuming:
- Download manifest tracks completed PDFs
- GROBID manifest tracks parsed files
- Won't re-process completed items

## Troubleshooting

### GROBID Issues

```bash
# Check if running
curl http://localhost:8070/api/isalive

# View logs
docker logs grobid

# Restart if needed
docker restart grobid

# Increase memory (if needed)
docker run -d --rm -p 8070:8070 -m 4g --name grobid lfoppiano/grobid:0.7.3
```

### Download Failures

```bash
# Resume downloads
python3 download_all_pdfs.py --input ottoman_bank_ALL.json

# Check manifest for errors
python3 -c "
import json
with open('download_manifest.json') as f:
    m = json.load(f)
    for paper_id, result in m['downloads'].items():
        if result['status'] != 'success':
            print(f\"{result['status']}: {paper_id}\")
"
```

### Storage Issues

```bash
# Check disk space
df -h ottoman_pdfs/

# Remove PDFs after GROBID parsing (optional)
rm ottoman_pdfs/*.pdf
```

## Cost Analysis

### LLM Annotation Costs (GPT-3.5)

| Dataset | Chunks | Cost |
|---------|--------|------|
| Tier 1 (mentions) | ~50,000 | $20 |
| Tier 2 (papers) | ~500,000 | $200 |
| Full text (all) | ~10M | $4,000 |

### Recommendations

1. **For Workshop Demo**: Use Tier 1 subset (10-100 chunks)
2. **For Research**: Process Tier 1 fully, sample Tier 2
3. **For Production**: Implement relevance filtering first

## Workshop Integration

### Learning Objectives Demonstrated

1. **Scale Management**: From 21K papers to millions of chunks
2. **Pipeline Design**: Modular, resumable, monitored
3. **Cost Optimization**: Tiered processing strategies
4. **Quality Control**: Smart chunking for relevance
5. **Tool Integration**: OpenAlex → GROBID → Custom processing

### Key Takeaways

1. **Abstract vs Full-Text**: 0.03% vs 5-10% mention rate
2. **OA Advantage**: 98.9% availability enables analysis
3. **Processing Time**: Days not hours for full pipeline
4. **Cost Scaling**: Linear with chunk count
5. **Relevance Filtering**: Critical for feasibility

## Next Steps

1. **Run the pipeline** on a subset first
2. **Evaluate chunk quality** from Tier 1
3. **Test taxonomy** on high-relevance chunks
4. **Calculate ROI** for full processing
5. **Optimize** based on initial results

## Support

For issues or questions:
- Check log files (*.log)
- Review manifest files (*_manifest.json)
- Verify prerequisites (GROBID, storage, network)
- Test with small subsets first