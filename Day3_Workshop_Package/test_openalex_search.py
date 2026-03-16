#!/usr/bin/env python3
"""
Test different OpenAlex search methods to understand the difference.
"""

import requests
import json

def test_search(query_type, query, limit=5):
    """Test different search approaches."""

    base_url = "https://api.openalex.org/works"

    if query_type == "no_quotes":
        # This searches for Ottoman OR Bank anywhere
        params = {
            'filter': f'fulltext.search:{query}',
            'per_page': str(limit)
        }
        desc = f"fulltext.search:{query} (NO quotes - searches Ottoman OR Bank)"

    elif query_type == "with_quotes":
        # This searches for exact phrase "Ottoman Bank"
        params = {
            'filter': f'fulltext.search:"{query}"',
            'per_page': str(limit)
        }
        desc = f'fulltext.search:"{query}" (WITH quotes - exact phrase)'

    elif query_type == "url_encoded_quotes":
        # URL-encoded version
        params = {
            'filter': f'fulltext.search:%22{query.replace(" ", "%20")}%22',
            'per_page': str(limit)
        }
        desc = f'fulltext.search:%22{query}%22 (URL-encoded quotes)'

    print(f"\n{'='*60}")
    print(f"Testing: {desc}")
    print(f"URL: {base_url}?filter={params['filter']}&per_page={params['per_page']}")

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        meta = data.get('meta', {})
        count = meta.get('count', 0)

        print(f"Results found: {count:,}")

        # Check first few results for actual Ottoman Bank mentions
        works = data.get('results', [])

        for i, work in enumerate(works[:3], 1):
            title = work.get('title', 'No title')
            abstract = work.get('abstract')

            # Check if Ottoman Bank actually appears
            ottoman_bank_in_title = 'ottoman bank' in (title or '').lower()
            ottoman_bank_in_abstract = 'ottoman bank' in (abstract or '').lower() if abstract else False

            print(f"\n  Result {i}: {title[:60]}...")
            print(f"    Ottoman Bank in title: {ottoman_bank_in_title}")
            print(f"    Ottoman Bank in abstract: {ottoman_bank_in_abstract}")

            if abstract and len(abstract) > 100:
                # Look for Ottoman or Bank separately
                ottoman_count = abstract.lower().count('ottoman')
                bank_count = abstract.lower().count('bank')
                print(f"    'Ottoman' count in abstract: {ottoman_count}")
                print(f"    'Bank' count in abstract: {bank_count}")

        return count
    else:
        print(f"Error: {response.status_code}")
        return 0

# Run tests
print("Testing OpenAlex Search Methods")
print("="*60)

# Test 1: Without quotes (what we used)
count1 = test_search("no_quotes", "Ottoman Bank")

# Test 2: With quotes (exact phrase)
count2 = test_search("with_quotes", "Ottoman Bank")

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"Without quotes (Ottoman OR Bank): {count1:,} results")
print(f"With quotes (exact phrase 'Ottoman Bank'): {count2:,} results")
print(f"Difference: {count1 - count2:,} extra results from OR search")

if count1 > count2:
    print(f"\n⚠️ We were searching with OR logic, not exact phrase!")
    print(f"This explains why papers don't actually mention 'Ottoman Bank'")
    print(f"They just mention 'Ottoman' OR 'Bank' somewhere in the text!")