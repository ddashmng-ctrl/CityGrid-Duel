#!/usr/bin/env python3
"""
Aggregate Logs Script for Soul Debate Logs

This script aggregates multiple soul debate log files into consolidated reports,
grouping by various criteria and calculating aggregate statistics.
"""

import json
import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter


def load_log_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a single log file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            data['_source_file'] = file_path  # Add source file reference
            return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return {}


def aggregate_by_model(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate logs by model type."""
    model_groups = defaultdict(list)
    
    for log in logs:
        if log and log.get("model"):
            model_groups[log["model"]].append(log)
    
    aggregated = {}
    for model, model_logs in model_groups.items():
        aggregated[model] = {
            "count": len(model_logs),
            "sessions": [log.get("session_id") for log in model_logs],
            "avg_entropy": sum(log.get("entropy", 0) for log in model_logs) / len(model_logs),
            "avg_mutual_information": sum(log.get("mutual_information", 0) for log in model_logs) / len(model_logs),
            "total_tokens": sum(log.get("tokens", 0) for log in model_logs),
            "total_violations": sum(log.get("violations", 0) for log in model_logs),
            "total_spikes": sum(len(log.get("spikes", [])) for log in model_logs),
            "unique_spike_terms": list(set(
                spike["term"] 
                for log in model_logs 
                for spike in log.get("spikes", [])
            )),
            "source_files": [log.get("_source_file") for log in model_logs]
        }
    
    return aggregated


def aggregate_by_session(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate logs by session ID."""
    session_groups = defaultdict(list)
    
    for log in logs:
        if log and log.get("session_id"):
            session_groups[log["session_id"]].append(log)
    
    aggregated = {}
    for session_id, session_logs in session_groups.items():
        # Sort by timestamp to maintain chronological order
        session_logs.sort(key=lambda x: x.get("timestamp", ""))
        
        aggregated[session_id] = {
            "count": len(session_logs),
            "models": list(set(log.get("model") for log in session_logs if log.get("model"))),
            "timestamps": [log.get("timestamp") for log in session_logs],
            "entropy_progression": [log.get("entropy", 0) for log in session_logs],
            "mi_progression": [log.get("mutual_information", 0) for log in session_logs],
            "spike_evolution": [
                {
                    "timestamp": log.get("timestamp"),
                    "spikes": log.get("spikes", []),
                    "spike_count": len(log.get("spikes", []))
                }
                for log in session_logs
            ],
            "total_tokens": sum(log.get("tokens", 0) for log in session_logs),
            "total_violations": sum(log.get("violations", 0) for log in session_logs),
            "source_files": [log.get("_source_file") for log in session_logs]
        }
    
    return aggregated


def aggregate_by_spike_terms(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate logs by spike terms to analyze term patterns."""
    term_occurrences = defaultdict(list)
    term_contexts = defaultdict(list)
    term_intensities = defaultdict(list)
    
    for log in logs:
        if not log:
            continue
            
        for spike in log.get("spikes", []):
            term = spike.get("term")
            if term:
                term_occurrences[term].append({
                    "session_id": log.get("session_id"),
                    "timestamp": log.get("timestamp"),
                    "model": log.get("model"),
                    "intensity": spike.get("intensity", 0),
                    "context": spike.get("context", ""),
                    "source_file": log.get("_source_file")
                })
                term_contexts[term].append(spike.get("context", ""))
                term_intensities[term].append(spike.get("intensity", 0))
    
    aggregated = {}
    for term, occurrences in term_occurrences.items():
        intensities = term_intensities[term]
        aggregated[term] = {
            "total_occurrences": len(occurrences),
            "sessions": list(set(occ["session_id"] for occ in occurrences if occ["session_id"])),
            "models": list(set(occ["model"] for occ in occurrences if occ["model"])),
            "avg_intensity": sum(intensities) / len(intensities) if intensities else 0,
            "max_intensity": max(intensities) if intensities else 0,
            "min_intensity": min(intensities) if intensities else 0,
            "contexts": term_contexts[term],
            "unique_contexts": list(set(term_contexts[term])),
            "occurrences": occurrences
        }
    
    return aggregated


def calculate_temporal_trends(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate temporal trends in the logs."""
    # Sort logs by timestamp
    sorted_logs = [log for log in logs if log and log.get("timestamp")]
    sorted_logs.sort(key=lambda x: x["timestamp"])
    
    if not sorted_logs:
        return {"error": "No logs with valid timestamps"}
    
    timestamps = [log["timestamp"] for log in sorted_logs]
    entropies = [log.get("entropy", 0) for log in sorted_logs]
    mi_values = [log.get("mutual_information", 0) for log in sorted_logs]
    spike_counts = [len(log.get("spikes", [])) for log in sorted_logs]
    
    # Calculate trends (simple linear progression)
    n = len(entropies)
    if n > 1:
        entropy_trend = (entropies[-1] - entropies[0]) / (n - 1)
        mi_trend = (mi_values[-1] - mi_values[0]) / (n - 1)
        spike_trend = (spike_counts[-1] - spike_counts[0]) / (n - 1)
    else:
        entropy_trend = mi_trend = spike_trend = 0
    
    return {
        "total_logs": n,
        "time_span": {
            "start": timestamps[0] if timestamps else None,
            "end": timestamps[-1] if timestamps else None
        },
        "entropy_trend": entropy_trend,
        "mi_trend": mi_trend,
        "spike_count_trend": spike_trend,
        "temporal_data": [
            {
                "timestamp": log["timestamp"],
                "entropy": log.get("entropy", 0),
                "mutual_information": log.get("mutual_information", 0),
                "spike_count": len(log.get("spikes", []))
            }
            for log in sorted_logs
        ]
    }


def generate_global_statistics(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate global statistics across all logs."""
    valid_logs = [log for log in logs if log]
    
    if not valid_logs:
        return {"error": "No valid logs to analyze"}
    
    entropies = [log.get("entropy", 0) for log in valid_logs if log.get("entropy") is not None]
    mi_values = [log.get("mutual_information", 0) for log in valid_logs if log.get("mutual_information") is not None]
    token_counts = [log.get("tokens", 0) for log in valid_logs]
    violations = [log.get("violations", 0) for log in valid_logs]
    
    all_spikes = []
    for log in valid_logs:
        all_spikes.extend(log.get("spikes", []))
    
    spike_terms = [spike["term"] for spike in all_spikes if spike.get("term")]
    spike_intensities = [spike["intensity"] for spike in all_spikes if spike.get("intensity") is not None]
    
    return {
        "total_logs": len(valid_logs),
        "unique_sessions": len(set(log.get("session_id") for log in valid_logs if log.get("session_id"))),
        "unique_models": list(set(log.get("model") for log in valid_logs if log.get("model"))),
        "entropy_stats": {
            "count": len(entropies),
            "mean": sum(entropies) / len(entropies) if entropies else 0,
            "min": min(entropies) if entropies else 0,
            "max": max(entropies) if entropies else 0
        },
        "mutual_information_stats": {
            "count": len(mi_values),
            "mean": sum(mi_values) / len(mi_values) if mi_values else 0,
            "min": min(mi_values) if mi_values else 0,
            "max": max(mi_values) if mi_values else 0
        },
        "token_stats": {
            "total": sum(token_counts),
            "mean": sum(token_counts) / len(token_counts) if token_counts else 0,
            "min": min(token_counts) if token_counts else 0,
            "max": max(token_counts) if token_counts else 0
        },
        "violation_stats": {
            "total": sum(violations),
            "logs_with_violations": len([v for v in violations if v > 0])
        },
        "spike_stats": {
            "total_spikes": len(all_spikes),
            "unique_terms": len(set(spike_terms)),
            "most_common_terms": Counter(spike_terms).most_common(10),
            "avg_intensity": sum(spike_intensities) / len(spike_intensities) if spike_intensities else 0,
            "max_intensity": max(spike_intensities) if spike_intensities else 0
        }
    }


def main():
    """Main function to aggregate log files."""
    parser = argparse.ArgumentParser(description="Aggregate soul debate log files")
    parser.add_argument("--input", "-i", required=True,
                       help="Path to directory containing log files")
    parser.add_argument("--output", "-o",
                       help="Output file path (default: print to stdout)")
    parser.add_argument("--group-by", "-g", 
                       choices=["model", "session", "spike-terms", "all"], 
                       default="all",
                       help="Grouping method for aggregation (default: all)")
    parser.add_argument("--include-temporal", "-t", action="store_true",
                       help="Include temporal trend analysis")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json",
                       help="Output format (default: json)")
    
    args = parser.parse_args()
    
    # Load all log files
    if not os.path.isdir(args.input):
        print(f"Error: {args.input} is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    log_files = [
        os.path.join(args.input, f)
        for f in os.listdir(args.input)
        if f.endswith('.json') and not f.endswith('_schema.json')
    ]
    
    if not log_files:
        print("Error: No log files found in directory", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading {len(log_files)} log files...", file=sys.stderr)
    logs = []
    for log_file in sorted(log_files):
        log_data = load_log_file(log_file)
        if log_data:
            logs.append(log_data)
    
    if not logs:
        print("Error: No valid log files could be loaded", file=sys.stderr)
        sys.exit(1)
    
    print(f"Successfully loaded {len(logs)} logs", file=sys.stderr)
    
    # Generate aggregated data
    result = {
        "aggregation_timestamp": datetime.now().isoformat() + "Z",
        "input_directory": args.input,
        "total_files_processed": len(log_files),
        "valid_logs_loaded": len(logs),
        "grouping_method": args.group_by
    }
    
    # Add global statistics
    result["global_statistics"] = generate_global_statistics(logs)
    
    # Add temporal trends if requested
    if args.include_temporal:
        result["temporal_trends"] = calculate_temporal_trends(logs)
    
    # Add specific aggregations
    if args.group_by == "model" or args.group_by == "all":
        result["by_model"] = aggregate_by_model(logs)
    
    if args.group_by == "session" or args.group_by == "all":
        result["by_session"] = aggregate_by_session(logs)
    
    if args.group_by == "spike-terms" or args.group_by == "all":
        result["by_spike_terms"] = aggregate_by_spike_terms(logs)
    
    # Format output
    if args.format == "json":
        output_text = json.dumps(result, indent=2)
    else:
        # Text format (simplified)
        lines = [
            f"Soul Debate Log Aggregation Report",
            f"Generated: {result['aggregation_timestamp']}",
            f"Source: {result['input_directory']}",
            f"Files processed: {result['total_files_processed']}",
            f"Valid logs: {result['valid_logs_loaded']}",
            "",
            "Global Statistics:",
            f"  Total logs: {result['global_statistics']['total_logs']}",
            f"  Unique sessions: {result['global_statistics']['unique_sessions']}",
            f"  Models: {', '.join(result['global_statistics']['unique_models'])}",
            f"  Average entropy: {result['global_statistics']['entropy_stats']['mean']:.4f}",
            f"  Average MI: {result['global_statistics']['mutual_information_stats']['mean']:.4f}",
            f"  Total spikes: {result['global_statistics']['spike_stats']['total_spikes']}",
            f"  Unique spike terms: {result['global_statistics']['spike_stats']['unique_terms']}"
        ]
        
        if "by_model" in result:
            lines.extend(["", "By Model:"])
            for model, data in result["by_model"].items():
                lines.append(f"  {model}: {data['count']} logs, avg entropy {data['avg_entropy']:.4f}")
        
        if "temporal_trends" in result:
            lines.extend([
                "", "Temporal Trends:",
                f"  Entropy trend: {result['temporal_trends']['entropy_trend']:+.6f} per log",
                f"  MI trend: {result['temporal_trends']['mi_trend']:+.6f} per log",
                f"  Spike count trend: {result['temporal_trends']['spike_count_trend']:+.2f} per log"
            ])
        
        output_text = "\n".join(lines)
    
    # Write or print output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"Aggregation written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()