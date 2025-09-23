#!/usr/bin/env bash
set -e
mkdir -p output
python -u tools/generate_dataset.py --out output/dataset.json --seed 42
python -u baseline/simulate_baseline.py --dataset output/dataset.json --out output/baseline_summary.json --log output/baseline_log.json
echo "Baseline run complete. Summary in output/baseline_summary.json"
