#!/usr/bin/env python3
"""
Summarize logs and update README.md with the latest aggregated statistics.
"""

import csv
import json
import os
from datetime import datetime
from statistics import mean, median


def load_aggregated_data(csv_file):
    """Load the aggregated CSV data."""
    if not os.path.exists(csv_file):
        print(f"Aggregated CSV file {csv_file} not found")
        return []
    
    data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                row['seed'] = int(row['seed']) if row['seed'] else 0
                row['violations'] = int(row['violations']) if row['violations'] else 0
                row['tokens'] = int(row['tokens']) if row['tokens'] else 0
                row['spike_count'] = int(row['spike_count']) if row['spike_count'] else 0
                row['entropy'] = float(row['entropy']) if row['entropy'] else 0.0
                row['mutual_information'] = float(row['mutual_information']) if row['mutual_information'] else 0.0
                row['text_length'] = int(row['text_length']) if row['text_length'] else 0
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    return data


def generate_summary(data):
    """Generate summary statistics from the aggregated data."""
    if not data:
        return {
            'total_entries': 0,
            'summary': 'No data available'
        }
    
    total_entries = len(data)
    models = list(set(row['model'] for row in data))
    branches = list(set(row['branch'] for row in data))
    
    # Calculate statistics
    avg_tokens = mean(row['tokens'] for row in data) if data else 0
    avg_spike_count = mean(row['spike_count'] for row in data) if data else 0
    avg_entropy = mean(row['entropy'] for row in data) if data else 0
    avg_mutual_info = mean(row['mutual_information'] for row in data) if data else 0
    
    # Find most common spike terms
    all_spike_terms = []
    for row in data:
        if row['spike_terms']:
            terms = row['spike_terms'].split('|')
            all_spike_terms.extend(terms)
    
    spike_frequency = {}
    for term in all_spike_terms:
        spike_frequency[term] = spike_frequency.get(term, 0) + 1
    
    top_spike_terms = sorted(spike_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Group by model for comparison
    model_stats = {}
    for model in models:
        model_data = [row for row in data if row['model'] == model]
        if model_data:
            model_stats[model] = {
                'count': len(model_data),
                'avg_entropy': mean(row['entropy'] for row in model_data),
                'avg_mutual_info': mean(row['mutual_information'] for row in model_data),
                'avg_spike_count': mean(row['spike_count'] for row in model_data)
            }
    
    summary = {
        'total_entries': total_entries,
        'models': models,
        'branches': branches,
        'avg_tokens': avg_tokens,
        'avg_spike_count': avg_spike_count,
        'avg_entropy': avg_entropy,
        'avg_mutual_info': avg_mutual_info,
        'top_spike_terms': top_spike_terms,
        'model_stats': model_stats,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    return summary


def update_readme(summary):
    """Update the README.md file with the latest summary."""
    readme_path = "README.md"
    
    # Read existing README
    existing_content = ""
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Generate new soul debate section
    soul_debate_section = f"""
## 🧠 Soul Debate Analytics

**Last Updated:** {summary['last_updated']}  
**Total Log Entries:** {summary['total_entries']}

### Model Performance Summary
"""
    
    if summary['model_stats']:
        for model, stats in summary['model_stats'].items():
            soul_debate_section += f"""
**{model}:**
- Entries: {stats['count']}
- Avg Entropy: {stats['avg_entropy']:.3f}
- Avg Mutual Information: {stats['avg_mutual_info']:.3f}
- Avg Spike Count: {stats['avg_spike_count']:.2f}
"""
    
    soul_debate_section += f"""
### Key Metrics
- **Average Token Count:** {summary['avg_tokens']:.1f}
- **Average Entropy:** {summary['avg_entropy']:.3f}
- **Average Mutual Information:** {summary['avg_mutual_info']:.3f}
- **Average Spike Count:** {summary['avg_spike_count']:.2f}
"""
    
    if summary['top_spike_terms']:
        soul_debate_section += """
### Most Frequent Spike Terms
"""
        for term, count in summary['top_spike_terms']:
            soul_debate_section += f"- **{term}:** {count} occurrences\n"
    
    soul_debate_section += "\n---\n"
    
    # Check if there's already a soul debate section
    soul_section_start = existing_content.find("## 🧠 Soul Debate Analytics")
    
    if soul_section_start != -1:
        # Find the end of the section (next ## or end of file)
        section_end = existing_content.find("\n## ", soul_section_start + 1)
        if section_end == -1:
            section_end = existing_content.find("\n---", soul_section_start + 1)
            if section_end != -1:
                section_end = existing_content.find("\n", section_end + 4)
        
        if section_end == -1:
            section_end = len(existing_content)
        
        # Replace the existing section
        updated_content = (existing_content[:soul_section_start] + 
                         soul_debate_section + 
                         existing_content[section_end:])
    else:
        # Add to the end of the file
        updated_content = existing_content.rstrip() + "\n\n" + soul_debate_section
    
    # Write updated README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated {readme_path} with latest soul debate analytics")


if __name__ == "__main__":
    csv_file = "aggregated_logs.csv"
    
    # Load and summarize data
    data = load_aggregated_data(csv_file)
    summary = generate_summary(data)
    
    # Print summary to console
    print("=== Soul Debate Log Summary ===")
    print(f"Total entries: {summary['total_entries']}")
    if summary['total_entries'] > 0:
        print(f"Models: {', '.join(summary['models'])}")
        print(f"Branches: {', '.join(summary['branches'])}")
        print(f"Average entropy: {summary['avg_entropy']:.3f}")
        print(f"Average mutual information: {summary['avg_mutual_info']:.3f}")
        print(f"Average spike count: {summary['avg_spike_count']:.2f}")
        
        if summary['top_spike_terms']:
            print("Top spike terms:")
            for term, count in summary['top_spike_terms']:
                print(f"  - {term}: {count}")
    
    # Update README
    update_readme(summary)