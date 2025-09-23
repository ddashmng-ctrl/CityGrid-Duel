#!/usr/bin/env python3
"""
compare_logs.py - Multi-file JSON log comparison and visualization tool

This script accepts multiple JSON files as input and plots entropy and mutual information (MI) 
metrics over time, if timestamps exist in the input files. Generated figures are saved to 
the docs/qualia/imgs/ directory for easy embedding in README.md.

Usage:
    python scripts/compare_logs.py file1.json file2.json [file3.json ...]
    
Requirements:
    - Each JSON file should contain timestamp, entropy, and mutual_information fields
    - Timestamps should be in ISO format (e.g., "2025-09-23T18:25:00Z")
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def load_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load and parse a JSON file, handling errors gracefully."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filepath}: {e}")
        return None


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime object."""
    try:
        # Handle various ISO formats
        if timestamp_str.endswith('Z'):
            return datetime.fromisoformat(timestamp_str[:-1])
        else:
            return datetime.fromisoformat(timestamp_str)
    except (ValueError, AttributeError):
        return None


def extract_data_from_files(filepaths: List[str]) -> List[Dict[str, Any]]:
    """Extract relevant data from multiple JSON files."""
    extracted_data = []
    
    for filepath in filepaths:
        data = load_json_file(filepath)
        if data is None:
            continue
            
        # Extract required fields
        entry = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'timestamp': data.get('timestamp'),
            'entropy': data.get('entropy'),
            'mutual_information': data.get('mutual_information'),
            'session_id': data.get('session_id', 'unknown')
        }
        
        # Parse timestamp if available
        if entry['timestamp']:
            parsed_time = parse_timestamp(entry['timestamp'])
            entry['datetime'] = parsed_time
        else:
            entry['datetime'] = None
            
        extracted_data.append(entry)
    
    return extracted_data


def create_plots(data: List[Dict[str, Any]], output_dir: str) -> Tuple[str, str]:
    """Create entropy and MI plots and save them to output directory."""
    
    # Check if we have timestamp data for time series plots
    has_timestamps = any(entry['datetime'] is not None for entry in data)
    
    if not has_timestamps:
        print("Warning: No valid timestamps found. Creating comparison plots without time axis.")
        return create_comparison_plots(data, output_dir)
    else:
        print(f"Creating time series plots for {len(data)} files...")
        return create_time_series_plots(data, output_dir)


