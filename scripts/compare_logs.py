#!/usr/bin/env python3
"""
compare_logs.py - Compare JSON log files and visualize entropy and mutual information

This script compares two JSON log files (soul debate logs) and creates
side-by-side visualizations of entropy and mutual information values.
"""

import json
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_json_file(filepath):
    """
    Load and validate JSON file.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        dict: Parsed JSON data
        
    Raises:
        SystemExit: If file cannot be read or parsed
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unable to read '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def extract_metrics(data):
    """
    Extract entropy, mutual information, and spike data from JSON.
    
    Args:
        data (dict): Parsed JSON data
        
    Returns:
        dict: Extracted metrics
    """
    metrics = {
        'entropy': data.get('entropy', 0.0),
        'mutual_information': data.get('mutual_information', 0.0),
        'spikes': data.get('spikes', []),
        'timestamp': data.get('timestamp', 'Unknown'),
        'session_id': data.get('session_id', 'Unknown')
    }
    
    # Calculate spike count and intensity statistics
    spikes = metrics['spikes']
    metrics['spike_count'] = len(spikes)
    metrics['spike_intensities'] = [spike.get('intensity', 0.0) for spike in spikes]
    
    return metrics


def create_comparison_plot(metrics1, metrics2, file1_name, file2_name):
    """
    Create side-by-side comparison plot of entropy and mutual information.
    
    Args:
        metrics1 (dict): Metrics from first file
        metrics2 (dict): Metrics from second file
        file1_name (str): Name of first file
        file2_name (str): Name of second file
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Log Comparison: Entropy and Mutual Information', fontsize=16, fontweight='bold')
    
    # Entropy comparison (bar chart)
    files = [Path(file1_name).stem, Path(file2_name).stem]
    entropies = [metrics1['entropy'], metrics2['entropy']]
    
    bars1 = ax1.bar(files, entropies, color=['#1f77b4', '#ff7f0e'], alpha=0.8)
    ax1.set_title('Entropy Comparison')
    ax1.set_ylabel('Entropy')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars1, entropies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Mutual Information comparison (bar chart)
    mis = [metrics1['mutual_information'], metrics2['mutual_information']]
    
    bars2 = ax2.bar(files, mis, color=['#2ca02c', '#d62728'], alpha=0.8)
    ax2.set_title('Mutual Information Comparison')
    ax2.set_ylabel('Mutual Information')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars2, mis):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Spike count comparison
    spike_counts = [metrics1['spike_count'], metrics2['spike_count']]
    
    bars3 = ax3.bar(files, spike_counts, color=['#9467bd', '#8c564b'], alpha=0.8)
    ax3.set_title('Spike Count Comparison')
    ax3.set_ylabel('Number of Spikes')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars3, spike_counts):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    # Spike intensity distribution (if spikes exist)
    if metrics1['spike_intensities'] or metrics2['spike_intensities']:
        all_intensities = metrics1['spike_intensities'] + metrics2['spike_intensities']
        if all_intensities:
            bins = np.linspace(0, 1, 11)
            
            if metrics1['spike_intensities']:
                ax4.hist(metrics1['spike_intensities'], bins=bins, alpha=0.6, 
                        label=f'{Path(file1_name).stem}', color='#1f77b4')
            
            if metrics2['spike_intensities']:
                ax4.hist(metrics2['spike_intensities'], bins=bins, alpha=0.6, 
                        label=f'{Path(file2_name).stem}', color='#ff7f0e')
            
            ax4.set_title('Spike Intensity Distribution')
            ax4.set_xlabel('Intensity')
            ax4.set_ylabel('Count')
            ax4.legend()
        else:
            ax4.text(0.5, 0.5, 'No spike data available', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Spike Intensity Distribution')
    else:
        ax4.text(0.5, 0.5, 'No spike data available', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Spike Intensity Distribution')
    
    plt.tight_layout()
    plt.show()


def print_summary(metrics1, metrics2, file1_name, file2_name):
    """
    Print summary of differences between the two files.
    
    Args:
        metrics1 (dict): Metrics from first file
        metrics2 (dict): Metrics from second file
        file1_name (str): Name of first file
        file2_name (str): Name of second file
    """
    print("\n" + "="*60)
    print("LOG COMPARISON SUMMARY")
    print("="*60)
    
    print(f"\nFile 1: {file1_name}")
    print(f"  Session ID: {metrics1['session_id']}")
    print(f"  Timestamp: {metrics1['timestamp']}")
    print(f"  Entropy: {metrics1['entropy']:.3f}")
    print(f"  Mutual Information: {metrics1['mutual_information']:.3f}")
    print(f"  Spike Count: {metrics1['spike_count']}")
    
    print(f"\nFile 2: {file2_name}")
    print(f"  Session ID: {metrics2['session_id']}")
    print(f"  Timestamp: {metrics2['timestamp']}")
    print(f"  Entropy: {metrics2['entropy']:.3f}")
    print(f"  Mutual Information: {metrics2['mutual_information']:.3f}")
    print(f"  Spike Count: {metrics2['spike_count']}")
    
    print("\nDIFFERENCES:")
    print("-" * 30)
    
    # Average entropy
    avg_entropy = (metrics1['entropy'] + metrics2['entropy']) / 2
    entropy_diff = abs(metrics1['entropy'] - metrics2['entropy'])
    print(f"Average Entropy: {avg_entropy:.3f}")
    print(f"Entropy Difference: {entropy_diff:.3f}")
    
    # Spike count
    total_spikes = metrics1['spike_count'] + metrics2['spike_count']
    spike_diff = abs(metrics1['spike_count'] - metrics2['spike_count'])
    print(f"Total Spike Count: {total_spikes}")
    print(f"Spike Count Difference: {spike_diff}")
    
    # MI range
    mi_values = [metrics1['mutual_information'], metrics2['mutual_information']]
    mi_range = max(mi_values) - min(mi_values)
    mi_avg = sum(mi_values) / 2
    print(f"Average Mutual Information: {mi_avg:.3f}")
    print(f"MI Range: {mi_range:.3f}")
    
    # Spike intensity analysis
    all_intensities = metrics1['spike_intensities'] + metrics2['spike_intensities']
    if all_intensities:
        intensity_range = max(all_intensities) - min(all_intensities)
        avg_intensity = sum(all_intensities) / len(all_intensities)
        print(f"Average Spike Intensity: {avg_intensity:.3f}")
        print(f"Spike Intensity Range: {intensity_range:.3f}")
    else:
        print("No spike intensity data available")
    
    print("="*60)


def main():
    """Main function to handle command line arguments and orchestrate comparison."""
    parser = argparse.ArgumentParser(
        description="Compare two JSON log files and visualize entropy and mutual information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s logs/file1.json logs/file2.json
  %(prog)s logs/example_soul_debate.json logs/example_soul_debate_2.json
        """
    )
    
    parser.add_argument('file1', 
                       help='Path to first JSON log file')
    parser.add_argument('file2', 
                       help='Path to second JSON log file')
    parser.add_argument('--no-plot', action='store_true',
                       help='Skip showing the comparison plot')
    
    args = parser.parse_args()
    
    # Validate input files exist
    if not Path(args.file1).exists():
        print(f"Error: File '{args.file1}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.file2).exists():
        print(f"Error: File '{args.file2}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading and comparing files:")
    print(f"  File 1: {args.file1}")
    print(f"  File 2: {args.file2}")
    
    # Load JSON files
    data1 = load_json_file(args.file1)
    data2 = load_json_file(args.file2)
    
    # Extract metrics
    metrics1 = extract_metrics(data1)
    metrics2 = extract_metrics(data2)
    
    # Print summary
    print_summary(metrics1, metrics2, args.file1, args.file2)
    
    # Create visualization
    if not args.no_plot:
        print("\nGenerating comparison plot...")
        create_comparison_plot(metrics1, metrics2, args.file1, args.file2)
    
    print("\nComparison complete!")


if __name__ == "__main__":
    main()