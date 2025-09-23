#!/usr/bin/env python3
"""
Aggregate logs from various simulation runs into consolidated format.
This is a minimal implementation for the logs pipeline workflow.
"""
import argparse
import json
import os
import glob
import sys


def aggregate_logs():
    """Aggregate logs from output directory into a single summary file."""
    output_dir = "output"
    logs_dir = "logs"
    
    # Ensure directories exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Find all JSON files in output directory
    json_files = glob.glob(os.path.join(output_dir, "*.json"))
    
    aggregated_data = {
        "timestamp": "2024-09-23T17:00:00Z",
        "total_files_processed": len(json_files),
        "files": []
    }
    
    # Process each JSON file
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            file_info = {
                "filename": os.path.basename(file_path),
                "path": file_path,
                "size_bytes": os.path.getsize(file_path),
                "summary": data if isinstance(data, dict) else {"raw_data": data}
            }
            aggregated_data["files"].append(file_info)
            
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}", file=sys.stderr)
    
    # Write aggregated logs
    output_file = os.path.join(logs_dir, "aggregated_logs.json")
    with open(output_file, 'w') as f:
        json.dump(aggregated_data, f, indent=2)
    
    print(f"Successfully aggregated {len(json_files)} files into {output_file}")
    return 0


def main():
    """Main entry point for the aggregate_logs script."""
    parser = argparse.ArgumentParser(description="Aggregate simulation logs")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()
    
    try:
        result = aggregate_logs()
        if not args.quiet:
            print("Log aggregation completed successfully")
        return result
    except Exception as e:
        print(f"Error during log aggregation: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())