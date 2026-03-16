#!/usr/bin/env python3
"""
Download all available PDFs from the Ottoman Bank OpenAlex dataset.
Robust downloader with retry logic, progress tracking, and resume capability.
"""

import json
import os
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_download.log'),
        logging.StreamHandler()
    ]
)

# Configuration
DOWNLOAD_DIR = Path("ottoman_pdfs")
MANIFEST_FILE = "download_manifest.json"
MAX_WORKERS = 5  # Concurrent downloads
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TIMEOUT = 30  # seconds per download
CHUNK_SIZE = 8192  # bytes

# Headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Academic Research Bot) Ottoman Bank Study/1.0'
}

def get_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of content."""
    return hashlib.sha256(content).hexdigest()

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename for filesystem compatibility."""
    # Remove/replace invalid characters
    invalid_chars = '<>:"|?*\\/\n\r\t'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext) - 3] + '...' + ext

    return filename

def download_pdf(paper: Dict, download_dir: Path) -> Dict:
    """Download a single PDF with retry logic."""

    paper_id = paper.get('id', 'unknown')
    title = paper.get('title', 'untitled')
    year = paper.get('publication_year', 'unknown')

    # Get OA URL
    oa_info = paper.get('open_access', {})
    oa_url = oa_info.get('oa_url')

    if not oa_url:
        return {
            'paper_id': paper_id,
            'status': 'no_url',
            'message': 'No OA URL available'
        }

    # Create filename from paper ID
    paper_id_clean = paper_id.replace('https://openalex.org/', '')
    filename = f"{paper_id_clean}_{year}.pdf"
    filename = sanitize_filename(filename)
    filepath = download_dir / filename

    # Check if already downloaded
    if filepath.exists():
        return {
            'paper_id': paper_id,
            'status': 'exists',
            'filename': filename,
            'message': 'Already downloaded'
        }

    # Attempt download with retries
    for attempt in range(MAX_RETRIES):
        try:
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
                    # Try to find PDF link in HTML
                    if b'pdf' in content.lower() and b'href' in content.lower():
                        return {
                            'paper_id': paper_id,
                            'status': 'html_page',
                            'message': 'Got HTML page instead of PDF',
                            'oa_url': oa_url
                        }
                    return {
                        'paper_id': paper_id,
                        'status': 'not_pdf',
                        'message': 'Content is not a PDF'
                    }

                # Save PDF
                filepath.write_bytes(content)
                file_hash = get_file_hash(content)

                return {
                    'paper_id': paper_id,
                    'status': 'success',
                    'filename': filename,
                    'size': len(content),
                    'hash': file_hash,
                    'oa_url': oa_url,
                    'title': title[:100]
                }

            elif response.status_code == 404:
                return {
                    'paper_id': paper_id,
                    'status': 'not_found',
                    'message': f'URL returned 404'
                }

            else:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return {
                    'paper_id': paper_id,
                    'status': 'http_error',
                    'message': f'HTTP {response.status_code}'
                }

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return {
                'paper_id': paper_id,
                'status': 'timeout',
                'message': 'Download timeout'
            }

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
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

def load_manifest() -> Dict:
    """Load existing download manifest if it exists."""
    if Path(MANIFEST_FILE).exists():
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {
        'downloads': {},
        'statistics': {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    }

def save_manifest(manifest: Dict):
    """Save download manifest."""
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)

