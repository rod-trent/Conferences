"""
term.py - shared terminal helpers for the WPNinjas 2027 "Defender for Agents" demos.

Pure standard library so every demo runs unchanged in CPython and in Pyodide
(the browser demo site). Colour is emitted only when stdout is a terminal, or
when the site's runner pretends to be one.

The output markers below are load-bearing: the demo site pauses playback on
them so the presenter can talk.

    STEP n/N  <title>          pause BEFORE  (what is about to happen)
    >> WHY THIS MATTERS: ...   pause AFTER   (what just happened)
    VERDICT: ...               pause BEFORE  (the payoff)
    [PASS] / [FAIL]            pause AFTER in "every step" mode
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
import time

WIDTH = 78


def _colour_on() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class C:
    """ANSI codes, resolved lazily so a redirected stdout gets plain text."""

    @staticmethod
    def wrap(code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if _colour_on() else text


def bold(t: str) -> str: return C.wrap("1", t)
def dim(t: str) -> str: return C.wrap("2", t)
def red(t: str) -> str: return C.wrap("31", t)
def green(t: str) -> str: return C.wrap("32", t)
def yellow(t: str) -> str: return C.wrap("33", t)
def blue(t: str) -> str: return C.wrap("34", t)
def magenta(t: str) -> str: return C.wrap("35", t)
def cyan(t: str) -> str: return C.wrap("36", t)


FAST = False


def set_fast(on: bool) -> None:
    global FAST
    FAST = on


def pause(seconds: float) -> None:
    """Pacing for a live terminal run. The browser runner no-ops time.sleep."""
    if not FAST:
        time.sleep(seconds)


def rule(char: str = "=") -> None:
    print(dim(char * WIDTH))


def banner(title: str, subtitle: str = "") -> None:
    rule()
    print(bold(" " + title))
    if subtitle:
        print(dim(" " + subtitle))
    rule()


def step(n: int, total: int, title: str) -> None:
    print()
    print(bold(cyan(f"STEP {n}/{total}  {title}")))
    print(dim("-" * WIDTH))
    pause(0.4)


def why(text: str) -> None:
    head = ">> WHY THIS MATTERS: "
    lines = textwrap.wrap(head + text, WIDTH, subsequent_indent="   ")
    print()
    print(yellow(head) + lines[0][len(head):])
    for line in lines[1:]:
        print(line)
    pause(0.6)


def say(text: str, indent: int = 2) -> None:
    for line in textwrap.wrap(text, WIDTH - indent) or [""]:
        print(" " * indent + line)


def kv(key: str, value: str, width: int = 22, indent: int = 2) -> None:
    print(" " * indent + dim(f"{key:<{width}}") + str(value))


def tool(name: str, detail: str = "") -> None:
    print(f"  {magenta('[tool]')} {bold(name)} {dim(detail)}")
    pause(0.25)


def ok(text: str) -> None:
    print(f"  {green('[PASS]')} {text}")


def fail(text: str) -> None:
    print(f"  {red('[FAIL]')} {text}")


def warn(text: str) -> None:
    print(f"  {yellow('[WARN]')} {text}")


def block(text: str) -> None:
    print(f"  {red('[BLOCKED]')} {text}")


def allow(text: str) -> None:
    print(f"  {green('[ALLOWED]')} {text}")


def show_json(obj, indent: int = 4) -> None:
    pad = " " * indent
    for line in json.dumps(obj, indent=2).splitlines():
        print(pad + dim(line) if line.strip() in "{}[]," else pad + line)


def verdict(text: str, good: bool = True) -> None:
    print()
    colour = green if good else red
    print(bold(colour("VERDICT: " + text)))


def synthetic_notice() -> None:
    print(dim("  Synthetic data. 'Contoso Outdoors', its agents, users and incidents are"))
    print(dim("  fabricated for teaching. Detection logic here is a local stand-in for the"))
    print(dim("  Microsoft services named - it illustrates the flow, it is not the product."))


def self_test_report(results: list[tuple[str, bool]]) -> int:
    print()
    passed = 0
    for name, good in results:
        (ok if good else fail)(name)
        passed += int(good)
    print()
    line = f"  {passed}/{len(results)} checks passed"
    print(green(line) if passed == len(results) else red(line))
    return 0 if passed == len(results) else 1
