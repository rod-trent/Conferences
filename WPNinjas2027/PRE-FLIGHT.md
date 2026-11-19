# Pre-flight — Defender for Agents, WPNinjas US 2027

## Run order and timing (60 minutes)

| Slides | Section | Demo | Minutes |
|---|---|---|---|
| 1–4 | Opening, hook, agenda | | 6 |
| 5–9 | Why agents change the threat model | | 11 |
| 10–12 | The Defender map, what changed in 2026 | | 6 |
| 13–18 | Shield the model | **Demo 1** (slide 18) | 13 |
| 19–24 | Runtime protection | **Demo 2** (slide 22), **Demo 3** (slide 24) | 16 |
| 25–30 | Know, hunt, prove | **Demos 4, 5, 6** (slides 27, 29, 30) | 13 |
| 31–33 | Monday morning, resources, Q&A | | 5+ |

That is over 60 with every demo at full length. If time is short, cut in this
order: Demo 4 to its "Protection gaps only" variant; Demo 3 to Block then Audit;
Demo 6 to the "Document shields off" variant only. Demo 2 is the one to protect.

## Facts most likely to have changed by January — check the week before

Every one of these was true on 19 November 2026 (see [SOURCES.md](SOURCES.md)).

- [ ] **Dec 23, 2026 retirement** of the legacy Copilot Studio onboarding happened
      as planned, and agents without a blocking rule are in audit mode (slides 12, 21).
- [ ] **Automatic tenant-level onboarding** (public preview from Nov 22, 2026) —
      still preview, or GA? (slide 12)
- [ ] **Coverage table** on the real-time protection page: Copilot Studio still
      "tool invocations only"? Foundry still preview? (slide 21)
- [ ] **Defender for Endpoint AI agent runtime protection** — still preview; named
      agents unchanged; prompt evidence still on-by-default "in an upcoming release"? (slide 23)
- [ ] **Alerts for AI services** list unchanged, especially anything new for
      indirect injection (slide 17, demo 01).
- [ ] **Foundry guardrails** — tool call / tool response intervention points still
      preview (slide 15).
- [ ] **Agent 365 licensing** wording (slides 12, 28).
- [ ] **The two Learn disagreements** listed at the bottom of SOURCES.md — resolved?

If something moved, update `deck/build/deck.js`, run `node deck.js`, and fix the
matching demo text; `python run-all-tests.py` tells you if the site drifted.

## Morning-of checklist

- [ ] `python run-all-tests.py` → **All green**.
- [ ] Open the demo site on the venue network once, so the service worker caches
      Pyodide and every transcript. The status pill should read **Python ready**.
- [ ] Rehearse the dead-network path: open `?mode=fallback` — the pill should read
      **recorded output (forced)** and every demo should still play.
- [ ] Set the text size with `A+` for the back of the room (it is remembered).
- [ ] Pause mode **at stages** (default). `space` continues, `→` skips to the end.
- [ ] Demo slides link to [wpninjas2027-demos.vercel.app](https://wpninjas2027-demos.vercel.app) `?demo=<id>`
      (ids: `shield`, `toolcall`, `endpoint`, `posture`, `hunt`, `redteam`).
      Add `&v=<n>` to land on a specific variant.
- [ ] If you changed a demo: `npx vercel deploy --prod` from `WPNinjas2027/` —
      the Vercel project is not Git-connected, so a push alone does not redeploy.
- [ ] Have the terminal fallback ready: every demo runs with `python <script> --fast`.

## Things to say out loud

- The detection logic in the demos is a local stand-in; the flow, names and
  shapes are Microsoft's. Say it once, at Demo 1.
- Audit is visibility, not protection. (Demo 2, Demo 3, Demo 5.)
- An agent with no Microsoft Entra agent ID cannot be scoped into a custom block rule.
- Document attack detection is off by default in Foundry.
- One second, default allow.
