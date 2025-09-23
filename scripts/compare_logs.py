#!/usr/bin/env python3
"""
Compare and analyze JSON log files containing soul debate metrics.

This script accepts multiple JSON files as input and generates plots for
entropy and mutual information metrics over time if timestamps are available.
Generated figures are saved to the docs/qualia/imgs/ directory.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime object."""
    if timestamp_str.endswith('Z'):
        timestamp_str = timestamp_str[:-1] + '+00:00'
    return datetime.fromisoformat(timestamp_str)


def load_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load and validate a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return None


def extract_metrics(log_files: List[str]) -> pd.DataFrame:
    """Extract metrics from multiple JSON log files into a DataFrame."""
    records = []
    
    for filepath in log_files:
        data = load_json_file(filepath)
        if data is None:
            continue
            
        # Extract required fields
        record = {
            'file': os.path.basename(filepath),
            'timestamp': data.get('timestamp'),
            'entropy': data.get('entropy'),
            'mutual_information': data.get('mutual_information'),
            'session_id': data.get('session_id', 'unknown'),
            'model': data.get('model', 'unknown')
        }
        
        # Only include records with valid metrics
        if record['entropy'] is not None and record['mutual_information'] is not None:
            records.append(record)
    
    df = pd.DataFrame(records)
    
    # Parse timestamps if available
    if not df.empty and df['timestamp'].notna().any():
        df['datetime'] = df['timestamp'].apply(
            lambda x: parse_timestamp(x) if x else None
        )
        df = df.sort_values('datetime').reset_index(drop=True)
    
    return df


def plot_metrics_over_time(df: pd.DataFrame, output_dir: str) -> None:
    """Plot entropy and mutual information metrics over time."""
    if df.empty:
        print("No valid data to plot.")
        return
    
    if 'datetime' not in df.columns or df['datetime'].isna().all():
        print("No valid timestamps found. Cannot create time-series plots.")
        return
    
    # Filter out rows with invalid timestamps
    df_time = df.dropna(subset=['datetime'])
    
    if df_time.empty:
        print("No records with valid timestamps found.")
        return
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('Soul Debate Metrics Over Time', fontsize=16, fontweight='bold')
    
    # Group by file for different colors/styles
    unique_files = df_time['file'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_files)))
    
    # Plot Entropy
    ax1.set_title('Entropy Over Time', fontsize=14)
    for i, file in enumerate(unique_files):
        file_data = df_time[df_time['file'] == file]
        ax1.plot(file_data['datetime'], file_data['entropy'], 
                marker='o', linestyle='-', color=colors[i], 
                label=file, linewidth=2, markersize=6)
    
    ax1.set_ylabel('Entropy', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Plot Mutual Information
    ax2.set_title('Mutual Information Over Time', fontsize=14)
    for i, file in enumerate(unique_files):
        file_data = df_time[df_time['file'] == file]
        ax2.plot(file_data['datetime'], file_data['mutual_information'], 
                marker='s', linestyle='-', color=colors[i], 
                label=file, linewidth=2, markersize=6)
    
    ax2.set_ylabel('Mutual Information', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(output_dir, 'soul_debate_metrics_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Time-series plot saved to: {output_path}")
    plt.close()


def print_summary_stats(df: pd.DataFrame) -> None:
    """Print summary statistics for the loaded data."""
    if df.empty:
        print("No valid data found.")
        return
    
    print("\n=== Summary Statistics ===")
    print(f"Total files processed: {df['file'].nunique()}")
    print(f"Total records: {len(df)}")
    
    if 'datetime' in df.columns:
        valid_timestamps = df['datetime'].notna().sum()
        print(f"Records with valid timestamps: {valid_timestamps}")
    
    print("\nMetrics by file:")
    summary = df.groupby('file').agg({
        'entropy': ['mean', 'std', 'min', 'max'],
        'mutual_information': ['mean', 'std', 'min', 'max']
    }).round(4)
    
    print(summary)
    
    # Overall statistics
    print("\nOverall statistics:")
    print(f"Entropy: mean={df['entropy'].mean():.4f}, std={df['entropy'].std():.4f}")
    print(f"Mutual Information: mean={df['mutual_information'].mean():.4f}, std={df['mutual_information'].std():.4f}")


def main():
    """Main function to parse arguments and execute comparison."""
    parser = argparse.ArgumentParser(
        description="Compare and analyze multiple JSON log files containing soul debate metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_2.json
  python scripts/compare_logs.py logs/*.json --output-dir custom/output/
  python scripts/compare_logs.py logs/example_*.json --no-plots
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='JSON log files to compare (accepts multiple files)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='docs/qualia/imgs',
        help='Directory to save generated figures (default: docs/qualia/imgs)'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating plots, only show summary statistics'
    )
    
    args = parser.parse_args()
    
    # Validate input files
    valid_files = []
    for filepath in args.files:
        if os.path.exists(filepath):
            valid_files.append(filepath)
        else:
            print(f"Warning: File not found: {filepath}", file=sys.stderr)
    
    if not valid_files:
        print("Error: No valid input files found.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(valid_files)} files...")
    
    # Extract metrics from all files
    df = extract_metrics(valid_files)
    
    if df.empty:
        print("Error: No valid data found in any of the input files.", file=sys.stderr)
        sys.exit(1)
    
    # Print summary statistics
    print_summary_stats(df)
    
    # Generate plots if requested and timestamps are available
    if not args.no_plots:
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        plot_metrics_over_time(df, args.output_dir)
    
    print(f"\nAnalysis complete. Processed {len(df)} records from {len(valid_files)} files.")


if __name__ == '__main__':
    main()