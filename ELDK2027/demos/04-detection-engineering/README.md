# Demo 04 — The Detection Engineering Agent

Slide 20 · runs offline, standard library only · also on the [demo site](https://eldk2027-demos.vercel.app/?demo=detection)

The detection engineering agent takes the Demo 03 envelope and drafts three candidate rules:

- an IOC rule
- a broad rule
- a behavioural rule

It back-tests each one against seven days of synthetic telemetry before asking anyone to enable it.

## What it shows

- **The gates:** catch every known-bad case, keep false positives to 2 a day or fewer, and stay under the 150-alerts-per-run cap that custom detections have.
- **What the back-test finds:**
  - The IOC rule misses an earlier attack from a different AiTM node.
  - The broad rule fires 18 times a day.
  - Only the behavioural rule passes.
- **Enabling is a hard action.** The rule is created disabled, and a human approves it with the back-test report attached.
- **`--ship-first`:** what day one looks like when the agent enables its first draft.

## Run it

```bash
cd demos/04-detection-engineering
python detection_agent.py               # draft, back-test, gate, ask
python detection_agent.py --ship-first  # 23 alerts, 0 real
python detection_agent.py --kql         # the three candidates as KQL
python detection_agent.py --self-test   # 9 checks
```

The KQL is illustrative. Check the table and column names against your own workspace before you use it.

All data is synthetic. The agent logic is a deterministic local stand-in for the systems named.
