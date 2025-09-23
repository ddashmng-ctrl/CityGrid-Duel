#!/usr/bin/env python3
"""
Script to summarize logs and generate a leaderboard.
This script reads the aggregated logs and creates a leaderboard summary.
"""

import json
import csv
import os
from pathlib import Path
from collections import defaultdict

def load_aggregated_data():
    """Load data from aggregated CSV file."""
    csv_file = Path("logs/aggregated_logs.csv")
    if not csv_file.exists():
        print("No aggregated_logs.csv found. Run aggregate_logs.py first.")
        return []
    
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    return data

def generate_leaderboard_table(data):
    """Generate a markdown table for the leaderboard."""
    if not data:
        return "## Leaderboard\n\nNo data available for leaderboard generation."
    
    # Separate simulation results and soul debate logs
    simulation_data = [row for row in data if row['source'] == 'simulation_results' and row['avg_grid_draw_kw']]
    soul_debate_data = [row for row in data if row['source'] == 'soul_debate_logs']
    
    markdown = "## 🏆 CityGrid Duel Leaderboard\n\n"
    
    # Simulation Results Leaderboard (lower kW is better)
    if simulation_data:
        # Sort by average grid draw (lower is better)
        simulation_data.sort(key=lambda x: float(x['avg_grid_draw_kw']) if x['avg_grid_draw_kw'] else float('inf'))
        
        markdown += "### 🏙️ Simulation Results (Lower Average Grid Draw is Better)\n\n"
        markdown += "| Rank | Model | Avg Grid Draw (kW) | Violations | Duration (hours) | File |\n"
        markdown += "|------|-------|-------------------|------------|------------------|------|\n"
        
        for i, row in enumerate(simulation_data, 1):
            avg_kw = f"{float(row['avg_grid_draw_kw']):.2f}" if row['avg_grid_draw_kw'] else "N/A"
            violations = row['violations'] if row['violations'] else "0"
            duration = row['simulation_hours'] if row['simulation_hours'] else "N/A"
            model = row['model'] if row['model'] else "Unknown"
            filename = row['filename']
            markdown += f"| {i} | {model} | {avg_kw} | {violations} | {duration} | `{filename}` |\n"
        
        markdown += "\n"
    
    # Soul Debate Logs Summary
    if soul_debate_data:
        markdown += "### 🧠 Soul Debate Logs Summary\n\n"
        markdown += "| Model | Files | Avg Tokens | Avg Entropy | Avg Mutual Info | Total Spikes | Max Spike Intensity |\n"
        markdown += "|-------|-------|------------|-------------|-----------------|--------------|--------------------|\n"
        
        # Group by model
        model_stats = defaultdict(list)
        for row in soul_debate_data:
            model = row['model'] if row['model'] else "Unknown"
            model_stats[model].append(row)
        
        for model, rows in model_stats.items():
            file_count = len(rows)
            avg_tokens = sum(int(row['tokens']) if row['tokens'] else 0 for row in rows) / file_count if file_count > 0 else 0
            avg_entropy = sum(float(row['entropy']) if row['entropy'] else 0 for row in rows) / file_count if file_count > 0 else 0
            avg_mutual_info = sum(float(row['mutual_information']) if row['mutual_information'] else 0 for row in rows) / file_count if file_count > 0 else 0
            total_spikes = sum(int(row['spike_count']) if row['spike_count'] else 0 for row in rows)
            max_spike_intensity = max(float(row['max_spike_intensity']) if row['max_spike_intensity'] else 0 for row in rows)
            
            markdown += f"| {model} | {file_count} | {avg_tokens:.0f} | {avg_entropy:.2f} | {avg_mutual_info:.2f} | {total_spikes} | {max_spike_intensity:.2f} |\n"
        
        markdown += "\n"
    
    # Recent Activity
    if data:
        markdown += "### 📊 Recent Activity\n\n"
        # Sort by timestamp (most recent first)
        recent_data = sorted([row for row in data if row['timestamp']], 
                           key=lambda x: x['timestamp'], reverse=True)[:5]
        
        if recent_data:
            markdown += "| Timestamp | Model | Source | File |\n"
            markdown += "|-----------|-------|--------|------|\n"
            
            for row in recent_data:
                timestamp = row['timestamp'][:19] if row['timestamp'] else "N/A"  # Remove timezone for brevity
                model = row['model'] if row['model'] else "Unknown"
                source = "Simulation" if row['source'] == 'simulation_results' else "Soul Debate"
                filename = row['filename']
                markdown += f"| {timestamp} | {model} | {source} | `{filename}` |\n"
        else:
            markdown += "No recent activity found.\n"
    
    markdown += f"\n---\n*Last updated: {len(data)} total entries processed*\n"
    
    return markdown

def save_leaderboard(markdown_content):
    """Save the leaderboard to a file."""
    output_file = "leaderboard_summary.md"
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    print(f"Leaderboard saved to {output_file}")

def main():
    """Main function to generate and save the leaderboard."""
    data = load_aggregated_data()
    leaderboard_markdown = generate_leaderboard_table(data)
    
    # Print the leaderboard to stdout (for GitHub Actions to capture)
    print(leaderboard_markdown)
    
    # Also save to a file
    save_leaderboard(leaderboard_markdown)

if __name__ == "__main__":
    main()