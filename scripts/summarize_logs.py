#!/usr/bin/env python3
"""
Summarize logs into README format.
This script processes aggregated logs and updates documentation.
"""
import argparse
import json
import os
import sys
from datetime import datetime


def summarize_logs():
    """Summarize aggregated logs and update README if needed."""
    logs_dir = "logs"
    aggregated_file = os.path.join(logs_dir, "aggregated_logs.json")
    
    if not os.path.exists(aggregated_file):
        print(f"Warning: Aggregated logs file not found at {aggregated_file}", file=sys.stderr)
        return 1
    
    try:
        with open(aggregated_file, 'r') as f:
            logs_data = json.load(f)
    except Exception as e:
        print(f"Error reading aggregated logs: {e}", file=sys.stderr)
        return 1
    
    # Generate summary statistics
    total_files = logs_data.get("total_files_processed", 0)
    files_info = logs_data.get("files", [])
    
    summary = {
        "last_updated": datetime.now().isoformat(),
        "total_log_files": total_files,
        "total_size_bytes": sum(f.get("size_bytes", 0) for f in files_info),
        "files_summary": [
            {
                "name": f.get("filename", "unknown"),
                "size": f.get("size_bytes", 0)
            }
            for f in files_info
        ]
    }
    
    # Write summary to logs directory
    summary_file = os.path.join(logs_dir, "logs_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Generate README section (basic implementation)
    readme_section = f"""
## 📊 Logs Summary

**Last Updated:** {summary['last_updated']}
**Total Log Files:** {summary['total_log_files']}
**Total Size:** {summary['total_size_bytes']} bytes

### Processed Files:
"""
    
    for file_info in summary['files_summary']:
        readme_section += f"- `{file_info['name']}` ({file_info['size']} bytes)\n"
    
    # Write README section to file
    readme_logs_file = os.path.join(logs_dir, "README_logs_section.md")
    with open(readme_logs_file, 'w') as f:
        f.write(readme_section)
    
    print(f"Log summary generated: {summary_file}")
    print(f"README section generated: {readme_logs_file}")
    return 0


def main():
    """Main entry point for the summarize_logs script."""
    parser = argparse.ArgumentParser(description="Summarize logs into README format")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()
    
    try:
        result = summarize_logs()
        if not args.quiet:
            print("Log summarization completed successfully")
        return result
    except Exception as e:
        print(f"Error during log summarization: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())