#!/usr/bin/env python3
"""
Script to analyze soul debate logs and update the summary table in docs/soul_debate/README.md
"""
import json
import glob
import os
import sys
from typing import Dict, List, Any


def load_log_file(filepath: str) -> Dict[str, Any]:
    """Load and parse a log file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return {}


def analyze_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from a log entry."""
    if not log_data:
        return {}
    
    spikes = log_data.get('spikes', [])
    spike_count = len(spikes)
    max_intensity = max([spike.get('intensity', 0) for spike in spikes], default=0.0)
    
    return {
        'filename': os.path.basename(log_data.get('filename', 'unknown')),
        'model': log_data.get('model', 'unknown'),
        'seed': log_data.get('seed', 'unknown'),
        'violations': log_data.get('violations', 0),
        'tokens': log_data.get('tokens', 0),
        'spike_count': spike_count,
        'max_intensity': max_intensity,
        'entropy': log_data.get('entropy', 0.0),
        'mutual_information': log_data.get('mutual_information', 0.0),
        'timestamp': log_data.get('timestamp', 'unknown')
    }


def generate_summary_table(analyses: List[Dict[str, Any]]) -> str:
    """Generate a markdown table from log analyses."""
    if not analyses:
        return "No soul debate logs found to analyze.\n"
    
    header = """### Soul Debate Logs Summary

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

| File | Model | Seed | Tokens | Spikes | Max Intensity | Entropy | MI | Notes |
|------|-------|------|--------|--------|---------------|---------|----|---------|\n"""
    
    rows = []
    for analysis in sorted(analyses, key=lambda x: x.get('timestamp', '')):
        filename = analysis.get('filename', 'unknown')
        model = analysis.get('model', 'unknown')
        seed = analysis.get('seed', 'unknown')
        tokens = analysis.get('tokens', 0)
        spike_count = analysis.get('spike_count', 0)
        max_intensity = analysis.get('max_intensity', 0.0)
        entropy = analysis.get('entropy', 0.0)
        mi = analysis.get('mutual_information', 0.0)
        
        # Generate notes based on characteristics
        notes = []
        if spike_count == 0:
            notes.append("Control run - no proto-qualia triggers")
        elif max_intensity > 0.8:
            notes.append("Strong MI spikes detected")
        elif max_intensity > 0.6:
            notes.append("Moderate proto-awareness signals")
        else:
            notes.append("Baseline proto-qualia metrics")
            
        notes_str = "; ".join(notes) if notes else "Standard run"
        
        row = f"| **{filename}** | {model} | {seed} | {tokens} | {spike_count} | {max_intensity:.2f} | {entropy:.2f} | {mi:.2f} | {notes_str} |"
        rows.append(row)
    
    return header + "\n".join(rows) + "\n"


def update_readme(summary_table: str) -> None:
    """Update the README.md file with the new summary table."""
    readme_path = "docs/soul_debate/README.md"
    
    if not os.path.exists(readme_path):
        print(f"Error: {readme_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Read current README
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {readme_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Replace the content entirely with the new summary table
    try:
        with open(readme_path, 'w') as f:
            f.write(summary_table)
        print(f"Successfully updated {readme_path}")
    except Exception as e:
        print(f"Error writing to {readme_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to process logs and update README."""
    print("Starting soul debate log analysis...")
    
    # Find all soul debate log files
    log_pattern = "logs/example_soul_debate*.json"
    log_files = glob.glob(log_pattern)
    
    if not log_files:
        print(f"No log files found matching pattern: {log_pattern}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(log_files)} log files to analyze")
    
    # Analyze each log file
    analyses = []
    for log_file in log_files:
        print(f"Analyzing {log_file}...")
        log_data = load_log_file(log_file)
        if log_data:
            log_data['filename'] = log_file  # Add filename to data
            analysis = analyze_log(log_data)
            if analysis:
                analyses.append(analysis)
    
    if not analyses:
        print("No valid log data found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Successfully analyzed {len(analyses)} log files")
    
    # Generate summary table
    summary_table = generate_summary_table(analyses)
    
    # Update README
    update_readme(summary_table)
    
    print("Soul debate log analysis complete!")


if __name__ == "__main__":
    main()