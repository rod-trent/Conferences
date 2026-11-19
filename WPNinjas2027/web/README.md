# Browser demo site

**Deployed: [wpninjas2027-demos.vercel.app](https://wpninjas2027-demos.vercel.app)**

A static site that runs the six demos **in a browser**, so you can put it beside
the deck and click through the demos instead of alt-tabbing to a terminal. No
backend, no build step at deploy time.

It is the same runner as the MMS 2026 sessions' site, retargeted: palette and
art match this deck, and the pause rules know this session's markers.

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
- in **at every step** mode, also on `[PASS]`/`[FAIL]`, `[BLOCKED]`/`[ALLOWED]`/`[WARN]`,
  `[tool]` calls and red-team scorecard rows

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
?demo=shield&v=2      ASCII smuggling
?demo=toolcall&v=1    the default (audit) rule — the data leaves
?demo=toolcall&v=3    fail-open
?demo=endpoint&v=1    Audit mode on the laptop
?demo=hunt&v=1        hunt 3: what the audited agent did next
?demo=redteam&v=1     document shields off
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

The site is committed pre-built. The Vercel project **`wpninjas2027-demos`**
is connected to `rod-trent/Conferences` with **Root Directory = `WPNinjas2027`**,
so **every push to `main` redeploys production** (other branches get preview
deployments). `WPNinjas2027/vercel.json` points `outputDirectory` at
`web/public` with no build step; `.vercelignore` keeps the deck and tooling out.

After changing a demo:

```bash
cd WPNinjas2027
python web/build.py              # regenerate public/
python run-all-tests.py          # must be green - the drift check guards the site
git commit -am "..." && git push # Vercel deploys main
```

A manual deploy still works, but run it from the **repo root** (the project's
Root Directory is `WPNinjas2027`): `npx vercel deploy --prod`.

Per-deployment URLs (`…-<hash>-<team>.vercel.app`) sit behind Vercel
Authentication; the production alias above is public.
