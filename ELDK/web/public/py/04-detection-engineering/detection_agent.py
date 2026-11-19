#!/usr/bin/env python3
"""
Demo 04 - The Detection Engineering Agent
=========================================

Demo 03 handed Detection Engineering an incident: AiTM token replay, then a
malicious inbox rule. The agent drafts three candidate custom detection rules and
back-tests each one against seven days of (synthetic) tenant telemetry before
anyone is asked to enable one.

    candidate A   IOC rule      the attacker IPs from this incident
    candidate B   broad rule    any new inbox rule after a non-corporate sign-in
    candidate C   behavioural   risky sign-in, then a rule that hides finance mail

The gates (what the agent must prove before it may ask for approval):
    recall      catches every known-bad case in the window
    noise       <= 2 false positives per day
    volume      under the 150-alerts-per-run cap custom detections have (Learn)

Enabling a custom detection is a hard action: the agent creates the rule
disabled and asks a human (Demo 01's HITL control, Demo 03's gate).

    python detection_agent.py                # draft, back-test, gate, ask
    python detection_agent.py --ship-first   # skip the back-test, enable B - the first 24 hours
    python detection_agent.py --kql          # the three candidates as KQL
    python detection_agent.py --self-test
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

DAYS = 7
USERS = 320
CAP_PER_RUN = 150          # custom detection rules: max alerts per run (Microsoft Learn)
MAX_FP_PER_DAY = 2
INCIDENT_IPS = ["203.0.113.77", "203.0.113.91"]
FINANCE_WORDS = ("invoice", "payment", "bank", "faktura")
HIDE_FOLDERS = ("RSS Feeds", "Conversation History", "Archive", "(delete)")

KQL = {
    "A": """// A - IOC rule: the attacker IPs from INC-4471
SigninLogs
| where IPAddress in ("203.0.113.77", "203.0.113.91")
| join kind=inner (OfficeActivity | where Operation == "New-InboxRule")
    on $left.UserPrincipalName == $right.UserId""",
    "B": """// B - broad: any new inbox rule within 1h of a non-corporate sign-in
let corp = dynamic(["198.51.100.0/24"]);
SigninLogs
| where not(ipv4_is_in_any_range(IPAddress, corp))
| project UserPrincipalName, SigninTime = TimeGenerated
| join kind=inner (OfficeActivity | where Operation == "New-InboxRule")
    on $left.UserPrincipalName == $right.UserId
| where TimeGenerated between (SigninTime .. SigninTime + 1h)""",
    "C": """// C - behavioural: risky sign-in, then a rule that hides finance mail
SigninLogs
| where RiskLevelDuringSignIn in ("medium", "high")
| project UserPrincipalName, SigninTime = TimeGenerated
| join kind=inner (
    OfficeActivity
    | where Operation in ("New-InboxRule", "Set-InboxRule")
    | where Parameters has_any ("invoice", "payment", "bank", "faktura")
    | where Parameters has_any ("RSS Feeds", "Conversation History", "Archive", "DeleteMessage")
  ) on $left.UserPrincipalName == $right.UserId
