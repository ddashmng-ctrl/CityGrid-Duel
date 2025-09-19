import json, sys, os, glob

REQ = {"seed": 42, "simulation_duration_hours": 72, "comfort_violations": 0}

def load(path):
    with open(path) as f:
        return json.load(f)

def score(label, path):
    J = load(path)
    errs = []
    for k, v in REQ.items():
        if J.get(k) != v:
            errs.append(f"{label}: {k}={J.get(k)} (expected {v})")
    avg = J.get("average_grid_draw_kw")
    if avg is None:
        errs.append(f"{label}: missing average_grid_draw_kw")
    return avg, errs

def find_one(pattern):
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None

paths = {
    "baseline": find_one("output/baseline*_summary.json") or "output/baseline_summary.json",
    "orion":    find_one("output/orion_v1.2/*summary.json"),
    "grok":     find_one("output/grok_v1.2*summary.json") or find_one("output/grok*_summary.json"),
}

results = []
errors = []

for label, p in paths.items():
    if p and os.path.exists(p):
        avg, errs = score(label, p)
        if avg is not None:
            results.append((label, avg, p))
        errors += errs
    else:
        errors.append(f"{label}: no JSON file found")

results.sort(key=lambda x: x[1])  # lower is better

print("== Verified Leaderboard ==")
for i, (label, avg, p) in enumerate(results, 1):
    print(f"{i}. {label} → {avg:.2f} kW ({p})")

if errors:
    print("\nIssues:")
    for e in errors:
        print("-", e)

crit = [e for e in errors if "no JSON" in e or "expected" in e or "missing" in e]
sys.exit(1 if crit else 0)