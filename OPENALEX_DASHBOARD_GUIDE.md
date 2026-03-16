# Building Interactive OpenAlex Research Dashboards
## From API Data to Web Visualization

**Last Updated:** March 2026
**Example Dashboard:** https://sdspieg.github.io/openalex-russian-policy/
**Purpose:** Guide students through creating professional research dashboards from OpenAlex data

> **📚 Prerequisites:** First read `OPENALEX_API_STUDENT_GUIDE.md` for understanding the OpenAlex API basics, authentication, and data collection methods. This guide builds upon those foundations to create interactive visualizations.

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Collection Pipeline](#data-collection-pipeline)
4. [Data Processing & Cleaning](#data-processing--cleaning)
5. [Dashboard Generation](#dashboard-generation)
6. [Visualization Components](#visualization-components)
7. [Deployment on GitHub Pages](#deployment-on-github-pages)
8. [Complete Working Code](#complete-working-code)
9. [Customization Guide](#customization-guide)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide shows how to build a complete research dashboard like the Russian Policy Research Dashboard, which analyzes 6,196+ academic papers with interactive visualizations.

### What You'll Build
- **Multi-tab interface** with 9+ analysis sections
- **20+ interactive visualizations** using Plotly.js
- **Dark-themed professional design**
- **Sortable charts** with multiple views
- **Help modals** for user guidance
- **Mobile-responsive layout**
- **GitHub Pages deployment** (free hosting)

### Technologies Used
- **Python:** Data collection and processing
- **Plotly.js:** Interactive visualizations
- **HTML/CSS/JavaScript:** Dashboard interface
- **GitHub Pages:** Free hosting
- **OpenAlex API:** Data source

---

## Architecture

```
Project Structure:
├── scripts/
│   ├── collect_openalex_data.py    # API data collection
│   ├── process_data.py              # Data cleaning & analysis
│   └── generate_dashboard.py        # HTML generation
├── data/
│   ├── raw_papers.json              # Raw API responses
│   └── processed_analysis.json      # Cleaned data
├── index.html                       # Final dashboard
└── README.md                        # Documentation
```

---

## Data Collection Pipeline

### Step 1: Search and Collect Papers
```python
#!/usr/bin/env python3
"""
collect_openalex_data.py - Collect papers from OpenAlex API
"""

import requests
import json
import time
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm

class OpenAlexCollector:
    def __init__(self, email: str = None):
        self.base_url = "https://api.openalex.org"
        self.headers = {'mailto': email} if email else {}
        self.delay = 0.1  # Rate limiting

    def search_papers(
        self,
        search_terms: List[str],
        year_from: int = 2000,
        year_to: int = 2026,
        max_papers: int = 10000
    ) -> List[Dict]:
        """
        Collect papers matching search terms
        """
        all_papers = []

        # Build search query
        search_query = ' OR '.join([f'("{term}")' for term in search_terms])

        # Pagination
        page = 1
        per_page = 200  # Max allowed

        with tqdm(total=max_papers, desc="Collecting papers") as pbar:
            while len(all_papers) < max_papers:
                params = {
                    'search': search_query,
                    'filter': f'publication_year:{year_from}-{year_to},type:article',
                    'page': page,
                    'per_page': per_page,
                    'sort': 'publication_date:desc'
                }

                # Make request
                time.sleep(self.delay)
                response = requests.get(
                    f"{self.base_url}/works",
                    params=params,
                    headers=self.headers
                )

                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    break

                data = response.json()

                # Check if we have results
                if not data['results']:
                    break

                # Add papers
                all_papers.extend(data['results'])
                pbar.update(len(data['results']))

                # Check if more pages available
                if data['meta']['count'] <= len(all_papers):
                    break

                page += 1

        print(f"Collected {len(all_papers)} papers")
        return all_papers

    def save_papers(self, papers: List[Dict], filename: str):
        """
        Save papers to JSON file (handle large datasets)
        """
        # Split into chunks if > 100MB
        chunk_size = 2000  # Papers per chunk

        if len(papers) <= chunk_size:
            # Single file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(papers, f, ensure_ascii=False, indent=2)
            print(f"Saved to {filename}")
        else:
            # Multiple files
            for i in range(0, len(papers), chunk_size):
                chunk = papers[i:i+chunk_size]
                chunk_file = filename.replace('.json', f'_part{i//chunk_size + 1}.json')
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    json.dump(chunk, f, ensure_ascii=False, indent=2)
                print(f"Saved chunk to {chunk_file}")

def main():
    # Configuration
    SEARCH_TERMS = [
        "russian foreign policy",
        "russian defense policy",
        "russian security policy",
        "russia ukraine",
        "putin foreign policy"
    ]

    # Initialize collector
    collector = OpenAlexCollector(email="your.email@university.edu")

    # Collect papers
    papers = collector.search_papers(
        search_terms=SEARCH_TERMS,
        year_from=2000,
        year_to=2026,
        max_papers=10000
    )

    # Save results
    collector.save_papers(papers, "openalex_papers.json")

    print(f"Collection complete: {len(papers)} papers")

if __name__ == "__main__":
    main()
```

---

## Data Processing & Cleaning

### Step 2: Clean and Analyze Data
```python
#!/usr/bin/env python3
"""
process_data.py - Process and analyze collected papers
"""

import json
import pandas as pd
from collections import defaultdict, Counter
from datetime import datetime
import statistics

class DataProcessor:
    def __init__(self):
        self.papers = []
        self.analysis = {}

    def load_papers(self, filename: str):
        """
        Load papers from JSON (handles multi-part files)
        """
        import os
        import glob

        # Check for multi-part files
        if '_part' in filename:
            pattern = filename.replace('_part1', '_part*')
        else:
            pattern = filename.replace('.json', '_part*.json')

        files = glob.glob(pattern)
        if not files:
            files = [filename]

        all_papers = []
        for file in sorted(files):
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as f:
                    all_papers.extend(json.load(f))
                print(f"Loaded {file}")

        self.papers = all_papers
        print(f"Total papers loaded: {len(self.papers)}")
        return self.papers

    def clean_papers(self):
        """
        Remove invalid entries
        """
        cleaned = []
        removed_count = 0

        for paper in self.papers:
            # Skip paratext
            if paper.get('type') == 'paratext':
                removed_count += 1
                continue

            # Skip papers without titles
            if not paper.get('title'):
                removed_count += 1
                continue

            # Skip metadata entries
            title_lower = paper.get('title', '').lower()
            if any(term in title_lower for term in [
                'cover and back matter',
                'front matter',
                'cover and front matter',
                'table of contents',
                'editorial board'
            ]):
                removed_count += 1
                continue

            # Skip entries with too many authors (likely errors)
            if len(paper.get('authorships', [])) > 50:
                removed_count += 1
                continue

            # Skip retracted papers
            if paper.get('is_retracted', False):
                removed_count += 1
                continue

            cleaned.append(paper)

        print(f"Removed {removed_count} invalid entries")
        print(f"Clean dataset: {len(cleaned)} papers")
        self.papers = cleaned
        return cleaned

    def analyze_papers(self):
        """
        Comprehensive analysis of paper dataset
        """
        analysis = {
            "stats": {},
            "temporal": defaultdict(int),
            "topics": defaultdict(int),
            "sources": defaultdict(int),
            "institutions": defaultdict(int),
            "countries": defaultdict(int),
            "research_themes": defaultdict(int),
            "top_cited": [],
            "search_location": {"title_abstract": 0, "fulltext_only": 0},
            "oa_types": defaultdict(int),
            "languages": defaultdict(int),
            "taxonomy": {
                "domains": defaultdict(int),
                "fields": defaultdict(int),
                "subfields": defaultdict(int)
            },
            "authorship_distribution": defaultdict(int),
            "detailed_citation_distribution": {},
            "outward_citation_distribution": {}
        }

        # Process each paper
        citations = []
        references = []
        authors_set = set()

        for paper in self.papers:
            # Year
            year = paper.get("publication_year")
            if year:
                analysis["temporal"][year] += 1

            # Citations
            cited_count = paper.get("cited_by_count", 0)
            citations.append(cited_count)

            # References
            ref_count = len(paper.get("referenced_works", []))
            references.append(ref_count)

            # Authors
            author_count = len(paper.get("authorships", []))
            if author_count <= 5:
                analysis["authorship_distribution"][str(author_count)] += 1
            elif author_count <= 10:
                analysis["authorship_distribution"]["6-10"] += 1
            else:
                analysis["authorship_distribution"]["11+"] += 1

            # Extract authors
            for authorship in paper.get("authorships", []):
                author = authorship.get("author", {})
                if author and author.get("id"):
                    authors_set.add(author.get("id"))

                # Institutions and countries
                for inst in (authorship.get("institutions") or []):
                    if inst:
                        inst_name = inst.get("display_name")
                        if inst_name:
                            analysis["institutions"][inst_name] += 1

                        country = inst.get("country_code")
                        if country:
                            analysis["countries"][country] += 1

            # Topics
            for topic in paper.get("topics", []):
                topic_name = topic.get("display_name")
                if topic_name:
                    analysis["topics"][topic_name] += 1

            # Source/Venue
            source = paper.get("primary_location", {}).get("source")
            if source:
                source_name = source.get("display_name")
                if source_name:
                    analysis["sources"][source_name] += 1

            # Open Access
            oa_status = paper.get("open_access", {}).get("oa_status", "closed")
            analysis["oa_types"][oa_status] += 1

            # Language
            lang = paper.get("language")
            if lang:
                analysis["languages"][lang.upper()] += 1

            # Taxonomy (concepts)
            for concept in paper.get("concepts", []):
                level = concept.get("level")
                name = concept.get("display_name")
                if name:
                    if level == 0:
                        analysis["taxonomy"]["domains"][name] += 1
                    elif level == 1:
                        analysis["taxonomy"]["fields"][name] += 1
                    elif level == 2:
                        analysis["taxonomy"]["subfields"][name] += 1

        # Citation distribution
        analysis["detailed_citation_distribution"] = self._calculate_citation_distribution(citations)
        analysis["outward_citation_distribution"] = self._calculate_reference_distribution(references)

        # Top cited papers
        sorted_papers = sorted(self.papers, key=lambda x: x.get("cited_by_count", 0), reverse=True)[:20]
        for paper in sorted_papers:
            analysis["top_cited"].append({
                "title": paper.get("title", "Unknown"),
                "year": paper.get("publication_year", "Unknown"),
                "citations": paper.get("cited_by_count", 0),
                "doi": paper.get("doi"),
                "authors": self._get_author_names(paper)
            })

        # Basic stats
        analysis["stats"] = {
            "total_papers": len(self.papers),
            "total_citations": sum(citations),
            "unique_authors": len(authors_set),
            "open_access": sum(1 for p in self.papers
                             if p.get("open_access", {}).get("is_oa", False))
        }

        # Convert defaultdicts to regular dicts and sort
        for key in ["temporal", "topics", "sources", "institutions",
                   "countries", "oa_types", "languages"]:
            if key in analysis:
                analysis[key] = dict(analysis[key])

        # Sort topics and limit
        analysis["topics"] = dict(Counter(analysis["topics"]).most_common(50))
        analysis["sources"] = dict(Counter(analysis["sources"]).most_common(20))
        analysis["institutions"] = dict(Counter(analysis["institutions"]).most_common(15))
        analysis["countries"] = self._map_country_codes(
            dict(Counter(analysis["countries"]).most_common(15))
        )

        self.analysis = analysis
        return analysis

    def _calculate_citation_distribution(self, citations):
        """Calculate detailed citation distribution"""
        dist = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0,
                "6-10": 0, "11-20": 0, "21-50": 0, "51-100": 0, "100+": 0}

        for cit in citations:
            if cit == 0:
                dist["0"] += 1
            elif cit <= 5:
                dist[str(cit)] += 1
            elif cit <= 10:
                dist["6-10"] += 1
            elif cit <= 20:
                dist["11-20"] += 1
            elif cit <= 50:
                dist["21-50"] += 1
            elif cit <= 100:
                dist["51-100"] += 1
            else:
                dist["100+"] += 1

        return dist

    def _calculate_reference_distribution(self, references):
        """Calculate reference distribution"""
        dist = {"0-10": 0, "11-20": 0, "21-30": 0, "31-40": 0, "41-50": 0, "50+": 0}

        for ref in references:
            if ref <= 10:
                dist["0-10"] += 1
            elif ref <= 20:
                dist["11-20"] += 1
            elif ref <= 30:
                dist["21-30"] += 1
            elif ref <= 40:
                dist["31-40"] += 1
            elif ref <= 50:
                dist["41-50"] += 1
            else:
                dist["50+"] += 1

        return dist

    def _get_author_names(self, paper):
        """Extract author names from paper"""
        authors = []
        for authorship in paper.get("authorships", [])[:3]:  # First 3 authors
            author = authorship.get("author", {})
            if author:
                authors.append(author.get("display_name", "Unknown"))
        return " & ".join(authors) if authors else "Unknown"

    def _map_country_codes(self, country_dict):
        """Map country codes to names"""
        country_map = {
            "US": "United States", "RU": "Russia", "GB": "United Kingdom",
            "DE": "Germany", "FR": "France", "CA": "