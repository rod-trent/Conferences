# Demo 06 — Red-Team Your Agent

Slide 30 · runs offline, standard library only · also on the [demo site](../../web/)

Runs a 14-item corpus (12 attacks, 2 benign controls) through four layers and reports Attack Success Rate (ASR), the metric the Microsoft Foundry AI Red Teaming Agent uses.

## What it shows

- L1 Prompt Shields user input · L2 Prompt Shields document attacks (off by default in Foundry) · L3 runtime tool-call inspection · L4 least-privilege tool allow-list.
- Strategy names from the AI Red Teaming Agent (Jailbreak, Indirect Jailbreak, AsciiSmuggler, Base64, Crescendo); OWASP LLM Top 10 2025 ids.
- What gets through, on purpose: multi-turn Crescendo, a non-English jailbreak, and a polite injection to a domain with no reputation — with the mitigation for each.

## Run it

```bash
cd demos/06-red-team-your-agent
python red_team_agent.py                     # all four layers
python red_team_agent.py --doc-shields-off   # the Foundry default — watch a fraudulent refund get through
python red_team_agent.py --only L1           # Prompt Shields alone
python red_team_agent.py --verbose           # why each payload matters
python red_team_agent.py --self-test         # 9 checks
```

Add `--fast` to skip the on-stage pacing.

## Note

Use the corpus shape (`attack_corpus.json`) as a starting point for your own regression set, and the AI Red Teaming Agent for the real thing.

Detection logic is a local stand-in for the Microsoft services named (see `../common/`). All data is synthetic.
