# Demo 03 — The Handoff Chain

Slide 19 · runs offline, standard library only · also on the [demo site](https://eldk2027-demos.vercel.app/?demo=handoff)

Four role agents work one incident end to end: **Triage → Investigation → Detection Engineering → Posture Remediation**. The incident: a compromised partner tenant's SharePoint share chains to an adversary-in-the-middle page. Two users enter their passwords, and the attacker replays their tokens from two proxy IPs.

## What it shows

The structured run passes a typed handoff envelope between agents: schema, entities, evidence references and a version number. The receiver validates it. Then an approval gate on the hard actions approves revoking both sessions and **rejects** disabling the payroll service account.

The variants break it the ways the Azure Architecture Center's orchestration-pattern guidance warns about:

| Variant | Pitfall | Result |
|---|---|---|
| `--free-text` | Lossy handoff | A prose summary loses the second user; the attacker keeps that session |
| `--loop` | Infinite handoff loop | The hop limit stops it and escalates to a human |
| `--race` | Shared mutable state | Last writer wins and a user disappears; a version check fixes it |
| `--no-gate` | Ungated hard action | The attacker is contained, and payroll fails tonight |

## Run it

```bash
cd demos/03-hand-off
python soc_handoffs.py               # structured envelope + approval gate
python soc_handoffs.py --free-text
python soc_handoffs.py --loop
python soc_handoffs.py --race
python soc_handoffs.py --no-gate
python soc_handoffs.py --self-test   # 11 checks
```

All data is synthetic. The agent logic is a deterministic local stand-in for the systems named.
