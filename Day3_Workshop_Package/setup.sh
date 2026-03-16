#!/bin/bash
# Setup script for Day 3 Workshop
# Run with: bash setup.sh

echo "======================================"
echo "Day 3 Workshop Setup"
echo "======================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$python_version" ]]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
echo "✅ Python version: $python_version"

# Create virtual environment (optional but recommended)
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install requirements
echo ""
echo "Installing required packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Testing CLI LLM availability..."
echo "======================================"

# Test Claude CLI
echo -n "Testing Claude CLI: "
if command -v claude &> /dev/null; then
    echo "✅ Available"
    echo "  $(claude --version 2>&1 | head -1)"
else
    echo "⚠️ Not installed"
    echo "  Install with: pip install anthropic"
fi

# Test OpenAI CLI
echo -n "Testing OpenAI CLI: "
if command -v openai &> /dev/null; then
    echo "✅ Available"
else
    echo "⚠️ Not installed"
    echo "  Install with: pip install openai"
fi

# Test Gemini setup
echo -n "Testing Gemini API: "
if [ ! -z "$GEMINI_API_KEY" ]; then
    echo "✅ API key found"
else
    echo "⚠️ No API key"
    echo "  Set with: export GEMINI_API_KEY='your-key-here'"
    echo "  Get key from: https://makersuite.google.com/app/apikey"
fi

# Create working directory
echo ""
echo "Creating working directories..."
mkdir -p data
mkdir -p output
echo "✅ Created data/ and output/ directories"

# Check for Day 1 and Day 2 files
echo ""
echo "======================================"
echo "Checking for required files..."
echo "======================================"

echo -n "Looking for corpus JSON files: "
if ls *.json 1> /dev/null 2>&1; then
    echo "✅ Found JSON files:"
    ls *.json | head -5
else
    echo "⚠️ No JSON files found"
    echo "  Please copy your corpus file from Day 1"
fi

echo -n "Looking for taxonomy TSV files: "
if ls *.tsv 1> /dev/null 2>&1; then
    echo "✅ Found TSV files:"
    ls *.tsv | head -5
else
    echo "⚠️ No TSV files found"
    echo "  Please copy your taxonomy file from Day 2"
fi

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Copy your corpus JSON file from Day 1 to this directory"
echo "2. Copy your taxonomy TSV file from Day 2 to this directory"
echo "3. Run: python 01_extract_chunks.py --input your_corpus.json"
echo ""
echo "For help with any script, use the --help flag:"
echo "  python 01_extract_chunks.py --help"