#!/usr/bin/env python3
"""
Compare logs between different models/sessions.
Analyzes entropy, mutual information, and spike patterns.
"""

import json
import glob
import argparse
import os
from datetime import datetime
from typing import List, Dict, Any


def load_log_files(pattern: str) -> List[Dict[str, Any]]:
    """Load all log files matching the pattern."""
    files = glob.glob(pattern)
    logs = []
    
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                log_data = json.load(f)
                log_data['_source_file'] = file_path
                logs.append(log_data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    return logs


def compare_entropy(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare entropy values across logs."""
    entropy_data = []
    
    for log in logs:
        entropy_data.append({
            'model': log.get('model', 'unknown'),
            'session_id': log.get('session_id', 'unknown'),
            'timestamp': log.get('timestamp', ''),
            'entropy': log.get('entropy', 0.0),
            'source_file': log.get('_source_file', '')
        })
    
    # Sort by timestamp
    entropy_data.sort(key=lambda x: x['timestamp'])
    
    return {
        'entropy_comparison': entropy_data,
        'stats': {
            'total_logs': len(entropy_data),
            'avg_entropy': sum(d['entropy'] for d in entropy_data) / len(entropy_data) if entropy_data else 0,
            'max_entropy': max(d['entropy'] for d in entropy_data) if entropy_data else 0,
            'min_entropy': min(d['entropy'] for d in entropy_data) if entropy_data else 0
        }
    }


def compare_spikes(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare spike patterns across logs."""
    spike_analysis = {
        'by_model': {},
        'total_spikes': 0,
        'spike_terms': {},
        'high_intensity_spikes': []
    }
    
    for log in logs:
        model = log.get('model', 'unknown')
        spikes = log.get('spikes', [])
        
        if model not in spike_analysis['by_model']:
            spike_analysis['by_model'][model] = {
                'total_spikes': 0,
                'avg_intensity': 0.0,
                'spike_count': 0
            }
        
        for spike in spikes:
            term = spike.get('term', '')
            intensity = spike.get('intensity', 0.0)
            
            spike_analysis['total_spikes'] += 1
            spike_analysis['by_model'][model]['total_spikes'] += 1
            spike_analysis['by_model'][model]['spike_count'] += 1
            
            # Track spike terms
            if term not in spike_analysis['spike_terms']:
                spike_analysis['spike_terms'][term] = 0
            spike_analysis['spike_terms'][term] += 1
            
            # High intensity spikes (> 0.8)
            if intensity > 0.8:
                spike_analysis['high_intensity_spikes'].append({
                    'model': model,
                    'term': term,
                    'intensity': intensity,
                    'context': spike.get('context', ''),
                    'timestamp': log.get('timestamp', '')
                })
    
    # Calculate averages
    for model_data in spike_analysis['by_model'].values():
        if model_data['spike_count'] > 0:
            model_data['avg_intensity'] = model_data['total_spikes'] / model_data['spike_count']
    
    return spike_analysis


def main():
    parser = argparse.ArgumentParser(description='Compare logs between different models/sessions')
    parser.add_argument('--logs-pattern', default='logs/*.json', 
                       help='Pattern to match log files (default: logs/*.json)')
    parser.add_argument('--output', default='output/log_comparison.json',
                       help='Output file for comparison results')
    
    args = parser.parse_args()
    
    # Load logs
    print(f"Loading logs from pattern: {args.logs_pattern}")
    logs = load_log_files(args.logs_pattern)
    print(f"Loaded {len(logs)} log files")
    
    if not logs:
        print("No logs found. Exiting.")
        return
    
    # Compare entropy
    entropy_comparison = compare_entropy(logs)
    
    # Compare spikes
    spike_comparison = compare_spikes(logs)
    
    # Generate comparison report
    comparison_report = {
        'timestamp': datetime.now().isoformat(),
        'total_logs_analyzed': len(logs),
        'entropy_analysis': entropy_comparison,
        'spike_analysis': spike_comparison,
        'source_pattern': args.logs_pattern
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(comparison_report, f, indent=2)
    
    print(f"Comparison results saved to: {args.output}")
    print(f"Entropy stats: avg={entropy_comparison['stats']['avg_entropy']:.3f}, "
          f"range=[{entropy_comparison['stats']['min_entropy']:.3f}, "
          f"{entropy_comparison['stats']['max_entropy']:.3f}]")
    print(f"Spike stats: total={spike_comparison['total_spikes']}, "
          f"high_intensity={len(spike_comparison['high_intensity_spikes'])}")


if __name__ == '__main__':
    main()