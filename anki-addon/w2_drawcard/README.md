# w2_drawcard — draw-it-from-blank, inside Anki

Anki add-on that opens the Excalidraw diagram-drawing editor (with the macOS
trackpad lock-in) from **Tools → "Draw-it-from-blank (diagram card)"**, inside
the running Anki app. Reuses the web UI from [`web/draw-editor/`](../../web/draw-editor/);
the native trackpad capture runs in Anki's own Qt event loop.

## Install (dev)

Symlink (or copy) this folder into Anki's add-ons folder so Anki loads it:

```bash
ln -s "$PWD/anki-addon/w2_drawcard" \
  "$HOME/Library/Application Support/Anki2/addons21/w2_drawcard"
```

Then launch Anki (`./run` from the repo root) and use **Tools → Draw-it-from-blank**.

## Controls

- **Space** — lock in / draw with one finger (absolute trackpad mapping)
- **2-finger drag** move the region · **pinch** resize it (while unlocked)
- **Space / Esc** — unlock
- Settings (pan/pinch speed, smoothing, stroke width, invert) live in Excalidraw's **☰** menu.

## Requirements

- macOS. The trackpad feature uses public AppKit `NSTouch` + Core Graphics via
  **pyobjc** (`pyobjc-framework-Cocoa`, `pyobjc-framework-Quartz`). If pyobjc is
  missing the editor still opens (mouse/stylus drawing); the trackpad lock-in is
  disabled and logged as `pyobjc=False`.
- Excalidraw + React load from a CDN, so the editor needs network on first use.

## Status

Prototype integration. Next: make it a real card type in the reviewer (currently
a standalone editor window launched from the menu).
