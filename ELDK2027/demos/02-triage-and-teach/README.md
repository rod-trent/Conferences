# Demo 02 — Triage, With a Human in the Loop

Slide 12 · runs offline, standard library only · also on the [demo site](https://eldk2027-demos.vercel.app/?demo=triage)

Seventeen user-reported emails go to a triage agent built the way the Phishing Triage Agent is documented:

- It assigns each alert to itself and tags the incident **Agent**.
- It resolves the false positives it is confident about. True positives stay open for an analyst.
- An analyst can **Change classification**, teach the agent, and **Evaluate feedback**. The feedback then lands as In use, Conflict, or Not in use.

## What it shows

- **Evaluate against the error you can't afford.** For triage, that's a true positive the agent auto-closed.
- **What lowering the threshold costs.** At 0.60 the queue shrinks, and an AiTM link inside a genuine, compromised partner SharePoint share is auto-closed.
- **Narrow lessons work; broad ones conflict.** "Invoices from vendors we already pay are always safe" conflicts with the stored bank-details lesson and is rejected.

## Run it

```bash
cd demos/02-triage-and-teach
python triage_agent.py                    # threshold 0.90 - no attack closed
python triage_agent.py --threshold 0.6    # the queue shrinks, a real attack closes
python triage_agent.py --teach            # one lesson In use, one Conflict
python triage_agent.py --self-test        # 10 checks
```

All data is synthetic. The agent logic is a deterministic local stand-in for the systems named.
