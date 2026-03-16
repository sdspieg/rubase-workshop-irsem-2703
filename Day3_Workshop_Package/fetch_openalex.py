#!/usr/bin/env python3
"""
OpenAlex Data Fetcher - Production Ready Version
Author: RuBase Workshop Team
Date: March 13, 2026

IMPORTANT: Correct API Usage for OpenAlex

SEARCH TYPES:
1. Basic Search (titles/abstracts): search=query
   Example: https://api.openalex.org/works?search=Ottoman%20Bank

2. Full-Text Search (entire paper): filter=fulltext.search:query
   WITHOUT QUOTES: Searches for any of the words (OR logic)
   Example: filter=fulltext.search:Ottoman Bank → finds Ottoman OR Bank (21,388 results)

   WITH QUOTES: Searches for exact phrase
   Example: filter=fulltext.search:"Ottoman Bank" → finds exact phrase (513 results)

3. Title Search Only: filter=title.search:query
   Example: https://api.openalex.org/works?filter=title.search:Ottoman%20Bank
   (Same quote rules apply for exact phrases)

PAGINATION:
- Standard: page=1,2,3... (max 10,000 results, page 50)
- Cursor: cursor=* then cursor=next_cursor (unlimited results)

This script uses CURSOR pagination to fetch ALL results.
"""

import json
import time
import sys
import argparse
from urllib.request import urlopen
from urllib.parse import urlencode, quote
from urllib.error import URLError
from datetime import datetime

def fetch_page(query, search_type='fulltext', cursor='*', per_page=200):
    """
    Fetch a single page of results from OpenAlex

    Args:
        query: Search query
        search_type: 'fulltext', 'title', or 'basic'
        cursor: Cursor for pagination ('*' for first page)
        per_page: Results per page (max 200)
    """
    base_url = "https://api.openalex.org/works"

    # Build query based on search type
    if search_type == 'fulltext':
        # For exact phrases, wrap in quotes if not already quoted
        if ' ' in query and not (query.startswith('"') and query.endswith('"')):
            # Contains spaces but not quoted - user probably wants OR search
            # To force exact phrase, use quotes
            pass
        params = {
            'filter': f'fulltext.search:{query}',
            'per_page': str(per_page),
            'cursor': cursor
        }
    elif search_type == 'title':
        params = {
            'filter': f'title.search:{query}',
            'per_page': str(per_page),
            'cursor': cursor
        }
    else:  # basic search
        params = {
            'search': query,
            'per_page': str(per_page),
            'cursor': cursor
        }

    url = base_url + '?' + urlencode(params)

    try:
        with urlopen(url) as response:
            return json.loads(response.read())
    except URLError as e:
        print(f"Error fetching page: {e}")
        return None

def fetch_all_results(query, search_type='fulltext', max_results=None, verbose=True):
    """
    Fetch all results for a query using cursor pagination

    Args:
        query: Search query
        search_type: 'fulltext', 'title', or 'basic'
        max_results: Maximum results to fetch (None for all)
        verbose: Print progress updates

    Returns:
        Dictionary with results and metadata
    """
    if verbose:
        print(f"Fetching {search_type} search results for: '{query}'")
        print("=" * 60)

    all_results = []
    cursor = '*'
    page_count = 0
    start_time = time.time()

    # First page to get total count
    data = fetch_page(query, search_type, cursor)
    if not data:
        print("Failed to fetch first page!")
        return None

    total_expected = data['meta']['count']

    if verbose:
        print(f"Total results available: {total_expected:,}")
        if max_results:
            print(f"Fetching up to: {max_results:,}")
        print(f"Estimated pages: {(min(total_expected, max_results or total_expected) + 199) // 200}")
        print("-" * 60)

    # Process first page
    all_results.extend(data['results'])
    page_count = 1

    if verbose and page_count % 10 == 0:
        print(f"Page {page_count}: {len(data['results'])} results | Total: {len(all_results):,}")

    # Continue with remaining pages
    while 'next_cursor' in data['meta'] and data['meta']['next_cursor']:
        # Check if we've reached max_results
        if max_results and len(all_results) >= max_results:
            break

        cursor = data['meta']['next_cursor']

        # Rate limiting - be nice to the API
        time.sleep(0.05)  # 50ms delay

        # Fetch next page
        data = fetch_page(query, search_type, cursor)
        if not data:
            print(f"Failed at page {page_count + 1}, saving what we have...")
            break

        all_results.extend(data['results'])
        page_count += 1

        # Progress update
        if verbose and (page_count % 10 == 0 or page_count == 1):
            elapsed = time.time() - start_time
            rate = len(all_results) / elapsed
            remaining = (total_expected - len(all_results)) / rate if rate > 0 else 0
            print(f"Page {page_count}: {len(data['results'])} results | "
                  f"Total: {len(all_results):,} | "
                  f"Rate: {rate:.0f}/s | "
                  f"ETA: {remaining:.0f}s")

    # Trim to max_results if specified
    if max_results and len(all_results) > max_results:
        all_results = all_results[:max_results]

    elapsed = time.time() - start_time

    if verbose:
        print("=" * 60)
        print(f"\n✅ Fetching complete!")
        print(f"   Pages fetched: {page_count}")
        print(f"   Total results: {len(all_results):,}")
        print(f"   Time taken: {elapsed:.1f}s")
        print(f"   Average rate: {len(all_results)/elapsed:.0f} results/s")

    # Create output structure
    output_data = {
        'meta': {
            'query': query,
            'search_type': search_type,
            'total_count': len(all_results),
            'total_available': total_expected,
            'pages_fetched': page_count,
            'fetch_date': datetime.now().isoformat(),
            'fetch_duration_seconds': round(elapsed, 2)
        },
        'results': all_results
    }

    # Quick stats
    if verbose:
        abstracts = sum(1 for r in all_results if r.get('abstract_inverted_index'))
        print(f"\n📊 Quick Statistics:")
        print(f"   Papers with abstracts: {abstracts:,} ({abstracts*100/len(all_results):.1f}%)")

        years = [r.get('publication_year') for r in all_results if r.get('publication_year')]
        if years:
            print(f"   Year range: {min(years)} - {max(years)}")

    return output_data

def main():
    parser = argparse.ArgumentParser(description='Fetch data from OpenAlex API')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--type', '-t',
                       choices=['fulltext', 'title', 'basic'],
                       default='fulltext',
                       help='Search type (default: fulltext)')
    parser.add_argument('--output', '-o',
                       help='Output file (default: query_results.json)')
    parser.add_argument('--max', '-m',
                       type=int,
                       help='Maximum results to fetch')
    parser.add_argument('--quiet', '-q',
                       action='store_true',
                       help='Suppress progress output')

    args = parser.parse_args()

    # Default output filename
    if not args.output:
        safe_query = args.query.replace(' ', '_').replace('/', '_')[:50]
        args.output = f"{safe_query}_{args.type}_results.json"

    # Fetch results
    results = fetch_all_results(
        args.query,
        search_type=args.type,
        max_results=args.max,
        verbose=not args.quiet
    )

    if not results:
        print("Failed to fetch results!")
        return 1

    # Save to file
    print(f"\n💾 Saving to: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    import os
    file_size = os.path.getsize(args.output) / (1024 * 1024)
    print(f"✅ Saved successfully ({file_size:.2f} MB)")

    return 0

if __name__ == "__main__":
    sys.exit(main())