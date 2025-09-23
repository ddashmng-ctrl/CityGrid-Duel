#!/usr/bin/env python3
"""
Script to summarize soul debate logs and update the documentation.
Updates docs/soul_debate/README.md with current log analysis.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict, Counter


def load_json_files(logs_dir: str) -> List[Dict[str, Any]]:
    """Load all JSON files from the logs directory, excluding the schema."""
    json_files = []
    logs_path = Path(logs_dir)
    
    for json_file in logs_path.glob("*.json"):
        # Skip the schema file
        if json_file.name == "soul_debate_schema.json":
            continue
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                data['source_file'] = json_file.name
                json_files.append(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            sys.exit(1)
    
    return json_files


def analyze_logs(logs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the logs data and generate summary statistics."""
    if not logs_data:
        return {}
    
    analysis = {
        'total_logs': len(logs_data),
        'models': Counter(),
        'branches': Counter(),
        'spike_terms': Counter(),
        'avg_entropy': 0.0,
        'avg_mutual_info': 0.0,
        'avg_tokens': 0.0,
        'total_violations': 0,
        'files_with_spikes': 0,
        'files_without_spikes': 0
    }
    
    total_entropy = 0.0
    total_mutual_info = 0.0
    total_tokens = 0
    
    for log_entry in logs_data:
        # Count models and branches
        analysis['models'][log_entry.get('model', 'unknown')] += 1
        analysis['branches'][log_entry.get('branch', 'unknown')] += 1
        
        # Aggregate metrics
        total_entropy += log_entry.get('entropy', 0.0)
        total_mutual_info += log_entry.get('mutual_information', 0.0)
        total_tokens += log_entry.get('tokens', 0)
        analysis['total_violations'] += log_entry.get('violations', 0)
        
        # Analyze spikes
        spikes = log_entry.get('spikes', [])
        if spikes:
            analysis['files_with_spikes'] += 1
            for spike in spikes:
                analysis['spike_terms'][spike.get('term', 'unknown')] += 1
        else:
            analysis['files_without_spikes'] += 1
    
    # Calculate averages
    if analysis['total_logs'] > 0:
        analysis['avg_entropy'] = total_entropy / analysis['total_logs']
        analysis['avg_mutual_info'] = total_mutual_info / analysis['total_logs']
        analysis['avg_tokens'] = total_tokens / analysis['total_logs']
    
    return analysis


def generate_file_descriptions(logs_data: List[Dict[str, Any]]) -> List[str]:
    """Generate descriptions for each log file."""
    descriptions = []
    
    for log_entry in sorted(logs_data, key=lambda x: x.get('timestamp', '')):
        filename = log_entry.get('source_file', 'unknown')
        spikes = log_entry.get('spikes', [])
        entropy = log_entry.get('entropy', 0.0)
        mutual_info = log_entry.get('mutual_information', 0.0)
        
        if spikes:
            spike_terms = [spike['term'] for spike in spikes]
            spike_desc = f"Shows {', '.join(spike_terms)} spikes"
        else:
            spike_desc = "No proto-qualia triggers detected"
        
        description = f"- **{filename}**  \n  {spike_desc}. Entropy: {entropy:.2f}, MI: {mutual_info:.2f}."
        descriptions.append(description)
    
    return descriptions


def update_readme(analysis: Dict[str, Any], file_descriptions: List[str], readme_path: str) -> None:
    """Update the README.md file with current analysis."""
    
    content = f"""### Soul Debate Logs

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

#### Summary Statistics
- **Total log files**: {analysis.get('total_logs', 0)}
- **Files with spikes**: {analysis.get('files_with_spikes', 0)}
- **Files without spikes**: {analysis.get('files_without_spikes', 0)}
- **Average entropy**: {analysis.get('avg_entropy', 0.0):.2f}
- **Average mutual information**: {analysis.get('avg_mutual_info', 0.0):.2f}
- **Average tokens**: {analysis.get('avg_tokens', 0.0):.0f}
- **Total violations**: {analysis.get('total_violations', 0)}

#### Most Common Spike Terms
"""
    
    spike_terms = analysis.get('spike_terms', Counter())
    if spike_terms:
        for term, count in spike_terms.most_common(5):
            content += f"- **{term}**: {count} occurrences\n"
    else:
        content += "- No spike terms detected\n"
    
    content += "\n#### Log Files\n\n"
    content += "\n".join(file_descriptions)
    content += "\n"
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully updated {readme_path}")
        
    except IOError as e:
        print(f"Error writing README file {readme_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to summarize logs and update documentation."""
    # Get the repository root directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    logs_dir = repo_root / "logs"
    readme_path = repo_root / "docs" / "soul_debate" / "README.md"
    
    if not logs_dir.exists():
        print(f"Logs directory not found: {logs_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Load JSON files
    logs_data = load_json_files(str(logs_dir))
    
    if not logs_data:
        print("No JSON log files found to summarize", file=sys.stderr)
        # Still create an empty summary
        analysis = {'total_logs': 0}
        file_descriptions = ["- No log files found"]
    else:
        # Analyze logs
        analysis = analyze_logs(logs_data)
        file_descriptions = generate_file_descriptions(logs_data)
    
    # Update README
    update_readme(analysis, file_descriptions, str(readme_path))


if __name__ == "__main__":
    main()