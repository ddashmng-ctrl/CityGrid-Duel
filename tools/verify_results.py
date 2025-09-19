import json, glob, os, sys

REQ = {"seed": 42, "simulation_duration_hours": 72, "comfort_violations": 0}

def load(path):
    with open(path) as f: return json.load(f)

def check(label, path):
    J = load(path)
    errs = []
    for k, v in REQ.items():
        if J.get(k) != v:
            errs.append(f"{label}: {k}={J.get(k)} (expected {v})")
    avg = J.get("average_grid_draw_kw")
    return avg, errs

def find(pattern): 
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None

paths = {
  "baseline": find("output/baseline*_summary.json"),
  "orion":    find("output/orion_v*/orion*_summary.json"),
  "grok":     find("output/orion_v*/grok*_summary.json"),
}

results, errors = [], []
for label, p in paths.items():
    if p and os.path.exists(p):
        avg, errs = check(label, p)
        if avg is not None: results.append((label, avg, p))
        errors += errs
    else:
        errors.append(f"{label}: no JSON found")

results.sort(key=lambda x: x[1])  # lower is better
print("== Verified Leaderboard ==")
for i,(label,avg,p) in enumerate(results,1):
    print(f"{i}. {label} → {avg:.2f} kW ({p})")

if errors:
    print("\nIssues:")
    for e in errors: print("-", e)
sys.exit(1 if errors else 0)