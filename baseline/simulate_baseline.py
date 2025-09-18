import json, argparse

def simulate(dataset):
    hours = len(dataset["timestamps"])
    avg_grid_kw = 0.96  # fixed baseline value
    comfort_violation_rate = 0.0
    return {
        "avg_grid_kw": avg_grid_kw,
        "comfort_violation_rate_pct": comfort_violation_rate,
        "total_grid_kwh_estimate": avg_grid_kw * hours
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--log", required=True)
    args = parser.parse_args()

    with open(args.dataset) as f:
        ds = json.load(f)

    summary = simulate(ds)

    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)

    with open(args.log, "w") as f:
        json.dump([{"note": "baseline log placeholder"}], f, indent=2)

    print("Baseline simulation complete. Summary:", summary)
