#!/bin/bash
# One-click duel runner for Orion and Grok
# Usage: ./tools/duel_runner.sh "Your commit message"

# Define results directory and filenames
RESULTS_DIR="results"
ORION_OUTPUT="$RESULTS_DIR/orion_results.json"
GROK_OUTPUT="$RESULTS_DIR/grok_results.json"

# Ensure results directory exists
mkdir -p "$RESULTS_DIR"

# Step 1: Run Orion and save output
python3 orion.py > "$ORION_OUTPUT"
echo "Orion output saved to $ORION_OUTPUT"

# Step 2: Run Grok and save output
python3 grok.py > "$GROK_OUTPUT"
echo "Grok output saved to $GROK_OUTPUT"

# Step 3: Use auto_commit.sh to commit and push results
./tools/auto_commit.sh "$1"