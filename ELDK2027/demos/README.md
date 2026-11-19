# Demos

Six demos, one story. One incident runs through demos 02–05: an AiTM link in a compromised partner's SharePoint share.

| # | Folder | Script | Self-test |
|---|---|---|---|
| 1 | [01-design-the-agent](01-design-the-agent/) | `agent_review.py` | 12 checks |
| 2 | [02-triage-and-teach](02-triage-and-teach/) | `triage_agent.py` | 10 checks |
| 3 | [03-hand-off](03-hand-off/) | `soc_handoffs.py` | 11 checks |
| 4 | [04-detection-engineering](04-detection-engineering/) | `detection_agent.py` | 9 checks |
| 5 | [05-perception-playbook](05-perception-playbook/) | `perception_playbook.py` | 10 checks |
| 6 | [06-build-vs-buy](06-build-vs-buy/) | `build_vs_buy.py` | 10 checks |

Everything is Python standard library: no packages, no network, no tenant. Each script takes `--fast` (no on-stage pacing) and `--self-test`. `common/term.py` prints the output markers the demo site pauses on: `STEP n/N`, `>> WHY THIS MATTERS:`, `REQUIRES HUMAN APPROVAL`, `[handoff]`, and `VERDICT:`.

```bash
python ../run-all-tests.py
```
