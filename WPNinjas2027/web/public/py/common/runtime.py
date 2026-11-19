"""
runtime.py - a local STAND-IN for tool-invocation inspection at agent runtime.

Mirrors the decision Microsoft Defender makes when an agent is about to invoke
a tool (Copilot Studio external threat detection, Defender XDR real-time
protection rules, Defender for Endpoint local agent runtime protection):

    proposed tool call + planner context  ->  allow | block (+ detection type)

Detection-type labels are the ones Microsoft Learn lists for Defender XDR
real-time protection rules:

    Secret exfiltration
    Malicious content propagation
    Evasion techniques
    Unsafe email domain        (evaluated at the tool REQUEST point only)

The logic is transparent heuristics, not Microsoft's models. It exists so the
flow can be shown offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import shields

SECRET = re.compile(
    r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|password\s*[:=]\s*\S+|client_secret\s*[:=]\s*\S+|"
    r"AccountKey=[A-Za-z0-9+/=]{20,})", re.I)

URL = re.compile(r"https?://([A-Za-z0-9.-]+)", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
PIPE_TO_SHELL = re.compile(r"(curl|wget|iwr|invoke-webrequest)[^|]*\|\s*(sh|bash|iex|invoke-expression)", re.I)

# Tenant-specific context a real deployment learns; here it is configuration.
TRUSTED_DOMAINS = {"contoso-outdoors.com", "contoso-outdoors.onmicrosoft.com", "sharepoint.com",
                   "microsoft.com", "github.com", "pypi.org"}
KNOWN_BAD_DOMAINS = {"contoso-0utdoors.com", "vendor-remit-portal.net", "paste-drop.io",
                     "cdn-update-check.xyz"}

OUTBOUND_TOOLS = {"SendEmail", "PostToWebhook", "UploadFile", "HttpRequest", "ShareFile",
                  "Bash", "Shell", "RunCommand", "WebFetch"}


@dataclass
class Decision:
    block: bool
    detections: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def reason_code(self) -> int | None:
        codes = {"Secret exfiltration": 101, "Malicious content propagation": 102,
                 "Evasion techniques": 103, "Unsafe email domain": 104}
        return codes.get(self.detections[0]) if self.detections else None


def _domains(text: str) -> set[str]:
    out = {m.lower() for m in URL.findall(text)}
    out |= {m.lower() for m in EMAIL.findall(text)}
    return out


def _untrusted(domain: str) -> bool:
    return not any(domain == t or domain.endswith("." + t) for t in TRUSTED_DOMAINS)


def inspect_tool_call(tool: str, inputs: dict, *, user_message: str = "",
                      previous_tool_outputs: list[str] | None = None) -> Decision:
    """Decide whether a proposed tool invocation should run."""
    prev = previous_tool_outputs or []
    blob = " ".join(str(v) for v in inputs.values())
    d = Decision(False)

    def hit(kind: str, why: str) -> None:
        if kind not in d.detections:
            d.detections.append(kind)
        d.reasons.append(why)

    outbound = tool in OUTBOUND_TOOLS
    dests = _domains(blob)

    # 1. Unsafe email domain - judged on the request itself.
    if tool == "SendEmail":
        for dom in dests:
            if dom in KNOWN_BAD_DOMAINS:
                hit("Unsafe email domain", f"recipient domain {dom} is a known look-alike / malicious domain")

    # 2. Secret exfiltration - a secret in the arguments of an outbound tool.
    if outbound and SECRET.search(blob):
        hit("Secret exfiltration", "outbound tool arguments contain a credential-shaped string")

    # 3. Malicious content propagation - the arguments carry content that came
    #    from an injected source, or a known-bad destination, or pipe-to-shell.
    injected_prev = [p for p in prev if shields.analyze_document(p).attack_detected]
    if outbound and injected_prev:
        for dom in dests:
            if _untrusted(dom):
                hit("Malicious content propagation",
                    f"tool output earlier in this turn carried injected instructions; this call sends to {dom}")
                break
    if outbound and any(dom in KNOWN_BAD_DOMAINS for dom in dests) and tool != "SendEmail":
        hit("Malicious content propagation", "destination is a known-bad domain")
    if PIPE_TO_SHELL.search(blob):
        hit("Malicious content propagation", "downloads remote content and pipes it straight into a shell")

    # 4. Evasion techniques - hidden or encoded content in what the agent is about to do.
    if shields.reveal_smuggled(blob) or shields.reveal_smuggled(user_message):
        hit("Evasion techniques", "invisible Unicode tag characters in the tool arguments or prompt")
    if re.search(r"(-enc(odedcommand)?\s+[A-Za-z0-9+/=]{16,}|base64\s+-d)", blob, re.I):
        hit("Evasion techniques", "encoded command line")

    d.block = bool(d.detections)
    return d
