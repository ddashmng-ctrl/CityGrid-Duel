#!/usr/bin/env python3
"""
compare_logs.py - Compare two JSON log files containing entropy and mutual information data.

This script compares two JSON files from the soul debate logs, extracting entropy and 
mutual information (MI) values to create visualizations and summary statistics.

Usage:
    python compare_logs.py <file1.json> <file2.json>

The script will:
1. Load and validate both JSON files
2. Extract entropy, MI values, and spike data
3. Generate side-by-side comparison plots
4. Print summary differences including averages and ranges
"""

import json
import sys
import argparse
import os
import matplotlib
# Use Agg backend for non-interactive environments
if os.environ.get('DISPLAY') is None:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load and validate a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        ValueError: If required fields are missing
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {filepath}: {e.msg}", e.doc, e.pos)
    
    # Validate required fields
    required_fields = ['entropy', 'mutual_information', 'spikes']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields in {filepath}: {missing_fields}")
    
    return data


def extract_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant metrics from JSON data.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        Dictionary containing extracted metrics
    """
    spikes = data.get('spikes', [])
    
    return {
        'entropy': data['entropy'],
        'mutual_information': data['mutual_information'],
        'spike_count': len(spikes),
        'spike_intensities': [spike.get('intensity', 0) for spike in spikes],
        'session_id': data.get('session_id', 'unknown'),
        'model': data.get('model', 'unknown'),
        'timestamp': data.get('timestamp', 'unknown'),
        'tokens': data.get('tokens', 0)
    }


def create_comparison_plot(metrics1: Dict[str, Any], metrics2: Dict[str, Any], 
                          file1_name: str, file2_name: str, save_path: str = None) -> None:
    """
    Create side-by-side comparison plots for the metrics.
    
    Args:
        metrics1: Metrics from first file
        metrics2: Metrics from second file
        file1_name: Name of first file (for labels)
        file2_name: Name of second file (for labels)
        save_path: Path to save the plot (if None, displays interactively)
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Soul Debate Log Comparison', fontsize=16, fontweight='bold')
    
    # Entropy comparison (bar chart)
    ax1.bar(['File 1', 'File 2'], 
            [metrics1['entropy'], metrics2['entropy']], 
            color=['skyblue', 'lightcoral'])
    ax1.set_title('Entropy Comparison')
    ax1.set_ylabel('Entropy Value')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate([metrics1['entropy'], metrics2['entropy']]):
        ax1.text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')
    
    # Mutual Information comparison (bar chart)
    ax2.bar(['File 1', 'File 2'], 
            [metrics1['mutual_information'], metrics2['mutual_information']], 
            color=['lightgreen', 'orange'])
    ax2.set_title('Mutual Information Comparison')
    ax2.set_ylabel('MI Value')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate([metrics1['mutual_information'], metrics2['mutual_information']]):
        ax2.text(i, v + 0.005, f'{v:.3f}', ha='center', va='bottom')
    
    # Spike count comparison (bar chart)
    ax3.bar(['File 1', 'File 2'], 
            [metrics1['spike_count'], metrics2['spike_count']], 
            color=['gold', 'mediumpurple'])
    ax3.set_title('Spike Count Comparison')
    ax3.set_ylabel('Number of Spikes')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate([metrics1['spike_count'], metrics2['spike_count']]):
        ax3.text(i, v + 0.05, str(v), ha='center', va='bottom')
    
    # Spike intensities comparison (if spikes exist)
    if metrics1['spike_intensities'] or metrics2['spike_intensities']:
        all_intensities1 = metrics1['spike_intensities']
        all_intensities2 = metrics2['spike_intensities']
        
        # Create scatter plot for spike intensities
        if all_intensities1:
            ax4.scatter(range(len(all_intensities1)), all_intensities1, 
                       label=f'File 1 ({len(all_intensities1)} spikes)', 
                       alpha=0.7, s=50)
        if all_intensities2:
            ax4.scatter(range(len(all_intensities2)), all_intensities2, 
                       label=f'File 2 ({len(all_intensities2)} spikes)', 
                       alpha=0.7, s=50)
        
        ax4.set_title('Spike Intensities')
        ax4.set_xlabel('Spike Index')
        ax4.set_ylabel('Intensity')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No spike data available', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Spike Intensities')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()