| where TimeGenerated between (SigninTime .. SigninTime + 1h)""",
}


def telemetry(seed: int = 4471) -> list[dict]:
    """Seven days of sign-in -> inbox-rule pairs. Deterministic."""
    rnd = random.Random(seed)
    rows = []
    for day in range(DAYS):
        for _ in range(rnd.randint(30, 38)):                       # benign rule creations per day
            u = f"user{rnd.randrange(USERS):03d}@fabrikam-nordic.dk"
            corp = rnd.random() > 0.55                               # hybrid work: lots of home/mobile IPs
            words = "invoice" if rnd.random() < 0.06 else rnd.choice(["newsletter", "jira", "teams", "build"])
            folder = rnd.choice(["Invoices", "News", "Projects", "Archive" if words != "invoice" else "Invoices"])
            rows.append({"day": day, "hour": rnd.randrange(24), "user": u,
                         "ip": "198.51.100." + str(rnd.randrange(2, 250)) if corp else f"100.{rnd.randrange(64, 127)}.{rnd.randrange(255)}.{rnd.randrange(255)}",
                         "risk": "none", "words": words, "folder": folder, "bad": False})
    # The one benign case that looks like an attack: an AP clerk on holiday, flagged unfamiliar location.
    rows.append({"day": 3, "hour": 9, "user": "anne.lund@fabrikam-nordic.dk", "ip": "100.88.12.4", "risk": "medium",
                 "words": "invoice", "folder": "Archive", "bad": False})
    # Known bad: this incident, and an earlier one from a different AiTM node.
    rows.append({"day": 6, "hour": 10, "user": "freja.nielsen@fabrikam-nordic.dk", "ip": "203.0.113.77",
                 "risk": "high", "words": "invoice", "folder": "RSS Feeds", "bad": True})
    rows.append({"day": 2, "hour": 23, "user": "line.krogh@fabrikam-nordic.dk", "ip": "192.0.2.44",
                 "risk": "high", "words": "payment", "folder": "(delete)", "bad": True})
    return rows


def rule_a(r: dict) -> bool:
    return r["ip"] in INCIDENT_IPS


def rule_b(r: dict) -> bool:
    return not r["ip"].startswith("198.51.100.")


def rule_c(r: dict) -> bool:
    return r["risk"] in ("medium", "high") and r["words"] in FINANCE_WORDS and r["folder"] in HIDE_FOLDERS


RULES = {"A": ("IOC rule", rule_a), "B": ("broad rule", rule_b), "C": ("behavioural rule", rule_c)}


def backtest(rule, rows: list[dict]) -> dict:
    hits = [r for r in rows if rule(r)]
    bad = [r for r in rows if r["bad"]]
    tp = [r for r in hits if r["bad"]]
    fp = [r for r in hits if not r["bad"]]
    per_run: dict[tuple, int] = {}
    for r in hits:
        per_run[(r["day"], r["hour"])] = per_run.get((r["day"], r["hour"]), 0) + 1
    res = {
        "hits": len(hits), "tp": len(tp), "bad": len(bad), "fp": len(fp),
        "fp_per_day": len(fp) / DAYS, "max_per_run": max(per_run.values(), default=0),
        "missed": [r["user"] for r in bad if r not in tp],
    }
    res["gates"] = {
        "recall": res["tp"] == res["bad"],
        "noise": res["fp_per_day"] <= MAX_FP_PER_DAY,
        "volume": res["max_per_run"] < CAP_PER_RUN,
    }
    res["pass"] = all(res["gates"].values())
    return res


def run() -> dict:
    rows = telemetry()
    t.banner("Demo 04 - The Detection Engineering Agent",
             f"Back-test before you ask  ·  {DAYS} days  ·  {len(rows)} sign-in -> inbox-rule pairs")
    t.synthetic_notice()

    t.step(1, 3, "Draft three candidates from the INC-4471 handoff envelope")
    for k, (name, _) in RULES.items():
        print(f"    {t.bold(k)}  {name:<18} {t.dim(KQL[k].splitlines()[0].split(': ', 1)[1])}")
    t.why("The cheapest rule to write is the IOC rule - it is also the one that expires the "
          "day the attacker rotates infrastructure.")

    t.step(2, 3, "Back-test each one against seven days of telemetry")
    print(t.dim(f"    {'rule':<22}{'caught':>8}{'FP/day':>9}{'max/run':>9}   gates"))
    results = {}
    for k, (name, fn) in RULES.items():
        r = results[k] = backtest(fn, rows)
        gates = "  ".join((t.green if v else t.red)(f"{g} {'ok' if v else 'X'}") for g, v in r["gates"].items())
        print(f"    {k + ' ' + name:<22}{r['tp']:>5}/{r['bad']:<2}{r['fp_per_day']:>9.1f}{r['max_per_run']:>9}   {gates}")
    for k, r in results.items():
        if r["missed"]:
            t.fail(f"{k} misses {', '.join(u.split('@')[0] for u in r['missed'])} - different AiTM node")
        if not r["gates"]["noise"]:
            t.fail(f"{k} would page someone {r['fp_per_day']:.0f} times a day for nothing")
    t.why("C is the only rule that catches both known-bad cases without burying the queue. Its one "
          "false positive in a week is an AP clerk on holiday - explainable, and acceptable.")

    t.step(3, 3, "Create C disabled, then ask")
    t.tool("create custom detection", "C - frequency: every hour, state: disabled")
    t.gate("enable custom detection 'Risky sign-in, then a rule that hides finance mail'")
    t.say("Back-test report attached: 2/2 known-bad, 0.1 FP/day, max 1 alert per run.", 4)
    t.allow("Approved by detection lead - enabled")
    t.verdict("The agent did the engineering. A human made the decision, with evidence.")
    return results


def ship_first() -> dict:
    rows = telemetry()
    t.banner("Demo 04 - Ship first, test later", "Candidate B enabled with no back-test")
    t.synthetic_notice()
    t.step(1, 2, "Enable B, run hourly")
    t.warn("no back-test, no approval - the agent 'helpfully' enables its first draft")
    day0 = [r for r in rows if r["day"] == 0 and rule_b(r)]
    t.step(2, 2, "The first 24 hours")
    t.kv("alerts raised", str(len(day0)))
    t.kv("true positives", str(sum(r["bad"] for r in day0)))
    t.kv("analyst minutes", f"{len(day0) * 6} (6 min each)")
    t.why("Noise is not harmless. Every one of those alerts trains the analysts - and the triage "
          "agent - to close this rule without looking. That is how the real one gets missed.")
    t.verdict(f"{len(day0)} alerts, 0 attacks. The rule is disabled by lunch, and so is trust in it.", good=False)
    return {"day0": len(day0)}


def self_test() -> int:
    rows = telemetry()
    a, b, c = (backtest(fn, rows) for _, fn in RULES.values())
    r = [
        ("telemetry is deterministic", telemetry() == rows),
        ("two known-bad cases in the window", sum(x["bad"] for x in rows) == 2),
        ("A (IOC) misses the earlier AiTM node", a["tp"] == 1 and not a["gates"]["recall"]),
        ("B (broad) catches both", b["gates"]["recall"]),
        ("B fails the noise gate", not b["gates"]["noise"]),
        ("C passes all three gates", c["pass"]),
        ("C's only false positive is the AP clerk on holiday", c["fp"] == 1),
        ("no rule comes near the 150-per-run cap", all(x["max_per_run"] < CAP_PER_RUN for x in (a, b, c))),
        ("ship-first day one: > 10 alerts, 0 true positives",
         len([x for x in rows if x["day"] == 0 and rule_b(x)]) > 10
         and not any(x["bad"] for x in rows if x["day"] == 0 and rule_b(x))),
    ]
    t.banner("Demo 04 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ship-first", action="store_true")
    p.add_argument("--kql", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.kql:
        for k in KQL:
            print(KQL[k] + "\n")
    elif a.ship_first:
        ship_first()
    else:
        run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
