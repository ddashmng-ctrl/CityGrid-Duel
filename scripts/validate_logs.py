#!/usr/bin/env python3
"""
Soul Debate Logs Validation Script

This script validates JSON files in the logs directory against the soul debate schema.
It loads the JSON schema and validates all JSON files, reporting any validation errors.
"""

import json
import os
import sys
import glob
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: jsonschema library is required. Install with: pip install jsonschema")
    sys.exit(1)


def load_schema(schema_path):
    """Load and return the JSON schema from the specified path."""
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        print(f"✓ Loaded schema from: {schema_path}")
        return schema
    except FileNotFoundError:
        print(f"Error: Schema file not found: {schema_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file {schema_path}: {e}")
        return None
    except Exception as e:
        print(f"Error: Failed to load schema from {schema_path}: {e}")
        return None


def find_json_files(logs_dir):
    """Find all JSON files in the logs directory."""
    pattern = os.path.join(logs_dir, "*.json")
    json_files = glob.glob(pattern)
    
    # Filter out the schema file itself
    schema_files = ['soul_debate_schema.json']
    json_files = [f for f in json_files if not any(schema in f for schema in schema_files)]
    
    return sorted(json_files)


def load_json_file(file_path):
    """Load and return JSON data from file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")


def validate_json_file(file_path, schema):
    """Validate a single JSON file against the schema."""
    try:
        # Load the JSON data
        data = load_json_file(file_path)
        
        # Validate against schema
        validate(instance=data, schema=schema)
        return True, None
        
    except ValidationError as e:
        # Format validation error message
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        error_msg = f"at '{error_path}': {e.message}"
        return False, error_msg
        
    except ValueError as e:
        return False, str(e)
        
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main():
    """Main function to validate all JSON files in the logs directory."""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    logs_dir = os.path.join(repo_root, "logs")
    
    # Try to find the schema file - prioritize the one mentioned in requirements
    schema_candidates = [
        os.path.join(logs_dir, "soul_debate_schema.json"),
        os.path.join(logs_dir, "soul_debate_schema_proper.json")
    ]
    
    schema_path = None
    for candidate in schema_candidates:
        if os.path.exists(candidate):
            schema_path = candidate
            break
    
    if not schema_path:
        print(f"Error: No schema file found in {logs_dir}")
        print("Expected files: soul_debate_schema.json or soul_debate_schema_proper.json")
        sys.exit(1)
    
    # Load schema
    schema = load_schema(schema_path)
    if schema is None:
        sys.exit(1)
    
    # Find JSON files to validate
    json_files = find_json_files(logs_dir)
    
    if not json_files:
        print(f"No JSON files found in {logs_dir} (excluding schema files)")
        return
    
    print(f"\nValidating {len(json_files)} JSON files against schema...")
    print("-" * 60)
    
    # Validate each file
    valid_files = []
    invalid_files = []
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        is_valid, error_msg = validate_json_file(file_path, schema)
        
        if is_valid:
            print(f"✓ {filename}")
            valid_files.append(filename)
        else:
            print(f"✗ {filename}")
            print(f"  Error: {error_msg}")
            invalid_files.append((filename, error_msg))
    
    # Summary
    print("-" * 60)
    print(f"Validation Summary:")
    print(f"  Valid files:   {len(valid_files)}")
    print(f"  Invalid files: {len(invalid_files)}")
    
    if invalid_files:
        print(f"\nInvalid files and their errors:")
        for filename, error in invalid_files:
            print(f"  • {filename}: {error}")
        sys.exit(1)
    else:
        print(f"\n🎉 All JSON files are valid!")


if __name__ == "__main__":
    main()