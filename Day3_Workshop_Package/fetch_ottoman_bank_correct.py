#!/usr/bin/env python3
"""
Fetch papers that ACTUALLY mention "Ottoman Bank" as an exact phrase.
This is the CORRECT way to search for papers about the Ottoman Bank.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

def fetch_ottoman_bank_papers():
    """Fetch all papers with exact phrase 'Ottoman Bank' in full text."""

    base_url = "https://api.openalex.org/works"
    all_results = []
    cursor = "*"
    page = 1

    print("="*60)
    print("FETCHING OTTOMAN BANK PAPERS (CORRECT METHOD)")
    print("="*60)
    print('Using EXACT PHRASE search: fulltext.search:"Ottoman Bank"')
    print()

    while cursor:
        params = {
            'filter': 'fulltext.search:"Ottoman Bank"',  # EXACT PHRASE with quotes!
            'per_page': '200',
            'cursor': cursor
        }

        print(f"Fetching page {page}...")

        try:
            response = requests.get(base_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                meta = data.get('meta', {})

                all_results.extend(results)

                # Get next cursor
                next_cursor = meta.get('next_cursor')

                if next_cursor and next_cursor != cursor:
                    cursor = next_cursor
                    page += 1
                    time.sleep(0.5)  # Be polite
                else:
                    cursor = None

                print(f"  Retrieved {len(results)} papers (total so far: {len(all_results)})")

            else:
                print(f"Error: {response.status_code}")
                break

        except Exception as e:
            print(f"Error fetching data: {e}")
            break

    return all_results

def analyze_papers(papers):
    """Analyze the fetched papers to understand what we got."""

    print("\n" + "="*60)
    print("ANALYSIS OF FETCHED PAPERS")
    print("="*60)

    # Basic stats
    print(f"\nTotal papers found: {len(papers)}")

    # Check OA status
    oa_papers = [p for p in papers if p.get('open_access', {}).get('is_oa', False)]
    print(f"Open Access papers: {len(oa_papers)} ({len(oa_papers)*100/len(papers):.1f}%)")

    # Check for abstracts
    papers_with_abstracts = [p for p in papers if p.get('abstract') or p.get('abstract_inverted_index')]
    print(f"Papers with abstracts: {len(papers_with_abstracts)} ({len(papers_with_abstracts)*100/len(papers):.1f}%)")

    # Check Ottoman Bank in titles
    ottoman_in_title = 0
    for paper in papers:
        title = (paper.get('title') or '').lower()
        if 'ottoman bank' in title or 'imperial ottoman bank' in title:
            ottoman_in_title += 1

    print(f"Papers with 'Ottoman Bank' in title: {ottoman_in_title} ({ottoman_in_title*100/len(papers):.1f}%)")

    # Sample some titles
    print("\nSample of paper titles (first 10):")
    for i, paper in enumerate(papers[:10], 1):
        title = paper.get('title', 'No title')
        year = paper.get('publication_year', '?')
        print(f"  {i}. [{year}] {title[:80]}...")

    # Check year distribution
    years = [p.get('publication_year') for p in papers if p.get('publication_year')]
    if years:
        print(f"\nYear range: {min(years)} - {max(years)}")

        # Recent papers
        recent = [y for y in years if y >= 2020]
        print(f"Papers from 2020 onwards: {len(recent)}")

    # Check for Ottoman Bank in abstracts
    ottoman_in_abstract = 0
    sample_abstracts = []

    for paper in papers:
        abstract = paper.get('abstract', '')

        # Handle inverted index format
        if not abstract and paper.get('abstract_inverted_index'):
            inverted = paper.get('abstract_inverted_index', {})
            if inverted:
                try:
                    max_pos = max(max(positions) for positions in inverted.values() if positions)
                    words = [''] * (max_pos + 1)
                    for word, positions in inverted.items():
                        for pos in positions:
                            if pos < len(words):
                                words[pos] = word
                    abstract = ' '.join(words)
                except:
                    abstract = ''

        if abstract and ('ottoman bank' in abstract.lower() or 'imperial ottoman' in abstract.lower()):
            ottoman_in_abstract += 1
            if len(sample_abstracts) < 3:
                sample_abstracts.append({
                    'title': paper.get('title', 'Unknown'),
                    'year': paper.get('publication_year', '?'),
                    'abstract': abstract[:300]
                })

    print(f"\nPapers with 'Ottoman Bank' in abstract: {ottoman_in_abstract} ({ottoman_in_abstract*100/len(papers):.1f}%)")

    if sample_abstracts:
        print("\nSample abstracts mentioning Ottoman Bank:")
        for i, sample in enumerate(sample_abstracts, 1):
            print(f"\n  {i}. {sample['title'][:60]} ({sample['year']})")
            print(f"     Abstract: {sample['abstract']}...")

    return {
        'total': len(papers),
        'oa_count': len(oa_papers),
        'with_abstracts': len(papers_with_abstracts),
        'ottoman_in_title': ottoman_in_title,
        'ottoman_in_abstract': ottoman_in_abstract
    }

def main():
    """Main execution."""

    start_time = time.time()

    # Fetch papers
    papers = fetch_ottoman_bank_papers()

    if not papers:
        print("No papers fetched!")
        return

    # Analyze
    stats = analyze_papers(papers)

    # Save results
    output_file = "ottoman_bank_papers_CORRECT.json"
    output_data = {
        'metadata': {
            'search_method': 'fulltext.search:"Ottoman Bank"',
            'description': 'Papers with EXACT PHRASE "Ottoman Bank" in full text',
            'fetched_date': datetime.now().isoformat(),
            'total_papers': len(papers),
            'statistics': stats
        },
        'results': papers
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time

    print("\n" + "="*60)
    print("FETCH COMPLETE")
    print("="*60)
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Papers saved to: {output_file}")
    print(f"Total size: {Path(output_file).stat().st_size / (1024*1024):.1f} MB")

    print("\n✅ These papers ACTUALLY mention 'Ottoman Bank' as a phrase!")
    print("   Not just 'Ottoman' OR 'Bank' separately.")

if __name__ == "__main__":
    main()