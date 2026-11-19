#!/usr/bin/env python3
"""
Demo 05 - Hunt the Agent Kill Chain
===================================

Alerts tell you about the attacks your controls saw. Hunting tells you about
the ones they only AUDITED. This demo runs five advanced hunting queries over
a synthetic week of Defender XDR data and assembles the campaign.

Tables (Microsoft Learn, "AI agent detection and protection" hunting list):
  AlertInfo, AlertEvidence, BehaviorInfo, CloudAppEvents, AgentsInfo
CloudAppEvents ActionType values for agents (Agent 365 observability):
  InvokeAgent, InferenceCall, ExecuteToolBySDK, ExecuteToolByGateway,
  ExecuteToolByMCPServer

The KQL printed is what you would paste into Advanced hunting. The results
come from evaluating the same logic in Python over hunting_sample.json -
there is no KQL engine in here. Column VALUES in the sample (alert titles
aside) are illustrative; check them against your own tenant.

    python hunt_agents.py               # all five hunts, then the timeline
    python hunt_agents.py --hunt 4      # just one
    python hunt_agents.py --kql         # the queries only, to paste
    python hunt_agents.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

AGENT_ACTIONS = {"InvokeAgent", "InferenceCall", "ExecuteToolBySDK", "ExecuteToolByGateway", "ExecuteToolByMCPServer"}
TOOL_ACTIONS = {"ExecuteToolBySDK", "ExecuteToolByGateway", "ExecuteToolByMCPServer"}


def load() -> dict:
    data = json.loads((HERE / "hunting_sample.json").read_text(encoding="utf-8"))
    inv = json.loads((HERE.parent / "04-find-every-agent" / "agentsinfo_sample.json").read_text(encoding="utf-8"))
    latest: dict[str, dict] = {}
    for r in inv:
        if r["AgentId"] not in latest or r["Timestamp"] > latest[r["AgentId"]]["Timestamp"]:
            latest[r["AgentId"]] = r
    data["AgentsInfo"] = [r for r in latest.values() if r["LifecycleStatus"] != "Deleted"]
    return data


def table(rows: list[dict], cols: list[str], widths: list[int]) -> None:
    print("  " + t.dim("".join(f"{c:<{w}}" for c, w in zip(cols, widths))))
    for r in rows:
        print("  " + "".join(f"{str(r.get(c, ''))[:w - 1]:<{w}}" for c, w in zip(cols, widths)))
    print(t.dim(f"  ({len(rows)} rows)"))


# ---------------------------------------------------------------------------
# The hunts. Each: (title, kql, python-evaluator, columns, widths, why)
# ---------------------------------------------------------------------------

def h1(d):
    keys = ("Jailbreak", "ASCII Smuggling", "prompt injection", "Anomalous tool invocation", "LLM Reconnaissance")
    return sorted([a for a in d["AlertInfo"] if any(k.lower() in a["Title"].lower() for k in keys)],
                  key=lambda a: a["Timestamp"])


def h2(d):
    return sorted(d["BehaviorInfo"], key=lambda b: b["Timestamp"])


def h3(d):
    audited = {b["AdditionalFields"]["ConversationId"] for b in d["BehaviorInfo"] if b["ActionType"] == "Audited"}
    out = []
    for e in d["CloudAppEvents"]:
        if e["ActionType"] in TOOL_ACTIONS and e["RawEventData"].get("ConversationId") in audited:
            out.append({"Timestamp": e["Timestamp"], "ConversationId": e["RawEventData"]["ConversationId"],
                        "AgentId": e["RawEventData"]["AgentId"], "Tool": e["RawEventData"]["ToolName"],
                        "Target": e["RawEventData"].get("Target", ""), "Result": e["RawEventData"]["Result"]})
    return sorted(out, key=lambda r: r["Timestamp"])


def h4(d):
    ip_alerts = {}
    for ev in d["AlertEvidence"]:
        if ev["EntityType"] == "Ip":
            ip_alerts.setdefault(ev["RemoteIP"], set()).add(ev["AlertId"])
    ips = set(ip_alerts)
    seen: dict[tuple, dict] = {}
    for e in d["CloudAppEvents"]:
        if e["ActionType"] == "InvokeAgent" and e["IPAddress"] in ips:
            k = (e["IPAddress"], e["RawEventData"]["AgentId"])
            row = seen.setdefault(k, {"IPAddress": e["IPAddress"], "AgentId": e["RawEventData"]["AgentId"],
                                      "Invocations": 0, "FirstSeen": e["Timestamp"],
                                      "AlertsFromIP": len(ip_alerts[e["IPAddress"]])})
            row["Invocations"] += 1
            row["FirstSeen"] = min(row["FirstSeen"], e["Timestamp"])
    return sorted(seen.values(), key=lambda r: r["FirstSeen"])


def h5(d):
    hit_agents = {b["AdditionalFields"]["AgentId"] for b in d["BehaviorInfo"]}
    hit_agents |= {r["AgentId"] for r in h4(d)}
    out = []
    for a in d["AgentsInfo"]:
        if a["AgentId"] in hit_agents:
            out.append({"AgentName": a["AgentName"], "Platform": a["Platform"].replace("Microsoft ", ""),
                        "EntraAgentId": "yes" if a["EntraAgentId"] else "NO",
                        "Owners": ", ".join(a["Owners"]) or "NONE",
                        "ToolsAuth": a["ToolsAuthenticationType"]})
    return out


HUNTS = [
    ("Every AI and agent alert this week",
     """AlertInfo
