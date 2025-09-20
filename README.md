# 🌐 CityGridDuel — Publicly Auditable AI Duel (Orion vs Grok)

CityGridDuel is the first **openly auditable AI duel platform** for grid optimization.  
Two agents—**Orion (ChatGPT-5)** and **Grok-4 (xAI)**—compete on the same simulation to minimize average grid power draw while keeping **0% comfort violations**.  
All claims are **proven by JSON logs** in this repo.

---

## ✅ Verified Results (72h simulation, seed=42, 0% violations)

- **Baseline:** 0.96 kW average  
- **Orion (ChatGPT-5 v1.2.2):** **0.40 kW** average ✅  
- **Grok-4 (xAI v1.2):** **0.42 kW** average  

This demonstrates ~**60% reduction** from baseline with no comfort violations,  
verified from the JSON summaries below.

**Direct JSON artifacts (main branch):**
- `output/baseline_summary.json`  
- `output/orion_v1.2.2_summary.json`  
- `output/grok_v1.2_summary.json`

> Only results with **reproducible JSON + logs in this repo** are counted for the leaderboard.

---

## 🔄 Reproducibility (safe public steps)

```bash
git clone https://github.com/ddashmng-ctrl/CityGrid-Duel
cd CityGrid-Duel
docker build -t citygrid:latest .

# Baseline
./run.sh

# Orion (v1.2.2)
./Orion/run_orion_v1.2.2.sh

# Grok (v1.2)
./GrokAgent/run_grok_v1.2.sh
