#!/bin/bash

# Ottoman Bank Full-Text Extraction Pipeline
# This script orchestrates the complete pipeline from OpenAlex to annotated chunks

echo "=========================================="
echo "Ottoman Bank Full-Text Extraction Pipeline"
echo "=========================================="

# Check if GROBID is running
check_grobid() {
    if curl -s http://localhost:8070/api/isalive > /dev/null 2>&1; then
        echo "✓ GROBID server is running"
        return 0
    else
        echo "✗ GROBID server is not running"
        echo ""
        echo "Please start GROBID with:"
        echo "  docker run --rm -p 8070:8070 lfoppiano/grobid:0.7.3"
        echo ""
        echo "Or if you have GROBID installed locally:"
        echo "  cd /path/to/grobid && ./gradlew run"
        return 1
    fi
}

# Step 0: Check prerequisites
echo ""
echo "Step 0: Checking prerequisites..."
echo "---------------------------------"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed"
    exit 1
else
    echo "✓ Python 3 is installed"
fi

# Check required Python packages
python3 -c "import requests" 2>/dev/null || {
    echo "Installing required Python packages..."
    pip install requests
}

# Check if we have the OpenAlex data
if [ ! -f "ottoman_bank_ALL.json" ]; then
    echo ""
    echo "✗ Ottoman Bank dataset not found!"
    echo "Please run: python3 fetch_openalex.py 'Ottoman Bank' --type fulltext --all -o ottoman_bank_ALL.json"
    exit 1
else
    echo "✓ Ottoman Bank dataset found"
fi

# Step 1: Analyze OA status
echo ""
echo "Step 1: Analyzing Open Access status..."
echo "---------------------------------------"
python3 analyze_open_access.py --input ottoman_bank_ALL.json

# Ask user if they want to proceed with download
echo ""
echo "Ready to download ~21,000 PDFs (estimated 10-20 GB)"
read -p "Do you want to proceed with PDF downloads? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipping PDF download. You can run this later with:"
    echo "  python3 download_all_pdfs.py --input ottoman_bank_ALL.json"
else
    # Step 2: Download PDFs
    echo ""
    echo "Step 2: Downloading PDFs..."
    echo "---------------------------"
    echo "This will take several hours. The script will resume if interrupted."
    echo ""

    # Start download with 5 workers
    python3 download_all_pdfs.py --input ottoman_bank_ALL.json --workers 5

    # Check if download was successful
    if [ ! -d "ottoman_pdfs" ] || [ -z "$(ls -A ottoman_pdfs)" ]; then
        echo "✗ No PDFs were downloaded"
        exit 1
    fi

    PDF_COUNT=$(ls ottoman_pdfs/*.pdf 2>/dev/null | wc -l)
    echo "✓ Downloaded $PDF_COUNT PDFs"
fi

# Step 3: GROBID parsing
echo ""
echo "Step 3: Parsing PDFs with GROBID..."
echo "-----------------------------------"

# Check if GROBID is running
if ! check_grobid; then
    echo "Please start GROBID and run:"
    echo "  python3 grobid_parse_pdfs.py"
    exit 1
fi

echo "Starting GROBID parsing..."
echo "This will take several hours. The script will resume if interrupted."
python3 grobid_parse_pdfs.py --workers 3

# Check if parsing was successful
if [ ! -d "ottoman_fulltext" ] || [ -z "$(ls -A ottoman_fulltext)" ]; then
    echo "✗ No full texts were extracted"
    exit 1
fi

FULLTEXT_COUNT=$(ls ottoman_fulltext/*.json 2>/dev/null | wc -l)
echo "✓ Extracted full text from $FULLTEXT_COUNT PDFs"

# Step 4: Create chunks from full text
echo ""
echo "Step 4: Creating chunks from full text..."
echo "-----------------------------------------"
python3 extract_fulltext_chunks.py

# Check if chunking was successful
if [ ! -f "ottoman_bank_fulltext_chunks.json" ]; then
    echo "✗ Chunk creation failed"
    exit 1
fi

echo "✓ Chunks created successfully"

# Step 5: Apply taxonomy annotation
echo ""
echo "Step 5: Annotating chunks with Ottoman Bank taxonomy..."
echo "-------------------------------------------------------"

# First test with a small subset
echo "Testing annotation with 10 chunks..."
python3 ottoman_bank_annotate.py \
    --input ottoman_fulltext_tier1_mentions.json \
    --output ottoman_fulltext_annotated_test.json \
    --test

echo ""
echo "Full annotation available with:"
echo "  python3 ottoman_bank_annotate.py --input ottoman_fulltext_tier1_mentions.json --output ottoman_fulltext_annotated.json"

# Step 6: Summary
echo ""
echo "=========================================="
echo "PIPELINE COMPLETE"
echo "=========================================="
echo ""
echo "Results:"
echo "--------"

if [ -f "download_manifest.json" ]; then
    python3 -c "
import json
with open('download_manifest.json') as f:
    m = json.load(f)
    stats = m.get('statistics', {})
    print(f\"PDFs downloaded: {stats.get('success', 0):,}\")
"
fi

if [ -f "grobid_parsed_manifest.json" ]; then
    python3 -c "
import json
with open('grobid_parsed_manifest.json') as f:
    m = json.load(f)
    stats = m.get('statistics', {})
    print(f\"Full texts extracted: {stats.get('success', 0):,}\")
"
fi

if [ -f "ottoman_bank_fulltext_chunks.json" ]; then
    python3 -c "
import json
with open('ottoman_bank_fulltext_chunks.json') as f:
    data = json.load(f)
    meta = data.get('metadata', {})
    print(f\"Total chunks created: {meta.get('total_chunks', 0):,}\")
    print(f\"Chunks with Ottoman Bank mentions: {meta.get('chunks_with_mentions', 0):,}\")
"
fi

echo ""
echo "Available datasets:"
echo "------------------"
echo "1. ottoman_fulltext_tier1_mentions.json - Direct Ottoman Bank mentions"
echo "2. ottoman_fulltext_tier2_papers.json - Chunks from papers with mentions"
echo "3. ottoman_fulltext_tier3_sample.json - Sample of all chunks"
echo ""
echo "Next steps:"
echo "-----------"
echo "1. Review the extracted chunks"
echo "2. Run full annotation on desired tier"
echo "3. Analyze annotation results"
echo ""
echo "For workshop use, recommend starting with Tier 1 (direct mentions)"