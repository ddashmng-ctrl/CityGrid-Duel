#!/usr/bin/env python3
"""
Aggregate logs script for CityGrid Duel.

This script loads all JSON files from the /logs/ directory and extracts
specific fields to create a consolidated CSV file.
"""

import json
import csv
import glob
import os
import sys
from pathlib import Path


def load_json_file(file_path):
    """
    Load and parse a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Parsed JSON data or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load {file_path}: {e}", file=sys.stderr)
        return None


def extract_fields(data, file_path):
    """
    Extract required fields from JSON data.
    
    Args:
        data (dict): Parsed JSON data
        file_path (str): Path to the file (for error reporting)
        
    Returns:
        dict: Extracted fields or None if required fields are missing
    """
    try:
        # Extract run_id (from session_id field)
        run_id = data.get('session_id')
        if run_id is None:
            print(f"Warning: Missing 'session_id' field in {file_path}", file=sys.stderr)
            return None
            
        # Extract avg_entropy (from entropy field)
        avg_entropy = data.get('entropy')
        if avg_entropy is None:
            print(f"Warning: Missing 'entropy' field in {file_path}", file=sys.stderr)
            return None
            
        # Extract max_MI (from mutual_information field)
        max_MI = data.get('mutual_information')
        if max_MI is None:
            print(f"Warning: Missing 'mutual_information' field in {file_path}", file=sys.stderr)
            return None
            
        # Extract spike_count (length of spikes array)
        spikes = data.get('spikes', [])
        if not isinstance(spikes, list):
            print(f"Warning: 'spikes' field is not a list in {file_path}", file=sys.stderr)
            spike_count = 0
        else:
            spike_count = len(spikes)
            
        return {
            'run_id': run_id,
            'avg_entropy': avg_entropy,
            'max_MI': max_MI,
            'spike_count': spike_count
        }
        
    except Exception as e:
        print(f"Warning: Error extracting fields from {file_path}: {e}", file=sys.stderr)
        return None


def aggregate_logs(logs_dir, output_file):
    """
    Aggregate all JSON logs into a single CSV file.
    
    Args:
        logs_dir (str): Directory containing JSON log files
        output_file (str): Path for output CSV file
        
    Returns:
        int: Number of successfully processed files
    """
    # Find all JSON files in the logs directory, excluding schema files
    json_pattern = os.path.join(logs_dir, "*.json")
    all_json_files = glob.glob(json_pattern)
    
    # Filter out schema files
    json_files = [f for f in all_json_files if not f.endswith('_schema.json')]
    
    if not json_files:
        print(f"Warning: No JSON files found in {logs_dir}", file=sys.stderr)
        return 0
    
    aggregated_data = []
    processed_count = 0
    
    for file_path in sorted(json_files):
        print(f"Processing: {file_path}")
        
        # Load JSON data
        data = load_json_file(file_path)
        if data is None:
            continue
            
        # Extract required fields
        extracted = extract_fields(data, file_path)
        if extracted is None:
            continue
            
        aggregated_data.append(extracted)
        processed_count += 1
    
    # Write to CSV file
    if aggregated_data:
        fieldnames = ['run_id', 'avg_entropy', 'max_MI', 'spike_count']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(aggregated_data)
            
            print(f"Successfully wrote {len(aggregated_data)} records to {output_file}")
            
        except IOError as e:
            print(f"Error: Failed to write CSV file {output_file}: {e}", file=sys.stderr)
            return 0
    else:
        print("Warning: No valid data to write to CSV", file=sys.stderr)
        return 0
    
    return processed_count


def main():
    """Main function."""
    # Get the repository root directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # Define paths
    logs_dir = repo_root / "logs"
    output_file = logs_dir / "aggregated_logs.csv"
    
    print(f"Looking for JSON files in: {logs_dir}")
    print(f"Output CSV will be saved to: {output_file}")
    
    # Check if logs directory exists
    if not logs_dir.exists():
        print(f"Error: Logs directory {logs_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Aggregate logs
    processed = aggregate_logs(str(logs_dir), str(output_file))
    
    if processed == 0:
        print("Error: No files were successfully processed", file=sys.stderr)
        sys.exit(1)
    
    print(f"Aggregation complete. Processed {processed} files.")


if __name__ == "__main__":
    main()