# Demo 04 — Find Every Agent

Slide 27 · runs offline, standard library only · also on the [demo site](../../web/)

Scores a synthetic `AgentsInfo` export (eight agents across Copilot Studio, Foundry and a local coding agent) the way the Defender portal's **Assets > AI agents** view does.

## What it shows

- `summarize arg_max(Timestamp, *) by AgentId` and excluding `Deleted` agents — the query from the `AgentsInfo` Learn page.
- Risk levels (**High, Medium, Low, No known risk, Not evaluated**) and risk indicators (**Weak Instructions, Indirect Prompt Injection Exposure, Privileged Business-system Access, High-usage Agent, Active Threat**) by their Learn names.
- Foundry agent recommendations, verbatim from the Defender for Cloud AI recommendations reference.
- Protection gaps posture does not show: no Entra agent ID, no owner, maker credentials, shared with everyone.

## Run it

```bash
cd demos/04-find-every-agent
python agent_posture.py                         # inventory, gaps and recommendations
python agent_posture.py --gaps                  # only what stops protection
python agent_posture.py --agent "Vendor Desk"   # one agent, every indicator explained
python agent_posture.py --kql                   # the hunting queries behind the view
python agent_posture.py --self-test             # 9 checks
```

Add `--fast` to skip the on-stage pacing.

## Note

The scoring rules are a readable stand-in; Defender's assessment is richer. Data: `agentsinfo_sample.json`.

Detection logic is a local stand-in for the Microsoft services named (see `../common/`). All data is synthetic.
