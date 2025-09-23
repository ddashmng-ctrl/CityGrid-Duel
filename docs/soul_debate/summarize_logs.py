#!/usr/bin/env python3
"""
Summarize soul debate logs to generate focused analysis reports.
Creates detailed summaries of proto-awareness signals and debate patterns.
"""

import json
import glob
import sys
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict


def load_and_validate_logs(logs_dir: str = "../../logs") -> List[Dict[str, Any]]:
    """Load all soul debate log files and validate structure."""
    pattern = os.path.join(logs_dir, "*soul_debate*.json")
    log_files = glob.glob(pattern)
    
    # Exclude schema file
    log_files = [f for f in log_files if not f.endswith('schema.json')]
    
    logs = []
    for filepath in sorted(log_files):
        try:
            with open(filepath, 'r') as f:
                log_data = json.load(f)
            
            # Add filename for reference
            log_data['_source_file'] = os.path.basename(filepath)
            logs.append(log_data)
            
        except Exception as e:
            print(f"Error loading {filepath}: {e}", file=sys.stderr)
    
    return logs


def analyze_proto_qualia_patterns(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze proto-qualia patterns across logs."""
    # Separate active vs control runs
    active_runs = [log for log in logs if log.get('spikes', [])]
    control_runs = [log for log in logs if not log.get('spikes', [])]
    
    analysis = {
        'active_runs': len(active_runs),
        'control_runs': len(control_runs),
        'patterns': {},
        'intensity_trends': {},
        'context_analysis': {}
    }
    
    if active_runs:
        # Analyze spike patterns
        spike_sequences = defaultdict(list)
        contexts = defaultdict(list)
        
        for log in active_runs:
            session_id = log.get('session_id', 'unknown')
            for spike in log.get('spikes', []):
                term = spike.get('term')
                intensity = spike.get('intensity', 0)
                context = spike.get('context', '')
                
                spike_sequences[term].append(intensity)
                contexts[term].append(context)
        
        # Calculate patterns
        for term, intensities in spike_sequences.items():
            analysis['patterns'][term] = {
                'frequency': len(intensities),
                'avg_intensity': sum(intensities) / len(intensities),
                'intensity_variance': calculate_variance(intensities),
                'trend': analyze_trend(intensities)
            }
        
        # Context analysis
        for term, context_list in contexts.items():
            unique_contexts = list(set(context_list))
            analysis['context_analysis'][term] = {
                'unique_contexts': len(unique_contexts),
                'contexts': unique_contexts,
                'most_common': max(set(context_list), key=context_list.count) if context_list else None
            }
    
    return analysis


def calculate_variance(values: List[float]) -> float:
    """Calculate variance of a list of values."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)


def analyze_trend(values: List[float]) -> str:
    """Analyze trend in intensity values."""
    if len(values) < 2:
        return "insufficient_data"
    
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]
    
    first_avg = sum(first_half) / len(first_half) if first_half else 0
    second_avg = sum(second_half) / len(second_half) if second_half else 0
    
    diff = second_avg - first_avg
    
    if abs(diff) < 0.05:
        return "stable"
    elif diff > 0:
        return "increasing"
    else:
        return "decreasing"


