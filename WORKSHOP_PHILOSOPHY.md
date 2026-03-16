# Workshop Philosophy: "Teaching to Fish"

## Core Principle
**We give you the fishing rod and teach you to use it, not just hand you the fish.**

The workshop provides scripts, tools, and data examples, BUT the main goal is teaching YOU how to use CLI tools and research methods independently.

## The Ottoman Bank Case Study Example

Instead of just providing finished research, we demonstrate:

### 1. Query Development
- **What we show**: How to search OpenAlex with specific terms
- **What you learn**: How to construct effective academic search queries
- **The insight**: Quotes matter! ("Ottoman Bank" = 511 results vs Ottoman Bank = 21,388 results)

### 2. Multiple Search Strategies
- **Direct institutional search**: "Ottoman Bank" → 511 papers
- **Geographic approach**: "Galata district" AND bankers → 6 papers (found missed papers!)
- **Broader context**: Galata AND banking → 306 papers
- **What you learn**: Same topic, different angles reveal different datasets

### 3. Critical Discovery Process
- Found a 2024 paper about Ottoman Bank director via Galata search
- This paper was MISSED by direct "Ottoman Bank" search (Turkish title indexing issue)
- **What you learn**: Absence of evidence ≠ evidence of absence

## Workshop Components That Teach "Fishing"

### DISCOVER Module
- **Re-emphasize**: Bibliographic/full-text academic corpora
- **Official websites** and institutional sources
- **Other sources**: News, reports, grey literature
- **Google search** with ParseHub for structured extraction
- **What you learn**: Where to look and how to systematically collect

### COLLECT Module
- **OpenAlex API**: Hands-on query building
- **Data pipeline construction**: Scripts you can modify
- **What you learn**: How to build your own collection workflows

### ANALYZE Module
- **LLMs as a jury**: Using AI for systematic analysis
- **CLI tools mastery**: Command-line workflows
- **TANA × CLI integration**: Note-taking meets data processing
- **What you learn**: How to process and analyze at scale

## Key Teaching Moments

### 1. Tool Mastery Over Tool Dependence
- **Bad**: "Use this specific script for Ottoman Bank data"
- **Good**: "Here's how to modify the OpenAlex query for any institution"

### 2. Understanding Trade-offs
- **Speed vs. Comprehensiveness**: API queries vs. manual searches
- **Precision vs. Recall**: Exact phrases vs. broader terms
- **Language vs. Coverage**: English vs. multilingual searches

### 3. Building Intuition
- **When to trust automation**: High-volume, consistent tasks
- **When to intervene manually**: Edge cases, quality issues
- **How to verify results**: Cross-checking, sampling, validation

## The Real Value You Take Away

### Not Just:
- The specific datasets we create
- The exact scripts we provide
- The particular analyses we show

### But Rather:
- **Methodology**: How to approach similar research questions
- **Adaptability**: How to modify tools for your needs
- **Critical thinking**: How to evaluate and improve results
- **Independence**: Confidence to tackle new research challenges

## Examples in Practice

### Ottoman Bank Research
- **Fish**: "Here's data about Ottoman Bank"
- **Fishing**: "Here's how to query any historical institution in OpenAlex"

### CLI Tool Usage
- **Fish**: "Here's how to process this specific dataset"
- **Fishing**: "Here's how CLI tools work and how to chain them together"

### LLM Analysis
- **Fish**: "Here's what the AI found in this corpus"
- **Fishing**: "Here's how to design prompts and validation workflows"

## Success Metrics

You've learned to "fish" when you can:

1. **Modify our scripts** for your own research questions
2. **Combine tools** in new ways we didn't explicitly teach
3. **Troubleshoot problems** using documentation and experimentation
4. **Evaluate quality** of automated vs. manual approaches
5. **Teach others** the methods you've learned

## Bottom Line

This workshop is designed so that 6 months from now, when you have a new research question, you won't think:

> "I wish I had that specific script from the workshop"

Instead, you'll think:

> "I know how to build this workflow myself"

**That's the difference between giving fish and teaching to fish.**