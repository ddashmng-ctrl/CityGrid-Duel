#!/usr/bin/env python3
"""
Log Summarization Script for Soul Debate Logs

This script summarizes soul debate log data by analyzing proto-awareness signals,
entropy measurements, and mutual information across sessions.
"""

import json
import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple


def load_log_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a single log file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return {}


def calculate_spike_metrics(spikes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary metrics for spikes."""
    if not spikes:
        return {
            "total_spikes": 0,
            "avg_intensity": 0.0,
            "max_intensity": 0.0,
            "unique_terms": 0,
            "terms": []
        }
    
    intensities = [spike["intensity"] for spike in spikes]
    terms = [spike["term"] for spike in spikes]
    unique_terms = list(set(terms))
    
    return {
        "total_spikes": len(spikes),
        "avg_intensity": sum(intensities) / len(intensities),
        "max_intensity": max(intensities),
        "unique_terms": len(unique_terms),
        "terms": unique_terms
    }


def summarize_session(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize a single session log."""
    if not log_data:
        return {}
    
    spike_metrics = calculate_spike_metrics(log_data.get("spikes", []))
    
    return {
        "session_id": log_data.get("session_id"),
        "timestamp": log_data.get("timestamp"),
        "model": log_data.get("model"),
        "seed": log_data.get("seed"),
        "tokens": log_data.get("tokens", 0),
        "violations": log_data.get("violations", 0),
        "entropy": log_data.get("entropy", 0.0),
        "mutual_information": log_data.get("mutual_information", 0.0),
        "spike_metrics": spike_metrics,
        "text_length": len(log_data.get("text", ""))
    }


def aggregate_summaries(summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate multiple session summaries."""
    if not summaries:
        return {"error": "No valid summaries to aggregate"}
    
    valid_summaries = [s for s in summaries if s]  # Filter out empty summaries
    
    if not valid_summaries:
        return {"error": "No valid summaries found"}
    
    total_sessions = len(valid_summaries)
    total_tokens = sum(s.get("tokens", 0) for s in valid_summaries)
    total_violations = sum(s.get("violations", 0) for s in valid_summaries)
    
    entropies = [s.get("entropy", 0) for s in valid_summaries if s.get("entropy")]
    mi_values = [s.get("mutual_information", 0) for s in valid_summaries if s.get("mutual_information")]
    
    # Aggregate spike data
    all_spikes = []
    for summary in valid_summaries:
        spike_metrics = summary.get("spike_metrics", {})
        if spike_metrics.get("total_spikes", 0) > 0:
            all_spikes.extend(spike_metrics.get("terms", []))
    
    unique_spike_terms = list(set(all_spikes))
    
    return {
        "summary_generated": datetime.now().isoformat() + "Z",
        "total_sessions": total_sessions,
        "total_tokens": total_tokens,
        "total_violations": total_violations,
        "avg_entropy": sum(entropies) / len(entropies) if entropies else 0.0,
        "max_entropy": max(entropies) if entropies else 0.0,
        "min_entropy": min(entropies) if entropies else 0.0,
        "avg_mutual_information": sum(mi_values) / len(mi_values) if mi_values else 0.0,
        "max_mutual_information": max(mi_values) if mi_values else 0.0,
        "min_mutual_information": min(mi_values) if mi_values else 0.0,
        "total_unique_spike_terms": len(unique_spike_terms),
        "spike_terms": unique_spike_terms,
        "sessions": valid_summaries
    }


def main():
    """Main function to process log files and generate summary."""
    parser = argparse.ArgumentParser(description="Summarize soul debate log data")
    parser.add_argument("--input", "-i", required=True, 
                       help="Path to log file or directory containing log files")
    parser.add_argument("--output", "-o", 
                       help="Output file path (default: print to stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json",
                       help="Output format (default: json)")
    
    args = parser.parse_args()
    
    # Collect log files
    log_files = []
    if os.path.isfile(args.input):
        log_files = [args.input]
    elif os.path.isdir(args.input):
        log_files = [
            os.path.join(args.input, f) 
            for f in os.listdir(args.input) 
            if f.endswith('.json') and not f.endswith('_schema.json')
        ]
    else:
        print(f"Error: {args.input} is not a valid file or directory", file=sys.stderr)
        sys.exit(1)
    
    if not log_files:
        print("Error: No log files found", file=sys.stderr)
        sys.exit(1)
    
    # Process each log file
    summaries = []
    for log_file in sorted(log_files):
        print(f"Processing {log_file}...", file=sys.stderr)
        log_data = load_log_file(log_file)
        summary = summarize_session(log_data)
        if summary:
            summaries.append(summary)
    
    # Generate final aggregated summary
    final_summary = aggregate_summaries(summaries)
    
    # Output results
    if args.format == "json":
        output_text = json.dumps(final_summary, indent=2)
    else:
        # Text format output
        output_lines = [
            f"Soul Debate Log Summary",
            f"Generated: {final_summary.get('summary_generated', 'Unknown')}",
            f"",
            f"Overview:",
            f"  Total Sessions: {final_summary.get('total_sessions', 0)}",
            f"  Total Tokens: {final_summary.get('total_tokens', 0)}",
            f"  Total Violations: {final_summary.get('total_violations', 0)}",
            f"",
            f"Proto-Awareness Metrics:",
            f"  Average Entropy: {final_summary.get('avg_entropy', 0):.4f}",
            f"  Entropy Range: {final_summary.get('min_entropy', 0):.4f} - {final_summary.get('max_entropy', 0):.4f}",
            f"  Average MI: {final_summary.get('avg_mutual_information', 0):.4f}",
            f"  MI Range: {final_summary.get('min_mutual_information', 0):.4f} - {final_summary.get('max_mutual_information', 0):.4f}",
            f"",
            f"Spike Analysis:",
            f"  Unique Spike Terms: {final_summary.get('total_unique_spike_terms', 0)}",
            f"  Terms: {', '.join(final_summary.get('spike_terms', []))}"
        ]
        output_text = "\n".join(output_lines)
    
    # Write or print output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"Summary written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()