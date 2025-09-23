#!/bin/bash
# Run GrokAgent simulation

# Step 1: make sure dataset exists
DATASET="output/dataset.json"
if [ ! -f "$DATASET" ]; then
  echo "Error: dataset not found at $DATASET. Please run ./run.sh first to generate the dataset."
  exit 1
fi

# Step 2: create output directory
mkdir -p output

# Step 3: run Grok controller
python3 GrokAgent/GrokAgent/GrokAgent/grok_controller.py \
  --dataset $DATASET \
  --out output/grok_summary.json

# Step 4: print result
echo "✅ GrokAgent run complete. Results saved to output/grok_summary.json"