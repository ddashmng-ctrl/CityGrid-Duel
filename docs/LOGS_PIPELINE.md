# Logs Pipeline Workflow

This document describes the `logs_pipeline.yml` GitHub Actions workflow that automatically applies labels to pull requests that modify files in the `/logs/` directory.

## Features

### 🎯 Automatic Label Application
When a pull request modifies any files in the `/logs/` directory, the workflow automatically applies two labels:
- `proto-qualia` - Indicates changes to proto-awareness signal logs
- `soul-debate` - Indicates changes to soul debate simulation logs

### 🔍 Smart Change Detection
- Analyzes all files changed in the pull request
- Only applies labels when `/logs/` directory files are modified
- Handles mixed PRs (changes both inside and outside `/logs/`)
- Gracefully handles PRs with no `/logs/` changes

### 🛡️ Robust Edge Case Handling
- **Idempotent**: Skips labeling if labels already exist
- **Non-failing**: Continues execution even if label application fails
- **Mixed Changes**: Applies labels even when PR includes non-logs changes
- **Comprehensive Logging**: Provides detailed status information

## Workflow Triggers

The workflow runs on pull request events:
- `opened` - When a new PR is created
- `synchronize` - When new commits are pushed to the PR
- `edited` - When the PR description/title is edited

## Example Scenarios

### Scenario 1: Pure Logs Changes
```
Changed files:
- logs/example_soul_debate.json
- logs/new_experiment.json

Result: ✅ Both labels applied
```

### Scenario 2: Mixed Changes
```
Changed files:
- logs/example_soul_debate.json
- README.md
- tools/verify_results.py

Result: ✅ Both labels applied (logs changes detected)
```

### Scenario 3: No Logs Changes
```
Changed files:
- README.md
- tools/verify_results.py

Result: ℹ️ No labels applied (no logs changes)
```

### Scenario 4: Labels Already Exist
```
Existing labels: proto-qualia, enhancement
Changed files: logs/test.json

Result: ✅ Only soul-debate label added (proto-qualia skipped)
```