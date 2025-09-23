#!/usr/bin/env python3
"""
Aggregate logs from the soul debate simulation.
This script processes raw soul debate logs and generates aggregated statistics.
"""

import json
import os
import sys
import glob
from pathlib import Path
import argparse


def load_log_file(filepath):
    """Load and validate a soul debate log file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return None


def aggregate_logs(logs_dir="logs", output_file="logs/aggregated_logs.json"):
    """Aggregate all soul debate log files in the specified directory."""
    logs_pattern = os.path.join(logs_dir, "*soul_debate*.json")
    log_files = glob.glob(logs_pattern)
    
    if not log_files:
        print(f"No soul debate log files found in {logs_dir}", file=sys.stderr)
        return False
    
    print(f"Found {len(log_files)} log files to aggregate")
    
    aggregated_data = {
        "metadata": {
            "aggregation_timestamp": None,  # Would be set to current time in real implementation
            "total_files_processed": 0,
            "files_processed": []
        },
        "summary": {
            "total_runs": 0,
            "successful_runs": 0,
            "average_entropy": 0.0,
            "average_mi_spikes": 0.0,
            "proto_qualia_events": 0
        },
        "detailed_metrics": []
    }
    
    successful_logs = 0
    total_entropy = 0.0
    total_mi_spikes = 0.0
    total_proto_qualia = 0
    
    for log_file in log_files:
        print(f"Processing {log_file}")
        log_data = load_log_file(log_file)
        
        if log_data is None:
            continue
            
        successful_logs += 1
        aggregated_data["metadata"]["files_processed"].append(os.path.basename(log_file))
        
        # Extract metrics from actual log structure
        entropy = log_data.get("entropy", 0.0)
        mi_spikes = log_data.get("mutual_information", 0.0)
        spikes_data = log_data.get("spikes", [])
        proto_qualia = len(spikes_data)  # Number of spike events as proto-qualia indicator
        
        total_entropy += entropy
        total_mi_spikes += mi_spikes
        total_proto_qualia += proto_qualia
        
        aggregated_data["detailed_metrics"].append({
            "file": os.path.basename(log_file),
            "entropy": entropy,
            "mi_spikes": mi_spikes,
            "proto_qualia_events": proto_qualia
        })
    
    # Calculate averages
    if successful_logs > 0:
        aggregated_data["summary"]["total_runs"] = len(log_files)
        aggregated_data["summary"]["successful_runs"] = successful_logs
        aggregated_data["summary"]["average_entropy"] = total_entropy / successful_logs
        aggregated_data["summary"]["average_mi_spikes"] = total_mi_spikes / successful_logs
        aggregated_data["summary"]["proto_qualia_events"] = total_proto_qualia
        aggregated_data["metadata"]["total_files_processed"] = successful_logs
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write aggregated data
    with open(output_file, 'w') as f:
        json.dump(aggregated_data, f, indent=2)
    
    print(f"Aggregated data written to {output_file}")
    print(f"Successfully processed {successful_logs}/{len(log_files)} files")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Aggregate soul debate logs")
    parser.add_argument("--logs-dir", default="logs", help="Directory containing log files")
    parser.add_argument("--output", default="logs/aggregated_logs.json", help="Output file for aggregated data")
    
    args = parser.parse_args()
    
    success = aggregate_logs(args.logs_dir, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()