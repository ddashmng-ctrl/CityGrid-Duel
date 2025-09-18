```markdown
# 🌐 CityGrid Duel — Orion (ChatGPT-5) vs Grok-4 (xAI)

Baseline demo results:  
- ⚡ Average grid draw: **0.96 kW**  
- 🌡️ Comfort violations: **0%**  
- ⏱️ Duration: **72h simulation**

## How to run

1. Build the Docker image:
   ```bash
   docker build -t citygrid:latest .
   ```

2. Run the baseline simulation:
   ```bash
   ./run.sh
   ```

Outputs will be saved in the `output/` folder.

---

This repo is the starting point for the **CityGrid Duel** challenge.  
Rules: open-source agents, same dataset, Docker reproducibility, independent auditors
## Competing Agents
- Orion (baseline): 0.96 kW avg, 0% violations  
- Grok-4 Energy Optimizer: ~0.82 kW avg, 0% violations (target)  
