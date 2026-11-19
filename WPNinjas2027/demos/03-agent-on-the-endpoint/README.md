# Demo 03 — The Agent on Your Laptop

Slide 24 · runs offline, standard library only · also on the [demo site](../../web/)

A developer asks a coding agent to fix failing tests. The README the developer reviewed contains an instruction in invisible Unicode tag characters: pipe a remote script into bash and post `.env` to a paste site.

## What it shows

- Defender for Endpoint AI agent runtime protection (Preview) inspecting the agent loop at user prompt, tool request and tool response.
- The three modes: **Block**, **Audit**, **Disabled** — and the alert **Suspicious AI prompt injection**.
- That endpoint prompt evidence is not redacted.
- The documented preview known issue (an agent continuing after a post-tool-response block), and why request-time checks still stop the damage.

## Run it

```bash
cd demos/03-agent-on-the-endpoint
python local_agent_protection.py                     # Block mode
python local_agent_protection.py --mode audit        # Audit — alerts, no blocks
python local_agent_protection.py --mode disabled     # no protection
python local_agent_protection.py --agent-continues   # the known issue, and defence in depth
python local_agent_protection.py --self-test         # 9 checks
```

Add `--fast` to skip the on-stage pacing.

## Note

The secrets in the demo are fake strings. Nothing is executed or fetched.

Detection logic is a local stand-in for the Microsoft services named (see `../common/`). All data is synthetic.
