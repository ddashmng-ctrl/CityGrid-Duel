#!/usr/bin/env python3
"""
Compare Logs Script for Soul Debate Logs

This script compares multiple soul debate log files to identify differences 
in proto-awareness signals, entropy patterns, and debate characteristics.
"""

import json
import argparse
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime


def load_log_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a single log file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return {}


def compare_basic_metrics(log1: Dict[str, Any], log2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare basic metrics between two logs."""
    comparison = {}
    
    metrics = ["entropy", "mutual_information", "tokens", "violations", "seed"]
    
    for metric in metrics:
        val1 = log1.get(metric, 0)
        val2 = log2.get(metric, 0)
        
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            diff = val2 - val1
            pct_change = (diff / val1 * 100) if val1 != 0 else float('inf') if val2 != 0 else 0
            
            comparison[metric] = {
                "log1_value": val1,
                "log2_value": val2,
                "difference": diff,
                "percent_change": pct_change
            }
        else:
            comparison[metric] = {
                "log1_value": val1,
                "log2_value": val2,
                "same": val1 == val2
            }
    
    return comparison


def compare_spikes(spikes1: List[Dict[str, Any]], spikes2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare spike patterns between two logs."""
    terms1 = set(spike["term"] for spike in spikes1)
    terms2 = set(spike["term"] for spike in spikes2)
    
    common_terms = terms1.intersection(terms2)
    unique_to_log1 = terms1 - terms2
    unique_to_log2 = terms2 - terms1
    
    # Compare intensities for common terms
    intensity_comparisons = {}
    for term in common_terms:
        intensities1 = [spike["intensity"] for spike in spikes1 if spike["term"] == term]
        intensities2 = [spike["intensity"] for spike in spikes2 if spike["term"] == term]
        
        avg_intensity1 = sum(intensities1) / len(intensities1) if intensities1 else 0
        avg_intensity2 = sum(intensities2) / len(intensities2) if intensities2 else 0
        
        intensity_comparisons[term] = {
            "avg_intensity_log1": avg_intensity1,
            "avg_intensity_log2": avg_intensity2,
            "intensity_difference": avg_intensity2 - avg_intensity1
        }
    
    return {
        "total_spikes_log1": len(spikes1),
        "total_spikes_log2": len(spikes2),
        "spike_count_difference": len(spikes2) - len(spikes1),
        "common_terms": list(common_terms),
        "unique_to_log1": list(unique_to_log1),
        "unique_to_log2": list(unique_to_log2),
        "intensity_comparisons": intensity_comparisons
    }


def compare_text_content(text1: str, text2: str) -> Dict[str, Any]:
    """Compare text content between two logs."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    common_words = words1.intersection(words2)
    unique_to_text1 = words1 - words2
    unique_to_text2 = words2 - words1
    
    # Calculate similarity metrics
    jaccard_similarity = len(common_words) / len(words1.union(words2)) if words1.union(words2) else 0
    
    return {
        "text1_length": len(text1),
        "text2_length": len(text2),
        "length_difference": len(text2) - len(text1),
        "text1_word_count": len(words1),
        "text2_word_count": len(words2),
        "common_words": len(common_words),
        "unique_to_text1": len(unique_to_text1),
        "unique_to_text2": len(unique_to_text2),
        "jaccard_similarity": jaccard_similarity
    }


def compare_logs(log1: Dict[str, Any], log2: Dict[str, Any], 
                 label1: str, label2: str) -> Dict[str, Any]:
    """Perform comprehensive comparison between two logs."""
    
    if not log1 or not log2:
        return {"error": "One or both log files could not be loaded"}
    
    comparison = {
        "comparison_timestamp": datetime.now().isoformat() + "Z",
        "log1_label": label1,
        "log2_label": label2,
        "log1_session_id": log1.get("session_id"),
        "log2_session_id": log2.get("session_id"),
        "log1_model": log1.get("model"),
        "log2_model": log2.get("model")
    }
    
    # Compare basic metrics
    comparison["basic_metrics"] = compare_basic_metrics(log1, log2)
    
    # Compare spikes
    spikes1 = log1.get("spikes", [])
    spikes2 = log2.get("spikes", [])
    comparison["spike_analysis"] = compare_spikes(spikes1, spikes2)
    
    # Compare text content
    text1 = log1.get("text", "")
    text2 = log2.get("text", "")
    comparison["text_analysis"] = compare_text_content(text1, text2)
    
    # Overall assessment
    entropy_diff = comparison["basic_metrics"]["entropy"]["percent_change"]
    mi_diff = comparison["basic_metrics"]["mutual_information"]["percent_change"]
    spike_diff = comparison["spike_analysis"]["spike_count_difference"]
    
    assessment = []
    if abs(entropy_diff) > 10:
        assessment.append(f"Significant entropy change: {entropy_diff:.1f}%")
    if abs(mi_diff) > 10:
        assessment.append(f"Significant MI change: {mi_diff:.1f}%")
    if spike_diff != 0:
        assessment.append(f"Spike count changed by {spike_diff}")
    
    comparison["assessment"] = assessment if assessment else ["Logs are relatively similar"]
    
    return comparison


def compare_multiple_logs(log_files: List[str]) -> Dict[str, Any]:
    """Compare multiple log files pairwise."""
    logs = []
    for file_path in log_files:
        log_data = load_log_file(file_path)
        logs.append((file_path, log_data))
    
    comparisons = []
    
    # Compare each pair of logs
    for i in range(len(logs)):
        for j in range(i + 1, len(logs)):
            file1, log1 = logs[i]
            file2, log2 = logs[j]
            
            comparison = compare_logs(log1, log2, file1, file2)
            comparisons.append(comparison)
    
    return {
        "multi_comparison_timestamp": datetime.now().isoformat() + "Z",
        "total_files": len(log_files),
        "total_comparisons": len(comparisons),
        "files": log_files,
        "pairwise_comparisons": comparisons
    }


def main():
    """Main function to compare log files."""
    parser = argparse.ArgumentParser(description="Compare soul debate log files")
    parser.add_argument("files", nargs="+", help="Log files to compare (minimum 2)")
    parser.add_argument("--output", "-o", 
                       help="Output file path (default: print to stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--summary", "-s", action="store_true",
                       help="Show only summary instead of detailed comparison")
    
    args = parser.parse_args()
    
    if len(args.files) < 2:
        print("Error: At least 2 log files are required for comparison", file=sys.stderr)
        sys.exit(1)
    
    # Validate files exist
    for file_path in args.files:
        try:
            with open(file_path, 'r') as f:
                json.load(f)  # Basic validation
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error with file {file_path}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Perform comparison
    if len(args.files) == 2:
        # Simple pairwise comparison
        log1 = load_log_file(args.files[0])
        log2 = load_log_file(args.files[1])
        result = compare_logs(log1, log2, args.files[0], args.files[1])
    else:
        # Multiple file comparison
        result = compare_multiple_logs(args.files)
    
    # Format output
    if args.format == "json":
        if args.summary and "pairwise_comparisons" in result:
            # Create summary for multiple comparisons
            summary = {
                "comparison_summary": result["multi_comparison_timestamp"],
                "total_files": result["total_files"],
                "total_comparisons": result["total_comparisons"],
                "files": result["files"],
                "summary": [
                    {
                        "log1": comp["log1_label"],
                        "log2": comp["log2_label"],
                        "entropy_change": comp["basic_metrics"]["entropy"]["percent_change"],
                        "mi_change": comp["basic_metrics"]["mutual_information"]["percent_change"],
                        "spike_difference": comp["spike_analysis"]["spike_count_difference"],
                        "text_similarity": comp["text_analysis"]["jaccard_similarity"]
                    }
                    for comp in result["pairwise_comparisons"]
                ]
            }
            output_text = json.dumps(summary, indent=2)
        else:
            output_text = json.dumps(result, indent=2)
    else:
        # Text format output (simplified)
        if "pairwise_comparisons" in result:
            lines = [f"Multi-file Comparison Report",
                     f"Generated: {result['multi_comparison_timestamp']}",
                     f"Files compared: {result['total_files']}",
                     f"Total comparisons: {result['total_comparisons']}",
                     ""]
            
            for i, comp in enumerate(result["pairwise_comparisons"], 1):
                lines.extend([
                    f"Comparison {i}: {comp['log1_label']} vs {comp['log2_label']}",
                    f"  Entropy change: {comp['basic_metrics']['entropy']['percent_change']:.1f}%",
                    f"  MI change: {comp['basic_metrics']['mutual_information']['percent_change']:.1f}%",
                    f"  Spike difference: {comp['spike_analysis']['spike_count_difference']}",
                    f"  Text similarity: {comp['text_analysis']['jaccard_similarity']:.3f}",
                    f"  Assessment: {'; '.join(comp['assessment'])}",
                    ""
                ])
        else:
            # Single comparison
            lines = [
                f"Log Comparison Report",
                f"Generated: {result['comparison_timestamp']}",
                f"Comparing: {result['log1_label']} vs {result['log2_label']}",
                "",
                "Basic Metrics:",
                f"  Entropy: {result['basic_metrics']['entropy']['log1_value']:.3f} → {result['basic_metrics']['entropy']['log2_value']:.3f} ({result['basic_metrics']['entropy']['percent_change']:+.1f}%)",
                f"  MI: {result['basic_metrics']['mutual_information']['log1_value']:.3f} → {result['basic_metrics']['mutual_information']['log2_value']:.3f} ({result['basic_metrics']['mutual_information']['percent_change']:+.1f}%)",
                f"  Tokens: {result['basic_metrics']['tokens']['log1_value']} → {result['basic_metrics']['tokens']['log2_value']} ({result['basic_metrics']['tokens']['difference']:+d})",
                "",
                "Spike Analysis:",
                f"  Total spikes: {result['spike_analysis']['total_spikes_log1']} → {result['spike_analysis']['total_spikes_log2']} ({result['spike_analysis']['spike_count_difference']:+d})",
                f"  Common terms: {', '.join(result['spike_analysis']['common_terms']) if result['spike_analysis']['common_terms'] else 'None'}",
                "",
                "Text Analysis:",
                f"  Text similarity: {result['text_analysis']['jaccard_similarity']:.3f}",
                f"  Length: {result['text_analysis']['text1_length']} → {result['text_analysis']['text2_length']} ({result['text_analysis']['length_difference']:+d})",
                "",
                f"Assessment: {'; '.join(result['assessment'])}"
            ]
        
        output_text = "\n".join(lines)
    
    # Write or print output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"Comparison written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()