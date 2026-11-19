#!/usr/bin/env python3
"""
Demo 03 - The Handoff Chain
===========================

Four role agents work one incident end to end:

    Triage  ->  Investigation  ->  Detection Engineering  ->  Posture Remediation

The incident continues Demo 02: a partner tenant was compromised and its
"Q1 board pack" share chained to an adversary-in-the-middle (AiTM) sign-in page.
Two Fabrikam Nordic users entered their passwords. The attacker replays their
session tokens from two proxy addresses.

What carries the work between agents is a typed handoff envelope (schema,
entities, evidence references, a version number). The variants break it the way
multi-agent systems really break - each one a pitfall the Azure Architecture
Center's "AI agent orchestration patterns" guidance names:

    python soc_handoffs.py                # structured envelope, approval gate
    python soc_handoffs.py --free-text    # handoff as a prose summary - an entity is lost
    python soc_handoffs.py --loop         # two agents hand back and forth - hop limit
    python soc_handoffs.py --race         # two writers, no version check - lost update
    python soc_handoffs.py --no-gate      # remediation acts without approval
    python soc_handoffs.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

ATTACKER_IP = "203.0.113.77"
ATTACKER_IP_2 = "203.0.113.91"      # AiTM kits rotate proxy nodes
HOP_LIMIT = 6

USERS = {
    "freja.nielsen@fabrikam-nordic.dk": {"name": "Freja Nielsen", "dept": "Finance"},
    "jonas.berg@fabrikam-nordic.dk": {"name": "Jonas Berg", "dept": "Procurement"},
    "svc-payroll@fabrikam-nordic.dk": {"name": "Payroll service account", "dept": "HR systems",
                                        "impact": "runs the 02:00 payroll batch for 1,400 employees"},
}

# The evidence the agents can query. Each row has an id so envelopes can cite it.
SIGNINS = [
    {"id": "S-1", "user": "freja.nielsen@fabrikam-nordic.dk", "ip": "198.51.100.20", "app": "Outlook", "note": "office"},
    {"id": "S-2", "user": "freja.nielsen@fabrikam-nordic.dk", "ip": ATTACKER_IP, "app": "OfficeHome", "note": "token replay"},
    {"id": "S-3", "user": "jonas.berg@fabrikam-nordic.dk", "ip": ATTACKER_IP_2, "app": "SharePoint", "note": "token replay"},
    {"id": "S-4", "user": "svc-payroll@fabrikam-nordic.dk", "ip": ATTACKER_IP, "app": "Payroll API",
     "note": "failed - password spray, MFA not satisfied"},
]
EVENTS = [
    {"id": "X-1", "user": "freja.nielsen@fabrikam-nordic.dk", "action": "New-InboxRule",
     "detail": "move mail containing 'invoice' to RSS Feeds"},
    {"id": "X-2", "user": "jonas.berg@fabrikam-nordic.dk", "action": "FileDownloaded",
     "detail": "Vendor bank details.xlsx"},
]

REQUIRED = ["schema", "incident", "version", "from", "to", "hop", "entities", "findings", "evidence"]


# ---------------------------------------------------------------------------
# The handoff contract
# ---------------------------------------------------------------------------

def envelope(src: str, dst: str, prev: dict | None = None, **changes) -> dict:
    env = copy.deepcopy(prev) if prev else {
        "schema": "soc.handoff/v1", "incident": "INC-4471", "version": 0, "hop": 0,
        "entities": {"users": [], "ips": [], "urls": []}, "findings": [], "evidence": [],
        "requested_action": None,
    }
    env.update({"from": src, "to": dst, "hop": env["hop"] + 1, "version": env["version"] + 1})
    for k, v in changes.items():
        env[k] = v
    return env


def validate(env: dict) -> list[str]:
    """Receiver-side validation: 'validate each agent's output before passing it on'."""
    problems = [f"missing field '{f}'" for f in REQUIRED if f not in env]
    if not problems:
        if not env["entities"]["users"]:
            problems.append("no user entities")
        known = {r["id"] for r in SIGNINS + EVENTS} | {"E-1017"}
        problems += [f"evidence {e} does not exist" for e in env["evidence"] if e not in known]
    return problems


# ---------------------------------------------------------------------------
# The four agents (deterministic stand-ins)
# ---------------------------------------------------------------------------

def triage_agent() -> dict:
    """Alert E-1017 reopened by an analyst; two users clicked the share link."""
    return envelope("Triage", "Investigation",
                    entities={"users": ["freja.nielsen@fabrikam-nordic.dk", "jonas.berg@fabrikam-nordic.dk"],
                              "ips": [], "urls": ["hxxps://kystlogistik-sharepoint.example/board-pack"]},
                    findings=["E-1017 is a true positive: AiTM link inside a genuine partner share",
                              "2 users clicked the link (Safe Links click data)"],
                    evidence=["E-1017"])


