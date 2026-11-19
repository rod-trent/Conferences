# Workplace Ninjas US 2027 — Rod Trent

[![WPNinjas US 2027](https://img.shields.io/badge/Workplace%20Ninjas%20US-2027-FF7A2F?style=for-the-badge)](https://workplaceninjas.us/)
[![Runs offline](https://img.shields.io/badge/demos-run%20offline-5AD18F?style=for-the-badge)](demos/README.md)

**11–13 January 2027 · The Scott Resort & Spa, Scottsdale, AZ**

Slide deck, demo code and a browser demo site for one session. Everything here
runs offline — no tenant, no Azure, no network, no dependencies. Read the code
before you point any of it at a production tenant.

---

## 🛡️ Defender for Agents: Extending Threat Protection to Autonomous Workflows

AI agents interact with enterprise data in ways traditional applications never
could. This session demonstrates how Microsoft Defender capabilities extend to
agent runtime protection, including detection of jailbreak and prompt injection
attacks targeting autonomous workflows.

📊 **Deck:** [`SlideDecks/Defender for Agents - WPNinjas US 2027.pptx`](SlideDecks/) — 33 slides, speaker notes on every one
📁 **Demos:** [`demos/`](demos/) · 🌐 **Browser demo site:** [`web/`](web/) · 🔎 **KQL:** [`demos/kql/agent-hunting.kql`](demos/kql/agent-hunting.kql)

**What you will learn**

- **Threat model** — apps answer, agents act. For autonomous workflows the attack
  that matters is the document attack (XPIA): the attacker never talks to your
  agent, they write something it will read.
- **Shield the model** — Prompt Shields annotations, Foundry guardrail intervention
  points (user input, tool call, tool response, output), and the Defender for AI
  Services alerts that name what happened exactly.
- **Stop the tool call** — Defender real-time protection inspects a proposed tool
  invocation before it runs. Default rules audit; custom rules block; only agents
  with a Microsoft Entra agent ID can be scoped; a late verdict fails open by default.
- **The agent on your laptop** — Defender for Endpoint AI agent runtime protection
  for local coding agents, in Block, Audit and Disabled.
- **Know, hunt, prove** — agent inventory and risk, identity for agents, hunting
  across `AgentsInfo` / `BehaviorInfo` / `CloudAppEvents`, and red teaming with
  Attack Success Rate.

| # | Demo | What it does |
|---|------|--------------|
| 1 | [Shield the Model, Alert the SOC](demos/01-shield-the-model/) | Jailbreak, ASCII smuggling and a poisoned grounding doc through a Prompt Shields stand-in; the Defender for AI Services alert by its exact name, with and without end-user context |
| 2 | [Stop the Tool Call](demos/02-stop-the-tool-call/) | A Copilot Studio agent reads a poisoned vendor email; the SendEmail call is blocked before it runs — then audit-only, no Entra agent ID, and the one-second fail-open |
| 3 | [The Agent on Your Laptop](demos/03-agent-on-the-endpoint/) | A coding agent reads a README with an invisible instruction; endpoint runtime protection in Block, Audit and Disabled, plus a documented preview issue |
| 4 | [Find Every Agent](demos/04-find-every-agent/) | An `AgentsInfo` export scored into risk levels and risk indicators, plus the protection gaps posture does not show |
| 5 | [Hunt the Agent Kill Chain](demos/05-hunt-the-agent-kill-chain/) | Five advanced hunting queries that find the audited tool call that leaked, pivot on the attacker's IP, and trace it to posture debt |
| 6 | [Red-Team Your Agent](demos/06-red-team-your-agent/) | Twelve attacks and two benign controls through four layers, scored as Attack Success Rate — including what gets through |

### Quick start

```bash
git clone https://github.com/rod-trent/Conferences.git
cd Conferences/WPNinjas2027
python run-all-tests.py          # 6 self-test suites, 34 site variants, drift check — ~12 s
python demos/02-stop-the-tool-call/runtime_protection.py --rule audit
```

Python 3.10+ standard library only.

### ▶ Run them in a browser

[`web/`](web/) is a static site that runs these demos **in the browser** —
real Python compiled to WebAssembly (Pyodide), executing in the tab, beside the
deck. Playback pauses at every `WHY THIS MATTERS` line so you can talk over it;
each demo's flags are buttons; `?demo=toolcall&v=1` deep-links straight to a
variant. If the venue network dies it falls back to transcripts baked from the
same code, and a service worker keeps it working offline once loaded.
See [`web/README.md`](web/README.md) to run it locally or deploy it.

### Presenting?

Start with **[PRE-FLIGHT.md](PRE-FLIGHT.md)** — run order, timings, the facts most
likely to have changed by January, and the checklist for the morning of.

### Accuracy

Product names, settings paths, alert names, table names and dates come from
Microsoft Learn, checked **19 November 2026**. Every page used is listed in
**[SOURCES.md](SOURCES.md)**. This area moved a lot in 2026 — re-check the
items flagged in PRE-FLIGHT.md the week of the event.

The demos' **detection logic is a local, readable stand-in** for the Microsoft
services named. It shows the flow — prompt in, annotation out, tool call judged,
alert raised — offline. It is not the product, and the demos say so on screen.
All data is synthetic: "Contoso Outdoors", its agents, people and incidents are
fabricated.

### Repository layout

```
WPNinjas2027/
├── SlideDecks/          the deck (.pptx)
├── deck/build/          deck generator (pptxgenjs) and its art
├── demos/
│   ├── common/          shared terminal helpers + Prompt Shields / runtime stand-ins
│   ├── 01-…  06-…       the six demos, each with a README
│   └── kql/             paste-ready hunting queries
├── web/                 browser demo site (build.py + public/)
├── run-all-tests.py
├── PRE-FLIGHT.md
└── SOURCES.md
```
