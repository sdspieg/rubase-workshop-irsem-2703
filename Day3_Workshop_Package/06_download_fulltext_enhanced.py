#!/usr/bin/env python3
"""
Enhanced full-text downloader using Playwright for handling HTML pages.
Downloads PDFs directly when available, or captures HTML pages as PDFs/screenshots.

Requirements:
    pip install playwright requests
    playwright install chromium
"""

import json
import os
import sys
import time
import hashlib
import requests
import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")

# Configuration
DEFAULT_OUTPUT_DIR = "downloaded_content"
DEFAULT_LIMIT = 10
MAX_RETRIES = 3
RETRY_DELAY = 2
TIMEOUT = 30000  # 30 seconds for browser operations
CHUNK_SIZE = 8192

# Headers for direct download
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

async def try_direct_download(url: str, filepath: Path, verbose: bool = True) -> Tuple[bool, str]:
    """Try to download PDF directly without browser."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
            stream=True,
            allow_redirects=True
        )

        if response.status_code == 200:
            content = b''
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    content += chunk

            # Check if it's a PDF
            if content.startswith(b'%PDF'):
                filepath.write_bytes(content)
                if verbose:
                    size_mb = len(content) / (1024 * 1024)
                    print(f"    ✓ Direct PDF download successful ({size_mb:.1f} MB)")
                return True, "direct_pdf"

            # Check if it's HTML with PDF link
            if b'<html' in content.lower() or b'<!doctype' in content.lower():
                if verbose:
                    print(f"    → Got HTML page, will use browser to extract content")
                return False, "html_page"

        return False, f"http_{response.status_code}"

    except Exception as e:
        if verbose:
            print(f"    → Direct download failed: {str(e)[:50]}")
        return False, "error"

async def capture_with_playwright(url: str, output_dir: Path, filename_base: str,
                                 verbose: bool = True) -> Dict:
    """Use Playwright to capture content from URL."""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )

        page = await context.new_page()
        result = {
            'status': 'failed',
            'method': 'none',
            'files': []
        }

        try:
            # Navigate to page
            if verbose:
                print(f"    → Loading page with browser...")

            response = await page.goto(url, wait_until='networkidle', timeout=TIMEOUT)

            if response.status != 200 and response.status != 304:
                result['status'] = 'http_error'
                result['message'] = f'HTTP {response.status}'
                return result

            # Wait for content to load
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Extra wait for dynamic content

            # Check for PDF viewer
            if await page.locator('embed[type="application/pdf"]').count() > 0:
                if verbose:
                    print(f"    → Found embedded PDF viewer")

                # Try to find direct PDF URL
                pdf_embed = await page.locator('embed[type="application/pdf"]').first
                pdf_url = await pdf_embed.get_attribute('src')

                if pdf_url:
                    # Download the PDF directly
                    pdf_path = output_dir / f"{filename_base}.pdf"
                    success, _ = await try_direct_download(pdf_url, pdf_path, verbose=False)
                    if success:
                        result['status'] = 'success'
                        result['method'] = 'embedded_pdf'
                        result['files'].append(str(pdf_path))
                        if verbose:
                            print(f"    ✓ Extracted embedded PDF")
                        return result

            # Check for PDF in iframe
            if await page.locator('iframe').count() > 0:
                frames = page.frames
                for frame in frames[1:]:  # Skip main frame
                    if 'pdf' in frame.url.lower():
                        if verbose:
                            print(f"    → Found PDF in iframe: {frame.url}")
                        pdf_path = output_dir / f"{filename_base}.pdf"
                        success, _ = await try_direct_download(frame.url, pdf_path, verbose=False)
                        if success:
                            result['status'] = 'success'
                            result['method'] = 'iframe_pdf'
                            result['files'].append(str(pdf_path))
                            return result

            # Look for download links
            download_selectors = [
                'a[href$=".pdf"]',
                'a:has-text("Download PDF")',
                'a:has-text("Full Text")',
                'a:has-text("Download")',
                'button:has-text("Download")',
                'a[class*="download"]',
                'a[id*="download"]'
            ]

            for selector in download_selectors:
                if await page.locator(selector).count() > 0:
                    link = await page.locator(selector).first
                    href = await link.get_attribute('href')

                    if href and ('.pdf' in href.lower() or 'download' in href.lower()):
                        # Make absolute URL
                        if href.startswith('/'):
                            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                            href = base_url + href
                        elif not href.startswith('http'):
                            href = url.rsplit('/', 1)[0] + '/' + href

                        if verbose:
                            print(f"    → Found download link: {href[:50]}...")

                        pdf_path = output_dir / f"{filename_base}.pdf"
                        success, _ = await try_direct_download(href, pdf_path, verbose=False)
                        if success:
                            result['status'] = 'success'
                            result['method'] = 'download_link'
                            result['files'].append(str(pdf_path))
                            if verbose:
                                print(f"    ✓ Downloaded from link")
                            return result

            # If no PDF found, capture the page as PDF and screenshot
            if verbose:
                print(f"    → No direct PDF found, capturing page content...")

            # Take screenshot
            screenshot_path = output_dir / f"{filename_base}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            result['files'].append(str(screenshot_path))

            if verbose:
                print(f"    ✓ Saved screenshot: {screenshot_path.name}")

            # Generate PDF from page
            pdf_path = output_dir / f"{filename_base}_rendered.pdf"
            await page.pdf(
                path=str(pdf_path),
                format='A4',
                print_background=True,
                margin={'top': '1cm', 'bottom': '1cm', 'left': '1cm', 'right': '1cm'}
            )
            result['files'].append(str(pdf_path))

            if verbose:
                print(f"    ✓ Saved rendered PDF: {pdf_path.name}")

            # Extract text content
            text_content = await page.evaluate('() => document.body.innerText')
            if text_content:
                text_path = output_dir / f"{filename_base}.txt"
                text_path.write_text(text_content, encoding='utf-8')
                result['files'].append(str(text_path))

                if verbose:
                    print(f"    ✓ Saved text content: {text_path.name} ({len(text_content):,} chars)")

            result['status'] = 'success'
            result['method'] = 'page_capture'

        except asyncio.TimeoutError:
            result['status'] = 'timeout'
            result['message'] = f'Page load timeout after {TIMEOUT/1000}s'
            if verbose:
                print(f"    ✗ Timeout loading page")

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)
            if verbose:
                print(f"    ✗ Error: {str(e)[:100]}")

        finally:
            await context.close()
            await browser.close()

        return result

async def download_content(paper: Dict, output_dir: Path, verbose: bool = True) -> Dict:
    """Download content using hybrid approach: direct download first, then browser."""

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

    # Create filename base
    paper_id_clean = paper_id.replace('https://openalex.org/', '')
    filename_base = sanitize_filename(f"{paper_id_clean}_{year}")

    # Check if already processed
    existing_files = list(output_dir.glob(f"{filename_base}.*"))
    if existing_files:
        if verbose:
            print(f"  ✓ Already processed: {filename_base}")
        return {
            'paper_id': paper_id,
            'status': 'exists',
            'files': [str(f) for f in existing_files],
            'title': title
        }

    # First try direct PDF download
    pdf_path = output_dir / f"{filename_base}.pdf"
    success, method = await try_direct_download(oa_url, pdf_path, verbose)

    if success:
        return {
            'paper_id': paper_id,
            'status': 'success',
            'method': method,
            'files': [str(pdf_path)],
            'title': title
        }

    # If direct download failed and we have Playwright, use browser
    if PLAYWRIGHT_AVAILABLE and method == "html_page":
        result = await capture_with_playwright(oa_url, output_dir, filename_base, verbose)
        result['paper_id'] = paper_id
        result['title'] = title
        result['url'] = oa_url
        return result

    # Fallback if no Playwright
    return {
        'paper_id': paper_id,
        'status': 'failed',
        'message': 'Not a direct PDF and Playwright not available',
        'title': title
    }

async def download_all_content(papers: List[Dict], output_dir: Path, verbose: bool = True) -> List[Dict]:
    """Download content from all papers."""

    results = []

    for i, paper in enumerate(papers, 1):
        if verbose:
            print(f"\n[{i}/{len(papers)}] Processing: {paper.get('title', 'untitled')[:80]}...")

        result = await download_content(paper, output_dir, verbose)
        results.append(result)

        # Brief pause between downloads
        await asyncio.sleep(0.5)

    return results

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced full-text downloader with browser support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This enhanced version handles both direct PDF downloads and HTML pages.
For HTML pages, it captures screenshots, rendered PDFs, and text content.

Requirements:
  pip install playwright requests
  playwright install chromium

Examples:
  # Download first 10 papers
  python 06_download_fulltext_enhanced.py --input papers.json --limit 10

  # Download all with screenshots
  python 06_download_fulltext_enhanced.py --input papers.json --all

  # Quiet mode
  python 06_download_fulltext_enhanced.py --input papers.json --limit 5 --quiet
        """
    )

    parser.add_argument('--input', '-i', required=True,
                       help='Input JSON file with papers from OpenAlex')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_DIR,
                       help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--limit', '-l', type=int, default=DEFAULT_LIMIT,
                       help=f'Maximum number to download (default: {DEFAULT_LIMIT})')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Download all available papers')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')

    args = parser.parse_args()

    # Check Playwright
    if not PLAYWRIGHT_AVAILABLE:
        print("\n⚠️ Warning: Playwright not available. Only direct PDF downloads will work.")
        print("Install Playwright for full functionality:")
        print("  pip install playwright")
        print("  playwright install chromium\n")

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
    else:
        print(f"Error: Unexpected JSON structure")
        sys.exit(1)

    print(f"Found {len(papers):,} papers in dataset")

    # Filter for OA papers
    oa_papers = [
        p for p in papers
        if p.get('open_access', {}).get('is_oa', False)
        and p.get('open_access', {}).get('oa_url')
    ]

    print(f"Found {len(oa_papers):,} Open Access papers with URLs")

    # Apply limit
    if not args.all:
        papers_to_download = oa_papers[:args.limit]
        print(f"Limiting to first {len(papers_to_download)} papers")
    else:
        papers_to_download = oa_papers

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    print(f"Saving content to: {output_dir.absolute()}")

    # Download content
    print(f"\n⬇️ Starting download of {len(papers_to_download)} papers...")

    start_time = time.time()

    # Run async download
    results = asyncio.run(download_all_content(
        papers_to_download,
        output_dir,
        verbose=not args.quiet
    ))

    # Calculate statistics
    stats = {
        'success': sum(1 for r in results if r['status'] == 'success'),
        'exists': sum(1 for r in results if r['status'] == 'exists'),
        'failed': sum(1 for r in results if r['status'] not in ['success', 'exists']),
        'methods': {}
    }

    for r in results:
        if 'method' in r:
            method = r['method']
            stats['methods'][method] = stats['methods'].get(method, 0) + 1

    elapsed = time.time() - start_time

    # Save log
    log_file = output_dir / 'download_log_enhanced.json'
    log_data = {
        'metadata': {
            'source_file': args.input,
            'download_date': datetime.now().isoformat(),
            'total_papers': len(papers),
            'attempted': len(papers_to_download),
            'elapsed_seconds': elapsed,
            'playwright_available': PLAYWRIGHT_AVAILABLE
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

    if stats['methods']:
        print("\nDownload methods used:")
        for method, count in stats['methods'].items():
            print(f"  {method}: {count}")

    print(f"\nTime elapsed: {elapsed:.1f} seconds")
    print(f"Average speed: {len(papers_to_download)/elapsed:.1f} papers/sec")

    print(f"\n✓ Content saved to: {output_dir.absolute()}")
    print(f"✓ Log saved to: {log_file}")

if __name__ == "__main__":
    main()