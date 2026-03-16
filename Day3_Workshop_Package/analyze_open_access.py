#!/usr/bin/env python3
"""
Analyze Open Access status of papers in the Ottoman Bank dataset.
Provides detailed statistics on OA availability and access types.
"""

import json
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any

def analyze_oa_status(input_file: str):
    """Analyze Open Access status of papers in the dataset."""

    print(f"Loading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different JSON structures
    if 'results' in data:
        papers = data['results']
    elif 'works' in data:
        papers = data['works']
    elif isinstance(data, list):
        papers = data
    else:
        print(f"Unexpected JSON structure. Keys found: {list(data.keys())}")
        return

    print(f"Total papers loaded: {len(papers):,}")

    # Initialize counters
    oa_count = 0
    oa_status_counter = Counter()
    oa_urls = []
    repository_count = 0
    year_oa_stats = {}
    oa_by_type = Counter()

    # Analyze each paper
    for paper in papers:
        # Get OA information
        oa_info = paper.get('open_access', {})
        is_oa = oa_info.get('is_oa', False)
        oa_status = oa_info.get('oa_status', 'unknown')
        oa_url = oa_info.get('oa_url', None)
        has_repository = oa_info.get('any_repository_has_fulltext', False)

        # Count OA papers
        if is_oa:
            oa_count += 1
            if oa_url:
                oa_urls.append(oa_url)

        # Track OA status types
        oa_status_counter[oa_status] += 1

        # Track repository availability
        if has_repository:
            repository_count += 1

        # Get publication year
        pub_year = paper.get('publication_year', None)
        if pub_year:
            if pub_year not in year_oa_stats:
                year_oa_stats[pub_year] = {'total': 0, 'oa': 0}
            year_oa_stats[pub_year]['total'] += 1
            if is_oa:
                year_oa_stats[pub_year]['oa'] += 1

        # Categorize OA type
        if is_oa:
            if oa_status == 'gold':
                oa_by_type['Gold OA (Publisher)'] += 1
            elif oa_status == 'green':
                oa_by_type['Green OA (Repository)'] += 1
            elif oa_status == 'hybrid':
                oa_by_type['Hybrid OA'] += 1
            elif oa_status == 'bronze':
                oa_by_type['Bronze OA (Free to read)'] += 1
            else:
                oa_by_type[f'Other ({oa_status})'] += 1

    # Print results
    print("\n" + "="*60)
    print("OPEN ACCESS STATISTICS")
    print("="*60)

    print(f"\nOverall OA Status:")
    print(f"  Open Access papers: {oa_count:,} ({oa_count*100/len(papers):.1f}%)")
    print(f"  Closed Access papers: {len(papers)-oa_count:,} ({(len(papers)-oa_count)*100/len(papers):.1f}%)")

    print(f"\nOA Status Distribution:")
    for status, count in sorted(oa_status_counter.items(), key=lambda x: -x[1]):
        print(f"  {status:20s}: {count:5,} ({count*100/len(papers):.1f}%)")

    print(f"\nOA Type Breakdown (for OA papers):")
    if oa_count > 0:
        for oa_type, count in sorted(oa_by_type.items(), key=lambda x: -x[1]):
            print(f"  {oa_type:30s}: {count:5,} ({count*100/oa_count:.1f}% of OA)")

    print(f"\nRepository Availability:")
    print(f"  Papers in repositories: {repository_count:,} ({repository_count*100/len(papers):.1f}%)")

    print(f"\nOA URLs available: {len(oa_urls):,}")
    if oa_urls:
        # Sample some OA URLs
        print(f"\nSample OA URLs (first 5):")
        for url in oa_urls[:5]:
            print(f"  - {url}")

    # Year-based analysis
    if year_oa_stats:
        print(f"\n" + "="*60)
        print("OA AVAILABILITY BY YEAR (recent 10 years)")
        print("="*60)

        recent_years = sorted([y for y in year_oa_stats.keys() if y and y > 2013])[-10:]

        print(f"\n{'Year':<6} {'Total':<8} {'OA':<8} {'OA %':<8}")
        print("-" * 30)

        for year in recent_years:
            stats = year_oa_stats[year]
            oa_percent = (stats['oa'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{year:<6} {stats['total']:<8} {stats['oa']:<8} {oa_percent:<8.1f}")

    # Calculate full-text availability estimate
    print(f"\n" + "="*60)
    print("FULL-TEXT AVAILABILITY ESTIMATE")
    print("="*60)

    # For full-text extraction, we need:
    # 1. OA papers with URLs (can potentially download)
    # 2. Papers in repositories (might be accessible)

    downloadable = len([p for p in papers
                        if p.get('open_access', {}).get('is_oa', False)
                        and p.get('open_access', {}).get('oa_url')])

    print(f"\nPotentially downloadable full-text:")
    print(f"  OA with URLs: {downloadable:,} ({downloadable*100/len(papers):.1f}%)")
    print(f"  Repository papers: {repository_count:,} ({repository_count*100/len(papers):.1f}%)")

    # Create summary for workshop
    print(f"\n" + "="*60)
    print("WORKSHOP IMPLICATIONS")
    print("="*60)

    print(f"\nFor the workshop dataset:")
    print(f"1. Only {oa_count*100/len(papers):.1f}% of papers are Open Access")
    print(f"2. We can potentially access full-text for ~{downloadable} papers")
    print(f"3. Most papers ({(len(papers)-oa_count)*100/len(papers):.1f}%) only have abstracts available")
    print(f"4. This is why we focus on abstract classification in the workshop")

    # Save detailed report
    report = {
        'metadata': {
            'analyzed_file': input_file,
            'analysis_date': datetime.now().isoformat(),
            'total_papers': len(papers)
        },
        'statistics': {
            'open_access_count': oa_count,
            'open_access_percent': oa_count*100/len(papers),
            'closed_access_count': len(papers) - oa_count,
            'repository_count': repository_count,
            'downloadable_count': downloadable
        },
        'oa_status_distribution': dict(oa_status_counter),
        'oa_type_distribution': dict(oa_by_type),
        'sample_oa_urls': oa_urls[:20] if oa_urls else []
    }

    output_file = input_file.replace('.json', '_oa_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {output_file}")

if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Analyze OA status of Ottoman Bank papers')
    parser.add_argument('--input', '-i',
                       help='Input JSON file with papers')

    args = parser.parse_args()

    # Try to find the appropriate file
    possible_files = [
        'ottoman_bank_ALL.json',
        'ottoman_bank_openalex_full.json',
        'ottoman_bank_openalex.json'
    ]

    input_file = args.input

    if not input_file:
        # Try to find a file automatically
        for filename in possible_files:
            if Path(filename).exists():
                input_file = filename
                print(f"Using found file: {filename}")
                break

    if not input_file:
        print("Error: No input file specified and no default files found")
        print("Please specify --input or ensure one of these files exists:")
        for f in possible_files:
            print(f"  - {f}")
        sys.exit(1)

    if not Path(input_file).exists():
        print(f"Error: File {input_file} not found")
        sys.exit(1)

    analyze_oa_status(input_file)