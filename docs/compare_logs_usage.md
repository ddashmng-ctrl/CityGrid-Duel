# Compare Logs Script Documentation

## Overview

The `compare_logs.py` script in the `scripts/` directory provides comprehensive analysis and visualization of entropy and mutual information (MI) metrics from multiple JSON log files.

## Features

- **Multi-file input**: Accept any number of JSON files as input
- **Time series plotting**: When timestamps are available, creates time series plots showing metrics over time
- **Comparison plotting**: When no timestamps exist, creates comparison bar charts
- **Statistical analysis**: Provides mean, standard deviation, min, and max statistics
- **Robust error handling**: Gracefully handles missing files and invalid JSON
- **High-quality output**: Generates 300 DPI PNG images for documentation

## Usage

### Basic Usage
```bash
python scripts/compare_logs.py file1.json file2.json [file3.json ...]
```

### With glob patterns
```bash
python scripts/compare_logs.py logs/*.json
```

### Verbose output
```bash
python scripts/compare_logs.py --verbose logs/*.json
```

### Custom output directory
```bash
python scripts/compare_logs.py --output-dir custom_dir logs/*.json
```

## Output

The script generates two plots:
- `entropy_over_time.png` or `entropy_comparison.png`
- `mutual_information_over_time.png` or `mutual_information_comparison.png`

These are saved to `docs/qualia/imgs/` by default for easy embedding in README.md files.

## JSON File Format

Expected JSON structure:
```json
{
  "timestamp": "2025-09-23T18:25:00Z",
  "session_id": "duel-001",
  "entropy": 1.88,
  "mutual_information": 0.39,
  "...": "other fields"
}
```

Required fields:
- `entropy`: Numeric entropy value
- `mutual_information`: Numeric MI value  
- `timestamp`: ISO format timestamp (optional, enables time series plots)

## Examples

Generated plots show:
- Time series progression of metrics across different sessions
- Clear labeling with file names and values
- Statistical summaries in console output
- Professional formatting suitable for documentation

The script successfully handles the existing log files in the repository and provides clear, informative visualizations for analysis.