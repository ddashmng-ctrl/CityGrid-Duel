#!/usr/bin/env python3
"""
Validate soul debate JSON logs using formal JSON Schema validation.
Uses jsonschema library for comprehensive validation.
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


def validate_with_jsonschema():
    """Validate using jsonschema library if available."""
    if not JSONSCHEMA_AVAILABLE:
        print("jsonschema library not available. Install with: pip install jsonschema")
        return False
    
    # Load formal schema
    schema_path = Path("logs/soul_debate_schema_formal.json")
    if not schema_path.exists():
        print(f"Formal schema file not found: {schema_path}")
        return False
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Files to validate
    files_to_validate = [
        "logs/example_soul_debate.json",
        "logs/example_soul_debate_2.json", 
        "logs/example_soul_debate_control.json"
    ]
    
    all_valid = True
    
    print("JSON Schema Validation Results")
    print("=" * 40)
    
    for filepath in files_to_validate:
        filename = Path(filepath).name
        print(f"\nValidating {filename}:")
        
        if not Path(filepath).exists():
            print(f"  ❌ File not found: {filepath}")
            all_valid = False
            continue
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            validate(instance=data, schema=schema)
            print(f"  ✅ Valid according to JSON Schema")
            
        except ValidationError as e:
            print(f"  ❌ Schema validation error:")
            print(f"     {e.message}")
            if e.absolute_path:
                print(f"     Path: {' -> '.join(map(str, e.absolute_path))}")
            all_valid = False
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}")
            all_valid = False
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_valid = False
    
    return all_valid


def basic_validation():
    """Basic validation without external dependencies."""
    print("Basic Structure Validation")
    print("=" * 40)
    
    # Load reference schema
    with open('logs/soul_debate_schema.json', 'r') as f:
        reference = json.load(f)
    
    required_fields = list(reference.keys())
    files_to_validate = [
        "logs/example_soul_debate.json",
        "logs/example_soul_debate_2.json", 
        "logs/example_soul_debate_control.json"
    ]
    
    all_valid = True
    
    for filepath in files_to_validate:
        filename = Path(filepath).name
        print(f"\nValidating {filename}:")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            missing_fields = set(required_fields) - set(data.keys())
            if missing_fields:
                print(f"  ❌ Missing fields: {missing_fields}")
                all_valid = False
            else:
                print(f"  ✅ All required fields present")
            
            # Check field types
            type_errors = []
            for field in required_fields:
                if field in data:
                    ref_type = type(reference[field])
                    data_type = type(data[field])
                    if ref_type != data_type:
                        type_errors.append(f"{field}: expected {ref_type.__name__}, got {data_type.__name__}")
            
            if type_errors:
                print(f"  ❌ Type errors: {type_errors}")
                all_valid = False
            else:
                print(f"  ✅ All field types correct")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_valid = False
    
    return all_valid


def main():
    """Main validation function."""
    print("Soul Debate JSON Validation Suite")
    print("=" * 50)
    
    # Try JSON Schema validation first
    if JSONSCHEMA_AVAILABLE:
        schema_valid = validate_with_jsonschema()
        print(f"\nJSON Schema validation: {'PASSED' if schema_valid else 'FAILED'}")
    else:
        print("\nJSON Schema library not available, using basic validation...")
        schema_valid = basic_validation()
        print(f"\nBasic validation: {'PASSED' if schema_valid else 'FAILED'}")
    
    if schema_valid:
        print("\n🎉 All soul debate JSON files are valid!")
        return 0
    else:
        print("\n❌ Some files failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())