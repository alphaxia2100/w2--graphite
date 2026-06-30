# Trackpad lock-in — de-risk spike

Throwaway prototype answering the one unproven question in the [PRD §7](../../PRD.md)
trackpad feature: **can an `NSView` over `QWebEngineView` (Chromium) actually
receive indirect (trackpad) touches, so we can read `NSTouch.normalizedPosition`
and feed absolute finger position into the canvas?**

This is milestone 3 in the PRD build order — a **go/no-go gate** for the v2
absolute-trackpad mode. Research: [`docs/research/trackpad-and-editor.md`](../../docs/research/trackpad-and-editor.md).

## What it does

Shows a PyQt6 window with a `QWebEngineView` canvas and tries **two** capture
mechanisms simultaneously, logging which fires:

- **A — `TouchCaptureView`**: a transparent `NSView` added over the webview, made
  first responder, implementing `touchesBegan/Moved/Ended`. The documented path.
- **B — local `NSEvent` monitor**: app-level interception of any event carrying
  touches, independent of the responder chain. The fallback path.

`normalizedPosition` is `0..1`, origin **lower-left**; the canvas inverts Y.

## Run

```bash
# from the repo root; pyobjc must be in the env (already added to out/pyenv)
out/pyenv/bin/python experiments/trackpad-spike/spike.py
```

Focus the window, then drag **one finger** on the trackpad. Blue dots = mechanism
A, orange = mechanism B. Events also print to stdout with a heartbeat.

## Interpreting the result (the gate)

- **Mechanism A fires** → ship v2 as designed (NSView + `makeFirstResponder`).
- **Only B fires** → use the app-level monitor instead (still public API); revise the PRD's "first responder" detail.
- **Neither fires** (heartbeat alive, zero events while touching) → the
  responder/monitor route is blocked by Chromium; fall back to a native
  `QGraphicsScene` draw surface fed by the same `NSTouch` stream (PRD §7 fallback).
  Do **not** reach for the private `MultitouchSupport.framework`.

## Result — PASS (2026-06-30)

**Mechanism A fired.** A first-responder `TouchCaptureView` over `QWebEngineView`
received indirect `NSTouch` events; `makeFirstResponder -> True` and first
responder stayed ours (`firstResponder_is_ours=True` on the heartbeat).
`normalizedPosition` (0–1, lower-left origin) streamed into the canvas and traced
the finger. Mechanism B (the app-level `NSEvent` monitor) also fired, giving a
backup path. Hundreds of events captured cleanly in a single drag.

**Decision:** ship v2 on the documented mechanism-A route (NSView +
`makeFirstResponder`). The `QGraphicsScene` fallback and the private
`MultitouchSupport.framework` are **not** needed.

## Status

Spike — not production code. Depends on `pyobjc-framework-Cocoa` + `-Quartz`.
