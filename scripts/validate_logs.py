#!/usr/bin/env python3
"""
Script to validate JSON log files against the soul_debate_schema.json schema.
"""

import json
import jsonschema
import sys
import glob
from pathlib import Path

def validate_file(file_path, schema):
    """Validate a single JSON file against the schema."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        jsonschema.validate(data, schema)
        print(f"✅ {file_path} is valid")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ {file_path} validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to validate all JSON files in logs/ directory."""
    # Load schema
    schema_path = "logs/soul_debate_schema.json"
    if not Path(schema_path).exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Find all JSON files in logs/ directory (except schema)
    json_files = glob.glob("logs/*.json")
    json_files = [f for f in json_files if not f.endswith("soul_debate_schema.json")]
    
    if not json_files:
        print("No JSON files found to validate")
        return
    
    print(f"Validating {len(json_files)} JSON files...")
    
    all_valid = True
    for file_path in json_files:
        if not validate_file(file_path, schema):
            all_valid = False
    
    if all_valid:
        print(f"\n✅ All {len(json_files)} files validated successfully!")
    else:
        print(f"\n❌ Some files failed validation")
        sys.exit(1)

if __name__ == "__main__":
    main()