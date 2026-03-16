#!/usr/bin/env python3
"""
Extract and chunk full text from GROBID-parsed PDFs.
Creates chunks that preserve Ottoman Bank mentions with context.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
FULLTEXT_DIR = Path("ottoman_fulltext")
OUTPUT_FILE = "ottoman_bank_fulltext_chunks.json"
CHUNK_SIZE = 1000  # characters
OVERLAP_SIZE = 100  # characters
MIN_CHUNK_SIZE = 200  # minimum chunk size

# Ottoman Bank related terms
OTTOMAN_BANK_TERMS = [
    'ottoman bank',
    'imperial ottoman bank',
    'banque impériale ottomane',
    'banque ottomane',
    'ottoman imperial bank',
    'bank-ı osmanî',
    'bank-i osmani'
]

def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters for matching
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.strip().lower()

def find_ottoman_mentions(text: str) -> List[Tuple[int, int, str]]:
    """Find all Ottoman Bank mentions in text."""
    mentions = []
    text_lower = text.lower()

    for term in OTTOMAN_BANK_TERMS:
        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(term, start)
            if pos == -1:
                break
            mentions.append((pos, pos + len(term), term))
            start = pos + 1

    # Sort by position
    mentions.sort(key=lambda x: x[0])
    return mentions

def smart_chunk_text(text: str, paper_id: str, chunk_size: int = CHUNK_SIZE,
                     overlap: int = OVERLAP_SIZE) -> List[Dict]:
    """
    Create smart chunks that preserve Ottoman Bank mentions.
    Tries to keep mentions in the middle of chunks for context.
    """
    chunks = []
    mentions = find_ottoman_mentions(text)

    if not text:
        return chunks

    # If we have Ottoman Bank mentions, create chunks around them
    if mentions:
        covered_positions = set()

        for mention_start, mention_end, term in mentions:
            # Check if this mention is already covered
            if mention_start in covered_positions:
                continue

            # Calculate chunk boundaries to center the mention
            padding = (chunk_size - (mention_end - mention_start)) // 2
            chunk_start = max(0, mention_start - padding)
            chunk_end = min(len(text), mention_end + padding)

            # Extend to word boundaries
            while chunk_start > 0 and text[chunk_start-1] not in ' \n\t':
                chunk_start -= 1
            while chunk_end < len(text) and text[chunk_end] not in ' \n\t':
                chunk_end += 1

            chunk_text = text[chunk_start:chunk_end].strip()

            if len(chunk_text) >= MIN_CHUNK_SIZE:
                chunks.append({
                    'chunk_text': chunk_text,
                    'chunk_start': chunk_start,
                    'chunk_end': chunk_end,
                    'ottoman_mention': term,
                    'mention_position': mention_start - chunk_start
                })

                # Mark positions as covered
                for pos in range(chunk_start, chunk_end):
                    covered_positions.add(pos)

    # Also create regular chunks for full coverage
    position = 0
    regular_chunk_index = 0

    while position < len(text):
        chunk_end = min(position + chunk_size, len(text))

        # Extend to word boundary
        while chunk_end < len(text) and chunk_end > position and text[chunk_end] not in ' \n\t':
            chunk_end += 1

        chunk_text = text[position:chunk_end].strip()

        if len(chunk_text) >= MIN_CHUNK_SIZE:
            # Check if this chunk contains Ottoman Bank mentions
            chunk_mentions = find_ottoman_mentions(chunk_text)

            chunks.append({
                'chunk_text': chunk_text,
                'chunk_start': position,
                'chunk_end': chunk_end,
                'has_ottoman_mention': len(chunk_mentions) > 0,
                'ottoman_mentions': [m[2] for m in chunk_mentions] if chunk_mentions else [],
                'regular_chunk': True,
                'regular_chunk_index': regular_chunk_index
            })
            regular_chunk_index += 1

        # Move position with overlap
        position += chunk_size - overlap
        if position >= len(text) - MIN_CHUNK_SIZE:
            break

    return chunks

def process_fulltext_files():
    """Process all GROBID-extracted full texts."""

    # Get all parsed JSON files
    json_files = list(FULLTEXT_DIR.glob("*.json"))
    logging.info(f"Found {len(json_files):,} parsed full-text files")

    if not json_files:
        print(f"No parsed files found in {FULLTEXT_DIR}")
        print("Please run grobid_parse_pdfs.py first")
        return

    all_chunks = []
    stats = {
        'total_papers': 0,
        'papers_with_mentions': 0,
        'total_chunks': 0,
        'chunks_with_mentions': 0,
        'mention_counts': Counter(),
        'total_text_length': 0
    }

    # Process each file
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        paper_id = data.get('paper_id', json_file.stem)
        full_text = data.get('full_text', '')

        if not full_text:
            continue

        stats['total_papers'] += 1
        stats['total_text_length'] += len(full_text)

        # Find mentions in full paper
        paper_mentions = find_ottoman_mentions(full_text)
        if paper_mentions:
            stats['papers_with_mentions'] += 1
            for _, _, term in paper_mentions:
                stats['mention_counts'][term] += 1

        # Create chunks
        chunks = smart_chunk_text(full_text, paper_id)

        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk['paper_id'] = paper_id
            chunk['paper_title'] = data.get('title', '')
            chunk['chunk_id'] = f"{paper_id}_chunk_{i}"
            chunk['chunk_index'] = i
            chunk['total_chunks'] = len(chunks)
            chunk['source'] = 'fulltext'

            # Count mentions
            if chunk.get('has_ottoman_mention') or chunk.get('ottoman_mention'):
                stats['chunks_with_mentions'] += 1

        all_chunks.extend(chunks)
        stats['total_chunks'] += len(chunks)

        # Progress update
        if stats['total_papers'] % 100 == 0:
            logging.info(f"Processed {stats['total_papers']:,} papers, "
                        f"created {stats['total_chunks']:,} chunks, "
                        f"found {stats['papers_with_mentions']:,} papers with mentions")

    # Sort chunks by relevance (Ottoman mentions first)
    all_chunks.sort(key=lambda x: (
        not (x.get('ottoman_mention') or x.get('has_ottoman_mention', False)),
        x.get('paper_id', ''),
        x.get('chunk_index', 0)
    ))

    # Create output
    output_data = {
        'metadata': {
            'source': 'GROBID-extracted full text',
            'total_papers': stats['total_papers'],
            'papers_with_mentions': stats['papers_with_mentions'],
            'total_chunks': stats['total_chunks'],
            'chunks_with_mentions': stats['chunks_with_mentions'],
            'chunk_size': CHUNK_SIZE,
            'overlap_size': OVERLAP_SIZE,
            'total_text_length': stats['total_text_length']
        },
        'mention_statistics': dict(stats['mention_counts']),
        'chunks': all_chunks
    }

    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "="*60)
    print("FULL-TEXT CHUNK EXTRACTION COMPLETE")
    print("="*60)
    print(f"Papers processed: {stats['total_papers']:,}")
    print(f"Papers with Ottoman Bank mentions: {stats['papers_with_mentions']:,} "
          f"({stats['papers_with_mentions']*100/stats['total_papers']:.1f}%)")
    print(f"Total chunks created: {stats['total_chunks']:,}")
    print(f"Chunks with Ottoman Bank mentions: {stats['chunks_with_mentions']:,} "
          f"({stats['chunks_with_mentions']*100/stats['total_chunks']:.1f}%)")
    print(f"Total text processed: {stats['total_text_length']/1e6:.1f} million characters")

    print("\nOttoman Bank mention frequencies:")
    for term, count in stats['mention_counts'].most_common():
        print(f"  '{term}': {count:,} occurrences")

    print(f"\nChunks saved to: {OUTPUT_FILE}")

    # Create tiered datasets for annotation
    create_tiered_fulltext_datasets(all_chunks)

def create_tiered_fulltext_datasets(chunks: List[Dict]):
    """Create tiered datasets from full-text chunks."""

    # Tier 1: Chunks with direct Ottoman Bank mentions
    tier1 = [c for c in chunks if c.get('ottoman_mention') or c.get('has_ottoman_mention')]

    # Tier 2: Sample of chunks from papers with mentions
    papers_with_mentions = set(c['paper_id'] for c in tier1)
    tier2 = []
    for paper_id in papers_with_mentions:
        paper_chunks = [c for c in chunks if c['paper_id'] == paper_id]
        # Take up to 10 chunks per paper
        tier2.extend(paper_chunks[:10])

    # Remove duplicates
    tier2_ids = set(c['chunk_id'] for c in tier2)
    tier2 = [c for c in tier2 if c['chunk_id'] in tier2_ids]

    # Tier 3: Random sample of all chunks
    tier3_sample = chunks[::100]  # Every 100th chunk

    print("\nCreating tiered datasets:")
    print(f"  Tier 1 (Direct mentions): {len(tier1):,} chunks")
    print(f"  Tier 2 (Papers with mentions): {len(tier2):,} chunks")
    print(f"  Tier 3 (Sample): {len(tier3_sample):,} chunks")

    # Save tiered datasets
    datasets = [
        ('ottoman_fulltext_tier1_mentions.json', tier1, 'Direct Ottoman Bank mentions from full text'),
        ('ottoman_fulltext_tier2_papers.json', tier2, 'All chunks from papers with mentions'),
        ('ottoman_fulltext_tier3_sample.json', tier3_sample, 'Sample of all chunks')
    ]

    for filename, data, description in datasets:
        output = {
            'metadata': {
                'description': description,
                'total_chunks': len(data),
                'source': 'GROBID full-text extraction'
            },
            'chunks': data
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"  Saved: {filename}")

if __name__ == "__main__":
    process_fulltext_files()