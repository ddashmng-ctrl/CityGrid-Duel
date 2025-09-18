import json, argparse
from grok_controller import grok_strategy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.dataset) as f:
        ds = json.load(f)

    summary = grok_strategy(ds)

    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)

    print("Wrote GrokAgent results to", args.out)
