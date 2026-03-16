#!/usr/bin/env python3
"""
Step 3: Taxonomic Annotation with Multi-Dimensional Taxonomy
Author: RuBase Workshop Team
Date: March 13, 2026

This script:
1. Loads your taxonomy (TSV from Day 2)
2. Loads filtered chunks
3. Annotates each chunk with relevant taxonomy nodes
4. Outputs annotated corpus with taxonomy labels

Usage:
    python 03_annotate_taxonomy.py --taxonomy my_taxonomy.tsv --chunks chunks_filtered.json
"""

import json
import os
import csv
import subprocess
import argparse
from datetime import datetime
from typing import List, Dict, Any, Set
import time
import sys

# Configuration
BATCH_SIZE = 5  # Chunks per batch
MODEL = "claude-3-haiku-20240307"  # Fast model for classification
MAX_LABELS_PER_CHUNK = 5  # Maximum taxonomy labels per chunk
TEST_MODE_CHUNKS = 10  # Number of chunks for test mode

# Annotation prompt template
ANNOTATION_PROMPT = """You are annotating academic text with a multi-dimensional taxonomy.

TAXONOMY STRUCTURE:
{taxonomy_desc}

TEXT TO ANNOTATE:
{text}

TASK:
Identify which lowest-level taxonomy elements (taxa) apply to this text.
Only select taxa that are explicitly relevant to the content.
You may select taxa from multiple dimensions if applicable.

Provide your response as a JSON list of selected taxa.
Each item should include the full taxonomic path.

Example format:
[
  {{"hltp": "Temporal", "level2": "Historical", "level3": "Pre-2000", "taxon": "Cold War era"}},
  {{"hltp": "Geographic", "level2": "Regional", "level3": "Europe", "taxon": "Eastern Europe"}}
]

If no taxa apply, return an empty list: []

Your response (JSON only):"""

