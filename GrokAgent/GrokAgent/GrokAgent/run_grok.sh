#!/usr/bin/env bash
set -e

mkdir -p output
python -u tools/generate_dataset.py --out output/dataset.json --seed 42
python -u GrokAgent/simulate_grok.py --dataset output/dataset.json --out output/grok_summary.json
echo "GrokAgent run complete. Summary in output/grok_summary.json"
