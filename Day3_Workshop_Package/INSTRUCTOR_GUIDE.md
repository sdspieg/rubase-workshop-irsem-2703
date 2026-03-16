# Instructor Guide: Day 3 Taxonomic Annotation Workshop

## Pre-Workshop Preparation (30 min before)

### Technical Setup
1. **Test all scripts** with sample data
2. **Verify LLM access** - have backup API keys ready
3. **Prepare example files**:
   - Sample corpus JSON (50-100 papers)
   - Sample taxonomy TSV (from Day 2 or prepared example)
   - Pre-run results for demonstration
4. **Cost monitoring** - Have API dashboards open:
   - https://console.anthropic.com/usage
   - https://platform.openai.com/usage

### Materials Checklist
- [ ] Workshop package files distributed
- [ ] Slides/presentation ready
- [ ] Backup USB with all files
- [ ] Sample outputs for comparison
- [ ] Cost estimation spreadsheet
- [ ] Troubleshooting guide printed

---

## Hour 1: Setup & Data Preparation (5:30-6:30 PM)

### Opening (5:30-5:45)
**Key Points:**
- Recap what they built on Days 1-2
- Today's goal: Connect corpus to taxonomy
- Show end result visualization first (motivation)
- Emphasize cost consciousness

**Live Demo Preparation:**
```bash
# Have this ready to run
cd Day3_Workshop_Package
bash setup.sh
```

### Environment Setup (5:45-6:00)
**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| Python not found | Use `python3` or `py` on Windows |
| pip install fails | Try `--user` flag or use conda |
| CLI LLM not working | Use `--no-llm` flag for demos |
| Import errors | Check virtual environment activation |

**Quick Test:**
```python
# Have participants run this
python -c "import json, csv, os; print('✅ Basic imports work')"
```

### Extract & Chunk Demo (6:00-6:30)
**Script 1 Walkthrough:**

```bash
# Basic usage
python 01_extract_chunks.py --input corpus.json

# Custom chunk size (for demos)
python 01_extract_chunks.py --input corpus.json --chunk-size 300
```

**Teaching Points:**
1. Why chunking matters (context windows)
2. Overlap prevents information loss
3. Chunk size tradeoffs:
   - Smaller = more API calls = higher cost
   - Larger = less granular annotation

**Expected Output:**
```
📊 Statistics:
  Papers processed: 100
  Chunks created: 450
  Avg chunks per paper: 4.5
```

---

## Hour 2: Filtering & Annotation (6:30-7:30 PM)

### Relevance Filtering (6:30-6:45)
**Key Demonstration:**

```bash
# With their actual topic
python 02_relevance_filter.py \
  --input chunks.json \
  --topic "cyber security in critical infrastructure"

# Fallback without LLM
python 02_relevance_filter.py \
  --input chunks.json \
  --topic "cyber security" \
  --no-llm
```

**Discussion Points:**
- Show actual cost savings (usually 60-70% reduction)
- Explain binary classification simplicity
- Relevance vs. importance distinction

### Break Management (6:45-7:00)
- Have participants save their progress
- Keep one example running on projector
- Answer individual questions

### Taxonomic Annotation (7:00-7:30)
**Critical Section - Go Slow Here**

**Test Mode First (IMPORTANT):**
```bash
# Always start with test mode
python 03_annotate_taxonomy.py \
  --chunks chunks_filtered.json \
  --taxonomy my_taxonomy.tsv \
  --test

# This only processes 10 chunks - safe for demos
```

**Check Costs Before Full Run:**
```python
# Quick cost calculator
chunks = 300  # their number
cost_per_1k = 0.001  # Claude Haiku
total = chunks * cost_per_1k
print(f"Estimated cost: ${total:.2f}")
```

**Full Run (if affordable):**
```bash
python 03_annotate_taxonomy.py \
  --chunks chunks_filtered.json \
  --taxonomy my_taxonomy.tsv \
  --export-csv
```

**Troubleshooting Taxonomy Format:**
If their TSV doesn't load:
1. Check delimiter (tab vs comma)
2. Check column headers
3. Provide sample TSV format:
```
HLTP	2nd Level TE	3rd Level TE	Taxon
Geographic	Regional	Europe	France
Geographic	Regional	Europe	Germany
```

---

## Hour 3: Analysis & Synthesis (7:30-8:30 PM)

### Results Analysis (7:30-7:50)
**Run Analysis:**
```bash
python 04_analyze_results.py \
  --input chunks_annotated.json \
  --export-all
```

**Interpret Results Together:**
1. Coverage percentage (aim for >70%)
2. Dimension balance (look for outliers)
3. Taxonomy fit (too many unannnotated = poor fit)

**Common Patterns to Discuss:**
- Geographic dimension often dominates
- Temporal dimensions underutilized
- Methods dimension good discriminator

### Group Discussion (7:50-8:20)
**Facilitation Questions:**

1. **Discovery:** "What surprised you about your corpus?"
2. **Taxonomy Fit:** "How well did your taxonomy match?"
3. **Gaps:** "What dimensions were missing?"
4. **Methods:** "Would you change chunk size?"

**Share Examples:**
- Have 2-3 volunteers show their coverage matrix
- Discuss different patterns
- Celebrate interesting findings

### Wrap-up (8:20-8:30)
**Final Checklist:**
- [ ] Everyone has saved outputs
- [ ] Share link to workshop materials
- [ ] Provide follow-up resources
- [ ] Collect feedback

**Next Steps for Participants:**
1. Refine taxonomy based on results
2. Try different chunking strategies
3. Experiment with different models
4. Integrate with reference manager

---

## Emergency Procedures

### If LLM APIs Are Down
1. Switch to `--no-llm` mode
2. Use pre-computed results in `backup_results/`
3. Focus on methodology discussion

### If Time Runs Short
Priority order:
1. ✅ Extract & chunk (must complete)
2. ✅ Test mode annotation (must see)
3. ⚠️ Skip full annotation
4. ✅ Show pre-computed analysis

### If Costs Are Concern
- Use smallest model (Haiku/GPT-3.5)
- Process subset (first 50 chunks)
- Share one account for demos
- Use test mode only

---

## Post-Workshop

### Data to Collect
1. Number of successful completions
2. Average processing time
3. Total API costs incurred
4. Common error types

### Materials to Share
- Completed notebooks
- Additional example taxonomies
- Visualization templates
- Paper on methodology

### Follow-up Communication
Send within 24 hours:
- Thank you note
- Links to all materials
- Troubleshooting FAQ
- Office hours schedule

---

## Quick Reference Card

```bash
# The Complete Pipeline
python 01_extract_chunks.py -i corpus.json
python 02_relevance_filter.py -i chunks.json -t "research topic"
python 03_annotate_taxonomy.py -c chunks_filtered.json -t taxonomy.tsv --test
python 04_analyze_results.py -i chunks_annotated.json --export-all
```

**Typical Costs:**
- 500 papers → 1000 chunks → 300 relevant → $0.50-$1.50 total

**Time Estimates:**
- Extraction: 1-2 minutes
- Filtering: 3-5 minutes
- Annotation: 5-10 minutes
- Analysis: 1 minute

**Success Metrics:**
- ✅ >70% chunks annotated
- ✅ >3 dimensions used
- ✅ <$2 total cost
- ✅ Meaningful patterns identified