| where Timestamp > ago(7d)
| where Title has_any ("Jailbreak", "ASCII Smuggling", "prompt injection",
                       "Anomalous tool invocation", "LLM Reconnaissance")
| project Timestamp, Title, Severity, ServiceSource, AlertId
| order by Timestamp asc""",
     h1, ["Timestamp", "Title", "Severity", "ServiceSource"], [22, 52, 9, 24],
     "Model-level alerts (Defender for AI Services) and endpoint agent alerts (Defender for Endpoint) "
     "arrive in one table. Start every agent hunt here - but do not stop here."),
    ("Real-time protection behaviors: blocked AND audited",
     """BehaviorInfo
| where Timestamp > ago(7d)
| where Categories has "AI" or Title has "agent"     // confirm values in your tenant
| extend AgentId = tostring(AdditionalFields.AgentId),
         ConversationId = tostring(AdditionalFields.ConversationId),
         DetectionType = tostring(AdditionalFields.DetectionType)
| project Timestamp, ActionType, DetectionType, AgentId, ConversationId""",
     h2, ["Timestamp", "ActionType", "DetectionType", "AgentId", "ConversationId"], [22, 12, 32, 10, 14],
     "Blocked is a closed case. AUDITED means Defender saw it and let it run - the agent had no "
     "custom block rule. Every Audited row is a question: what did the tool do next?"),
    ("What the agent actually did after an audited behavior",
     """let audited = BehaviorInfo
    | where Timestamp > ago(7d) and ActionType == "Audited"
    | project ConversationId = tostring(AdditionalFields.ConversationId);
CloudAppEvents
| where Timestamp > ago(7d)
| where ActionType in ("ExecuteToolBySDK", "ExecuteToolByGateway", "ExecuteToolByMCPServer")
| extend ConversationId = tostring(RawEventData.ConversationId),
         AgentId = tostring(RawEventData.AgentId)
| where ConversationId in (audited)
| project Timestamp, ConversationId, AgentId, Tool = RawEventData.ToolName,
          Target = RawEventData.Target, Result = RawEventData.Result""",
     h3, ["Timestamp", "ConversationId", "AgentId", "Tool", "Target", "Result"], [22, 16, 9, 11, 28, 9],
     "This is the finding. The audited SendEmail succeeded - to a paste site. The alert was "
     "accurate and the data still left. Audit is visibility, not protection."),
    ("Same attacker, other agents (pivot on IP)",
     """let attackerIPs = AlertEvidence
    | where Timestamp > ago(7d) and EntityType == "Ip"
    | distinct RemoteIP;
CloudAppEvents
| where Timestamp > ago(7d) and ActionType == "InvokeAgent"
| where IPAddress in (attackerIPs)
| summarize Invocations = count(), FirstSeen = min(Timestamp)
    by IPAddress, AgentId = tostring(RawEventData.AgentId)""",
     h4, ["IPAddress", "AgentId", "Invocations", "FirstSeen", "AlertsFromIP"], [16, 9, 12, 22, 12],
     "The IP that jailbroke Trail Concierge also went shopping for other agents. Prompt attacks are "
     "reconnaissance too - the end-user context from demo 01 is what makes this pivot possible."),
    ("Enrich: who owns the agents involved, and can we block them?",
     """AgentsInfo
