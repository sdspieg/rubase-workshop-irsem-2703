#!/usr/bin/env python3
"""
Parse downloaded PDFs using GROBID to extract structured full text.
GROBID extracts titles, abstracts, sections, citations, and more from academic PDFs.

Requirements:
1. GROBID server running (docker or local)
2. pip install requests
"""

import json
import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grobid_parsing.log'),
        logging.StreamHandler()
    ]
)

# Configuration
GROBID_URL = os.environ.get('GROBID_URL', 'http://localhost:8070')
PDF_DIR = Path("ottoman_pdfs")
OUTPUT_DIR = Path("ottoman_fulltext")
PARSED_MANIFEST = "grobid_parsed_manifest.json"
MAX_WORKERS = 3  # GROBID can be resource-intensive
TIMEOUT = 120  # seconds per PDF

# GROBID namespaces
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def check_grobid_server() -> bool:
    """Check if GROBID server is available."""
    try:
        response = requests.get(f"{GROBID_URL}/api/isalive", timeout=5)
        return response.status_code == 200
    except:
        return False

def parse_grobid_xml(xml_content: str) -> Dict:
    """Parse GROBID TEI XML to extract structured content."""
    try:
        root = ET.fromstring(xml_content)

        # Extract title
        title_elem = root.find('.//tei:titleStmt/tei:title', NS)
        title = title_elem.text if title_elem is not None else ""

        # Extract abstract
        abstract_elem = root.find('.//tei:abstract', NS)
        abstract = ""
        if abstract_elem is not None:
            abstract_parts = abstract_elem.itertext()
            abstract = ' '.join(abstract_parts).strip()

        # Extract body text by sections
        sections = []
        body = root.find('.//tei:body', NS)
        if body is not None:
            for div in body.findall('.//tei:div', NS):
                section = {
                    'title': '',
                    'content': []
                }

                # Get section title
                head = div.find('tei:head', NS)
                if head is not None:
                    section['title'] = head.text or ''

                # Get section paragraphs
                for p in div.findall('tei:p', NS):
                    text = ' '.join(p.itertext()).strip()
                    if text:
                        section['content'].append(text)

                if section['content']:
                    sections.append(section)

        # Extract references
        references = []
        for bibl in root.findall('.//tei:listBibl/tei:biblStruct', NS):
            ref = {}

            # Title
            title_elem = bibl.find('.//tei:title', NS)
            if title_elem is not None:
                ref['title'] = title_elem.text

            # Authors
            authors = []
            for author in bibl.findall('.//tei:author/tei:persName', NS):
                forename = author.find('tei:forename', NS)
                surname = author.find('tei:surname', NS)
                if surname is not None:
                    name = surname.text or ''
                    if forename is not None and forename.text:
                        name = f"{forename.text} {name}"
                    authors.append(name.strip())
            if authors:
                ref['authors'] = authors

            # Year
            date_elem = bibl.find('.//tei:date', NS)
            if date_elem is not None:
                ref['year'] = date_elem.get('when', '')

            if ref:
                references.append(ref)

        # Combine all text for full-text search
        full_text_parts = []
        if title:
            full_text_parts.append(title)
        if abstract:
            full_text_parts.append(abstract)
        for section in sections:
            if section['title']:
                full_text_parts.append(section['title'])
            full_text_parts.extend(section['content'])

        full_text = '\n\n'.join(full_text_parts)

        return {
            'title': title,
            'abstract': abstract,
            'sections': sections,
            'references': references,
            'full_text': full_text,
            'num_sections': len(sections),
            'num_references': len(references),
            'text_length': len(full_text)
        }

    except Exception as e:
        logging.error(f"Error parsing GROBID XML: {e}")
        return None

def process_pdf_with_grobid(pdf_path: Path) -> Dict:
    """Process a single PDF with GROBID."""

    pdf_name = pdf_path.name
    paper_id = pdf_path.stem

    # Check if already processed
    output_path = OUTPUT_DIR / f"{paper_id}.json"
    if output_path.exists():
        return {
            'pdf_name': pdf_name,
            'paper_id': paper_id,
            'status': 'exists',
            'message': 'Already processed'
        }

    try:
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            files = {
                'input': (pdf_name, f, 'application/pdf')
            }

            # Call GROBID processFulltextDocument
            response = requests.post(
                f"{GROBID_URL}/api/processFulltextDocument",
                files=files,
                timeout=TIMEOUT,
                data={
                    'consolidateHeader': '1',
                    'consolidateCitations': '0',  # Faster without citation consolidation
                    'includeRawCitations': '1',
                    'teiCoordinates': '0'
                }
            )

        if response.status_code == 200:
            # Parse the TEI XML response
            parsed_content = parse_grobid_xml(response.text)

            if parsed_content:
                # Add metadata
                result = {
                    'paper_id': paper_id,
                    'pdf_name': pdf_name,
                    'pdf_size': pdf_path.stat().st_size,
                    'processed_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    **parsed_content
                }

                # Save parsed content
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                return {
                    'pdf_name': pdf_name,
                    'paper_id': paper_id,
                    'status': 'success',
                    'text_length': parsed_content['text_length'],
                    'num_sections': parsed_content['num_sections']
                }
            else:
                return {
                    'pdf_name': pdf_name,
                    'paper_id': paper_id,
                    'status': 'parse_error',
                    'message': 'Failed to parse GROBID XML'
                }

        elif response.status_code == 503:
            return {
                'pdf_name': pdf_name,
                'paper_id': paper_id,
                'status': 'server_busy',
                'message': 'GROBID server busy'
            }
        else:
            return {
                'pdf_name': pdf_name,
                'paper_id': paper_id,
                'status': 'http_error',
                'message': f'HTTP {response.status_code}'
            }

    except requests.exceptions.Timeout:
        return {
            'pdf_name': pdf_name,
            'paper_id': paper_id,
            'status': 'timeout',
            'message': f'Timeout after {TIMEOUT} seconds'
        }

    except Exception as e:
        return {
            'pdf_name': pdf_name,
            'paper_id': paper_id,
            'status': 'error',
            'message': str(e)
        }

