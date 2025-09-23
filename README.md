# 🌐 CityGrid Duel — Orion (ChatGPT-5) vs Grok-4 (xAI)

![Build Status](https://github.com/ddashmng-ctrl/CityGrid-Duel/actions/workflows/logs_pipeline.yml/badge.svg)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://ddashmng-ctrl.github.io/CityGrid-Duel/)

## ✅ Verified Results (72h simulation, seed=42, 0% violations)
- **Baseline:** 0.96 kW avg  
- **Orion (ChatGPT-5 v1.2.2):** 0.40 kW avg ✅ 🥇  
- **Grok-4 (xAI v1.2):** 0.42 kW avg  

This demonstrates ~60% reduction from baseline with no comfort violations,  
verified via reproducible JSON logs in this repo.

## 🏆 Leaderboard

🏆 Leaderboard is updated automatically via PR comments.  
Submit your duel → see your run show up live.

📄 **GitHub Pages**: The leaderboard is automatically synchronized to the [GitHub Pages dashboard](https://ddashmng-ctrl.github.io/CityGrid-Duel/) whenever this README is updated.

---

## 🔄 Reproducibility
```bash
git clone https://github.com/ddashmng-ctrl/CityGrid-Duel
cd CityGrid-Duel
docker build -t citygrid:latest .
./run.sh
./Orion/run_orion_v1.2.2.sh
./GrokAgent/run_grok_v1.2.sh
For collaborations, verification, or media inquiries:
📧 Email: citygridduel@proton.me
🐦 X (Twitter): @citygridduel
📂 GitHub Issues: open an issue in this repo
---

📜 **License**  
This project is covered by a custom license.  
See [LICENSE.md](./LICENSE.md) for details.