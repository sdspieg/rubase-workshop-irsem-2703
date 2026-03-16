#!/usr/bin/env python3
"""
Comprehensive multi-taxonomy annotation script.
Annotates chunks against ALL taxa in a taxonomy, providing confidence scores for each.

This script is designed for exhaustive taxonomic analysis where you want to know
how each chunk relates to every possible taxon in your taxonomy.
"""

import json
import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime

# Configuration
DEFAULT_MODEL = "claude-3-haiku-20240307"  # Fast and efficient
BATCH_SIZE = 5  # Process 5 chunks at a time
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 0.2  # seconds between API calls

def load_taxonomy(taxonomy_file: str) -> Dict[str, List[str]]:
    """Load taxonomy from TSV file and return structured format."""
    taxonomy = {}
    all_taxa = []
    hltp_structure = defaultdict(lambda: defaultdict(list))

    with open(taxonomy_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        header = lines[0].strip()

        for line in lines[1:]:  # Skip header
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                hltp, level2, level3, taxon = parts[:4]

                # Create full hierarchical label
                full_label = f"{hltp} > {level2} > {level3} > {taxon}"
                all_taxa.append(full_label)

                # Store in hierarchical structure
                if hltp not in taxonomy:
                    taxonomy[hltp] = []
                taxonomy[hltp].append({
                    'level2': level2,
                    'level3': level3,
                    'taxon': taxon,
                    'full_label': full_label
                })

                hltp_structure[hltp][level2].append(taxon)

    print(f"✓ Loaded taxonomy with {len(taxonomy)} HLTPs and {len(all_taxa)} total taxa")

    return taxonomy, all_taxa, hltp_structure

def create_annotation_prompt(taxonomy: Dict, all_taxa: List[str]) -> str:
    """Create a comprehensive annotation prompt for all taxa."""

    prompt = """You are an expert taxonomic classifier. Your task is to analyze a text chunk and provide confidence scores for EVERY taxon in the taxonomy.

# Instructions

1. Read the text chunk carefully
2. For EACH taxon listed below, provide a confidence score (0-100):
   - 0 = Completely unrelated
   - 1-20 = Very unlikely
   - 21-40 = Unlikely but possible
   - 41-60 = Moderately relevant
   - 61-80 = Likely relevant
   - 81-100 = Highly relevant

3. Be generous with low scores (1-20) for taxa that might have indirect relevance
4. Reserve high scores (80+) only for clear, direct relevance
5. Most taxa will score 0 for most chunks - this is expected

# Taxonomy to Score

Please provide a confidence score (0-100) for each of these taxa:

"""

    # Add all taxa to prompt
    for i, taxon in enumerate(all_taxa, 1):
        prompt += f"{i}. {taxon}\n"

    prompt += """

# Output Format

Provide your response as a JSON object with this structure:
{
  "scores": {
    "Taxon Full Label 1": confidence_score,
    "Taxon Full Label 2": confidence_score,
    ...
  },
  "top_taxa": ["list of taxa with scores > 60"],
  "reasoning": "Brief explanation of your highest-scoring assignments"
}

Important: Include ALL taxa in the scores object, even those with 0 scores."""

    return prompt

def call_llm(prompt: str, chunk_text: str, model: str = DEFAULT_MODEL) -> Optional[Dict]:
    """Call LLM for comprehensive annotation."""

    full_prompt = f"{prompt}\n\n# Text Chunk to Analyze:\n\n{chunk_text}\n\n# Your Analysis:"

    # Try Claude
    try:
        result = subprocess.run(
            ['claude', '-m', model],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=60  # Longer timeout for comprehensive analysis
        )
        if result.returncode == 0:
            return parse_llm_response(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try OpenAI
    try:
        result = subprocess.run(
            ['openai', 'api', 'chat.completions.create',
             '-m', 'gpt-3.5-turbo',
             '-g', full_prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return parse_llm_response(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try Gemini
    try:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            import requests
            gemini_data = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2000
                }
            }

            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
                json=gemini_data,
                timeout=60
            )

            if response.status_code == 200:
                response_data = response.json()
                if 'candidates' in response_data:
                    text = response_data['candidates'][0]['content']['parts'][0]['text']
                    return parse_llm_response(text)
    except Exception:
        pass

    return None

def parse_llm_response(response: str) -> Optional[Dict]:
    """Parse LLM response to extract scores."""
    try:
        # Try to extract JSON
        if '{' in response and '}' in response:
            json_start = response.index('{')
            json_end = response.rindex('}') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: Failed to parse LLM response as JSON: {e}")

    return None

def keyword_fallback(chunk_text: str, all_taxa: List[str]) -> Dict:
    """Simple keyword matching as fallback."""
    chunk_lower = chunk_text.lower()
    scores = {}

    for taxon in all_taxa:
        # Extract key terms from taxon
        taxon_terms = taxon.lower().split(' > ')[-1].split()

        # Simple scoring based on term matches
        score = 0
        for term in taxon_terms:
            if len(term) > 3 and term in chunk_lower:
                score += 20

        scores[taxon] = min(score, 60)  # Cap keyword scores at 60

    top_taxa = [t for t, s in scores.items() if s > 40]

    return {
        'scores': scores,
        'top_taxa': top_taxa,
        'reasoning': 'Keyword-based fallback scoring',
        'method': 'keyword_fallback'
    }

def annotate_chunks(chunks: List[Dict], taxonomy: Dict, all_taxa: List[str],
                    test_mode: bool = False, use_llm: bool = True) -> List[Dict]:
    """Annotate chunks with comprehensive taxonomy scores."""

    if test_mode:
        chunks = chunks[:5]  # Even fewer for comprehensive analysis
        print(f"🧪 TEST MODE: Processing only first 5 chunks")

    annotated_chunks = []
    prompt = create_annotation_prompt(taxonomy, all_taxa)

    # Statistics tracking
    taxa_frequency = Counter()
    taxa_total_scores = defaultdict(float)
    taxa_appearance_count = defaultdict(int)

    print(f"\n📊 Annotating {len(chunks)} chunks with {len(all_taxa)} taxa...")
    print("="*60)

    for i, chunk in enumerate(chunks):
        chunk_text = chunk.get('chunk_text', chunk.get('content', ''))

        if not chunk_text:
            continue

        print(f"\n[{i+1}/{len(chunks)}] Processing chunk from paper: {chunk.get('paper_title', 'Unknown')[:50]}...")

        if use_llm:
            annotation = call_llm(prompt, chunk_text)
            if not annotation:
                print("  ⚠️ LLM call failed, using keyword fallback")
                annotation = keyword_fallback(chunk_text, all_taxa)
        else:
            annotation = keyword_fallback(chunk_text, all_taxa)

        # Add annotation to chunk
        chunk['taxonomy_scores'] = annotation.get('scores', {})
        chunk['top_taxa'] = annotation.get('top_taxa', [])
        chunk['annotation_reasoning'] = annotation.get('reasoning', '')
        chunk['annotation_method'] = annotation.get('method', 'llm')

        # Calculate statistics
        for taxon, score in chunk['taxonomy_scores'].items():
            if score > 0:
                taxa_appearance_count[taxon] += 1
                taxa_total_scores[taxon] += score
                if score > 60:
                    taxa_frequency[taxon] += 1

        annotated_chunks.append(chunk)

        # Show top taxa for this chunk
        if chunk['top_taxa']:
            print(f"  ✓ Top taxa: {', '.join(chunk['top_taxa'][:3])}")
        else:
            print(f"  ✓ No high-confidence taxa (all scores < 60)")

        # Rate limiting
        if use_llm:
            time.sleep(RATE_LIMIT_DELAY)

    # Print statistics
    print("\n" + "="*60)
    print("📈 ANNOTATION STATISTICS")
    print("="*60)

    print(f"\nChunks processed: {len(annotated_chunks)}")
    print(f"Taxa evaluated per chunk: {len(all_taxa)}")
    print(f"Total evaluations: {len(annotated_chunks) * len(all_taxa):,}")

    # Taxa with high scores
    high_score_taxa = taxa_frequency.most_common(20)
    if high_score_taxa:
        print(f"\n🏆 Top Taxa (scores > 60):")
        for taxon, count in high_score_taxa[:10]:
            avg_score = taxa_total_scores[taxon] / taxa_appearance_count[taxon]
            print(f"  • {taxon}: {count} chunks (avg score: {avg_score:.1f})")

    # Taxa coverage by HLTP
    print(f"\n📊 Coverage by High-Level Topic Pillar:")
    for hltp in taxonomy.keys():
        hltp_scores = [
            score for chunk in annotated_chunks
            for taxon, score in chunk['taxonomy_scores'].items()
            if taxon.startswith(hltp) and score > 60
        ]
        if hltp_scores:
            print(f"  • {hltp}: {len(hltp_scores)} high-confidence assignments")

    # Unused taxa
    used_taxa = set(taxa_appearance_count.keys())
    unused_taxa = set(all_taxa) - used_taxa
    print(f"\n📉 Taxonomy Utilization:")
    print(f"  • Taxa with any positive score: {len(used_taxa)}/{len(all_taxa)} ({len(used_taxa)*100/len(all_taxa):.1f}%)")
    print(f"  • Taxa never scored > 0: {len(unused_taxa)}")

    return annotated_chunks

def save_results(annotated_chunks: List[Dict], all_taxa: List[str], output_file: str):
    """Save comprehensive annotation results."""

    # Create summary statistics
    summary = {
        'total_chunks': len(annotated_chunks),
        'total_taxa': len(all_taxa),
        'total_evaluations': len(annotated_chunks) * len(all_taxa),
        'timestamp': datetime.now().isoformat()
    }

    # Create taxa statistics
    taxa_stats = {}
    for taxon in all_taxa:
        scores = [
            chunk['taxonomy_scores'].get(taxon, 0)
            for chunk in annotated_chunks
        ]
        nonzero_scores = [s for s in scores if s > 0]

        taxa_stats[taxon] = {
            'appearances': len(nonzero_scores),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'high_confidence_count': len([s for s in scores if s > 60])
        }

    # Sort taxa by relevance
    ranked_taxa = sorted(
        taxa_stats.items(),
        key=lambda x: (x[1]['high_confidence_count'], x[1]['avg_score']),
        reverse=True
    )

    output_data = {
        'metadata': summary,
        'taxa_statistics': dict(ranked_taxa),
        'annotated_chunks': annotated_chunks
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_file}")

    # Also create a CSV matrix
    csv_file = output_file.replace('.json', '_matrix.csv')
    create_score_matrix(annotated_chunks, all_taxa, csv_file)

def create_score_matrix(chunks: List[Dict], all_taxa: List[str], output_file: str):
    """Create a CSV matrix of chunks × taxa scores."""
    import csv

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        header = ['chunk_id', 'paper_title'] + all_taxa
        writer.writerow(header)

        # Data rows
        for chunk in chunks:
            row = [
                chunk.get('chunk_id', 'unknown'),
                chunk.get('paper_title', 'unknown')[:50]
            ]
            for taxon in all_taxa:
                score = chunk.get('taxonomy_scores', {}).get(taxon, 0)
                row.append(score)

            writer.writerow(row)

    print(f"📊 Score matrix saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive multi-taxonomy annotation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script performs exhaustive taxonomic analysis, scoring every chunk
against every taxon in your taxonomy. This provides complete coverage
analysis but is more expensive than selective annotation.

Examples:
  # Test with 5 chunks
  python annotate_all_taxa.py --chunks data.json --taxonomy taxonomy.tsv --test

  # Full annotation
  python annotate_all_taxa.py --chunks data.json --taxonomy taxonomy.tsv --output full_annotation.json

  # Keyword-only (no LLM)
  python annotate_all_taxa.py --chunks data.json --taxonomy taxonomy.tsv --no-llm
        """
    )

    parser.add_argument('--chunks', '-c', required=True,
                       help='Input chunks JSON file')
    parser.add_argument('--taxonomy', '-t', required=True,
                       help='Taxonomy TSV file')
    parser.add_argument('--output', '-o',
                       default='chunks_all_taxa_annotated.json',
                       help='Output file for annotations')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only 5 chunks')
    parser.add_argument('--no-llm', action='store_true',
                       help='Use keyword matching instead of LLM')

    args = parser.parse_args()

    # Check input files
    if not Path(args.chunks).exists():
        print(f"Error: Chunks file {args.chunks} not found")
        sys.exit(1)

    if not Path(args.taxonomy).exists():
        print(f"Error: Taxonomy file {args.taxonomy} not found")
        sys.exit(1)

    print("="*60)
    print("🔬 COMPREHENSIVE TAXONOMY ANNOTATION")
    print("="*60)

    # Load data
    print("\n📁 Loading data...")
    with open(args.chunks, 'r', encoding='utf-8') as f:
        chunk_data = json.load(f)

    if 'chunks' in chunk_data:
        chunks = chunk_data['chunks']
    elif isinstance(chunk_data, list):
        chunks = chunk_data
    else:
        print(f"Error: Unexpected JSON structure in {args.chunks}")
        sys.exit(1)

    print(f"✓ Loaded {len(chunks)} chunks")

    # Load taxonomy
    taxonomy, all_taxa, hltp_structure = load_taxonomy(args.taxonomy)

    # Cost estimation
    if not args.no_llm:
        cost_per_chunk = 0.0005  # Rough estimate for comprehensive analysis
        if args.test:
            estimated_cost = 5 * cost_per_chunk
        else:
            estimated_cost = len(chunks) * cost_per_chunk

        print(f"\n💰 Estimated cost: ${estimated_cost:.2f}")
        print(f"   ({len(chunks)} chunks × {len(all_taxa)} taxa = {len(chunks)*len(all_taxa):,} evaluations)")

        if not args.test and estimated_cost > 10:
            print("\n⚠️  Warning: This will cost more than $10!")
            response = input("Continue? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                sys.exit(0)

    # Annotate
    annotated_chunks = annotate_chunks(
        chunks,
        taxonomy,
        all_taxa,
        test_mode=args.test,
        use_llm=not args.no_llm
    )

    # Save results
    save_results(annotated_chunks, all_taxa, args.output)

    print("\n🎉 Annotation complete!")

if __name__ == "__main__":
    main()