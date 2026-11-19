#!/usr/bin/env python3
"""
run-all-tests.py - every self-test, every site variant, and the site drift check.

    python run-all-tests.py

No dependencies, no network, no tenant. Exit code 0 means the demos you are
about to put on a projector do what the slides say they do.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMOS = ROOT / "demos"

SELF_TESTS = [
    "01-design-the-agent/agent_review.py",
    "02-triage-and-teach/triage_agent.py",
    "03-hand-off/soc_handoffs.py",
    "04-detection-engineering/detection_agent.py",
    "05-perception-playbook/perception_playbook.py",
    "06-build-vs-buy/build_vs_buy.py",
]


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       env={"NO_COLOR": "1", "PYTHONIOENCODING": "utf-8", **_env()})
    return p.returncode, (p.stdout + p.stderr)


def _env() -> dict:
    import os
    return {k: v for k, v in os.environ.items() if k not in ("NO_COLOR",)}


def main() -> int:
    t0 = time.time()
    failures = 0
    print("\nSelf-tests")
    for rel in SELF_TESTS:
        script = DEMOS / rel
        code, out = run([sys.executable, script.name, "--self-test"], script.parent)
        summary = [l for l in out.splitlines() if "checks passed" in l]
        status = "ok  " if code == 0 else "FAIL"
        failures += code != 0
        print(f"  [{status}] {rel:<52} {summary[-1].strip() if summary else ''}")
        if code:
            print(out)

    print("\nEvery variant the demo site exposes")
    sys.path.insert(0, str(ROOT / "web"))
    import build  # noqa: E402
    for demo in build.DEMOS_MANIFEST:
        if demo["kind"] != "run":
            continue
        script = DEMOS / demo["script"]
        for v in demo["variants"]:
            code, out = run([sys.executable, script.name, *v["args"]], script.parent)
            ok = code == 0 and "Traceback" not in out
            failures += not ok
            print(f"  [{'ok  ' if ok else 'FAIL'}] {demo['id']:<16} {' '.join(v['args']) or '(no args)'}")
            if not ok:
                print(out[-2000:])

    print("\nSite drift check")
    code, out = run([sys.executable, "build.py", "--check"], ROOT / "web")
    failures += code != 0
    print(f"  [{'ok  ' if code == 0 else 'FAIL'}] web/public matches the demo sources")
    if code:
        print(out[-2000:])

    print(f"\n{'All green' if not failures else f'{failures} failure(s)'} in {time.time() - t0:.1f}s\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
