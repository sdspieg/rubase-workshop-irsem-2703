# Critical Instructions for Claude

## Verification Habits
1. **ALWAYS VERIFY FIRST** - test changes before claiming they work
2. **ITERATE until 100% correct** - don't stop at "good enough"
3. **Use screenshots/Playwright** to verify visual changes
4. **Check live site**, not just local files
5. **If user says something isn't right**, verify and fix immediately

## Project Overview
This is the RuBase workshop materials for Fletcher School presentation, focusing on using OpenAlex and LLMs for academic research.

## Key Components
- Day 1: BUILD - Workshop setup and basics
- Day 2: COLLECT - OpenAlex data collection
- Day 3: ANALYZE - LLM analysis and visualization

## Testing Commands
For verifying slide presentations:
```python
python verify_final.py  # Full verification
python verify_buttons.py  # Button verification
```

## Important Files
- modules/analyze/ottoman-bank-case-study.html - Case study presentation
- modules/analyze/cli-llms-guide.html - CLI LLMs comprehensive guide
- Day3_Workshop_Package/ - All workshop materials and scripts

## Style Guidelines
- Use vibrant gradient backgrounds for slides
- Ensure all content fits within viewport (92% width, 88vh height)
- Test navigation on all slide presentations
- Verify responsive design at different screen sizes