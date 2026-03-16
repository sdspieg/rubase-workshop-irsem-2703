# Module 2: Building Taxonomies - Exercise Guide

## 15-Minute Taxonomy Sprint

### Part 1: Manual Taxonomy Creation (7.5 minutes)

Build your own taxonomy from scratch to understand the fundamentals.

#### Step 1: Choose Your Domain
Pick something you know well:
- Your research topic
- A hobby (cooking, sports, gaming)
- Professional field
- Academic discipline

#### Step 2: Identify 3 Orthogonal Dimensions
Ask yourself: "What are 3 independent ways to categorize things in this domain?"

**Test for Orthogonality**: Can something be high on dimension A and low on dimension B? If yes, they're orthogonal!

Example for Coffee:
- Temperature (hot/cold)
- Strength (mild/strong)
- Origin (region)

#### Step 3: Create Your Hierarchy
For each dimension:
- Add 2 L2 elements (major categories)
- Add 2 taxa per L2 (specific examples)

#### Manual Template
```
Dimension 1: _____________
  L2a: _____________
    - Taxon: _____________
    - Taxon: _____________
  L2b: _____________
    - Taxon: _____________
    - Taxon: _____________

Dimension 2: _____________
  L2a: _____________
    - Taxon: _____________
    - Taxon: _____________
  L2b: _____________
    - Taxon: _____________
    - Taxon: _____________

Dimension 3: _____________
  L2a: _____________
    - Taxon: _____________
    - Taxon: _____________
  L2b: _____________
    - Taxon: _____________
    - Taxon: _____________
```

---

### Part 2: AI-Powered Taxonomy Generation (7.5 minutes)

Now let's see how AI can expand your taxonomy to 864 classification points!

#### The Magic Prompt

Copy this prompt and paste it into Claude or GPT-4:

```prompt
You are a domain expert creating a multi-dimensional taxonomy.

DOMAIN: [Your domain from Part 1]

Create a comprehensive taxonomy with:
- 5-9 orthogonal dimensions (HLTPs)
- Each HLTP has exactly 4 L2 elements
- Each L2 has exactly 3 L3 elements
- Each L3 has exactly 8 specific taxa

Output format: TSV (Tab-Separated Values) with columns:
HLTP | 2nd Level TE | 3rd Level TE | Taxon

Requirements:
✓ Dimensional independence - each dimension must be orthogonal
✓ Complete coverage - no gaps in the taxonomy
✓ Observable criteria - taxa must be identifiable
✓ No ambiguous terms - clear, specific language
✓ Consistent abstraction levels within each level

Start with these dimensions if relevant to the domain:
1. [Dimension 1 from your manual taxonomy]
2. [Dimension 2 from your manual taxonomy]
3. [Dimension 3 from your manual taxonomy]

Add additional orthogonal dimensions to reach 5-9 total.

Generate the complete taxonomy now.
```

#### Quick Python Script for Processing

Once you have your AI-generated taxonomy, you can process it:

```python
import pandas as pd
import io

# Paste your TSV output here
taxonomy_tsv = """
HLTP	2nd Level TE	3rd Level TE	Taxon
[Paste AI output here]
"""

# Load into DataFrame
df = pd.read_csv(io.StringIO(taxonomy_tsv), sep='\t')

# Quick stats
print(f"Total dimensions (HLTPs): {df['HLTP'].nunique()}")
print(f"Total L2 elements: {df['2nd Level TE'].nunique()}")
print(f"Total L3 elements: {df['3rd Level TE'].nunique()}")
print(f"Total taxa: {len(df)}")

# Save to file
df.to_csv('my_taxonomy.csv', index=False)
print("Taxonomy saved to my_taxonomy.csv")
```

---

## Comparison Checklist

After completing both parts, compare:

### Coverage
- [ ] Does the AI taxonomy cover aspects you missed?
- [ ] Are there dimensions you thought of that AI didn't?

### Orthogonality
- [ ] Are all AI dimensions truly independent?
- [ ] Did AI maintain better orthogonality than your manual version?

### Specificity
- [ ] Are the AI's taxa more specific or general than yours?
- [ ] Which provides better observable criteria?

### Practicality
- [ ] Which taxonomy would be easier to apply to real data?
- [ ] Which has better coverage of edge cases?

---

## Common Pitfalls to Avoid

### ❌ Don't Do This
- **Overlapping dimensions**: "Aggressive" appearing in multiple dimensions
- **Mixed abstraction levels**: "Nuclear weapons" (specific) under "Strategic" (abstract)
- **Ambiguous terms**: "Complex", "Advanced", "Sophisticated"
- **False orthogonality**: "Speed" and "Velocity" as separate dimensions

### ✅ Do This Instead
- **True independence**: Each dimension varies independently
- **Consistent levels**: All L2s at same abstraction level
- **Observable criteria**: "Uses Twitter" not "Digital native"
- **Clear terminology**: "Publication count > 50" not "Prolific"

---

## Share Your Results!

Post your most interesting dimension or surprising taxon discovery in the workshop chat!

**Discussion Prompts:**
1. What dimension did AI suggest that surprised you?
2. Which was harder: identifying dimensions or creating the hierarchy?
3. How would you validate this taxonomy with real data?

---

## Resources

- [Multi-Dimensional Taxonomy Framework Paper](https://example.com)
- [RuBase Dashboard](https://rumilspace.app) - See taxonomies in action
- [Workshop Slides](../modules/frame/index.html) - Today's presentation

---

*Remember: The goal isn't perfection - it's understanding how multi-dimensional thinking transforms analysis!*