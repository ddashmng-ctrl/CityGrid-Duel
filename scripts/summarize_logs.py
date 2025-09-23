#!/usr/bin/env python3
"""
Log summarization script for the logs pipeline workflow.
Generates summary statistics and insights from aggregated log data.
"""

import sys
import os
import json
import csv
from pathlib import Path
import statistics


def load_aggregated_csv():
    """Load the aggregated logs CSV file."""
    csv_file = Path("logs/aggregated_logs.csv")
    if not csv_file.exists():
        print(f"ERROR: Aggregated logs file '{csv_file}' not found")
        print("Make sure to run aggregate_logs.py first")
        sys.exit(1)
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        if not data:
            print(f"ERROR: No data found in {csv_file}")
            sys.exit(1)
            
        print(f"Successfully loaded {len(data)} rows from {csv_file}")
        return data
        
    except Exception as e:
        print(f"ERROR: Failed to load {csv_file}: {e}")
        sys.exit(1)


def analyze_soul_debate_logs(data):
    """Analyze soul debate log data."""
    soul_debate_data = [row for row in data if row['source'] == 'soul_debate_logs']
    
    if not soul_debate_data:
        print("WARNING: No soul debate log data found")
        return {}
    
    try:
        # Extract numeric values for analysis
        entropies = [float(row['entropy']) for row in soul_debate_data if row['entropy']]
        mutual_infos = [float(row['mutual_information']) for row in soul_debate_data if row['mutual_information']]
        spike_counts = [int(row['spike_count']) for row in soul_debate_data if row['spike_count']]
        max_intensities = [float(row['max_spike_intensity']) for row in soul_debate_data if row['max_spike_intensity']]
        
        analysis = {
            'total_sessions': len(soul_debate_data),
            'entropy_stats': {
                'mean': statistics.mean(entropies) if entropies else 0,
                'median': statistics.median(entropies) if entropies else 0,
                'max': max(entropies) if entropies else 0,
                'min': min(entropies) if entropies else 0
            },
            'mutual_information_stats': {
                'mean': statistics.mean(mutual_infos) if mutual_infos else 0,
                'median': statistics.median(mutual_infos) if mutual_infos else 0,
                'max': max(mutual_infos) if mutual_infos else 0,
                'min': min(mutual_infos) if mutual_infos else 0
            },
            'spike_analysis': {
                'total_spikes': sum(spike_counts),
                'avg_spikes_per_session': statistics.mean(spike_counts) if spike_counts else 0,
                'max_spikes_session': max(spike_counts) if spike_counts else 0,
                'max_spike_intensity': max(max_intensities) if max_intensities else 0
            }
        }
        
        print(f"Analyzed {len(soul_debate_data)} soul debate sessions")
        return analysis
        
    except Exception as e:
        print(f"ERROR: Failed to analyze soul debate logs: {e}")
        sys.exit(1)


def analyze_simulation_results(data):
    """Analyze simulation result data."""
    simulation_data = [row for row in data if row['source'] == 'simulation_results']
    
    if not simulation_data:
        print("WARNING: No simulation result data found")
        return {}
    
    try:
        # Extract numeric values for analysis
        avg_draws = [float(row['avg_grid_draw_kw']) for row in simulation_data if row['avg_grid_draw_kw']]
        violations = [int(row['violations']) for row in simulation_data if row['violations']]
        sim_hours = [float(row['simulation_hours']) for row in simulation_data if row['simulation_hours']]
        
        analysis = {
            'total_simulations': len(simulation_data),
            'grid_draw_stats': {
                'mean': statistics.mean(avg_draws) if avg_draws else 0,
                'median': statistics.median(avg_draws) if avg_draws else 0,
                'best': min(avg_draws) if avg_draws else 0,
                'worst': max(avg_draws) if avg_draws else 0
            },
            'violation_stats': {
                'total_violations': sum(violations),
                'simulations_with_violations': len([v for v in violations if v > 0]),
                'max_violations': max(violations) if violations else 0
            },
            'duration_stats': {
                'total_hours': sum(sim_hours),
                'avg_hours': statistics.mean(sim_hours) if sim_hours else 0
            }
        }
        
        print(f"Analyzed {len(simulation_data)} simulation results")
        return analysis
        
    except Exception as e:
        print(f"ERROR: Failed to analyze simulation results: {e}")
        sys.exit(1)


def generate_summary_report(soul_analysis, sim_analysis):
    """Generate a comprehensive summary report."""
    try:
        report = {
            'timestamp': str(Path('logs/aggregated_logs.csv').stat().st_mtime),
            'summary': {
                'total_data_points': soul_analysis.get('total_sessions', 0) + sim_analysis.get('total_simulations', 0),
                'soul_debate_sessions': soul_analysis.get('total_sessions', 0),
                'simulation_runs': sim_analysis.get('total_simulations', 0)
            },
            'soul_debate_analysis': soul_analysis,
            'simulation_analysis': sim_analysis
        }
        
        # Save summary to JSON
        summary_file = Path("logs/summary_report.json")
        with open(summary_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"SUCCESS: Generated summary report: {summary_file}")
        
        # Print key insights
        print("\n=== SUMMARY INSIGHTS ===")
        print(f"Total data points processed: {report['summary']['total_data_points']}")
        
        if soul_analysis:
            print(f"Soul debate sessions: {soul_analysis['total_sessions']}")
            if soul_analysis.get('spike_analysis', {}).get('total_spikes', 0) > 0:
                print(f"Total proto-qualia spikes detected: {soul_analysis['spike_analysis']['total_spikes']}")
        
        if sim_analysis:
            print(f"Simulation runs: {sim_analysis['total_simulations']}")
            if sim_analysis.get('grid_draw_stats', {}).get('best', 0) > 0:
                print(f"Best grid draw efficiency: {sim_analysis['grid_draw_stats']['best']:.3f} kW")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to generate summary report: {e}")
        sys.exit(1)


def summarize_logs():
    """Main function to summarize logs."""
    try:
        print("Starting log summarization...")
        
        # Load aggregated data
        data = load_aggregated_csv()
        
        # Analyze different data sources
        soul_analysis = analyze_soul_debate_logs(data)
        sim_analysis = analyze_simulation_results(data)
        
        # Generate summary report
        return generate_summary_report(soul_analysis, sim_analysis)
        
    except Exception as e:
        print(f"ERROR: Log summarization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(summarize_logs())