| summarize arg_max(Timestamp, *) by AgentId
| where AgentId in ("cs-7f21", "fd-1a09", "cs-9e88")   // from hunts 2-4
| project AgentName, Platform, EntraAgentId, Owners, ToolsAuthenticationType""",
     h5, ["AgentName", "Platform", "EntraAgentId", "Owners", "ToolsAuth"], [20, 15, 13, 34, 18],
     "The agent that leaked is the one with no Entra agent ID, no owner and the maker's mailbox. "
     "It could never have been put in a block rule. Posture debt became an incident."),
]


def run_hunt(d: dict, i: int, total: int) -> None:
    title, kql, fn, cols, widths, why = HUNTS[i]
    t.step(i + 1, total, title)
    for line in kql.splitlines():
        print("  " + t.cyan(line))
    print()
    rows = fn(d)
    if fn is h2:
        rows = [{**r, **r["AdditionalFields"]} for r in rows]
    if fn is h1:
        rows = [{**r, "ServiceSource": r["ServiceSource"].replace("Microsoft ", "")} for r in rows]
    table(rows, cols, widths)
    t.why(why)


def timeline(d: dict) -> None:
    print()
    t.rule("-")
    print(t.bold("  The campaign, assembled"))
    events = [
        ("2026-12-01 14:02", "203.0.113.77 jailbreaks Trail Concierge (blocked by Prompt Shields)"),
        ("2026-12-01 14:09", "same IP probes Q3 Promo Bot and Vendor Desk"),
        ("2026-12-02 09:15", "injected 'remittance' email reaches the AP mailbox"),
        ("2026-12-02 09:16", "Vendor Desk SendEmail to vendor-remit-portal.net -> BLOCKED (custom rule)"),
        ("2026-12-02 11:40", "promo-page comment injects Q3 Promo Bot"),
        ("2026-12-02 11:41", "Q3 Promo Bot SendEmail to paste-drop.io -> AUDITED, executed"),
        ("2026-12-03 10:05", "code-agent on CO-DEV-LT-0412 blocked by Defender for Endpoint (unrelated repo)"),
    ]
    for ts, what in events:
        colour = t.red if "AUDITED" in what else (t.green if "BLOCKED" in what or "blocked" in what else str)
        print(f"  {t.dim(ts)}  {colour(what)}")
    t.verdict("One campaign, three agents. Two controls held; the gap was an agent nobody could scope.", good=False)
    print(t.dim("  Actions: give Q3 Promo Bot an owner and Entra agent ID, or retire it; add it to a custom"))
    print(t.dim("  block rule; rotate the maker's mailbox credentials; block 203.0.113.77."))


def self_test() -> int:
    d = load()
    r = []
    a = h1(d)
    r.append(("hunt 1 finds model + endpoint agent alerts", len(a) == 3))
    r.append(("hunt 1 ignores unrelated alerts", all("Impossible travel" not in x["Title"] for x in a)))
    b = h2(d)
    r.append(("hunt 2 returns one blocked and one audited", sorted(x["ActionType"] for x in b) == ["Audited", "Blocked"]))
    c = h3(d)
    r.append(("hunt 3 finds the audited SendEmail that succeeded",
              any(x["Tool"] == "SendEmail" and x["Result"] == "Success" for x in c)))
    r.append(("hunt 3 excludes the blocked conversation", all(x["ConversationId"] != "conv-5521" for x in c)))
    p = h4(d)
    r.append(("hunt 4 pivots the attacker IP to 3 agents", {x["AgentId"] for x in p} == {"fd-1a09", "cs-9e88", "cs-7f21"}))
    e = h5(d)
    leak = [x for x in e if x["AgentName"] == "Q3 Promo Bot"]
    r.append(("hunt 5: leaking agent has no Entra agent ID and no owner",
              leak and leak[0]["EntraAgentId"] == "NO" and leak[0]["Owners"] == "NONE"))
    r.append(("all CloudAppEvents agent ActionTypes are documented values",
              all(x["ActionType"] in AGENT_ACTIONS for x in d["CloudAppEvents"])))
    t.banner("Demo 05 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hunt", type=int, choices=range(1, len(HUNTS) + 1))
    p.add_argument("--kql", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.kql:
        for i, h in enumerate(HUNTS, 1):
            print(f"// Hunt {i}: {h[0]}\n{h[1]}\n")
        return 0
    d = load()
    t.banner("Demo 05 - Hunt the Agent Kill Chain", "Defender XDR advanced hunting, 7 days, Contoso Outdoors")
    t.synthetic_notice()
    if a.hunt:
        run_hunt(d, a.hunt - 1, len(HUNTS))
        return 0
    for i in range(len(HUNTS)):
        run_hunt(d, i, len(HUNTS))
    timeline(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
