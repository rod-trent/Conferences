# Browser demo site

**Deployed: [eldk2027-demos.vercel.app](https://eldk2027-demos.vercel.app)**

A static site that runs the six demos **in a browser**, so you can put it beside
the deck and click through the demos instead of alt-tabbing to a terminal. No
backend, no build step at deploy time.

It's the same runner as the WPNinjas 2027 and MMS 2026 sites, retargeted. The
palette and art match this deck, and the pause rules know this session's markers.

## How it works

The demos are pure Python standard library, so they run **unmodified** in the
browser via [Pyodide](https://pyodide.org) (CPython compiled to WebAssembly).
The page mounts the demo sources into Pyodide's virtual filesystem at the same
relative paths they use on disk, so `../common` imports and data files work.

If Pyodide cannot load — dead venue Wi-Fi on a first visit — the page plays a
transcript baked from the same code at build time. The status pill tells you which:

| Pill | Meaning |
|------|---------|
| `Python ready` (green) | running the real code in your tab |
| `recorded output` (amber) | playing a transcript baked from that same code |

A service worker caches the page, the demo sources, every transcript and the
Pyodide runtime, so once loaded in the room it keeps working offline.

## Stage controls

Playback pauses at the beats the demos mark in their own output:

- after every `>> WHY THIS MATTERS:` line
- before each `STEP n/N` and before the `VERDICT:`
- before every `REQUIRES HUMAN APPROVAL` gate
- in **at every step** mode, also on `[PASS]`/`[FAIL]`, `[BLOCKED]`/`[ALLOWED]`/`[WARN]`,
  `[tool]` calls, `[handoff]` lines and ranked items

| Key | Action |
|-----|--------|
| `space` | continue, or pause where you are |
| `→` | skip to the end |
| `r` | re-run the current variant |
| `1`–`9` | jump to that variant |
| `esc` | close |
| `+` / `-` / `0` | text size up / down / reset (remembered) |

## Deep links

```
?demo=handoff&v=1     the free-text handoff - an entity is lost
?demo=triage&v=1      threshold 0.60 - a real attack auto-closes
?demo=perception&v=1  Suggest an alternative at the gate
?demo=tco&v=1         sensitivity: what moves the break-even
?mode=fallback        rehearse the dead-network path
```

Demo ids and variant order are in `public/data/manifest.json`.

## Run it locally

Pyodide needs HTTP, not `file://`:

```bash
python -m http.server 8765 --directory web/public
# open http://localhost:8765
```

## Build

```bash
python web/build.py            # rebuild public/py, public/transcripts, public/data/manifest.json
python web/build.py --check    # fail if public/ is stale (run-all-tests.py runs this)
```

Everything under `public/py`, `public/transcripts` and `public/data` is
**generated**. Edit the demos, then rebuild — never edit those by hand.

## Deploy (Vercel)

The site is committed pre-built. `ELDK2027/vercel.json` points `outputDirectory` at `web/public` and has no build step. `.vercelignore` keeps the deck and the tooling out of the upload.

The Vercel project **`eldk2027-demos`** is connected to `rod-trent/Conferences` with **Root Directory = `ELDK2027`**, so **every push to `main` redeploys production**. The deck's QR codes point at `eldk2027-demos.vercel.app`.

To deploy by hand, run this from the **repo root**. The repo root's `.vercel` link belongs to the WPNinjas project, so pass this project's ids:

```bash
VERCEL_ORG_ID=team_NfjmdhUYN3lWcsTGFcCqCRg7 VERCEL_PROJECT_ID=prj_Lp5hKtVKKCK1nz2sCH2LLGxgpFEi npx vercel deploy --prod
```

Per-deployment URLs (`…-<hash>-<team>.vercel.app`) sit behind Vercel Authentication. The production alias is public.

After changing a demo:

```bash
cd ELDK2027
python web/build.py              # regenerate public/
python run-all-tests.py          # must be green - the drift check guards the site
git commit -am "..." && git push # Vercel deploys main
```
