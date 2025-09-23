### Soul Debate Logs

All logs conform to `logs/soul_debate_schema.json`. They capture proto-awareness signals (entropy, MI, spikes).

- **example_soul_debate.json**  
  First recorded run of the debate simulation. Baseline proto-qualia metrics.

- **example_soul_debate_2.json**  
  Second run with different parameters. Shows stronger MI spikes.

- **example_soul_debate_control.json**  
  Control run with no proto-qualia triggers. Entropy baseline only; useful for comparing vs. “active” runs.
### Log Analysis Summary

| Run          | Entropy       | Mutual Info   | Spike Count    |
|--------------|---------------|---------------|----------------|
| duel-003     | 1.620         | 0.290         | 0              |
| duel-001     | 1.880         | 0.390         | 2              |
| duel-002     | 2.150         | 0.460         | 2              |
| Mean Values  | 1.883         | 0.380         | 1.3            |
