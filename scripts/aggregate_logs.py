#!/usr/bin/env python3
"""
aggregate_logs.py

Aggregates JSON log files from the /logs/ directory into a single CSV file.
Extracts run_id, avg_entropy, max_MI, and spike_count from each JSON file.

Usage: 
    python scripts/aggregate_logs.py
    
The script will automatically:
- Load all JSON files from the /logs/ directory (excluding schema files)
- Extract required fields: session_id → run_id, entropy → avg_entropy, 
  mutual_information → max_MI, len(spikes) → spike_count
- Handle errors gracefully for invalid JSON or missing fields
- Output aggregated data to logs/aggregated_logs.csv

Example output CSV:
    run_id,avg_entropy,max_MI,spike_count
    duel-001,1.88,0.39,2
    duel-002,2.15,0.46,2
    duel-003,1.62,0.29,0
"""

import json
import csv
import os
import glob
from pathlib import Path


def load_json_files(logs_dir):
    """
    Load all JSON files from the logs directory.
    
    Args:
        logs_dir (str): Path to the logs directory
        
    Returns:
        list: List of tuples (filename, data) for successfully loaded files
    """
    json_files = []
    json_pattern = os.path.join(logs_dir, "*.json")
    
    for file_path in glob.glob(json_pattern):
        filename = os.path.basename(file_path)
        
        # Skip schema files as they don't contain log data
        if 'schema' in filename.lower():
            print(f"⊖ Skipping schema file: {filename}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_files.append((filename, data))
                print(f"✓ Loaded {filename}")
        except json.JSONDecodeError as e:
            print(f"⚠ Warning: Invalid JSON in {file_path}: {e}")
        except Exception as e:
            print(f"⚠ Warning: Error loading {file_path}: {e}")
    
    return json_files


def extract_fields(filename, data):
    """
    Extract required fields from JSON data.
    
    Args:
        filename (str): Name of the source file
        data (dict): JSON data
        
    Returns:
        dict: Extracted fields or None if critical fields are missing
    """
    extracted = {}
    
    # Extract run_id (from session_id field)
    run_id = data.get('session_id')
    if run_id is None:
        print(f"⚠ Warning: Missing 'session_id' field in {filename}")
        return None
    extracted['run_id'] = run_id
    
    # Extract avg_entropy (from entropy field)
    avg_entropy = data.get('entropy')
    if avg_entropy is None:
        print(f"⚠ Warning: Missing 'entropy' field in {filename}")
        return None
    extracted['avg_entropy'] = avg_entropy
    
    # Extract max_MI (from mutual_information field)
    max_mi = data.get('mutual_information')
    if max_mi is None:
        print(f"⚠ Warning: Missing 'mutual_information' field in {filename}")
        return None
    extracted['max_MI'] = max_mi
    
    # Extract spike_count (from length of spikes array)
    spikes = data.get('spikes', [])
    if not isinstance(spikes, list):
        print(f"⚠ Warning: 'spikes' field is not a list in {filename}")
        spikes = []
    extracted['spike_count'] = len(spikes)
    
    return extracted


def aggregate_logs(logs_dir, output_file):
    """
    Main function to aggregate logs from JSON files to CSV.
    
    Args:
        logs_dir (str): Path to the logs directory
        output_file (str): Path to the output CSV file
    """
    print(f"Aggregating logs from {logs_dir}...")
    
    # Check if logs directory exists
    if not os.path.exists(logs_dir):
        print(f"Error: Logs directory {logs_dir} does not exist")
        return False
    
    # Load JSON files
    json_files = load_json_files(logs_dir)
    
    if not json_files:
        print("Warning: No valid JSON files found in logs directory")
        return False
    
    # Extract data from each file
    aggregated_data = []
    for filename, data in json_files:
        extracted = extract_fields(filename, data)
        if extracted:
            aggregated_data.append(extracted)
        else:
            print(f"⚠ Skipping {filename} due to missing required fields")
    
    if not aggregated_data:
        print("Error: No valid data extracted from JSON files")
        return False
    
    # Write to CSV
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['run_id', 'avg_entropy', 'max_MI', 'spike_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in aggregated_data:
                writer.writerow(row)
        
        print(f"✓ Successfully wrote {len(aggregated_data)} records to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error writing CSV file: {e}")
        return False


def main():
    """Main entry point for the script."""
    # Determine script directory and repository root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    logs_dir = os.path.join(repo_root, "logs")
    output_file = os.path.join(repo_root, "logs", "aggregated_logs.csv")
    
    print("=== CityGrid Duel Log Aggregator ===")
    print(f"Logs directory: {logs_dir}")
    print(f"Output file: {output_file}")
    print()
    
    success = aggregate_logs(logs_dir, output_file)
    
    if success:
        print("\n✓ Log aggregation completed successfully!")
    else:
        print("\n✗ Log aggregation failed!")
        exit(1)


if __name__ == "__main__":
    main()