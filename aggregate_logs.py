#!/usr/bin/env python3
"""
Aggregate logs from the logs directory into a CSV file.
Processes all JSON files in the logs directory that conform to the soul_debate_schema.json.
"""

import json
import csv
import os
import glob
from pathlib import Path


def load_schema(schema_path):
    """Load the JSON schema for validation."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Schema file {schema_path} not found. Proceeding without validation.")
        return None


def validate_json_against_schema(data, schema):
    """Basic validation of JSON data against schema structure."""
    if not schema:
        return True
    
    # Basic validation - check if required fields exist
    required_fields = [
        "timestamp", "session_id", "branch", "model", "seed", 
        "violations", "tokens", "spikes", "entropy", "mutual_information", "text"
    ]
    
    for field in required_fields:
        if field not in data:
            print(f"Warning: Missing required field '{field}' in log entry")
            return False
    
    return True


def process_logs(logs_dir, output_csv, schema_path):
    """Process all JSON log files and aggregate them into a CSV."""
    # Load schema
    schema = load_schema(schema_path)
    
    # Find all JSON files in logs directory (excluding schema)
    json_files = glob.glob(os.path.join(logs_dir, "*.json"))
    json_files = [f for f in json_files if not f.endswith("schema.json")]
    
    if not json_files:
        print(f"No JSON log files found in {logs_dir}")
        return
    
    aggregated_data = []
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            if validate_json_against_schema(data, schema):
                # Flatten spike data for CSV
                spike_terms = [spike.get('term', '') for spike in data.get('spikes', [])]
                spike_intensities = [spike.get('intensity', 0) for spike in data.get('spikes', [])]
                spike_contexts = [spike.get('context', '') for spike in data.get('spikes', [])]
                
                row = {
                    'timestamp': data.get('timestamp', ''),
                    'session_id': data.get('session_id', ''),
                    'branch': data.get('branch', ''),
                    'model': data.get('model', ''),
                    'seed': data.get('seed', 0),
                    'violations': data.get('violations', 0),
                    'tokens': data.get('tokens', 0),
                    'spike_count': len(data.get('spikes', [])),
                    'spike_terms': '|'.join(spike_terms),
                    'spike_intensities': '|'.join(map(str, spike_intensities)),
                    'spike_contexts': '|'.join(spike_contexts),
                    'entropy': data.get('entropy', 0),
                    'mutual_information': data.get('mutual_information', 0),
                    'text_length': len(data.get('text', '')),
                    'source_file': os.path.basename(json_file)
                }
                aggregated_data.append(row)
                print(f"Processed: {os.path.basename(json_file)}")
            else:
                print(f"Skipping invalid file: {os.path.basename(json_file)}")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing {json_file}: {e}")
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    if aggregated_data:
        # Write to CSV
        fieldnames = [
            'timestamp', 'session_id', 'branch', 'model', 'seed', 'violations',
            'tokens', 'spike_count', 'spike_terms', 'spike_intensities', 
            'spike_contexts', 'entropy', 'mutual_information', 'text_length', 'source_file'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(aggregated_data)
        
        print(f"Successfully aggregated {len(aggregated_data)} log entries to {output_csv}")
    else:
        print("No valid log entries found to aggregate")


if __name__ == "__main__":
    logs_dir = "logs"
    output_csv = "aggregated_logs.csv"
    schema_path = "logs/soul_debate_schema.json"
    
    process_logs(logs_dir, output_csv, schema_path)