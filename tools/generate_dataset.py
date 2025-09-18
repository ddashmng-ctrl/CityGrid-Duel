import json, argparse, math, random
from datetime import datetime, timedelta

def gen_dataset(hours=72, seed=42):
    random.seed(seed)
    start = datetime(2025, 9, 17, 0, 0, 0)
    timestamps = [(start + timedelta(hours=h)).isoformat()+"Z" for h in range(hours)]
    weather = []
    price = []
    for h in range(hours):
        hour = (start + timedelta(hours=h)).hour
        temp = 21 + 6*math.sin((hour/24.0)*2*math.pi)
        weather.append({"ts": timestamps[h], "temp_C": round(temp,2)})
        if 17 <= hour <= 20:
            price.append(0.40)
        elif 7 <= hour <= 16:
            price.append(0.18)
        else:
            price.append(0.08)
    return {"timestamps": timestamps, "weather": weather, "price": price}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ds = gen_dataset(seed=args.seed)
    with open(args.out, "w") as f:
        json.dump(ds, f, indent=2)
    print("Wrote", args.out)
