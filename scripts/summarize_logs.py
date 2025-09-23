#!/usr/bin/env python3
"""
Soul Debate Log Summarizer

This script processes soul debate logs from the logs/ directory and generates
a summary table with run statistics. The table is sorted by run_id and includes
mean values in the final row.

The script writes to docs/soul_debate/README.md without duplicating old tables.

Usage:
    python3 scripts/summarize_logs.py [--logs-dir LOGS_DIR] [--output OUTPUT_FILE]
"""

import json
import glob
import os
import argparse
from typing import List, Dict, Any


def load_soul_debate_logs(logs_dir: str = "logs") -> List[Dict[str, Any]]:
    """Load all soul debate log files from the logs directory."""
    pattern = os.path.join(logs_dir, "*soul_debate*.json")
    log_files = glob.glob(pattern)
    
    # Filter out schema files
    log_files = [f for f in log_files if not f.endswith("schema.json")]
    
    logs = []
    for file_path in log_files:
        try:
            with open(file_path, 'r') as f:
                log_data = json.load(f)
                logs.append(log_data)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    return logs


def extract_summary_data(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract summary statistics from log data."""
    summary_data = []
    
    for log in logs:
        # Extract relevant fields
        run_id = log.get("session_id", "unknown")
        avg_entropy = log.get("entropy", 0.0)
        spike_count = len(log.get("spikes", []))
        max_mi = log.get("mutual_information", 0.0)
        
        summary_data.append({
            "run_id": run_id,
            "avg_entropy": avg_entropy,
            "spike_count": spike_count,
            "max_MI": max_mi
        })
    
    return summary_data


def calculate_means(summary_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate mean values for numeric columns."""
    if not summary_data:
        return {"run_id": "MEAN", "avg_entropy": 0.0, "spike_count": 0.0, "max_MI": 0.0}
    
    total_entropy = sum(row["avg_entropy"] for row in summary_data)
    total_spikes = sum(row["spike_count"] for row in summary_data)
    total_mi = sum(row["max_MI"] for row in summary_data)
    count = len(summary_data)
    
    return {
        "run_id": "MEAN",
        "avg_entropy": total_entropy / count,
        "spike_count": total_spikes / count,
        "max_MI": total_mi / count
    }


def generate_table_markdown(summary_data: List[Dict[str, Any]]) -> str:
    """Generate markdown table from summary data."""
    if not summary_data:
        return "No data available.\n"
    
    # Sort by run_id
    sorted_data = sorted(summary_data, key=lambda x: x["run_id"])
    
    # Calculate means and append
    means = calculate_means(sorted_data)
    all_data = sorted_data + [means]
    
    # Generate table
    lines = []
    lines.append("| run_id | avg_entropy | spike_count | max_MI |")
    lines.append("|--------|-------------|-------------|--------|")
    
    for row in all_data:
        run_id = row["run_id"]
        avg_entropy = f"{row['avg_entropy']:.3f}"
        spike_count = f"{row['spike_count']:.1f}" if row["run_id"] == "MEAN" else str(row["spike_count"])
        max_mi = f"{row['max_MI']:.3f}"
        
        lines.append(f"| {run_id} | {avg_entropy} | {spike_count} | {max_mi} |")
    
    return "\n".join(lines) + "\n"


def update_readme(table_markdown: str, readme_path: str = "docs/soul_debate/README.md") -> None:
    """Update the README.md file with the new table, avoiding duplication."""
    # Read current content
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Check if there's already a summary table section
    lines = content.split('\n')
    new_lines = []
    in_summary_section = False
    table_added = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for existing Summary Table section
        if line.strip() == "### Summary Table":
            # Skip the entire summary section
            in_summary_section = True
            # Add the new summary table here
            if not table_added:
                new_lines.append("### Summary Table")
                new_lines.append("")
                new_lines.append(table_markdown.rstrip())
                table_added = True
            # Skip to the next section or end
            i += 1
            # Skip empty lines and table content
            while i < len(lines):
                next_line = lines[i]
                if (next_line.strip().startswith("|") or 
                    next_line.strip() == "" or
                    next_line.strip().startswith("###")):
                    if next_line.strip().startswith("###"):
                        # Start of next section, don't skip this line
                        break
                    i += 1
                else:
                    break
            in_summary_section = False
            continue
        else:
            new_lines.append(line)
            i += 1
    
    # If no table section was found, append it at the end
    if not table_added:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.append("### Summary Table")
        new_lines.append("")
        new_lines.append(table_markdown.rstrip())
    
    # Write updated content
    os.makedirs(os.path.dirname(readme_path), exist_ok=True)
    with open(readme_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Updated {readme_path} with summary table")


def main():
    """Main function to process logs and update README."""
    parser = argparse.ArgumentParser(
        description="Summarize soul debate logs and update README.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 scripts/summarize_logs.py
    python3 scripts/summarize_logs.py --logs-dir my_logs --output my_readme.md
        """
    )
    parser.add_argument(
        "--logs-dir", 
        default="logs", 
        help="Directory containing soul debate log files (default: logs)"
    )
    parser.add_argument(
        "--output", 
        default="docs/soul_debate/README.md", 
        help="Output README file to update (default: docs/soul_debate/README.md)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("Soul Debate Log Summarizer")
        print("=" * 30)
    
    # Load logs
    logs = load_soul_debate_logs(args.logs_dir)
    if not args.quiet:
        print(f"Loaded {len(logs)} log files")
    
    if not logs:
        if not args.quiet:
            print("No log files found. Exiting.")
        return
    
    # Extract summary data
    summary_data = extract_summary_data(logs)
    if not args.quiet:
        print(f"Extracted data for {len(summary_data)} runs")
    
    # Generate table
    table_markdown = generate_table_markdown(summary_data)
    if not args.quiet:
        print("\nGenerated summary table:")
        print(table_markdown)
    
    # Update README
    update_readme(table_markdown, args.output)
    if not args.quiet:
        print(f"{args.output} updated successfully!")


if __name__ == "__main__":
    main()