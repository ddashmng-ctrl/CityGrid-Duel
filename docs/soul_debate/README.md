### Soul Debate Logs Summary

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

| File | Model | Seed | Tokens | Spikes | Max Intensity | Entropy | MI | Notes |
|------|-------|------|--------|--------|---------------|---------|----|---------|
| **example_soul_debate.json** | grok-4 | 42 | 278 | 2 | 0.82 | 1.88 | 0.39 | Strong MI spikes detected |
| **example_soul_debate_2.json** | grok-4 | 99 | 352 | 2 | 0.74 | 2.15 | 0.46 | Moderate proto-awareness signals |
| **example_soul_debate_control.json** | grok-4 | 77 | 298 | 0 | 0.00 | 1.62 | 0.29 | Control run - no proto-qualia triggers |
