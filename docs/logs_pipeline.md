# Logs Pipeline Documentation

## Overview

The logs pipeline workflow (`logs_pipeline.yml`) automatically analyzes soul debate logs and generates matplotlib charts whenever log files or scripts are updated.

## Trigger Conditions

The workflow runs on:
- Pull requests that modify `logs/*.json`, `scripts/**`, or the workflow file itself
- Pushes to the main branch with the same path changes
- Manual workflow dispatch

## Pipeline Steps

### 1. Log Analysis Scripts

#### `scripts/compare_logs.py`
- Compares entropy, mutual information, and spike patterns across log files
- Identifies high-intensity spikes (>0.8)
- Generates comparison statistics
- Output: `output/log_comparison.json`

#### `scripts/aggregate_logs.py`
- Creates time-series data from logs
- Aggregates statistics by model and session
- Tracks entropy and spike evolution over time
- Output: `output/aggregated_logs.json`

#### `scripts/generate_charts.py`
- Creates three types of matplotlib visualizations:
  1. **Entropy Over Time** - Line chart showing entropy evolution by model
  2. **Spike Analysis** - Dual subplot with spike counts and intensities
  3. **Model Comparison** - Bar chart comparing average metrics
- Outputs PNG files with 300 DPI resolution
- Generates markdown summary report

### 2. Artifacts & PR Comments

The workflow:
- Uploads charts and analysis data as GitHub Actions artifacts (30-day retention)
- Posts/updates PR comments with analysis summary and chart information
- Provides direct links to workflow run artifacts for chart downloads

## Chart Types

### Entropy Over Time Chart
- **File**: `entropy_over_time.png`
- **Purpose**: Visualizes how system entropy evolves during debates
- **Features**: Color-coded by model, time-series line plot

### Spike Analysis Chart
- **File**: `spike_analysis.png`
- **Purpose**: Tracks spike frequency and intensity patterns
- **Features**: Dual subplot with counts (top) and intensities (bottom)

### Model Comparison Chart
- **File**: `model_comparison.png`
- **Purpose**: Compares average performance metrics across models
- **Features**: Grouped bar chart with entropy, spike count, and mutual information

## Sample Analysis Output

```
=== Log Analysis Pipeline Summary ===
✅ Log comparison completed
✅ Log aggregation completed 
✅ Chart generation completed
✅ Artifacts uploaded

📊 Analysis Results:
  - Total logs processed: 4
  - Models analyzed: 1
    - grok-4: 4 logs, avg entropy 1.893

📁 Generated artifacts:
- entropy_over_time.png
- spike_analysis.png
- model_comparison.png
- chart_summary.md
```

## Usage

The pipeline runs automatically, but can also be triggered manually:

1. Go to GitHub Actions in the repository
2. Select "Logs Pipeline with Charts" workflow
3. Click "Run workflow"

## Dependencies

- Python 3.11
- matplotlib >= 3.5.0
- pandas
- numpy

## Log Format

The pipeline expects JSON logs following the soul debate schema:

```json
{
  "timestamp": "2025-09-23T17:45:00Z",
  "session_id": "duel-001",
  "model": "grok-4",
  "entropy": 1.92,
  "mutual_information": 0.41,
  "spikes": [
    { "term": "ache", "intensity": 0.87, "context": "reflection" }
  ]
}
```

## Troubleshooting

- **No charts generated**: Check that log files are valid JSON and follow the expected schema
- **Missing artifacts**: Verify the workflow completed successfully in GitHub Actions
- **Invalid workflow**: Use `python -c "import yaml; yaml.safe_load(open('.github/workflows/logs_pipeline.yml'))"` to check syntax