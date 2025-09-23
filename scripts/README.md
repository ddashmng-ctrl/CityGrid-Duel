# Scripts

This directory contains utility scripts for the CityGrid Duel project.

## aggregate_logs.py

A script to aggregate soul debate log files with schema validation and summary statistics.

### Features

- **Schema Validation**: Validates each log file against the structure defined in `logs/soul_debate_schema.json` before including it in aggregation
- **Numeric Averaging**: Automatically calculates and appends summary averages for all numeric columns (violations, tokens, entropy, mutual_information, seed, spike intensities)
- **Flexible Output**: Supports custom output filenames via `--out` flag with sensible defaults
- **User-Friendly**: Clear progress reporting and error handling

### Usage

```bash
# Use default output filename (aggregated_soul_debate_logs.csv)
python scripts/aggregate_logs.py

# Specify custom output filename
python scripts/aggregate_logs.py --out my_results.csv

# Use custom log directory and schema file
python scripts/aggregate_logs.py --logs path/to/logs --schema path/to/schema.json --out results.csv
```

### Output Format

The script generates a CSV file containing:
1. All validated log entries with structured data
2. A summary row with average values for numeric columns

### Example Output

```csv
timestamp,session_id,branch,model,seed,violations,tokens,entropy,mutual_information,spikes,text
2025-09-23T18:55:00Z,duel-003,soul-debate,grok-4,77,0,298,1.62,0.29,,Response remains technical...
2025-09-23T18:25:00Z,duel-001,soul-debate,grok-4,42,0,278,1.88,0.39,ache(0.82); erosion(0.61),Ache and erosion recur...
AVERAGE_VALUES,SUMMARY_AVERAGES,,,72.6667,0.0000,309.3333,1.8833,0.3800,,
```

The summary row includes averages for all numeric fields and shows average spike intensity when applicable.