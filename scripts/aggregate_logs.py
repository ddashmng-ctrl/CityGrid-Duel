#!/usr/bin/env python3
"""
Script to aggregate log files for the PR leaderboard workflow.
This script processes JSON log files and creates aggregated data.
"""

import json
import csv
import os
import sys
from pathlib import Path

def load_json_logs():
    """Load and process all JSON log files."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("Warning: logs directory does not exist")
        return []
    
    json_files = logs_dir.glob("*.json")
    
    rows = []
    for json_file in json_files:
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extract key metrics for CSV
            row = {
                'filename': json_file.name,
                'timestamp': data.get('timestamp', ''),
                'session_id': data.get('session_id', ''),
                'model': data.get('model', ''),
                'seed': data.get('seed', ''),
                'violations': data.get('violations', 0),
                'tokens': data.get('tokens', 0),
                'entropy': data.get('entropy', 0.0),
                'mutual_information': data.get('mutual_information', 0.0),
                'spike_count': len(data.get('spikes', [])),
                'max_spike_intensity': max([s.get('intensity', 0) for s in data.get('spikes', [])], default=0)
            }
            rows.append(row)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not process {json_file}: {e}")
    
    return rows

def load_output_summaries():
    """Load summary data from output directory."""
    output_dir = Path("output")
    if not output_dir.exists():
        print("Warning: output directory does not exist")
        return []
    
    summary_files = list(output_dir.glob("*summary.json"))
    
    rows = []
    for summary_file in summary_files:
        try:
            with open(summary_file, 'r') as f:
                data = json.load(f)
            
            # Extract simulation metrics
            row = {
                'filename': summary_file.name,
                'timestamp': '',  # Not available in summary files
                'session_id': 'simulation',
                'model': summary_file.stem.replace('_summary', ''),
                'seed': data.get('seed', 42),
                'violations': data.get('comfort_violations', 0),
                'tokens': 0,  # Not applicable
                'entropy': 0.0,  # Not applicable
                'mutual_information': 0.0,  # Not applicable
                'spike_count': 0,  # Not applicable
                'max_spike_intensity': 0.0,  # Not applicable
                'simulation_hours': data.get('simulation_duration_hours', 0),
                'avg_grid_draw_kw': data.get('average_grid_draw_kw', 0.0)
            }
            rows.append(row)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not process {summary_file}: {e}")
    
    return rows

def generate_csv():
    """Generate the aggregated CSV file."""
    
    # Load data from both sources
    log_rows = load_json_logs()
    summary_rows = load_output_summaries()
    
    # Combine and standardize
    all_rows = []
    
    # Add log data
    for row in log_rows:
        all_rows.append({
            'source': 'soul_debate_logs',
            'filename': row['filename'],
            'timestamp': row['timestamp'],
            'session_id': row['session_id'],
            'model': row['model'],
            'seed': row['seed'],
            'violations': row['violations'],
            'tokens': row['tokens'],
            'entropy': row['entropy'],
            'mutual_information': row['mutual_information'],
            'spike_count': row['spike_count'],
            'max_spike_intensity': row['max_spike_intensity'],
            'simulation_hours': '',
            'avg_grid_draw_kw': ''
        })
    
    # Add summary data
    for row in summary_rows:
        all_rows.append({
            'source': 'simulation_results',
            'filename': row['filename'],
            'timestamp': row['timestamp'],
            'session_id': row['session_id'],
            'model': row['model'],
            'seed': row['seed'],
            'violations': row['violations'],
            'tokens': row['tokens'],
            'entropy': row['entropy'],
            'mutual_information': row['mutual_information'],
            'spike_count': row['spike_count'],
            'max_spike_intensity': row['max_spike_intensity'],
            'simulation_hours': row['simulation_hours'],
            'avg_grid_draw_kw': row['avg_grid_draw_kw']
        })
    
    # Write CSV file
    output_file = "logs/aggregated_logs.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if all_rows:
        with open(output_file, 'w', newline='') as f:
            fieldnames = all_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        
        print(f"Generated aggregated CSV with {len(all_rows)} rows: {output_file}")
    else:
        print("No data found to aggregate")
    
    return len(all_rows)

if __name__ == "__main__":
    try:
        count = generate_csv()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)