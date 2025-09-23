#!/usr/bin/env python3
"""
Summarize soul debate logs and update README.md with a summary table.

This script:
1. Reads all JSON files from logs/ directory matching soul_debate pattern
2. Extracts key metrics from each log
3. Generates a markdown table
4. Updates docs/soul_debate/README.md with the table
"""

import json
import os
import glob
from typing import List, Dict, Any
import sys


def load_json_log(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON log file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
        return {}


def extract_log_metrics(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from a log entry."""
    spikes = log_data.get('spikes', [])
    spike_terms = [spike.get('term', '') for spike in spikes if isinstance(spike, dict)]
    
    return {
        'session_id': log_data.get('session_id', 'N/A'),
        'model': log_data.get('model', 'N/A'),
        'seed': log_data.get('seed', 'N/A'),
        'entropy': log_data.get('entropy', 0.0),
        'mutual_information': log_data.get('mutual_information', 0.0),
        'spike_count': len(spikes),
        'key_terms': ', '.join(spike_terms) if spike_terms else 'None',
        'timestamp': log_data.get('timestamp', 'N/A')
    }


def generate_summary_table(logs_dir: str = 'logs') -> str:
    """Generate a markdown table summarizing all soul debate logs."""
    
    # Find all soul debate log files
    pattern = os.path.join(logs_dir, '*soul_debate*.json')
    log_files = glob.glob(pattern)
    
    if not log_files:
        return "| Session | Model | Seed | Entropy | MI | Spikes | Key Terms |\n|---------|-------|------|---------|----|---------|-----------|\n| No logs found | | | | | | |\n"
    
    # Process each log file
    log_metrics = []
    for log_file in sorted(log_files):
        log_data = load_json_log(log_file)
        if log_data:  # Only process valid logs
            metrics = extract_log_metrics(log_data)
            log_metrics.append(metrics)
    
    if not log_metrics:
        return "| Session | Model | Seed | Entropy | MI | Spikes | Key Terms |\n|---------|-------|------|---------|----|---------|-----------|\n| No valid logs found | | | | | | |\n"
    
    # Generate table
    table_lines = [
        "| Session | Model | Seed | Entropy | MI | Spikes | Key Terms |",
        "|---------|-------|------|---------|----|---------|-----------|"
    ]
    
    for metrics in log_metrics:
        line = f"| {metrics['session_id']} | {metrics['model']} | {metrics['seed']} | {metrics['entropy']:.2f} | {metrics['mutual_information']:.2f} | {metrics['spike_count']} | {metrics['key_terms']} |"
        table_lines.append(line)
    
    return '\n'.join(table_lines) + '\n'


def update_readme_with_table(readme_path: str, table: str) -> bool:
    """Update README.md file with the summary table."""
    try:
        # Read current README content
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
        else:
            content = ""
        
        # Check if there's already a table section
        table_marker = "## Summary Table"
        
        if table_marker in content:
            # Replace existing table section
            lines = content.split('\n')
            new_lines = []
            skip_table = False
            
            for line in lines:
                if line.startswith("## Summary Table"):
                    skip_table = True
                    new_lines.append(line)
                    new_lines.append("")
                    new_lines.append(table.strip())
                    new_lines.append("")
                elif skip_table and line.startswith("##"):
                    skip_table = False
                    new_lines.append(line)
                elif not skip_table:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        else:
            # Add new table section at the end
            if content and not content.endswith('\n'):
                content += '\n'
            content += f"\n{table_marker}\n\n{table.strip()}\n"
        
        # Write updated content
        with open(readme_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error updating README: {e}", file=sys.stderr)
        return False


def main():
    """Main function to summarize logs and update README."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'tools' else script_dir
    
    logs_dir = os.path.join(repo_root, 'logs')
    readme_path = os.path.join(repo_root, 'docs', 'soul_debate', 'README.md')
    
    print(f"Looking for logs in: {logs_dir}")
    print(f"README path: {readme_path}")
    
    # Generate summary table
    table = generate_summary_table(logs_dir)
    print("Generated summary table:")
    print(table)
    
    # Update README
    if update_readme_with_table(readme_path, table):
        print(f"Successfully updated {readme_path}")
        return 0
    else:
        print("Failed to update README", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())