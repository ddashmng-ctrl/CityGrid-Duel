# Sub-0.30 kW Pilot — V2G + Building Flex
Goal: hit < 0.30 kW avg (72h, seed=42, 0% violations) by adding EV fleet Vehicle-to-Grid (V2G) and building flexibility.

**How to run**
docker build -t citygrid:latest .
./run.sh
./agents/orion_v2g/run_orion_v2g.sh

**Outputs (must exist)**
- output/orion_v2g/orion_v2g_summary.json
- output/orion_v2g/run.log

**Scoring rules**
- seed=42, hours=72, comfort_violations=0
- lower average_grid_draw_kw is better

**Scenario knobs**
- scenarios/v2g_s1/config.json : { "num_ev": 50, "battery_kwh": 60, "v2g_limit_kw": 7.2 }

**Vision**
Citizens as distributed energy partners: EVs/home batteries discharge at peaks and recharge off-peak—cutting city demand and paying participants.