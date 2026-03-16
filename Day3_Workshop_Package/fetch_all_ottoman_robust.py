#!/usr/bin/env python3
"""
Robust fetcher for ALL Ottoman Bank results from OpenAlex
Will fetch all 21,388 results across ~107 pages
"""

import json
import time
import sys
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError

def fetch_page(cursor='*'):
    """Fetch a single page of results"""
    base_url = "https://api.openalex.org/works"
    params = {
        'filter': 'fulltext.search:Ottoman Bank',
        'per_page': '200',
        'cursor': cursor
    }
    url = base_url + '?' + urlencode(params)

    try:
        with urlopen(url) as response:
            return json.loads(response.read())
    except URLError as e:
        print(f"Error: {e}")
        return None

def main():
    print("Starting fetch of ALL Ottoman Bank results from OpenAlex")
    print("=" * 60)

    all_results = []
    cursor = '*'
    page_count = 0

    # First page to get total count
    data = fetch_page(cursor)
    if not data:
        print("Failed to fetch first page!")
        return

    total_expected = data['meta']['count']
    print(f"Total results to fetch: {total_expected:,}")
    print(f"Estimated pages: {(total_expected + 199) // 200}")
    print("-" * 60)

    # Process first page
    all_results.extend(data['results'])
    page_count = 1
    print(f"Page {page_count}: {len(data['results'])} results | Total: {len(all_results):,}")

    # Continue with remaining pages
    while 'next_cursor' in data['meta'] and data['meta']['next_cursor']:
        cursor = data['meta']['next_cursor']

        # Small delay to be nice to API
        time.sleep(0.05)

        # Fetch next page
        data = fetch_page(cursor)
        if not data:
            print(f"Failed at page {page_count + 1}, saving what we have...")
            break

        all_results.extend(data['results'])
        page_count += 1

        # Progress update every 10 pages
        if page_count % 10 == 0:
            print(f"Page {page_count}: {len(data['results'])} results | Total: {len(all_results):,}")

    # Final page
    if page_count % 10 != 0:
        print(f"Page {page_count}: {len(data['results'])} results | Total: {len(all_results):,}")

    print("=" * 60)
    print(f"\n✅ Fetching complete!")
    print(f"   Pages fetched: {page_count}")
    print(f"   Total results: {len(all_results):,}")

    # Save results
    output_file = 'ottoman_bank_ALL.json'
    output_data = {
        'meta': {
            'total_count': len(all_results),
            'expected_count': total_expected,
            'pages_fetched': page_count,
            'query': 'fulltext.search:Ottoman Bank'
        },
        'results': all_results
    }

    print(f"\n💾 Saving to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    import os
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ Saved successfully ({file_size:.2f} MB)")

    # Quick stats
    abstracts = sum(1 for r in all_results if r.get('abstract_inverted_index'))
    print(f"\n📊 Quick Statistics:")
    print(f"   Papers with abstracts: {abstracts:,} ({abstracts*100/len(all_results):.1f}%)")

    # Get year range
    years = [r.get('publication_year') for r in all_results if r.get('publication_year')]
    if years:
        print(f"   Year range: {min(years)} - {max(years)}")

    return all_results

if __name__ == "__main__":
    results = main()