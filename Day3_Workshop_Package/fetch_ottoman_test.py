#!/usr/bin/env python3
"""
Test fetching Ottoman Bank results - first 5 pages only
"""

import json
import urllib.request
import urllib.parse

# Test with 5 pages first
url = "https://api.openalex.org/works?filter=fulltext.search:Ottoman%20Bank&per_page=200&cursor=*"

print("Testing fetch of first page...")
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

meta = data['meta']
print(f"Total results available: {meta['count']:,}")
print(f"First page has: {len(data['results'])} results")
print(f"Next cursor: {meta.get('next_cursor', 'none')[:50]}...")

# Calculate pages needed
total = meta['count']
per_page = 200
pages_needed = (total + per_page - 1) // per_page

print(f"\nTo get all {total:,} results:")
print(f"  Pages needed: {pages_needed}")
print(f"  Estimated time: {pages_needed * 0.1:.1f} seconds (with rate limiting)")
print(f"  Estimated data size: ~{total * 0.002:.1f} MB")

print("\nReady to fetch all? Use fetch_all_ottoman.py")