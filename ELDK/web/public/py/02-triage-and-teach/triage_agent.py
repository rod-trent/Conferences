#!/usr/bin/env python3
"""
Demo 02 - Triage, With a Human in the Loop
==========================================

Seventeen user-reported emails. A triage agent classifies each one, resolves the
false positives it is confident about, and leaves everything else open for an
analyst. Then we evaluate it against analyst-confirmed labels - and teach it.

Behaviour mirrored from the Phishing Triage Agent on Microsoft Learn:
  - the agent assigns the alert to itself and tags the incident "Agent"
  - false positives are resolved automatically; true positives stay open for
    an analyst - the agent never closes a true positive on purpose
  - an analyst can "Change classification" with a natural-language reason and
    choose "Use this feedback to teach the agent"; "Evaluate feedback" runs
    conflict checks, and feedback ends up In use, Conflict, or Not in use
  - feedback is once per alert, and only True Positive / False Positive

The scoring here is a deterministic stand-in so the demo is repeatable.

    python triage_agent.py                    # confidence threshold 0.90
    python triage_agent.py --threshold 0.60   # "it's slow, lower the bar" - watch what closes
    python triage_agent.py --teach            # the analyst teaches it, one lesson conflicts
    python triage_agent.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

DATA = json.loads((HERE / "alerts.json").read_text(encoding="utf-8"))


def _matches(alert: dict, pattern: str) -> bool:
    if pattern.startswith("sender:"):
        return pattern[len("sender:"):] in alert["sender"]
    return pattern in alert["signals"]


def fp_confidence(alert: dict, memory: list[dict]) -> float:
    """Confidence that the alert is a false positive, 0.01-0.99."""
    m = sum(DATA["weights"][s] for s in alert["signals"])
    m += sum(l["delta"] for l in memory if l["status"] == "In use" and _matches(alert, l["pattern"]))
    return round(min(0.99, max(0.01, 0.5 - m)), 2)


def triage(threshold: float, memory: list[dict]) -> list[dict]:
    out = []
    for a in DATA["alerts"]:
        c = fp_confidence(a, memory)
        if c >= threshold:
            action = "resolved: false positive"
        elif c <= 0.20:
            action = "open: likely true positive"
        else:
            action = "open: needs analyst"
        out.append({**a, "fp": c, "action": action, "closed": action.startswith("resolved")})
    return out


def evaluate(rows: list[dict]) -> dict:
    closed = [r for r in rows if r["closed"]]
    bad = [r for r in closed if r["label"] == "TP"]
    fps = [r for r in rows if r["label"] == "FP"]
    return {
        "closed": len(closed),
        "queue": len(rows) - len(closed),
        "tp_closed": bad,
        "fp_caught": sum(1 for r in closed if r["label"] == "FP"),
        "fp_total": len(fps),
        "workload_cut": len(closed) / len(rows),
    }


def evaluate_feedback(fb: dict, memory: list[dict]) -> tuple[str, str]:
    """Return (status, reason) for one piece of analyst feedback."""
    for lesson in memory:
        if lesson["status"] == "In use" and lesson["pattern"] == fb["pattern"] \
                and (lesson["delta"] > 0) != (fb["delta"] > 0):
            return "Conflict", f"contradicts {lesson['id']}: \"{lesson['text']}\""
    return "In use", "no conflict with stored lessons"


def print_rows(rows: list[dict], threshold: float) -> None:
    print(t.dim(f"  {'alert':<8}{'fp conf':>8}  {'decision':<28}subject"))
    for r in rows:
        col = t.green if r["closed"] else t.yellow if "needs" in r["action"] else t.red
        act = f"{r['action']:<28}"
        print(f"  {r['id']:<8}{r['fp']:>8.2f}  {col(act)}{t.dim(r['subject'][:34])}")


def run(threshold: float) -> dict:
    memory = [dict(m) for m in DATA["memory"]]
    t.banner("Demo 02 - Triage, With a Human in the Loop",
             f"{len(DATA['alerts'])} user-reported emails  ·  auto-resolve threshold {threshold:.2f}")
    t.synthetic_notice()

    t.step(1, 3, "The agent picks up the queue")
    t.tool("assign", f"{len(DATA['alerts'])} alerts -> Triage Agent")
    t.tool("tag", "incident tag 'Agent' added")
    t.kv("stored lessons", f"{len(memory)}  ({memory[0]['id']}: {memory[0]['text'][:48]}...)")
    t.why("Self-assignment and the 'Agent' tag are the handoff contract with the humans: anyone "
          "looking at the queue knows a machine holds it.")

    t.step(2, 3, "Classify - resolve only what it is sure about")
    rows = triage(threshold, memory)
    print_rows(rows, threshold)
    ev = evaluate(rows)
    t.why(f"The agent resolved {ev['closed']} of {len(rows)}. Everything else is still open with the analyst - "
          "that is the human in the loop, by design.")

    t.step(3, 3, "Evaluate against analyst-confirmed labels")
    t.kv("false positives caught", f"{ev['fp_caught']} of {ev['fp_total']}")
    t.kv("analyst queue", f"{ev['queue']} (workload cut {ev['workload_cut']:.0%})")
    t.kv("true positives closed", str(len(ev["tp_closed"])))
    if ev["tp_closed"]:
        for r in ev["tp_closed"]:
            t.fail(f"{r['id']} {r['subject']} - closed at {r['fp']:.2f}")
            if r.get("story"):
                t.say(t.red(r["story"]), 9)
        t.why("A lower bar bought a smaller queue and closed a real attack. Measure the error you "
              "cannot afford - a closed true positive - not the average accuracy.")
        t.verdict(f"Threshold {threshold:.2f}: {len(ev['tp_closed'])} real attack auto-closed. Ship-blocker.",
                  good=False)
    else:
        t.ok("no true positive auto-closed")
        t.why("This is the gate that goes into the evaluation suite: zero closed true positives, "
              "re-run on every prompt, model or lesson change.")
        t.verdict(f"Threshold {threshold:.2f}: {ev['workload_cut']:.0%} of the queue handled, "
                  "no attack closed.")
    return ev


def teach(threshold: float) -> list[tuple[str, str]]:
    memory = [dict(m) for m in DATA["memory"]]
    t.banner("Demo 02 - Teach the Agent", "Change classification -> Use this feedback to teach the agent")
    t.synthetic_notice()
    before = {r["id"]: r for r in triage(threshold, memory)}
    statuses = []
    for i, fb in enumerate(DATA["feedback"], 1):
        a = before[fb["alert"]]
        t.step(i, len(DATA["feedback"]) + 1, f"Analyst feedback on {fb['alert']}")
        t.kv("alert", a["subject"])
        t.kv("agent said", f"{a['action']} (fp {a['fp']:.2f})")
        t.kv("analyst says", fb["classification"])
        t.kv("reason", f"\"{fb['reason']}\"")
        t.tool("Evaluate feedback", "safety and conflict checks")
        status, why = evaluate_feedback(fb, memory)
        if status == "In use":
            t.ok(f"In use - {why}")
            memory.append({"id": f"L-0{len(memory) + 1}", "text": fb["reason"], "pattern": fb["pattern"],
                           "delta": fb["delta"], "status": "In use"})
        else:
            t.warn(f"{status} - {why}")
        statuses.append((fb["alert"], status))
        if status == "In use":
            t.why("A good lesson is narrow: one sender domain, one reason. It changes one decision.")
        else:
            t.why("The broad lesson would have taught the agent to close the vendor-fraud email. "
                  "The conflict check is the second human in the loop.")

    t.step(len(DATA["feedback"]) + 1, len(DATA["feedback"]) + 1, "Re-run with the new memory")
    after = triage(threshold, memory)
    changed = [r for r in after if r["action"] != before[r["id"]]["action"]]
    for r in changed:
        print(f"  {r['id']}  {before[r['id']]['action']} -> {t.green(r['action'])}")
    ev = evaluate(after)
    t.kv("true positives closed", str(len(ev["tp_closed"])))
    t.verdict(f"{len(changed)} decision changed, 0 attacks closed. Teach narrowly, evaluate every lesson.",
              good=not ev["tp_closed"])
    return statuses


def self_test() -> int:
    mem = [dict(m) for m in DATA["memory"]]
    r = []
    ev = evaluate(triage(0.90, mem))
    r.append(("0.90 threshold closes no true positive", not ev["tp_closed"]))
    r.append(("0.90 threshold still resolves >= 5 false positives", ev["fp_caught"] >= 5))
    ev6 = evaluate(triage(0.60, mem))
    r.append(("0.60 threshold auto-closes the partner-tenant AiTM share E-1017",
              [x["id"] for x in ev6["tp_closed"]] == ["E-1017"]))
    r.append(("0.60 threshold shrinks the queue", ev6["queue"] < ev["queue"]))
    r.append(("lesson L-01 holds the vendor-fraud email E-1006 at <= 0.20",
              {x["id"]: x for x in triage(0.90, mem)}["E-1006"]["fp"] <= 0.20))
    r.append(("agent never resolves anything as true positive",
              all(not x["action"].startswith("resolved: true") for x in triage(0.5, mem))))
    s1 = evaluate_feedback(DATA["feedback"][0], mem)[0]
    s2 = evaluate_feedback(DATA["feedback"][1], mem)[0]
    r.append(("narrow lesson -> In use", s1 == "In use"))
    r.append(("lesson contradicting L-01 -> Conflict", s2 == "Conflict"))
    mem2 = mem + [{"id": "L-02", "text": "", "pattern": DATA["feedback"][0]["pattern"],
                   "delta": DATA["feedback"][0]["delta"], "status": "In use"}]
    row = {x["id"]: x for x in triage(0.90, mem2)}["E-1008"]
    r.append(("after the lesson E-1008 is resolved", row["closed"] and row["label"] == "FP"))
    r.append(("17 alerts, 8 labelled true positive",
              len(DATA["alerts"]) == 17 and sum(a["label"] == "TP" for a in DATA["alerts"]) == 8))
    t.banner("Demo 02 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--threshold", type=float, default=0.90)
    p.add_argument("--teach", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.teach:
        teach(a.threshold)
    else:
        run(a.threshold)
    return 0


if __name__ == "__main__":
    sys.exit(main())
