#!/usr/bin/env python3
"""
Ottoman Bank taxonomy annotation script.

Classifies chunks from Ottoman Bank corpus against the 6-HLTP Ottoman Bank taxonomy.
Based on the transparent battlefield annotation approach but adapted for financial history.
"""

import json
import os
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess

# Configuration
MODEL = "claude-3-haiku-20240307"  # Fast and accurate for classification
BATCH_SIZE = 5  # Process 5 chunks at a time
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 0.2  # 200ms between API calls

# Load the annotation prompt
SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = SCRIPT_DIR / "ottoman_bank_annotation_prompt.txt"

def load_prompt() -> str:
    """Load the Ottoman Bank annotation prompt."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")

def load_taxonomy() -> Dict[str, List[str]]:
    """Load the Ottoman Bank taxonomy from TSV file."""
    taxonomy_path = SCRIPT_DIR / "ottoman_bank_taxonomy.tsv"
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")

    taxonomy = {}
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split('\t')
            if len(parts) == 4:
                hltp, level2, level3, taxon = parts
                full_label = f"{hltp} | {level2} | {level3} | {taxon}"
                if hltp not in taxonomy:
                    taxonomy[hltp] = []
                taxonomy[hltp].append(full_label)

    return taxonomy

def load_chunks(input_file: str) -> List[Dict[str, Any]]:
    """Load chunks from JSON file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'chunks' in data:
        return data['chunks']
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Unexpected JSON structure in {input_file}")

def call_llm(prompt: str, chunk_text: str, model: str = MODEL) -> Optional[Dict]:
    """Call LLM for annotation - supports Claude, OpenAI, and Gemini."""

    full_prompt = f"{prompt}\n\n# Text Chunk to Classify:\n\n{chunk_text}\n\n# Your Classification:"

    # Try Claude first
    try:
        result = subprocess.run(
            ['claude', '-m', model],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=30
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
            timeout=30
        )
        if result.returncode == 0:
            return parse_llm_response(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try Gemini
    try:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            gemini_data = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1000
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
                response_data = json.loads(result.stdout)
                if 'candidates' in response_data:
                    text = response_data['candidates'][0]['content']['parts'][0]['text']
                    return parse_llm_response(text)
    except Exception:
        pass

    return None

def parse_llm_response(response: str) -> Dict:
    """Parse LLM response to extract classification."""
    result = {
        'is_relevant': False,
        'labels': [],
        'confidence': [],
        'explanation': '',
        'exclusion_explanation': ''
    }

    # Try to extract JSON if present
    if '{' in response and '}' in response:
        try:
            json_start = response.index('{')
            json_end = response.rindex('}') + 1
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)

            result['is_relevant'] = parsed.get('is_relevant', False)
            result['labels'] = parsed.get('labels', [])
            result['confidence'] = parsed.get('confidence', [])
            result['explanation'] = parsed.get('explanation', '')
            result['exclusion_explanation'] = parsed.get('exclusion_explanation', '')

            return result
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: parse text response
    response_lower = response.lower()

    # Check relevance
    if 'not relevant' in response_lower or 'is_relevant": false' in response_lower:
        result['is_relevant'] = False
        # Try to extract explanation
        if 'explanation:' in response_lower:
            explanation_start = response_lower.index('explanation:') + 12
            result['exclusion_explanation'] = response[explanation_start:].strip()[:200]
    else:
        result['is_relevant'] = True
        # Extract labels (look for taxonomy patterns)
        lines = response.split('\n')
        for line in lines:
            if '|' in line and any(hltp in line for hltp in ['Financial Operations', 'Institutional Structure',
                                                               'Historical Context', 'Economic Impact',
                                                               'Political Dimensions', 'Social and Cultural']):
                result['labels'].append(line.strip())

    return result

