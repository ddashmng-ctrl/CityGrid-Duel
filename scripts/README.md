# Scripts Directory

This directory contains utility scripts for analyzing and comparing CityGrid Duel logs.

## compare_logs.py

A Python script for comparing two JSON log files containing entropy and mutual information data from soul debate sessions.

### Features

- **Data Validation**: Validates JSON format and required fields (entropy, mutual_information, spikes)
- **Statistical Analysis**: Computes differences in entropy, mutual information, and spike metrics
- **Visualization**: Creates side-by-side comparison plots showing:
  - Entropy comparison (bar chart)
  - Mutual information comparison (bar chart) 
  - Spike count comparison (bar chart)
  - Spike intensity scatter plot
- **Summary Output**: Detailed text summary with session metadata and metric differences
- **Error Handling**: Comprehensive error handling for file I/O and data validation issues

### Usage

```bash
# Basic comparison
python scripts/compare_logs.py logs/file1.json logs/file2.json

# Skip plotting (for headless environments)
python scripts/compare_logs.py logs/file1.json logs/file2.json --no-plot

# Save plot to custom location
python scripts/compare_logs.py logs/file1.json logs/file2.json --save-plot my_comparison.png

# View help
python scripts/compare_logs.py --help
```

### Examples

```bash
# Compare two soul debate sessions
python scripts/compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_2.json

# Compare active session vs control
python scripts/compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_control.json
```

### Requirements

- Python 3.6+
- matplotlib
- numpy

### Expected JSON Format

The script expects JSON files with the following structure:

```json
{
  "timestamp": "2025-09-23T18:25:00Z",
  "session_id": "duel-001", 
  "model": "grok-4",
  "entropy": 1.88,
  "mutual_information": 0.39,
  "spikes": [
    {"term": "ache", "intensity": 0.82, "context": "self-reflection"},
    {"term": "erosion", "intensity": 0.61, "context": "identity under debate"}
  ],
  "tokens": 278,
  "text": "..."
}
```

Required fields: `entropy`, `mutual_information`, `spikes`