def download_all_pdfs(input_file: str, resume: bool = True):
    """Download all PDFs from the Ottoman Bank dataset."""

    # Create download directory
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    # Load papers
    logging.info(f"Loading papers from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    if 'results' in data:
        papers = data['results']
    elif isinstance(data, list):
        papers = data
    else:
        papers = data.get('works', [])

    # Filter for OA papers with URLs
    oa_papers = [
        p for p in papers
        if p.get('open_access', {}).get('is_oa', False)
        and p.get('open_access', {}).get('oa_url')
    ]

    logging.info(f"Found {len(oa_papers):,} OA papers with URLs out of {len(papers):,} total")

    # Load manifest for resume capability
    manifest = load_manifest() if resume else {'downloads': {}, 'statistics': {}}
    completed_ids = set(manifest['downloads'].keys()) if resume else set()

    # Filter out already downloaded if resuming
    if resume and completed_ids:
        papers_to_download = [p for p in oa_papers if p.get('id') not in completed_ids]
        logging.info(f"Resuming: {len(completed_ids):,} already processed, {len(papers_to_download):,} remaining")
    else:
        papers_to_download = oa_papers

    # Statistics
    stats = {
        'success': 0,
        'exists': 0,
        'failed': 0,
        'no_url': 0,
        'not_pdf': 0,
        'errors': []
    }

    # Download with progress tracking
    logging.info(f"Starting download of {len(papers_to_download):,} PDFs...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_pdf, paper, DOWNLOAD_DIR): paper
            for paper in papers_to_download
        }

        completed = 0
        for future in as_completed(futures):
            completed += 1
            paper = futures[future]
            result = future.result()

            # Update manifest
            manifest['downloads'][result['paper_id']] = result

            # Update statistics
            status = result['status']
            if status == 'success':
                stats['success'] += 1
                logging.info(f"[{completed}/{len(papers_to_download)}] ✓ Downloaded: {result['filename']}")
            elif status == 'exists':
                stats['exists'] += 1
            else:
                stats['failed'] += 1
                if status not in stats:
                    stats[status] = 0
                stats[status] += 1

                if status in ['error', 'timeout', 'http_error']:
                    logging.warning(f"[{completed}/{len(papers_to_download)}] ✗ Failed: {paper.get('id')} - {result['message']}")

            # Progress update every 100 papers
            if completed % 100 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed
                remaining = (len(papers_to_download) - completed) / rate if rate > 0 else 0

                logging.info(f"Progress: {completed}/{len(papers_to_download)} | "
                           f"Success: {stats['success']} | "
                           f"Failed: {stats['failed']} | "
                           f"Rate: {rate:.1f}/sec | "
                           f"ETA: {remaining/60:.1f} min")

                # Save manifest periodically
                save_manifest(manifest)

    # Final statistics
    elapsed_time = time.time() - start_time
    manifest['statistics'] = {
        'total_processed': len(papers_to_download),
        'success': stats['success'],
        'already_existed': stats['exists'],
        'failed': stats['failed'],
        'elapsed_time': elapsed_time,
        'papers_per_second': len(papers_to_download) / elapsed_time if elapsed_time > 0 else 0
    }

    # Save final manifest
    save_manifest(manifest)

    # Print summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE")
    print("="*60)
    print(f"Total processed: {len(papers_to_download):,}")
    print(f"Successfully downloaded: {stats['success']:,}")
    print(f"Already existed: {stats['exists']:,}")
    print(f"Failed: {stats['failed']:,}")

    if stats['failed'] > 0:
        print("\nFailure breakdown:")
        for status, count in stats.items():
            if status not in ['success', 'exists', 'failed', 'errors'] and count > 0:
                print(f"  {status}: {count}")

    print(f"\nTime elapsed: {elapsed_time/60:.1f} minutes")
    print(f"Download rate: {len(papers_to_download)/elapsed_time:.1f} papers/sec")

    # Calculate total size
    total_size = sum(
        result.get('size', 0)
        for result in manifest['downloads'].values()
        if result.get('status') == 'success'
    )
    print(f"Total downloaded size: {total_size / (1024**3):.2f} GB")

    print(f"\nPDFs saved to: {DOWNLOAD_DIR.absolute()}")
    print(f"Manifest saved to: {MANIFEST_FILE}")

    return manifest

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download all OA PDFs from Ottoman Bank dataset')
    parser.add_argument('--input', '-i',
                       default='ottoman_bank_ALL.json',
                       help='Input JSON file with papers')
    parser.add_argument('--no-resume', action='store_true',
                       help='Start fresh, ignore existing downloads')
    parser.add_argument('--workers', '-w', type=int, default=5,
                       help='Number of concurrent downloads')

    args = parser.parse_args()

    if args.workers:
        MAX_WORKERS = args.workers

    if not Path(args.input).exists():
        print(f"Error: Input file {args.input} not found")
        exit(1)

    download_all_pdfs(args.input, resume=not args.no_resume)