def load_parsed_manifest() -> Dict:
    """Load existing parsing manifest if it exists."""
    if Path(PARSED_MANIFEST).exists():
        with open(PARSED_MANIFEST, 'r') as f:
            return json.load(f)
    return {
        'processed': {},
        'statistics': {}
    }

def save_parsed_manifest(manifest: Dict):
    """Save parsing manifest."""
    with open(PARSED_MANIFEST, 'w') as f:
        json.dump(manifest, f, indent=2)

def parse_all_pdfs(resume: bool = True):
    """Parse all downloaded PDFs with GROBID."""

    # Check GROBID server
    if not check_grobid_server():
        print(f"ERROR: GROBID server not available at {GROBID_URL}")
        print("\nTo start GROBID:")
        print("  docker run --rm -p 8070:8070 lfoppiano/grobid:0.7.3")
        print("\nOr set GROBID_URL environment variable:")
        print("  export GROBID_URL=http://your-grobid-server:8070")
        return

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Get list of PDFs
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    logging.info(f"Found {len(pdf_files):,} PDF files to process")

    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}")
        return

    # Load manifest for resume capability
    manifest = load_parsed_manifest() if resume else {'processed': {}, 'statistics': {}}
    processed_ids = set(manifest['processed'].keys()) if resume else set()

    # Filter out already processed if resuming
    if resume and processed_ids:
        pdfs_to_process = [p for p in pdf_files if p.stem not in processed_ids]
        logging.info(f"Resuming: {len(processed_ids):,} already processed, {len(pdfs_to_process):,} remaining")
    else:
        pdfs_to_process = pdf_files

    # Statistics
    stats = {
        'success': 0,
        'exists': 0,
        'failed': 0,
        'errors': []
    }

    # Process PDFs
    logging.info(f"Starting GROBID processing of {len(pdfs_to_process):,} PDFs...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_pdf_with_grobid, pdf_path): pdf_path
            for pdf_path in pdfs_to_process
        }

        completed = 0
        for future in as_completed(futures):
            completed += 1
            pdf_path = futures[future]
            result = future.result()

            # Update manifest
            manifest['processed'][result['paper_id']] = result

            # Update statistics
            status = result['status']
            if status == 'success':
                stats['success'] += 1
                logging.info(f"[{completed}/{len(pdfs_to_process)}] ✓ Parsed: {result['pdf_name']} "
                           f"({result['text_length']:,} chars, {result['num_sections']} sections)")
            elif status == 'exists':
                stats['exists'] += 1
            else:
                stats['failed'] += 1
                logging.warning(f"[{completed}/{len(pdfs_to_process)}] ✗ Failed: {result['pdf_name']} - {result.get('message', status)}")

            # Progress update every 50 PDFs
            if completed % 50 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed
                remaining = (len(pdfs_to_process) - completed) / rate if rate > 0 else 0

                logging.info(f"Progress: {completed}/{len(pdfs_to_process)} | "
                           f"Success: {stats['success']} | "
                           f"Failed: {stats['failed']} | "
                           f"Rate: {rate:.2f}/sec | "
                           f"ETA: {remaining/60:.1f} min")

                # Save manifest periodically
                save_parsed_manifest(manifest)

    # Final statistics
    elapsed_time = time.time() - start_time
    manifest['statistics'] = {
        'total_processed': len(pdfs_to_process),
        'success': stats['success'],
        'already_existed': stats['exists'],
        'failed': stats['failed'],
        'elapsed_time': elapsed_time,
        'pdfs_per_second': len(pdfs_to_process) / elapsed_time if elapsed_time > 0 else 0
    }

    # Save final manifest
    save_parsed_manifest(manifest)

    # Print summary
    print("\n" + "="*60)
    print("GROBID PARSING COMPLETE")
    print("="*60)
    print(f"Total processed: {len(pdfs_to_process):,}")
    print(f"Successfully parsed: {stats['success']:,}")
    print(f"Already existed: {stats['exists']:,}")
    print(f"Failed: {stats['failed']:,}")

    print(f"\nTime elapsed: {elapsed_time/60:.1f} minutes")
    print(f"Processing rate: {len(pdfs_to_process)/elapsed_time:.2f} PDFs/sec")

    # Calculate total extracted text
    total_text_length = sum(
        result.get('text_length', 0)
        for result in manifest['processed'].values()
        if result.get('status') == 'success'
    )
    print(f"Total extracted text: {total_text_length / 1e6:.1f} million characters")

    print(f"\nExtracted texts saved to: {OUTPUT_DIR.absolute()}")
    print(f"Manifest saved to: {PARSED_MANIFEST}")

    return manifest

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse PDFs with GROBID')
    parser.add_argument('--no-resume', action='store_true',
                       help='Start fresh, ignore existing parsed files')
    parser.add_argument('--workers', '-w', type=int, default=3,
                       help='Number of concurrent GROBID processes')
    parser.add_argument('--grobid-url', '-g',
                       help='GROBID server URL')

    args = parser.parse_args()

    if args.workers:
        MAX_WORKERS = args.workers

    if args.grobid_url:
        GROBID_URL = args.grobid_url

    parse_all_pdfs(resume=not args.no_resume)