def annotate_chunks(chunks: List[Dict], system_prompt: str, test_mode: bool = False,
                    use_llm: bool = True) -> List[Dict]:
    """Annotate chunks with Ottoman Bank taxonomy."""

    if test_mode:
        chunks = chunks[:10]
        print(f"🧪 TEST MODE: Processing only first 10 chunks")

    annotated_chunks = []
    taxonomy_coverage = {}
    total_annotations = 0
    relevant_count = 0

    print(f"\n🏛️ Annotating {len(chunks)} chunks with Ottoman Bank taxonomy...")
    print("=" * 60)

    # Test LLM availability
    if use_llm:
        test_response = call_llm("Respond with: OK", "test", MODEL)
        if not test_response:
            print("⚠️ LLM not available. Using fallback classification.")
            use_llm = False

    # Process chunks
    for i, chunk in enumerate(chunks):
        if i % 10 == 0 and i > 0:
            print(f"Progress: {i}/{len(chunks)} chunks processed | "
                  f"Relevant: {relevant_count}/{i} ({relevant_count*100/i:.1f}%)")

        chunk_text = chunk.get('chunk_text', chunk.get('content', ''))

        if use_llm:
            # Get classification from LLM
            classification = call_llm(system_prompt, chunk_text, MODEL)

            if classification:
                chunk['is_relevant'] = classification['is_relevant']
                chunk['taxonomy_labels'] = classification['labels']
                chunk['confidence'] = classification['confidence']
                chunk['explanation'] = classification['explanation']
                chunk['exclusion_explanation'] = classification['exclusion_explanation']

                if classification['is_relevant']:
                    relevant_count += 1
                    # Track taxonomy coverage
                    for label in classification['labels']:
                        taxonomy_coverage[label] = taxonomy_coverage.get(label, 0) + 1
                        total_annotations += 1
            else:
                # LLM call failed
                chunk['is_relevant'] = None
                chunk['error'] = 'LLM classification failed'
        else:
            # Fallback: simple keyword matching
            chunk_lower = chunk_text.lower()
            is_relevant = ('ottoman bank' in chunk_lower or
                          'banque impériale ottomane' in chunk_lower or
                          'imperial ottoman bank' in chunk_lower)

            chunk['is_relevant'] = is_relevant
            chunk['taxonomy_labels'] = []
            chunk['fallback_classification'] = True

            if is_relevant:
                relevant_count += 1

        annotated_chunks.append(chunk)

        # Rate limiting
        if use_llm:
            time.sleep(RATE_LIMIT_DELAY)

    # Final statistics
    print("\n" + "=" * 60)
    print(f"\n📊 Annotation Results:")
    print(f"  Total chunks: {len(annotated_chunks)}")
    print(f"  Relevant chunks: {relevant_count} ({relevant_count*100/len(annotated_chunks):.1f}%)")
    print(f"  Irrelevant chunks: {len(annotated_chunks) - relevant_count}")
    print(f"  Total annotations: {total_annotations}")

    if taxonomy_coverage:
        print(f"\n🏷️ Top 10 Most Applied Taxa:")
        sorted_taxa = sorted(taxonomy_coverage.items(), key=lambda x: x[1], reverse=True)
        for label, count in sorted_taxa[:10]:
            # Shorten label for display
            parts = label.split(' | ')
            if len(parts) >= 2:
                short_label = f"{parts[0]} | {parts[-1]}"
            else:
                short_label = label[:60]
            print(f"  - {short_label}: {count} times")

    return annotated_chunks

def save_results(annotated_chunks: List[Dict], output_file: str):
    """Save annotated chunks to JSON file."""

    output_data = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'total_chunks': len(annotated_chunks),
            'relevant_chunks': sum(1 for c in annotated_chunks if c.get('is_relevant')),
            'model_used': MODEL,
            'taxonomy': 'Ottoman Bank 6-HLTP Taxonomy'
        },
        'chunks': annotated_chunks
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Annotate Ottoman Bank chunks with taxonomy')
    parser.add_argument('--input', '-i', required=True,
                       help='Input chunks JSON file')
    parser.add_argument('--output', '-o',
                       help='Output annotated file',
                       default='ottoman_bank_annotated.json')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only 10 chunks')
    parser.add_argument('--no-llm', action='store_true',
                       help='Use keyword matching instead of LLM')

    args = parser.parse_args()

    print("=" * 60)
    print("🏛️ OTTOMAN BANK TAXONOMY ANNOTATION")
    print("=" * 60)

    # Load resources
    system_prompt = load_prompt()
    taxonomy = load_taxonomy()
    chunks = load_chunks(args.input)

    print(f"✅ Loaded {len(chunks)} chunks")
    print(f"✅ Loaded taxonomy with {len(taxonomy)} HLTPs")

    # Annotate
    annotated_chunks = annotate_chunks(
        chunks,
        system_prompt,
        test_mode=args.test,
        use_llm=not args.no_llm
    )

    # Save results
    save_results(annotated_chunks, args.output)

    print("\n🎉 Annotation complete!")

if __name__ == "__main__":
    main()