#!/usr/bin/env python3
"""
Generate a comprehensive validation report for soul debate JSON files.
"""

import json
import datetime
from pathlib import Path


def generate_validation_report():
    """Generate a detailed validation report."""
    
    report = {
        "validation_timestamp": datetime.datetime.now().isoformat(),
        "schema_file": "logs/soul_debate_schema.json",
        "formal_schema_file": "logs/soul_debate_schema_formal.json",
        "validated_files": [],
        "validation_summary": {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0
        }
    }
    
    # Files to validate
    files_to_validate = [
        "example_soul_debate.json",
        "example_soul_debate_2.json", 
        "example_soul_debate_control.json"
    ]
    
    # Load reference schema
    with open('logs/soul_debate_schema.json', 'r') as f:
        reference_schema = json.load(f)
    
    required_fields = list(reference_schema.keys())
    
    for filename in files_to_validate:
        filepath = Path(f"logs/{filename}")
        file_report = {
            "filename": filename,
            "exists": filepath.exists(),
            "valid": False,
            "errors": [],
            "structure_analysis": {}
        }
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Check required fields
                missing_fields = set(required_fields) - set(data.keys())
                extra_fields = set(data.keys()) - set(required_fields)
                
                file_report["structure_analysis"] = {
                    "total_fields": len(data.keys()),
                    "required_fields_present": len(required_fields) - len(missing_fields),
                    "missing_fields": list(missing_fields),
                    "extra_fields": list(extra_fields),
                    "field_types_correct": True,
                    "spike_count": len(data.get('spikes', [])),
                    "spike_analysis": []
                }
                
                # Check field types
                type_errors = []
                for field in required_fields:
                    if field in data:
                        ref_type = type(reference_schema[field])
                        data_type = type(data[field])
                        if ref_type != data_type:
                            type_errors.append(f"{field}: expected {ref_type.__name__}, got {data_type.__name__}")
                            file_report["structure_analysis"]["field_types_correct"] = False
                
                if type_errors:
                    file_report["errors"].extend(type_errors)
                
                if missing_fields:
                    file_report["errors"].extend([f"Missing field: {field}" for field in missing_fields])
                
                # Analyze spikes
                for i, spike in enumerate(data.get('spikes', [])):
                    spike_analysis = {
                        "spike_index": i,
                        "has_required_fields": all(field in spike for field in ['term', 'intensity', 'context']),
                        "intensity_in_range": False
                    }
                    
                    if 'intensity' in spike and isinstance(spike['intensity'], (int, float)):
                        spike_analysis["intensity_in_range"] = 0.0 <= spike['intensity'] <= 1.0
                    
                    file_report["structure_analysis"]["spike_analysis"].append(spike_analysis)
                
                # Overall validation
                file_report["valid"] = (
                    len(missing_fields) == 0 and 
                    len(type_errors) == 0 and
                    all(spike["has_required_fields"] and spike["intensity_in_range"] 
                        for spike in file_report["structure_analysis"]["spike_analysis"])
                )
                
            except json.JSONDecodeError as e:
                file_report["errors"].append(f"Invalid JSON: {e}")
            except Exception as e:
                file_report["errors"].append(f"Error: {e}")
        else:
            file_report["errors"].append("File not found")
        
        report["validated_files"].append(file_report)
        report["validation_summary"]["total_files"] += 1
        if file_report["valid"]:
            report["validation_summary"]["valid_files"] += 1
        else:
            report["validation_summary"]["invalid_files"] += 1
    
    return report


def print_report(report):
    """Print a human-readable validation report."""
    print("Soul Debate JSON Validation Report")
    print("=" * 50)
    print(f"Generated: {report['validation_timestamp']}")
    print(f"Schema: {report['schema_file']}")
    print()
    
    summary = report['validation_summary']
    print(f"Summary: {summary['valid_files']}/{summary['total_files']} files valid")
    print()
    
    for file_report in report['validated_files']:
        status = "✅ VALID" if file_report['valid'] else "❌ INVALID"
        print(f"{status} - {file_report['filename']}")
        
        if not file_report['exists']:
            print("  File not found")
            continue
        
        structure = file_report['structure_analysis']
        print(f"  Fields: {structure['required_fields_present']}/{len(structure['missing_fields']) + structure['required_fields_present']} required fields present")
        
        if structure['missing_fields']:
            print(f"  Missing: {', '.join(structure['missing_fields'])}")
        
        if structure['extra_fields']:
            print(f"  Extra: {', '.join(structure['extra_fields'])}")
        
        print(f"  Spikes: {structure['spike_count']} detected")
        
        if file_report['errors']:
            print(f"  Errors: {'; '.join(file_report['errors'])}")
        
        print()


def main():
    """Main function."""
    report = generate_validation_report()
    print_report(report)
    
    # Save report to file
    with open('logs/validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to: logs/validation_report.json")
    
    return 0 if report['validation_summary']['invalid_files'] == 0 else 1


if __name__ == "__main__":
    exit(main())