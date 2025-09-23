# Log Validation Workflow

This repository includes an automated GitHub Actions workflow for validating JSON log files in the `logs/` directory against the soul debate schema.

## Overview

The workflow (`log-validation.yml`) automatically validates all JSON files in the `logs/` directory whenever:
- Changes are pushed to any branch affecting `logs/*.json` files
- Pull requests are opened affecting `logs/*.json` files  
- The workflow file itself is modified

## Schema

All log files must conform to the schema defined in `logs/soul_debate_schema.json`. The schema validates:

### Required Fields
- `timestamp`: ISO 8601 timestamp with Z suffix
- `session_id`: Session identifier in format "duel-XXX"
- `branch`: Must be "soul-debate"
- `model`: Model name used for the debate
- `seed`: Non-negative integer random seed
- `violations`: Non-negative integer violation count
- `tokens`: Non-negative integer token count
- `spikes`: Array of proto-awareness spike objects
- `entropy`: Non-negative number for entropy measurement
- `mutual_information`: Non-negative number for mutual information
- `text`: Non-empty string with debate content

### Spike Objects
Each spike in the `spikes` array must contain:
- `term`: String term that triggered the spike
- `intensity`: Number between 0 and 1 (inclusive)
- `context`: String describing the context

## Manual Validation

You can run the validation script locally:

```bash
# Install dependencies
pip install jsonschema

# Run validation
python .github/workflows/validate_logs.py
```

## Error Handling

The validation script provides detailed error messages for:
- **Malformed JSON**: Syntax errors with line/column information
- **Schema violations**: Missing required fields, incorrect data types, etc.
- **File access issues**: Permission errors, missing files, etc.

## Exit Codes

- `0`: All files passed validation
- `1`: One or more files failed validation or encountered errors

This allows the workflow to properly fail CI/CD builds when log files are invalid.