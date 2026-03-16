# Pending Tasks & Loose Ends for Analyze Module

## Immediate Tasks

### 1. Create Welcome/Schedule Slideshow
**Status**: NOT STARTED
**Requirements**:
- Opening slidedeck with workshop schedule
- Currently placeholder content
- Highlight key discovery points:
  - Bibliographic vs fulltext academic sources
  - Corpora resources
  - Official websites and other sources
  - Google search with ParseHub
  - LLMs as a jury for verification

### 2. Tana-CLI Integration Documentation
**Status**: NOT DOCUMENTED
**Key Points to Cover**:
- Integration with personal knowledge management tools
- If working in CLI with Tana hookup:
  - Automatically attaches notes to today's daily notes
  - Seamless workflow between CLI and PKM
- Benefits for research workflow
- Setup instructions

### 3. Fix CLI LLMs Slideshow Styling
**Status**: COMPLETED ✓
**Issue**: Was using wrong color scheme (purple gradients instead of dark blue)
**Resolution**: Changed to match dark blue theme

### 4. Complete Voice/Talk Feature Documentation
**Status**: PARTIALLY COMPLETE
**Current State**: Voice input mentioned in CLI slideshow (slide about voice messages)
**Still Needed**:
- Expand on voice interaction capabilities
- Add practical examples of voice commands
- Document voice-to-text workflow

## Content to Add/Verify

### Discovery Methods to Emphasize
**For Welcome/Overview Slideshow**:
1. **Bibliographic vs Fulltext Academic**
   - OpenAlex for bibliographic metadata
   - Distinction between citations and full content
   - When to use each approach

2. **Corpora Resources**
   - Pre-built text collections
   - Domain-specific databases
   - How to access and utilize

3. **Official Websites & Other Sources**
   - Government databases
   - Organization repositories
   - Primary source materials

4. **Google Search with ParseHub**
   - Web scraping capabilities
   - Structured data extraction
   - Automation possibilities

5. **LLMs as a Jury**
   - Cross-verification strategies
   - Multiple LLM consensus approaches
   - Fact-checking methodologies

### CLI LLMs Slideshow Content Checklist
- [x] Voice input capability mentioned
- [x] MD documentation requirements (CLAUDE.md, GEMINI.md, AGENTS.md) - DONE
- [ ] Integration with Tana and other PKM tools - NEEDS EXPANSION
- [x] Monorepo best practices - MENTIONED
- [x] Ancestor/descendant loading patterns - MENTIONED

### Workshop Philosophy Documentation
**Location**: Should be prominent in materials
**Key Points to Emphasize**:
1. "Teaching to Fish" approach - HOW to use tools, not just providing data
2. Two LLM interaction methods:
   - Programmatic (APIs)
   - Direct (text/images)
3. Verification strategies for citations and webpages

## Module Completeness Checklist

### Day 3: ANALYZE Module
- [x] Ottoman Bank Case Study (16 slides) - COMPLETE & VERIFIED
- [x] CLI LLMs Guide (16 slides) - NEEDS STYLING FIX
- [x] Deep Research Guide (24 slides) - COMPLETE & VERIFIED
- [x] WACKO Presentation (5 slides) - COMPLETE & VERIFIED
- [x] Main module index page with resources
- [x] Integration with main resources page

### Resources Organization
- [x] All slidedecks added to main resources page
- [x] Scripts and data files linked
- [x] Documentation properly referenced
- [ ] Technical help section needs expansion

## Future Enhancements (Post-Workshop)

### 1. Interactive Features
- Add live code execution in slides
- Implement progress tracking
- Create interactive exercises

### 2. Additional Content
- Video tutorials for complex topics
- More case studies beyond Ottoman Bank
- Extended API documentation

### 3. Integration Improvements
- Better Zotero integration examples
- Enhanced Tana workflow documentation
- More CLI tool comparisons

## Critical Reminders

### Always Verify
- Test on live GitHub Pages site
- Check all links work
- Verify styling consistency

### Dataset Integrity
- Ottoman Bank: 511 papers (quoted search)
- Galata additions: 85 unique papers
- Total: 596 papers for analysis

### Style Guidelines
- Dark blue gradients: #1a2a4a → #243655
- Text: White (#ffffff) with 0.95 opacity
- Headings: Cyan (#00ffff)
- Dimensions: 92-95% width, 88-92vh height

## Testing Requirements

Before marking module complete:
1. Run `python verify_final.py`
2. Check all navigation buttons work
3. Verify content fits on single slides
4. Test on different screen sizes
5. Confirm GitHub Pages deployment

## Notes for Instructor

### Key Teaching Points
1. Importance of quoted vs unquoted searches
2. How to verify data before analysis
3. CLI tools as research accelerators
4. LLM verification strategies

### Common Student Questions
1. "Why did we get different paper counts?"
   - Answer: Quoted vs unquoted search differences
2. "How do we know the LLM analysis is correct?"
   - Answer: Citation verification + source checking
3. "Can we talk to the CLI tools?"
   - Answer: Yes, voice input is supported

## Key Integration Points to Document

### Tana x CLI Integration
**Critical Feature**: When you work in CLI and have it hooked up to Tana:
- Automatically attaches the session notes to today's daily notes
- Creates proper backlinks and references
- Maintains context across tools
- Enables seamless research workflow

**Benefits**:
- Never lose track of what you worked on
- Automatic documentation of research process
- Cross-referenced knowledge base
- Time-stamped progress tracking

### Other PKM Integrations
- Obsidian integration possibilities
- Notion API connections
- Roam Research workflows
- LogSeq compatibility

## Priority Order for Completion

1. **URGENT**: Create Welcome/Schedule slideshow with discovery emphasis
2. **HIGH**: Document Tana-CLI integration fully
3. **HIGH**: Verify all content fits properly on slides
4. **MEDIUM**: Expand voice/talk documentation
5. **MEDIUM**: Add ParseHub tutorial/examples
6. **LOW**: Future enhancements