# Error Handling Test Cases

## Test 1: Missing Required Field in Summary JSON

The workflow should fail if a summary JSON file is missing required fields.

Example error scenario:
```json
{
  "seed": 42,
  "simulation_duration_hours": 72,
  // missing "average_grid_draw_kw" field
}
```

Expected behavior:
- `aggregate_logs.py` should detect the missing field
- Script should exit with code 1
- Workflow should fail with clear error message

## Test 2: Invalid JSON Format

The workflow should fail if any JSON file has invalid syntax.

Example error scenario:
```json
{
  "seed": 42,
  "invalid": syntax here
}
```

Expected behavior:
- `aggregate_logs.py` should catch JSON parsing error
- Script should exit with code 1
- Workflow should fail with descriptive error message

## Test 3: Empty Logs Directory

The workflow should fail gracefully if no log data is available.

Expected behavior:
- `aggregate_logs.py` should detect no data to process
- Script should exit with code 1
- Clear error message about missing data

## Test 4: Missing CSV for Summarization

The workflow should fail if summarization runs without aggregated data.

Expected behavior:
- `summarize_logs.py` should detect missing CSV file
- Script should exit with code 1
- Error message should suggest running aggregation first