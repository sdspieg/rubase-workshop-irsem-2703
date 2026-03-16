#!/usr/bin/env python3
"""
Step 4: Analyze and Visualize Results
Author: RuBase Workshop Team
Date: March 13, 2026

This script:
1. Loads annotated chunks
2. Generates coverage statistics
3. Identifies patterns and gaps
4. Creates visualizations
5. Exports for further analysis

Usage:
    python 04_analyze_results.py --input chunks_annotated.json
"""

import json
import os
import csv
import argparse
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter, defaultdict
import statistics

def load_annotations(filepath: str) -> Dict[str, Any]:
    """Load annotated chunks"""
    print(f"📂 Loading annotations from: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data['chunks'])} annotated chunks")
    return data

def analyze_coverage(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze taxonomy coverage"""
    chunks = data['chunks']
    coverage_stats = {
        'total_chunks': len(chunks),
        'annotated_chunks': 0,
        'unannotated_chunks': 0,
        'total_annotations': 0,
        'dimensions_used': defaultdict(int),
        'taxa_frequency': Counter(),
        'labels_per_chunk': [],
        'papers_covered': set()
    }

    # Process each chunk
    for chunk in chunks:
        labels = chunk.get('taxonomy_labels', [])
        num_labels = len(labels)

        coverage_stats['labels_per_chunk'].append(num_labels)

        if num_labels > 0:
            coverage_stats['annotated_chunks'] += 1
        else:
            coverage_stats['unannotated_chunks'] += 1

        coverage_stats['total_annotations'] += num_labels

        # Track paper coverage
        paper_id = chunk.get('paper_id', '')
        if paper_id:
            coverage_stats['papers_covered'].add(paper_id)

        # Process each label
        for label in labels:
            hltp = label.get('hltp', 'Unknown')
            taxon = label.get('taxon', 'Unknown')

            coverage_stats['dimensions_used'][hltp] += 1
            coverage_stats['taxa_frequency'][f"{hltp}::{taxon}"] += 1

    # Calculate statistics
    if coverage_stats['labels_per_chunk']:
        coverage_stats['avg_labels_per_chunk'] = statistics.mean(coverage_stats['labels_per_chunk'])
        coverage_stats['median_labels_per_chunk'] = statistics.median(coverage_stats['labels_per_chunk'])
        coverage_stats['max_labels_per_chunk'] = max(coverage_stats['labels_per_chunk'])
        coverage_stats['min_labels_per_chunk'] = min(coverage_stats['labels_per_chunk'])
    else:
        coverage_stats['avg_labels_per_chunk'] = 0
        coverage_stats['median_labels_per_chunk'] = 0
        coverage_stats['max_labels_per_chunk'] = 0
        coverage_stats['min_labels_per_chunk'] = 0

    coverage_stats['num_papers_covered'] = len(coverage_stats['papers_covered'])
    coverage_stats['unique_taxa_used'] = len(coverage_stats['taxa_frequency'])

    return coverage_stats

def print_analysis_report(stats: Dict[str, Any]):
    """Print detailed analysis report"""
    print("\n" + "=" * 60)
    print("📊 TAXONOMY COVERAGE ANALYSIS REPORT")
    print("=" * 60)

    print("\n📈 Overall Statistics:")
    print(f"  Total chunks analyzed: {stats['total_chunks']}")
    print(f"  Chunks with annotations: {stats['annotated_chunks']} "
          f"({stats['annotated_chunks']/stats['total_chunks']*100:.1f}%)")
    print(f"  Chunks without annotations: {stats['unannotated_chunks']} "
          f"({stats['unannotated_chunks']/stats['total_chunks']*100:.1f}%)")
    print(f"  Total papers covered: {stats['num_papers_covered']}")

    print("\n🏷️ Annotation Statistics:")
    print(f"  Total annotations applied: {stats['total_annotations']}")
    print(f"  Unique taxa used: {stats['unique_taxa_used']}")
    print(f"  Average labels per chunk: {stats['avg_labels_per_chunk']:.2f}")
    print(f"  Median labels per chunk: {stats['median_labels_per_chunk']:.1f}")
    print(f"  Max labels per chunk: {stats['max_labels_per_chunk']}")
    print(f"  Min labels per chunk: {stats['min_labels_per_chunk']}")

    print("\n🌐 Dimension Usage:")
    sorted_dims = sorted(stats['dimensions_used'].items(), key=lambda x: x[1], reverse=True)
    for dim, count in sorted_dims[:10]:
        percentage = count / stats['total_annotations'] * 100
        print(f"  {dim}: {count} ({percentage:.1f}%)")
    if len(sorted_dims) > 10:
        print(f"  ... and {len(sorted_dims)-10} more dimensions")

    print("\n🔝 Top 10 Most Frequent Taxa:")
    for taxa_key, count in stats['taxa_frequency'].most_common(10):
        percentage = count / stats['total_annotations'] * 100
        print(f"  {taxa_key}: {count} times ({percentage:.1f}%)")

    # Identify potential issues
    print("\n⚠️ Potential Issues to Review:")
    issues = []

    if stats['unannotated_chunks'] > stats['total_chunks'] * 0.3:
        issues.append(f"High percentage of unannotated chunks ({stats['unannotated_chunks']/stats['total_chunks']*100:.1f}%)")

    if stats['avg_labels_per_chunk'] < 1:
        issues.append("Low average labels per chunk - taxonomy might be too specific")

    if stats['avg_labels_per_chunk'] > 5:
        issues.append("High average labels per chunk - consider more specific filtering")

    if stats['unique_taxa_used'] < 10:
        issues.append("Very few unique taxa used - taxonomy might not fit the corpus well")

    # Check for dimension imbalance
    if sorted_dims and sorted_dims[0][1] > stats['total_annotations'] * 0.5:
        issues.append(f"Dimension '{sorted_dims[0][0]}' dominates with {sorted_dims[0][1]/stats['total_annotations']*100:.1f}% of annotations")

    if issues:
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("  ✅ No major issues detected")

def create_visualizations(stats: Dict[str, Any], output_prefix: str):
    """Create simple text-based visualizations"""
    viz_file = f"{output_prefix}_visualization.txt"
    print(f"\n📊 Creating visualizations: {viz_file}")

    with open(viz_file, 'w', encoding='utf-8') as f:
        f.write("TAXONOMY COVERAGE VISUALIZATION\n")
        f.write("=" * 60 + "\n\n")

        # Dimension usage bar chart
        f.write("Dimension Usage (Bar Chart):\n")
        f.write("-" * 40 + "\n")
        max_count = max(stats['dimensions_used'].values()) if stats['dimensions_used'] else 1
        sorted_dims = sorted(stats['dimensions_used'].items(), key=lambda x: x[1], reverse=True)

        for dim, count in sorted_dims[:15]:
            bar_length = int((count / max_count) * 30)
            bar = '█' * bar_length
            f.write(f"{dim:20} {bar} {count}\n")

        # Distribution of labels per chunk
        f.write("\n\nLabels Per Chunk Distribution:\n")
        f.write("-" * 40 + "\n")
        if stats['labels_per_chunk']:
            label_counts = Counter(stats['labels_per_chunk'])
            for num_labels in sorted(label_counts.keys()):
                count = label_counts[num_labels]
                bar_length = int((count / max(label_counts.values())) * 30)
                bar = '▓' * bar_length
                f.write(f"{num_labels} labels: {bar} {count} chunks\n")

        # Top taxa cloud
        f.write("\n\nTop Taxa Word Cloud (by frequency):\n")
        f.write("-" * 40 + "\n")
        for taxa_key, count in stats['taxa_frequency'].most_common(20):
            taxa_name = taxa_key.split('::')[-1]
            f.write(f"{taxa_name}({count}) ")
            if stats['taxa_frequency'].most_common(20).index((taxa_key, count)) % 5 == 4:
                f.write("\n")

    print("✅ Visualizations created")

def export_detailed_results(data: Dict[str, Any], stats: Dict[str, Any], output_prefix: str):
    """Export detailed results for further analysis"""

    # Export taxonomy coverage matrix
    matrix_file = f"{output_prefix}_coverage_matrix.csv"
    print(f"\n📄 Exporting coverage matrix: {matrix_file}")

    papers_taxa = defaultdict(lambda: defaultdict(int))

    for chunk in data['chunks']:
        paper_id = chunk.get('paper_id', 'unknown')
        for label in chunk.get('taxonomy_labels', []):
            taxa_key = f"{label.get('hltp', '')}::{label.get('taxon', '')}"
            papers_taxa[paper_id][taxa_key] += 1

    # Write matrix
    all_taxa = sorted(set(taxa for paper in papers_taxa.values() for taxa in paper.keys()))

    with open(matrix_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['paper_id'] + all_taxa)

        for paper_id, taxa_counts in papers_taxa.items():
            row = [paper_id] + [taxa_counts.get(taxa, 0) for taxa in all_taxa]
            writer.writerow(row)

    print(f"✅ Exported coverage matrix for {len(papers_taxa)} papers")

    # Export summary statistics
    summary_file = f"{output_prefix}_summary.json"
    print(f"\n📄 Exporting summary statistics: {summary_file}")

    summary = {
        'metadata': data['metadata'],
        'statistics': {
            'total_chunks': stats['total_chunks'],
            'annotated_chunks': stats['annotated_chunks'],
            'total_annotations': stats['total_annotations'],
            'unique_taxa': stats['unique_taxa_used'],
            'papers_covered': stats['num_papers_covered'],
            'avg_labels_per_chunk': stats['avg_labels_per_chunk']
        },
        'top_dimensions': dict(sorted(stats['dimensions_used'].items(),
                                     key=lambda x: x[1], reverse=True)[:10]),
        'top_taxa': dict(stats['taxa_frequency'].most_common(20))
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("✅ Exported summary statistics")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Analyze taxonomic annotations')
    parser.add_argument('--input', '-i',
                       help='Input annotated file',
                       default='chunks_annotated.json')
    parser.add_argument('--output-prefix', '-o',
                       help='Prefix for output files',
                       default='analysis')
    parser.add_argument('--export-all',
                       action='store_true',
                       help='Export all analysis files')

    args = parser.parse_args()

    print("=" * 60)
    print("📊 STEP 4: ANALYZE RESULTS")
    print("=" * 60)

    # Check input file
    if not os.path.exists(args.input):
        print(f"❌ Error: Annotated file '{args.input}' not found!")
        return

    # Load and analyze
    data = load_annotations(args.input)
    stats = analyze_coverage(data)

    # Print report
    print_analysis_report(stats)

    # Create visualizations
    create_visualizations(stats, args.output_prefix)

    # Export detailed results if requested
    if args.export_all:
        export_detailed_results(data, stats, args.output_prefix)

    print("\n🎉 Analysis complete!")
    print("\n📝 Next Steps:")
    print("  1. Review the analysis report above")
    print("  2. Check visualization file for patterns")
    print("  3. Import coverage matrix into Excel/Sheets for pivot tables")
    print("  4. Use summary.json for creating custom visualizations")
    print("\n💡 Consider:")
    print("  - Are there dimensions that are over/under-represented?")
    print("  - Do the patterns match your research expectations?")
    print("  - Should you refine your taxonomy based on these results?")

if __name__ == "__main__":
    main()