#!/usr/bin/env python3
"""
Aggregate soul debate logs to generate summary statistics.
Processes all JSON log files in the logs/ directory that match the soul_debate_schema.
"""

import json
import glob
import sys
import os
from typing import List, Dict, Any
from datetime import datetime


def load_log_file(filepath: str) -> Dict[str, Any]:
    """Load and validate a soul debate log file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Validate required fields
    required_fields = ['timestamp', 'session_id', 'model', 'entropy', 'mutual_information', 'spikes']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        print(f"Warning: {filepath} missing fields: {missing_fields}", file=sys.stderr)
    
    return data


def aggregate_logs(logs_dir: str = "../../logs") -> Dict[str, Any]:
    """Aggregate statistics from all soul debate log files."""
    # Find all soul debate JSON files
    pattern = os.path.join(logs_dir, "*soul_debate*.json")
    log_files = glob.glob(pattern)
    
    # Exclude schema file
    log_files = [f for f in log_files if not f.endswith('schema.json')]
    
    if not log_files:
        print(f"No soul debate log files found in {logs_dir}")
        return {}
    
    print(f"Found {len(log_files)} log files to process")
    
    logs = []
    for filepath in sorted(log_files):
        try:
            log_data = load_log_file(filepath)
            logs.append(log_data)
            print(f"Loaded: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Error loading {filepath}: {e}", file=sys.stderr)
    
    if not logs:
        return {}
    
    # Calculate aggregated statistics
    total_logs = len(logs)
    total_tokens = sum(log.get('tokens', 0) for log in logs)
    total_spikes = sum(len(log.get('spikes', [])) for log in logs)
    
    entropies = [log.get('entropy', 0) for log in logs]
    mis = [log.get('mutual_information', 0) for log in logs]
    
    avg_entropy = sum(entropies) / len(entropies) if entropies else 0
    avg_mi = sum(mis) / len(mis) if mis else 0
    
    # Spike analysis
    all_spikes = []
    for log in logs:
        all_spikes.extend(log.get('spikes', []))
    
    spike_terms = {}
    for spike in all_spikes:
        term = spike.get('term', 'unknown')
        intensity = spike.get('intensity', 0)
        if term not in spike_terms:
            spike_terms[term] = []
        spike_terms[term].append(intensity)
    
    # Calculate average intensity per term
    spike_summary = {}
    for term, intensities in spike_terms.items():
        spike_summary[term] = {
            'count': len(intensities),
            'avg_intensity': sum(intensities) / len(intensities),
            'max_intensity': max(intensities),
            'min_intensity': min(intensities)
        }
    
    # Model breakdown
    models = {}
    for log in logs:
        model = log.get('model', 'unknown')
        if model not in models:
            models[model] = {'count': 0, 'total_tokens': 0}
        models[model]['count'] += 1
        models[model]['total_tokens'] += log.get('tokens', 0)
    
    return {
        'summary': {
            'total_logs': total_logs,
            'total_tokens': total_tokens,
            'total_spikes': total_spikes,
            'avg_entropy': round(avg_entropy, 3),
            'avg_mutual_information': round(avg_mi, 3),
            'processed_files': [os.path.basename(f) for f in sorted(log_files)]
        },
        'models': models,
        'spike_analysis': spike_summary,
        'entropy_range': {
            'min': min(entropies) if entropies else 0,
            'max': max(entropies) if entropies else 0,
            'avg': round(avg_entropy, 3)
        },
        'mi_range': {
            'min': min(mis) if mis else 0,
            'max': max(mis) if mis else 0,
            'avg': round(avg_mi, 3)
        }
    }


def main():
    """Main function to run aggregation and output results."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate soul debate logs')
    parser.add_argument('--logs-dir', default='../../logs', 
                       help='Directory containing log files (default: ../../logs)')
    parser.add_argument('--output', help='Output file for aggregated results (default: stdout)')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                       help='Output format (default: table)')
    
    args = parser.parse_args()
    
    # Run aggregation
    results = aggregate_logs(args.logs_dir)
    
    if not results:
        print("No results to display")
        return
    
    if args.format == 'json':
        output = json.dumps(results, indent=2)
    else:
        # Format as table
        output = format_table_output(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


def format_table_output(results: Dict[str, Any]) -> str:
    """Format results as readable tables."""
    output = []
    
    # Summary table
    output.append("=== SOUL DEBATE LOG AGGREGATION SUMMARY ===\n")
    summary = results['summary']
    output.append(f"Total Logs Processed: {summary['total_logs']}")
    output.append(f"Total Tokens: {summary['total_tokens']}")
    output.append(f"Total Spikes: {summary['total_spikes']}")
    output.append(f"Average Entropy: {summary['avg_entropy']}")
    output.append(f"Average Mutual Information: {summary['avg_mutual_information']}")
    output.append(f"Files Processed: {', '.join(summary['processed_files'])}")
    output.append("")
    
    # Model breakdown
    if results.get('models'):
        output.append("=== MODEL BREAKDOWN ===")
        output.append("Model           | Count | Total Tokens | Avg Tokens/Log")
        output.append("----------------|-------|--------------|---------------")
        for model, stats in results['models'].items():
            avg_tokens = stats['total_tokens'] / stats['count'] if stats['count'] > 0 else 0
            output.append(f"{model:<15} | {stats['count']:>5} | {stats['total_tokens']:>12} | {avg_tokens:>13.1f}")
        output.append("")
    
    # Spike analysis
    if results.get('spike_analysis'):
        output.append("=== SPIKE TERM ANALYSIS ===")
        output.append("Term      | Count | Avg Intensity | Max | Min")
        output.append("----------|-------|---------------|-----|----")
        for term, stats in sorted(results['spike_analysis'].items()):
            output.append(f"{term:<9} | {stats['count']:>5} | {stats['avg_intensity']:>13.3f} | {stats['max_intensity']:>3.2f} | {stats['min_intensity']:>3.2f}")
        output.append("")
    
    # Ranges
    output.append("=== METRIC RANGES ===")
    entropy = results.get('entropy_range', {})
    mi = results.get('mi_range', {})
    output.append(f"Entropy: {entropy.get('min', 0):.3f} - {entropy.get('max', 0):.3f} (avg: {entropy.get('avg', 0):.3f})")
    output.append(f"Mutual Information: {mi.get('min', 0):.3f} - {mi.get('max', 0):.3f} (avg: {mi.get('avg', 0):.3f})")
    
    return "\n".join(output)


if __name__ == "__main__":
    main()