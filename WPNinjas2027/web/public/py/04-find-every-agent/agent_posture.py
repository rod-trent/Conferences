#!/usr/bin/env python3
"""
Demo 04 - Find Every Agent
==========================

You cannot protect an agent you do not know exists. This demo walks a
synthetic AgentsInfo export (the Defender XDR advanced hunting table that
replaced AIAgentsInfo) and does what the Defender portal's
Assets > AI agents view does: assign each agent a risk level and the risk
indicators behind it.

Column names, risk levels and risk-indicator names are from Microsoft Learn.
The SCORING RULES are a local, readable stand-in - Defender's own assessment
is richer.

    python agent_posture.py                       # inventory + risk
    python agent_posture.py --agent "Vendor Desk" # one agent, every indicator explained
    python agent_posture.py --gaps                # what blocks protection, not just posture
    python agent_posture.py --kql                 # the hunting queries behind the view
    python agent_posture.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

LEVELS = ["High", "Medium", "Low", "No known risk", "Not evaluated"]

BUSINESS_SYSTEMS = ("Dataverse:Finance", "SAP", "Dynamics 365 Finance", "Workday", "ServiceNow:Admin")
UNTRUSTED_SOURCES = ("Outlook", "Email", "Web search", "Public website", "SharePoint (external sharing)", "GitHub issues")
OUTBOUND = ("SendEmail", "PostToWebhook", "HttpRequest", "ShareFile", "Bash")


def load() -> list[dict]:
    rows = json.loads((HERE / "agentsinfo_sample.json").read_text(encoding="utf-8"))
    latest: dict[str, dict] = {}
    for r in rows:                                   # summarize arg_max(Timestamp, *) by AgentId
        if r["AgentId"] not in latest or r["Timestamp"] > latest[r["AgentId"]]["Timestamp"]:
            latest[r["AgentId"]] = r
    return [r for r in latest.values() if r["LifecycleStatus"] != "Deleted"]


def assess(a: dict) -> dict:
    """Return {'level', 'indicators': [(name, why)], 'gaps': [...], 'recs': [...]}."""
    ind: list[tuple[str, str]] = []
    gaps: list[str] = []
    recs: list[str] = []

    if a["Platform"] == "Local":
        return {"level": "Not evaluated", "indicators": [], "recs": [],
                "gaps": ["Local agent: protected by Defender for Endpoint runtime protection, not cloud rules"]}

    instr = (a.get("Instructions") or "").strip()
    if len(instr) < 80 or not any(w in instr.lower() for w in ("never", "only", "do not", "must not")):
        ind.append(("Weak Instructions", f"{len(instr)} chars, no explicit boundaries"))
        if a["Platform"] == "Microsoft Foundry":
            recs.append("Azure AI Agent should be configured with operational instructions (Preview)")

    sources = a.get("DeclaredDataSources", []) + a.get("Triggers", [])
    if any(s.startswith(UNTRUSTED_SOURCES) for s in sources):
        ind.append(("Indirect Prompt Injection Exposure",
                    "reads content an outsider can write: " +
                    ", ".join(s for s in sources if s.startswith(UNTRUSTED_SOURCES))))
        if a["Platform"] == "Microsoft Foundry":
            recs.append("Foundry AI Agent with Indirect prompt Injection risk should use enhanced guardrails controls (Preview)")
            if a.get("McpServers"):
                recs.append("Foundry AI Agent with Indirect prompt Injection risk should require human in the loop "
                            "control for MCP tool actions (Preview)")

    if any(p.startswith(BUSINESS_SYSTEMS) for p in a.get("Permissions", []) + a.get("DeclaredTools", [])):
        ind.append(("Privileged Business-system Access", "can write to a system of record"))

    if a.get("MonthlyInvocations", 0) > 20000:
        ind.append(("High-usage Agent", f"{a['MonthlyInvocations']:,} invocations / month"))

    if a.get("ActiveAlerts", 0):
        ind.append(("Active Threat", f"{a['ActiveAlerts']} active alert(s)"))

    if a["Platform"] == "Microsoft Foundry":
        g = a.get("Guardrails", [])
        if "Jailbreak" not in g:
            recs.append("Foundry AI Agent's Guardrails should include Jailbreak control (Preview)")
        for m in a.get("McpServers", []):
            if not m.get("allowedTools"):
                recs.append("Foundry Agent's MCP tool should be configured with allowed tools list (Preview)")
                break

    # Gaps that stop PROTECTION, not just posture.
    if not a.get("EntraAgentId"):
        gaps.append("No Microsoft Entra agent ID - cannot be scoped into a real-time BLOCK rule or Conditional Access")
    if not a.get("Owners"):
        gaps.append("No owner - nobody to approve a block, answer an alert or retire it")
    if a.get("ToolsAuthenticationType") == "Maker credentials":
        gaps.append("Tools run as the maker's credentials - every user gets the maker's access")
    if "Everyone" in a.get("SharedWith", []) and a["PublishedStatus"] == "Published":
        gaps.append("Shared with everyone in the tenant")

    names = {n for n, _ in ind}
    outbound = any(x in OUTBOUND for x in a.get("DeclaredTools", []))
    if "Active Threat" in names or (
            "Indirect Prompt Injection Exposure" in names and ("Privileged Business-system Access" in names or outbound)):
        level = "High"
    elif len(ind) >= 2 or "Indirect Prompt Injection Exposure" in names:
        level = "Medium"
    elif ind or gaps:
        level = "Low"
    else:
        level = "No known risk"
    return {"level": level, "indicators": ind, "gaps": gaps, "recs": recs}


def colour(level: str) -> str:
    return {"High": t.red, "Medium": t.yellow, "Low": t.cyan, "No known risk": t.green}.get(level, t.dim)(level)


def inventory(agents: list[dict]) -> None:
    t.step(1, 3, "Inventory - every agent, every platform")
    print(t.dim(f"  {'Agent':<30}{'Platform':<16}{'Status':<11}{'Risk':<15}Indicators"))
    rows = sorted(agents, key=lambda a: LEVELS.index(assess(a)["level"]))
    for a in rows:
        r = assess(a)
        plat = a["Platform"].replace("Microsoft ", "")
        print(f"  {a['AgentName']:<30}{plat:<16}{a['PublishedStatus']:<11}"
              f"{colour(r['level'])}{' ' * (15 - len(r['level']))}"
              f"{', '.join(n for n, _ in r['indicators']) or t.dim('-')}")
    counts = {lvl: sum(assess(a)["level"] == lvl for a in agents) for lvl in LEVELS}
    print()
    print("  " + "   ".join(f"{colour(k)}: {v}" for k, v in counts.items() if v))
    t.why("Three of these agents read content an outsider can write AND can act on it. That combination - "
          "untrusted input plus a consequential tool - is the definition of an XPIA target.")


def gaps_view(agents: list[dict]) -> None:
    t.step(2, 3, "Protection gaps - what stops Defender from blocking")
    for a in agents:
        r = assess(a)
        if not r["gaps"]:
            continue
        print(f"  {t.bold(a['AgentName'])} {t.dim('(' + a['Platform'] + ')')}")
        for g in r["gaps"]:
            print(f"    {t.yellow('!')} {g}")
    t.why("Posture tells you what is risky. These gaps tell you what you could not protect even if you "
          "wanted to - an agent with no Entra agent ID never appears in the real-time rule picker.")


def recs_view(agents: list[dict]) -> None:
    t.step(3, 3, "Recommendations for Foundry agents (verbatim from Learn)")
    print(t.dim("  Since 1 July 2026 agent discovery and posture are licensed through Microsoft Agent 365."))
    for a in agents:
        r = assess(a)
        for rec in dict.fromkeys(r["recs"]):
            print(f"  {t.bold(a['AgentName'])}{' ' * (22 - len(a['AgentName']))}{rec}")
    t.verdict("Inventory first, then scope: the High agents go into a custom BLOCK rule this week.")


def detail(agents: list[dict], name: str) -> int:
    match = [a for a in agents if a["AgentName"].lower() == name.lower()]
    if not match:
        print(f"no agent named {name!r}. Try: " + ", ".join(a["AgentName"] for a in agents))
        return 1
    a = match[0]
    r = assess(a)
    t.banner(f"Agent: {a['AgentName']}", f"{a['Platform']} - risk {r['level']}")
    for k in ("AgentId", "EntraAgentId", "Platform", "PublishedStatus", "LifecycleStatus", "Owners", "SharedWith",
              "Model", "Channels", "DeclaredTools", "DeclaredDataSources", "Triggers", "McpServers",
              "Guardrails", "ToolsAuthenticationType"):
        v = a.get(k)
        t.kv(k, json.dumps(v) if isinstance(v, (list, dict)) else (v or t.yellow("(empty)")), width=26)
    print()
    print(t.bold("  Risk indicators"))
    for n, why in r["indicators"] or [("none", "")]:
        print(f"    {t.red('*')} {n:<36} {t.dim(why)}")
    print(t.bold("  Protection gaps"))
    for g in r["gaps"] or ["none"]:
        print(f"    {t.yellow('!')} {g}")
    print(t.bold("  Instructions"))
    t.say(t.dim(a.get("Instructions") or "(none)"), indent=4)
    return 0


KQL = r"""
// 1. Latest state of every agent (the query on Microsoft Learn's AgentsInfo page)
AgentsInfo
| summarize arg_max(Timestamp, *) by AgentId
| where LifecycleStatus != "Deleted"

