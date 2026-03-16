#!/usr/bin/env python3
"""
Step 1: Extract and Chunk Abstracts from JSON Corpus
Author: RuBase Workshop Team
Date: March 13, 2026

This script:
1. Loads your JSON corpus file (from Lens.org or OpenAlex)
2. Extracts titles and abstracts
3. Chunks abstracts into manageable pieces for LLM processing
4. Saves chunks to a new JSON file for next steps

Usage:
    python 01_extract_chunks.py --input ottoman_bank_openalex.json
"""

import json
import os
from typing import List, Dict, Any
import argparse
from datetime import datetime

# Configuration - Adjust these as needed
CHUNK_SIZE = 500  # Characters per chunk
OVERLAP_SIZE = 50  # Character overlap between chunks
MIN_CHUNK_SIZE = 100  # Minimum chunk size to keep

def load_corpus(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON corpus file from Lens or OpenAlex"""
    print(f"📂 Loading corpus from: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            papers = data
        elif isinstance(data, dict):
            # OpenAlex format
            if 'results' in data:
                papers = data['results']
            # Lens format
            elif 'data' in data:
                papers = data['data']
            else:
                papers = [data]
        else:
            raise ValueError("Unexpected JSON structure")

        print(f"✅ Loaded {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return []

def extract_text_from_paper(paper: Dict[str, Any]) -> Dict[str, str]:
    """Extract title and abstract from paper object

    Handles multiple formats:
    - Lens.org format (abstract, abstract_text)
    - OpenAlex format (abstract_inverted_index)
    - Generic formats (Abstract, summary)
    """

    # Try different field names for title
    title = (paper.get('title') or
             paper.get('display_name') or
             paper.get('Title') or
             "No title")

    # Try different field names for abstract
    abstract = (paper.get('abstract') or
                paper.get('abstract_text') or
                paper.get('Abstract') or
                paper.get('summary') or
                "")

    # For OpenAlex, handle abstract_inverted_index format
    # This is the PRIMARY format for OpenAlex abstracts
    if not abstract and 'abstract_inverted_index' in paper:
        inverted = paper.get('abstract_inverted_index', {})
        if inverted:
            try:
                # Find max position to create array
                max_pos = max(max(positions) for positions in inverted.values() if positions)
                words = [''] * (max_pos + 1)
                for word, positions in inverted.items():
                    for pos in positions:
                        if pos < len(words):  # Safety check
                            words[pos] = word
                abstract = ' '.join(words)
            except (ValueError, TypeError, IndexError) as e:
                print(f"Warning: Failed to parse inverted index: {e}")
                abstract = ""

    # Get ID
    paper_id = (paper.get('id') or
                paper.get('lens_id') or
                paper.get('doi') or
                f"paper_{hash(title)}")

    return {
        'id': str(paper_id),
        'title': title,
        'abstract': abstract
    }

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks"""
    if chunk_size is None:
        chunk_size = CHUNK_SIZE
    if overlap is None:
        overlap = OVERLAP_SIZE

    if not text or len(text) < MIN_CHUNK_SIZE:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.7:  # If period is in last 30% of chunk
                end = start + last_period + 1
                chunk = text[start:end]

        if len(chunk) >= MIN_CHUNK_SIZE:
            chunks.append(chunk.strip())

        start = end - overlap if end < text_length else text_length

    return chunks

def process_corpus(papers: List[Dict[str, Any]], chunk_size: int = None, overlap: int = None) -> List[Dict[str, Any]]:
    """Process all papers and create chunks"""
    all_chunks = []
    papers_processed = 0
    chunks_created = 0
    papers_skipped = 0

    print("\n🔄 Processing papers...")

    for i, paper in enumerate(papers):
        if i % 50 == 0 and i > 0:
            print(f"  Processed {i}/{len(papers)} papers...")

        # Extract text
        paper_data = extract_text_from_paper(paper)

        if not paper_data['abstract']:
            papers_skipped += 1
            continue

        # Create chunks
        abstract_chunks = chunk_text(paper_data['abstract'], chunk_size, overlap)

        # Store each chunk with metadata
        for chunk_idx, chunk in enumerate(abstract_chunks):
            chunk_record = {
                'chunk_id': f"{paper_data['id']}_chunk_{chunk_idx}",
                'paper_id': paper_data['id'],
                'paper_title': paper_data['title'],
                'chunk_index': chunk_idx,
                'total_chunks': len(abstract_chunks),
                'chunk_text': chunk,
                'chunk_length': len(chunk)
            }
            all_chunks.append(chunk_record)
            chunks_created += 1

        papers_processed += 1

    print(f"\n📊 Statistics:")
    print(f"  Papers with abstracts: {papers_processed}")
    print(f"  Papers without abstracts: {papers_skipped}")
    print(f"  Chunks created: {chunks_created}")
    if papers_processed > 0:
        print(f"  Avg chunks per paper: {chunks_created/papers_processed:.1f}")
    else:
        print(f"  Avg chunks per paper: N/A (no papers with abstracts)")

    return all_chunks

def save_chunks(chunks: List[Dict[str, Any]], output_file: str, chunk_size: int, overlap_size: int):
    """Save chunks to JSON file"""
    print(f"\n💾 Saving {len(chunks)} chunks to: {output_file}")

    output_data = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'total_chunks': len(chunks),
            'chunk_size': chunk_size,
            'overlap_size': overlap_size
        },
        'chunks': chunks
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Calculate file size
    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    print(f"✅ Saved successfully ({file_size:.2f} MB)")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Extract and chunk abstracts from corpus')
    parser.add_argument('--input', '-i',
                       help='Input JSON file path',
                       default='corpus.json')
    parser.add_argument('--output', '-o',
                       help='Output chunks file path',
                       default='chunks.json')
    parser.add_argument('--chunk-size', '-c',
                       type=int,
                       help=f'Characters per chunk (default: {CHUNK_SIZE})',
                       default=CHUNK_SIZE)
    parser.add_argument('--overlap', '-v',
                       type=int,
                       help=f'Overlap between chunks (default: {OVERLAP_SIZE})',
                       default=OVERLAP_SIZE)
    parser.add_argument('--test',
                       action='store_true',
                       help='Test mode: process only first 10 papers')

    args = parser.parse_args()

    print("=" * 60)
    print("📝 STEP 1: EXTRACT AND CHUNK ABSTRACTS")
    print("=" * 60)

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found!")
        print("\n💡 Tips:")
        print("  - Make sure you're in the right directory")
        print("  - Check if your corpus file has a different name")
        print("  - Use --input flag to specify the file path")
        return

    # Process corpus
    papers = load_corpus(args.input)
    if not papers:
        print("❌ No papers found in corpus!")
        return

    # Limit papers in test mode
    if args.test:
        papers = papers[:10]
        print(f"🧪 TEST MODE: Processing only first 10 papers")

    chunks = process_corpus(papers, args.chunk_size, args.overlap)
    if not chunks:
        print("❌ No chunks created! Papers may not have abstracts.")
        print("   Check if your corpus contains abstract data.")
        return

    # Save results
    save_chunks(chunks, args.output, args.chunk_size, args.overlap)

    print("\n🎉 Success! Next step: Run 02_relevance_filter.py")
    print(f"   python 02_relevance_filter.py --input {args.output}")

if __name__ == "__main__":
    main()