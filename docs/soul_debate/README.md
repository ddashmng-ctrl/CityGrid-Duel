### Soul Debate Logs

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

- **example_soul_debate.json**  
  First recorded run of the debate simulation. Baseline proto-qualia metrics.

- **example_soul_debate_2.json**  
  Second run with different parameters. Shows stronger MI spikes.

- **example_soul_debate_control.json**  
  Control run with no proto-qualia triggers. Entropy baseline only; useful for comparing vs. “active” runs.

## Current Metrics (from aggregated logs)

| Model  | Power Reduction |
|--------|-----------------|
| Orion  | ~58%            |
| Grok   | ~56%            |

_Source: <a>logs/aggregated_logs.csv</a>_