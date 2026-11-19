#!/usr/bin/env python3
"""
Demo 05 - A Microsoft Perception Playbook
=========================================

The same threat, run the other way: not five agents you wired together, but a
Microsoft-managed playbook that coordinates red, blue and green team agents.

What this models is what Microsoft Learn documents (checked 19 Nov 2026):
  - agents by team. Red: Recon Agent (read-only, Azure environments only).
    Blue: Triage, Threat Intelligence, Attack Investigation, Detection
    Authoring. Green: Posture Prioritization, Identity Risk Reduction, Risk
    Reduction.
  - playbooks are "reusable templates that define how agents should respond to
    specific scenarios"; they are preset by Microsoft and the list is read-only
    ("You can't create custom playbooks in this release").
  - a playbook runs only when every agent it needs is enabled.
  - the documented "Protect against a threat" sequence: Threat Intelligence ->
    Recon -> Posture Prioritization -> Detection Authoring / Attack Investigation,
    each agent's output becoming "a structured input for the next agent".
  - sessions are "immutable records that serve as an audit trail"; at an
    approval gate the session shows "Waiting for input" with Approve, Reject,
    Suggest an alternative, and Stop (Stop cannot be undone).
  - each agent gets a Microsoft Entra Agent ID at setup; actions are recorded in
    Microsoft Purview audit logs.

The agents' reasoning below is a deterministic stand-in. Perception's internals
are not public; the flow, names and controls are Microsoft's.

    python perception_playbook.py                         # approve at the gate
    python perception_playbook.py --decision suggest      # suggest an alternative
    python perception_playbook.py --decision reject
    python perception_playbook.py --decision stop
    python perception_playbook.py --disable "Recon Agent" # a required agent is off
    python perception_playbook.py --custom                # try to write your own playbook
    python perception_playbook.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

AGENTS = {
    "Recon Agent": "red",
    "Triage Agent": "blue",
    "Threat Intelligence Agent": "blue",
    "Attack Investigation Agent": "blue",
    "Detection Authoring Agent": "blue",
    "Posture Prioritization Agent": "green",
    "Identity Risk Reduction Agent": "green",
    "Risk Reduction Agent": "green",
}
TEAM_COLOUR = {"red": t.red, "blue": t.blue, "green": t.green}

PLAYBOOKS = [
    "Triage alert", "Protect against a threat", "Investigate attack", "Extract threat intelligence",
    "Identify attack paths", "Plan for posture remediation", "Assess identity risks",
    "Reduce credential phishing risk", "Close identity attack paths used in your environment",
]

PROTECT = {
    "name": "Protect against a threat",
    "sequence": ["Threat Intelligence Agent", "Recon Agent", "Posture Prioritization Agent",
                 "Detection Authoring Agent", "Attack Investigation Agent"],
}

REPORT = ("Threat report TR-2027-014: an AiTM phishing kit delivered through compromised partner "
          "SharePoint tenants is targeting Nordic logistics and finance teams.")


class Session:
    """Append-only session record. The hash chain illustrates 'immutable'; it is not
    how Perception stores sessions (that is not documented)."""

    def __init__(self, playbook: str):
        self.playbook = playbook
        self.entries: list[dict] = []
        self.status = "Running"

    def add(self, actor: str, kind: str, payload: dict) -> dict:
        prev = self.entries[-1]["hash"] if self.entries else "0" * 16
        body = json.dumps({"actor": actor, "kind": kind, "payload": payload, "prev": prev}, sort_keys=True)
        e = {"n": len(self.entries) + 1, "actor": actor, "kind": kind, "payload": payload, "prev": prev,
             "hash": hashlib.sha256(body.encode()).hexdigest()[:16]}
        self.entries.append(e)
        return e

    def verify(self) -> bool:
        prev = "0" * 16
        for e in self.entries:
            body = json.dumps({"actor": e["actor"], "kind": e["kind"], "payload": e["payload"], "prev": prev},
                              sort_keys=True)
            if e["prev"] != prev or hashlib.sha256(body.encode()).hexdigest()[:16] != e["hash"]:
                return False
            prev = e["hash"]
        return True


# ---------------------------------------------------------------------------
# Agent stand-ins: each returns the structured output the next one consumes
# ---------------------------------------------------------------------------

def threat_intelligence(_: dict) -> dict:
    return {"ttps": ["T1566.002 Spearphishing Link", "T1557 Adversary-in-the-Middle",
                     "T1550.004 Web Session Cookie", "T1564.008 Email Hiding Rules"],
            "targets": ["Finance", "Procurement"], "source": "TR-2027-014"}


def recon(inp: dict) -> dict:
    return {"scope": "Azure (read-only)",
            "attack_paths": [
                {"from": "Finance user (token theft)", "via": "Key Vault Secrets Officer on kv-payments",
                 "to": "stpaymentsprod (payment files)", "choke_point": "kv-payments"},
                {"from": "svc-legacy-ftp (dormant, password auth)", "via": "Key Vault Secrets Officer on kv-payments",
                 "to": "stpaymentsprod (payment files)", "choke_point": "kv-payments"},
            ],
            "not_covered": ["on-premises SAP payment run", "AWS archive bucket"],
            "ttps": inp["ttps"]}


def posture_prioritization(inp: dict) -> dict:
    return {"priorities": [
        {"rank": 1, "fix": "CA policy: token protection for Finance + Procurement", "breaks_paths": 1},
        {"rank": 2, "fix": "Disable dormant account svc-legacy-ftp", "breaks_paths": 1, "hard": True},
        {"rank": 3, "fix": "Make Key Vault Secrets Officer on kv-payments eligible (PIM), not standing",
         "breaks_paths": 2},
    ], "choke_point": inp["attack_paths"][0]["choke_point"]}


def detection_authoring(inp: dict) -> dict:
    return {"rule": "Risky sign-in, then an inbox rule that hides finance mail", "language": "KQL",
            "state": "proposed"}


def attack_investigation(inp: dict) -> dict:
    return {"already_exploited": True, "incident": "INC-4471", "status": "contained (Demo 03)",
            "new_findings": "none beyond INC-4471"}


IMPL = {
    "Threat Intelligence Agent": threat_intelligence,
    "Recon Agent": recon,
    "Posture Prioritization Agent": posture_prioritization,
    "Detection Authoring Agent": detection_authoring,
    "Attack Investigation Agent": attack_investigation,
}


def gate_decision(decision: str) -> tuple[str, str]:
    return {
        "approve": ("Approved", "disable svc-legacy-ftp"),
        "reject": ("Rejected", "svc-legacy-ftp left enabled; finding stays in the session"),
        "suggest": ("Suggested an alternative",
                    "remove svc-legacy-ftp's Key Vault role instead - a partner still uses it quarterly"),
        "stop": ("Stopped", "session stopped - this cannot be undone"),
    }[decision]


def run_playbook(enabled: set[str], decision: str = "approve", quiet: bool = False) -> dict:
    s = Session(PROTECT["name"])
    missing = [a for a in PROTECT["sequence"] if a not in enabled]
    if missing:
        s.status = "Not started"
        return {"session": s, "missing": missing, "ran": [], "outcome": None}

    s.add("Analyst", "start", {"playbook": PROTECT["name"], "input": "TR-2027-014"})
    data: dict = {}
    ran = []
    total = len(PROTECT["sequence"]) + 1
    for i, agent in enumerate(PROTECT["sequence"], 1):
        team = AGENTS[agent]
        if not quiet:
            t.step(i, total, f"{agent}  ({team} team)")
        out = IMPL[agent](data)
        data = {**data, **out}
        e = s.add(agent, "output", out)
        ran.append(agent)
        if not quiet:
            _show(agent, out)
            nxt = PROTECT["sequence"][i] if i < len(PROTECT["sequence"]) else "Approval gate"
            t.handoff(agent, nxt, f"session entry #{e['n']} {e['hash']}")
            _why(agent)

    # The hard action from Posture Prioritization waits for a human.
    if not quiet:
        t.step(total, total, "Waiting for input")
        t.gate("Disable user account svc-legacy-ftp  (from Posture Prioritization, rank 2)")
        print(t.dim("    options:  Approve  ·  Reject  ·  Suggest an alternative  ·  Stop"))
    status, effect = gate_decision(decision)
    s.add("Analyst", "decision", {"decision": status, "effect": effect})
    if decision == "suggest":
        s.add("Posture Prioritization Agent", "revised", {"fix": "Remove Key Vault Secrets Officer from svc-legacy-ftp",
                                                          "breaks_paths": 1})
        s.add("Analyst", "decision", {"decision": "Approved", "effect": "role removed"})
    s.status = "Stopped" if decision == "stop" else "Completed"
    if not quiet:
        (t.block if decision in ("reject", "stop") else t.allow)(f"{status}: {effect}")
        if decision == "suggest":
            t.tool("Posture Prioritization Agent", "revises the step: remove the role, keep the account")
            t.allow("Approved: role removed, account kept for the partner")
    return {"session": s, "missing": [], "ran": ran, "outcome": status}


def _show(agent: str, out: dict) -> None:
    if agent == "Threat Intelligence Agent":
        t.say(t.dim(REPORT), 4)
        for x in out["ttps"]:
            print("    - " + x)
    elif agent == "Recon Agent":
        t.kv("scope", out["scope"])
        for p in out["attack_paths"]:
            print(f"    - {p['from']}")
            print(f"        -> {p['via']}  -> {p['to']}")
        t.warn("not covered: " + ", ".join(out["not_covered"]))
    elif agent == "Posture Prioritization Agent":
        for p in out["priorities"]:
            hard = t.yellow("  [needs approval]") if p.get("hard") else ""
            print(f"    {p['rank']}. {p['fix']}{hard}")
    elif agent == "Detection Authoring Agent":
        t.kv("proposed rule", out["rule"])
    elif agent == "Attack Investigation Agent":
        t.kv("already exploited?", f"yes - {out['incident']}, {out['status']}")
        t.kv("new findings", out["new_findings"])


def _why(agent: str) -> None:
    text = {
        "Threat Intelligence Agent": "No handoff envelope to design. The playbook defines what passes "
                                     "between agents - in your build, that was Demo 03.",
        "Recon Agent": "Red team, read-only - and Azure only. The on-prem SAP payment run is out of "
                       "scope, and the session says so instead of pretending.",
        "Posture Prioritization Agent": "Ranked by attack paths broken, not by severity label. Rank 3 "
                                        "closes two paths at the choke point.",
        "Detection Authoring Agent": "Same rule Demo 04's custom agent arrived at - without you "
                                     "maintaining the agent that wrote it.",
        "Attack Investigation Agent": "The playbook checks whether the threat has already landed. It has: "
                                      "INC-4471, contained.",
    }[agent]
    t.why(text)


def main_run(a) -> None:
    enabled = set(AGENTS) - set(a.disable or [])
    t.banner("Demo 05 - A Microsoft Perception Playbook",
             f"Playbook: {PROTECT['name']}  ·  decision at the gate: {a.decision}")
    t.synthetic_notice()
    print(t.dim("  Modelled on Microsoft Learn (agentic-security docs). Agent reasoning is a stand-in."))
    o = run_playbook(enabled, a.decision)
    if o["missing"]:
        t.step(1, 1, "Start the playbook")
        for m in o["missing"]:
            t.block(f"{m} is not enabled")
        t.why("A playbook runs only when every agent it needs is enabled. Turning one agent off is a "
              "governance decision with a visible consequence - not a silent gap.")
        t.verdict("Playbook not started. Enable the agent or run a playbook that doesn't need it.", good=False)
        return
    s = o["session"]
    print()
    t.kv("session", f"{s.status}, {len(s.entries)} entries, chain {'intact' if s.verify() else 'BROKEN'}")
    t.kv("audit", "each action also lands in Microsoft Purview audit logs")
    good = o["outcome"] in ("Approved", "Suggested an alternative")
    t.verdict({
        "Approved": "Five agents, one playbook, one human decision - and none of them yours to maintain.",
        "Suggested an alternative": "The human changed the plan, the agent adapted, the record shows both.",
        "Rejected": "Rejected - and the finding is still in the session for the next review.",
        "Stopped": "Stopped. The session is final; the audit trail is not lost.",
    }[o["outcome"]], good=good or o["outcome"] == "Rejected")


def custom() -> None:
    t.banner("Demo 05 - Write your own playbook?", "The trade-off, shown")
    t.synthetic_notice()
    t.step(1, 2, "The playbook library")
    for p in PLAYBOOKS:
        print("    - " + p)
    t.step(2, 2, "Create playbook: 'Vendor bank-detail fraud'")
    t.block("Preset by Microsoft. The playbook list is read-only. You can't create custom playbooks "
            "in this release.")
    t.why("This is the price of 'managed'. Microsoft maintains the agents, prompts, handoffs and "
          "updates - and decides the scenarios. Your vendor-fraud workflow is still a custom build.")
    t.verdict("Buy what is standard. Build only what is yours.", good=True)


def self_test() -> int:
    every = set(AGENTS)
    r = []
    o = run_playbook(every, "approve", quiet=True)
    r.append(("documented sequence runs in order", o["ran"] == PROTECT["sequence"]))
    r.append(("8 agents across red/blue/green", len(AGENTS) == 8 and set(AGENTS.values()) == {"red", "blue", "green"}))
    r.append(("Recon is the only red team agent", [a for a, tm in AGENTS.items() if tm == "red"] == ["Recon Agent"]))
    r.append(("approve -> Completed", o["session"].status == "Completed"))
    r.append(("session hash chain verifies", o["session"].verify()))
    s = o["session"]
    s.entries[2]["payload"]["scope"] = "all clouds"
    r.append(("editing an entry breaks the chain", not s.verify()))
    o = run_playbook(every, "stop", quiet=True)
    r.append(("stop -> Stopped", o["session"].status == "Stopped"))
    o = run_playbook(every, "suggest", quiet=True)
    r.append(("suggest -> revised step recorded and approved",
              any(e["kind"] == "revised" for e in o["session"].entries)))
    o = run_playbook(every - {"Recon Agent"}, quiet=True)
    r.append(("disabled required agent -> playbook not started", o["missing"] == ["Recon Agent"] and not o["ran"]))
    r.append(("9 documented playbooks listed", len(PLAYBOOKS) == 9))
    t.banner("Demo 05 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--decision", choices=["approve", "reject", "suggest", "stop"], default="approve")
    p.add_argument("--disable", action="append", metavar="AGENT", choices=sorted(AGENTS))
    p.add_argument("--custom", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.custom:
        custom()
    else:
        main_run(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
