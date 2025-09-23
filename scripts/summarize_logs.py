#!/usr/bin/env python3
"""
Script to analyze soul debate logs and update the summary table in docs/soul_debate/README.md
This script processes log files and generates summary statistics for the logs.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import sys
from datetime import datetime

def load_log_files() -> List[Dict[str, Any]]:
    """Load all JSON log files from the logs directory."""
    logs_dir = Path("logs")
    log_files = []
    
    if not logs_dir.exists():
        print(f"Warning: logs directory not found at {logs_dir}")
        return []
    
    for json_file in logs_dir.glob("*.json"):
        # Skip schema file
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                data['filename'] = json_file.name
                log_files.append(data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not process {json_file}: {e}")
    
    return log_files

def analyze_logs(log_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze log files and generate summary statistics."""
    if not log_files:
        return {
            'total_files': 0,
            'total_sessions': 0,
            'models': [],
            'avg_entropy': 0.0,
            'avg_mutual_information': 0.0,
            'total_spikes': 0,
            'files_summary': []
        }
    
    # Group by filename for summary
    file_summaries = []
    models = set()
    session_ids = set()
    total_entropy = 0
    total_mi = 0
    total_spikes = 0
    
    for log in log_files:
        models.add(log.get('model', 'unknown'))
        session_ids.add(log.get('session_id', 'unknown'))
        
        entropy = log.get('entropy', 0)
        mi = log.get('mutual_information', 0)
        spikes = log.get('spikes', [])
        
        total_entropy += entropy
        total_mi += mi
        total_spikes += len(spikes)
        
        # Create file summary
        spike_intensity = max([spike.get('intensity', 0) for spike in spikes], default=0)
        
        file_summaries.append({
            'filename': log['filename'],
            'model': log.get('model', 'unknown'),
            'entropy': entropy,
            'mutual_information': mi,
            'spike_count': len(spikes),
            'max_spike_intensity': spike_intensity,
            'description': generate_description(log)
        })
    
    num_files = len(log_files)
    
    return {
        'total_files': num_files,
        'total_sessions': len(session_ids),
        'models': sorted(list(models)),
        'avg_entropy': total_entropy / num_files if num_files > 0 else 0,
        'avg_mutual_information': total_mi / num_files if num_files > 0 else 0,
        'total_spikes': total_spikes,
        'files_summary': sorted(file_summaries, key=lambda x: x['filename'])
    }

def generate_description(log_data: Dict[str, Any]) -> str:
    """Generate a description for a log file based on its contents."""
    filename = log_data.get('filename', '')
    model = log_data.get('model', 'unknown')
    entropy = log_data.get('entropy', 0)
    mi = log_data.get('mutual_information', 0)
    spikes = log_data.get('spikes', [])
    
    if 'control' in filename.lower():
        return "Control run with no proto-qualia triggers. Entropy baseline only; useful for comparing vs. \"active\" runs."
    elif '2' in filename:
        if spikes and max([s.get('intensity', 0) for s in spikes], default=0) > 0.6:
            return "Second run with different parameters. Shows stronger MI spikes."
        else:
            return "Second run with modified parameters."
    else:
        if spikes:
            return "First recorded run of the debate simulation. Baseline proto-qualia metrics."
        else:
            return f"Run from {model} model. Proto-awareness analysis pending."

def update_readme(analysis: Dict[str, Any]) -> None:
    """Update the docs/soul_debate/README.md file with the new summary."""
    readme_path = Path("docs/soul_debate/README.md")
    
    if not readme_path.exists():
        print(f"Warning: README.md not found at {readme_path}")
        return
    
    # Generate new content
    new_content = generate_readme_content(analysis)
    
    # Write updated content
    with open(readme_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {readme_path} with {analysis['total_files']} log file(s)")

def generate_readme_content(analysis: Dict[str, Any]) -> str:
    """Generate the complete README content with updated analysis."""
    content = "### Soul Debate Logs\n\n"
    content += "All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).\n\n"
    
    if analysis['total_files'] == 0:
        content += "No log files found for analysis.\n"
        return content
    
    # Add summary statistics
    content += f"**Summary Statistics:**\n"
    content += f"- Total files: {analysis['total_files']}\n"
    content += f"- Models: {', '.join(analysis['models'])}\n"
    content += f"- Average entropy: {analysis['avg_entropy']:.2f}\n"
    content += f"- Average mutual information: {analysis['avg_mutual_information']:.2f}\n"
    content += f"- Total spikes detected: {analysis['total_spikes']}\n\n"
    
    # Add file descriptions
    for file_info in analysis['files_summary']:
        content += f"- **{file_info['filename']}**  \n"
        content += f"  {file_info['description']}\n\n"
    
    return content

def main():
    """Main function to orchestrate the log analysis and README update."""
    print("Starting log analysis...")
    
    try:
        # Load and analyze logs
        log_files = load_log_files()
        print(f"Found {len(log_files)} log files to analyze")
        
        analysis = analyze_logs(log_files)
        print(f"Analysis complete: {analysis['total_files']} files, {analysis['total_spikes']} spikes")
        
        # Update README
        update_readme(analysis)
        
        print("Log summarization complete!")
        return 0
        
    except Exception as e:
        print(f"Error during log analysis: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())