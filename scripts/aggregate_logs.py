#!/usr/bin/env python3
"""
Aggregate logs and generate time-series data for analysis.
Processes soul debate logs and creates aggregated metrics.
"""

import json
import glob
import argparse
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict


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


def aggregate_time_series(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create time-series aggregations of log data."""
    time_series = {
        'entropy_over_time': [],
        'spikes_over_time': [],
        'mutual_info_over_time': [],
        'model_activity': defaultdict(list)
    }
    
    # Sort logs by timestamp
    sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
    
    for log in sorted_logs:
        timestamp = log.get('timestamp', '')
        model = log.get('model', 'unknown')
        entropy = log.get('entropy', 0.0)
        mutual_info = log.get('mutual_information', 0.0)
        spikes = log.get('spikes', [])
        
        # Entropy time series
        time_series['entropy_over_time'].append({
            'timestamp': timestamp,
            'model': model,
            'entropy': entropy,
            'session_id': log.get('session_id', '')
        })
        
        # Mutual information time series
        time_series['mutual_info_over_time'].append({
            'timestamp': timestamp,
            'model': model,
            'mutual_information': mutual_info,
            'session_id': log.get('session_id', '')
        })
        
        # Spike count time series
        spike_count = len(spikes)
        avg_spike_intensity = sum(s.get('intensity', 0) for s in spikes) / spike_count if spike_count > 0 else 0
        
        time_series['spikes_over_time'].append({
            'timestamp': timestamp,
            'model': model,
            'spike_count': spike_count,
            'avg_spike_intensity': avg_spike_intensity,
            'session_id': log.get('session_id', '')
        })
        
        # Model activity tracking
        time_series['model_activity'][model].append({
            'timestamp': timestamp,
            'entropy': entropy,
            'spike_count': spike_count,
            'mutual_info': mutual_info
        })
    
    return time_series


def aggregate_by_model(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate statistics by model."""
    model_stats = defaultdict(lambda: {
        'total_logs': 0,
        'entropy_values': [],
        'spike_counts': [],
        'mutual_info_values': [],
        'total_tokens': 0,
        'total_violations': 0
    })
    
    for log in logs:
        model = log.get('model', 'unknown')
        stats = model_stats[model]
        
        stats['total_logs'] += 1
        stats['entropy_values'].append(log.get('entropy', 0.0))
        stats['spike_counts'].append(len(log.get('spikes', [])))
        stats['mutual_info_values'].append(log.get('mutual_information', 0.0))
        stats['total_tokens'] += log.get('tokens', 0)
        stats['total_violations'] += log.get('violations', 0)
    
    # Calculate summary statistics
    summary_stats = {}
    for model, stats in model_stats.items():
        if stats['total_logs'] > 0:
            summary_stats[model] = {
                'total_logs': stats['total_logs'],
                'avg_entropy': sum(stats['entropy_values']) / len(stats['entropy_values']),
                'max_entropy': max(stats['entropy_values']) if stats['entropy_values'] else 0,
                'min_entropy': min(stats['entropy_values']) if stats['entropy_values'] else 0,
                'avg_spike_count': sum(stats['spike_counts']) / len(stats['spike_counts']),
                'max_spike_count': max(stats['spike_counts']) if stats['spike_counts'] else 0,
                'avg_mutual_info': sum(stats['mutual_info_values']) / len(stats['mutual_info_values']),
                'total_tokens': stats['total_tokens'],
                'total_violations': stats['total_violations']
            }
    
    return summary_stats


def aggregate_by_session(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate statistics by session."""
    session_stats = defaultdict(lambda: {
        'logs': [],
        'models': set(),
        'entropy_progression': [],
        'spike_progression': []
    })
    
    for log in logs:
        session_id = log.get('session_id', 'unknown')
        model = log.get('model', 'unknown')
        
        session_stats[session_id]['logs'].append(log)
        session_stats[session_id]['models'].add(model)
        session_stats[session_id]['entropy_progression'].append({
            'timestamp': log.get('timestamp', ''),
            'entropy': log.get('entropy', 0.0),
            'model': model
        })
        session_stats[session_id]['spike_progression'].append({
            'timestamp': log.get('timestamp', ''),
            'spike_count': len(log.get('spikes', [])),
            'model': model
        })
    
    # Convert sets to lists for JSON serialization
    for session_id in session_stats:
        session_stats[session_id]['models'] = list(session_stats[session_id]['models'])
        # Sort progressions by timestamp
        session_stats[session_id]['entropy_progression'].sort(key=lambda x: x['timestamp'])
        session_stats[session_id]['spike_progression'].sort(key=lambda x: x['timestamp'])
    
    return dict(session_stats)


def main():
    parser = argparse.ArgumentParser(description='Aggregate logs and generate time-series data')
    parser.add_argument('--logs-pattern', default='logs/*.json',
                       help='Pattern to match log files (default: logs/*.json)')
    parser.add_argument('--output', default='output/aggregated_logs.json',
                       help='Output file for aggregated results')
    
    args = parser.parse_args()
    
    # Load logs
    print(f"Loading logs from pattern: {args.logs_pattern}")
    logs = load_log_files(args.logs_pattern)
    print(f"Loaded {len(logs)} log files")
    
    if not logs:
        print("No logs found. Exiting.")
        return
    
    # Generate aggregations
    time_series = aggregate_time_series(logs)
    model_stats = aggregate_by_model(logs)
    session_stats = aggregate_by_session(logs)
    
    # Create aggregated report
    aggregated_report = {
        'timestamp': datetime.now().isoformat(),
        'total_logs_processed': len(logs),
        'time_series': time_series,
        'model_statistics': model_stats,
        'session_statistics': session_stats,
        'source_pattern': args.logs_pattern
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(aggregated_report, f, indent=2)
    
    print(f"Aggregated results saved to: {args.output}")
    print(f"Models analyzed: {list(model_stats.keys())}")
    print(f"Sessions analyzed: {len(session_stats)}")
    print(f"Time series points: entropy={len(time_series['entropy_over_time'])}, "
          f"spikes={len(time_series['spikes_over_time'])}")


if __name__ == '__main__':
    main()