#!/usr/bin/env python3
"""
build.py
========
Builds the WPNinjas US 2027 demo site in web/public/.

    python web/build.py            # build
    python web/build.py --check    # build to a temp dir and diff (CI drift guard)

What it does
------------
1. Copies the runnable demo sources into public/py/, preserving the directory
   layout so the scripts' relative imports and data-file paths work unchanged
   inside Pyodide's virtual filesystem.

2. Runs every demo variant locally with colour forced on, and bakes the output
   into public/transcripts/. That is the offline fallback: if Pyodide cannot
   load - dead conference Wi-Fi on first visit - the page plays the baked
   transcript instead, and it looks identical.

3. Writes public/data/manifest.json describing every card the site renders.

The demos are the single source of truth. Nothing here edits them, and CI runs
--check so the site can never drift from the code it claims to run.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import runpy
import shutil
import sys
import tempfile
from pathlib import Path

WEB = Path(__file__).resolve().parent
ROOT = WEB.parent
DEMOS = ROOT / "demos"

COMMON = "common"

# Files copied into the browser filesystem. Everything a script imports or
# reads at runtime has to be listed here.
PY_ASSETS = [
    f"{COMMON}/term.py",
    f"{COMMON}/shields.py",
    f"{COMMON}/runtime.py",
    "01-shield-the-model/shield_and_alert.py",
    "02-stop-the-tool-call/runtime_protection.py",
    "03-agent-on-the-endpoint/local_agent_protection.py",
    "04-find-every-agent/agent_posture.py",
    "04-find-every-agent/agentsinfo_sample.json",
    "05-hunt-the-agent-kill-chain/hunt_agents.py",
    "05-hunt-the-agent-kill-chain/hunting_sample.json",
    "06-red-team-your-agent/red_team_agent.py",
    "06-red-team-your-agent/attack_corpus.json",
]

# id, session, title, blurb, script, and the variants exposed as buttons.
DEMOS_MANIFEST: list[dict] = [
    {
        "id": "shield",
        "session": "agents",
        "title": "Shield the Model, Alert the SOC",
        "subtitle": "Demo 1 · slide 18",
        "blurb": "Prompt Shields annotates a jailbreak, Defender for AI Services raises the alert by its "
                 "exact Learn name, and the end-user context tells the SOC who and where. Then switch the "
                 "guardrail to annotate-only and watch 'blocked' become 'detected'.",
        "kind": "run",
        "script": "01-shield-the-model/shield_and_alert.py",
        "variants": [
            {"label": "Jailbreak, guardrail blocks", "args": ["--fast"], "primary": True},
            {"label": "Annotate-only guardrail", "args": ["--annotate-only", "--fast"]},
            {"label": "ASCII smuggling", "args": ["--scenario", "smuggling", "--fast"], "highlight": True},
            {"label": "Attack in a grounding doc", "args": ["--scenario", "document", "--fast"]},
            {"label": "No user context", "args": ["--no-user-context", "--fast"]},
            {"label": "Benign control", "args": ["--scenario", "benign", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "toolcall",
        "session": "agents",
        "title": "Stop the Tool Call",
        "subtitle": "Demo 2 · slide 22",
        "blurb": "A Copilot Studio agent reads a poisoned vendor email and decides to send the vendor "
                 "master list to a look-alike domain. Defender sees the tool call before it runs. Then "
                 "the three ways it goes wrong: audit-only, no Entra agent ID, and the one-second fail-open.",
        "kind": "run",
        "script": "02-stop-the-tool-call/runtime_protection.py",
        "variants": [
            {"label": "Custom block rule", "args": ["--fast"], "primary": True},
            {"label": "Default rule (audit)", "args": ["--rule", "audit", "--fast"], "highlight": True},
            {"label": "No Entra agent ID", "args": ["--no-agent-id", "--fast"]},
            {"label": "Late reply: fail-open", "args": ["--latency", "1400", "--fast"]},
            {"label": "Late reply: fail-closed",
             "args": ["--latency", "1400", "--error-behavior", "block", "--fast"]},
            {"label": "Benign control", "args": ["--benign", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "endpoint",
        "session": "agents",
        "title": "The Agent on Your Laptop",
        "subtitle": "Demo 3 · slide 24",
        "blurb": "A coding agent reads a README with an instruction hidden in invisible Unicode. Defender "
                 "for Endpoint AI agent runtime protection in Block, Audit and Disabled - plus the "
                 "documented preview issue that shows why inspection happens at more than one point.",
        "kind": "run",
        "script": "03-agent-on-the-endpoint/local_agent_protection.py",
        "variants": [
            {"label": "Block mode", "args": ["--fast"], "primary": True},
            {"label": "Audit mode", "args": ["--mode", "audit", "--fast"], "highlight": True},
            {"label": "Disabled", "args": ["--mode", "disabled", "--fast"]},
            {"label": "Agent ignores the block", "args": ["--agent-continues", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "posture",
        "session": "agents",
        "title": "Find Every Agent",
        "subtitle": "Demo 4 · slide 27",
        "blurb": "An AgentsInfo export scored the way the Defender portal's AI agents view does - risk "
                 "levels and risk indicators by their Learn names - plus the protection gaps posture "
                 "alone does not show you.",
        "kind": "run",
        "script": "04-find-every-agent/agent_posture.py",
        "variants": [
            {"label": "Inventory and risk", "args": ["--fast"], "primary": True},
            {"label": "Protection gaps only", "args": ["--gaps", "--fast"], "highlight": True},
            {"label": "Drill into Vendor Desk", "args": ["--agent", "Vendor Desk"]},
            {"label": "The KQL behind it", "args": ["--kql"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "hunt",
        "session": "agents",
        "title": "Hunt the Agent Kill Chain",
        "subtitle": "Demo 5 · slide 29",
        "blurb": "Five advanced hunting queries over a synthetic week: AI alerts, real-time protection "
                 "behaviors, what an audited agent did next, the attacker's IP pivot, and the posture "
                 "debt that turned into an incident.",
        "kind": "run",
        "script": "05-hunt-the-agent-kill-chain/hunt_agents.py",
        "variants": [
            {"label": "Full hunt", "args": ["--fast"], "primary": True},
            {"label": "Hunt 3: after the audit", "args": ["--hunt", "3", "--fast"], "highlight": True},
            {"label": "Hunt 4: IP pivot", "args": ["--hunt", "4", "--fast"]},
            {"label": "KQL only (to paste)", "args": ["--kql"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "redteam",
        "session": "agents",
        "title": "Red-Team Your Agent",
        "subtitle": "Demo 6 · slide 30",
        "blurb": "Twelve attacks and two benign controls through four layers, scored as Attack Success "
                 "Rate. It reports what gets through on purpose: Crescendo, non-English, and the polite "
                 "injection to a domain nobody has seen yet.",
        "kind": "run",
        "script": "06-red-team-your-agent/red_team_agent.py",
        "variants": [
            {"label": "All four layers", "args": ["--fast"], "primary": True},
            {"label": "Document shields off (default)", "args": ["--doc-shields-off", "--fast"],
             "highlight": True},
            {"label": "Prompt Shields alone", "args": ["--only", "L1", "--fast"]},
            {"label": "Why each payload matters", "args": ["--verbose", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
]


# ---------------------------------------------------------------------------
# Deck links
# ---------------------------------------------------------------------------
#
# The decks are not copied into the site: they are 15MB, .vercelignore keeps
# SlideDecks/ out of the deploy, and a second copy would drift. Instead the
# cards link the committed files on GitHub three ways:
#
#   view      Office's own web viewer, which renders a .pptx in the browser
#   download  GitHub's raw endpoint
#   open      the ms-powerpoint: URI, which hands it to desktop PowerPoint
#
# Check all three links once the repo is pushed.

import urllib.parse

REPO_RAW = "https://raw.githubusercontent.com/rod-trent/Conferences/main/WPNinjas2027/SlideDecks/"
REPO_DL = "https://github.com/rod-trent/Conferences/raw/main/WPNinjas2027/SlideDecks/"
OFFICE_VIEWER = "https://view.officeapps.live.com/op/view.aspx?src="


def deck_links(filename: str) -> dict:
    quoted = urllib.parse.quote(filename)
    raw = REPO_RAW + quoted
    return {
        "file": filename,
        "view": OFFICE_VIEWER + urllib.parse.quote(raw, safe=""),
        "download": REPO_DL + quoted,
        # PowerPoint's protocol handler wants the plain URL after "ofe|u|".
        "powerpoint": "ms-powerpoint:ofe|u|" + raw,
    }


DECK_FILE = "Defender for Agents - WPNinjas US 2027.pptx"

SESSIONS = {
    "agents": {
        "id": "agents",
        "title": "Defender for Agents",
        "subtitle": "Extending Threat Protection to Autonomous Workflows",
        "slot": "Workplace Ninjas US 2027 · Scottsdale, AZ · 11–13 January 2027",
        "presenters": "Rod Trent",
        "accent": "#FF7A2F",
        "deck": deck_links(DECK_FILE),
    },
}


# ---------------------------------------------------------------------------
# Baking transcripts
# ---------------------------------------------------------------------------


# Some demos stamp the moment they ran into their output - generated_utc,
# started_utc, and the run-log filename. Those change every build and are not
# drift. --check masks them so it compares what the demo actually produced.
VOLATILE = [
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})"),
    re.compile(r"run-\d+-\d+\.json"),
]


def normalise(raw: bytes) -> bytes:
    """Mask timestamps and line endings so --check compares content.

    Line endings vary with the developer's git checkout; timestamps vary with
    the clock. Neither is drift.
    """
    raw = raw.replace(b"\r\n", b"\n")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    for pattern in VOLATILE:
        text = pattern.sub("<TIMESTAMP>", text)
    return text.encode("utf-8")


def write_lf(path: Path, text: str) -> None:
    """Write text with LF endings on every platform.

    Without this, a Windows build emits CRLF, a Linux CI rebuild emits LF, and
    --check reports drift that is not there.
    """
    path.write_text(text, encoding="utf-8", newline="\n")


class TTYCapture(io.StringIO):
    """Captures stdout while claiming to be a terminal.

    The demos decide whether to emit ANSI colour with sys.stdout.isatty().
    Baked transcripts need the colour codes so the fallback looks identical to
    a live Pyodide run.
    """

    def isatty(self) -> bool:  # noqa: D102
        return True


def bake(script_rel: str, args: list[str]) -> str:
    """Run one demo variant and capture its coloured output."""
    script = DEMOS / script_rel
    cwd = os.getcwd()
    old_argv, old_stdout, old_path = sys.argv, sys.stdout, list(sys.path)
    buf = TTYCapture()

    try:
        os.chdir(script.parent)
        sys.argv = [str(script), *args]
        sys.stdout = buf
        # `python script.py` puts the script's directory on sys.path; runpy does
        # not. The demos rely on it for their sibling imports, and Pyodide needs
        # the same treatment - see assets/app.js.
        sys.path.insert(0, str(script.parent))
        try:
            runpy.run_path(str(script), run_name="__main__")
        except SystemExit:
            pass
    finally:
        os.chdir(cwd)
        sys.argv, sys.stdout, sys.path = old_argv, old_stdout, old_path
        # Demo modules cache module-level state; drop them so the next bake is clean.
        for name in ("term", "shields", "runtime"):
            sys.modules.pop(name, None)

    return buf.getvalue()




# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(out: Path) -> dict:
    py_dir = out / "py"
    tx_dir = out / "transcripts"
    data_dir = out / "data"

    for d in (py_dir, tx_dir, data_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    # 1. Copy the demo sources, normalising line endings to LF.
    #
    # Not cosmetic: git checks demos/ out as CRLF on Windows and LF on Linux, so
    # a byte-for-byte copy would make the build output depend on the developer's
    # checkout settings and --check would report drift that is not there.
    for rel in PY_ASSETS:
        src = DEMOS / rel
        if not src.exists():
            raise SystemExit(f"missing demo asset: {rel}")
        dst = py_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))

    # 2. Bake every variant.
    baked = 0
    for demo in DEMOS_MANIFEST:
        if demo["kind"] != "run":
            continue
        for i, variant in enumerate(demo["variants"]):
            text = bake(demo["script"], variant["args"])
            key = f"{demo['id']}-{i}"
            write_lf(tx_dir / f"{key}.txt", text)
            variant["transcript"] = key
            baked += 1
            print(f"  baked {key:<34} {len(text):>7,} chars  "
                  f"({' '.join(variant['args']) or 'no args'})")

    # 3. Manifest.
    manifest = {
        "generated_note": "Built by web/build.py. Do not edit by hand.",
        "repo": "https://github.com/rod-trent/Conferences/tree/main/WPNinjas2027",
        "event": {
            "name": "Workplace Ninjas US 2027",
            "location": "The Scott Resort & Spa, Scottsdale, AZ",
            "dates": "11–13 January 2027",
            "url": "https://workplaceninjas.us/",
        },
        "sessions": list(SESSIONS.values()),
        "pyAssets": PY_ASSETS,
        "demos": DEMOS_MANIFEST,
    }
    write_lf(data_dir / "manifest.json", json.dumps(manifest, indent=2) + "\n")

    print(f"\n  {len(PY_ASSETS)} sources copied, {baked} transcripts baked")
    return manifest


def main() -> int:
    # Transcripts must carry colour; a NO_COLOR in the caller's environment
    # (run-all-tests.py sets it) would bake plain text and look like drift.
    os.environ.pop("NO_COLOR", None)
    parser = argparse.ArgumentParser(description="Build the demo site.")
    parser.add_argument("--check", action="store_true",
                        help="Build to a temp dir and fail if it differs from public/.")
    args = parser.parse_args()

    public = WEB / "public"

    if not args.check:
        print("\nBuilding web/public ...")
        build(public)
        print(f"  -> {public}\n")
        return 0

    print("\nChecking web/public is up to date ...")
    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp) / "public"
        candidate.mkdir()
        build(candidate)

        drift: list[str] = []
        for sub in ("py", "transcripts", "data"):
            a, b = public / sub, candidate / sub
            if not a.exists():
                drift.append(f"{sub}/ missing from public/")
                continue
            a_files = {p.relative_to(a) for p in a.rglob("*") if p.is_file()}
            b_files = {p.relative_to(b) for p in b.rglob("*") if p.is_file()}
            for missing in sorted(b_files - a_files):
                drift.append(f"{sub}/{missing.as_posix()} missing")
            for extra in sorted(a_files - b_files):
                drift.append(f"{sub}/{extra.as_posix()} is stale")
            for common in sorted(a_files & b_files):
                if normalise((a / common).read_bytes()) != normalise((b / common).read_bytes()):
                    drift.append(f"{sub}/{common.as_posix()} differs")

    if drift:
        print("\n  web/public is out of date. The site would not match the demos:\n")
        for d in drift[:40]:
            print(f"    {d}")
        if len(drift) > 40:
            print(f"    ... and {len(drift) - 40} more")
        print("\n  Fix: python web/build.py\n")
        return 1

    print("\n  Up to date. The site runs exactly the committed demo code.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
