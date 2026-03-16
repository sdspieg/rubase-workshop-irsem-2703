# Day 3: Taxonomic Annotation Workshop
## Applying Multi-Dimensional Taxonomies to Research Corpora
### Friday, March 13, 2026

---

## 🎯 Learning Objectives
By the end of this session, participants will:
1. Extract and chunk abstracts from their JSON corpora
2. Apply binary relevance filtering to reduce API costs
3. Taxonomically annotate relevant chunks using their Day 2 taxonomies
4. Analyze coverage and patterns in their classified data
5. Export results for visualization and further analysis

---

## ⏱️ Session Timeline (3 Hours)

### Hour 1: Setup & Data Preparation (60 min)
**5:30-5:45 PM** - Welcome & Overview (15 min)
- Recap Day 1 (corpora) and Day 2 (taxonomies)
- Today's pipeline overview
- Cost considerations and API limits
- Expected outcomes

**5:45-6:00 PM** - Environment Setup (15 min)
- Verify Python installation
- Install required packages: `pip install pandas openai anthropic`
- Test CLI LLM access
- Create working directory structure

**6:00-6:30 PM** - Step 1: Extract & Chunk (30 min)
- Run `01_extract_chunks.py` on JSON files
- Understand chunking strategy (500 chars with 50 char overlap)
- Review output files
- Discuss chunk size tradeoffs

### Hour 2: Filtering & Annotation (60 min)
**6:30-6:45 PM** - Step 2: Relevance Filtering (15 min)
- Run `02_relevance_filter.py`
- Understand binary classification
- Calculate cost savings
- Review filtered results

**6:45-7:00 PM** - BREAK (15 min)

**7:00-7:30 PM** - Step 3: Taxonomic Annotation (30 min)
- Configure `03_annotate_taxonomy.py` with personal taxonomy
- Run small test batch (10 chunks)
- Verify output format
- Calculate full corpus costs
- Run full annotation (or subset based on budget)

### Hour 3: Analysis & Synthesis (60 min)
**7:30-7:50 PM** - Results Analysis (20 min)
- Run `04_analyze_results.py`
- Generate coverage statistics
- Identify patterns and gaps
- Export for visualization

**7:50-8:20 PM** - Group Discussion & Troubleshooting (30 min)
- Share interesting patterns
- Discuss methodology challenges
- Troubleshoot issues
- Plan next steps

**8:20-8:30 PM** - Wrap-up & Next Steps (10 min)
- Export final datasets
- Resources for continued work
- Integration with other tools
- Closing remarks

---

## 📊 Cost Estimation Guide

### Typical Corpus Size
- 500 abstracts × 200 words average = 100,000 words
- After chunking: ~1,000 chunks
- After relevance filtering (30% relevant): ~300 chunks

### API Costs (March 2026 estimates)
**Claude 3 Haiku** (Recommended for this task)
- Input: $0.25 per million tokens
- Output: $1.25 per million tokens
- Estimated cost per corpus: $0.50-$1.50

**GPT-3.5-Turbo**
- Input: $0.50 per million tokens
- Output: $1.50 per million tokens
- Estimated cost per corpus: $0.75-$2.00

**Free Tier Limits**
- Anthropic: $5 free credits (enough for ~5 corpora)
- OpenAI: $5 free credits (enough for ~3 corpora)

---

## 🛠️ Required Files Checklist
Participants should have:
- [ ] JSON corpus from Day 1 (lens_export.json or openalex_export.json)
- [ ] Taxonomy TSV from Day 2 (my_taxonomy.tsv)
- [ ] Python 3.8+ installed
- [ ] CLI LLM configured (claude or openai)
- [ ] Workshop scripts (provided today)

---

## 💡 Tips for Success
1. Start with a small test batch before processing everything
2. Monitor API usage dashboard during processing
3. Save outputs frequently
4. Keep original files as backup
5. Document any modifications to scripts
6. Share interesting findings with the group

---

## 🚀 Extensions (Optional)
For advanced participants who finish early:
- Modify chunk size and overlap parameters
- Add confidence scores to classifications
- Implement multi-label classification
- Create visualization of taxonomy coverage
- Export to Zotero with tags