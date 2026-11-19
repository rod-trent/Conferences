#!/usr/bin/env python3
"""
Demo 01 - Design Review for SOC Agents
======================================

Four agents in one (synthetic) SOC: one Microsoft-built, three custom. Each is
reviewed against the controls Microsoft documents for agents, and scored.

The checks, and where they come from on Microsoft Learn:
  ID    its own identity - "Don't create AI agents as plain app registrations"
        (Entra Agent ID best practices); a user-account identity "inherits your
        access and permissions" (Security Copilot agents overview)
  OWN   a sponsor (required when creating an agent identity) and an owner;
        sponsors attest every 6-12 months
  CRED  no client secrets - managed identity or certificates
  LP    least privilege - granted permissions match what the agent uses
  HITL  hard actions (isolate, disable, delete, CA changes) need approval
  EVAL  an evaluation suite with gates that runs on every change
  RED   red-teamed, Attack Success Rate known
  LOOP  an iteration limit ("set iteration limits", Architecture Center)
  KILL  a documented way to stop it
  AUD   actions land in an audit log someone can query
  COST  a consumption cap (overage SCUs can be capped or unlimited)
  LIFE  no dependency with an announced retirement date

    python agent_review.py                          # scorecard for all four
    python agent_review.py --agent "Auto-Containment Bot"
    python agent_review.py --fix "Auto-Containment Bot"   # least-privilege diff
    python agent_review.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

DATA = json.loads((HERE / "agents.json").read_text(encoding="utf-8"))

# (id, weight, title)
CHECKS = [
    ("ID", 15, "Own agent identity"),
    ("OWN", 8, "Sponsor + owner, attested"),
    ("CRED", 7, "No client secrets"),
    ("LP", 15, "Least privilege"),
    ("HITL", 15, "Approval on hard actions"),
    ("EVAL", 10, "Eval suite gates every change"),
    ("RED", 5, "Red-teamed (ASR known)"),
    ("LOOP", 5, "Iteration limit"),
    ("KILL", 5, "Kill switch"),
    ("AUD", 5, "Queryable audit trail"),
    ("COST", 5, "Consumption cap"),
    ("LIFE", 5, "No retiring dependency"),
]


def _days(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def review(agent: dict, data: dict = DATA) -> list[tuple[str, bool, str]]:
    """Return (check id, passed, finding) for every check."""
    today = data["today"]
    hard = set(data["hard_actions"])
    high = set(data["high_privilege"])
    out: list[tuple[str, bool, str]] = []

    ident = agent["identity"]["type"]
    if ident == "entra-agent-id":
        out.append(("ID", True, "Microsoft Entra Agent ID"))
    elif ident == "user-account":
        out.append(("ID", False, f"runs as {agent['identity']['account']} - inherits that person's access"))
    else:
        out.append(("ID", False, "plain app registration - invisible to agent governance"))

    if not agent["sponsor"]:
        out.append(("OWN", False, "no sponsor - nobody is accountable for it"))
    elif not agent["attested"] or _days(agent["attested"], today) > 365:
        out.append(("OWN", False, f"sponsor last attested {agent['attested'] or 'never'} (> 12 months)"))
    else:
        out.append(("OWN", True, f"sponsor {agent['sponsor']}, attested {agent['attested']}"))

    cred = agent["identity"]["credential"]
    out.append(("CRED", "secret" not in cred, cred))

    unused = [p for p in agent["granted"] if p not in agent["used"]]
    risky_unused = [p for p in unused if p in high]
    if unused:
        out.append(("LP", False, f"{len(unused)} unused grant(s): {', '.join(unused)}"
                    + (" - high privilege!" if risky_unused else "")))
    else:
        out.append(("LP", True, f"{len(agent['granted'])} grants, all used"))

    ungated = [a for a in agent["actions"] if a in hard and a not in agent["approval_required"]]
    if ungated:
        out.append(("HITL", False, "no approval before: " + ", ".join(ungated)))
    else:
        gated = [a for a in agent["actions"] if a in hard]
        out.append(("HITL", True, ("approval before: " + ", ".join(gated)) if gated else "takes no hard actions"))

    ev = agent["evaluation"]
    if not ev:
        out.append(("EVAL", False, "no evaluation suite"))
    elif not ev["runs_on_change"]:
        out.append(("EVAL", False, f"{ev['suite']} exists but does not run on change"))
    else:
        gates = "; ".join(f"{k} {v}" for k, v in ev["gates"].items())
        out.append(("EVAL", True, f"{ev['suite']} ({ev['cases']} cases) gates: {gates}"))

    rt = agent["red_team"]
    out.append(("RED", bool(rt), f"ASR {rt['asr']:.0%} on {rt['last_run']}" if rt else "never red-teamed"))

    loop = agent["max_iterations"]
    out.append(("LOOP", bool(loop), f"max {loop} iterations" if loop else "unbounded"))

    out.append(("KILL", bool(agent["kill_switch"]), agent["kill_switch"] or "no documented stop"))

    aud = agent["audit"]
    out.append(("AUD", "audit" in aud.lower() or "history" in aud.lower(), aud))

    budget = agent["budget"]
    out.append(("COST", budget not in ("none",) and "unlimited" not in budget, budget))

    retiring = [(d, data["retirements"][d]) for d in agent["dependencies"] if d in data["retirements"]]
    if retiring:
        out.append(("LIFE", False, "; ".join(f"{d} retires {when}" for d, when in retiring)))
    else:
        out.append(("LIFE", True, "no announced retirements"))
    return out


def score(results: list[tuple[str, bool, str]]) -> int:
    weights = {c[0]: c[1] for c in CHECKS}
    return sum(weights[cid] for cid, good, _ in results if good)


def tier(s: int) -> str:
    return "Ready" if s >= 85 else "Fix first" if s >= 60 else "Do not run"


def find(name: str) -> dict:
    for a in DATA["agents"]:
        if a["name"].lower() == name.lower():
            return a
    raise SystemExit(f"no agent named {name!r}; try one of: " + ", ".join(a["name"] for a in DATA["agents"]))


def scorecard() -> None:
    t.banner("Demo 01 - Design Review for SOC Agents",
             "Fabrikam Nordic SOC  ·  4 agents  ·  12 controls from Microsoft Learn")
    t.synthetic_notice()

    t.step(1, 3, "The inventory - who built what, running as whom")
    for a in DATA["agents"]:
        ident = a["identity"]["type"].replace("-", " ")
        print(f"  {t.bold(a['name']):<34} {t.dim(a['builder'])}")
        print(f"      {t.dim('runs as:')} {ident}")
        print(f"      {t.dim('can:')}     {', '.join(a['actions'])}")
    t.why("Three of the four are custom. Custom Security Copilot agents can't get their own Entra "
          "Agent ID yet - the option is Microsoft-built only - so the builder chose a user account.")

    t.step(2, 3, "Twelve controls, weighted")
    ids = [c[0] for c in CHECKS]
    head = "  " + f"{'agent':<24}" + "".join(f"{i:>5}" for i in ids) + "  score"
    print(t.dim(head))
    worst = None
    for a in DATA["agents"]:
        res = review(a)
        s = score(res)
        cells = "".join((t.green if g else t.red)(f"{'ok' if g else 'X':>5}") for _, g, _ in res)
        col = t.green if s >= 85 else t.yellow if s >= 60 else t.red
        print(f"  {a['name']:<24}{cells}  {col(f'{s:>3}  {tier(s)}')}")
        if worst is None or s < worst[1]:
            worst = (a, s)
    t.why("Weights favour the controls that limit blast radius: identity, least privilege and "
          "approval on hard actions are 45 of the 100 points.")

    t.step(3, 3, f"Why '{worst[0]['name']}' scores {worst[1]}")
    for cid, good, finding in review(worst[0]):
        (t.ok if good else t.fail)(f"{cid:<5} {finding}")
    t.why("Every failure here is a design decision, not a model problem. A better prompt fixes none "
          "of them.")
    t.verdict(f"{sum(1 for a in DATA['agents'] if score(review(a)) >= 85)} of 4 agents are ready. "
              "Design the controls before you design the prompt.", good=False)


def detail(name: str) -> None:
    a = find(name)
    t.banner(f"Demo 01 - {a['name']}", a["builder"])
    t.synthetic_notice()
    print()
    t.say(a["purpose"])
    print()
    t.kv("identity", f"{a['identity']['type']} ({a['identity']['credential']})")
    t.kv("sponsor / owner", f"{a['sponsor'] or '-'} / {a['owner'] or '-'}")
    t.kv("actions", ", ".join(a["actions"]))
    t.kv("approval before", ", ".join(a["approval_required"]) or "-")
    res = review(a)
    t.step(1, 1, "Findings")
    for cid, good, finding in res:
        (t.ok if good else t.fail)(f"{cid:<5} {finding}")
    s = score(res)
    t.verdict(f"{s}/100 - {tier(s)}", good=s >= 85)


def fix(name: str) -> None:
    a = find(name)
    t.banner(f"Demo 01 - least-privilege fix for {a['name']}")
    t.synthetic_notice()
    t.step(1, 2, "Grants versus use (from 30 days of sign-in and audit logs)")
    for p in a["granted"]:
        if p in a["used"]:
            print(f"    {t.green('keep  ')} {p}")
        else:
            print(f"    {t.red('remove')} {p}" + (t.red("   high privilege") if p in DATA["high_privilege"] else ""))
    t.why("An agent that reads untrusted input - emails, alerts, URLs - should be assumed injectable. "
          "Whatever it is granted is what an attacker gets.")
    t.step(2, 2, "The rebuilt design")
    fixed = dict(a)
    fixed.update({
        "identity": {"type": "entra-agent-id", "credential": "managed identity"},
        "sponsor": "soc-manager@fabrikam-nordic.dk", "owner": "secops-platform@fabrikam-nordic.dk",
        "attested": DATA["today"], "granted": list(a["used"]),
        "approval_required": [x for x in a["actions"] if x in DATA["hard_actions"]],
        "evaluation": {"suite": "containment-50", "cases": 50, "gates": {"wrong-entity actions": "0"}, "runs_on_change": True},
        "red_team": {"last_run": DATA["today"], "asr": 0.06}, "max_iterations": 10,
        "kill_switch": "Disable agent identity (sponsor)", "audit": "Purview audit log",
        "budget": "Quota alert at 80%", "dependencies": ["Foundry workflows"],
    })
    before, after = score(review(a)), score(review(fixed))
    for cid, good, finding in review(fixed):
        (t.ok if good else t.fail)(f"{cid:<5} {finding}")
    t.verdict(f"{before} -> {after}. Same model, same prompt.", good=after >= 85)


def self_test() -> int:
    by = {a["name"]: a for a in DATA["agents"]}
    r = []
    res = {cid: g for cid, g, _ in review(by["Phishing Triage Agent"])}
    r.append(("Microsoft-built triage agent passes every control", all(res.values())))
    r.append(("triage agent scores 100", score(review(by["Phishing Triage Agent"])) == 100))
    res = {cid: g for cid, g, _ in review(by["Auto-Containment Bot"])}
    r.append(("app registration fails ID", not res["ID"]))
    r.append(("client secret fails CRED", not res["CRED"]))
    r.append(("ungated isolate/disable fails HITL", not res["HITL"]))
    r.append(("connected-agents dependency fails LIFE", not res["LIFE"]))
    r.append(("Auto-Containment Bot is 'Do not run'", tier(score(review(by["Auto-Containment Bot"]))) == "Do not run"))
    res = {cid: g for cid, g, _ in review(by["Nordlys Enrichment"])}
    r.append(("user-account identity fails ID", not res["ID"]))
    r.append(("unused Security Administrator fails LP", not res["LP"]))
    res = {cid: g for cid, g, _ in review(by["Detection Drafter"])}
    r.append(("attestation > 12 months fails OWN", not res["OWN"]))
    r.append(("gated 'enable custom detection' passes HITL", res["HITL"]))
    r.append(("weights sum to 100", sum(c[1] for c in CHECKS) == 100))
    t.banner("Demo 01 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--agent", help="show one agent's findings")
    p.add_argument("--fix", metavar="AGENT", help="show the least-privilege rebuild for one agent")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.agent:
        detail(a.agent)
    elif a.fix:
        fix(a.fix)
    else:
        scorecard()
    return 0


if __name__ == "__main__":
    sys.exit(main())
