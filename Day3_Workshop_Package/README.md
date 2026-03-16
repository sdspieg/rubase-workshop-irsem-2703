# Day 3: Taxonomic Annotation Workshop Package
## AI-Powered Research Classification Pipeline

Welcome to Day 3 of the RuBase Workshop! Today you'll apply your multi-dimensional taxonomy to classify your research corpus using LLMs.

---

## 🚀 Quick Start

```bash
# 1. Setup environment
bash setup.sh

# 2. Run the complete pipeline
python 01_extract_chunks.py --input your_corpus.json
python 02_relevance_filter.py --input chunks.json --topic "your research topic"
python 03_annotate_taxonomy.py --chunks chunks_filtered.json --taxonomy your_taxonomy.tsv --test
python 04_analyze_results.py --input chunks_annotated.json --export-all
```

---

## 📁 File Structure

```
Day3_Workshop_Package/
├── Core Pipeline Scripts
│   ├── 01_extract_chunks.py      # Extract and chunk abstracts
│   ├── 02_relevance_filter.py    # Filter relevant chunks
│   ├── 03_annotate_taxonomy.py   # Apply taxonomy labels
│   └── 04_analyze_results.py     # Analyze and visualize
│
├── Data Fetching (NEW)
│   ├── fetch_openalex.py         # Fetch data from OpenAlex API
│   │                              # Supports full-text search
│   │                              # Handles unlimited results
│   └── 05_download_fulltext.py   # Download full-text PDFs
│                                  # Works with any OA papers
│                                  # Includes retry logic
│
├── Setup & Documentation
│   ├── setup.sh                  # Environment setup script
│   ├── requirements.txt          # Python dependencies
│   ├── TROUBLESHOOTING.md        # Common issues & solutions (NEW)
│   ├── SESSION_STRUCTURE.md      # 3-hour workshop timeline
│   ├── INSTRUCTOR_GUIDE.md       # Detailed teaching guide
│   └── README.md                  # This file
│
└── Example Data
    ├── example_openalex_real.json   # Real OpenAlex format
    ├── example_lens_real.json       # Real Lens format
    └── ottoman_bank_ALL.json        # Full dataset example (21k papers)
```

---

## 📋 Prerequisites

### From Previous Days
- **Day 1:** JSON corpus file from Lens.org or OpenAlex (`corpus.json`)
- **Day 2:** Taxonomy TSV file (`my_taxonomy.tsv`)

### Technical Requirements
- Python 3.8 or higher
- CLI LLM tool (Claude or OpenAI CLI)
- ~1GB free disk space
- Internet connection for API calls

---

## 🔧 Installation

### Option 1: Automated Setup
```bash
bash setup.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install CLI tools (choose one)
pip install anthropic  # For Claude
pip install openai     # For GPT
```

---

## 📊 Pipeline Steps

### Step 1: Extract and Chunk Abstracts
Splits abstracts into manageable chunks for processing.

```bash
python 01_extract_chunks.py --input corpus.json --output chunks.json

# Options:
#   --chunk-size 500    # Characters per chunk (default: 500)
#   --overlap 50        # Overlap between chunks (default: 50)
```

**Expected output:** `chunks.json` with ~5 chunks per abstract

### Step 2: Binary Relevance Filtering
Reduces chunks to only those relevant to your research topic.

```bash
python 02_relevance_filter.py \
    --input chunks.json \
    --output chunks_filtered.json \
    --topic "cyber security in critical infrastructure"

# Options:
#   --no-llm           # Use keyword matching instead of LLM
```

**Expected output:** `chunks_filtered.json` with ~30% of original chunks

### Step 3: Taxonomic Annotation
Applies taxonomy labels to relevant chunks.

```bash
# ALWAYS test first with 10 chunks
python 03_annotate_taxonomy.py \
    --chunks chunks_filtered.json \
    --taxonomy my_taxonomy.tsv \
    --output chunks_annotated.json \
    --test

# If test looks good and cost is acceptable, run full annotation
python 03_annotate_taxonomy.py \
    --chunks chunks_filtered.json \
    --taxonomy my_taxonomy.tsv \
    --output chunks_annotated.json \
    --export-csv

# Options:
#   --test             # Process only 10 chunks for testing
#   --no-llm           # Use keyword matching instead
#   --export-csv       # Also export as CSV
```

