#!/usr/bin/env python3
"""
Log aggregation script for the logs pipeline workflow.
Aggregates log files from multiple sources into a unified CSV format.
"""

import sys
import os
import json
import csv
from pathlib import Path


def load_json_logs():
    """Load and process all JSON log files."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print(f"ERROR: Logs directory '{logs_dir}' does not exist")
        return []
    
    json_files = list(logs_dir.glob("*.json"))
    if not json_files:
        print(f"WARNING: No JSON log files found in '{logs_dir}'")
        return []
    
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
            print(f"Successfully processed {json_file.name}")
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {json_file}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to process {json_file}: {e}")
            sys.exit(1)
    
    return rows


def load_output_summaries():
    """Load summary data from output directory."""
    output_dir = Path("output")
    if not output_dir.exists():
        print(f"WARNING: Output directory '{output_dir}' does not exist")
        return []
    
    summary_files = list(output_dir.glob("*summary.json"))
    if not summary_files:
        print(f"WARNING: No summary files found in '{output_dir}'")
        return []
    
    rows = []
    for summary_file in summary_files:
        try:
            with open(summary_file, 'r') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ['seed', 'simulation_duration_hours', 'average_grid_draw_kw']
            for field in required_fields:
                if field not in data:
                    print(f"ERROR: Missing required field '{field}' in {summary_file}")
                    sys.exit(1)
            
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
            print(f"Successfully processed {summary_file.name}")
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {summary_file}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to process {summary_file}: {e}")
            sys.exit(1)
    
    return rows


def aggregate_logs():
    """Main function to aggregate logs and generate CSV."""
    try:
        print("Starting log aggregation...")
        
        # Load data from both sources
        log_rows = load_json_logs()
        summary_rows = load_output_summaries()
        
        if not log_rows and not summary_rows:
            print("ERROR: No log data found to aggregate")
            sys.exit(1)
        
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
                'simulation_hours': row.get('simulation_hours', ''),
                'avg_grid_draw_kw': row.get('avg_grid_draw_kw', '')
            })
        
        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Write to CSV
        output_file = logs_dir / "aggregated_logs.csv"
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'source', 'filename', 'timestamp', 'session_id', 'model', 'seed',
                'violations', 'tokens', 'entropy', 'mutual_information',
                'spike_count', 'max_spike_intensity', 'simulation_hours', 'avg_grid_draw_kw'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        
        print(f"SUCCESS: Generated {output_file} with {len(all_rows)} rows")
        return 0
        
    except Exception as e:
        print(f"ERROR: Log aggregation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(aggregate_logs())