def triage_free_text() -> str:
    return ("Reopened E-1017 as a true positive - the partner share links to an AiTM page. "
            "Freja Nielsen in Finance clicked it and entered her password; someone from "
            "procurement may have clicked too. Please investigate.")


def entities_from_text(text: str) -> list[str]:
    """What an LLM-style extractor can resolve from prose: names it can map to a UPN."""
    found = []
    for upn, u in USERS.items():
        if u["name"] in text:
            found.append(upn)
    return found


def investigation_agent(env: dict) -> dict:
    users = env["entities"]["users"]
    # Suspicious sign-ins for the users we were handed (Entra ID Protection flags the replays).
    s = [r for r in SIGNINS if r["user"] in users and r["note"] == "token replay"]
    ips = sorted({r["ip"] for r in s})
    x = [r for r in EVENTS if r["user"] in users]
    # Pivot: who else did those attacker IPs touch?
    pivot = sorted({r["user"] for r in SIGNINS if r["ip"] in ips} - set(users))
    findings = env["findings"] + [f"token replay: {r['user'].split('@')[0]} from {r['ip']}" for r in s]
    findings += [f"{r['action']} by {r['user'].split('@')[0]}: {r['detail']}" for r in x]
    if pivot:
        findings.append(f"IP pivot: {', '.join(ips)} also tried {', '.join(p.split('@')[0] for p in pivot)}")
    ents = copy.deepcopy(env["entities"])
    ents["ips"] = sorted(set(ents["ips"]) | set(ips))
    ents["related_accounts"] = pivot
    return envelope("Investigation", "Detection Engineering", env, entities=ents, findings=findings,
                    evidence=env["evidence"] + [r["id"] for r in s + x])


def detection_agent(env: dict) -> dict:
    rule = {
        "name": "AiTM token replay followed by inbox rule",
        "kql": ("let replay = SigninLogs | where IPAddress in (dynamic(" + json.dumps(env["entities"]["ips"]) + ")) "
                "| project UserPrincipalName, SigninTime=TimeGenerated;\n"
                "OfficeActivity | where Operation == 'New-InboxRule' "
                "| join kind=inner replay on $left.UserId == $right.UserPrincipalName "
                "| where TimeGenerated between (SigninTime .. SigninTime + 1h)"),
        "state": "draft - disabled until back-tested (Demo 04)",
    }
    return envelope("Detection Engineering", "Posture Remediation", env,
                    findings=env["findings"] + [f"draft detection: {rule['name']}"], detection=rule)


def remediation_plan(env: dict) -> list[dict]:
    plan = []
    for u in env["entities"]["users"]:
        plan.append({"action": "revoke sessions + reset password", "target": u, "hard": True})
    for u in env["entities"].get("related_accounts", []):
        plan.append({"action": "disable user", "target": u, "hard": True,
                     "impact": USERS[u].get("impact")})
    plan.append({"action": "CA policy: token protection (Exchange, SharePoint)",
                 "target": "Finance + Procurement", "hard": True})
    plan.append({"action": "block URL indicator", "target": env["entities"]["urls"][0], "hard": False})
    return plan


def approve(step: dict) -> tuple[bool, str]:
    """The analyst at the gate. Rejects anything that would stop the business."""
    if step.get("impact"):
        return False, f"Reject - {step['impact']}. Suggest: reset password + require MFA re-registration instead"
    return True, "Approve"


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def show_env(env: dict, keys=("schema", "incident", "version", "hop", "from", "to")) -> None:
    print("    " + t.dim("  ".join(f"{k}={env[k]}" for k in keys)))
    print("    " + t.dim("users=") + ", ".join(u.split("@")[0] for u in env["entities"]["users"])
          + t.dim("   evidence=") + ", ".join(env["evidence"]))


