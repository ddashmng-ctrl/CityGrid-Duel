#!/usr/bin/env python3
"""
Script to summarize logs and generate leaderboard for the PR workflow.
This script creates a markdown leaderboard table from aggregated data.
"""

import json
import csv
import os
import sys
import glob
from pathlib import Path

def load_simulation_results():
    """Load simulation results from output directory."""
    results = []
    
    # Define patterns for finding simulation results
    patterns = {
        "baseline": "output/baseline*_summary.json",
        "orion": "output/orion_v*/orion*_summary.json",
        "grok": "output/orion_v*/grok*_summary.json"
    }
    
    for label, pattern in patterns.items():
        files = sorted(glob.glob(pattern))
        if files:
            path = files[-1]  # Take the latest file
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                avg_kw = data.get('average_grid_draw_kw')
                if avg_kw is not None:
                    results.append({
                        'label': label,
                        'avg_kw': avg_kw,
                        'seed': data.get('seed', 42),
                        'violations': data.get('comfort_violations', 0),
                        'duration': data.get('simulation_duration_hours', 72),
                        'path': path
                    })
            except Exception as e:
                print(f"Warning: Could not load {path}: {e}")
    
    return results

def load_soul_debate_logs():
    """Load soul debate logs for additional metrics."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []
    
    logs = []
    for json_file in logs_dir.glob("*.json"):
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            logs.append({
                'filename': json_file.name,
                'model': data.get('model', 'unknown'),
                'tokens': data.get('tokens', 0),
                'entropy': data.get('entropy', 0.0),
                'mutual_information': data.get('mutual_information', 0.0),
                'spike_count': len(data.get('spikes', [])),
                'max_spike_intensity': max([s.get('intensity', 0) for s in data.get('spikes', [])], default=0)
            })
        except Exception as e:
            print(f"Warning: Could not process {json_file}: {e}")
    
    return logs

def generate_leaderboard_markdown():
    """Generate markdown leaderboard table."""
    
    # Load simulation results
    sim_results = load_simulation_results()
    soul_logs = load_soul_debate_logs()
    
    # Sort simulation results by average kW (lower is better)
    sim_results.sort(key=lambda x: x['avg_kw'])
    
    markdown = []
    markdown.append("# 🏆 CityGrid Duel Leaderboard")
    markdown.append("")
    
    if sim_results:
        markdown.append("## 🔋 Simulation Results (Lower kW is better)")
        markdown.append("")
        markdown.append("| Rank | Model | Avg Grid Draw (kW) | Violations | Duration (h) | File |")
        markdown.append("|------|-------|-------------------|------------|--------------|------|")
        
        for i, result in enumerate(sim_results, 1):
            markdown.append(f"| {i} | **{result['label']}** | {result['avg_kw']:.2f} | {result['violations']} | {result['duration']} | `{os.path.basename(result['path'])}` |")
        
        markdown.append("")
    
    if soul_logs:
        markdown.append("## 🧠 Soul Debate Metrics")
        markdown.append("")
        markdown.append("| Model | Tokens | Entropy | Mutual Info | Spike Count | Max Intensity | File |")
        markdown.append("|-------|--------|---------|-------------|-------------|---------------|------|")
        
        # Sort by mutual information (higher is more interesting)
        soul_logs.sort(key=lambda x: x['mutual_information'], reverse=True)
        
        for log in soul_logs:
            markdown.append(f"| **{log['model']}** | {log['tokens']} | {log['entropy']:.2f} | {log['mutual_information']:.2f} | {log['spike_count']} | {log['max_spike_intensity']:.2f} | `{log['filename']}` |")
        
        markdown.append("")
    
    if not sim_results and not soul_logs:
        markdown.append("No results found to display in leaderboard.")
        markdown.append("")
    
    # Add metadata
    markdown.append("---")
    markdown.append("*Leaderboard generated automatically from PR changes*")
    
    return "\n".join(markdown)

def save_leaderboard_to_file(content, filename="leaderboard.md"):
    """Save leaderboard content to a file."""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Leaderboard saved to {filename}")

def main():
    """Main function to generate and output leaderboard."""
    try:
        leaderboard = generate_leaderboard_markdown()
        
        # Save to file for GitHub Actions to use
        save_leaderboard_to_file(leaderboard)
        
        # Also print to stdout for direct use
        print("=== LEADERBOARD ===")
        print(leaderboard)
        
        return 0
    except Exception as e:
        print(f"Error generating leaderboard: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())