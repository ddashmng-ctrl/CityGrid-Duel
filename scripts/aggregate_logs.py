#!/usr/bin/env python3
"""
aggregate_logs.py - Aggregates JSON log files into a single CSV

This script combines all JSON files located in the logs/ directory and creates
a single CSV file with calculated metrics for each run.

Usage:
    python scripts/aggregate_logs.py [--logs-dir LOGS_DIR] [--output OUTPUT_CSV]

Output CSV columns:
    - run_id: Unique identifier for each run (extracted from session_id)
    - avg_entropy: Average entropy value for the run
    - max_MI: Maximum mutual information value for the run  
    - spike_count: Total number of spikes recorded for the run
"""

import json
import csv
import os
import glob
import argparse
import sys
from pathlib import Path


def load_json_file(filepath):
    """
    Load and parse a JSON file with error handling.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        dict or None: Parsed JSON data or None if invalid
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)
        return None


def extract_metrics(json_data):
    """
    Extract required metrics from JSON data.
    
    Args:
        json_data (dict): Parsed JSON data
        
    Returns:
        dict: Dictionary containing run_id, avg_entropy, max_MI, spike_count
    """
    # Extract run_id from session_id, fallback to filename if not available
    run_id = json_data.get('session_id', 'unknown')
    
    # Extract entropy (single value in the logs)
    entropy = json_data.get('entropy', 0.0)
    avg_entropy = float(entropy)
    
    # Extract mutual information (single value in the logs)
    mutual_info = json_data.get('mutual_information', 0.0)
    max_MI = float(mutual_info)
    
    # Count spikes
    spikes = json_data.get('spikes', [])
    spike_count = len(spikes) if isinstance(spikes, list) else 0
    
    return {
        'run_id': run_id,
        'avg_entropy': avg_entropy,
        'max_MI': max_MI,
        'spike_count': spike_count
    }


def aggregate_logs(logs_dir, output_csv):
    """
    Aggregate all JSON files in logs directory into a CSV file.
    
    Args:
        logs_dir (str): Path to logs directory
        output_csv (str): Path to output CSV file
    """
    # Find all JSON files in logs directory
    json_pattern = os.path.join(logs_dir, "*.json")
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"No JSON files found in {logs_dir}", file=sys.stderr)
        return
    
    # Filter out schema files (not actual log data)
    log_files = [f for f in json_files if not f.endswith('_schema.json')]
    
    print(f"Found {len(log_files)} JSON log files to process")
    
    # Collect metrics from all files
    all_metrics = []
    processed_count = 0
    error_count = 0
    
    for filepath in log_files:
        print(f"Processing: {os.path.basename(filepath)}")
        
        json_data = load_json_file(filepath)
        if json_data is None:
            error_count += 1
            continue
            
        try:
            metrics = extract_metrics(json_data)
            all_metrics.append(metrics)
            processed_count += 1
        except (KeyError, ValueError, TypeError) as e:
            print(f"Warning: Failed to extract metrics from {filepath}: {e}", file=sys.stderr)
            error_count += 1
    
    if not all_metrics:
        print("No valid metrics found to write to CSV", file=sys.stderr)
        return
    
    # Write to CSV
    fieldnames = ['run_id', 'avg_entropy', 'max_MI', 'spike_count']
    
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for metrics in all_metrics:
                writer.writerow(metrics)
        
        print(f"\nAggregation complete!")
        print(f"Successfully processed: {processed_count} files")
        print(f"Errors encountered: {error_count} files")
        print(f"Output written to: {output_csv}")
        
    except IOError as e:
        print(f"Error writing CSV file {output_csv}: {e}", file=sys.stderr)


def main():
    """Main function to handle command line arguments and orchestrate the aggregation."""
    parser = argparse.ArgumentParser(
        description="Aggregate JSON log files into a single CSV with calculated metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--logs-dir',
        default='logs',
        help='Directory containing JSON log files (default: logs)'
    )
    
    parser.add_argument(
        '--output',
        default='aggregated_logs.csv',
        help='Output CSV file path (default: aggregated_logs.csv)'
    )
    
    args = parser.parse_args()
    
    # Validate logs directory exists
    if not os.path.isdir(args.logs_dir):
        print(f"Error: Logs directory '{args.logs_dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Run aggregation
    aggregate_logs(args.logs_dir, args.output)


if __name__ == '__main__':
    main()