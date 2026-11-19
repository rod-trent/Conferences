# Demos — Defender for Agents

Six demos, Python 3.10+ standard library only, no network, no tenant.

```bash
python ../run-all-tests.py   # everything, ~12 s
```

| # | Demo | Slide | Script | Self-test |
|---|---|---|---|---|
| 01 | [Shield the Model, Alert the SOC](01-shield-the-model/) | 18 | `shield_and_alert.py` | 10 checks |
| 02 | [Stop the Tool Call](02-stop-the-tool-call/) | 22 | `runtime_protection.py` | 10 checks |
| 03 | [The Agent on Your Laptop](03-agent-on-the-endpoint/) | 24 | `local_agent_protection.py` | 9 checks |
| 04 | [Find Every Agent](04-find-every-agent/) | 27 | `agent_posture.py` | 9 checks |
| 05 | [Hunt the Agent Kill Chain](05-hunt-the-agent-kill-chain/) | 29 | `hunt_agents.py` | 8 checks |
| 06 | [Red-Team Your Agent](06-red-team-your-agent/) | 30 | `red_team_agent.py` | 9 checks |

## Shared code

- [`common/term.py`](common/term.py) — terminal output. The markers `STEP n/N`, `>> WHY THIS MATTERS:` and `VERDICT:` are where the demo site pauses playback.
- [`common/shields.py`](common/shields.py) — a transparent heuristic stand-in for Prompt Shields that returns the same response shapes, plus ASCII-smuggling encode/decode.
- [`common/runtime.py`](common/runtime.py) — a stand-in for tool-invocation inspection, returning Defender XDR's detection-type labels.

These are teaching aids. They are deliberately readable and deliberately imperfect — demo 06 reports what they miss.

## KQL

[`kql/agent-hunting.kql`](kql/agent-hunting.kql) — the inventory and hunting queries from demos 04 and 05.
