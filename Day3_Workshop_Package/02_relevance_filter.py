#!/usr/bin/env python3
"""
Step 2: Binary Relevance Filtering
Author: RuBase Workshop Team
Date: March 13, 2026

This script:
1. Loads the chunks from Step 1
2. Applies relevance filtering based on your research topic
3. Reduces the number of chunks to process (saves API costs)
4. Outputs only relevant chunks for taxonomic annotation

Usage:
    python 02_relevance_filter.py --topic "your research topic"
"""

import json
import os
import subprocess
import argparse
from datetime import datetime
from typing import List, Dict, Any
import time

# Configuration
BATCH_SIZE = 10  # Process chunks in batches to show progress
MODEL = "claude-3-haiku-20240307"  # Fast and cheap model for filtering

# Relevance prompt template
RELEVANCE_PROMPT = """You are helping filter academic abstracts for relevance to a specific research topic.

RESEARCH TOPIC: {topic}

TEXT TO EVALUATE:
{text}

Is this text relevant to the research topic above? Consider it relevant if it:
- Directly discusses the topic or closely related concepts
- Provides theoretical background relevant to the topic
- Discusses methods applicable to studying the topic
- Contains empirical findings related to the topic

Respond with ONLY one word: "relevant" or "irrelevant"

Your response:"""

def load_chunks(filepath: str) -> Dict[str, Any]:
    """Load chunks from previous step"""
    print(f"📂 Loading chunks from: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data['chunks'])} chunks")
    return data

