#!/usr/bin/env python3
"""
Analyze the actual content downloaded from Ottoman Bank papers.
Extracts text from PDFs and analyzes word counts and topics.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import PyPDF2
import pdfplumber

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using pdfplumber (better) or PyPDF2 (fallback)."""
    text = ""

    # Try pdfplumber first (better extraction)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception as e:
        print(f"  pdfplumber failed: {e}")

    # Fallback to PyPDF2
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"  PyPDF2 failed: {e}")

    return text

def extract_text_from_txt(txt_path: Path) -> str:
    """Read text file content."""
    try:
        return txt_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"  Failed to read text file: {e}")
        return ""

def clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
    return text.strip()

def analyze_content(text: str) -> Dict:
    """Analyze text content for key themes and statistics."""

    # Word count
    words = text.split()
    word_count = len(words)

    # Character count
    char_count = len(text)

    # Find Ottoman Bank mentions
    text_lower = text.lower()
    ottoman_bank_mentions = text_lower.count('ottoman bank')
    imperial_ottoman_mentions = text_lower.count('imperial ottoman')

    # Key terms related to Ottoman Bank
    key_terms = {
        'banking': len(re.findall(r'\bbank\w*\b', text_lower)),
        'ottoman': len(re.findall(r'\bottoman\w*\b', text_lower)),
        'turkey/turkish': len(re.findall(r'\b(turk\w*|turkey)\b', text_lower)),
        'finance/financial': len(re.findall(r'\bfinanc\w*\b', text_lower)),
        'economic/economy': len(re.findall(r'\beconom\w*\b', text_lower)),
        'capital': len(re.findall(r'\bcapital\w*\b', text_lower)),
        'credit': len(re.findall(r'\bcredit\w*\b', text_lower)),
        'debt': len(re.findall(r'\bdebt\w*\b', text_lower)),
        'trade': len(re.findall(r'\btrad\w*\b', text_lower)),
        'empire': len(re.findall(r'\bempire\w*\b', text_lower)),
        'institution': len(re.findall(r'\binstitut\w*\b', text_lower)),
        'development': len(re.findall(r'\bdevelop\w*\b', text_lower)),
        'modern': len(re.findall(r'\bmodern\w*\b', text_lower)),
        'reform': len(re.findall(r'\breform\w*\b', text_lower)),
        'state': len(re.findall(r'\bstate\w*\b', text_lower))
    }

    # Extract potential topics (most common multi-word phrases)
    # Simple bigram extraction
    bigrams = []
    for i in range(len(words)-1):
        if len(words[i]) > 3 and len(words[i+1]) > 3:  # Skip short words
            bigram = f"{words[i].lower()} {words[i+1].lower()}"
            if not any(char.isdigit() for char in bigram):  # Skip with numbers
                bigrams.append(bigram)

    common_bigrams = Counter(bigrams).most_common(10)

    # Identify document type/genre
    doc_type = "unknown"
    if 'abstract' in text_lower[:1000]:
        doc_type = "academic paper"
    elif 'chapter' in text_lower[:1000]:
        doc_type = "book chapter"
    elif 'report' in text_lower[:1000]:
        doc_type = "report"

    return {
        'word_count': word_count,
        'char_count': char_count,
        'ottoman_bank_mentions': ottoman_bank_mentions,
        'imperial_ottoman_mentions': imperial_ottoman_mentions,
        'key_terms': key_terms,
        'common_phrases': [phrase for phrase, count in common_bigrams],
        'doc_type': doc_type
    }

