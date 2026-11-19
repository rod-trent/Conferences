#!/usr/bin/env python3
"""
Demo 06 - Build vs. Buy: the Three-Year View
============================================

A transparent cost model for the decision this session ends on: run your own
multi-agent SOC, or run Microsoft Perception and build only what it does not
cover.

What is fact and what is assumption (see assumptions.json):
  facts        $6 per overage SCU; the Microsoft 365 E5/E7 inclusion of 400 SCUs
               per 1,000 user licences a month (cap 10,000); two platform
               retirements on 2027-03-31 that a custom build must absorb;
               Perception is consumption-priced with NO public rate card
  assumptions  engineering weeks, the cost of a week, maintenance load, SCU use -
               replace them with yours

Because there is no rate card, the model does not invent one. It computes the
break-even: the monthly Perception spend below which buying is cheaper. Get your
real number from Microsoft's cost calculator and compare - or pass it as --quote.

    python build_vs_buy.py                       # mid-size SOC, break-even
    python build_vs_buy.py --profile small
    python build_vs_buy.py --profile large
    python build_vs_buy.py --quote 12000         # with a (hypothetical) monthly quote
    python build_vs_buy.py --sensitivity         # which assumption moves the answer most
    python build_vs_buy.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))

import term as t  # noqa: E402

DATA = json.loads((HERE / "assumptions.json").read_text(encoding="utf-8"))
F = DATA["facts"]
YEARS = DATA["years"]


def included_scu(users: int) -> float:
    return min(users / 1000 * F["e5_scu_per_1000_users_month"], F["e5_scu_cap_month"])


def build_cost(p: dict) -> dict:
    wk = p["engineer_week_usd"]
    overage = max(0.0, p["custom_scu_month"] - included_scu(p["e5_users"]))
    lines = {
        "build": p["custom_agents"] * p["build_weeks_per_agent"] * wk,
        "maintenance": p["custom_agents"] * p["maintenance_weeks_per_agent_year"] * YEARS * wk,
        "evaluation + red team": p["eval_upkeep_weeks_year"] * YEARS * wk,
        "on-call for your code": p["oncall_weeks_year"] * YEARS * wk,
        "platform migrations": p["migration_weeks"] * wk,
        "SCU overage": overage * F["scu_overage_usd"] * 12 * YEARS,
    }
    return {"lines": lines, "total": sum(lines.values()), "overage_scu_month": overage}


def buy_cost(p: dict, quote: float | None) -> dict:
    """Everything on the Perception path except Perception's own consumption."""
    wk = p["engineer_week_usd"]
    r = p["residual_custom_agents"]
    # Residual custom agents still get their share of eval/on-call, pro rata.
    share = r / p["custom_agents"]
    lines = {
        "enablement (URBAC, Agent IDs, roles)": p["perception_enablement_weeks"] * wk,
        "residual custom build": r * p["build_weeks_per_agent"] * wk,
        "residual maintenance": r * p["maintenance_weeks_per_agent_year"] * YEARS * wk,
        "residual eval + on-call": share * (p["eval_upkeep_weeks_year"] + p["oncall_weeks_year"]) * YEARS * wk,
    }
    fixed = sum(lines.values())
    if quote is not None:
        lines["Perception consumption (your quote)"] = quote * 12 * YEARS
    return {"lines": lines, "fixed": fixed, "total": sum(lines.values())}


def breakeven_month(p: dict) -> float:
    return (build_cost(p)["total"] - buy_cost(p, None)["fixed"]) / (12 * YEARS)


def owned_components(path: str, p: dict) -> list[str]:
    if path == "build":
        return [f"{p['custom_agents']} agents (prompts, tools, memory)", "handoff contract + orchestrator",
                "agent identities + permissions", "evaluation suite + red-team corpus",
                "connectors to Defender / Sentinel / Graph", "model + API version upgrades",
                "platform migrations", "on-call for all of it"]
    return [f"{p['residual_custom_agents']} residual custom agent(s)", "RBAC, approvals and agent enablement",
            "evaluation of the residual agent(s)"]


def money(x: float) -> str:
    return f"${x:,.0f}"


def bar(x: float, scale: float, width: int = 30) -> str:
    n = max(0, round(x / scale * width)) if scale else 0
    return "#" * n


