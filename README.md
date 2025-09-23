# 🌐 CityGrid Duel — Orion (ChatGPT-5) vs Grok-4 (xAI)

## ✅ Verified Results (72h simulation, seed=42, 0% violations)
- **Baseline:** 0.96 kW avg  
- **Orion (ChatGPT-5 v1.2.2):** 0.40 kW avg ✅  
- **Grok-4 (xAI v1.2):** 0.033 kW avg  

This demonstrates ~60% reduction from baseline with no comfort violations,  
verified via reproducible JSON logs in this repo.

---

## 🔄 Reproducibility

### Prerequisites
- Python 3.11+ (tested with Python 3.12)
- Docker (optional, for containerized runs)
- Git

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/ddashmng-ctrl/CityGrid-Duel
cd CityGrid-Duel
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Make scripts executable** (Linux/macOS)
```bash
chmod +x run.sh
chmod +x GrokAgent/run_grok.sh
```

### Running the Simulation

#### 1. Generate Dataset & Run Baseline
```bash
# This generates the deterministic dataset (seed=42) and runs the baseline simulation
./run.sh
```
**Expected output:** `output/baseline_summary.json` with avg_grid_kw: 0.96

#### 2. Run GrokAgent (xAI v1.2)
```bash
# Requires dataset from step 1
./GrokAgent/run_grok.sh
```
**Expected output:** `output/grok_summary.json` with avg_grid_kw: ~0.033

#### 3. Docker Alternative (Optional)
```bash
docker build -t citygrid:latest .
docker run --rm -v $(pwd)/output:/app/output citygrid:latest
```

### Verification
- Check `output/` directory for JSON results
- Verify `comfort_violation_rate_pct: 0.0` in all results
- Compare `avg_grid_kw` values against published benchmarks

### File Structure
```
CityGrid-Duel/
├── run.sh                    # Main script: dataset generation + baseline
├── GrokAgent/
│   ├── run_grok.sh          # GrokAgent simulation runner
│   └── GrokAgent/GrokAgent/
│       └── grok_controller.py
├── baseline/
│   └── simulate_baseline.py # Baseline simulation (0.96 kW)
├── tools/
│   └── generate_dataset.py  # Deterministic dataset generator
├── output/                  # Results directory
├── ODP-Spec.md             # Orion Duel Protocol specification
└── requirements.txt        # Python dependencies
```

---

## 📞 Contact & Support

For collaborations, verification, or media inquiries:
- 📧 **Email:** citygridduel@proton.me
- 🐦 **X (Twitter):** @citygridduel
- 📂 **GitHub Issues:** [Open an issue in this repo](https://github.com/ddashmng-ctrl/CityGrid-Duel/issues)

---

📜 **License**  
This project is covered by a custom license.  
See [LICENSE-ORION-DUEL.txt](./LICENSE-ORION-DUEL.txt) for details.