def main():
    import sys
    content_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "ottoman_bank_correct_content")

    if not content_dir.exists():
        print(f"Error: {content_dir} not found")
        return

    # Load download log to get paper titles
    log_file = content_dir / "download_log_enhanced.json"
    paper_info = {}
    if log_file.exists():
        with open(log_file, 'r') as f:
            log_data = json.load(f)
            for result in log_data['results']:
                paper_id = result['paper_id'].replace('https://openalex.org/', '')
                paper_info[paper_id] = result.get('title', 'Unknown')

    print("="*60)
    print("CONTENT ANALYSIS OF DOWNLOADED PAPERS")
    print("="*60)

    all_analyses = []

    # Process each downloaded item
    for item in sorted(content_dir.iterdir()):
        if item.suffix in ['.pdf', '.txt']:
            paper_id = item.stem.replace('_rendered', '').split('_')[0]
            title = paper_info.get(paper_id, 'Unknown')[:60]

            print(f"\n📄 {item.name}")
            print(f"   Title: {title}")

            # Extract text
            text = ""
            if item.suffix == '.pdf':
                text = extract_text_from_pdf(item)
            elif item.suffix == '.txt':
                text = extract_text_from_txt(item)

            if text:
                text = clean_text(text)
                analysis = analyze_content(text)
                analysis['file'] = item.name
                analysis['title'] = title
                all_analyses.append(analysis)

                print(f"   Words: {analysis['word_count']:,}")
                print(f"   Ottoman Bank mentions: {analysis['ottoman_bank_mentions']}")

                # Show top key terms
                top_terms = sorted(analysis['key_terms'].items(),
                                 key=lambda x: x[1], reverse=True)[:5]
                if top_terms:
                    print(f"   Top terms: {', '.join([f'{k} ({v})' for k, v in top_terms])}")
            else:
                print(f"   ⚠️ No text extracted")

    # Overall statistics
    if all_analyses:
        print("\n" + "="*60)
        print("OVERALL STATISTICS")
        print("="*60)

        word_counts = [a['word_count'] for a in all_analyses]
        ottoman_mentions = [a['ottoman_bank_mentions'] for a in all_analyses]

        print(f"\nDocuments analyzed: {len(all_analyses)}")
        print(f"\nWord counts:")
        print(f"  Average: {sum(word_counts)/len(word_counts):,.0f} words")
        print(f"  Minimum: {min(word_counts):,} words")
        print(f"  Maximum: {max(word_counts):,} words")
        print(f"  Total: {sum(word_counts):,} words")

        print(f"\nOttoman Bank mentions:")
        docs_with_mentions = sum(1 for m in ottoman_mentions if m > 0)
        print(f"  Documents with mentions: {docs_with_mentions}/{len(all_analyses)} ({docs_with_mentions*100/len(all_analyses):.1f}%)")
        print(f"  Total mentions: {sum(ottoman_mentions)}")
        print(f"  Average per document: {sum(ottoman_mentions)/len(all_analyses):.1f}")

        # Aggregate key terms
        print(f"\nMost common terms across all documents:")
        all_terms = Counter()
        for analysis in all_analyses:
            for term, count in analysis['key_terms'].items():
                all_terms[term] += count

        for term, count in all_terms.most_common(10):
            print(f"  {term}: {count:,} occurrences")

        # Papers with Ottoman Bank mentions
        print(f"\nPapers with Ottoman Bank mentions:")
        for analysis in all_analyses:
            if analysis['ottoman_bank_mentions'] > 0:
                print(f"  • {analysis['title'][:60]}: {analysis['ottoman_bank_mentions']} mentions")

        # Common themes
        print(f"\nCommon themes (based on frequent phrases):")
        all_phrases = Counter()
        for analysis in all_analyses:
            for phrase in analysis.get('common_phrases', []):
                all_phrases[phrase] += 1

        for phrase, count in all_phrases.most_common(15):
            if count > 1:  # Only show phrases that appear in multiple docs
                print(f"  • {phrase} ({count} documents)")

        # Save detailed results
        output_file = content_dir / "content_analysis.json"
        with open(output_file, 'w') as f:
            json.dump({
                'summary': {
                    'documents_analyzed': len(all_analyses),
                    'avg_word_count': sum(word_counts)/len(word_counts),
                    'min_word_count': min(word_counts),
                    'max_word_count': max(word_counts),
                    'total_words': sum(word_counts),
                    'docs_with_ottoman_mentions': docs_with_mentions,
                    'total_ottoman_mentions': sum(ottoman_mentions)
                },
                'analyses': all_analyses
            }, f, indent=2)

        print(f"\nDetailed analysis saved to: {output_file}")

if __name__ == "__main__":
    # Check for required libraries
    try:
        import PyPDF2
    except ImportError:
        print("Installing PyPDF2...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'PyPDF2'])
        import PyPDF2

    try:
        import pdfplumber
    except ImportError:
        print("Installing pdfplumber...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pdfplumber'])
        import pdfplumber

    main()