def run(profile: str, quote: float | None) -> dict:
    p = DATA["profiles"][profile]
    b, y = build_cost(p), buy_cost(p, quote)
    be = breakeven_month(p)
    t.banner("Demo 06 - Build vs. Buy: the Three-Year View", p["label"])
    t.synthetic_notice()
    print(t.dim("  Facts from Microsoft; every other number is an assumption in assumptions.json."))

    t.step(1, 4, "Build: what a custom multi-agent SOC costs over three years")
    scale = max(b["lines"].values())
    for k, v in b["lines"].items():
        print(f"    {k:<26}{money(v):>11}  {t.dim(bar(v, scale))}")
    print(f"    {t.bold('total'):<34}{t.bold(money(b['total'])):>19}")
    t.kv("SCUs included with E5", f"{included_scu(p['e5_users']):,.0f}/month  ->  overage {b['overage_scu_month']:,.0f}/month")
    run_cost = b["total"] - b["lines"]["build"]
    t.why(f"Building is {b['lines']['build'] / b['total']:.0%} of the bill. Running it - maintenance, "
          f"evaluation, on-call, migrations - is {run_cost / b['total']:.0%}.")

    t.step(2, 4, "Buy: Perception, plus what it does not cover")
    for k, v in y["lines"].items():
        print(f"    {k:<38}{money(v):>11}")
    t.kv("Perception consumption", "no public rate card" if quote is None else f"{money(quote)}/month (your quote)")
    t.why("No custom playbooks in this release - so anything unique to you (vendor bank-detail "
          "fraud, say) stays a custom build on both paths.")

    t.step(3, 4, "Break-even")
    print(f"    Perception is cheaper if its consumption stays under {t.bold(money(be) + '/month')}")
    print(f"    {t.dim('(three-year build total minus the fixed costs of the buy path, per month)')}")
    if quote is not None:
        diff = b["total"] - y["total"]
        (t.ok if diff > 0 else t.warn)(f"at {money(quote)}/month: buy {money(y['total'])} vs build {money(b['total'])} "
                                       f"- {'buy' if diff > 0 else 'build'} saves {money(abs(diff))}")
    t.why("Ask for the number that decides it. The cost calculator and usage dashboard Microsoft "
          "announced at Ignite give you the right-hand side of this comparison.")

    t.step(4, 4, "Supportability: what you own at 02:00")
    ob, oy = owned_components("build", p), owned_components("buy", p)
    for i in range(max(len(ob), len(oy))):
        left = ob[i] if i < len(ob) else ""
        right = oy[i] if i < len(oy) else ""
        print(f"    {left:<44}{t.dim(right)}")
    print(t.dim(f"    {'^ build: ' + str(len(ob)) + ' things you own':<44}^ buy: {len(oy)} things you own"))
    for r in F["retirements"]:
        t.warn(f"{r['what']} retires {r['date']} - a build-path migration, Microsoft's problem on the buy path")
    t.verdict(f"Buy wins below {money(be)}/month of Perception consumption. Build what's yours; buy what's standard.")
    return {"build": b, "buy": y, "breakeven": be}


SENS_KEYS = ("maintenance_weeks_per_agent_year", "build_weeks_per_agent", "oncall_weeks_year",
             "eval_upkeep_weeks_year", "custom_scu_month")


def sensitivity_rank(profile: str) -> list[tuple[str, float]]:
    p = DATA["profiles"][profile]
    out = [(k, breakeven_month({**p, k: p[k] * 2}) - breakeven_month({**p, k: p[k] * 0.5})) for k in SENS_KEYS]
    return sorted(out, key=lambda x: -x[1])


def sensitivity(profile: str) -> list[tuple[str, float]]:
    p = DATA["profiles"][profile]
    base = breakeven_month(p)
    t.banner("Demo 06 - Sensitivity", f"{p['label']}  ·  break-even {money(base)}/month")
    t.synthetic_notice()
    t.step(1, 1, "Halve or double one assumption at a time (engineer cost held fixed)")
    out = []
    # The engineer's weekly cost scales every effort line on both paths, so it is held fixed here.
    for k in ("maintenance_weeks_per_agent_year", "build_weeks_per_agent", "oncall_weeks_year",
              "eval_upkeep_weeks_year", "custom_scu_month"):
        lo = breakeven_month({**p, k: p[k] * 0.5})
        hi = breakeven_month({**p, k: p[k] * 2})
        out.append((k, hi - lo))
        print(f"    {k:<36}{money(lo):>10} .. {money(hi):<10}")
    out.sort(key=lambda x: -x[1])
    t.why(f"The assumption that moves the answer most is '{out[0][0]}' - worth "
          f"{money(out[0][1])}/month of swing. Get it from your own history of keeping automations "
          "alive, not from a vendor.")
    t.verdict("Argue about maintenance, not about build cost.")
    return out


def self_test() -> int:
    m = DATA["profiles"]["medium"]
    r = []
    r.append(("E5 inclusion: 2,000 users -> 800 SCUs/month", included_scu(2000) == 800))
    r.append(("E5 inclusion caps at 10,000 SCUs/month", included_scu(40000) == 10000))
    b = build_cost(m)
    r.append(("medium: overage = 1,300 - 800 = 500 SCUs/month", b["overage_scu_month"] == 500))
    r.append(("medium: overage cost = 500 x $6 x 36", b["lines"]["SCU overage"] == 500 * 6 * 36))
    r.append(("running costs exceed build cost on every profile",
              all(build_cost(p)["total"] - build_cost(p)["lines"]["build"] > build_cost(p)["lines"]["build"]
                  for p in DATA["profiles"].values())))
    be = breakeven_month(m)
    r.append(("at the break-even quote both paths cost the same",
              abs(buy_cost(m, be)["total"] - b["total"]) < 1))
    r.append(("no quote -> no invented Perception price", "Perception consumption (your quote)" not in buy_cost(m, None)["lines"]))
    r.append(("break-even rises with the size of the SOC",
              breakeven_month(DATA["profiles"]["small"]) < be < breakeven_month(DATA["profiles"]["large"])))
    r.append(("sensitivity: maintenance is the biggest lever (medium)",
              sensitivity_rank("medium")[0][0] == "maintenance_weeks_per_agent_year"))
    r.append(("maintenance moves break-even more than build weeks",
              breakeven_month({**m, "maintenance_weeks_per_agent_year": m["maintenance_weeks_per_agent_year"] * 2})
              > breakeven_month({**m, "build_weeks_per_agent": m["build_weeks_per_agent"] * 2})))
    t.banner("Demo 06 self-test")
    return t.self_test_report(r)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--profile", choices=sorted(DATA["profiles"]), default="medium")
    p.add_argument("--quote", type=float, help="your Perception monthly consumption quote, USD")
    p.add_argument("--sensitivity", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    t.set_fast(a.fast)
    if a.self_test:
        return self_test()
    if a.sensitivity:
        sensitivity(a.profile)
    else:
        run(a.profile, a.quote)
    return 0


if __name__ == "__main__":
    sys.exit(main())