**Expected output:** `chunks_annotated.json` with taxonomy labels

### Step 4: Analyze Results
Generates statistics and visualizations.

```bash
python 04_analyze_results.py \
    --input chunks_annotated.json \
    --output-prefix analysis \
    --export-all

# Options:
#   --export-all       # Export all analysis files
```

**Expected outputs:**
- `analysis_visualization.txt` - Text-based charts
- `analysis_coverage_matrix.csv` - Paper × Taxa matrix
- `analysis_summary.json` - Statistics summary

---

## 💰 Cost Estimation

### Typical Corpus (500 papers)
| Step | Items | Cost |
|------|-------|------|
| Extraction | 1000 chunks created | Free |
| Filtering | 1000 chunks → 300 relevant | ~$0.25 |
| Annotation | 300 chunks annotated | ~$0.75 |
| **Total** | | **~$1.00** |

### Cost by Model
- **Claude 3 Haiku:** $0.25/1M input, $1.25/1M output
- **GPT-3.5-Turbo:** $0.50/1M input, $1.50/1M output
- **GPT-4:** $30/1M input, $60/1M output (not recommended)

### Cost Saving Tips
1. Always use `--test` mode first
2. Use aggressive relevance filtering
3. Reduce chunk size if needed
4. Use Haiku or GPT-3.5 for annotation

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "LLM not found" | Use `--no-llm` flag or install CLI tool |
| "Taxonomy won't load" | Check TSV format, use tabs not commas |
| "Out of API credits" | Use test mode or --no-llm fallback |
| "Import error" | Activate virtual environment |
| "JSON decode error" | Check corpus file format |

### Taxonomy TSV Format
Your taxonomy file must have this exact format:
```tsv
HLTP	2nd Level TE	3rd Level TE	Taxon
Geographic	Regional	Europe	France
Geographic	Regional	Europe	Germany
Temporal	Historical	20th Century	World War II
```

### Corpus JSON Format
Supports both Lens.org and OpenAlex formats:
```json
{
  "results": [
    {
      "title": "Paper title",
      "abstract": "Abstract text..."
    }
  ]
}
```

---

## 📈 Interpreting Results

### Good Coverage Indicators
- ✅ >70% of chunks have annotations
- ✅ 3+ dimensions actively used
- ✅ Even distribution across papers
- ✅ Reasonable taxa frequency (not too concentrated)

### Warning Signs
- ⚠️ <50% chunks annotated → taxonomy too specific
- ⚠️ 1 dimension dominates → add more dimensions
- ⚠️ Too many labels per chunk → refine taxonomy
- ⚠️ Very few unique taxa → taxonomy doesn't fit

---

## 🎓 Learning Objectives

By completing this workshop, you will:
1. ✅ Understand text chunking strategies
2. ✅ Apply binary relevance filtering
3. ✅ Implement multi-label classification
4. ✅ Analyze taxonomy coverage
5. ✅ Identify patterns in your corpus

---

## 📚 Additional Resources

- [OpenAlex API Documentation](https://docs.openalex.org)
- [Anthropic Claude Pricing](https://www.anthropic.com/pricing)
- [OpenAI Pricing](https://openai.com/pricing)
- [RuBase Project](https://hcss.nl/rubase/)

---

## 🆘 Support

During the workshop:
- Raise your hand for immediate help
- Check the troubleshooting section above
- Ask your neighbor (collaborative learning!)

After the workshop:
- Email: stephan@hcss.nl
- GitHub Issues: [Workshop Repository](https://github.com/sdspieg/rubase-workshop-fletcher-2603)

---

## 📝 Notes Section

Use this space to track your progress:

- [ ] Corpus loaded successfully
- [ ] Chunks created: _____ total
- [ ] Filtered to: _____ relevant chunks
- [ ] Taxonomy loaded with _____ dimensions
- [ ] Test annotation successful
- [ ] Full annotation cost estimate: $_____
- [ ] Final coverage: _____%
- [ ] Interesting findings:
  -
  -
  -

---

**Happy Annotating! 🚀**

*Remember: Start small, test first, monitor costs!*