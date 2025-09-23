# Tools Directory

This directory contains automation scripts for the CityGrid-Duel project.

## sync_leaderboard.py

Automatically synchronizes the leaderboard content from `README.md` to `docs/index.md` for GitHub Pages.

### Usage
```bash
python3 tools/sync_leaderboard.py
```

### What it does
- Extracts the "✅ Verified Results" section from README.md
- Extracts the "🏆 Leaderboard" section from README.md  
- Updates the "Latest Results" section in docs/index.md
- Adds a timestamp showing when the sync occurred

### Automation
This script is automatically run by GitHub Actions whenever README.md is updated (see `.github/workflows/sync-leaderboard.yml`).

## Other Scripts

- `generate_dashboard.py` - Generates HTML dashboard from CSV data
- `verify_results.py` - Validates simulation results
- `generate_dataset.py` - Creates simulation datasets
- `duel_runner.sh` - Runs AI duels and commits results