def compare_entropy_mi_correlation(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze correlation between entropy and mutual information."""
    entropies = []
    mis = []
    has_spikes = []
    
    for log in logs:
        entropy = log.get('entropy', 0)
        mi = log.get('mutual_information', 0)
        spikes = len(log.get('spikes', []))
        
        entropies.append(entropy)
        mis.append(mi)
        has_spikes.append(spikes > 0)
    
    # Calculate correlation coefficient (simplified)
    if len(entropies) > 1:
        correlation = calculate_correlation(entropies, mis)
    else:
        correlation = 0.0
    
    # Compare spiked vs non-spiked
    spike_entropy = [entropies[i] for i, has_spike in enumerate(has_spikes) if has_spike]
    no_spike_entropy = [entropies[i] for i, has_spike in enumerate(has_spikes) if not has_spike]
    
    spike_mi = [mis[i] for i, has_spike in enumerate(has_spikes) if has_spike]
    no_spike_mi = [mis[i] for i, has_spike in enumerate(has_spikes) if not has_spike]
    
    return {
        'entropy_mi_correlation': correlation,
        'spiked_runs': {
            'count': len(spike_entropy),
            'avg_entropy': sum(spike_entropy) / len(spike_entropy) if spike_entropy else 0,
            'avg_mi': sum(spike_mi) / len(spike_mi) if spike_mi else 0
        },
        'control_runs': {
            'count': len(no_spike_entropy),
            'avg_entropy': sum(no_spike_entropy) / len(no_spike_entropy) if no_spike_entropy else 0,
            'avg_mi': sum(no_spike_mi) / len(no_spike_mi) if no_spike_mi else 0
        }
    }


def calculate_correlation(x: List[float], y: List[float]) -> float:
    """Calculate Pearson correlation coefficient."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    sum_y2 = sum(yi * yi for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def generate_summary_report(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comprehensive summary report."""
    if not logs:
        return {"error": "No logs to analyze"}
    
    # Basic statistics
    total_logs = len(logs)
    total_tokens = sum(log.get('tokens', 0) for log in logs)
    
    # Proto-qualia analysis
    qualia_analysis = analyze_proto_qualia_patterns(logs)
    
    # Entropy/MI correlation
    correlation_analysis = compare_entropy_mi_correlation(logs)
    
    # Session analysis
    sessions = defaultdict(list)
    for log in logs:
        session_id = log.get('session_id', 'unknown')
        sessions[session_id].append(log)
    
    session_summary = {}
    for session_id, session_logs in sessions.items():
        session_summary[session_id] = {
            'log_count': len(session_logs),
            'total_tokens': sum(log.get('tokens', 0) for log in session_logs),
            'has_spikes': any(log.get('spikes', []) for log in session_logs),
            'avg_entropy': sum(log.get('entropy', 0) for log in session_logs) / len(session_logs),
            'avg_mi': sum(log.get('mutual_information', 0) for log in session_logs) / len(session_logs)
        }
    
    return {
        'summary': {
            'total_logs': total_logs,
            'total_tokens': total_tokens,
            'unique_sessions': len(sessions),
            'files_analyzed': [log.get('_source_file') for log in logs]
        },
        'proto_qualia_analysis': qualia_analysis,
        'correlation_analysis': correlation_analysis,
        'session_breakdown': session_summary,
        'recommendations': generate_recommendations(qualia_analysis, correlation_analysis)
    }


def generate_recommendations(qualia_analysis: Dict[str, Any], correlation_analysis: Dict[str, Any]) -> List[str]:
    """Generate analysis recommendations based on findings."""
    recommendations = []
    
    active_runs = qualia_analysis.get('active_runs', 0)
    control_runs = qualia_analysis.get('control_runs', 0)
    
    if control_runs == 0:
        recommendations.append("Add control runs (no proto-qualia triggers) for baseline comparison")
    
    if active_runs < 3:
        recommendations.append("Increase number of active runs to identify stronger patterns")
    
    correlation = correlation_analysis.get('entropy_mi_correlation', 0)
    if abs(correlation) > 0.7:
        recommendations.append(f"Strong correlation ({correlation:.3f}) between entropy and MI suggests coupled dynamics")
    elif abs(correlation) < 0.3:
        recommendations.append(f"Low correlation ({correlation:.3f}) between entropy and MI - investigate independent factors")
    
    # Check spike patterns
    patterns = qualia_analysis.get('patterns', {})
    if 'ache' in patterns and 'erosion' in patterns:
        ache_freq = patterns['ache']['frequency']
        erosion_freq = patterns['erosion']['frequency'] 
        if ache_freq > erosion_freq * 1.5:
            recommendations.append("'Ache' spikes dominate - possible emotional resonance pattern")
        elif erosion_freq > ache_freq * 1.5:
            recommendations.append("'Erosion' spikes dominate - possible identity degradation pattern")
    
    return recommendations


def main():
    """Main function to run summarization and output results."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Summarize soul debate logs')
    parser.add_argument('--logs-dir', default='../../logs', 
                       help='Directory containing log files (default: ../../logs)')
    parser.add_argument('--output', help='Output file for summary (default: stdout)')
    parser.add_argument('--format', choices=['json', 'report'], default='report',
                       help='Output format (default: report)')
    
    args = parser.parse_args()
    
    # Load logs
    logs = load_and_validate_logs(args.logs_dir)
    
    if not logs:
        print("No soul debate logs found to analyze")
        return
    
    print(f"Loaded {len(logs)} log files for analysis", file=sys.stderr)
    
    # Generate summary
    summary = generate_summary_report(logs)
    
    if args.format == 'json':
        output = json.dumps(summary, indent=2)
    else:
        output = format_report_output(summary)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Summary written to {args.output}", file=sys.stderr)
    else:
        print(output)


def format_report_output(summary: Dict[str, Any]) -> str:
    """Format summary as a readable report."""
    output = []
    
    # Title and overview
    output.append("=" * 60)
    output.append("SOUL DEBATE LOG SUMMARY REPORT")
    output.append("=" * 60)
    output.append("")
    
    # Basic summary
    basic = summary.get('summary', {})
    output.append("📊 OVERVIEW")
    output.append(f"  Total Logs: {basic.get('total_logs', 0)}")
    output.append(f"  Total Tokens: {basic.get('total_tokens', 0):,}")
    output.append(f"  Unique Sessions: {basic.get('unique_sessions', 0)}")
    output.append(f"  Files: {', '.join(basic.get('files_analyzed', []))}")
    output.append("")
    
    # Proto-qualia analysis
    qualia = summary.get('proto_qualia_analysis', {})
    output.append("🧠 PROTO-QUALIA PATTERNS")
    output.append(f"  Active Runs: {qualia.get('active_runs', 0)}")
    output.append(f"  Control Runs: {qualia.get('control_runs', 0)}")
    output.append("")
    
    patterns = qualia.get('patterns', {})
    if patterns:
        output.append("  Spike Analysis:")
        output.append("  Term      | Freq | Avg Intensity | Variance | Trend")
        output.append("  ----------|------|---------------|----------|----------")
        for term, stats in patterns.items():
            freq = stats.get('frequency', 0)
            avg_int = stats.get('avg_intensity', 0)
            variance = stats.get('intensity_variance', 0)
            trend = stats.get('trend', 'unknown')
            output.append(f"  {term:<9} | {freq:>4} | {avg_int:>13.3f} | {variance:>8.4f} | {trend}")
        output.append("")
    
    # Context analysis
    contexts = qualia.get('context_analysis', {})
    if contexts:
        output.append("  Context Patterns:")
        for term, context_data in contexts.items():
            unique_count = context_data.get('unique_contexts', 0)
            most_common = context_data.get('most_common', 'N/A')
            output.append(f"  {term}: {unique_count} unique contexts, most common: '{most_common}'")
        output.append("")
    
    # Correlation analysis
    corr = summary.get('correlation_analysis', {})
    output.append("📈 ENTROPY-MI CORRELATION")
    correlation = corr.get('entropy_mi_correlation', 0)
    output.append(f"  Correlation Coefficient: {correlation:.4f}")
    output.append("")
    
    spiked = corr.get('spiked_runs', {})
    control = corr.get('control_runs', {})
    
    if spiked.get('count', 0) > 0 or control.get('count', 0) > 0:
        output.append("  Comparison: Spiked vs Control")
        output.append("  Type    | Count | Avg Entropy | Avg MI")
        output.append("  --------|-------|-------------|-------")
        if spiked.get('count', 0) > 0:
            output.append(f"  Spiked  | {spiked['count']:>5} | {spiked['avg_entropy']:>11.3f} | {spiked['avg_mi']:>6.3f}")
        if control.get('count', 0) > 0:
            output.append(f"  Control | {control['count']:>5} | {control['avg_entropy']:>11.3f} | {control['avg_mi']:>6.3f}")
        output.append("")
    
    # Recommendations
    recommendations = summary.get('recommendations', [])
    if recommendations:
        output.append("💡 RECOMMENDATIONS")
        for i, rec in enumerate(recommendations, 1):
            output.append(f"  {i}. {rec}")
        output.append("")
    
    # Session breakdown
    sessions = summary.get('session_breakdown', {})
    if sessions:
        output.append("📋 SESSION BREAKDOWN")
        output.append("  Session | Logs | Tokens | Spikes | Avg Entropy | Avg MI")
        output.append("  --------|------|--------|--------|-----------|---------")
        for session_id, stats in sessions.items():
            spikes_indicator = "Yes" if stats.get('has_spikes', False) else "No"
            output.append(f"  {session_id:<7} | {stats['log_count']:>4} | {stats['total_tokens']:>6} | {spikes_indicator:>6} | {stats['avg_entropy']:>11.3f} | {stats['avg_mi']:>7.3f}")
    
    return "\n".join(output)


if __name__ == "__main__":
    main()