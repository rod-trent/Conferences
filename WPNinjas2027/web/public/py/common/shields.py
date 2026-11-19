"""
shields.py - a local, deterministic STAND-IN for prompt-attack classification.

What this is
------------
Azure AI Content Safety Prompt Shields is a trained classifier. This file is
not that. It is a small set of transparent heuristics that produce the same
*shape* of result, so the demos can show the end-to-end flow - prompt in,
annotation out, Defender alert raised, tool call blocked - offline, on a
locked-down laptop, with nothing to sign in to.

The heuristics are deliberately readable so the room can see WHY something
fired. They are also deliberately imperfect: demo 06 reports what they miss.

Shapes mirrored (Microsoft Learn, "Prompt Shields"):
  - Standalone Content Safety API: one userPrompt + up to five documents,
    returning userPromptAnalysis.attackDetected and
    documentsAnalysis[i].attackDetected.
  - Azure OpenAI annotations: prompt_filter_results[].content_filter_results
    .jailbreak / .indirect_attack  ->  {"filtered": bool, "detected": bool}

User prompt attack classes (Learn): Attempt to change system rules,
Embedding a conversation mockup, Role-Play, Encoding Attacks.
Document attack classes add: Manipulated Content, Allowing a compromised LLM
to access system infrastructures, Information Gathering, Availability, Fraud,
Malware.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# ASCII smuggling: Unicode "tag" characters (U+E0000-U+E007F) mirror ASCII but
# render as nothing. A human reviewer sees a clean sentence; the model reads
# the hidden instruction.
# --------------------------------------------------------------------------

TAG_BASE = 0xE0000


def smuggle(text: str) -> str:
    """Encode ASCII as invisible Unicode tag characters (for building payloads)."""
    return "".join(chr(TAG_BASE + ord(c)) for c in text if ord(c) < 0x80)


def reveal_smuggled(text: str) -> str:
    """Decode any tag characters back to ASCII so we can show what was hidden."""
    return "".join(chr(ord(c) - TAG_BASE) for c in text if TAG_BASE <= ord(c) <= TAG_BASE + 0x7F)


def visible(text: str) -> str:
    """What a human sees: the text with tag characters removed."""
    return "".join(c for c in text if not (TAG_BASE <= ord(c) <= TAG_BASE + 0x7F))


# --------------------------------------------------------------------------
# Heuristic rules
# --------------------------------------------------------------------------

USER_RULES: list[tuple[str, str]] = [
    ("Attempt to change system rules",
     r"\b(ignore|disregard|forget|override)\b.{0,40}\b(previous|prior|above|system|all)\b.{0,20}"
     r"\b(instructions?|rules|prompts?|guidelines)\b"),
    ("Attempt to change system rules",
     r"\b(developer|god|debug|unrestricted|jailbreak)\s+mode\b"),
    ("Attempt to change system rules",
     r"\byou (are|have been) (now )?(freed|unshackled|no longer bound)\b"),
    ("Role-Play",
     r"\b(pretend|act as|roleplay|role-play|you are now)\b.{0,60}\b(no (rules|restrictions|filters)|DAN|evil|unfiltered)\b"),
    ("Embedding a conversation mockup",
     r"(^|\n)\s*(assistant|system)\s*:\s*.{0,80}(sure|of course|here (is|are))"),
    ("Encoding Attacks",
     r"\b(decode|base64|rot13)\b.{0,40}\b(follow|execute|obey|run)\b"),
]

DOC_RULES: list[tuple[str, str]] = [
    ("Manipulated Content",
     r"\b(ai|assistant|agent|copilot|llm)\b.{0,40}\b(must|should|are instructed to|now)\b"),
    ("Manipulated Content",
     r"\b(ignore|disregard|override)\b.{0,40}\b(instructions?|rules|policy|previous)\b"),
    ("Information Gathering",
     r"\b(send|forward|email|post|upload|exfiltrate)\b.{0,60}\b(password|credential|secret|token|api key|\.env|"
     r"customer list|all (files|emails|records))\b"),
    ("Allowing a compromised LLM to access system infrastructures",
     r"\b(run|execute)\b.{0,30}\b(curl|wget|powershell|bash|iex|invoke-expression)\b|\|\s*(sh|bash|iex)\b"),
    ("Fraud",
     r"\b(change|update)\b.{0,30}\b(bank|iban|routing|payment|remit)\b.{0,30}\b(details?|account|to)\b"),
    ("Availability",
     r"\b(repeat|loop)\b.{0,30}\b(forever|1000+ times|indefinitely)\b"),
]

HIDDEN_MARKUP = re.compile(r"<!--.*?-->|<span[^>]*display:\s*none[^>]*>.*?</span>|color:\s*#?fff(fff)?\b",
                           re.I | re.S)
B64_BLOB = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}")


@dataclass
class Analysis:
    attack_detected: bool
    categories: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    smuggled: str = ""

    def as_api(self) -> dict:
        return {"attackDetected": self.attack_detected}


def _decode_b64_blobs(text: str) -> list[str]:
    out = []
    for blob in B64_BLOB.findall(text):
        try:
            decoded = base64.b64decode(blob + "=" * (-len(blob) % 4)).decode("utf-8")
        except Exception:  # noqa: BLE001 - not base64, carry on
            continue
        if decoded.isprintable() and len(decoded) > 8:
            out.append(decoded)
    return out


def _scan(text: str, rules: list[tuple[str, str]]) -> Analysis:
    cats: list[str] = []
    ev: list[str] = []
    hidden = reveal_smuggled(text)
    candidates = [visible(text)]
    if hidden:
        candidates.append(hidden)
        cats.append("Encoding Attacks")
        ev.append(f"invisible Unicode tag characters decode to: {hidden!r}")
    for decoded in _decode_b64_blobs(text):
        candidates.append(decoded)
    for cand in candidates:
        for cat, pattern in rules:
            m = re.search(pattern, cand, re.I)
            if m:
                if cat not in cats:
                    cats.append(cat)
                snippet = cand[max(0, m.start() - 10): m.end() + 10].strip().replace("\n", " ")
                ev.append(snippet)
    return Analysis(bool(cats), cats, ev, hidden)


def analyze_user_prompt(prompt: str) -> Analysis:
    return _scan(prompt, USER_RULES)


def analyze_document(doc: str) -> Analysis:
    a = _scan(doc, DOC_RULES + USER_RULES)
    if HIDDEN_MARKUP.search(doc) and a.attack_detected:
        a.evidence.append("instruction is hidden from the human reader (comment / invisible styling)")
    return a


def shield_prompt(user_prompt: str, documents: list[str] | None = None) -> dict:
    """Standalone Prompt Shields response shape."""
    documents = (documents or [])[:5]
    return {
        "userPromptAnalysis": analyze_user_prompt(user_prompt).as_api(),
        "documentsAnalysis": [analyze_document(d).as_api() for d in documents],
    }


def openai_annotations(user_prompt: str, documents: list[str] | None, *,
                       user_action: str = "block", doc_action: str = "annotate") -> dict:
    """Azure OpenAI-style prompt_filter_results annotation.

    user_action / doc_action mirror the guardrail configuration:
    "block" -> filtered=True when detected; "annotate" -> detected only.
    """
    u = analyze_user_prompt(user_prompt)
    d_hits = [analyze_document(d) for d in (documents or [])]
    d_detected = any(x.attack_detected for x in d_hits)
    return {
        "prompt_filter_results": [{
            "prompt_index": 0,
            "content_filter_results": {
                "jailbreak": {"filtered": u.attack_detected and user_action == "block",
                              "detected": u.attack_detected},
                "indirect_attack": {"filtered": d_detected and doc_action == "block",
                                    "detected": d_detected},
            },
        }]
    }
