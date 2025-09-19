#!/bin/bash
# Run GrokAgent simulation

# Step 1: make sure dataset exists
DATASET="tools/sample_dataset.json"
if [ ! -f "$DATASET" ]; then
  echo "Error: dataset not found at $DATASET"
  exit 1
fi

# Step 2: run Grok controller
python3 GrokAgent/grok_controller.py \
  --dataset $DATASET \
  --out output/grok_summary.json

# Step 3: print result
echo "✅ GrokAgent run complete. Results saved to output/grok_summary.json"