#!/usr/bin/env python3
"""
build.py
========
Builds the Experts Live Denmark 2027 demo site in web/public/.

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
    "01-design-the-agent/agent_review.py",
    "01-design-the-agent/agents.json",
    "02-triage-and-teach/triage_agent.py",
    "02-triage-and-teach/alerts.json",
    "03-hand-off/soc_handoffs.py",
    "04-detection-engineering/detection_agent.py",
    "05-perception-playbook/perception_playbook.py",
    "06-build-vs-buy/build_vs_buy.py",
    "06-build-vs-buy/assumptions.json",
]

# id, session, title, blurb, script, and the variants exposed as buttons.
DEMOS_MANIFEST: list[dict] = [
    {
        "id": "design",
        "session": "soc",
        "title": "Design Review for SOC Agents",
        "subtitle": "Demo 1 · slide 10",
        "blurb": "Four agents - one Microsoft-built, three custom - scored against twelve controls Microsoft "
                 "documents: identity, sponsor, least privilege, approval on hard actions, evaluation, "
                 "lifecycle. Then rebuild the worst one without touching its prompt.",
        "kind": "run",
        "script": "01-design-the-agent/agent_review.py",
        "variants": [
            {"label": "Scorecard", "args": ["--fast"], "primary": True},
            {"label": "Least-privilege rebuild", "args": ["--fix", "Auto-Containment Bot", "--fast"], "highlight": True},
            {"label": "Drill into Nordlys Enrichment", "args": ["--agent", "Nordlys Enrichment", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "triage",
        "session": "soc",
        "title": "Triage, With a Human in the Loop",
        "subtitle": "Demo 2 · slide 12",
        "blurb": "A triage agent resolves the false positives it is sure of and leaves the rest with an "
                 "analyst. Lower the threshold and it closes a real attack. Teach it narrowly, and the "
                 "conflict check stops the lesson that would have closed vendor fraud.",
        "kind": "run",
        "script": "02-triage-and-teach/triage_agent.py",
        "variants": [
            {"label": "Threshold 0.90", "args": ["--fast"], "primary": True},
            {"label": "Threshold 0.60", "args": ["--threshold", "0.6", "--fast"], "highlight": True},
            {"label": "Teach the agent", "args": ["--teach", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "handoff",
        "session": "soc",
        "title": "The Handoff Chain",
        "subtitle": "Demo 3 · slide 19",
        "blurb": "Triage, Investigation, Detection Engineering and Posture Remediation work one AiTM "
                 "incident through a typed handoff envelope and an approval gate. Then break it four ways: "
                 "a prose handoff, a loop, a race, and no gate.",
        "kind": "run",
        "script": "03-hand-off/soc_handoffs.py",
        "variants": [
            {"label": "Structured + gate", "args": ["--fast"], "primary": True},
            {"label": "Free-text handoff", "args": ["--free-text", "--fast"], "highlight": True},
            {"label": "Handoff loop", "args": ["--loop", "--fast"]},
            {"label": "Two writers", "args": ["--race", "--fast"]},
            {"label": "No approval gate", "args": ["--no-gate", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "detection",
        "session": "soc",
        "title": "The Detection Engineering Agent",
        "subtitle": "Demo 4 · slide 20",
        "blurb": "Three candidate rules - IOC, broad, behavioural - back-tested against a week of telemetry "
                 "before anyone is asked to enable one. Then the version where the agent ships first.",
        "kind": "run",
        "script": "04-detection-engineering/detection_agent.py",
        "variants": [
            {"label": "Back-test, then ask", "args": ["--fast"], "primary": True},
            {"label": "Ship first", "args": ["--ship-first", "--fast"], "highlight": True},
            {"label": "The KQL", "args": ["--kql"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "perception",
        "session": "soc",
        "title": "A Microsoft Perception Playbook",
        "subtitle": "Demo 5 · slide 27",
        "blurb": "The documented 'Protect against a threat' playbook: Threat Intelligence, Recon, Posture "
                 "Prioritization, Detection Authoring and Attack Investigation - one session, one approval "
                 "gate. Plus what you can't do: run without a required agent, or write your own playbook.",
        "kind": "run",
        "script": "05-perception-playbook/perception_playbook.py",
        "variants": [
            {"label": "Approve", "args": ["--fast"], "primary": True},
            {"label": "Suggest an alternative", "args": ["--decision", "suggest", "--fast"], "highlight": True},
            {"label": "Reject", "args": ["--decision", "reject", "--fast"]},
            {"label": "Stop", "args": ["--decision", "stop", "--fast"]},
            {"label": "Recon Agent disabled", "args": ["--disable", "Recon Agent", "--fast"]},
            {"label": "Custom playbook?", "args": ["--custom", "--fast"]},
            {"label": "Self-test", "args": ["--self-test"]},
        ],
    },
    {
        "id": "tco",
        "session": "soc",
        "title": "Build vs. Buy: the Three-Year View",
        "subtitle": "Demo 6 · slide 31",
        "blurb": "A transparent three-year cost model: Microsoft's facts ($6 overage SCU, the E5 SCU "
                 "inclusion, two 2027 retirements) plus your assumptions - and, because there is no public "
                 "Perception rate card, a break-even instead of an invented price.",
        "kind": "run",
        "script": "06-build-vs-buy/build_vs_buy.py",
        "variants": [
            {"label": "Mid-size SOC", "args": ["--fast"], "primary": True},
            {"label": "Sensitivity", "args": ["--sensitivity", "--fast"], "highlight": True},
            {"label": "Small SOC", "args": ["--profile", "small", "--fast"]},
            {"label": "Large SOC", "args": ["--profile", "large", "--fast"]},
            {"label": "With a $12k/month quote", "args": ["--quote", "12000", "--fast"]},
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

REPO_RAW = "https://raw.githubusercontent.com/rod-trent/Conferences/main/ELDK2027/SlideDecks/"
REPO_DL = "https://github.com/rod-trent/Conferences/raw/main/ELDK2027/SlideDecks/"
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


DECK_FILE = "The Agentic SOC - Experts Live Denmark 2027.pptx"

SESSIONS = {
    "soc": {
        "id": "soc",
        "title": "The Agentic SOC",
        "subtitle": "Best Practices for Custom Agents, Role Handoffs, and Why Microsoft Perception Is More "
                    "Supportable and Cost-Effective",
        "slot": "Experts Live Denmark 2027 · Bella Center Copenhagen · 9–10 February 2027",
        "presenters": "Rod Trent",
        "accent": "#008BD2",
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
        for name in ("term",):
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
        "repo": "https://github.com/rod-trent/Conferences/tree/main/ELDK2027",
        "event": {
            "name": "Experts Live Denmark 2027",
            "location": "Bella Center Copenhagen",
            "dates": "9–10 February 2027",
            "url": "https://eldk27.expertslive.dk/",
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
