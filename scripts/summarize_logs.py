#!/usr/bin/env python3
"""
summarize_logs.py - Extract and summarize soul debate logs

This script iterates through all JSON files in the /logs/ directory,
extracts avg_entropy, spike_count, and max_MI fields, and generates
a human-readable summary table that is appended to docs/soul_debate/README.md.
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def load_json_file(filepath: str) -> Optional[Dict]:
    """
    Load and parse a JSON file with error handling.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary containing parsed JSON data, or None if error occurred
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {filepath}: {e}")
        return None
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Warning: Error reading {filepath}: {e}")
        return None


def extract_metrics(data: Dict, filename: str) -> Optional[Dict]:
    """
    Extract required metrics from JSON data.
    
    Args:
        data: Parsed JSON data
        filename: Name of the source file for error reporting
        
    Returns:
        Dictionary with extracted metrics, or None if required fields missing
    """
    try:
        # Extract entropy (maps to avg_entropy)
        entropy = data.get('entropy')
        if entropy is None:
            print(f"Warning: Missing 'entropy' field in {filename}")
            return None
            
        # Extract spikes array and count (maps to spike_count)
        spikes = data.get('spikes', [])
        spike_count = len(spikes)
        
        # Extract mutual_information (maps to max_MI)
        mutual_information = data.get('mutual_information')
        if mutual_information is None:
            print(f"Warning: Missing 'mutual_information' field in {filename}")
            return None
            
        # Extract additional metadata for better summary
        timestamp = data.get('timestamp', 'Unknown')
        session_id = data.get('session_id', 'Unknown')
        model = data.get('model', 'Unknown')
        
        return {
            'filename': filename,
            'avg_entropy': entropy,
            'spike_count': spike_count,
            'max_MI': mutual_information,
            'timestamp': timestamp,
            'session_id': session_id,
            'model': model
        }
        
    except Exception as e:
        print(f"Warning: Error extracting metrics from {filename}: {e}")
        return None


def process_logs_directory(logs_dir: str) -> List[Dict]:
    """
    Process all JSON files in the logs directory.
    
    Args:
        logs_dir: Path to the logs directory
        
    Returns:
        List of dictionaries containing extracted metrics
    """
    if not os.path.exists(logs_dir):
        print(f"Error: Logs directory not found: {logs_dir}")
        return []
    
    json_pattern = os.path.join(logs_dir, "*.json")
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"Warning: No JSON files found in {logs_dir}")
        return []
    
    print(f"Found {len(json_files)} JSON files in {logs_dir}")
    
    results = []
    for filepath in sorted(json_files):
        filename = os.path.basename(filepath)
        
        # Skip schema files
        if 'schema' in filename.lower():
            print(f"Skipping schema file: {filename}")
            continue
            
        print(f"Processing: {filename}")
        
        data = load_json_file(filepath)
        if data is None:
            continue
            
        metrics = extract_metrics(data, filename)
        if metrics is not None:
            results.append(metrics)
    
    return results


def generate_summary_table(results: List[Dict]) -> str:
    """
    Generate a human-readable summary table from extracted metrics.
    
    Args:
        results: List of metric dictionaries
        
    Returns:
        Formatted markdown table as string
    """
    if not results:
        return "\n**No valid log data found for summary.**\n"
    
    # Generate timestamp for the summary
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start building the table
    table_lines = [
        "",
        "## Log Summary",
        f"*Generated on {now}*",
        "",
        "| File | Avg Entropy | Spike Count | Max MI | Session ID | Model |",
        "|------|-------------|-------------|--------|------------|-------|"
    ]
    
    # Add data rows
    for result in results:
        filename = result['filename']
        avg_entropy = f"{result['avg_entropy']:.2f}" if isinstance(result['avg_entropy'], (int, float)) else str(result['avg_entropy'])
        spike_count = str(result['spike_count'])
        max_mi = f"{result['max_MI']:.2f}" if isinstance(result['max_MI'], (int, float)) else str(result['max_MI'])
        session_id = result['session_id']
        model = result['model']
        
        table_lines.append(f"| {filename} | {avg_entropy} | {spike_count} | {max_mi} | {session_id} | {model} |")
    
    # Add summary statistics
    entropies = [r['avg_entropy'] for r in results if isinstance(r['avg_entropy'], (int, float))]
    spike_counts = [r['spike_count'] for r in results if isinstance(r['spike_count'], int)]
    mis = [r['max_MI'] for r in results if isinstance(r['max_MI'], (int, float))]
    
    if entropies and spike_counts and mis:
        table_lines.extend([
            "|------|-------------|-------------|--------|------------|-------|",
            f"| **Average** | {sum(entropies)/len(entropies):.2f} | {sum(spike_counts)/len(spike_counts):.1f} | {sum(mis)/len(mis):.2f} | - | - |"
        ])
    
    table_lines.append("")  # Empty line at end
    
    return "\n".join(table_lines)


def append_to_readme(readme_path: str, summary_table: str) -> bool:
    """
    Append the summary table to the README.md file.
    
    Args:
        readme_path: Path to the README.md file
        summary_table: Formatted summary table string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(readme_path):
            print(f"Warning: README file not found at {readme_path}")
            return False
        
        # Read existing content
        with open(readme_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Check if summary already exists (to avoid duplicates)
        if "## Log Summary" in existing_content:
            print("Note: Existing log summary found. Replacing with updated version.")
            # Find the start of the existing summary
            start_idx = existing_content.find("## Log Summary")
            if start_idx != -1:
                # Find the next section or end of file
                remaining = existing_content[start_idx:]
                next_section = remaining.find("\n## ", 1)  # Look for next section after the summary
                
                if next_section != -1:
                    # Replace just the summary section
                    existing_content = existing_content[:start_idx] + summary_table + "\n" + remaining[next_section:]
                else:
                    # Summary is at the end, replace everything after the start
                    existing_content = existing_content[:start_idx] + summary_table
        else:
            # Append new summary
            existing_content += summary_table
        
        # Write updated content
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(existing_content)
        
        print(f"Successfully appended summary to {readme_path}")
        return True
        
    except Exception as e:
        print(f"Error appending to README: {e}")
        return False


def main():
    """Main function to orchestrate the log summarization process."""
    
    # Define paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    logs_dir = os.path.join(repo_root, "logs")
    readme_path = os.path.join(repo_root, "docs", "soul_debate", "README.md")
    
    print("=== Soul Debate Log Summarizer ===")
    print(f"Logs directory: {logs_dir}")
    print(f"README path: {readme_path}")
    print()
    
    # Process all JSON files in logs directory
    results = process_logs_directory(logs_dir)
    
    if not results:
        print("No valid log data found. Exiting.")
        return 1
    
    print(f"\nSuccessfully processed {len(results)} log files.")
    
    # Generate summary table
    summary_table = generate_summary_table(results)
    print("\nGenerated summary table:")
    print(summary_table)
    
    # Append to README
    success = append_to_readme(readme_path, summary_table)
    
    if success:
        print("\n✅ Summary successfully appended to README.md")
        return 0
    else:
        print("\n❌ Failed to append summary to README.md")
        return 1


if __name__ == "__main__":
    exit(main())