def call_llm(prompt: str, model: str = MODEL) -> str:
    """Call LLM via CLI - supports Claude, OpenAI, and Gemini"""
    try:
        # Try Claude CLI first
        result = subprocess.run(
            ['claude', '-m', model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip().lower()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    try:
        # Try OpenAI CLI
        result = subprocess.run(
            ['openai', 'api', 'completions.create', '-m', 'gpt-3.5-turbo'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip().lower()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    try:
        # Try Gemini via curl (common approach)
        import os
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            # Format for Gemini API
            gemini_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10}
            }

            result = subprocess.run(
                ['curl', '-s', '-X', 'POST',
                 f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
                 '-H', 'Content-Type: application/json',
                 '-d', json.dumps(gemini_data)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if 'candidates' in response:
                    text = response['candidates'][0]['content']['parts'][0]['text']
                    return text.strip().lower()
    except Exception:
        pass

    # Fallback to simple keyword matching if no LLM available
    return None

def simple_relevance_check(text: str, topic: str) -> bool:
    """Simple keyword-based relevance check as fallback"""
    # Extract key terms from topic
    topic_words = set(word.lower() for word in topic.split() if len(word) > 3)
    text_lower = text.lower()

    # Count matching words
    matches = sum(1 for word in topic_words if word in text_lower)

    # Consider relevant if at least 2 topic words appear
    return matches >= min(2, len(topic_words))

def filter_chunks(chunks_data: Dict[str, Any], research_topic: str, use_llm: bool = True) -> Dict[str, Any]:
    """Filter chunks for relevance"""
    chunks = chunks_data['chunks']
    relevant_chunks = []
    irrelevant_count = 0

    print(f"\n🔍 Filtering {len(chunks)} chunks for relevance to:")
    print(f"   '{research_topic}'")
    print("\n" + "=" * 60)

    # Test LLM availability
    if use_llm:
        test_prompt = "Respond with 'yes'"
        test_response = call_llm(test_prompt)
        if test_response is None:
            print("⚠️ LLM not available. Using keyword-based filtering instead.")
            use_llm = False
        else:
            print(f"✅ Using LLM for relevance filtering (model: {MODEL})")

    # Process in batches
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]
        batch_relevant = 0

        for chunk in batch:
            if use_llm:
                # Create prompt
                prompt = RELEVANCE_PROMPT.format(
                    topic=research_topic,
                    text=chunk['chunk_text']
                )

                # Call LLM
                response = call_llm(prompt)

                # Parse response
                is_relevant = 'relevant' in response and 'irrelevant' not in response
            else:
                # Use simple keyword matching
                is_relevant = simple_relevance_check(chunk['chunk_text'], research_topic)

            if is_relevant:
                chunk['relevance_checked'] = True
                relevant_chunks.append(chunk)
                batch_relevant += 1
            else:
                irrelevant_count += 1

            # Small delay to avoid rate limiting
            if use_llm:
                time.sleep(0.1)

        # Progress update
        processed = min(i + BATCH_SIZE, len(chunks))
        print(f"  Batch {i//BATCH_SIZE + 1}: {batch_relevant}/{len(batch)} relevant | "
              f"Total: {processed}/{len(chunks)} processed")

    print("\n" + "=" * 60)
    print(f"\n📊 Filtering Results:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Relevant chunks: {len(relevant_chunks)} ({len(relevant_chunks)/len(chunks)*100:.1f}%)")
    print(f"  Filtered out: {irrelevant_count} ({irrelevant_count/len(chunks)*100:.1f}%)")
    print(f"  💰 Cost savings: ~{irrelevant_count/len(chunks)*100:.0f}% reduction in API calls")

    # Create filtered dataset
    filtered_data = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'research_topic': research_topic,
            'original_chunks': len(chunks),
            'relevant_chunks': len(relevant_chunks),
            'filtering_method': 'LLM' if use_llm else 'keyword',
            'model_used': MODEL if use_llm else None
        },
        'chunks': relevant_chunks
    }

    return filtered_data

def save_filtered_chunks(data: Dict[str, Any], output_file: str):
    """Save filtered chunks"""
    print(f"\n💾 Saving {len(data['chunks'])} relevant chunks to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    print(f"✅ Saved successfully ({file_size:.2f} MB)")

def estimate_costs(num_chunks: int):
    """Estimate API costs for annotation"""
    # Rough estimates
    tokens_per_chunk = 150  # Average
    tokens_per_response = 50  # Average
    total_tokens = num_chunks * (tokens_per_chunk + tokens_per_response)

    print(f"\n💵 Cost Estimation for Taxonomic Annotation:")
    print(f"  Chunks to process: {num_chunks}")
    print(f"  Estimated tokens: {total_tokens:,}")

    # Claude Haiku pricing
    claude_cost = (total_tokens / 1_000_000) * 0.25  # Input pricing
    claude_cost += (total_tokens / 1_000_000) * 1.25 * 0.2  # Output (20% of input)
    print(f"  Claude Haiku cost: ~${claude_cost:.2f}")

    # GPT-3.5 pricing
    gpt_cost = (total_tokens / 1_000_000) * 0.50  # Input pricing
    gpt_cost += (total_tokens / 1_000_000) * 1.50 * 0.2  # Output
    print(f"  GPT-3.5 cost: ~${gpt_cost:.2f}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Filter chunks for relevance')
    parser.add_argument('--input', '-i',
                       help='Input chunks file',
                       default='chunks.json')
    parser.add_argument('--output', '-o',
                       help='Output filtered chunks file',
                       default='chunks_filtered.json')
    parser.add_argument('--topic', '-t',
                       help='Research topic for filtering',
                       required=True)
    parser.add_argument('--no-llm',
                       action='store_true',
                       help='Use keyword filtering instead of LLM')

    args = parser.parse_args()

    print("=" * 60)
    print("🔍 STEP 2: RELEVANCE FILTERING")
    print("=" * 60)

    # Check input file
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found!")
        print("   Run 01_extract_chunks.py first")
        return

    # Load and filter
    chunks_data = load_chunks(args.input)
    filtered_data = filter_chunks(chunks_data, args.topic, use_llm=not args.no_llm)

    # Save results
    save_filtered_chunks(filtered_data, args.output)

    # Cost estimation
    estimate_costs(len(filtered_data['chunks']))

    print("\n🎉 Success! Next step: Run 03_annotate_taxonomy.py")
    print(f"   python 03_annotate_taxonomy.py --chunks {args.output} --taxonomy your_taxonomy.tsv")

if __name__ == "__main__":
    main()