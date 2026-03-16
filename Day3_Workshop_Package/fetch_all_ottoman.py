#!/usr/bin/env python3
"""
Fetch ALL Ottoman Bank results from OpenAlex using cursor pagination
"""

import json
import time
import urllib.request
import urllib.parse

def fetch_all_results():
    base_url = "https://api.openalex.org/works"
    query = "Ottoman Bank"
    per_page = 200

    # Encode the query properly
    params = {
        'filter': f'fulltext.search:{query}',
        'per_page': str(per_page),
        'cursor': '*'  # Start cursor
    }

    all_results = []
    page_count = 0
    total_expected = None

    print(f"Starting to fetch all results for: '{query}'")
    print("=" * 60)

    while True:
        # Construct URL
        url = base_url + '?' + urllib.parse.urlencode(params)

        # Fetch page
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
        except Exception as e:
            print(f"Error fetching page {page_count + 1}: {e}")
            break

        # Get metadata
        meta = data.get('meta', {})
        if total_expected is None:
            total_expected = meta.get('count', 0)
            print(f"Total results to fetch: {total_expected:,}")
            print(f"Pages needed: {(total_expected + per_page - 1) // per_page}")
            print("-" * 60)

        # Extract results
        results = data.get('results', [])
        all_results.extend(results)
        page_count += 1

        # Progress update
        print(f"Page {page_count}: Retrieved {len(results)} results | Total so far: {len(all_results):,}")

        # Check for next cursor
        next_cursor = meta.get('next_cursor')
        if not next_cursor:
            print("\nNo more results to fetch!")
            break

        # Update cursor for next request
        params['cursor'] = next_cursor

        # Rate limiting - be nice to the API
        time.sleep(0.1)  # 100ms delay between requests

        # Safety check
        if len(all_results) >= total_expected:
            print(f"\nReached expected total: {total_expected:,}")
            break

    print("=" * 60)
    print(f"\n✅ Fetching complete!")
    print(f"   Total pages fetched: {page_count}")
    print(f"   Total results retrieved: {len(all_results):,}")

    # Save to file
    output_file = 'ottoman_bank_ALL.json'
    output_data = {
        'meta': {
            'total_count': len(all_results),
            'expected_count': total_expected,
            'pages_fetched': page_count,
            'query': query
        },
        'results': all_results
    }

    print(f"\n💾 Saving to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    file_size = len(json.dumps(output_data)) / (1024 * 1024)
    print(f"✅ Saved successfully ({file_size:.2f} MB)")

    return all_results

if __name__ == "__main__":
    results = fetch_all_results()

    # Quick stats
    print("\n📊 Quick Statistics:")
    print(f"   Papers with abstracts: {sum(1 for r in results if r.get('abstract_inverted_index'))}")
    print(f"   Unique publication years: {len(set(r.get('publication_year', 0) for r in results))}")

    # Year distribution
    from collections import Counter
    years = Counter(r.get('publication_year', 0) for r in results if r.get('publication_year'))
    print(f"\n📅 Top 5 publication years:")
    for year, count in years.most_common(5):
        print(f"   {year}: {count} papers")