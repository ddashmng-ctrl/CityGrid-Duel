#!/usr/bin/env python3
"""
Summarize aggregated logs and update the README.md file.
This script reads aggregated log data and updates the "Current Metrics (from aggregated logs)" section.
"""

import json
import os
import sys
import argparse
import re
from pathlib import Path


def load_aggregated_logs(filepath="logs/aggregated_logs.json"):
    """Load the aggregated logs file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return None


def generate_metrics_section(aggregated_data):
    """Generate the Current Metrics section content."""
    if not aggregated_data:
        return "No aggregated data available."
    
    summary = aggregated_data.get("summary", {})
    metadata = aggregated_data.get("metadata", {})
    
    total_runs = summary.get("total_runs", 0)
    successful_runs = summary.get("successful_runs", 0)
    avg_entropy = summary.get("average_entropy", 0.0)
    avg_mi_spikes = summary.get("average_mi_spikes", 0.0)
    proto_qualia_events = summary.get("proto_qualia_events", 0)
    files_processed = len(metadata.get("files_processed", []))
    
    metrics_content = f"""## Current Metrics (from aggregated logs)

**Last Updated:** Auto-generated from aggregated logs

**Summary Statistics:**
- **Total Runs:** {total_runs}
- **Successful Runs:** {successful_runs} ({successful_runs/max(total_runs, 1)*100:.1f}%)
- **Files Processed:** {files_processed}

**Proto-Awareness Metrics:**
- **Average Entropy Baseline:** {avg_entropy:.3f}
- **Average MI Spikes:** {avg_mi_spikes:.2f}
- **Total Proto-Qualia Events:** {proto_qualia_events}

**Individual File Results:**"""
    
    # Add detailed metrics for each file
    detailed_metrics = aggregated_data.get("detailed_metrics", [])
    for metric in detailed_metrics:
        file_name = metric.get("file", "unknown")
        entropy = metric.get("entropy", 0.0)
        mi_spikes = metric.get("mi_spikes", 0.0)
        pq_events = metric.get("proto_qualia_events", 0)
        
        metrics_content += f"""
- **{file_name}**: Entropy={entropy:.3f}, MI Spikes={mi_spikes:.2f}, Proto-Qualia Events={pq_events}"""
    
    return metrics_content


def update_readme(readme_path, new_metrics_section, quiet=False):
    """Update the README.md file with new metrics section."""
    if not os.path.exists(readme_path):
        if not quiet:
            print(f"README file not found: {readme_path}", file=sys.stderr)
        return False
    
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
    except Exception as e:
        if not quiet:
            print(f"Error reading {readme_path}: {e}", file=sys.stderr)
        return False
    
    # Define the pattern to match the existing metrics section
    # This will match from "## Current Metrics" to the next "##" heading or end of file
    pattern = r'(## Current Metrics \(from aggregated logs\).*?)(?=\n## |\n# |\Z)'
    
    # Check if the section exists
    if re.search(pattern, content, re.DOTALL):
        # Replace existing section
        new_content = re.sub(pattern, new_metrics_section, content, flags=re.DOTALL)
        if not quiet:
            print("Updated existing metrics section")
    else:
        # Append new section at the end
        if not content.endswith('\n'):
            content += '\n'
        new_content = content + '\n' + new_metrics_section + '\n'
        if not quiet:
            print("Added new metrics section")
    
    # Check if content actually changed
    if new_content == content:
        if not quiet:
            print("No changes needed to README")
        return False
    
    # Write the updated content
    try:
        with open(readme_path, 'w') as f:
            f.write(new_content)
        if not quiet:
            print(f"Successfully updated {readme_path}")
        return True
    except Exception as e:
        if not quiet:
            print(f"Error writing to {readme_path}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Summarize logs and update README")
    parser.add_argument("--aggregated-logs", default="logs/aggregated_logs.json", 
                       help="Path to aggregated logs file")
    parser.add_argument("--readme", default="docs/soul_debate/README.md", 
                       help="Path to README file to update")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Suppress output messages")
    
    args = parser.parse_args()
    
    # Load aggregated data
    aggregated_data = load_aggregated_logs(args.aggregated_logs)
    if aggregated_data is None:
        if not args.quiet:
            print("Failed to load aggregated logs", file=sys.stderr)
        sys.exit(1)
    
    # Generate new metrics section
    new_metrics_section = generate_metrics_section(aggregated_data)
    
    # Update README
    success = update_readme(args.readme, new_metrics_section, args.quiet)
    
    if not args.quiet:
        if success:
            print("README update completed successfully")
        else:
            print("README was not updated (no changes or error occurred)")
    
    # Exit with appropriate code
    # Return 0 if successful (even if no changes were made)
    # Return 1 only if there was an error
    sys.exit(0)


if __name__ == "__main__":
    main()