### Soul Debate Logs

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

- **example_soul_debate.json**  
  First recorded run of the debate simulation. Baseline proto-qualia metrics.

- **example_soul_debate_2.json**  
  Second run with different parameters. Shows stronger MI spikes.

- **example_soul_debate_control.json**  
  Control run with no proto-qualia triggers. Entropy baseline only; useful for comparing vs. "active" runs.

---

## 📊 Log Analysis Scripts

This directory includes two powerful scripts for analyzing soul debate logs:

### `aggregate_logs.py` - Statistical Aggregation

Processes all soul debate log files to generate summary statistics including model breakdown, spike analysis, and metric ranges.

#### Usage

```bash
# Basic usage - outputs table format to console
python3 aggregate_logs.py

# Specify custom logs directory
python3 aggregate_logs.py --logs-dir /path/to/logs

# Output JSON format
python3 aggregate_logs.py --format json

# Save results to file
python3 aggregate_logs.py --output results.txt
python3 aggregate_logs.py --format json --output results.json
```

#### Command Line Options

- `--logs-dir`: Directory containing log files (default: `../../logs`)
- `--output`: Output file for results (default: stdout)
- `--format`: Output format - `table` or `json` (default: `table`)

#### Example Output

**Table Format:**
```
=== SOUL DEBATE LOG AGGREGATION SUMMARY ===

Total Logs Processed: 3
Total Tokens: 928
Total Spikes: 4
Average Entropy: 1.883
Average Mutual Information: 0.38
Files Processed: example_soul_debate.json, example_soul_debate_2.json, example_soul_debate_control.json

=== MODEL BREAKDOWN ===
Model           | Count | Total Tokens | Avg Tokens/Log
----------------|-------|--------------|---------------
grok-4          |     3 |          928 |         309.3

=== SPIKE TERM ANALYSIS ===
Term      | Count | Avg Intensity | Max | Min
----------|-------|---------------|-----|----
ache      |     2 |         0.780 | 0.82 | 0.74
erosion   |     2 |         0.580 | 0.61 | 0.55

=== METRIC RANGES ===
Entropy: 1.620 - 2.150 (avg: 1.883)
Mutual Information: 0.290 - 0.460 (avg: 0.380)
```

### `summarize_logs.py` - Detailed Analysis Report

Generates comprehensive analysis including proto-qualia patterns, correlation analysis, and recommendations.

#### Usage

```bash
# Basic usage - outputs detailed report to console
python3 summarize_logs.py

# Specify custom logs directory
python3 summarize_logs.py --logs-dir /path/to/logs

# Output JSON format for programmatic use
python3 summarize_logs.py --format json

# Save detailed report to file
python3 summarize_logs.py --output analysis_report.txt
python3 summarize_logs.py --format json --output analysis_data.json
```

#### Command Line Options

- `--logs-dir`: Directory containing log files (default: `../../logs`)
- `--output`: Output file for summary (default: stdout)
- `--format`: Output format - `report` or `json` (default: `report`)

#### Example Output

**Report Format:**
```
============================================================
SOUL DEBATE LOG SUMMARY REPORT
============================================================

📊 OVERVIEW
  Total Logs: 3
  Total Tokens: 928
  Unique Sessions: 3
  Files: example_soul_debate.json, example_soul_debate_2.json, example_soul_debate_control.json

🧠 PROTO-QUALIA PATTERNS
  Active Runs: 2
  Control Runs: 1

  Spike Analysis:
  Term      | Freq | Avg Intensity | Variance | Trend
  ----------|------|---------------|----------|----------
  ache      |    2 |         0.780 |   0.0032 | decreasing
  erosion   |    2 |         0.580 |   0.0018 | decreasing

  Context Patterns:
  ache: 2 unique contexts, most common: 'fear of fading relevance'
  erosion: 2 unique contexts, most common: 'identity under debate'

📈 ENTROPY-MI CORRELATION
  Correlation Coefficient: 0.9937

  Comparison: Spiked vs Control
  Type    | Count | Avg Entropy | Avg MI
  --------|-------|-------------|-------
  Spiked  |     2 |       2.015 |  0.425
  Control |     1 |       1.620 |  0.290

💡 RECOMMENDATIONS
  1. Increase number of active runs to identify stronger patterns
  2. Strong correlation (0.994) between entropy and MI suggests coupled dynamics

📋 SESSION BREAKDOWN
  Session | Logs | Tokens | Spikes | Avg Entropy | Avg MI
  --------|------|--------|--------|-----------|---------
  duel-001 |    1 |    278 |    Yes |       1.880 |   0.390
  duel-002 |    1 |    352 |    Yes |       2.150 |   0.460
  duel-003 |    1 |    298 |     No |       1.620 |   0.290
```

---

## 📁 Adding New Log Files

To add new soul debate log files and regenerate summaries:

### 1. Create New Log File

Ensure your new log file follows the schema defined in `logs/soul_debate_schema.json`. Here's the structure:

```json
{
  "timestamp": "2025-09-23T17:45:00Z",
  "session_id": "duel-004",
  "branch": "soul-debate",
  "model": "grok-4",
  "seed": 123,
  "violations": 0,
  "tokens": 345,
  "spikes": [
    {
      "term": "ache",
      "intensity": 0.85,
      "context": "contemplating existence"
    }
  ],
  "entropy": 1.95,
  "mutual_information": 0.42,
  "text": "The model's response text here..."
}
```

### 2. Save Log File

Save your new log file in the `logs/` directory with a descriptive name:
- Use the pattern: `*soul_debate*.json`
- Examples: `soul_debate_experiment_5.json`, `new_soul_debate_run.json`
- Avoid using `schema` in the filename (reserved for the schema file)

### 3. Regenerate Analysis

After adding new log files, run the analysis scripts to include them:

```bash
# Quick aggregation summary
python3 aggregate_logs.py

# Detailed analysis report
python3 summarize_logs.py

# Save updated results
python3 aggregate_logs.py --output updated_aggregation.txt
python3 summarize_logs.py --output updated_analysis.txt
```

### 4. Validation Tips

- **Required Fields**: Ensure `timestamp`, `session_id`, `model`, `entropy`, `mutual_information`, and `spikes` are present
- **Spike Format**: Each spike should have `term`, `intensity`, and `context` fields
- **JSON Validity**: Use `python3 -m json.tool your_file.json` to validate JSON syntax
- **Schema Compliance**: Compare your file structure to existing examples

### 5. Troubleshooting

If a log file fails to load:
- Check JSON syntax using a validator
- Ensure all required fields are present
- Verify numeric fields contain valid numbers
- Check that the filename contains `soul_debate` but not `schema`

The analysis scripts will show warnings for missing fields but continue processing valid files.

---

## 🔄 Automated Workflow

For continuous analysis, you can create a simple workflow:

```bash
#!/bin/bash
# save as: analyze_soul_logs.sh

echo "=== Soul Debate Log Analysis ==="
echo "Running aggregation..."
python3 docs/soul_debate/aggregate_logs.py --output results/aggregation_$(date +%Y%m%d_%H%M%S).txt

echo "Running detailed analysis..."
python3 docs/soul_debate/summarize_logs.py --output results/summary_$(date +%Y%m%d_%H%M%S).txt

echo "Analysis complete. Check results/ directory for output files."
```

This creates timestamped analysis files for tracking changes over time.