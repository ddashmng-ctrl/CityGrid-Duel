#!/usr/bin/env python3
"""
Validate all JSON files in the logs/ directory against the soul_debate_schema.json schema.
"""

import json
import os
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError


def load_json_file(file_path):
    """Load a JSON file with error handling for invalid JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None


def validate_json_against_schema(json_data, schema, file_path):
    """Validate JSON data against the provided schema."""
    try:
        validate(instance=json_data, schema=schema)
        print(f"✅ {file_path}: Valid")
        return True
    except ValidationError as e:
        print(f"❌ {file_path}: Validation failed")
        print(f"   Error: {e.message}")
        if e.absolute_path:
            print(f"   Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False
    except Exception as e:
        print(f"❌ {file_path}: Unexpected validation error: {e}")
        return False


def main():
    """Main validation function."""
    # Get the repository root directory
    repo_root = Path(__file__).parent.parent.parent
    logs_dir = repo_root / "logs"
    schema_path = logs_dir / "soul_debate_schema.json"
    
    print("🔍 Starting log validation...")
    print(f"Repository root: {repo_root}")
    print(f"Logs directory: {logs_dir}")
    print(f"Schema file: {schema_path}")
    
    # Check if logs directory exists
    if not logs_dir.exists():
        print(f"❌ Logs directory not found: {logs_dir}")
        sys.exit(1)
    
    # Load the schema
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    
    schema = load_json_file(schema_path)
    if schema is None:
        print("❌ Failed to load schema file")
        sys.exit(1)
    
    # Validate the schema itself
    try:
        from jsonschema import Draft7Validator
        Draft7Validator.check_schema(schema)
        print("✅ Schema file is valid")
    except SchemaError as e:
        print(f"❌ Schema file is invalid: {e}")
        sys.exit(1)
    
    # Find all JSON files in logs directory (excluding the schema file)
    json_files = [
        f for f in logs_dir.glob("*.json") 
        if f.name != "soul_debate_schema.json"
    ]
    
    if not json_files:
        print("ℹ️  No JSON log files found to validate")
        sys.exit(0)
    
    print(f"\n📋 Found {len(json_files)} JSON file(s) to validate:")
    for file_path in json_files:
        print(f"   - {file_path.name}")
    
    # Validate each JSON file
    print(f"\n🔬 Validating files...")
    valid_count = 0
    invalid_count = 0
    
    for file_path in sorted(json_files):
        print(f"\nValidating {file_path.name}...")
        
        # Load JSON file
        json_data = load_json_file(file_path)
        if json_data is None:
            invalid_count += 1
            continue
        
        # Validate against schema
        if validate_json_against_schema(json_data, schema, file_path.name):
            valid_count += 1
        else:
            invalid_count += 1
    
    # Summary
    print(f"\n📊 Validation Summary:")
    print(f"   ✅ Valid files: {valid_count}")
    print(f"   ❌ Invalid files: {invalid_count}")
    print(f"   📁 Total files: {valid_count + invalid_count}")
    
    if invalid_count > 0:
        print(f"\n❌ Validation failed: {invalid_count} file(s) have errors")
        sys.exit(1)
    else:
        print(f"\n✅ All files passed validation!")
        sys.exit(0)


if __name__ == "__main__":
    main()