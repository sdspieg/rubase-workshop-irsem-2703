# Taxonomy Comparison: Transparent Battlefield vs Ottoman Bank

## Methodological Parallels

Both systems implement the Multi-Dimensional Taxonomy Development Framework (MDTDF) with domain-specific adaptations.

### Framework Structure

| Component | Transparent Battlefield | Ottoman Bank |
|-----------|------------------------|--------------|
| **HLTPs** | 6 pillars | 6 pillars |
| **Total Taxa** | ~50 | 66 |
| **Hierarchy** | 4 levels (HLTP → L2 → L3 → Taxon) | 4 levels (HLTP → L2 → L3 → Taxon) |
| **Format** | TSV with pipe delimiters | TSV with tab delimiters |

### High-Level Topic Pillars Mapping

#### Military → Financial Domain Translation

**Transparent Battlefield HLTPs:**
1. ISR (Intelligence, Surveillance, Reconnaissance)
2. Kill Chain Operations
3. Command & Control
4. Force Protection
5. Logistics & Support
6. Information Operations

**Ottoman Bank HLTPs:**
1. Financial Operations (≈ Kill Chain Operations - core mission)
2. Institutional Structure (≈ Command & Control - governance)
3. Historical Context (temporal dimension - new)
4. Economic Impact (≈ Force Protection - systemic effects)
5. Political Dimensions (≈ Information Operations - influence)
6. Social and Cultural (≈ Logistics & Support - enabling factors)

## Technical Implementation Comparison

### Annotation Pipeline

```python
# Transparent Battlefield
- Uses GPT-5-mini for classification
- Async processing with asyncio
- Tiered relevance filtering (3 tiers)
- Focus on entity extraction + classification

# Ottoman Bank
- Multi-LLM support (Claude, OpenAI, Gemini)
- Synchronous batch processing
- Binary relevance filtering
- Pure taxonomic classification
```

### Relevance Filtering Strategy

**Transparent Battlefield Tiers:**
- **Tier 1 (Core)**: Direct military operations
- **Tier 2 (High)**: Strategic context
- **Tier 3 (Partial)**: Peripheral mentions

**Ottoman Bank Relevance:**
- **Directly Relevant**: Bank operations, governance
- **Contextually Relevant**: Economic reforms, financial imperialism
- **Not Relevant**: Separate mentions, pure politics

### Cost Optimization

| Strategy | Transparent Battlefield | Ottoman Bank |
|----------|------------------------|--------------|
| Pre-filtering | 3-tier military relevance | Ottoman Bank mention filter |
| Batch size | 10 chunks | 5 chunks |
| Test mode | Sample subset | 10-chunk test |
| Fallback | None | Keyword matching |
| LLM choice | GPT-5-mini only | Multiple providers |

## Data Processing Differences

### Input Sources

**Transparent Battlefield:**
- Russian/Ukrainian documents
- Military reports and analysis
- Real-time conflict data
- Multi-lingual corpus

**Ottoman Bank:**
- OpenAlex academic papers
- Historical documents
- 67,238 chunks from 21,397 papers
- Year range: 1766-2026

### Chunk Processing

```python
# Both systems:
- Chunk size: 500-5000 characters
- Overlap: 20%
- Metadata preservation

# Differences:
- TB: Focus on entity preservation
- OB: Abstract reconstruction from inverted index
```

## Taxonomy Depth Analysis

### Granularity Comparison

**Transparent Battlefield** emphasizes:
- Weapon systems and platforms
- Tactical operations
- Real-time intelligence
- Kinetic effects

**Ottoman Bank** emphasizes:
- Financial instruments
- Institutional evolution
- Historical periods
- Socio-economic impacts

### Example Parallel Taxa

| Domain Function | Transparent Battlefield | Ottoman Bank |
|-----------------|------------------------|--------------|
| **Core Operations** | "Kinetic strikes" | "Commercial loans to merchants" |
| **Intelligence** | "ISR platforms" | "Statistical data collection" |
| **Infrastructure** | "C2 systems" | "Railway construction financing" |
| **Foreign Relations** | "Coalition operations" | "European financial imperialism" |
| **Personnel** | "Force composition" | "European staff and expertise" |

## Prompt Engineering Comparison

### Structure

Both prompts follow similar architecture:
1. Role definition
2. Context explanation
3. Relevance criteria
4. Full taxonomy listing
5. Output format specification

### Key Differences

**Transparent Battlefield:**
```
- Military expertise assumed
- Entity extraction required
- Confidence scores optional
- Focus on operational relevance
```

**Ottoman Bank:**
```
- Historical expertise provided
- Pure classification
- Confidence scores mandatory (1-10)
- Explanation required for all decisions
```

## Performance Metrics

### Processing Scale

| Metric | Transparent Battlefield | Ottoman Bank |
|--------|------------------------|--------------|
| Documents | Continuous stream | 21,397 papers |
| Chunks | Variable | 67,238 |
| Languages | 2+ | Multiple |
| Time range | 2022-present | 1766-2026 |
| Update frequency | Daily | One-time/periodic |

### Cost Estimates

**Transparent Battlefield:**
- Daily limit: 10M tokens
- Cost: Variable based on stream

**Ottoman Bank (full corpus):**
- Total tokens: ~13.4M
- Estimated cost: $20-27
- Test mode: <$1

## Innovation Highlights

### Transparent Battlefield Innovations:
1. Real-time annotation pipeline
2. Multi-tier relevance filtering
3. Entity-taxonomy linking
4. Async high-throughput processing

### Ottoman Bank Adaptations:
1. Historical periodization taxonomy
2. Multi-LLM fallback system
3. Abstract reconstruction from inverted index
4. Domain-specific relevance criteria

## Workshop Integration Value

This comparison demonstrates:

1. **Domain Transferability**: Military → Financial history
2. **Methodological Consistency**: MDTDF framework preservation
3. **Technical Flexibility**: Adapting to data sources
4. **Cost Management**: Different optimization strategies
5. **Scalability**: From real-time to batch processing

## Key Takeaways

1. **Taxonomy Structure**: 6-HLTP framework transfers across domains
2. **Relevance Filtering**: Critical for cost management in both
3. **LLM Strategy**: Domain complexity drives model choice
4. **Batch Processing**: Optimal sizes vary by use case
5. **Documentation**: Comprehensive prompts essential for consistency

## Recommended Workshop Flow

1. **Show Transparent Battlefield**: Original military application
2. **Explain MDTDF**: Universal framework principles
3. **Demonstrate Adaptation**: Ottoman Bank transformation
4. **Highlight Innovations**: Domain-specific optimizations
5. **Practice Exercise**: Participants create their own domain taxonomy

This comparison provides concrete evidence that the MDTDF framework and annotation pipeline can be successfully adapted across radically different domains while maintaining methodological rigor.