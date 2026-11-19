# Demo 05 — Hunt the Agent Kill Chain

Slide 29 · runs offline, standard library only · also on the [demo site](../../web/)

Five advanced hunting queries over a synthetic week of Defender XDR data that assemble one campaign across three agents.

## What it shows

- `AlertInfo`: model alerts and endpoint agent alerts in one place.
- `BehaviorInfo`: real-time protection behaviors — Blocked vs Audited.
- `CloudAppEvents` with agent ActionTypes (`InvokeAgent`, `InferenceCall`, `ExecuteToolBySDK`, `ExecuteToolByGateway`, `ExecuteToolByMCPServer`): what an audited agent did next.
- An IP pivot from `AlertEvidence`, and `AgentsInfo` enrichment that shows the leak was posture debt.

## Run it

```bash
cd demos/05-hunt-the-agent-kill-chain
python hunt_agents.py               # all five hunts, then the timeline
python hunt_agents.py --hunt 3      # the audited SendEmail that succeeded
python hunt_agents.py --hunt 4      # the IP pivot
python hunt_agents.py --kql         # the queries only, to paste
python hunt_agents.py --self-test   # 8 checks
```

Add `--fast` to skip the on-stage pacing.

## Note

There is no KQL engine here: the printed KQL is evaluated by equivalent Python over `hunting_sample.json`. Table and ActionType names are from Learn; values inside `AdditionalFields` / `RawEventData` are illustrative — check your tenant. The queries are also in [`../kql/agent-hunting.kql`](../kql/agent-hunting.kql).

Detection logic is a local stand-in for the Microsoft services named (see `../common/`). All data is synthetic.
