# Workshop Branding Guide
## RuBase vs. StratBase: Strategic Brand Differentiation

---

## 🎯 Brand Strategy Overview

### Dual-Brand Purpose
We maintain two distinct but related workshop brands to maximize reach and appeal to different academic communities:

1. **RuBase** - For Russian, Eurasian, and area studies focused research
2. **StratBase** - For general strategic studies, international relations, and policy analysis

Both workshops use identical technical infrastructure and methodologies, but with tailored framing and examples.

---

## 📅 Upcoming Workshop Schedule & Branding

### Confirmed Workshops (2026)

| Date | Location | Institution | Brand | Status | Audience Focus |
|------|----------|------------|-------|--------|----------------|
| March 11-13 | Boston, USA | Fletcher School | RuBase | ✅ Completed | International relations, Russia/Eurasia |
| March 27, 2026 | Paris, France | IRSEM | StratBase | 🔄 Planning | Strategic studies, defense analysis |
| September 2026 | Astana, Kazakhstan | TBD | RuBase | 📋 Scheduled | Central Asian studies, regional analysis |
| September 2026 | Baku, Azerbaijan | TBD | RuBase | 📋 Scheduled | Caspian region, energy studies |
| October 2026 | Helsinki, Finland | TBD | RuBase | 📋 Scheduled | Nordic-Russian relations, Arctic studies |

### Branding Rationale by Location
- **Paris (IRSEM)**: StratBase - Broader strategic studies appeal for French defense institute
- **Central Asia/Caucasus**: RuBase - Regional focus, post-Soviet space expertise
- **Helsinki**: RuBase - Strong Russia/Baltic regional studies tradition

---

## 🎨 Brand Guidelines

### RuBase Workshops

