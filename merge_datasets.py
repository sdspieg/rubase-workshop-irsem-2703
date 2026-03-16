#!/usr/bin/env python3
"""
Merge Ottoman Bank, Galata District Bankers, and Galata Banking datasets
for comprehensive analysis and presentation update.
"""

import json
import os
from typing import Dict, List, Set

def load_json(filepath: str) -> List[Dict]:
    """Load JSON file and return list of papers."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle different data structures
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            elif isinstance(data, list):
                return data
            else:
                print(f"Warning: Unexpected data structure in {filepath}")
                return []
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def extract_paper_info(paper: Dict, search_strategy: str) -> Dict:
    """Extract key information from a paper record."""
    # Safe extraction with None checks
    open_access_info = paper.get('open_access') or {}
    primary_location = paper.get('primary_location') or {}
    source_info = primary_location.get('source') or {}

    return {
        'id': paper.get('id', ''),
        'doi': paper.get('doi', ''),
        'title': paper.get('title', ''),
        'display_name': paper.get('display_name', ''),
        'publication_year': paper.get('publication_year'),
        'publication_date': paper.get('publication_date', ''),
        'cited_by_count': paper.get('cited_by_count', 0),
        'is_open_access': open_access_info.get('is_oa', False),
        'language': paper.get('language'),
        'abstract': paper.get('abstract_inverted_index', {}),
        'authors': [author.get('display_name', '') for author in paper.get('authorships', [])],
        'journal': source_info.get('display_name', ''),
        'search_strategy': search_strategy,
        'keywords': paper.get('keywords', []),
        'concepts': [concept.get('display_name', '') for concept in paper.get('concepts', [])]
    }

def analyze_datasets():
    """Analyze and merge the three datasets."""
    base_path = '/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston_instructors/rubase-workshop-fletcher-2603/Day3_Workshop_Package'

    # Load datasets
    print("Loading datasets...")
    ottoman_papers = load_json(f"{base_path}/ottoman_bank_papers_CORRECT.json")
    galata_bankers = load_json(f"{base_path}/galata_district_bankers.json")
    galata_banking = load_json(f"{base_path}/galata_banking.json")

    print(f"Ottoman Bank papers: {len(ottoman_papers)}")
    print(f"Galata district bankers: {len(galata_bankers)}")
    print(f"Galata banking: {len(galata_banking)}")

    # Extract and standardize paper info
    all_papers = []
    paper_ids = set()  # Track duplicates

    # Process Ottoman Bank papers
    for paper in ottoman_papers:
        paper_info = extract_paper_info(paper, "Ottoman Bank direct")
        if paper_info['id'] not in paper_ids:
            all_papers.append(paper_info)
            paper_ids.add(paper_info['id'])

    # Process Galata district bankers
    for paper in galata_bankers:
        paper_info = extract_paper_info(paper, "Galata district bankers")
        if paper_info['id'] not in paper_ids:
            all_papers.append(paper_info)
            paper_ids.add(paper_info['id'])
        else:
            # Mark as found by multiple strategies
            for existing in all_papers:
                if existing['id'] == paper_info['id']:
                    existing['search_strategy'] += " + Galata district bankers"
                    break

    # Process Galata banking
    for paper in galata_banking:
        paper_info = extract_paper_info(paper, "Galata banking")
        if paper_info['id'] not in paper_ids:
            all_papers.append(paper_info)
            paper_ids.add(paper_info['id'])
        else:
            # Mark as found by multiple strategies
            for existing in all_papers:
                if existing['id'] == paper_info['id']:
                    existing['search_strategy'] += " + Galata banking"
                    break

    # Analyze findings
    print(f"\nTotal unique papers: {len(all_papers)}")

    # Find papers only found via Galata searches
    galata_only = [p for p in all_papers if 'Ottoman Bank direct' not in p['search_strategy']]
    print(f"Papers found ONLY via Galata searches: {len(galata_only)}")

    # Find the critical Ottoman Bank director paper
    director_paper = None
    for paper in all_papers:
        title = paper.get('title', '') or ''
        title_lower = title.lower()
        if 'falconnet' in title_lower or 'ottoman bank' in title_lower:
            if 'Galata' in paper['search_strategy'] and 'Ottoman Bank direct' not in paper['search_strategy']:
                director_paper = paper
                break

    # Statistical analysis
    stats = {
        'total_unique_papers': len(all_papers),
        'ottoman_direct_count': len([p for p in all_papers if 'Ottoman Bank direct' in p['search_strategy']]),
        'galata_bankers_count': len([p for p in all_papers if 'Galata district bankers' in p['search_strategy']]),
        'galata_banking_count': len([p for p in all_papers if 'Galata banking' in p['search_strategy']]),
        'galata_only_count': len(galata_only),
        'multi_strategy_count': len([p for p in all_papers if '+' in p['search_strategy']]),
        'avg_citations_overall': sum(p['cited_by_count'] for p in all_papers) / len(all_papers),
        'open_access_percentage': (sum(1 for p in all_papers if p['is_open_access']) / len(all_papers)) * 100,
        'year_range': (
            min(p['publication_year'] for p in all_papers if p['publication_year']),
            max(p['publication_year'] for p in all_papers if p['publication_year'])
        )
    }

    # Key insights
    insights = []

    if director_paper:
        insights.append({
            'type': 'critical_discovery',
            'title': 'Ottoman Bank Director Paper Found Only via Galata Search',
            'paper': director_paper,
            'implication': 'Demonstrates indexing gaps in direct institutional searches'
        })

    if galata_only:
        insights.append({
            'type': 'search_coverage',
            'title': f'{len(galata_only)} papers found only through geographic search strategy',
            'papers': galata_only[:5],  # Top 5 examples
            'implication': 'Geographic terms reveal research missed by institutional names'
        })

    # Language analysis
    languages = {}
    for paper in all_papers:
        lang = paper.get('language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1

    if 'tr' in languages or 'turkish' in languages:
        insights.append({
            'type': 'language_indexing',
            'title': 'Turkish language papers in dataset',
            'data': languages,
            'implication': 'Non-English content may require alternative search strategies'
        })

    # Save merged dataset
    output = {
        'metadata': {
            'total_papers': len(all_papers),
            'search_strategies': ['Ottoman Bank direct', 'Galata district bankers', 'Galata banking'],
            'analysis_date': '2026-03-13',
            'statistics': stats
        },
        'insights': insights,
        'papers': all_papers
    }

    with open(f"{base_path}/merged_ottoman_galata_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nMerged analysis saved to merged_ottoman_galata_analysis.json")
    print(f"Statistics: {stats}")
    print(f"Key insights: {len(insights)}")

    return output

if __name__ == "__main__":
    analysis = analyze_datasets()