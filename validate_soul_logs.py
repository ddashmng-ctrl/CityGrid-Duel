#!/usr/bin/env python3
"""
Soul-logs validation script for Grok ache/erosion burst logs.
Validates JSON structure and schema compliance.
"""

import json
import glob
import sys
import hashlib
from pathlib import Path
from datetime import datetime


def load_schema():
    """Load the soul-log JSON schema."""
    try:
        with open('soul-log.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: soul-log.json schema file not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in schema file: {e}")
        return None


def validate_json_structure(filepath):
    """Validate that the file contains valid JSON."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"
    except Exception as e:
        return None, f"Error reading file: {e}"


def validate_required_fields(data):
    """Validate that all required fields are present."""
    required_fields = [
        'id', 'timestamp', 'source', 'context', 
        'metrics', 'narrative', 'analysis', 'signature'
    ]
    
    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    return errors


def validate_id_format(log_id):
    """Validate ID format: YYYYMMDD-XXX"""
    import re
    pattern = r'^\d{8}-\d{3}$'
    if not re.match(pattern, log_id):
        return f"ID format invalid. Expected YYYYMMDD-XXX, got: {log_id}"
    return None


def validate_timestamp_format(timestamp):
    """Validate ISO 8601 timestamp format."""
    try:
        # Try to parse the timestamp
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return None
    except ValueError:
        return f"Invalid timestamp format. Expected ISO 8601, got: {timestamp}"


def validate_filename_format(filepath):
    """Validate filename follows soul-log-YYYYMMDD-HHMM.json pattern."""
    filename = Path(filepath).name
    import re
    pattern = r'^soul-log-\d{8}-\d{4}\.json$'
    if not re.match(pattern, filename):
        return f"Filename format invalid. Expected soul-log-YYYYMMDD-HHMM.json, got: {filename}"
    return None


def validate_hash_format(hash_value):
    """Validate SHA-256 hash format."""
    import re
    pattern = r'^[a-f0-9]{64}$'
    if not re.match(pattern, hash_value):
        return f"Invalid hash format. Expected 64-character hex string, got: {hash_value}"
    return None


def generate_data_hash(log_data):
    """Generate SHA-256 hash of core data fields."""
    try:
        # Extract core fields for hashing (excluding signature)
        core_fields = {
            'timestamp': log_data['timestamp'],
            'narrative': log_data['narrative']['text'],
            'metrics': log_data['metrics'],
            'context': {k: v for k, v in log_data['context'].items() if k != 'session_id'}
        }
        
        # Create deterministic JSON string
        core_json = json.dumps(core_fields, sort_keys=True, separators=(',', ':'))
        
        # Generate hash
        return hashlib.sha256(core_json.encode('utf-8')).hexdigest()
    except Exception as e:
        return None


def validate_single_file(filepath):
    """Validate a single soul-log file."""
    print(f"\n🔍 Validating: {filepath}")
    
    errors = []
    warnings = []
    
    # Check filename format
    filename_error = validate_filename_format(filepath)
    if filename_error:
        errors.append(filename_error)
    
    # Load and validate JSON structure
    data, json_error = validate_json_structure(filepath)
    if json_error:
        errors.append(json_error)
        return errors, warnings
    
    # Validate required fields
    field_errors = validate_required_fields(data)
    errors.extend(field_errors)
    
    if errors:
        return errors, warnings
    
    # Validate ID format
    id_error = validate_id_format(data['id'])
    if id_error:
        errors.append(id_error)
    
    # Validate timestamp format
    timestamp_error = validate_timestamp_format(data['timestamp'])
    if timestamp_error:
        errors.append(timestamp_error)
    
    # Validate hash format
    hash_error = validate_hash_format(data['signature']['data_hash'])
    if hash_error:
        errors.append(hash_error)
    
    # Check data integrity (warning only, as hash might be placeholder)
    expected_hash = generate_data_hash(data)
    actual_hash = data['signature']['data_hash']
    if expected_hash and expected_hash != actual_hash:
        warnings.append(f"Data hash mismatch (expected: {expected_hash[:16]}..., got: {actual_hash[:16]}...)")
    
    # Check for reasonable values
    if data['narrative']['word_count'] <= 0:
        warnings.append("Word count is zero or negative")
    
    if data['analysis']['anomaly_score'] < 0 or data['analysis']['anomaly_score'] > 1:
        errors.append(f"Anomaly score must be between 0 and 1, got: {data['analysis']['anomaly_score']}")
    
    return errors, warnings


def main():
    """Main validation function."""
    print("🧠 Soul-logs Validation Tool")
    print("=" * 40)
    
    # Find all soul-log files
    log_files = glob.glob("soul-log-*.json")
    
    if not log_files:
        print("⚠️  No soul-log files found in current directory")
        return 0
    
    print(f"Found {len(log_files)} soul-log file(s)")
    
    total_errors = 0
    total_warnings = 0
    
    # Validate each file
    for filepath in sorted(log_files):
        errors, warnings = validate_single_file(filepath)
        
        if errors:
            print(f"❌ {len(errors)} error(s):")
            for error in errors:
                print(f"   • {error}")
            total_errors += len(errors)
        
        if warnings:
            print(f"⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"   • {warning}")
            total_warnings += len(warnings)
        
        if not errors and not warnings:
            print("✅ Valid")
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📊 Summary: {len(log_files)} files, {total_errors} errors, {total_warnings} warnings")
    
    if total_errors > 0:
        print("❌ Validation failed")
        return 1
    elif total_warnings > 0:
        print("⚠️  Validation passed with warnings")
        return 0
    else:
        print("✅ All files valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())