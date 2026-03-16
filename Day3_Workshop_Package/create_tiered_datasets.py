#!/usr/bin/env python3
"""
Create tiered Ottoman Bank datasets for cost-effective annotation.

This script addresses the discovery that only 0.03% of chunks from the full-text
search actually mention "Ottoman Bank" in their abstracts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

def create_tiered_datasets(input_file: str):
    """Create three tiers of datasets based on relevance."""

    print("Loading full dataset...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    chunks = data['chunks']
    print(f"Total chunks loaded: {len(chunks):,}")

    # Define financial and Ottoman-related terms
    financial_terms = [
        'bank', 'banking', 'finance', 'financial', 'credit', 'loan', 'debt',
        'monetary', 'currency', 'capital', 'investment', 'bond', 'economic'
    ]

    ottoman_bank_terms = [
        'ottoman bank', 'imperial ottoman bank', 'banque impériale ottomane',
        'banque ottomane', 'ottoman imperial bank'
    ]

    # Tier 1: Direct mentions of Ottoman Bank
    print("\nCreating Tier 1: Direct Ottoman Bank mentions...")
    tier1_chunks = []
    for chunk in chunks:
        chunk_text_lower = chunk.get('chunk_text', '').lower()
        if any(term in chunk_text_lower for term in ottoman_bank_terms):
            tier1_chunks.append(chunk)

    # Tier 2: Ottoman + financial terms (likely relevant)
    print("Creating Tier 2: Ottoman + financial terms...")
    tier2_chunks = []
    for chunk in chunks:
        chunk_text_lower = chunk.get('chunk_text', '').lower()
        title_lower = chunk.get('paper_title', '').lower()

        # Check if Ottoman appears with financial terms
        has_ottoman = 'ottoman' in chunk_text_lower or 'ottoman' in title_lower
        has_financial = any(term in chunk_text_lower for term in financial_terms)

        if has_ottoman and has_financial:
            tier2_chunks.append(chunk)

    # Tier 2.5: High-confidence subset (Ottoman in title + financial terms in text)
    tier2_high_confidence = []
    for chunk in chunks:
        chunk_text_lower = chunk.get('chunk_text', '').lower()
        title_lower = chunk.get('paper_title', '').lower()

        ottoman_in_title = 'ottoman' in title_lower
        financial_in_text = any(term in chunk_text_lower for term in financial_terms)

        if ottoman_in_title and financial_in_text:
            tier2_high_confidence.append(chunk)

    # Tier 3: All Ottoman mentions (broader context)
    print("Creating Tier 3: All Ottoman mentions...")
    tier3_chunks = []
    for chunk in chunks:
        chunk_text_lower = chunk.get('chunk_text', '').lower()
        title_lower = chunk.get('paper_title', '').lower()

        if 'ottoman' in chunk_text_lower or 'ottoman' in title_lower:
            tier3_chunks.append(chunk)

    # Print statistics
    print("\n" + "="*60)
    print("DATASET STATISTICS")
    print("="*60)
    print(f"Original dataset: {len(chunks):,} chunks")
    print(f"Tier 1 (Direct mentions): {len(tier1_chunks):,} chunks ({len(tier1_chunks)*100/len(chunks):.2f}%)")
    print(f"Tier 2 (Ottoman + Finance): {len(tier2_chunks):,} chunks ({len(tier2_chunks)*100/len(chunks):.2f}%)")
    print(f"  - High confidence subset: {len(tier2_high_confidence):,} chunks")
    print(f"Tier 3 (Any Ottoman): {len(tier3_chunks):,} chunks ({len(tier3_chunks)*100/len(chunks):.2f}%)")

    # Cost estimates (assuming ~200 tokens per chunk, GPT-3.5 pricing)
    tokens_per_chunk = 200
    cost_per_1k_tokens = 0.002  # GPT-3.5-turbo

    print("\n" + "="*60)
    print("COST ESTIMATES (GPT-3.5-turbo)")
    print("="*60)
    for tier_name, tier_data in [
        ("Tier 1", tier1_chunks),
        ("Tier 2 (high conf)", tier2_high_confidence),
        ("Tier 2 (full)", tier2_chunks),
        ("Tier 3", tier3_chunks),
        ("Full dataset", chunks)
    ]:
        total_tokens = len(tier_data) * tokens_per_chunk
        cost = (total_tokens / 1000) * cost_per_1k_tokens
        print(f"{tier_name:20s}: ${cost:8.2f} ({len(tier_data):6,} chunks)")

    # Save datasets
    print("\n" + "="*60)
    print("SAVING DATASETS")
    print("="*60)

    datasets = [
        ('ottoman_bank_tier1_direct.json', tier1_chunks, 'Direct Ottoman Bank mentions'),
        ('ottoman_bank_tier2_high_confidence.json', tier2_high_confidence, 'Ottoman in title + financial terms'),
        ('ottoman_bank_tier2_finance.json', tier2_chunks, 'Ottoman + financial terms'),
        ('ottoman_bank_tier3_ottoman.json', tier3_chunks, 'All Ottoman mentions'),
    ]

    for filename, chunks_subset, description in datasets:
        output_data = {
            'metadata': {
                'source': input_file,
                'total_chunks': len(chunks_subset),
                'description': description,
                'estimated_cost_gpt35': f"${(len(chunks_subset) * tokens_per_chunk / 1000) * cost_per_1k_tokens:.2f}"
            },
            'chunks': chunks_subset
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Saved {filename}: {len(chunks_subset):,} chunks")

    # Create a sample for testing (10 chunks from tier 2 high confidence)
    print("\nCreating test sample...")
    test_sample = tier2_high_confidence[:10] if len(tier2_high_confidence) >= 10 else tier2_high_confidence

    test_data = {
        'metadata': {
            'source': 'Tier 2 high confidence',
            'total_chunks': len(test_sample),
            'description': 'Test sample for workshop demonstration'
        },
        'chunks': test_sample
    }

    with open('ottoman_bank_test_workshop.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

    print(f"Saved ottoman_bank_test_workshop.json: {len(test_sample)} chunks")

    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print("For the workshop:")
    print("1. Start with ottoman_bank_test_workshop.json for live demo")
    print("2. Use Tier 1 or Tier 2 high confidence for hands-on exercises")
    print("3. Explain Tier 3 as a challenge requiring relevance filtering")
    print("4. Show cost differences to emphasize importance of data curation")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Create tiered Ottoman Bank datasets')
    parser.add_argument('--input', '-i',
                       default='ottoman_bank_chunks_ALL.json',
                       help='Input file with all chunks')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file {args.input} not found")
        exit(1)

    create_tiered_datasets(args.input)