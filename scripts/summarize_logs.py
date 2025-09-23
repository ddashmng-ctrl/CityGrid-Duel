#!/usr/bin/env python3
"""
Script to summarize aggregated logs and update documentation.
This script reads logs/aggregated_logs.csv and generates a summary,
updating docs/soul_debate/README.md with current statistics.
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime

def read_aggregated_logs():
    """Read the aggregated CSV file and return parsed data."""
    csv_path = Path("logs/aggregated_logs.csv")
    
    if not csv_path.exists():
        print("Warning: aggregated_logs.csv not found")
        return []
    
    data = []
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                for field in ['violations', 'tokens', 'entropy', 'mutual_information', 
                             'spike_count', 'max_spike_intensity', 'simulation_hours', 'avg_grid_draw_kw']:
                    if row[field]:
                        try:
                            if field in ['entropy', 'mutual_information', 'avg_grid_draw_kw']:
                                row[field] = float(row[field])
                            else:
                                row[field] = int(row[field]) if '.' not in str(row[field]) else float(row[field])
                        except ValueError:
                            row[field] = 0
                    else:
                        row[field] = 0
                        
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []
    
    return data

def generate_summary_stats(data):
    """Generate summary statistics from the aggregated data."""
    if not data:
        return {
            'total_logs': 0,
            'soul_debate_logs': 0,
            'simulation_results': 0,
            'avg_entropy': 0,
            'avg_mutual_information': 0,
            'total_spikes': 0,
            'avg_grid_draw': 0,
            'total_violations': 0
        }
    
    soul_debate_logs = [row for row in data if row['source'] == 'soul_debate_logs']
    simulation_results = [row for row in data if row['source'] == 'simulation_results']
    
    # Calculate averages
    avg_entropy = sum(row['entropy'] for row in soul_debate_logs) / len(soul_debate_logs) if soul_debate_logs else 0
    avg_mi = sum(row['mutual_information'] for row in soul_debate_logs) / len(soul_debate_logs) if soul_debate_logs else 0
    total_spikes = sum(row['spike_count'] for row in soul_debate_logs)
    avg_grid_draw = sum(row['avg_grid_draw_kw'] for row in simulation_results) / len(simulation_results) if simulation_results else 0
    total_violations = sum(row['violations'] for row in data)
    
    return {
        'total_logs': len(data),
        'soul_debate_logs': len(soul_debate_logs),
        'simulation_results': len(simulation_results),
        'avg_entropy': round(avg_entropy, 4),
        'avg_mutual_information': round(avg_mi, 4),
        'total_spikes': total_spikes,
        'avg_grid_draw': round(avg_grid_draw, 4),
        'total_violations': total_violations,
        'last_updated': datetime.now().isoformat()
    }

def update_readme_with_summary(stats):
    """Update the docs/soul_debate/README.md with current summary statistics."""
    readme_path = Path("docs/soul_debate/README.md")
    
    # Ensure directory exists
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing content if it exists
    existing_content = ""
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            existing_content = f.read()
    
    # Generate updated content
    summary_section = f"""### Soul Debate Logs

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

#### Current Statistics (Last Updated: {stats['last_updated']})
- **Total Log Entries:** {stats['total_logs']}
- **Soul Debate Logs:** {stats['soul_debate_logs']}
- **Simulation Results:** {stats['simulation_results']}
- **Average Entropy:** {stats['avg_entropy']}
- **Average Mutual Information:** {stats['avg_mutual_information']}
- **Total Spike Events:** {stats['total_spikes']}
- **Average Grid Draw:** {stats['avg_grid_draw']} kW
- **Total Violations:** {stats['total_violations']}

#### Log Files
- **example_soul_debate.json**  
  First recorded run of the debate simulation. Baseline proto-qualia metrics.

- **example_soul_debate_2.json**  
  Second run with different parameters. Shows stronger MI spikes.

- **example_soul_debate_control.json**  
  Control run with no proto-qualia triggers. Entropy baseline only; useful for comparing vs. "active" runs.
"""
    
    # Write updated content
    with open(readme_path, 'w') as f:
        f.write(summary_section)
    
    print(f"Updated {readme_path} with current statistics")

def save_summary_json(stats):
    """Save summary statistics as JSON for potential future use."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    summary_path = logs_dir / "summary_stats.json"
    with open(summary_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Saved summary statistics to {summary_path}")

def main():
    """Main function to run log summarization."""
    try:
        # Read aggregated data
        data = read_aggregated_logs()
        
        # Generate summary statistics
        stats = generate_summary_stats(data)
        
        # Update README
        update_readme_with_summary(stats)
        
        # Save summary JSON
        save_summary_json(stats)
        
        print("Log summarization completed successfully")
        print(f"Processed {stats['total_logs']} log entries")
        
    except Exception as e:
        print(f"Error during log summarization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()