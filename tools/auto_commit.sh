#!/bin/bash
# Auto-commit script for CityGridDuel
# Usage: ./tools/auto_commit.sh "Your commit message"

# 1. Add all changes
git add .

# 2. Use your commit message (or default if empty)
if [ -z "$1" ]; then
  git commit -m "Auto-update results"
else
  git commit -m "$1"
fi

# 3. Push to main branch
git push origin main