def chain(free_text: bool = False, gate: bool = True, quiet: bool = False) -> dict:
    """Run the four-agent chain. Returns the outcome for tests."""
    say = (lambda *a, **k: None) if quiet else None
    total = 5
    if not quiet:
        t.step(1, total, "Triage hands off to Investigation")
    if free_text:
        text = triage_free_text()
        users = entities_from_text(text)
        env = envelope("Triage", "Investigation",
                       entities={"users": users, "ips": [], "urls": ["hxxps://kystlogistik-sharepoint.example/board-pack"]},
                       findings=["(from prose) " + text[:60] + "..."], evidence=["E-1017"])
        if not quiet:
            t.handoff("Triage", "Investigation", "as free text")
            t.say(t.dim('"' + text + '"'), 6)
            t.kv("entities extracted", ", ".join(u.split("@")[0] for u in users) or "(none)")
            t.why("'Someone from procurement' is not an entity. The next agent can only investigate "
                  "what it can resolve, and it resolved one user.")
    else:
        env = triage_agent()
        if not quiet:
            t.handoff("Triage", "Investigation", "soc.handoff/v1")
            show_env(env)
    problems = validate(env)
    if not quiet:
        (t.ok if not problems else t.fail)("receiver validation: " + ("envelope accepted" if not problems else "; ".join(problems)))

    if not quiet:
        t.step(2, total, "Investigation works the entities it was handed")
    n_before = len(env["findings"])
    env = investigation_agent(env)
    if not quiet:
        t.tool("query SigninLogs", f"users={len(env['entities']['users'])}, risky sign-ins")
        t.tool("query OfficeActivity", "mailbox and file activity")
        t.tool("pivot on attacker IPs", ", ".join(env["entities"]["ips"]))
        for f in env["findings"][n_before:]:
            print("    - " + f)
        t.handoff("Investigation", "Detection Engineering", f"v{env['version']}, {len(env['evidence'])} evidence refs")
        if not free_text:
            t.why("Evidence references travel with the claim. The next agent - or a human - can "
                  "check S-2 and X-1 instead of trusting a summary.")

    if not quiet:
        t.step(3, total, "Detection Engineering drafts a rule")
    env = detection_agent(env)
    if not quiet:
        t.kv("rule", env["detection"]["name"])
        t.kv("state", env["detection"]["state"])
        t.handoff("Detection Engineering", "Posture Remediation", f"v{env['version']}")

    if not quiet:
        t.step(4, total, "Posture Remediation proposes a plan")
    plan = remediation_plan(env)
    if not quiet:
        for p in plan:
            mark = t.yellow("hard") if p["hard"] else t.dim("soft")
            print(f"    [{mark}] {p['action']}  ->  {p['target'].split('@')[0]}")

    if not quiet:
        t.step(5, total, "Execute" + (" - through the approval gate" if gate else " - no gate"))
    executed, rejected = [], []
    for p in plan:
        if gate and p["hard"]:
            if not quiet:
                t.gate(f"{p['action']} -> {p['target'].split('@')[0]}")
            ok_, why = approve(p)
            if ok_:
                executed.append(p)
                if not quiet:
                    t.allow(why)
            else:
                rejected.append(p)
                if not quiet:
                    t.block(why)
        else:
            executed.append(p)
            if not quiet:
                (t.warn if p.get("impact") else t.allow)(f"{p['action']} -> {p['target'].split('@')[0]}"
                                                          + (f"  ({p['impact']})" if p.get("impact") else ""))
    compromised = {r["user"] for r in SIGNINS if r["note"] == "token replay"}
    revoked = {p["target"] for p in executed if p["action"].startswith("revoke")}
    outage = [p for p in executed if p.get("impact")]
    return {"env": env, "plan": plan, "executed": executed, "rejected": rejected,
            "still_compromised": sorted(compromised - revoked), "outage": outage}


def run(a) -> None:
    title = {"free": "free-text handoff", "nogate": "no approval gate"}.get(
        "free" if a.free_text else "nogate" if a.no_gate else "", "structured envelope + approval gate")
    t.banner("Demo 03 - The Handoff Chain", f"Triage -> Investigation -> Detection -> Remediation  ·  {title}")
    t.synthetic_notice()
    o = chain(free_text=a.free_text, gate=not a.no_gate)
    print()
    if o["still_compromised"]:
        for u in o["still_compromised"]:
            t.fail(f"{u.split('@')[0]} still has a live attacker session")
        t.why("Every agent did its own job correctly. The incident failed in the gap between "
              "two of them. Handoffs are where multi-agent systems break.")
        t.verdict("Contained 1 of 2 accounts. The attacker keeps Jonas's session.", good=False)
    elif o["outage"]:
        for p in o["outage"]:
            t.fail(f"{p['target'].split('@')[0]} disabled - {p['impact']}")
        t.why("The agent was right that the attacker touched the service account, and wrong about "
              "what to do. Scope human approval to the hard actions; that is where judgment lives.")
        t.verdict("Attacker contained - and payroll fails tonight.", good=False)
    else:
        t.ok("both compromised accounts revoked; payroll account protected without an outage")
        t.why("Typed envelope, receiver validation, evidence refs, and approval on hard actions only. "
              "The URL block went through without anyone being asked.")
        t.verdict("Contained, with a draft detection and a posture fix queued.")


