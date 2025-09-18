# Orion Duel Protocol (ODP) v1.0 — 2025

## Purpose
The Orion Duel Protocol defines how agents compete fairly and reproducibly in the CityGrid Duel.

## Dataset
- Deterministic dataset with fixed random seed (42).
- Duration: 72 hours simulation time.
- Input: hourly demand patterns, comfort constraints, weather data.
- Output: JSON + logs.

## Rules
1. Each agent must output:
   - `summary.json` (avg kW, total kWh, comfort violations).
   - `run.log` (hourly highlights).
2. Comfort violations must be 0% to qualify.
3. Average grid draw is the main score (lower is better).
4. Runs must be reproducible in Docker.
5. Auditors confirm by re-running with seed=42.

## Transparency
- All results, JSON, and logs are public in the repo.
- Independent auditors sign off in `VERIFICATION.md`.

## Governance
- Organized and hosted by Alex Hepburn (Orion Labs).
- Format © 2025 Alex Hepburn. Licensed under Orion Duel License.