// 2. Published agents with no Entra agent ID - cannot be scoped into a block rule
AgentsInfo
| summarize arg_max(Timestamp, *) by AgentId
| where LifecycleStatus == "Active" and PublishedStatus == "Published"
| where isempty(EntraAgentId)
| project AgentName, Platform, Owners, SharedWith

// 3. Agents that read outsider-writable content AND can send it somewhere
AgentsInfo
| summarize arg_max(Timestamp, *) by AgentId
| where tostring(DeclaredDataSources) has_any ("Outlook", "Web search", "Public website")
   or tostring(Triggers) has_any ("Email", "GitHub issues")
| where tostring(DeclaredTools) has_any ("SendEmail", "HttpRequest", "PostToWebhook", "ShareFile")
| project AgentName, Platform, DeclaredDataSources, DeclaredTools, Owners

// 4. Ownerless agents
AgentsInfo
| summarize arg_max(Timestamp, *) by AgentId
| where LifecycleStatus == "Active" and array_length(Owners) == 0
"""


def self_test() -> int:
    agents = load()
    by = {a["AgentName"]: assess(a) for a in agents}
    r = []
    r.append(("deleted agents are excluded", "Holiday Promo (retired)" not in by))
    r.append(("arg_max keeps the latest record per agent",
              next(a for a in agents if a["AgentName"] == "HR Policy Bot")["PublishedStatus"] == "Published"))
    r.append(("Vendor Desk is High (XPIA exposure + privileged + active threat)", by["Vendor Desk"]["level"] == "High"))
    r.append(("Trail Concierge flags the MCP allowed-tools recommendation",
              any("allowed tools list" in x for x in by["Trail Concierge"]["recs"])))
    r.append(("Release Notes Writer has no known risk", by["Release Notes Writer"]["level"] == "No known risk"))
    r.append(("HR Policy Bot has Weak Instructions",
              any(n == "Weak Instructions" for n, _ in by["HR Policy Bot"]["indicators"])))
    r.append(("Invoice Matcher gap: no Entra agent ID", any("Entra agent ID" in g for g in by["Invoice Matcher"]["gaps"])))
    r.append(("local agent is Not evaluated", by["code-agent on CO-DEV-LT-0412"]["level"] == "Not evaluated"))
    r.append(("every level used is a Learn risk level", all(v["level"] in LEVELS for v in by.values())))
    t.banner("Demo 04 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--agent")
    p.add_argument("--gaps", action="store_true")
    p.add_argument("--kql", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.kql:
        t.banner("Demo 04 - the hunting queries behind the inventory", "Defender XDR > Advanced hunting")
        print(KQL)
        return 0
    agents = load()
    if a.agent:
        return detail(agents, a.agent)
    t.banner("Demo 04 - Find Every Agent", f"AgentsInfo: {len(agents)} live agents (latest record per AgentId)")
    t.synthetic_notice()
    if a.gaps:
        gaps_view(agents)
        return 0
    inventory(agents)
    gaps_view(agents)
    recs_view(agents)
    return 0


if __name__ == "__main__":
    sys.exit(main())