def load_taxonomy(filepath: str) -> Dict[str, Any]:
    """Load taxonomy from TSV file"""
    print(f"📂 Loading taxonomy from: {filepath}")

    taxonomy = {
        'dimensions': {},
        'total_taxa': 0,
        'structure': []
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                hltp = row.get('HLTP', row.get('hltp', ''))
                level2 = row.get('2nd Level TE', row.get('level2', ''))
                level3 = row.get('3rd Level TE', row.get('level3', ''))
                taxon = row.get('Taxon', row.get('taxon', ''))

                if not hltp:
                    continue

                # Build hierarchical structure
                if hltp not in taxonomy['dimensions']:
                    taxonomy['dimensions'][hltp] = {}

                if level2 and level2 not in taxonomy['dimensions'][hltp]:
                    taxonomy['dimensions'][hltp][level2] = {}

                if level3 and level3 not in taxonomy['dimensions'][hltp][level2]:
                    taxonomy['dimensions'][hltp][level2][level3] = []

                if taxon and taxon not in taxonomy['dimensions'][hltp][level2][level3]:
                    taxonomy['dimensions'][hltp][level2][level3].append(taxon)
                    taxonomy['total_taxa'] += 1

                # Store flat structure for prompt
                taxonomy['structure'].append({
                    'hltp': hltp,
                    'level2': level2,
                    'level3': level3,
                    'taxon': taxon
                })

        print(f"✅ Loaded taxonomy with:")
        print(f"   Dimensions: {len(taxonomy['dimensions'])}")
        print(f"   Total taxa: {taxonomy['total_taxa']}")

        # Show dimension names
        for dim in list(taxonomy['dimensions'].keys())[:5]:
            print(f"   - {dim}")
        if len(taxonomy['dimensions']) > 5:
            print(f"   ... and {len(taxonomy['dimensions'])-5} more")

        return taxonomy

    except Exception as e:
        print(f"❌ Error loading taxonomy: {e}")
        sys.exit(1)

def load_chunks(filepath: str) -> Dict[str, Any]:
    """Load filtered chunks"""
    print(f"📂 Loading chunks from: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data['chunks'])} filtered chunks")
    return data

def create_taxonomy_description(taxonomy: Dict[str, Any], max_examples: int = 3) -> str:
    """Create a concise taxonomy description for the prompt"""
    desc_lines = ["Your taxonomy has the following dimensions:\n"]

    for i, (dim_name, dim_content) in enumerate(taxonomy['dimensions'].items(), 1):
        if i > 5:  # Limit to first 5 dimensions for prompt length
            desc_lines.append(f"... and {len(taxonomy['dimensions'])-5} more dimensions")
            break

        desc_lines.append(f"{i}. {dim_name}")

        # Show a few examples from this dimension
        examples_shown = 0
        for l2_name, l2_content in dim_content.items():
            if examples_shown >= max_examples:
                break
            for l3_name, taxa in l2_content.items():
                if examples_shown >= max_examples:
                    break
                if taxa:
                    desc_lines.append(f"   → {l2_name} → {l3_name} → {taxa[0]}")
                    examples_shown += 1

    return "\n".join(desc_lines)

def call_llm_for_annotation(prompt: str, model: str = MODEL) -> List[Dict]:
    """Call LLM and parse JSON response - supports Claude, OpenAI, and Gemini"""
    try:
        # Try Claude CLI
        result = subprocess.run(
            ['claude', '-m', model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            response = result.stdout.strip()
            # Extract JSON from response
            if '[' in response:
                json_start = response.index('[')
                json_end = response.rindex(']') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
    except Exception as e:
        pass

    try:
        # Try OpenAI CLI
        result = subprocess.run(
            ['openai', 'api', 'chat.completions.create',
             '-m', 'gpt-3.5-turbo',
             '-g', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            response = result.stdout.strip()
            if '[' in response:
                json_start = response.index('[')
                json_end = response.rindex(']') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
    except Exception:
        pass

    try:
        # Try Gemini via curl
        import os
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            # Format for Gemini API with JSON response
            gemini_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 500,
                    "responseMimeType": "application/json"
                }
            }

            result = subprocess.run(
                ['curl', '-s', '-X', 'POST',
                 f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
                 '-H', 'Content-Type: application/json',
                 '-d', json.dumps(gemini_data)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if 'candidates' in response:
                    text = response['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(text)
    except Exception as e:
        pass

    return []

def simple_taxonomy_match(text: str, taxonomy: Dict[str, Any]) -> List[Dict]:
    """Simple keyword matching as fallback"""
    matches = []
    text_lower = text.lower()

    for item in taxonomy['structure'][:100]:  # Check first 100 taxa
        if item['taxon'] and item['taxon'].lower() in text_lower:
            matches.append(item)
            if len(matches) >= MAX_LABELS_PER_CHUNK:
                break

    return matches

def annotate_chunks(chunks_data: Dict[str, Any], taxonomy: Dict[str, Any],
                    test_mode: bool = False, use_llm: bool = True) -> Dict[str, Any]:
    """Annotate chunks with taxonomy labels"""
    chunks = chunks_data['chunks']
    if test_mode:
        chunks = chunks[:TEST_MODE_CHUNKS]
        print(f"\n🧪 TEST MODE: Processing only first {TEST_MODE_CHUNKS} chunks")

    annotated_chunks = []
    taxonomy_coverage = {}  # Track which taxa are used
    total_annotations = 0

    print(f"\n🏷️ Annotating {len(chunks)} chunks with taxonomy...")
    print("=" * 60)

    # Create taxonomy description once
    taxonomy_desc = create_taxonomy_description(taxonomy)

    # Test LLM availability
    if use_llm:
        test_prompt = 'Respond with: ["test"]'
        try:
            test_response = call_llm_for_annotation(test_prompt)
            if not test_response:
                print("⚠️ LLM not responding properly. Using keyword matching.")
                use_llm = False
            else:
                print(f"✅ Using LLM for annotation (model: {MODEL})")
        except:
            print("⚠️ LLM not available. Using keyword matching.")
            use_llm = False

    # Process in batches
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]

        for chunk in batch:
            if use_llm:
                # Create annotation prompt
                prompt = ANNOTATION_PROMPT.format(
                    taxonomy_desc=taxonomy_desc,
                    text=chunk['chunk_text']
                )

                # Get annotations
                annotations = call_llm_for_annotation(prompt)

                # Limit number of labels
                if len(annotations) > MAX_LABELS_PER_CHUNK:
                    annotations = annotations[:MAX_LABELS_PER_CHUNK]
            else:
                # Use simple matching
                annotations = simple_taxonomy_match(chunk['chunk_text'], taxonomy)

            # Store annotated chunk
            chunk['taxonomy_labels'] = annotations
            chunk['num_labels'] = len(annotations)
            annotated_chunks.append(chunk)

            # Track coverage
            for ann in annotations:
                key = f"{ann.get('hltp', '')}::{ann.get('taxon', '')}"
                taxonomy_coverage[key] = taxonomy_coverage.get(key, 0) + 1
                total_annotations += 1

            # Small delay for API rate limiting
            if use_llm:
                time.sleep(0.2)

        # Progress update
        processed = min(i + BATCH_SIZE, len(chunks))
        print(f"  Batch {i//BATCH_SIZE + 1}: Processed {len(batch)} chunks | "
              f"Total: {processed}/{len(chunks)}")

    print("\n" + "=" * 60)
    print(f"\n📊 Annotation Results:")
    print(f"  Chunks annotated: {len(annotated_chunks)}")
    print(f"  Total annotations: {total_annotations}")
    print(f"  Avg labels per chunk: {total_annotations/len(annotated_chunks):.2f}")
    print(f"  Unique taxa used: {len(taxonomy_coverage)}")

    # Show most used taxa
    if taxonomy_coverage:
        print(f"\n🔝 Top 5 Most Applied Taxa:")
        sorted_taxa = sorted(taxonomy_coverage.items(), key=lambda x: x[1], reverse=True)
        for (taxa_key, count) in sorted_taxa[:5]:
            print(f"  - {taxa_key}: {count} times")

    # Create annotated dataset
    annotated_data = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'chunks_annotated': len(annotated_chunks),
            'total_annotations': total_annotations,
            'unique_taxa_used': len(taxonomy_coverage),
            'taxonomy_dimensions': len(taxonomy['dimensions']),
            'annotation_method': 'LLM' if use_llm else 'keyword',
            'model_used': MODEL if use_llm else None,
            'test_mode': test_mode
        },
        'taxonomy_coverage': taxonomy_coverage,
        'chunks': annotated_chunks
    }

    return annotated_data

def save_annotations(data: Dict[str, Any], output_file: str):
    """Save annotated chunks"""
    print(f"\n💾 Saving annotated data to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    print(f"✅ Saved successfully ({file_size:.2f} MB)")

def export_for_analysis(data: Dict[str, Any], output_prefix: str):
    """Export in various formats for analysis"""
    # Export as CSV for Excel/Sheets
    csv_file = f"{output_prefix}_annotations.csv"
    print(f"\n📄 Exporting to CSV: {csv_file}")

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['chunk_id', 'paper_id', 'paper_title', 'chunk_text',
                        'num_labels', 'taxonomy_labels'])

        for chunk in data['chunks']:
            labels_str = json.dumps(chunk.get('taxonomy_labels', []))
            writer.writerow([
                chunk.get('chunk_id', ''),
                chunk.get('paper_id', ''),
                chunk.get('paper_title', ''),
                chunk.get('chunk_text', '')[:200] + '...',  # Truncate text
                chunk.get('num_labels', 0),
                labels_str
            ])

    print(f"✅ Exported {len(data['chunks'])} annotated chunks to CSV")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Annotate chunks with taxonomy')
    parser.add_argument('--chunks', '-c',
                       help='Input filtered chunks file',
                       default='chunks_filtered.json')
    parser.add_argument('--taxonomy', '-t',
                       help='Taxonomy TSV file from Day 2',
                       required=True)
    parser.add_argument('--output', '-o',
                       help='Output annotated file',
                       default='chunks_annotated.json')
    parser.add_argument('--test',
                       action='store_true',
                       help=f'Test mode: process only {TEST_MODE_CHUNKS} chunks')
    parser.add_argument('--no-llm',
                       action='store_true',
                       help='Use keyword matching instead of LLM')
    parser.add_argument('--export-csv',
                       action='store_true',
                       help='Also export as CSV')

    args = parser.parse_args()

    print("=" * 60)
    print("🏷️ STEP 3: TAXONOMIC ANNOTATION")
    print("=" * 60)

    # Check input files
    if not os.path.exists(args.chunks):
        print(f"❌ Error: Chunks file '{args.chunks}' not found!")
        return

    if not os.path.exists(args.taxonomy):
        print(f"❌ Error: Taxonomy file '{args.taxonomy}' not found!")
        print("   Make sure to use your taxonomy TSV file from Day 2")
        return

    # Load data
    taxonomy = load_taxonomy(args.taxonomy)
    chunks_data = load_chunks(args.chunks)

    # Annotate
    annotated_data = annotate_chunks(
        chunks_data, taxonomy,
        test_mode=args.test,
        use_llm=not args.no_llm
    )

    # Save results
    save_annotations(annotated_data, args.output)

    # Export to CSV if requested
    if args.export_csv:
        export_for_analysis(annotated_data, args.output.replace('.json', ''))

    if args.test:
        print("\n⚠️ TEST MODE: Only processed first 10 chunks")
        print("   Remove --test flag to process all chunks")

    print("\n🎉 Success! Next step: Run 04_analyze_results.py")
    print(f"   python 04_analyze_results.py --input {args.output}")

if __name__ == "__main__":
    main()