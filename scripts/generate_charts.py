#!/usr/bin/env python3
"""
Generate matplotlib charts from aggregated log data.
Creates visualizations for entropy over time, spike counts, and other metrics.
"""

import json
import argparse
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for GitHub Actions
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict, Any
import numpy as np


def load_aggregated_data(file_path: str) -> Dict[str, Any]:
    """Load aggregated log data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading aggregated data from {file_path}: {e}")
        return {}


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime object."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return datetime.now()


def generate_entropy_chart(time_series_data: Dict[str, Any], output_dir: str) -> str:
    """Generate entropy over time chart."""
    entropy_data = time_series_data.get('entropy_over_time', [])
    
    if not entropy_data:
        print("No entropy data found")
        return ""
    
    # Group by model
    models = {}
    for entry in entropy_data:
        model = entry.get('model', 'unknown')
        if model not in models:
            models[model] = {'timestamps': [], 'entropy': []}
        
        timestamp = parse_timestamp(entry.get('timestamp', ''))
        models[model]['timestamps'].append(timestamp)
        models[model]['entropy'].append(entry.get('entropy', 0.0))
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i, (model, data) in enumerate(models.items()):
        color = colors[i % len(colors)]
        plt.plot(data['timestamps'], data['entropy'], 
                marker='o', label=model, color=color, linewidth=2, markersize=4)
    
    plt.title('Entropy Over Time by Model', fontsize=16, fontweight='bold')
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Entropy', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Format x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'entropy_over_time.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated entropy chart: {output_path}")
    return output_path


def generate_spike_count_chart(time_series_data: Dict[str, Any], output_dir: str) -> str:
    """Generate spike count over time chart."""
    spike_data = time_series_data.get('spikes_over_time', [])
    
    if not spike_data:
        print("No spike data found")
        return ""
    
    # Group by model
    models = {}
    for entry in spike_data:
        model = entry.get('model', 'unknown')
        if model not in models:
            models[model] = {'timestamps': [], 'spike_counts': [], 'intensities': []}
        
        timestamp = parse_timestamp(entry.get('timestamp', ''))
        models[model]['timestamps'].append(timestamp)
        models[model]['spike_counts'].append(entry.get('spike_count', 0))
        models[model]['intensities'].append(entry.get('avg_spike_intensity', 0.0))
    
    # Create subplot for spike counts and intensities
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Spike counts
    for i, (model, data) in enumerate(models.items()):
        color = colors[i % len(colors)]
        ax1.plot(data['timestamps'], data['spike_counts'], 
                marker='s', label=model, color=color, linewidth=2, markersize=4)
    
    ax1.set_title('Spike Count Over Time by Model', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Spikes', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Average spike intensities
    for i, (model, data) in enumerate(models.items()):
        color = colors[i % len(colors)]
        ax2.plot(data['timestamps'], data['intensities'], 
                marker='^', label=model, color=color, linewidth=2, markersize=4)
    
    ax2.set_title('Average Spike Intensity Over Time by Model', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Timestamp', fontsize=12)
    ax2.set_ylabel('Average Intensity', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis for both subplots
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'spike_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated spike analysis chart: {output_path}")
    return output_path


def generate_model_comparison_chart(model_stats: Dict[str, Any], output_dir: str) -> str:
    """Generate model comparison bar chart."""
    if not model_stats:
        print("No model statistics found")
        return ""
    
    models = list(model_stats.keys())
    entropy_avg = [model_stats[m]['avg_entropy'] for m in models]
    spike_avg = [model_stats[m]['avg_spike_count'] for m in models]
    mutual_info_avg = [model_stats[m]['avg_mutual_info'] for m in models]
    
    # Create grouped bar chart
    x = np.arange(len(models))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars1 = ax.bar(x - width, entropy_avg, width, label='Avg Entropy', color='#1f77b4', alpha=0.8)
    bars2 = ax.bar(x, spike_avg, width, label='Avg Spike Count', color='#ff7f0e', alpha=0.8)
    bars3 = ax.bar(x + width, mutual_info_avg, width, label='Avg Mutual Info', color='#2ca02c', alpha=0.8)
    
    ax.set_title('Model Performance Comparison', fontsize=16, fontweight='bold')
    ax.set_xlabel('Models', fontsize=12)
    ax.set_ylabel('Average Values', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
    
    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'model_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated model comparison chart: {output_path}")
    return output_path


def generate_summary_report(charts: List[str], output_dir: str) -> str:
    """Generate a markdown summary report with chart references."""
    report_content = """# Log Analysis Charts

This report contains visualizations generated from the soul debate logs.

## Charts Generated

"""
    
    for chart_path in charts:
        if chart_path:
            chart_name = os.path.basename(chart_path)
            report_content += f"- ![{chart_name}]({chart_name})\n"
    
    report_content += f"""
## Analysis Summary

- **Entropy Over Time**: Shows how system entropy evolves during debates
- **Spike Analysis**: Tracks both spike frequency and intensity patterns
- **Model Comparison**: Compares average performance metrics across models

Generated on: {datetime.now().isoformat()}
"""
    
    report_path = os.path.join(output_dir, 'chart_summary.md')
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"Generated summary report: {report_path}")
    return report_path


def main():
    parser = argparse.ArgumentParser(description='Generate matplotlib charts from aggregated log data')
    parser.add_argument('--input', default='output/aggregated_logs.json',
                       help='Input aggregated log data file')
    parser.add_argument('--output-dir', default='output/charts',
                       help='Output directory for charts')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load aggregated data
    print(f"Loading aggregated data from: {args.input}")
    data = load_aggregated_data(args.input)
    
    if not data:
        print("No data loaded. Exiting.")
        return
    
    charts_generated = []
    
    # Generate charts
    time_series = data.get('time_series', {})
    model_stats = data.get('model_statistics', {})
    
    # Entropy over time chart
    entropy_chart = generate_entropy_chart(time_series, args.output_dir)
    if entropy_chart:
        charts_generated.append(entropy_chart)
    
    # Spike analysis chart
    spike_chart = generate_spike_count_chart(time_series, args.output_dir)
    if spike_chart:
        charts_generated.append(spike_chart)
    
    # Model comparison chart
    comparison_chart = generate_model_comparison_chart(model_stats, args.output_dir)
    if comparison_chart:
        charts_generated.append(comparison_chart)
    
    # Generate summary report
    summary_report = generate_summary_report(charts_generated, args.output_dir)
    
    print(f"\nChart generation complete!")
    print(f"Generated {len(charts_generated)} charts in: {args.output_dir}")
    print(f"Summary report: {summary_report}")


if __name__ == '__main__':
    main()