def create_time_series_plots(data: List[Dict[str, Any]], output_dir: str) -> Tuple[str, str]:
    """Create time series plots for entropy and MI."""
    
    # Sort data by timestamp for proper time series
    valid_data = [entry for entry in data if entry['datetime'] is not None]
    valid_data.sort(key=lambda x: x['datetime'])
    
    # Extract data for plotting
    timestamps = [entry['datetime'] for entry in valid_data]
    entropies = [entry['entropy'] for entry in valid_data]
    mis = [entry['mutual_information'] for entry in valid_data]
    filenames = [entry['filename'] for entry in valid_data]
    
    # Create entropy plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, entropies, 'bo-', linewidth=2, markersize=8, alpha=0.7)
    
    # Add labels for each point
    for i, (ts, ent, fname) in enumerate(zip(timestamps, entropies, filenames)):
        plt.annotate(fname, (ts, ent), xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    plt.title('Entropy Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Entropy', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.tight_layout()
    
    entropy_path = os.path.join(output_dir, 'entropy_over_time.png')
    plt.savefig(entropy_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create MI plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, mis, 'ro-', linewidth=2, markersize=8, alpha=0.7)
    
    # Add labels for each point
    for i, (ts, mi, fname) in enumerate(zip(timestamps, mis, filenames)):
        plt.annotate(fname, (ts, mi), xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.8)
    
    plt.title('Mutual Information (MI) Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Mutual Information', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.tight_layout()
    
    mi_path = os.path.join(output_dir, 'mutual_information_over_time.png')
    plt.savefig(mi_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return entropy_path, mi_path


def create_comparison_plots(data: List[Dict[str, Any]], output_dir: str) -> Tuple[str, str]:
    """Create comparison bar plots when no timestamps are available."""
    
    filenames = [entry['filename'] for entry in data]
    entropies = [entry['entropy'] for entry in data]
    mis = [entry['mutual_information'] for entry in data]
    
    # Create entropy comparison plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(filenames)), entropies, alpha=0.7, color='blue')
    plt.title('Entropy Comparison Across Files', fontsize=14, fontweight='bold')
    plt.xlabel('Files', fontsize=12)
    plt.ylabel('Entropy', fontsize=12)
    plt.xticks(range(len(filenames)), filenames, rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, entropy in zip(bars, entropies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{entropy:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    entropy_path = os.path.join(output_dir, 'entropy_comparison.png')
    plt.savefig(entropy_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create MI comparison plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(filenames)), mis, alpha=0.7, color='red')
    plt.title('Mutual Information (MI) Comparison Across Files', fontsize=14, fontweight='bold')
    plt.xlabel('Files', fontsize=12)
    plt.ylabel('Mutual Information', fontsize=12)
    plt.xticks(range(len(filenames)), filenames, rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, mi in zip(bars, mis):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{mi:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    mi_path = os.path.join(output_dir, 'mutual_information_comparison.png')
    plt.savefig(mi_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return entropy_path, mi_path


def print_summary(data: List[Dict[str, Any]]):
    """Print a summary of the analyzed data."""
    print(f"\n{'='*60}")
    print(f"ANALYSIS SUMMARY - {len(data)} files processed")
    print(f"{'='*60}")
    
    for entry in data:
        print(f"\nFile: {entry['filename']}")
        print(f"  Session ID: {entry['session_id']}")
        print(f"  Timestamp: {entry['timestamp'] or 'N/A'}")
        print(f"  Entropy: {entry['entropy']:.3f}" if entry['entropy'] is not None else "  Entropy: N/A")
        print(f"  Mutual Information: {entry['mutual_information']:.3f}" if entry['mutual_information'] is not None else "  MI: N/A")
    
    # Calculate statistics if we have numeric data
    entropies = [e['entropy'] for e in data if e['entropy'] is not None]
    mis = [e['mutual_information'] for e in data if e['mutual_information'] is not None]
    
    if entropies:
        print(f"\nEntropy Statistics:")
        print(f"  Mean: {np.mean(entropies):.3f}")
        print(f"  Std:  {np.std(entropies):.3f}")
        print(f"  Min:  {np.min(entropies):.3f}")
        print(f"  Max:  {np.max(entropies):.3f}")
    
    if mis:
        print(f"\nMutual Information Statistics:")
        print(f"  Mean: {np.mean(mis):.3f}")
        print(f"  Std:  {np.std(mis):.3f}")
        print(f"  Min:  {np.min(mis):.3f}")
        print(f"  Max:  {np.max(mis):.3f}")


def main():
    """Main function to handle command line arguments and orchestrate the analysis."""
    parser = argparse.ArgumentParser(
        description='Compare and visualize entropy and MI metrics from multiple JSON log files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_2.json
  python scripts/compare_logs.py logs/*.json
  python scripts/compare_logs.py --output-dir custom_dir file1.json file2.json
        """
    )
    
    parser.add_argument('files', nargs='+', help='JSON files to analyze')
    parser.add_argument('--output-dir', '-o', default='docs/qualia/imgs',
                       help='Output directory for generated plots (default: docs/qualia/imgs)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate input files
    if len(args.files) < 1:
        print("Error: At least one JSON file must be provided.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.verbose:
        print(f"Processing {len(args.files)} files...")
        print(f"Output directory: {args.output_dir}")
    
    # Extract data from files
    data = extract_data_from_files(args.files)
    
    if not data:
        print("Error: No valid data could be extracted from the provided files.")
        sys.exit(1)
    
    # Filter out entries with missing critical data
    valid_data = [entry for entry in data if entry['entropy'] is not None and entry['mutual_information'] is not None]
    
    if not valid_data:
        print("Error: No entries with valid entropy and mutual information data found.")
        sys.exit(1)
    
    if args.verbose:
        print(f"Found {len(valid_data)} entries with valid data.")
    
    # Create plots
    entropy_plot, mi_plot = create_plots(valid_data, args.output_dir)
    
    # Print summary
    print_summary(valid_data)
    
    print(f"\n{'='*60}")
    print("PLOTS GENERATED")
    print(f"{'='*60}")
    print(f"Entropy plot: {entropy_plot}")
    print(f"MI plot: {mi_plot}")
    print(f"\nPlots saved to: {args.output_dir}")
    print("These images can now be embedded in README.md files.")


if __name__ == '__main__':
    main()