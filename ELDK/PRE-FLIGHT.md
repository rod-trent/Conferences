# Pre-flight — The Agentic SOC, Experts Live Denmark 2027

## Run order and timing

Experts Live technical sessions run 50 or 60 minutes, including 5–10 minutes for questions. Confirm your slot length in the Event Hub.

| Slides | Section | Demo | Minutes |
|---|---|---|---|
| 1–4 | Opening, hook, agenda | | 5 |
| 5–12 | Design agents you can govern | **Demo 1** (slide 10), **Demo 2** (slide 12) | 15 |
| 13–20 | Build your own SOC agents | **Demo 3** (slide 19), **Demo 4** (slide 20) | 17 |
| 21–27 | Microsoft Perception | **Demo 5** (slide 27) | 12 |
| 28–35 | Build vs. buy, close | **Demo 6** (slide 31) | 11 |

That adds up to more than 50 minutes with every demo at full length. If time is short, cut in this order:

1. Demo 4 down to "Ship first" only.
2. Demo 1 down to the scorecard.
3. Slide 15 (building blocks): talk over it in 30 seconds.

Demo 3 is the one to protect.

## Event logistics (from the call for speakers)

- [ ] The first draft deck is due in the Event Hub by **20 Jan 2027** and the final upload by **3 Feb 2027**. Experts Live asks speakers to use its official PowerPoint template. This deck uses the event's colours and logo; move it onto the template if they require it.
- [ ] The guidelines say "Commercial content is not allowed". The title argues for a Microsoft product, so keep the comparison fair, as slide 29 does, and check the framing with the organisers if you're unsure.

## Facts most likely to change before February: check the week before

Every one of these was true on 19 November 2026 (see [SOURCES.md](SOURCES.md)).

- [ ] **Perception status.** Ignite said "will be generally available", but several Learn pages still say limited, invitation-only preview. Has GA happened? (Slides 22 and 26.)
- [ ] **Custom playbooks.** Still "You can't create custom playbooks in this release"? This drives slides 24, 29 and 32 and Demo 5's `--custom` variant.
- [ ] **Recon Agent.** Still Azure-only? (Slides 23 and 29, Demo 5.)
- [ ] **Web App Pen Test Agent** added to Learn? If so, add it to slide 23 and `AGENTS` in Demo 5.
- [ ] **Perception pricing.** Has a rate card been published? If so, add it to `assumptions.json` and slide 30.
- [ ] **Custom agents and Entra Agent ID.** Is "Create an agent identity" still Microsoft-built agents only? (Slide 6, Demo 1.)
- [ ] **31 March 2027 retirements** (Foundry classic connected agents, Sentinel in the Azure portal) still on schedule? (Slides 9 and 33, Demos 1 and 6.)
- [ ] **E5/E7 Security Copilot inclusion** numbers unchanged? (Slide 30, Demo 6.)

If something moved, update `deck/build/deck.js`, run `node deck.js`, and fix the matching demo. `python run-all-tests.py` tells you if the site has drifted.

## Morning-of checklist

- [ ] `python run-all-tests.py` → **All green**.
- [ ] Open the demo site on the venue network once, so the service worker caches Pyodide and every transcript. The status pill should read **Python ready**.
- [ ] Rehearse the dead-network path: open `?mode=fallback`. The pill should read **recorded output (forced)**, and every demo should still play.
- [ ] Set the text size with `A+` for the back of the room. The site remembers it.
- [ ] Leave pause mode on **at stages** (the default). `space` continues, `→` skips to the end. Choose **at every step** for Demo 3 if you want to stop on each `[handoff]` line.
- [ ] The demo slides link to `eldk2027-demos.vercel.app/?demo=<id>` (ids: `design`, `triage`, `handoff`, `detection`, `perception`, `tco`). Add `&v=<n>` to land on a specific variant.
- [ ] Have the terminal fallback ready: every demo runs with `python <script> --fast`.

## Things to say out loud

- Once, at Demo 1: the agent logic in the demos is a deterministic stand-in. The names, controls and flows are Microsoft's.
- Once, at Demo 5: it models the documented Perception flow. Perception's internals are not public.
- At Demo 6: every number that isn't from Microsoft is an assumption. Fork it.
- Multi-agent SOCs fail in the handoffs.
- The cost of an agent is the years you run it.
