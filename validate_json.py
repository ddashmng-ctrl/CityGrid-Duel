#!/usr/bin/env python3
"""
Validate JSON files against the soul_debate_schema.json schema.
"""

import json
import glob
import os
import sys


def load_schema(schema_path):
    """Load the JSON schema."""
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file {schema_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing schema file: {e}")
        return None


def validate_structure(data, schema_example):
    """Validate JSON structure against the schema example."""
    errors = []
    
    # Check required fields based on the example structure
    required_fields = {
        "timestamp": str,
        "session_id": str,
        "branch": str,
        "model": str,
        "seed": int,
        "violations": int,
        "tokens": int,
        "spikes": list,
        "entropy": (int, float),
        "mutual_information": (int, float),
        "text": str
    }
    
    for field, expected_type in required_fields.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], expected_type):
            errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
    
    # Validate spikes structure
    if "spikes" in data and isinstance(data["spikes"], list):
        for i, spike in enumerate(data["spikes"]):
            if not isinstance(spike, dict):
                errors.append(f"Spike {i} should be an object")
                continue
            
            spike_fields = {"term": str, "intensity": (int, float), "context": str}
            for spike_field, spike_type in spike_fields.items():
                if spike_field not in spike:
                    errors.append(f"Spike {i} missing field: {spike_field}")
                elif not isinstance(spike[spike_field], spike_type):
                    errors.append(f"Spike {i} field '{spike_field}' should be {spike_type.__name__}")
    
    # Validate value ranges
    if "entropy" in data and isinstance(data["entropy"], (int, float)):
        if data["entropy"] < 0:
            errors.append("Entropy should be non-negative")
    
    if "mutual_information" in data and isinstance(data["mutual_information"], (int, float)):
        if data["mutual_information"] < 0:
            errors.append("Mutual information should be non-negative")
    
    if "violations" in data and isinstance(data["violations"], int):
        if data["violations"] < 0:
            errors.append("Violations should be non-negative")
    
    if "tokens" in data and isinstance(data["tokens"], int):
        if data["tokens"] <= 0:
            errors.append("Tokens should be positive")
    
    return errors


def validate_json_files(logs_dir, schema_path):
    """Validate all JSON files in the logs directory."""
    schema = load_schema(schema_path)
    if not schema:
        return False
    
    # Find all JSON files (excluding schema)
    json_files = glob.glob(os.path.join(logs_dir, "*.json"))
    json_files = [f for f in json_files if not f.endswith("schema.json")]
    
    if not json_files:
        print(f"No JSON files found in {logs_dir}")
        return True
    
    all_valid = True
    total_files = len(json_files)
    valid_files = 0
    
    print(f"Validating {total_files} JSON files against schema...")
    
    for json_file in sorted(json_files):
        filename = os.path.basename(json_file)
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            errors = validate_structure(data, schema)
            
            if errors:
                print(f"❌ {filename}: INVALID")
                for error in errors:
                    print(f"   - {error}")
                all_valid = False
            else:
                print(f"✅ {filename}: VALID")
                valid_files += 1
                
        except json.JSONDecodeError as e:
            print(f"❌ {filename}: JSON PARSE ERROR - {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {filename}: ERROR - {e}")
            all_valid = False
    
    print(f"\nValidation Summary: {valid_files}/{total_files} files valid")
    
    return all_valid


if __name__ == "__main__":
    logs_dir = "logs"
    schema_path = "logs/soul_debate_schema.json"
    
    success = validate_json_files(logs_dir, schema_path)
    sys.exit(0 if success else 1)