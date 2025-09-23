#!/usr/bin/env python3
"""
Script to summarize JSON log files and append a Markdown table to README.md.

Loads all JSON files from /logs directory (excluding soul_debate_schema.json),
extracts session_id, entropy, mutual_information, and spike_count fields,
and appends a summary table to docs/soul_debate/README.md.
"""

import json
import os
import statistics
from pathlib import Path


def load_json_logs():
    """Load and process all JSON log files from /logs directory."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print(f"Error: Logs directory '{logs_dir}' does not exist")
        return []
    
    json_files = logs_dir.glob("*.json")
    log_data = []
    
    for json_file in json_files:
        # Skip schema file as instructed
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extract required metrics
            session_id = data.get('session_id', '')
            entropy = data.get('entropy', 0.0)
            mutual_information = data.get('mutual_information', 0.0)
            spikes = data.get('spikes', [])
            spike_count = len(spikes)
            
            # Store data for table generation
            log_entry = {
                'run_id': session_id,
                'entropy': entropy,
                'mutual_information': mutual_information,
                'spike_count': spike_count
            }
            log_data.append(log_entry)
            print(f"Processed {json_file.name}: session_id={session_id}, entropy={entropy}, MI={mutual_information}, spikes={spike_count}")
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not process {json_file}: {e}")
        except Exception as e:
            print(f"Error: Unexpected error processing {json_file}: {e}")
    
    return log_data


def generate_markdown_table(log_data):
    """Generate a Markdown table from log data."""
    if not log_data:
        return ""
    
    # Calculate mean values
    entropies = [entry['entropy'] for entry in log_data]
    mutual_infos = [entry['mutual_information'] for entry in log_data]
    spike_counts = [entry['spike_count'] for entry in log_data]
    
    mean_entropy = statistics.mean(entropies) if entropies else 0.0
    mean_mi = statistics.mean(mutual_infos) if mutual_infos else 0.0
    mean_spikes = statistics.mean(spike_counts) if spike_counts else 0.0
    
    # Build table
    table_lines = [
        "",
        "### Log Analysis Summary",
        "",
        "| Run          | Entropy       | Mutual Info   | Spike Count    |",
        "|--------------|---------------|---------------|----------------|"
    ]
    
    # Add data rows
    for entry in log_data:
        run_id = entry['run_id'] or 'Unknown'
        entropy = f"{entry['entropy']:.3f}"
        mi = f"{entry['mutual_information']:.3f}"
        spikes = str(entry['spike_count'])
        
        table_lines.append(f"| {run_id:<12} | {entropy:<13} | {mi:<13} | {spikes:<14} |")
    
    # Add mean values row
    mean_entropy_str = f"{mean_entropy:.3f}"
    mean_mi_str = f"{mean_mi:.3f}"
    mean_spikes_str = f"{mean_spikes:.1f}"
    
    table_lines.append(f"| {'Mean Values':<12} | {mean_entropy_str:<13} | {mean_mi_str:<13} | {mean_spikes_str:<14} |")
    table_lines.append("")
    
    return "\n".join(table_lines)


def append_to_readme(table_content):
    """Append table to README.md, avoiding duplicates."""
    readme_path = "docs/soul_debate/README.md"
    
    # Check if README exists
    if not os.path.exists(readme_path):
        print(f"Error: README file '{readme_path}' does not exist")
        return False
    
    try:
        # Read existing content
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check if summary table already exists
        if "### Log Analysis Summary" in content:
            print("ℹ️  Summary table already exists in README.md")
            
            # Remove existing table to replace it
            lines = content.split('\n')
            new_lines = []
            skip_table = False
            
            for line in lines:
                if line.strip() == "### Log Analysis Summary":
                    skip_table = True
                    continue
                elif skip_table and (line.startswith('### ') or line.startswith('## ') or line.startswith('# ')):
                    skip_table = False
                    new_lines.append(line)
                elif not skip_table:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines).rstrip()
        
        # Append new table
        updated_content = content + table_content
        
        # Write back to file
        with open(readme_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully updated {readme_path}")
        return True
        
    except Exception as e:
        print(f"Error: Could not update {readme_path}: {e}")
        return False


def main():
    """Main function to summarize logs and update README."""
    print("🔄 Starting log summarization...")
    
    # Load JSON logs
    log_data = load_json_logs()
    
    if not log_data:
        print("⚠️  No valid log files found to process")
        return
    
    # Generate Markdown table
    table_content = generate_markdown_table(log_data)
    
    if not table_content:
        print("❌ Failed to generate table content")
        return
    
    # Update README
    success = append_to_readme(table_content)
    
    if success:
        print(f"🎉 Log summarization completed! Summary table added to docs/soul_debate/README.md")
        print(f"   Processed {len(log_data)} log files")
    else:
        print("❌ Log summarization failed")


if __name__ == "__main__":
    main()