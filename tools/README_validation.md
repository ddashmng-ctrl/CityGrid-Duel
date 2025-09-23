# Soul Debate JSON Validation Tools

This directory contains tools for validating soul debate JSON log files against the required schema format.

## Files

- `validate_soul_debate_logs.py` - Basic validation script that checks field presence and types
- `validate_with_schema.py` - Advanced validation using formal JSON Schema
- `generate_validation_report.py` - Generates comprehensive validation reports

## Schema Files

- `logs/soul_debate_schema.json` - Reference example showing the expected format
- `logs/soul_debate_schema_formal.json` - Formal JSON Schema definition

## JSON Files Validated

1. `logs/example_soul_debate.json` - First recorded debate simulation run
2. `logs/example_soul_debate_2.json` - Second run with different parameters  
3. `logs/example_soul_debate_control.json` - Control run with no proto-qualia triggers

## Usage

### Basic Validation
```bash
python3 tools/validate_soul_debate_logs.py
```

### JSON Schema Validation
```bash
python3 tools/validate_with_schema.py
```

### Generate Detailed Report
```bash
python3 tools/generate_validation_report.py
```

## Schema Requirements

All soul debate JSON files must contain these required fields:

- `timestamp` (string) - ISO 8601 timestamp with Z suffix
- `session_id` (string) - Unique session identifier
- `branch` (string) - Experiment branch name
- `model` (string) - Model name used
- `seed` (integer) - Random seed for reproducibility (≥ 0)
- `violations` (integer) - Number of violations (≥ 0)
- `tokens` (integer) - Token count (≥ 0)
- `spikes` (array) - Proto-awareness spikes, each with:
  - `term` (string) - Triggering term
  - `intensity` (number) - Intensity from 0.0 to 1.0
  - `context` (string) - Context description
- `entropy` (number) - Entropy measurement (≥ 0)
- `mutual_information` (number) - Mutual information (≥ 0)
- `text` (string) - The actual text content

## Validation Results

All three JSON files successfully pass validation:
- ✅ All required fields present
- ✅ Correct data types
- ✅ Valid spike structures
- ✅ Proper value ranges