#!/usr/bin/env python3
"""
Compare JSON logs script for CityGrid Duel soul debate analysis.

This script accepts two JSON log paths as input, loads entropy and mutual 
information (MI) values from each, plots a side-by-side comparison graph 
using matplotlib, and prints summary differences.
"""

import json
import argparse
import sys
from typing import Dict, List, Tuple, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib
    # Use non-interactive backend for environments without display
    matplotlib.use('Agg')
except ImportError:
    print("Error: matplotlib is required but not installed.")
    print("Please install it with: pip install matplotlib")
    sys.exit(1)


def load_log_data(log_path: str) -> Dict[str, Any]:
    """Load and parse JSON log file."""
    try:
        with open(log_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Log file not found: {log_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {log_path}: {e}")
        sys.exit(1)


def extract_metrics(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entropy, MI, and spike metrics from log data."""
    entropy = log_data.get('entropy', 0.0)
    mutual_info = log_data.get('mutual_information', 0.0)
    spikes = log_data.get('spikes', [])
    
    # Calculate spike statistics
    spike_count = len(spikes)
    spike_intensities = [spike.get('intensity', 0.0) for spike in spikes]
    avg_spike_intensity = sum(spike_intensities) / len(spike_intensities) if spike_intensities else 0.0
    
    return {
        'entropy': entropy,
        'mutual_information': mutual_info,
        'spike_count': spike_count,
        'spike_intensities': spike_intensities,
        'avg_spike_intensity': avg_spike_intensity,
        'session_id': log_data.get('session_id', 'unknown'),
        'timestamp': log_data.get('timestamp', 'unknown'),
        'model': log_data.get('model', 'unknown')
    }


def create_comparison_plot(metrics1: Dict[str, Any], metrics2: Dict[str, Any], 
                          log1_name: str, log2_name: str, output_file: str = 'log_comparison.png') -> None:
    """Create side-by-side comparison plots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Soul Debate Log Comparison', fontsize=16, fontweight='bold')
    
    # Entropy comparison
    ax1.bar([log1_name, log2_name], 
            [metrics1['entropy'], metrics2['entropy']], 
            color=['blue', 'red'], alpha=0.7)
    ax1.set_title('Entropy Comparison')
    ax1.set_ylabel('Entropy Value')
    ax1.grid(True, alpha=0.3)
    
    # Mutual Information comparison
    ax2.bar([log1_name, log2_name], 
            [metrics1['mutual_information'], metrics2['mutual_information']], 
            color=['blue', 'red'], alpha=0.7)
    ax2.set_title('Mutual Information Comparison')
    ax2.set_ylabel('MI Value')
    ax2.grid(True, alpha=0.3)
    
    # Spike count comparison
    ax3.bar([log1_name, log2_name], 
            [metrics1['spike_count'], metrics2['spike_count']], 
            color=['blue', 'red'], alpha=0.7)
    ax3.set_title('Spike Count Comparison')
    ax3.set_ylabel('Number of Spikes')
    ax3.grid(True, alpha=0.3)
    
    # Average spike intensity comparison
    ax4.bar([log1_name, log2_name], 
            [metrics1['avg_spike_intensity'], metrics2['avg_spike_intensity']], 
            color=['blue', 'red'], alpha=0.7)
    ax4.set_title('Average Spike Intensity')
    ax4.set_ylabel('Intensity Value')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Comparison plot saved as: {output_file}")
    
    # Show plot if possible (will be ignored in headless environments)
    try:
        plt.show()
    except:
        pass


def print_summary(metrics1: Dict[str, Any], metrics2: Dict[str, Any], 
                 log1_name: str, log2_name: str) -> None:
    """Print detailed summary of differences between logs."""
    print("\n" + "="*60)
    print("SOUL DEBATE LOG COMPARISON SUMMARY")
    print("="*60)
    
    print(f"\nLog 1: {log1_name}")
    print(f"  Session ID: {metrics1['session_id']}")
    print(f"  Timestamp: {metrics1['timestamp']}")
    print(f"  Model: {metrics1['model']}")
    
    print(f"\nLog 2: {log2_name}")
    print(f"  Session ID: {metrics2['session_id']}")
    print(f"  Timestamp: {metrics2['timestamp']}")
    print(f"  Model: {metrics2['model']}")
    
    print(f"\n{'-'*40}")
    print("ENTROPY ANALYSIS")
    print(f"{'-'*40}")
    print(f"{log1_name:20}: {metrics1['entropy']:.4f}")
    print(f"{log2_name:20}: {metrics2['entropy']:.4f}")
    entropy_diff = metrics2['entropy'] - metrics1['entropy']
    print(f"{'Difference:':20} {entropy_diff:+.4f} ({entropy_diff/metrics1['entropy']*100:+.1f}%)")
    
    print(f"\n{'-'*40}")
    print("MUTUAL INFORMATION ANALYSIS")
    print(f"{'-'*40}")
    print(f"{log1_name:20}: {metrics1['mutual_information']:.4f}")
    print(f"{log2_name:20}: {metrics2['mutual_information']:.4f}")
    mi_diff = metrics2['mutual_information'] - metrics1['mutual_information']
    print(f"{'Difference:':20} {mi_diff:+.4f} ({mi_diff/metrics1['mutual_information']*100:+.1f}%)")
    
    print(f"\n{'-'*40}")
    print("SPIKE ANALYSIS")
    print(f"{'-'*40}")
    print(f"{log1_name} spike count: {metrics1['spike_count']}")
    print(f"{log2_name} spike count: {metrics2['spike_count']}")
    spike_diff = metrics2['spike_count'] - metrics1['spike_count']
    print(f"Spike count difference: {spike_diff:+d}")
    
    print(f"\n{log1_name} avg spike intensity: {metrics1['avg_spike_intensity']:.4f}")
    print(f"{log2_name} avg spike intensity: {metrics2['avg_spike_intensity']:.4f}")
    if metrics1['avg_spike_intensity'] > 0:
        intensity_diff = metrics2['avg_spike_intensity'] - metrics1['avg_spike_intensity']
        print(f"Intensity difference: {intensity_diff:+.4f}")
    
    print(f"\n{'-'*40}")
    print("INTERPRETATION")
    print(f"{'-'*40}")
    
    if entropy_diff > 0:
        print(f"• {log2_name} shows HIGHER entropy (more uncertainty/variability)")
    else:
        print(f"• {log1_name} shows HIGHER entropy (more uncertainty/variability)")
    
    if mi_diff > 0:
        print(f"• {log2_name} shows HIGHER mutual information (stronger correlations)")
    else:
        print(f"• {log1_name} shows HIGHER mutual information (stronger correlations)")
    
    if spike_diff > 0:
        print(f"• {log2_name} has MORE proto-qualia spikes (+{spike_diff})")
    elif spike_diff < 0:
        print(f"• {log1_name} has MORE proto-qualia spikes (+{abs(spike_diff)})")
    else:
        print("• Both logs have the SAME number of spikes")


def main():
    """Main function to orchestrate log comparison."""
    parser = argparse.ArgumentParser(
        description="Compare two JSON soul debate logs for entropy and MI analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_2.json
  python compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_control.json
        """
    )
    
    parser.add_argument('log1', help='Path to first JSON log file')
    parser.add_argument('log2', help='Path to second JSON log file')
    parser.add_argument('--output', '-o', default='log_comparison.png',
                       help='Output filename for comparison plot (default: log_comparison.png)')
    
    args = parser.parse_args()
    
    # Load log data
    print(f"Loading log 1: {args.log1}")
    log1_data = load_log_data(args.log1)
    
    print(f"Loading log 2: {args.log2}")
    log2_data = load_log_data(args.log2)
    
    # Extract metrics
    metrics1 = extract_metrics(log1_data)
    metrics2 = extract_metrics(log2_data)
    
    # Create short names for display
    log1_name = args.log1.split('/')[-1].replace('.json', '')
    log2_name = args.log2.split('/')[-1].replace('.json', '')
    
    # Generate comparison plot
    print("Generating comparison plot...")
    create_comparison_plot(metrics1, metrics2, log1_name, log2_name, args.output)
    
    # Print summary
    print_summary(metrics1, metrics2, log1_name, log2_name)


if __name__ == "__main__":
    main()