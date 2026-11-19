# The Agentic SOC — Experts Live Denmark 2027

**The Agentic SOC: Best Practices for Custom Agents, Role Handoffs, and Why Microsoft Perception Is More Supportable and Cost-Effective**

Rod Trent · Experts Live Denmark 2027 · Bella Center Copenhagen · 9–10 February 2027 · #ELDK27

> AI agents are transforming Security Operations Centers, but building and operating them effectively requires more than just connecting models to tools. This session starts with practical best practices for designing secure, governable agents, then walks through building your own agents for common SOC workflows and the handoffs between specialised roles. It then examines Microsoft Perception and closes with a comparison of the custom-agent path versus Microsoft Perception on supportability, maintenance burden and total cost of ownership.

| | |
|---|---|
| **Deck** | [`SlideDecks/The Agentic SOC - Experts Live Denmark 2027.pptx`](SlideDecks/) — 35 slides, speaker notes on every slide |
| **Demo site** | [eldk2027-demos.vercel.app](https://eldk2027-demos.vercel.app) — every demo runs in the browser |
| **Demos** | [`demos/`](demos/) — six Python demos, standard library only, no tenant needed |
| **Sources** | [`SOURCES.md`](SOURCES.md) — every Microsoft Learn page the content relies on |
| **Before you present** | [`PRE-FLIGHT.md`](PRE-FLIGHT.md) — run order, timing, and the facts to re-check |

## The six demos

| # | Demo | Slide | Shows |
|---|---|---|---|
| 1 | [Design review for SOC agents](demos/01-design-the-agent/) | 10 | Twelve documented controls applied to four agents; rebuilding the worst one without touching its prompt |
| 2 | [Triage, with a human in the loop](demos/02-triage-and-teach/) | 12 | Confidence thresholds, evaluating against the error you can't afford, and the teach-and-conflict-check loop |
| 3 | [The handoff chain](demos/03-hand-off/) | 19 | Triage → investigation → detection engineering → posture remediation, a typed handoff envelope, an approval gate, and four ways it breaks |
| 4 | [The detection engineering agent](demos/04-detection-engineering/) | 20 | Back-testing three candidate rules before asking a human to enable one |
| 5 | [A Microsoft Perception playbook](demos/05-perception-playbook/) | 27 | The documented "Protect against a threat" playbook, Waiting for input, immutable sessions, and the read-only playbook library |
| 6 | [Build vs. buy](demos/06-build-vs-buy/) | 31 | A three-year cost model that keeps Microsoft's published facts separate from your assumptions, and computes a break-even rather than inventing a Perception price |

```bash
python run-all-tests.py     # every self-test, every site variant, and the site drift check
```

All data is synthetic. "Fabrikam Nordic" and its people, agents and incidents are made up. Agent logic is a deterministic local stand-in for the systems named.
