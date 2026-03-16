#!/usr/bin/env python3
"""
Generic full-text PDF downloader for OpenAlex papers.
Downloads PDFs from any OpenAlex dataset with OA URLs.

Usage:
    python 05_download_fulltext.py --input papers.json --limit 10
    python 05_download_fulltext.py --input papers.json --output pdf_dir --all
"""

import json
import os
import sys
import time
import hashlib
import requests
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
from datetime import datetime

# Configuration
DEFAULT_OUTPUT_DIR = "downloaded_pdfs"
DEFAULT_LIMIT = 10
MAX_RETRIES = 3
RETRY_DELAY = 2
TIMEOUT = 30
CHUNK_SIZE = 8192

# Headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Academic Research Bot) Research Study/1.0'
}

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename for filesystem compatibility."""
    invalid_chars = '<>:"|?*\\/\n\r\t'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext) - 3] + '...' + ext

    return filename

def download_pdf(paper: Dict, output_dir: Path, verbose: bool = True) -> Dict:
    """Download a single PDF."""

    paper_id = paper.get('id', 'unknown')
    title = paper.get('title', 'untitled')[:100]
    year = paper.get('publication_year', 'unknown')

    # Get OA URL
    oa_info = paper.get('open_access', {})
    if not oa_info.get('is_oa', False):
        return {
            'paper_id': paper_id,
            'status': 'not_oa',
            'message': 'Paper is not Open Access'
        }

    oa_url = oa_info.get('oa_url')
    if not oa_url:
        return {
            'paper_id': paper_id,
            'status': 'no_url',
            'message': 'No OA URL available'
        }

    # Create filename
    paper_id_clean = paper_id.replace('https://openalex.org/', '')
    filename = f"{paper_id_clean}_{year}.pdf"
    filename = sanitize_filename(filename)
    filepath = output_dir / filename

    # Check if already exists
    if filepath.exists():
        if verbose:
            print(f"  ✓ Already exists: {filename}")
        return {
            'paper_id': paper_id,
            'status': 'exists',
            'filename': filename
        }

    # Try to download
    for attempt in range(MAX_RETRIES):
        try:
            if verbose and attempt > 0:
                print(f"  Retry {attempt + 1}/{MAX_RETRIES} for {title[:50]}...")

            response = requests.get(
                oa_url,
                headers=HEADERS,
                timeout=TIMEOUT,
                stream=True,
                allow_redirects=True
            )

            if response.status_code == 200:
                content = b''
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        content += chunk

                # Verify it's a PDF
                if not content.startswith(b'%PDF'):
                    if verbose:
                        print(f"  ✗ Not a PDF: {title[:50]}")
                    return {
                        'paper_id': paper_id,
                        'status': 'not_pdf',
                        'message': 'Content is not a PDF'
                    }

                # Save PDF
                filepath.write_bytes(content)

                if verbose:
                    size_mb = len(content) / (1024 * 1024)
                    print(f"  ✓ Downloaded: {filename} ({size_mb:.1f} MB)")

                return {
                    'paper_id': paper_id,
                    'status': 'success',
                    'filename': filename,
                    'size': len(content),
                    'title': title
                }

            elif response.status_code == 404:
                if verbose:
                    print(f"  ✗ Not found (404): {title[:50]}")
                return {
                    'paper_id': paper_id,
                    'status': 'not_found',
                    'message': 'URL returned 404'
                }

            else:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue

                if verbose:
                    print(f"  ✗ HTTP {response.status_code}: {title[:50]}")
                return {
                    'paper_id': paper_id,
                    'status': 'http_error',
                    'message': f'HTTP {response.status_code}'
                }

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue

            if verbose:
                print(f"  ✗ Timeout: {title[:50]}")
            return {
                'paper_id': paper_id,
                'status': 'timeout',
                'message': 'Download timeout'
            }

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue

            if verbose:
                print(f"  ✗ Error: {title[:50]} - {str(e)}")
            return {
                'paper_id': paper_id,
                'status': 'error',
                'message': str(e)
            }

    return {
        'paper_id': paper_id,
        'status': 'failed',
        'message': f'Failed after {MAX_RETRIES} attempts'
    }

def main():
    parser = argparse.ArgumentParser(
        description='Download full-text PDFs from OpenAlex papers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download first 10 OA papers
  python 05_download_fulltext.py --input papers.json --limit 10

  # Download all OA papers
  python 05_download_fulltext.py --input papers.json --all

  # Download to specific directory
  python 05_download_fulltext.py --input papers.json --output my_pdfs --limit 20

  # Quiet mode (less output)
  python 05_download_fulltext.py --input papers.json --limit 10 --quiet
        """
    )

    parser.add_argument('--input', '-i', required=True,
                       help='Input JSON file with papers from OpenAlex')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_DIR,
                       help=f'Output directory for PDFs (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--limit', '-l', type=int, default=DEFAULT_LIMIT,
                       help=f'Maximum number of PDFs to download (default: {DEFAULT_LIMIT})')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Download all available PDFs (override limit)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')

    args = parser.parse_args()

    # Load input file
    if not Path(args.input).exists():
        print(f"Error: Input file {args.input} not found")
        sys.exit(1)

    print(f"\n📚 Loading papers from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract papers list
    if 'results' in data:
        papers = data['results']
    elif 'works' in data:
        papers = data['works']
    elif isinstance(data, list):
        papers = data
    elif 'chunks' in data:
        print("Error: This appears to be a chunks file, not a papers file")
        sys.exit(1)
    else:
        print(f"Error: Unexpected JSON structure. Keys found: {list(data.keys())}")
        sys.exit(1)

    print(f"Found {len(papers):,} papers in dataset")

    # Filter for OA papers
    oa_papers = [
        p for p in papers
        if p.get('open_access', {}).get('is_oa', False)
        and p.get('open_access', {}).get('oa_url')
    ]

    print(f"Found {len(oa_papers):,} Open Access papers with URLs")

    if not oa_papers:
        print("No OA papers found to download")
        sys.exit(0)

    # Apply limit
    if not args.all:
        papers_to_download = oa_papers[:args.limit]
        print(f"Limiting to first {len(papers_to_download)} papers")
    else:
        papers_to_download = oa_papers
        print(f"Downloading all {len(papers_to_download):,} OA papers")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    print(f"Saving PDFs to: {output_dir.absolute()}")

    # Download PDFs
    print(f"\n⬇️  Starting download of {len(papers_to_download)} PDFs...\n")

    results = []
    stats = {
        'success': 0,
        'exists': 0,
        'failed': 0,
        'not_oa': 0,
        'not_pdf': 0
    }

    start_time = time.time()

    for i, paper in enumerate(papers_to_download, 1):
        if not args.quiet:
            print(f"[{i}/{len(papers_to_download)}] Processing: {paper.get('title', 'untitled')[:80]}...")

        result = download_pdf(paper, output_dir, verbose=not args.quiet)
        results.append(result)

        # Update stats
        status = result['status']
        if status == 'success':
            stats['success'] += 1
        elif status == 'exists':
            stats['exists'] += 1
        else:
            stats['failed'] += 1
            if status in stats:
                stats[status] += 1

    # Calculate statistics
    elapsed = time.time() - start_time
    total_size = sum(r.get('size', 0) for r in results if r['status'] == 'success')

    # Save download log
    log_file = output_dir / 'download_log.json'
    log_data = {
        'metadata': {
            'source_file': args.input,
            'download_date': datetime.now().isoformat(),
            'total_papers': len(papers),
            'oa_papers': len(oa_papers),
            'attempted': len(papers_to_download),
            'elapsed_seconds': elapsed
        },
        'statistics': stats,
        'results': results
    }

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("📊 DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Successfully downloaded: {stats['success']}")
    print(f"Already existed: {stats['exists']}")
    print(f"Failed: {stats['failed']}")

    if stats['failed'] > 0:
        print("\nFailure breakdown:")
        for key in ['not_pdf', 'not_found', 'timeout', 'error', 'http_error']:
            if key in stats and stats[key] > 0:
                print(f"  {key}: {stats[key]}")

    print(f"\nTotal size downloaded: {total_size / (1024**2):.1f} MB")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Average speed: {len(papers_to_download)/elapsed:.1f} papers/sec")

    print(f"\n✓ PDFs saved to: {output_dir.absolute()}")
    print(f"✓ Log saved to: {log_file}")

    # Return code based on success
    if stats['success'] > 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()