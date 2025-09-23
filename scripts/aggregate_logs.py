#!/usr/bin/env python3
"""
Soul Debate Log Aggregation Script

This script aggregates soul debate log files, validates them against the schema,
and outputs a CSV with summary statistics including averages for numeric columns.
"""

import json
import csv
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_schema(schema_path: str) -> Dict[str, Any]:
    """Load the schema file to understand expected structure."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load schema from {schema_path}: {e}")
        return {}


def validate_log_entry(log_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate a log entry against the expected schema structure.
    Returns True if valid, False otherwise.
    """
    if not schema:
        # If no schema available, do basic validation
        required_fields = ['timestamp', 'session_id', 'branch', 'model', 'seed', 
                          'violations', 'tokens', 'entropy', 'mutual_information']
        return all(field in log_data for field in required_fields)
    
    # Validate against schema structure
    schema_keys = set(schema.keys())
    log_keys = set(log_data.keys())
    
    # Check if all schema keys are present
    if not schema_keys.issubset(log_keys):
        return False
    
    # Validate data types based on schema example
    try:
        # Check numeric fields
        numeric_fields = ['seed', 'violations', 'tokens', 'entropy', 'mutual_information']
        for field in numeric_fields:
            if field in log_data and not isinstance(log_data[field], (int, float)):
                return False
        
        # Check spikes structure
        if 'spikes' in log_data:
            if not isinstance(log_data['spikes'], list):
                return False
            for spike in log_data['spikes']:
                if not isinstance(spike, dict) or 'intensity' not in spike:
                    return False
                if not isinstance(spike['intensity'], (int, float)):
                    return False
        
        return True
    except Exception:
        return False


def load_log_files(log_dir: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Load and validate all JSON log files from the specified directory.
    Returns list of valid log entries.
    """
    valid_logs = []
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"Error: Log directory {log_dir} does not exist")
        return valid_logs
    
    json_files = list(log_path.glob("*.json"))
    # Filter out the schema file
    json_files = [f for f in json_files if 'schema' not in f.name.lower()]
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                log_data = json.load(f)
            
            if validate_log_entry(log_data, schema):
                valid_logs.append(log_data)
                print(f"✓ Validated: {file_path.name}")
            else:
                print(f"✗ Invalid schema: {file_path.name} (skipping)")
                
        except json.JSONDecodeError as e:
            print(f"✗ JSON error in {file_path.name}: {e} (skipping)")
        except Exception as e:
            print(f"✗ Error processing {file_path.name}: {e} (skipping)")
    
    print(f"Successfully validated {len(valid_logs)} log files")
    return valid_logs


def calculate_averages(logs: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate average values for all numeric columns."""
    if not logs:
        return {}
    
    # Numeric fields to average
    numeric_fields = ['violations', 'tokens', 'entropy', 'mutual_information', 'seed']
    averages = {}
    
    for field in numeric_fields:
        values = [log[field] for log in logs if field in log and isinstance(log[field], (int, float))]
        if values:
            averages[f'avg_{field}'] = sum(values) / len(values)
    
    # Calculate average spike intensity
    all_intensities = []
    for log in logs:
        if 'spikes' in log and isinstance(log['spikes'], list):
            for spike in log['spikes']:
                if isinstance(spike, dict) and 'intensity' in spike:
                    if isinstance(spike['intensity'], (int, float)):
                        all_intensities.append(spike['intensity'])
    
    if all_intensities:
        averages['avg_spike_intensity'] = sum(all_intensities) / len(all_intensities)
    
    return averages


def create_csv_output(logs: List[Dict[str, Any]], output_file: str):
    """Create CSV output with log data and summary row."""
    if not logs:
        print("No valid logs to aggregate")
        return
    
    # Determine all possible fieldnames from the logs
    all_fields = set()
    for log in logs:
        all_fields.update(log.keys())
    
    # Order fields logically
    ordered_fields = ['timestamp', 'session_id', 'branch', 'model', 'seed', 
                     'violations', 'tokens', 'entropy', 'mutual_information']
    
    # Add any additional fields not in the ordered list
    remaining_fields = sorted(all_fields - set(ordered_fields))
    fieldnames = ordered_fields + remaining_fields
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write each log entry
        for log in logs:
            # Handle spikes field specially since it's an array
            row = log.copy()
            if 'spikes' in row:
                # Convert spikes to a readable string format
                if isinstance(row['spikes'], list):
                    spike_strs = []
                    for spike in row['spikes']:
                        if isinstance(spike, dict):
                            spike_str = f"{spike.get('term', 'unknown')}({spike.get('intensity', 0):.2f})"
                            spike_strs.append(spike_str)
                    row['spikes'] = '; '.join(spike_strs)
            writer.writerow(row)
        
        # Add summary row with averages
        averages = calculate_averages(logs)
        if averages:
            summary_row = {field: '' for field in fieldnames}
            summary_row['session_id'] = 'SUMMARY_AVERAGES'
            summary_row['timestamp'] = 'AVERAGE_VALUES'
            
            # Fill in the average values
            for field, avg_value in averages.items():
                # Map avg_field to field
                if field.startswith('avg_'):
                    original_field = field[4:]  # Remove 'avg_' prefix
                    if original_field in fieldnames:
                        summary_row[original_field] = f"{avg_value:.4f}"
                else:
                    # Handle special cases like avg_spike_intensity
                    if field == 'avg_spike_intensity':
                        summary_row['spikes'] = f"average_intensity:{avg_value:.4f}"
            
            writer.writerow(summary_row)


def main():
    """Main function to handle CLI and orchestrate the aggregation."""
    parser = argparse.ArgumentParser(
        description='Aggregate soul debate log files with schema validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aggregate_logs.py --out results.csv
  python aggregate_logs.py --out /tmp/aggregated_soul_debates.csv
        """
    )
    
    parser.add_argument(
        '--out', 
        type=str, 
        default='aggregated_soul_debate_logs.csv',
        help='Output CSV filename (default: aggregated_soul_debate_logs.csv)'
    )
    
    parser.add_argument(
        '--logs', 
        type=str, 
        default='logs',
        help='Directory containing log files (default: logs)'
    )
    
    parser.add_argument(
        '--schema', 
        type=str, 
        default='logs/soul_debate_schema.json',
        help='Path to schema file (default: logs/soul_debate_schema.json)'
    )
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute paths
    script_dir = Path(__file__).parent.parent  # Go up from scripts/ to repo root
    log_dir = script_dir / args.logs
    schema_path = script_dir / args.schema
    
    print(f"Soul Debate Log Aggregator")
    print(f"=========================")
    print(f"Log directory: {log_dir}")
    print(f"Schema file: {schema_path}")
    print(f"Output file: {args.out}")
    print()
    
    # Load schema
    schema = load_schema(str(schema_path))
    
    # Load and validate log files
    logs = load_log_files(str(log_dir), schema)
    
    if not logs:
        print("No valid log files found. Exiting.")
        sys.exit(1)
    
    # Create CSV output
    try:
        create_csv_output(logs, args.out)
        print(f"\n✓ Successfully created aggregated CSV: {args.out}")
        print(f"  - Processed {len(logs)} valid log files")
        
        # Show summary statistics
        averages = calculate_averages(logs)
        if averages:
            print("\nSummary averages included in output:")
            for field, value in averages.items():
                print(f"  - {field}: {value:.4f}")
                
    except Exception as e:
        print(f"Error creating CSV output: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()