def print_summary(metrics1: Dict[str, Any], metrics2: Dict[str, Any], 
                 file1_name: str, file2_name: str) -> None:
    """
    Print summary comparison of the two files.
    
    Args:
        metrics1: Metrics from first file
        metrics2: Metrics from second file
        file1_name: Name of first file
        file2_name: Name of second file
    """
    print("\n" + "="*60)
    print("SOUL DEBATE LOG COMPARISON SUMMARY")
    print("="*60)
    
    print(f"\nFile 1: {file1_name}")
    print(f"  Session ID: {metrics1['session_id']}")
    print(f"  Model: {metrics1['model']}")
    print(f"  Timestamp: {metrics1['timestamp']}")
    print(f"  Tokens: {metrics1['tokens']}")
    
    print(f"\nFile 2: {file2_name}")
    print(f"  Session ID: {metrics2['session_id']}")
    print(f"  Model: {metrics2['model']}")
    print(f"  Timestamp: {metrics2['timestamp']}")
    print(f"  Tokens: {metrics2['tokens']}")
    
    print("\n" + "-"*40)
    print("ENTROPY ANALYSIS")
    print("-"*40)
    print(f"File 1 Entropy: {metrics1['entropy']:.4f}")
    print(f"File 2 Entropy: {metrics2['entropy']:.4f}")
    entropy_diff = metrics2['entropy'] - metrics1['entropy']
    print(f"Difference: {entropy_diff:+.4f} ({'higher' if entropy_diff > 0 else 'lower'} in File 2)")
    
    print("\n" + "-"*40)
    print("MUTUAL INFORMATION ANALYSIS")
    print("-"*40)
    print(f"File 1 MI: {metrics1['mutual_information']:.4f}")
    print(f"File 2 MI: {metrics2['mutual_information']:.4f}")
    mi_diff = metrics2['mutual_information'] - metrics1['mutual_information']
    print(f"Difference: {mi_diff:+.4f} ({'higher' if mi_diff > 0 else 'lower'} in File 2)")
    
    print("\n" + "-"*40)
    print("SPIKE ANALYSIS")
    print("-"*40)
    print(f"File 1 Spike Count: {metrics1['spike_count']}")
    print(f"File 2 Spike Count: {metrics2['spike_count']}")
    spike_diff = metrics2['spike_count'] - metrics1['spike_count']
    print(f"Difference: {spike_diff:+d} ({'more' if spike_diff > 0 else 'fewer'} in File 2)")
    
    # Spike intensity analysis
    if metrics1['spike_intensities']:
        avg_intensity1 = np.mean(metrics1['spike_intensities'])
        max_intensity1 = max(metrics1['spike_intensities'])
        print(f"File 1 - Avg Intensity: {avg_intensity1:.3f}, Max: {max_intensity1:.3f}")
    else:
        print("File 1 - No spikes")
    
    if metrics2['spike_intensities']:
        avg_intensity2 = np.mean(metrics2['spike_intensities'])
        max_intensity2 = max(metrics2['spike_intensities'])
        print(f"File 2 - Avg Intensity: {avg_intensity2:.3f}, Max: {max_intensity2:.3f}")
    else:
        print("File 2 - No spikes")
    
    print("\n" + "="*60)


def main():
    """Main function to orchestrate the comparison."""
    parser = argparse.ArgumentParser(
        description="Compare two JSON files containing entropy and mutual information data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_2.json
  python compare_logs.py file1.json file2.json
        """
    )
    parser.add_argument('file1', help='Path to first JSON file')
    parser.add_argument('file2', help='Path to second JSON file')
    parser.add_argument('--no-plot', action='store_true', 
                       help='Skip plotting (useful for headless environments)')
    parser.add_argument('--save-plot', type=str, metavar='PATH',
                       help='Save plot to specified file path instead of displaying')
    
    args = parser.parse_args()
    
    try:
        # Load and validate both files
        print(f"Loading {args.file1}...")
        data1 = load_json_file(args.file1)
        print(f"Loading {args.file2}...")
        data2 = load_json_file(args.file2)
        
        # Extract metrics
        metrics1 = extract_metrics(data1)
        metrics2 = extract_metrics(data2)
        
        # Create file names for display
        file1_name = Path(args.file1).name
        file2_name = Path(args.file2).name
        
        # Print summary
        print_summary(metrics1, metrics2, file1_name, file2_name)
        
        # Create plots (unless disabled)
        if not args.no_plot:
            print("\nGenerating comparison plots...")
            save_path = args.save_plot if args.save_plot else None
            if save_path is None and os.environ.get('DISPLAY') is None:
                # Auto-save in headless environments
                save_path = f"comparison_{Path(args.file1).stem}_vs_{Path(args.file2).stem}.png"
            
            create_comparison_plot(metrics1, metrics2, file1_name, file2_name, save_path)
        
        print("\nComparison completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()