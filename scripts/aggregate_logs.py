#!/usr/bin/env python3
"""
Script to aggregate JSON log files into a CSV summary.

Loads all JSON files from /logs directory (excluding soul_debate_schema.json),
extracts session_id, entropy, mutual_information, and spike_count fields,
and writes them to logs/aggregated_logs.csv.
"""

import json
import csv
import os
from pathlib import Path


def load_json_logs():
    """Load and process all JSON log files from /logs directory."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print(f"Error: Logs directory '{logs_dir}' does not exist")
        return []
    
    json_files = logs_dir.glob("*.json")
    rows = []
    
    for json_file in json_files:
        # Skip schema file as instructed
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extract required metrics
            session_id = data.get('session_id', '')
            entropy = data.get('entropy', 0.0)
            mutual_information = data.get('mutual_information', 0.0)
            spikes = data.get('spikes', [])
            spike_count = len(spikes)
            
            # Create row for CSV (using session_id as run_id)
            row = {
                'run_id': session_id,
                'avg_entropy': entropy,
                'max_MI': mutual_information,
                'spike_count': spike_count
            }
            rows.append(row)
            print(f"Processed {json_file.name}: session_id={session_id}, entropy={entropy}, MI={mutual_information}, spikes={spike_count}")
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not process {json_file}: {e}")
        except Exception as e:
            print(f"Error: Unexpected error processing {json_file}: {e}")
    
    return rows


def write_csv(rows):
    """Write aggregated data to CSV file."""
    output_file = "logs/aggregated_logs.csv"
    
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['run_id', 'avg_entropy', 'max_MI', 'spike_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Successfully wrote aggregated data to {output_file}")
        print(f"   Total rows: {len(rows)}")
        return output_file
        
    except Exception as e:
        print(f"Error: Could not write to {output_file}: {e}")
        return None


def main():
    """Main function to aggregate logs into CSV."""
    print("🔄 Starting log aggregation...")
    
    # Load JSON logs
    rows = load_json_logs()
    
    if not rows:
        print("⚠️  No valid log files found to process")
        return
    
    # Write to CSV
    output_file = write_csv(rows)
    
    if output_file:
        print(f"🎉 Log aggregation completed! Output written to: {output_file}")
    else:
        print("❌ Log aggregation failed")


if __name__ == "__main__":
    main()