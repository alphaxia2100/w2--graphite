# Handoff — w2-graphite (AWS SAA-C03 "Speedrun" study app)

_Last updated: 2026-07-01. Branch of record: `feat/draw-editor-v1` (@ `1eb2d41c` at write time)._

## 1. What this is

A fork of [Anki](https://github.com/ankitects/anki) (AGPL-3.0) for the **Speedrun** project:
fork Anki, pick one exam, build a desktop + mobile study app, make a real Rust engine
change, and measure **Memory / Performance / Readiness** honestly. Chosen exam: **AWS
Certified Solutions Architect – Associate (SAA-C03)**.

**Chosen study feature — the "draw-it-from-blank" diagram card:** the learner draws an
architecture (or any graph-structured concept) from a blank prompt, an AI describes/checks
it against a reference shown *only after* the attempt, and the **learner makes the final
self-grade**. Rationale, evidence, and the falsifiable ablation hypothesis are in
[`BrainLift.md`](BrainLift.md); the product spec is in [`PRD.md`](PRD.md).

**Verdict from the BrainLift:** build it as a *measurement/calibration* instrument, not a
"learn AWS faster than Anki" tool — see [`memory/brainlift-saa-key-risks.md`](memory/brainlift-saa-key-risks.md).

## 2. Where things are (repo map)

| Path | What |
|---|---|
| [`BrainLift.md`](BrainLift.md) | Research-backed BrainLift (7 spiky POVs, experts, knowledge tree, verdict). |
| [`PRD.md`](PRD.md) | Product spec for the draw-from-blank card (domain-agnostic). |
| [`memory/`](memory/) | Project context notes (goals, risks). |
| [`examples/reference-graphs/`](examples/reference-graphs/) | Typed-graph fixtures: water cycle + AWS multi-AZ. The card is domain-agnostic. |
| [`docs/research/trackpad-and-editor.md`](docs/research/trackpad-and-editor.md) | Sourced research behind the editor + trackpad choices. |
| [`web/draw-editor/`](web/draw-editor/) | **Standalone dev sandbox** for the editor: `index.html`, `serve.py`, `serve-trackpad.py`, `shot.py` (screenshot/probe harness). |
| [`qt/aqt/drawcard.py`](qt/aqt/drawcard.py) | **In-Anki integration**: native dialog + trackpad capture. |
| [`qt/aqt/drawcard_web/`](qt/aqt/drawcard_web/) | The editor page used inside Anki (`?chrome=native`). |
| [`qt/aqt/main.py`](qt/aqt/main.py) | Tools-menu action (`action_drawcard`, ~line 1451). |
| [`experiments/trackpad-spike/`](experiments/trackpad-spike/) | The de-risk spike (merged to main via PR #11). |

## 3. Branch map

- **`main`** — BrainLift, PRD, reference fixtures, research doc, trackpad spike (all merged/pushed).
- **`feat/draw-editor-v1`** — everything above **plus** the editor, trackpad lock-in, and Anki source integration. **This is the working branch; it is NOT yet merged to `main`.**
- `cursor/run-and-improve-ui-b566` — a **separate** session's parallel work: a *real reviewer card type* + sample decks + review-UI polish. Not ours; worth reconciling (see §7).
- `cursor/revise-brainlift-spiky-povs-b566` — another session's BrainLift revision.

> ⚠️ **Durability:** the sandbox environment can reset between sessions and wipe the local
> checkout. The only thing that saved the work was that branches are pushed to GitHub.
> **Push early; consider merging `feat/draw-editor-v1` → `main`.**

## 4. Build & run (macOS)

Path must contain **no spaces** (Anki's build requirement).

```bash
# One-time toolchain (survives resets in ~/.cargo):
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.92.0 --profile minimal
export PATH="$HOME/.cargo/bin:$PATH"
git clone https://github.com/alphaxia2100/w2--graphite.git ~/Developer/w2-graphite
cd ~/Developer/w2-graphite && git checkout feat/draw-editor-v1
bash tools/install-n2                      # build driver (compiles n2 into ~/.cargo/bin)

# Build (regenerates out/pyenv; ~3 min with cached crates):
./ninja pylib qt

# Trackpad needs pyobjc in the built env (REINSTALL after every rebuild — out/pyenv is wiped):
out/pyenv/bin/python -m pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz

# Run Anki, then Tools → "Draw-it-from-blank…"
./run
```

Headless engine smoke test (no GUI): see the pattern used during dev — load `anki`, create a
collection, add/read a note. The editor page also has self-tests: open
`web/draw-editor/index.html?tptest=1` (draw path) or `?selftest=1` (reveal/self-grade) via
`web/draw-editor/serve.py` / `shot.py`.

## 5. The feature today

**In Anki:** `Tools → "Draw-it-from-blank…"` opens a native Anki dialog — a themed toolbar
(prompt label + Trackpad/Done buttons) above an Excalidraw canvas.

**Controls:** **Space** = lock in and draw with one finger (absolute trackpad mapping);
**2-finger drag** move the region, **pinch** resize it (while unlocked); **Space/Esc** =
unlock. Settings (pan/pinch speed, smoothing, stroke width, invert) live in Excalidraw's
**☰** menu. Reveal shows the reference + optional rubric self-checklist + Again/Hard/Good/Easy.

## 6. How the trackpad works (architecture)

The hard part — absolute trackpad drawing inside a webview — is solved with **public macOS
APIs only** (validated by the spike; details in [`docs/research/trackpad-and-editor.md`](docs/research/trackpad-and-editor.md)):

- **Capture:** an app-level `NSEvent` local monitor reads `NSTouch.normalizedPosition`
  (0–1, absolute) while locked; single-finger only, so 2-finger gestures pass through.
- **Cursor:** `CGAssociateMouseAndMouseCursorPosition(False)` **freezes** (not hides) the
  cursor while locked; restored on unlock/close/app-deactivate. No private frameworks.
- **Bridge:** touches → `runJavaScript("window.__trackpad.onTouch(...)")`; JS→native lock
  signals via `document.title` (`TP:lock`/`TP:unlock`) → `titleChanged`.
- **Draw:** JS synthesizes pointer events into Excalidraw's freedraw tool at the mapped point.
- **Editor:** Excalidraw (MIT) via CDN (esm.sh for JS, **unpkg for CSS** — esm.sh's CSS path
  404s). Its scene graph (`getSceneElements()` + bindings) maps to a typed node/edge graph
  for judging.
- **Latency:** touches emit immediately (an earlier coalescing buffer *added* lag and was
  removed); default smoothing 0. There is a hard cross-process floor (~1 frame); "instant"
  isn't reachable in a webview. A native `QGraphicsScene` surface is the only path lower.

## 7. What's left (honest)

**Feature gaps**
- It's a **menu-launched editor dialog**, not yet a **reviewer card type** (front = prompt,
  back = reference, flowing through Anki's review loop + FSRS scheduling).
- **AI judge is not built** — the two-stage extract-then-judge pipeline, gold-set eval, and
  "beat a graph-edit-distance baseline" gate (PRD §10) are designed but not implemented.
- Reveal/self-grade panel is a light HTML card — **not night-mode aware**.
- Trackpad is **macOS-only** (degrades to mouse/stylus without pyobjc).

**Speedrun deliverable gaps (vs the assignment rubric)**
- **Rust engine change: NOT done.** The PRD proposes a `rslib` "mastery query"; this is a
  required deliverable (20% + a hard 50% cap if absent). Start here for the grade.
- **Three scores (Memory/Performance/Readiness): conceptual only** — not yet computed/displayed
  with ranges + the refuse-to-score rule.
- **Ablation test not run.** Falsifiable hypothesis is written in the BrainLift/PRD.
- Mobile companion + sync: not started.

**Housekeeping**
- Merge `feat/draw-editor-v1` → `main`.
- Reconcile with `cursor/run-and-improve-ui-b566` (it has a real card type + sample decks;
  decide whether to adopt/merge that approach).

## 8. Gotchas

- **`out/pyenv` is regenerated on every `./ninja` build → reinstall pyobjc afterward** or the
  trackpad silently falls back to mouse-only (logs `pyobjc=False`).
- Build path must have **no spaces**.
- Excalidraw loads from a **CDN** → needs network on first use.
- The in-Anki dialog runs a tiny local HTTP server on **:8142** serving `qt/aqt/drawcard_web/`.
- `web/draw-editor/` (sandbox) and `qt/aqt/drawcard_web/` (in-Anki) are **two copies** of the
  editor page — keep them in sync or unify.
- Anki add-ons load from `~/Library/Application Support/Anki2/addons21/` (an earlier add-on
  version was removed in favor of direct source integration).
