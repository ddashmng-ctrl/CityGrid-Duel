#!/usr/bin/env python3
"""
Validate soul debate JSON logs against the schema structure.
Ensures all required fields are present with correct data types.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def validate_spike_structure(spike: Any) -> List[str]:
    """Validate individual spike object structure."""
    errors = []
    
    if not isinstance(spike, dict):
        errors.append("Spike must be a dictionary")
        return errors
    
    # Required spike fields
    required_spike_fields = {
        'term': str,
        'intensity': (int, float),
        'context': str
    }
    
    for field, expected_type in required_spike_fields.items():
        if field not in spike:
            errors.append(f"Missing required spike field: {field}")
        elif not isinstance(spike[field], expected_type):
            errors.append(f"Spike field '{field}' must be {expected_type}, got {type(spike[field])}")
    
    # Validate intensity range (0.0 to 1.0)
    if 'intensity' in spike and isinstance(spike['intensity'], (int, float)):
        if not (0.0 <= spike['intensity'] <= 1.0):
            errors.append(f"Spike intensity must be between 0.0 and 1.0, got {spike['intensity']}")
    
    return errors


def validate_json_structure(data: Dict[str, Any], filename: str) -> List[str]:
    """Validate JSON data against the soul debate schema structure."""
    errors = []
    
    # Define expected schema structure
    required_fields = {
        'timestamp': str,
        'session_id': str,
        'branch': str,
        'model': str,
        'seed': int,
        'violations': int,
        'tokens': int,
        'spikes': list,
        'entropy': (int, float),
        'mutual_information': (int, float),
        'text': str
    }
    
    # Check for required fields and types
    for field, expected_type in required_fields.items():
        if field not in data:
            errors.append(f"{filename}: Missing required field '{field}'")
        elif not isinstance(data[field], expected_type):
            errors.append(f"{filename}: Field '{field}' must be {expected_type}, got {type(data[field])}")
    
    # Validate spikes array structure
    if 'spikes' in data and isinstance(data['spikes'], list):
        for i, spike in enumerate(data['spikes']):
            spike_errors = validate_spike_structure(spike)
            for error in spike_errors:
                errors.append(f"{filename}: Spike {i}: {error}")
    
    # Validate timestamp format (basic ISO 8601 check)
    if 'timestamp' in data and isinstance(data['timestamp'], str):
        if not data['timestamp'].endswith('Z') or 'T' not in data['timestamp']:
            errors.append(f"{filename}: Timestamp should be in ISO 8601 format with 'Z' suffix")
    
    # Validate numeric ranges
    if 'violations' in data and isinstance(data['violations'], int):
        if data['violations'] < 0:
            errors.append(f"{filename}: Violations count cannot be negative")
    
    if 'tokens' in data and isinstance(data['tokens'], int):
        if data['tokens'] < 0:
            errors.append(f"{filename}: Tokens count cannot be negative")
    
    if 'seed' in data and isinstance(data['seed'], int):
        if data['seed'] < 0:
            errors.append(f"{filename}: Seed cannot be negative")
    
    # Validate entropy and mutual_information ranges (should be non-negative)
    if 'entropy' in data and isinstance(data['entropy'], (int, float)):
        if data['entropy'] < 0:
            errors.append(f"{filename}: Entropy cannot be negative")
    
    if 'mutual_information' in data and isinstance(data['mutual_information'], (int, float)):
        if data['mutual_information'] < 0:
            errors.append(f"{filename}: Mutual information cannot be negative")
    
    return errors


def validate_files() -> Tuple[List[str], List[str]]:
    """Validate all soul debate JSON files against the schema."""
    logs_dir = Path("logs")
    
    # Files to validate
    files_to_validate = [
        "example_soul_debate.json",
        "example_soul_debate_2.json", 
        "example_soul_debate_control.json"
    ]
    
    all_errors = []
    validated_files = []
    
    for filename in files_to_validate:
        filepath = logs_dir / filename
        
        if not filepath.exists():
            all_errors.append(f"File not found: {filepath}")
            continue
        
        try:
            data = load_json_file(str(filepath))
            errors = validate_json_structure(data, filename)
            all_errors.extend(errors)
            validated_files.append(filename)
            
        except json.JSONDecodeError as e:
            all_errors.append(f"{filename}: Invalid JSON format - {e}")
        except Exception as e:
            all_errors.append(f"{filename}: Error reading file - {e}")
    
    return all_errors, validated_files


def main():
    """Main validation function."""
    print("Soul Debate JSON Schema Validation")
    print("=" * 40)
    
    errors, validated_files = validate_files()
    
    if not errors:
        print("✅ All files pass validation!")
        print(f"Validated files: {', '.join(validated_files)}")
        return 0
    else:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1


if __name__ == "__main__":
    exit(main())