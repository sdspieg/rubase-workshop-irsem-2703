# OpenAlex API Complete Student Guide
## Programmatic Academic Literature Search & Analysis

**Last Updated:** March 2026
**Author:** RuBase Workshop Team
**Purpose:** Enable students to programmatically search, retrieve, and analyze academic literature using the OpenAlex API

> **🚀 Next Step:** After mastering the API, see `OPENALEX_DASHBOARD_GUIDE.md` to build interactive web dashboards from your data!

---

## Table of Contents
1. [What is OpenAlex?](#what-is-openalex)
2. [Setup & Installation](#setup--installation)
3. [Basic API Concepts](#basic-api-concepts)
4. [Authentication & Rate Limits](#authentication--rate-limits)
5. [Core Search Queries](#core-search-queries)
6. [Advanced Filtering](#advanced-filtering)
7. [Data Processing & Analysis](#data-processing--analysis)
8. [Complete Working Examples](#complete-working-examples)
9. [Common Use Cases](#common-use-cases)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## What is OpenAlex?

OpenAlex is a free, open-source index of over 250 million scholarly works from around the world. It provides:
- **Papers & Citations:** Full metadata for academic publications
- **Authors & Affiliations:** Researcher profiles and institutional connections
- **Venues & Publishers:** Journal and conference information
- **Topics & Concepts:** Hierarchical subject classifications
- **Open Access Status:** Availability information for papers

### Key Advantages
- ✅ **Completely FREE** - No API key required
- ✅ **No rate limits** for polite use (10 requests/second)
- ✅ **Full metadata** including abstracts, references, citations
- ✅ **Daily updates** with new publications
- ✅ **RESTful API** with JSON responses

---

## Setup & Installation

### Prerequisites
```bash
# Install Python 3.7+
python --version  # Should be 3.7 or higher

# Create virtual environment (recommended)
python -m venv openalex_env

# Activate virtual environment
# On Windows:
openalex_env\Scripts\activate
# On Mac/Linux:
source openalex_env/bin/activate

# Install required packages
pip install requests pandas json matplotlib seaborn tqdm
```

### Basic Requirements File
Create `requirements.txt`:
```txt
requests>=2.28.0
pandas>=1.5.0
matplotlib>=3.5.0
seaborn>=0.12.0
tqdm>=4.65.0
python-dateutil>=2.8.2
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## Basic API Concepts

### API Endpoint Structure
```
https://api.openalex.org/{entity_type}?filter={filters}&search={query}
```

### Entity Types
- **works** - Academic papers, books, datasets
- **authors** - Researchers and their profiles
- **institutions** - Universities and research organizations
- **venues** - Journals, conferences, repositories
- **concepts** - Topics and subject areas
- **publishers** - Publishing houses
- **funders** - Funding organizations

### Response Format
```json
{
  "meta": {
    "count": 1234,
    "db_response_time_ms": 56,
    "page": 1,
    "per_page": 25
  },
  "results": [
    {
      "id": "https://openalex.org/W2741809807",
      "title": "Example Paper Title",
      "publication_year": 2024,
      ...
    }
  ]
}
```

---

## Authentication & Rate Limits

### Email Header (Polite Pool)
While not required, adding your email gets you into the "polite pool" with faster response times:

```python
import requests

headers = {
    'mailto': 'your.email@university.edu',
    'User-Agent': 'YourProject/1.0 (mailto:your.email@university.edu)'
}

response = requests.get(
    'https://api.openalex.org/works',
    headers=headers
)
```

### Rate Limiting Best Practices
```python
import time
from typing import List, Dict

class OpenAlexClient:
    def __init__(self, email: str = None, delay: float = 0.1):
        self.base_url = "https://api.openalex.org"
        self.delay = delay  # Seconds between requests
        self.headers = {}
        if email:
            self.headers['mailto'] = email

    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a rate-limited GET request"""
        time.sleep(self.delay)
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
```

---

## Core Search Queries

### 1. Basic Title/Abstract Search
```python
def search_papers(search_term: str, max_results: int = 100):
    """
    Search for papers by term in title and abstract
    """
    client = OpenAlexClient(email="your.email@example.com")

    params = {
        'search': search_term,
        'per_page': min(max_results, 200),  # Max 200 per page
        'filter': 'type:article'  # Only journal articles
    }

    results = client.get('works', params=params)

    papers = []
    for work in results['results']:
        papers.append({
            'id': work['id'],
            'title': work.get('title', 'No title'),
            'year': work.get('publication_year'),
            'doi': work.get('doi'),
            'citations': work.get('cited_by_count', 0),
            'open_access': work.get('open_access', {}).get('is_oa', False)
        })

    return papers

# Example usage
papers = search_papers("machine learning healthcare")
print(f"Found {len(papers)} papers")
```

### 2. Author-based Search
```python
def get_author_papers(author_name: str):
    """
    Find all papers by a specific author
    """
    client = OpenAlexClient(email="your.email@example.com")

    # First, find the author
    author_results = client.get('authors', {
        'search': author_name,
        'per_page': 5
    })

    if not author_results['results']:
        return []

    author_id = author_results['results'][0]['id']
    author_id = author_id.replace('https://openalex.org/', '')

    # Get their papers
    papers = client.get('works', {
        'filter': f'author.id:{author_id}',
        'per_page': 200,
        'sort': 'cited_by_count:desc'  # Most cited first
    })

    return papers['results']

# Example
papers = get_author_papers("Geoffrey Hinton")
```

### 3. Institution-based Search
```python
def get_institution_papers(institution_name: str, year_from: int = 2020):
    """
    Get papers from a specific institution
    """
    client = OpenAlexClient(email="your.email@example.com")

    # Find institution
    inst_results = client.get('institutions', {
        'search': institution_name,
        'per_page': 1
    })

    if not inst_results['results']:
        return []

    inst_id = inst_results['results'][0]['id']
    inst_id = inst_id.replace('https://openalex.org/', '')

    # Get papers
    papers = client.get('works', {
        'filter': f'institutions.id:{inst_id},publication_year:>{year_from-1}',
        'per_page': 200,
        'sort': 'publication_date:desc'
    })

    return papers['results']

# Example
mit_papers = get_institution_papers("MIT", 2023)
```

---

## Advanced Filtering

### Complex Filter Combinations
```python
def advanced_search(
    search_term: str,
    year_from: int = None,
    year_to: int = None,
    min_citations: int = None,
    open_access_only: bool = False,
    countries: List[str] = None,
    exclude_terms: List[str] = None
):
    """
    Advanced search with multiple filters
    """
    client = OpenAlexClient(email="your.email@example.com")

    # Build filter string
    filters = []

    if year_from:
        filters.append(f'publication_year:>{year_from-1}')
    if year_to:
        filters.append(f'publication_year:<{year_to+1}')
    if min_citations:
        filters.append(f'cited_by_count:>{min_citations-1}')
    if open_access_only:
        filters.append('open_access.is_oa:true')
    if countries:
        country_filter = '|'.join([f'institutions.country_code:{cc}' for cc in countries])
        filters.append(f'({country_filter})')

    # Build search query
    search_parts = [search_term]
    if exclude_terms:
        for term in exclude_terms:
            search_parts.append(f'-{term}')

    params = {
        'search': ' '.join(search_parts),
        'filter': ','.join(filters) if filters else None,
        'per_page': 200,
        'sort': 'relevance_score:desc'
    }

    results = client.get('works', params=params)
    return results['results']

# Example: Recent, highly-cited AI papers from US/UK, excluding "survey"
papers = advanced_search(
    search_term="artificial intelligence",
    year_from=2022,
    min_citations=10,
    open_access_only=True,
    countries=['US', 'GB'],
    exclude_terms=['survey', 'review']
)
```

### Full-text Search
```python
def fulltext_search(query: str, max_results: int = 50):
    """
    Search in full text (when available)
    """
    client = OpenAlexClient(email="your.email@example.com")

    params = {
        'filter': f'fulltext.search:{query}',
        'per_page': max_results
    }

    results = client.get('works', params=params)

    # Note: Full text is not always available
    papers_with_fulltext = []
    for work in results['results']:
        if work.get('fulltext'):
            papers_with_fulltext.append(work)

    print(f"Found {len(papers_with_fulltext)} papers with full-text matching '{query}'")
    return papers_with_fulltext
```

---

## Data Processing & Analysis

### 1. Pagination Handler
```python
def get_all_results(endpoint: str, params: Dict, max_results: int = 10000):
    """
    Handle pagination to get all results
    """
    client = OpenAlexClient(email="your.email@example.com")

    all_results = []
    page = 1
    per_page = 200  # Maximum allowed

    with tqdm(total=max_results, desc="Fetching papers") as pbar:
        while len(all_results) < max_results:
            params.update({
                'page': page,
                'per_page': per_page
            })

            response = client.get(endpoint, params)

            if not response['results']:
                break

            all_results.extend(response['results'])
            pbar.update(len(response['results']))

            page += 1

            # Check if we've got all available results
            if response['meta']['count'] <= len(all_results):
                break

    return all_results[:max_results]
```

### 2. Data Extraction and Cleaning
```python
def extract_paper_details(work: Dict) -> Dict:
    """
    Extract and clean paper metadata
    """
    # Extract authorships
    authors = []
    institutions = set()
    countries = set()

    for authorship in work.get('authorships', []):
        # Author info
        author = authorship.get('author', {})
        if author:
            authors.append({
                'id': author.get('id'),
                'name': author.get('display_name'),
                'orcid': author.get('orcid')
            })

        # Institution info
        for inst in authorship.get('institutions', []):
            if inst:
                institutions.add(inst.get('display_name'))
                if inst.get('country_code'):
                    countries.add(inst.get('country_code'))

    # Extract topics
    topics = []
    for topic in work.get('topics', []):
        topics.append({
            'name': topic.get('display_name'),
            'score': topic.get('score')
        })

    # Extract references
    references = work.get('referenced_works', [])

    return {
        'openalex_id': work.get('id'),
        'title': work.get('title'),
        'publication_year': work.get('publication_year'),
        'publication_date': work.get('publication_date'),
        'doi': work.get('doi'),
        'pmid': work.get('ids', {}).get('pmid'),
        'arxiv_id': work.get('ids', {}).get('arxiv'),

        # Venue info
        'venue': work.get('primary_location', {}).get('source', {}).get('display_name'),
        'venue_type': work.get('primary_location', {}).get('source', {}).get('type'),
        'publisher': work.get('primary_location', {}).get('source', {}).get('publisher'),

        # Authors and affiliations
        'authors': authors,
        'author_count': len(authors),
        'institutions': list(institutions),
        'countries': list(countries),
        'is_international_collab': len(countries) > 1,

        # Citations
        'cited_by_count': work.get('cited_by_count', 0),
        'references_count': len(references),
        'references': references,

        # Open Access
        'is_open_access': work.get('open_access', {}).get('is_oa', False),
        'oa_status': work.get('open_access', {}).get('oa_status'),
        'oa_url': work.get('open_access', {}).get('oa_url'),

        # Content
        'abstract': work.get('abstract'),
        'topics': topics,
        'language': work.get('language'),

        # Type
        'type': work.get('type'),
        'is_retracted': work.get('is_retracted', False),
        'is_paratext': work.get('is_paratext', False),
    }

# Example usage
def process_search_results(search_term: str):
    """
    Search and process results into clean dataset
    """
    papers = get_all_results(
        'works',
        {'search': search_term},
        max_results=1000
    )

    cleaned_papers = []
    for paper in papers:
        cleaned = extract_paper_details(paper)
        # Filter out paratext and retractions
        if not cleaned['is_paratext'] and not cleaned['is_retracted']:
            cleaned_papers.append(cleaned)

    # Convert to DataFrame
    df = pd.DataFrame(cleaned_papers)
    print(f"Processed {len(df)} valid papers")

    return df
```

### 3. Citation Network Analysis
```python
def build_citation_network(papers_df: pd.DataFrame):
    """
    Build citation relationships between papers
    """
    client = OpenAlexClient(email="your.email@example.com")

    citation_network = []
    paper_ids = set(papers_df['openalex_id'].tolist())

    for idx, paper in papers_df.iterrows():
        paper_id = paper['openalex_id']

        # Get papers that cite this one
        citing_params = {
            'filter': f'cites:{paper_id}',
            'per_page': 200
        }
        citing = client.get('works', citing_params)

        for citing_work in citing['results']:
            if citing_work['id'] in paper_ids:
                citation_network.append({
                    'source': citing_work['id'],
                    'target': paper_id,
                    'source_year': citing_work.get('publication_year'),
                    'target_year': paper['publication_year']
                })

    return pd.DataFrame(citation_network)
```

---

## Complete Working Examples

### Example 1: Complete Research Topic Analysis
```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import time

def analyze_research_topic(
    topic: str,
    years: int = 5,
    save_results: bool = True
):
    """
    Complete analysis of a research topic
    """
    print(f"Analyzing topic: {topic}")
    print("=" * 50)

    # Initialize client
    client = OpenAlexClient(email="your.email@example.com")

    # Set date range
    current_year = datetime.now().year
    year_from = current_year - years

    # Search parameters
    params = {
        'search': topic,
        'filter': f'publication_year:>{year_from-1},type:article',
        'per_page': 200
    }

    # Get papers
    print(f"\n1. Fetching papers from {year_from} to {current_year}...")
    papers = get_all_results('works', params, max_results=2000)
    print(f"   Found {len(papers)} papers")

    # Process papers
    print("\n2. Processing paper metadata...")
    processed_papers = []
    for paper in papers:
        processed_papers.append(extract_paper_details(paper))

    df = pd.DataFrame(processed_papers)

    # Remove paratext and retractions
    df = df[~df['is_paratext'] & ~df['is_retracted']]
    print(f"   {len(df)} valid papers after filtering")

    # Analysis
    print("\n3. Analyzing patterns...")

    # Temporal trends
    yearly_counts = df.groupby('publication_year').size()

    # Top venues
    top_venues = df['venue'].value_counts().head(10)

    # Top institutions
    all_institutions = []
    for institutions in df['institutions']:
        all_institutions.extend(institutions)
    institution_counts = pd.Series(all_institutions).value_counts().head(10)

    # Citation statistics
    citation_stats = {
        'mean': df['cited_by_count'].mean(),
        'median': df['cited_by_count'].median(),
        'max': df['cited_by_count'].max(),
        'total': df['cited_by_count'].sum()
    }

    # Open Access percentage
    oa_percentage = (df['is_open_access'].sum() / len(df)) * 100

    # International collaboration
    intl_collab_percentage = (df['is_international_collab'].sum() / len(df)) * 100

    # Create visualizations
    print("\n4. Creating visualizations...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Research Analysis: {topic}', fontsize=16)

    # Plot 1: Temporal trend
    axes[0, 0].plot(yearly_counts.index, yearly_counts.values, marker='o')
    axes[0, 0].set_title('Publications Over Time')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Number of Papers')
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Top venues
    axes[0, 1].barh(range(len(top_venues)), top_venues.values)
    axes[0, 1].set_yticks(range(len(top_venues)))
    axes[0, 1].set_yticklabels(top_venues.index, fontsize=8)
    axes[0, 1].set_title('Top 10 Publication Venues')
    axes[0, 1].set_xlabel('Number of Papers')

    # Plot 3: Citation distribution
    axes[1, 0].hist(df['cited_by_count'], bins=50, edgecolor='black', alpha=0.7)
    axes[1, 0].set_title('Citation Distribution')
    axes[1, 0].set_xlabel('Number of Citations')
    axes[1, 0].set_ylabel('Number of Papers')
    axes[1, 0].set_yscale('log')

    # Plot 4: Key statistics
    stats_text = f"""
    Total Papers: {len(df):,}
    Total Citations: {citation_stats['total']:,}
    Mean Citations: {citation_stats['mean']:.2f}
    Median Citations: {citation_stats['median']:.0f}
    Max Citations: {citation_stats['max']:,}

    Open Access: {oa_percentage:.1f}%
    International Collaboration: {intl_collab_percentage:.1f}%

    Top Countries:
    {', '.join(df['countries'].explode().value_counts().head(5).index.tolist())}
    """
    axes[1, 1].text(0.1, 0.5, stats_text, transform=axes[1, 1].transAxes,
                    fontsize=10, verticalalignment='center')
    axes[1, 1].axis('off')

    plt.tight_layout()

    # Save results
    if save_results:
        print("\n5. Saving results...")
        # Save data
        df.to_csv(f'{topic.replace(" ", "_")}_papers.csv', index=False)

        # Save summary
        summary = {
            'topic': topic,
            'date_range': f'{year_from}-{current_year}',
            'total_papers': len(df),
            'statistics': citation_stats,
            'oa_percentage': oa_percentage,
            'intl_collab_percentage': intl_collab_percentage,
            'top_venues': top_venues.to_dict(),
            'top_institutions': institution_counts.to_dict()
        }

        with open(f'{topic.replace(" ", "_")}_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        # Save plot
        plt.savefig(f'{topic.replace(" ", "_")}_analysis.png', dpi=300, bbox_inches='tight')
        print(f"   Saved: CSV data, JSON summary, and PNG visualization")

    plt.show()

    return df

# Run the analysis
df = analyze_research_topic("quantum computing", years=5)
```

### Example 2: Author Collaboration Network
```python
def analyze_author_network(topic: str, min_papers: int = 5):
    """
    Build and analyze co-authorship network for a topic
    """
    # Get papers
    client = OpenAlexClient(email="your.email@example.com")
    papers = get_all_results(
        'works',
        {'search': topic, 'filter': 'type:article'},
        max_results=1000
    )

    # Build co-authorship network
    collaborations = []
    author_papers = {}

    for paper in papers:
        authors = []
        for authorship in paper.get('authorships', []):
            author = authorship.get('author', {})
            if author:
                author_id = author.get('id')
                author_name = author.get('display_name')
                if author_id:
                    authors.append((author_id, author_name))
                    if author_id not in author_papers:
                        author_papers[author_id] = []
                    author_papers[author_id].append(paper.get('id'))

        # Create collaboration edges
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                collaborations.append({
                    'author1_id': authors[i][0],
                    'author1_name': authors[i][1],
                    'author2_id': authors[j][0],
                    'author2_name': authors[j][1],
                    'paper_id': paper.get('id')
                })

    # Convert to DataFrame
    collab_df = pd.DataFrame(collaborations)

    # Filter to prolific authors
    prolific_authors = {
        auth_id for auth_id, papers in author_papers.items()
        if len(papers) >= min_papers
    }

    collab_df = collab_df[
        collab_df['author1_id'].isin(prolific_authors) &
        collab_df['author2_id'].isin(prolific_authors)
    ]

    # Count collaboration strength
    collab_strength = collab_df.groupby(['author1_name', 'author2_name']).size()
    collab_strength = collab_strength.reset_index(name='collaboration_count')
    collab_strength = collab_strength.sort_values('collaboration_count', ascending=False)

    print(f"Top Collaborations in '{topic}':")
    print(collab_strength.head(10))

    return collab_strength

# Example
collaborations = analyze_author_network("machine learning", min_papers=10)
```

---

## Common Use Cases

### 1. Literature Review Automation
```python
def automated_literature_review(
    research_question: str,
    inclusion_criteria: Dict,
    exclusion_criteria: Dict
):
    """
    Automate systematic literature review process
    """
    # Initial search
    papers = advanced_search(
        search_term=research_question,
        year_from=inclusion_criteria.get('year_from', 2015),
        min_citations=inclusion_criteria.get('min_citations', 0),
        open_access_only=inclusion_criteria.get('open_access_only', False)
    )

    # Apply exclusion criteria
    filtered_papers = []
    for paper in papers:
        exclude = False

        # Check exclusion terms in title/abstract
        if exclusion_criteria.get('exclude_terms'):
            text = (paper.get('title', '') + ' ' +
                   paper.get('abstract', {}).get('value', '')).lower()
            for term in exclusion_criteria['exclude_terms']:
                if term.lower() in text:
                    exclude = True
                    break

        # Check paper type exclusions
        if exclusion_criteria.get('exclude_types'):
            if paper.get('type') in exclusion_criteria['exclude_types']:
                exclude = True

        if not exclude:
            filtered_papers.append(paper)

    # Create review summary
    review_summary = {
        'research_question': research_question,
        'papers_found': len(papers),
        'papers_after_filtering': len(filtered_papers),
        'date_conducted': datetime.now().isoformat(),
        'inclusion_criteria': inclusion_criteria,
        'exclusion_criteria': exclusion_criteria
    }

    return filtered_papers, review_summary

# Example
papers, summary = automated_literature_review(
    research_question="deep learning medical imaging diagnosis",
    inclusion_criteria={
        'year_from': 2020,
        'min_citations': 5,
        'open_access_only': True
    },
    exclusion_criteria={
        'exclude_terms': ['survey', 'review', 'editorial'],
        'exclude_types': ['paratext', 'erratum']
    }
)
```

### 2. Research Trend Detection
```python
def detect_emerging_topics(field: str, window_years: int = 2):
    """
    Identify emerging research topics in a field
    """
    client = OpenAlexClient(email="your.email@example.com")
    current_year = datetime.now().year

    # Get recent papers
    recent_papers = get_all_results(
        'works',
        {
            'search': field,
            'filter': f'publication_year:>{current_year-window_years-1}',
            'per_page': 200
        },
        max_results=2000
    )

    # Extract topics with growth rates
    topics_by_year = {}

    for paper in recent_papers:
        year = paper.get('publication_year')
        if not year:
            continue

        for topic in paper.get('topics', []):
            topic_name = topic.get('display_name')
            if topic_name:
                if topic_name not in topics_by_year:
                    topics_by_year[topic_name] = {}
                if year not in topics_by_year[topic_name]:
                    topics_by_year[topic_name][year] = 0
                topics_by_year[topic_name][year] += 1

    # Calculate growth rates
    emerging_topics = []
    for topic, years in topics_by_year.items():
        if len(years) >= 2:
            years_sorted = sorted(years.items())
            if len(years_sorted) >= 2:
                old_count = years_sorted[0][1]
                new_count = years_sorted[-1][1]
                if old_count > 0:
                    growth_rate = ((new_count - old_count) / old_count) * 100
                    emerging_topics.append({
                        'topic': topic,
                        'growth_rate': growth_rate,
                        'recent_papers': new_count,
                        'trend': 'emerging' if growth_rate > 50 else 'stable'
                    })

    # Sort by growth rate
    emerging_topics.sort(key=lambda x: x['growth_rate'], reverse=True)

    print(f"Top Emerging Topics in {field}:")
    for topic in emerging_topics[:10]:
        print(f"  {topic['topic']}: {topic['growth_rate']:.1f}% growth")

    return emerging_topics

# Example
emerging = detect_emerging_topics("artificial intelligence")
```

### 3. Institution Benchmarking
```python
def benchmark_institutions(institutions: List[str], field: str, years: int = 5):
    """
    Compare research output across institutions
    """
    client = OpenAlexClient(email="your.email@example.com")
    current_year = datetime.now().year

    benchmarks = []

    for inst_name in institutions:
        # Get institution papers
        papers = get_institution_papers(inst_name, current_year - years)

        # Filter to field
        field_papers = []
        for paper in papers:
            if field.lower() in str(paper).lower():
                field_papers.append(paper)

        # Calculate metrics
        if field_papers:
            citations = [p.get('cited_by_count', 0) for p in field_papers]
            oa_count = sum(1 for p in field_papers
                          if p.get('open_access', {}).get('is_oa', False))

            benchmarks.append({
                'institution': inst_name,
                'total_papers': len(field_papers),
                'total_citations': sum(citations),
                'mean_citations': sum(citations) / len(citations),
                'h_index': calculate_h_index(citations),
                'open_access_percentage': (oa_count / len(field_papers)) * 100
            })

    # Convert to DataFrame for comparison
    benchmark_df = pd.DataFrame(benchmarks)
    benchmark_df = benchmark_df.sort_values('h_index', ascending=False)

    # Visualize
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    x = range(len(benchmark_df))
    width = 0.35

    ax.bar([i - width/2 for i in x], benchmark_df['total_papers'],
           width, label='Total Papers')
    ax.bar([i + width/2 for i in x], benchmark_df['h_index'],
           width, label='H-Index')

    ax.set_xlabel('Institution')
    ax.set_ylabel('Count')
    ax.set_title(f'{field} Research Output Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(benchmark_df['institution'], rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.show()

    return benchmark_df

def calculate_h_index(citations: List[int]) -> int:
    """Calculate h-index from citation counts"""
    citations.sort(reverse=True)
    h_index = 0
    for i, c in enumerate(citations):
        if c >= i + 1:
            h_index = i + 1
        else:
            break
    return h_index

# Example
benchmarks = benchmark_institutions(
    ["MIT", "Stanford University", "Harvard University"],
    "computer science",
    years=5
)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Rate Limit Errors
```python
# Error: 429 Too Many Requests
# Solution: Add delays between requests

class RateLimitedClient(OpenAlexClient):
    def get(self, endpoint: str, params: Dict = None) -> Dict:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return super().get(endpoint, params)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception("Max retries exceeded")
```

#### 2. Handling Missing Data
```python
def safe_extract(data: Dict, path: str, default=None):
    """
    Safely extract nested dictionary values
    """
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    return value

# Example
title = safe_extract(paper, 'title', 'No Title')
venue = safe_extract(paper, 'primary_location.source.display_name', 'Unknown Venue')
```

#### 3. Memory Management for Large Datasets
```python
def process_large_dataset(search_term: str, chunk_size: int = 1000):
    """
    Process large datasets in chunks to manage memory
    """
    client = OpenAlexClient(email="your.email@example.com")

    # Get total count first
    count_response = client.get('works', {
        'search': search_term,
        'per_page': 1
    })
    total_count = count_response['meta']['count']

    print(f"Total papers to process: {total_count}")

    # Process in chunks
    processed_count = 0
    chunk_files = []

    for chunk_start in range(0, total_count, chunk_size):
        chunk = get_all_results(
            'works',
            {'search': search_term},
            max_results=min(chunk_size, total_count - chunk_start)
        )

        # Process chunk
        chunk_df = pd.DataFrame([extract_paper_details(p) for p in chunk])

        # Save chunk
        chunk_file = f'chunk_{processed_count//chunk_size}.parquet'
        chunk_df.to_parquet(chunk_file)
        chunk_files.append(chunk_file)

        processed_count += len(chunk)
        print(f"Processed {processed_count}/{total_count} papers")

        # Clear memory
        del chunk
        del chunk_df

    # Combine chunks if needed
    if len(chunk_files) > 1:
        print("Combining chunks...")
        all_chunks = [pd.read_parquet(f) for f in chunk_files]
        final_df = pd.concat(all_chunks, ignore_index=True)
        return final_df
    else:
        return pd.read_parquet(chunk_files[0])
```

---

## Best Practices

### 1. Efficient Querying
- **Use filters instead of post-processing** when possible
- **Request only needed fields** using `select` parameter
- **Batch requests** when getting data for multiple entities
- **Cache results** to avoid redundant API calls

### 2. Data Quality
- **Always filter out paratext** (is_paratext=false)
- **Check for retractions** (is_retracted=false)
- **Verify publication years** (some dates are estimates)
- **Handle NULL values** appropriately

### 3. Ethical Considerations
- **Respect rate limits** even though they're generous
- **Include your email** for polite pool access
- **Credit OpenAlex** in publications using their data
- **Don't overwhelm the API** with parallel requests

### 4. Code Organization
```python
# Recommended project structure
project/
├── config.py           # API settings and constants
├── client.py          # OpenAlexClient class
├── extractors.py      # Data extraction functions
├── analyzers.py       # Analysis functions
├── visualizers.py     # Plotting functions
├── data/
│   ├── raw/          # Raw API responses
│   ├── processed/    # Cleaned datasets
│   └── results/      # Analysis outputs
├── notebooks/         # Jupyter notebooks
└── requirements.txt   # Dependencies
```

---

## Additional Resources

### Related Guides
- **📊 Dashboard Creation Guide:** See `OPENALEX_DASHBOARD_GUIDE.md` in this folder for building interactive web dashboards from your OpenAlex data
- **🌐 Live Example:** https://sdspieg.github.io/openalex-russian-policy/ - A complete dashboard built using these techniques

### Official Documentation
- **OpenAlex API Docs:** https://docs.openalex.org
- **API Endpoint Reference:** https://docs.openalex.org/api-entities/works
- **Filter Documentation:** https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/filter-entity-lists

### Example Notebooks
- Complete examples available at: https://github.com/ourresearch/openalex-documentation-scripts

### Community Resources
- **OpenAlex User Group:** https://groups.google.com/g/openalex-users
- **GitHub Issues:** https://github.com/ourresearch/openalex-issues

### Citation
When using OpenAlex data, cite:
```
Priem, J., Piwowar, H., & Orr, R. (2022).
OpenAlex: A fully-open index of scholarly works, authors, venues,
institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833
```

---

## Quick Reference Card

### Most Common Operations
```python
# Search papers
client.get('works', {'search': 'your topic'})

# Get by DOI
client.get('works', {'filter': 'doi:10.1234/example'})

# Recent papers from institution
client.get('works', {
    'filter': 'institutions.display_name.search:MIT,publication_year:>2020'
})

# Highly cited papers
client.get('works', {
    'filter': 'cited_by_count:>100',
    'sort': 'cited_by_count:desc'
})

# Open Access only
client.get('works', {'filter': 'open_access.is_oa:true'})

# Multiple filters
client.get('works', {
    'filter': 'publication_year:2023,type:article,cited_by_count:>10'
})
```

---

*This guide provides everything needed to programmatically access and analyze academic literature through OpenAlex. Start with the basic examples and gradually move to more complex analyses as you become comfortable with the API.*