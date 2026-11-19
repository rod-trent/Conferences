# Demo 01 — Design Review for SOC Agents

Slide 10 · runs offline, standard library only · also on the [demo site](https://eldk2027-demos.vercel.app/?demo=design)

Four agents in one SOC: one Microsoft-built and three custom. Each is checked against twelve controls Microsoft documents for agents, and scored.

## What it shows

- **Identity.** Each agent should have its own Microsoft Entra Agent ID, not a plain app registration or someone's user account. Custom Security Copilot agents can't get one yet.
- **Ownership.** A sponsor (required for an agent identity) and an owner, re-attested every 6–12 months.
- **Credentials.** Managed identity or a certificate, not a client secret.
- **Least privilege.** What the agent is granted, compared with what it actually uses.
- **Approval on hard actions.** Isolate, disable, delete, Conditional Access changes, enabling a detection.
- **Evaluation.** A suite with gates that runs on every change, plus red-teaming with a known Attack Success Rate.
- **Operations.** An iteration limit, a kill switch, a queryable audit trail and a consumption cap.
- **Lifecycle.** No dependency with an announced retirement. Two land on 31 March 2027.

## Run it

```bash
cd demos/01-design-the-agent
python agent_review.py                                  # scorecard
python agent_review.py --agent "Nordlys Enrichment"     # one agent's findings
python agent_review.py --fix "Auto-Containment Bot"     # least-privilege rebuild: 0 -> 100
python agent_review.py --self-test                      # 12 checks
```

Edit `agents.json` to review your own agents.

All data is synthetic. The agent logic is a deterministic local stand-in for the systems named.