#### Visual Identity
- **Primary Colors**: Cyan (#00ffff), Purple (#9400d3)
- **Logo Elements**: Eastern European/Eurasian motifs
- **Imagery**: Maps of Eurasia, Cyrillic text elements, regional symbols

#### Messaging Focus
- "Understanding Russia and Eurasia through AI-augmented research"
- Emphasis on area studies, regional expertise
- Examples from Russian/post-Soviet contexts
- Case studies: Russian military doctrine, Central Asian politics, energy diplomacy

#### Target Audience
- Area studies scholars
- Regional specialists
- Intelligence analysts focused on Eurasia
- Graduate students in Slavic/Eurasian studies

### StratBase Workshops

#### Visual Identity
- **Primary Colors**: Green (#00ff00), Yellow (#ffd700)
- **Logo Elements**: Global/strategic imagery
- **Imagery**: World maps, network diagrams, strategic frameworks

#### Messaging Focus
- "Strategic analysis powered by artificial intelligence"
- Emphasis on methodology, frameworks, decision-making
- Examples from global security, grand strategy
- Case studies: NATO operations, Indo-Pacific strategy, global governance

#### Target Audience
- Strategic studies scholars
- Policy analysts
- Military/defense researchers
- International relations generalists

---

## 🔧 Technical Implementation

### Configuration File Structure
Create a `workshop-config.json` in each workshop repository:

```json
{
  "brand": "RuBase|StratBase",
  "workshop": {
    "title": "RuBase Methods Workshop",
    "subtitle": "AI-Augmented Research on Russia & Eurasia",
    "institution": "Fletcher School",
    "location": "Boston, USA",
    "dates": "March 11-13, 2026",
    "language": "en",
    "timezone": "America/New_York"
  },
  "theme": {
    "primaryColor": "#00ffff",
    "secondaryColor": "#9400d3",
    "logo": "rubase-logo.svg",
    "favicon": "rubase-favicon.ico"
  },
  "content": {
    "examples": "russia-focused",
    "caseStudies": ["ottoman-bank", "russia-ukraine", "central-asia"],
    "datasets": "eurasian",
    "terminology": "area-studies"
  },
  "features": {
    "showArchives": true,
    "enableDownloads": true,
    "multiLanguage": false
  }
}
```

### Quick Brand Switch Script
Create `switch-brand.sh`:

```bash
#!/bin/bash
# Usage: ./switch-brand.sh [rubase|stratbase]

BRAND=$1

if [ "$BRAND" = "rubase" ]; then
    echo "Switching to RuBase branding..."
    sed -i 's/StratBase/RuBase/g' index.html
    sed -i 's/#00ff00/#00ffff/g' index.html
    sed -i 's/Strategic Analysis/Russia \& Eurasia Studies/g' index.html
    cp assets/logos/rubase-logo.svg logo.svg
elif [ "$BRAND" = "stratbase" ]; then
    echo "Switching to StratBase branding..."
    sed -i 's/RuBase/StratBase/g' index.html
    sed -i 's/#00ffff/#00ff00/g' index.html
    sed -i 's/Russia \& Eurasia Studies/Strategic Analysis/g' index.html
    cp assets/logos/stratbase-logo.svg logo.svg
else
    echo "Usage: ./switch-brand.sh [rubase|stratbase]"
fi
```

---

## 📋 Workshop Customization Checklist

### For RuBase Workshops
- [ ] Update title to "RuBase Methods Workshop - [Institution]"
- [ ] Set primary color to cyan (#00ffff)
- [ ] Add regional maps/imagery
- [ ] Include Russia/Eurasia case studies
- [ ] Emphasize area studies applications
- [ ] Add Cyrillic examples where appropriate
- [ ] Include regional datasets (OpenAlex Russia queries)

### For StratBase Workshops
- [ ] Update title to "StratBase Methods Workshop - [Institution]"
- [ ] Set primary color to green (#00ff00)
- [ ] Add global strategy imagery
- [ ] Include diverse international case studies
- [ ] Emphasize strategic frameworks
- [ ] Focus on policy applications
- [ ] Include global datasets (OpenAlex broad queries)

---

## 🌍 Language Considerations

### RuBase Workshops
- Consider bilingual materials (English/Russian) for:
  - Astana workshop (English/Russian/Kazakh)
  - Baku workshop (English/Russian/Azerbaijani)
  - Helsinki workshop (English/Finnish/Russian)
- Include Cyrillic script examples
- Reference Russian-language sources

### StratBase Workshops
- Primarily English
- Paris IRSEM: Consider French translations for key slides
- Adapt terminology for local contexts

---

## 📊 Marketing & Outreach

### RuBase Marketing Channels
- Area studies departments
- Slavic/Eurasian studies programs
- Regional studies associations (ASEEES, CESS)
- Intelligence/security studies programs with regional focus
- Think tanks focused on Russia/Eurasia

### StratBase Marketing Channels
- Strategic studies departments
- International relations programs
- Policy schools
- Defense universities
- General IR associations (ISA, APSA)

### Unified Messaging
Both brands share core value propositions:
1. Cutting-edge AI/LLM integration
2. Hands-on, practical methodology
3. Open-source tools and approaches
4. Research productivity enhancement
5. Academic rigor with technical innovation

---

## 🎓 Content Adaptation Examples

### Case Study Adaptations

#### RuBase Version
**Ottoman Bank Case Study**
- Frame as: "Analyzing Russian financial influence in the Ottoman Empire"
- Highlight: Russian-Ottoman economic competition
- Examples: Russo-Turkish wars' economic dimensions

#### StratBase Version
**Ottoman Bank Case Study**
- Frame as: "Multi-polar competition in emerging markets"
- Highlight: Great power rivalry through financial instruments
- Examples: Contemporary parallels with BRI, development finance

### Module Framing

#### RuBase: Day 1 - DISCOVER
"Discovering hidden Russian & Eurasian research sources"
- OpenAlex queries for Cyrillic content
- Regional academic databases
- Post-Soviet scholarly networks

#### StratBase: Day 1 - DISCOVER
"Discovering global strategic research landscapes"
- OpenAlex for international relations
- Defense and security databases
- Policy research repositories

---

## 💼 Institutional Partnerships

### RuBase Partner Profiles
- **Regional Studies Centers**: Focus on area expertise
- **Language Departments**: Emphasize multilingual research
- **Intelligence Programs**: Regional analytical capabilities
- **Think Tanks**: Russia/Eurasia focused institutions

### StratBase Partner Profiles
- **Policy Schools**: Broad strategic analysis
- **IR Departments**: Theoretical and applied research
- **Defense Institutions**: Strategic planning and analysis
- **International Organizations**: Global governance focus

---

## 🚀 Implementation Timeline

### Phase 1: Immediate (March 2026)
- [x] Create dual branding in generic repository
- [x] Document workshop schedule
- [ ] Design StratBase logo variant
- [ ] Prepare IRSEM workshop materials

### Phase 2: Q2 2026 (April-June)
- [ ] Launch IRSEM workshop (StratBase)
- [ ] Develop brand-specific marketing materials
- [ ] Create institutional partnership templates

### Phase 3: Q3 2026 (July-September)
- [ ] Prepare Central Asian workshops (RuBase)
- [ ] Develop multilingual materials
- [ ] Create regional case studies
- [ ] Build local partnerships

### Phase 4: Q4 2026 (October-December)
- [ ] Helsinki workshop execution
- [ ] Year-end evaluation
- [ ] 2027 planning with brand differentiation
- [ ] Scale based on brand performance

---

## 📈 Success Metrics by Brand

### RuBase Success Indicators
- Attendance from area studies programs
- Citations in regional studies research
- Adoption by Russia/Eurasia focused institutions
- Integration with regional databases
- Multilingual material usage

### StratBase Success Indicators
- Broader institutional adoption
- Cross-disciplinary attendance
- Policy impact and citations
- Integration with strategic planning processes
- Executive education opportunities

---

## 🔄 Brand Evolution Strategy

### Short Term (2026)
- Test dual branding with 5-6 workshops
- Gather feedback on brand differentiation
- Measure audience response and growth
- Refine positioning based on data

### Medium Term (2027)
- Potentially create distinct websites
- Develop brand-specific feature sets
- Build specialized communities
- Create differentiated certification programs

### Long Term (2028+)
- Consider spinning off as separate programs
- Develop brand-specific tools and platforms
- Create specialized research networks
- Establish independent funding streams

---

## 📝 Quick Reference

### When to Use RuBase
- Institution has strong area studies focus
- Regional or country-specific audience
- Emphasis on language and cultural expertise
- Post-Soviet or Eurasian geographic focus
- Intelligence/security community connections

### When to Use StratBase
- Broader international relations audience
- Policy school or think tank setting
- Emphasis on frameworks and methodology
- Global or comparative focus
- Executive or professional education context

### When to Use Both
- Large, diverse institutions
- Conferences with multiple tracks
- Online workshops with varied audience
- Partnership with multiple departments

---

## 🛠️ Technical Notes

### Repository Naming Convention
```
rubase-workshop-[institution]-[YYMM]    # For RuBase branded
stratbase-workshop-[institution]-[YYMM]  # For StratBase branded
workshop-[institution]-[YYMM]           # For dual-branded
```

### Archive System Updates
The generic workshop should maintain both brand options:
1. Header shows "RuBase/StratBase Methods Workshop"
2. Archive selector indicates brand for each workshop
3. Color coding: Cyan for RuBase, Green for StratBase

### Future Development
Consider developing a configuration wizard that automatically:
1. Applies appropriate branding
2. Swaps case studies and examples
3. Adjusts color schemes
4. Updates terminology and framing
5. Generates appropriate marketing materials

---

*Document Created: March 15, 2026*
*Version: 1.0*
*Next Review: March 2026 (Post-IRSEM)*