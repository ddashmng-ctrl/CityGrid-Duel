#!/usr/bin/env python3
"""
Script to aggregate soul debate logs into a CSV file.
Processes all JSON files in the logs directory and creates/updates logs/aggregated_logs.csv
"""

import json
import csv
import os
import sys
from pathlib import Path
from typing import List, Dict, Any


def load_json_files(logs_dir: str) -> List[Dict[str, Any]]:
    """Load all JSON files from the logs directory, excluding the schema."""
    json_files = []
    logs_path = Path(logs_dir)
    
    for json_file in logs_path.glob("*.json"):
        # Skip the schema file
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                # Add filename for reference
                data['source_file'] = json_file.name
                json_files.append(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            sys.exit(1)
    
    return json_files


def aggregate_spikes(spikes: List[Dict[str, Any]]) -> str:
    """Aggregate spike data into a string representation."""
    if not spikes:
        return "none"
    
    spike_summaries = []
    for spike in spikes:
        spike_summaries.append(f"{spike['term']}:{spike['intensity']:.2f}")
    
    return "; ".join(spike_summaries)


def create_csv(logs_data: List[Dict[str, Any]], output_file: str) -> None:
    """Create CSV file from the aggregated logs data."""
    if not logs_data:
        print("No logs data to aggregate", file=sys.stderr)
        return
    
    fieldnames = [
        'source_file',
        'timestamp',
        'session_id',
        'branch',
        'model',
        'seed',
        'violations',
        'tokens',
        'spikes_summary',
        'entropy',
        'mutual_information',
        'text_length'
    ]
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for log_entry in logs_data:
                row = {
                    'source_file': log_entry.get('source_file', ''),
                    'timestamp': log_entry.get('timestamp', ''),
                    'session_id': log_entry.get('session_id', ''),
                    'branch': log_entry.get('branch', ''),
                    'model': log_entry.get('model', ''),
                    'seed': log_entry.get('seed', ''),
                    'violations': log_entry.get('violations', 0),
                    'tokens': log_entry.get('tokens', 0),
                    'spikes_summary': aggregate_spikes(log_entry.get('spikes', [])),
                    'entropy': log_entry.get('entropy', 0.0),
                    'mutual_information': log_entry.get('mutual_information', 0.0),
                    'text_length': len(log_entry.get('text', ''))
                }
                writer.writerow(row)
                
        print(f"Successfully aggregated {len(logs_data)} log entries to {output_file}")
        
    except IOError as e:
        print(f"Error writing CSV file {output_file}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to aggregate logs."""
    # Get the repository root directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    logs_dir = repo_root / "logs"
    output_file = logs_dir / "aggregated_logs.csv"
    
    if not logs_dir.exists():
        print(f"Logs directory not found: {logs_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Load JSON files
    logs_data = load_json_files(str(logs_dir))
    
    if not logs_data:
        print("No JSON log files found to aggregate", file=sys.stderr)
        sys.exit(1)
    
    # Sort by timestamp for consistent ordering
    logs_data.sort(key=lambda x: x.get('timestamp', ''))
    
    # Create aggregated CSV
    create_csv(logs_data, str(output_file))


if __name__ == "__main__":
    main()