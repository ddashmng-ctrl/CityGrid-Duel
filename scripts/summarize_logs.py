#!/usr/bin/env python3
"""
Summarize soul debate logs and update docs/soul_debate/README.md in-place.
"""

import json
import glob
import os
import sys
import argparse
from pathlib import Path


def load_log_file(file_path):
    """Load and parse a JSON log file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Handle escaped newlines in JSON content
            content = content.replace('\\n', '\n')
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def analyze_logs(logs_dir):
    """Analyze all soul debate log files and generate summary data."""
    log_files = glob.glob(os.path.join(logs_dir, "example_soul_debate*.json"))
    log_summaries = []
    
    for log_file in sorted(log_files):
        log_data = load_log_file(log_file)
        if log_data is None:
            continue
            
        filename = os.path.basename(log_file)
        
        # Extract key metrics
        entropy = log_data.get('entropy', 0)
        mi = log_data.get('mutual_information', 0)
        spikes = log_data.get('spikes', [])
        spike_count = len(spikes)
        max_spike_intensity = max([spike.get('intensity', 0) for spike in spikes], default=0)
        
        # Determine description based on filename and metrics
        if 'control' in filename:
            description = f"Control run with no proto-qualia triggers. Entropy baseline only; useful for comparing vs. \"active\" runs."
        elif filename == 'example_soul_debate.json':
            description = f"First recorded run of the debate simulation. Baseline proto-qualia metrics."
        elif filename == 'example_soul_debate_2.json':
            description = f"Second run with different parameters. Shows stronger MI spikes."
        else:
            description = f"Soul debate run with {spike_count} spikes, max intensity {max_spike_intensity:.2f}."
        
        log_summaries.append({
            'filename': filename,
            'description': description,
            'entropy': entropy,
            'mi': mi,
            'spike_count': spike_count,
            'max_intensity': max_spike_intensity
        })
    
    return log_summaries


def generate_readme_content(log_summaries):
    """Generate the updated README content."""
    content = """### Soul Debate Logs

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

"""
    
    for log in log_summaries:
        content += f"- **{log['filename']}**  \n"
        content += f"  {log['description']}\n\n"
    
    return content


def update_readme(readme_path, log_summaries, quiet=False):
    """Update the README.md file in-place with new log summaries."""
    new_content = generate_readme_content(log_summaries)
    
    try:
        with open(readme_path, 'w') as f:
            f.write(new_content)
        
        if not quiet:
            print(f"Updated {readme_path} with {len(log_summaries)} log summaries")
        
        return True
    except IOError as e:
        print(f"Error updating {readme_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Summarize soul debate logs into README")
    parser.add_argument('--quiet', action='store_true', help="Suppress output messages")
    parser.add_argument('--logs-dir', default='logs', help="Directory containing log files")
    parser.add_argument('--readme-path', default='docs/soul_debate/README.md', help="Path to README file")
    
    args = parser.parse_args()
    
    # Convert to absolute paths based on repository root
    repo_root = Path(__file__).parent.parent
    logs_dir = repo_root / args.logs_dir
    readme_path = repo_root / args.readme_path
    
    if not logs_dir.exists():
        print(f"Error: Logs directory {logs_dir} does not exist")
        sys.exit(1)
    
    if not readme_path.parent.exists():
        print(f"Error: README directory {readme_path.parent} does not exist")
        sys.exit(1)
    
    # Analyze logs
    log_summaries = analyze_logs(str(logs_dir))
    
    if not log_summaries:
        print("Error: No valid log files found")
        sys.exit(1)
    
    # Update README
    success = update_readme(str(readme_path), log_summaries, args.quiet)
    
    if not success:
        sys.exit(1)
    
    if not args.quiet:
        print("Log summarization completed successfully")


if __name__ == '__main__':
    main()