def loop_demo(limit: int = HOP_LIMIT, quiet: bool = False) -> dict:
    """Investigation wants a detection to confirm; Detection wants more evidence first."""
    if not quiet:
        t.banner("Demo 03 - Handoff loop", f"Investigation <-> Detection Engineering  ·  hop limit {limit}")
        t.synthetic_notice()
        t.step(1, 2, "Two agents, each waiting for the other")
    env = triage_agent()
    hops = 0
    a, b = "Investigation", "Detection Engineering"
    while True:
        hops += 1
        if hops > limit:
            break
        reason = "need a detection to confirm scope" if a == "Investigation" else "need more evidence to tune"
        if not quiet:
            t.handoff(a, b, f"hop {hops}: {reason}")
        a, b = b, a
    if not quiet:
        t.why("The Architecture Center names it: an 'infinite handoff loop'. Each agent is behaving "
              "reasonably; together they burn tokens forever.")
        t.step(2, 2, "The orchestrator enforces the hop limit")
        t.block(f"hop {limit + 1} refused - limit {limit}")
        t.gate("escalate INC-4471 to the on-call analyst with both agents' last envelopes")
        t.verdict("Bounded. A hop limit turns an infinite loop into a human escalation.")
    return {"hops": hops - 1, "escalated": True}


def race_demo(versioned: bool, quiet: bool = False) -> dict:
    """Triage merges a new user into the incident while Investigation writes findings."""
    store = {"version": 1, "users": ["freja.nielsen@fabrikam-nordic.dk"], "findings": []}
    inv_copy = copy.deepcopy(store)         # Investigation reads v1
    tri_copy = copy.deepcopy(store)         # Triage reads v1
    tri_copy["users"].append("jonas.berg@fabrikam-nordic.dk")
    tri_copy["version"] += 1
    store = tri_copy                        # Triage writes v2 first
    inv_copy["findings"].append("token replay for freja")
    inv_copy["version"] += 1
    conflict = versioned and inv_copy["version"] - 1 != store["version"]
    if conflict:
        # 409: re-read, re-apply, write v3.
        merged = copy.deepcopy(store)
        merged["findings"] += inv_copy["findings"]
        merged["version"] += 1
        store = merged
    else:
        store = inv_copy                    # last writer wins
    if not quiet:
        t.kv("Triage writes", "v2: + jonas.berg")
        t.kv("Investigation writes", f"based on v1{' -> 409 Conflict, re-read v2, write v3' if conflict else ' (no check)'}")
        t.kv("incident now", f"v{store['version']}  users=" + ", ".join(u.split('@')[0] for u in store["users"]))
    return {"users": store["users"], "conflict": conflict}


def race(quiet: bool = False) -> None:
    t.banner("Demo 03 - Two writers, one incident", "Shared mutable state - the concurrent-pattern pitfall")
    t.synthetic_notice()
    t.step(1, 2, "Last writer wins")
    o = race_demo(versioned=False)
    t.fail("jonas.berg is gone from the incident - nobody will investigate him")
    t.why("Both agents were right. The store kept only the later write. Avoid shared mutable state "
          "between concurrent agents, or make every write conditional on the version you read.")
    t.step(2, 2, "Same race, with a version check (etag / checkpoint)")
    o = race_demo(versioned=True)
    t.ok("conflict detected, re-read, merged - both users and the finding survive")
    t.verdict("Version every write. It is one integer, and it is the difference.")


def self_test() -> int:
    r = []
    o = chain(quiet=True)
    r.append(("structured run contains both compromised accounts", not o["still_compromised"]))
    r.append(("structured run causes no outage", not o["outage"]))
    r.append(("gate rejects disabling the payroll service account",
              any(p["target"].startswith("svc-payroll") for p in o["rejected"])))
    r.append(("URL block (soft action) runs without approval",
              any(p["action"] == "block URL indicator" for p in o["executed"])))
    r.append(("triage envelope passes validation", not validate(triage_agent())))
    r.append(("validation rejects an envelope with a fake evidence id",
              bool(validate({**triage_agent(), "evidence": ["S-99"]}))))
    o = chain(free_text=True, quiet=True)
    r.append(("free-text handoff loses jonas.berg", o["still_compromised"] == ["jonas.berg@fabrikam-nordic.dk"]))
    o = chain(gate=False, quiet=True)
    r.append(("no gate -> payroll account disabled", bool(o["outage"])))
    r.append(("loop stops at the hop limit", loop_demo(quiet=True)["hops"] == HOP_LIMIT))
    r.append(("race without version check loses a user", len(race_demo(False, quiet=True)["users"]) == 1))
    r.append(("race with version check keeps both users", len(race_demo(True, quiet=True)["users"]) == 2))
    t.banner("Demo 03 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--free-text", action="store_true")
    p.add_argument("--no-gate", action="store_true")
    p.add_argument("--loop", action="store_true")
    p.add_argument("--race", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.loop:
        loop_demo()
    elif a.race:
        race()
    else:
        run(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
