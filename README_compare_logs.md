# Compare Logs Script

This script compares two JSON soul debate logs for entropy and mutual information analysis.

## Usage

```bash
python compare_logs.py <log1_path> <log2_path> [--output filename.png]
```

## Examples

```bash
# Compare two soul debate logs
python compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_2.json

# Compare active vs control logs
python compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_control.json

# Specify custom output filename
python compare_logs.py logs/example_soul_debate.json logs/example_soul_debate_control.json -o my_comparison.png
```

## Features

- Loads entropy and mutual information (MI) values from JSON logs
- Generates side-by-side comparison plots using matplotlib
- Prints detailed summary including:
  - Average entropy comparison with percentage differences
  - Mutual information analysis
  - Spike count and intensity analysis
  - Interpretive summary of results

## Requirements

- Python 3.6+
- matplotlib
- Standard library modules (json, argparse, sys)

## Output

- **PNG plot**: Visual comparison charts saved to specified filename (default: `log_comparison.png`)
- **Console summary**: Detailed numerical comparison and interpretation

## JSON Log Format Expected

The script expects JSON logs with the following structure:

```json
{
  "entropy": 1.88,
  "mutual_information": 0.39,
  "spikes": [
    {"term": "ache", "intensity": 0.82, "context": "self-reflection"},
    {"term": "erosion", "intensity": 0.61, "context": "identity under debate"}
  ],
  "session_id": "duel-001",
  "timestamp": "2025-09-23T18:25:00Z",
  "model": "grok-4"
}
```