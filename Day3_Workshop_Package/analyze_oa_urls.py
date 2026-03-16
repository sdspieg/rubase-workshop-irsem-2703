#!/usr/bin/env python3
"""
Analyze OA URLs to understand what content types they return.
Captures HTML responses for analysis.
"""

import json
import requests
from pathlib import Path
from typing import Dict, List
import time

def analyze_url(url: str, output_dir: Path, index: int) -> Dict:
    """Fetch URL and analyze response type."""

    try:
        # Make request with redirect following
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Academic Research Bot)'},
            timeout=15,
            allow_redirects=True
        )

        # Get content type
        content_type = response.headers.get('content-type', '').lower()

        # Analyze content
        content = response.content
        content_text = response.text[:5000]  # First 5000 chars for analysis

        result = {
            'url': url,
            'final_url': response.url,
            'status_code': response.status_code,
            'content_type': content_type,
            'content_length': len(content),
            'redirected': url != response.url
        }

        # Determine content type
        if content.startswith(b'%PDF'):
            result['type'] = 'PDF'
            result['message'] = 'Direct PDF download'

        elif 'application/pdf' in content_type:
            result['type'] = 'PDF_HEADER'
            result['message'] = 'PDF by content-type header'

        elif b'<html' in content.lower() or b'<!doctype' in content.lower():
            result['type'] = 'HTML'
            result['message'] = 'HTML page'

            # Save HTML for analysis
            html_file = output_dir / f"html_{index:03d}.html"
            html_file.write_bytes(content)
            result['html_saved'] = str(html_file)

            # Look for PDF indicators in HTML
            indicators = {
                'pdf_link': '.pdf' in content_text.lower(),
                'pdf_viewer': 'pdf.js' in content_text.lower() or 'pdfviewer' in content_text.lower(),
                'embed_tag': '<embed' in content_text.lower() and 'pdf' in content_text.lower(),
                'iframe': '<iframe' in content_text.lower(),
                'download_button': 'download' in content_text.lower() and ('button' in content_text.lower() or 'href' in content_text.lower()),
                'viewcontent': 'viewcontent' in response.url.lower(),
                'springer': 'springer' in response.url.lower(),
                'elsevier': 'elsevier' in response.url.lower() or 'sciencedirect' in response.url.lower(),
                'jstor': 'jstor' in response.url.lower(),
                'repository': 'repository' in response.url.lower() or 'ir.' in response.url.lower()
            }
            result['html_indicators'] = indicators

        else:
            result['type'] = 'OTHER'
            result['message'] = f'Unknown type: {content_type}'

        return result

    except requests.exceptions.Timeout:
        return {'url': url, 'type': 'ERROR', 'message': 'Timeout'}
    except Exception as e:
        return {'url': url, 'type': 'ERROR', 'message': str(e)[:100]}

def main():
    # Load Ottoman Bank papers
    input_file = "ottoman_bank_page1.json"

    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)

    papers = data.get('results', data.get('works', []))

    # Filter for OA papers
    oa_papers = [
        p for p in papers
        if p.get('open_access', {}).get('is_oa', False)
        and p.get('open_access', {}).get('oa_url')
    ]

    print(f"Found {len(oa_papers)} OA papers")

    # Create output directory
    output_dir = Path("oa_url_analysis")
    output_dir.mkdir(exist_ok=True)

    # Analyze first 20 URLs
    limit = min(20, len(oa_papers))
    results = []

    print(f"\nAnalyzing first {limit} OA URLs...\n")

    for i, paper in enumerate(oa_papers[:limit]):
        oa_url = paper['open_access']['oa_url']
        title = paper.get('title', 'Unknown')[:80]

        print(f"[{i+1}/{limit}] Analyzing: {title}")
        print(f"  URL: {oa_url[:80]}...")

        result = analyze_url(oa_url, output_dir, i+1)
        result['paper_title'] = title
        result['paper_id'] = paper.get('id', '')
        results.append(result)

        print(f"  Type: {result['type']}")
        if result['type'] == 'HTML' and 'html_indicators' in result:
            indicators = [k for k, v in result['html_indicators'].items() if v]
            if indicators:
                print(f"  HTML indicators: {', '.join(indicators)}")

        time.sleep(0.5)  # Be polite

    # Analyze results
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    # Count types
    type_counts = {}
    for r in results:
        t = r.get('type', 'UNKNOWN')
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\nContent Types:")
    for t, count in sorted(type_counts.items()):
        print(f"  {t}: {count} ({count*100/len(results):.1f}%)")

    # For HTML pages, analyze indicators
    html_results = [r for r in results if r.get('type') == 'HTML']
    if html_results:
        print(f"\nHTML Page Analysis ({len(html_results)} pages):")

        indicator_counts = {}
        for r in html_results:
            for indicator, present in r.get('html_indicators', {}).items():
                if present:
                    indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1

        print("\nCommon patterns in HTML pages:")
        for indicator, count in sorted(indicator_counts.items(), key=lambda x: -x[1]):
            print(f"  {indicator}: {count} pages ({count*100/len(html_results):.1f}%)")

        # Show some example URLs
        print("\nExample HTML page URLs:")
        for r in html_results[:5]:
            print(f"  • {r['final_url'][:100]}")
            if r.get('html_saved'):
                print(f"    Saved as: {r['html_saved']}")

    # Save detailed results
    output_file = output_dir / "url_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'summary': type_counts,
            'total_analyzed': len(results),
            'results': results
        }, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")
    print(f"HTML files saved in: {output_dir}/")

if __name__ == "__main__":
    main()