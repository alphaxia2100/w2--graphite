# Diagram-Flashcard Feature: Editor + Trackpad Lock-In Recommendation

**Context:** Anki fork. Desktop = PyQt6 + `QWebEngineView` rendering Svelte/HTML/JS; engine = Rust. Card type asks the learner to *draw* a node/edge diagram (AWS architecture, water cycle, etc.) from memory. License constraint: Anki is **AGPL-3.0**, so anything we bundle must be AGPL-compatible (MIT/Apache/MPL all fine; "source-available-but-needs-a-paid-key" is not).

---

## 1. In-app drawing editor

### Primary: **Excalidraw** (`@excalidraw/excalidraw`, MIT)

Use Excalidraw as the capture surface. It is the only mainstream option that ships **all four** of our hard requirements out of the box — boxes (rect/ellipse/diamond), connectors that **bind to shapes**, text labels, and high-quality freehand — *and* exposes a documented, inspectable scene graph.

- **License fit:** MIT, fully AGPL-compatible, self-hostable with **no mandatory cloud**. Set `window.EXCALIDRAW_ASSET_PATH` and serve fonts locally so nothing phones home ([install docs](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/installation)). ~126k stars, actively maintained (v0.18.1, 2026-04-21) ([repo](https://github.com/excalidraw/excalidraw)).
- **Inspectable node/edge graph for judging — yes, nearly for free.** The ref API gives `getSceneElements()` returning `ExcalidrawElement[]`, plus `updateScene()` and `onChange()` ([API props](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/props/excalidraw-api)). Each element carries `boundElements` / `startBinding` / `endBinding`, so **shapes → nodes, bound arrows → edges, text → labels** maps almost directly to a typed graph for self/AI judging. This binding model is the single biggest reason to pick it over a toolkit we'd have to grow into an editor.
- **The one real cost — React in a Svelte shell.** Excalidraw hard-requires React + ReactDOM and does not bundle them ([npm](https://www.npmjs.com/package/@excalidraw/excalidraw)). Mount it as a React island via `ReactDOM.createRoot` into a single DOM node, or isolate it in its own page/iframe. React and Svelte coexist fine on one page; Excalidraw is client-only (no SSR), which suits a `QWebEngineView` page. It's the heaviest bundle of the candidates, but acceptable in a desktop/Electron-like context.
- **Precedent in Anki:** web-canvas drawing layered over the reviewer is well-trodden (AnkiDraw, the Tldraw integration, `pigoz/anki-canvas`), injected via `gui_hooks.webview_will_set_content`. Goal A is low-risk.

### Lightweight fallback: **Svelte Flow** (`@xyflow/svelte`, MIT) + **perfect-freehand** (MIT)

If the React island proves painful, or we want a smaller surface that matches the Svelte shell natively:

- **Svelte Flow** is the only first-class **native-Svelte** diagram option (no React bridge), MIT, actively maintained (xyflow, 37.4k stars, releases to 2026-06) ([repo](https://github.com/xyflow/xyflow)). It is **graph-native** — `nodes[]`/`edges[]` *is* the data model — so judging-export is trivial: the graph already exists.
- **Trade-off:** it's structured editing (drag predefined nodes, connect handles) with **no freehand**, and a more constrained, less "sketchy" capture UX. Backfill freehand with **perfect-freehand** (`getStroke()`, zero runtime deps, MIT — [repo](https://github.com/steveruizok/perfect-freehand)), which is also the natural sink for Goal B's absolute-trackpad points once that bridge lands.

### Explicitly rejected

- **tldraw** — technically best-in-class but **license-disqualified**: default license is development-only, production requires a paid key (~$6k/yr/team reported), the free tier forces a "made with tldraw" watermark, and **downstream users of an OSS fork would each need their own license** — incompatible with a free, redistributable Anki fork ([license](https://tldraw.dev/community/license)).
- **Konva / Fabric** — canvas toolkits, not editors; no bound connectors or freehand smoothing. You'd hand-build the editor and the scene→graph layer. More work than Excalidraw/Flow.
- **mxGraph / drawio / maxGraph** — mxGraph is archived/EOL; drawio shipped minified source in Dec 2024 and isn't cleanly embeddable; maxGraph is pre-1.0 with an unstable API. Avoid for greenfield.
- **JointJS** — MPL-2.0 core is license-OK and has a clean graph model, but the polished editor UX is gated behind paid JointJS+, and there's no freehand in core. Flow gives a comparable graph model under cleaner MIT with a Svelte build.

---

## 2. Trackpad-as-absolute-tablet "lock-in" feature

### The confirmed constraint

`QWebEngineView`/Chromium **does not** expose raw absolute trackpad touches to JS. On macOS the trackpad surfaces only as relative pointer/mouse + high-level pinch/scroll gestures; Chromium consumes the rest, and Qt's own `QTouchEvent` delivery on macOS is unreliable/"broken" with a long bug history ([QTBUG-28126](https://bugreports.qt.io/browse/QTBUG-28126), [Qt forum](https://forum.qt.io/topic/7329/how-to-receive-touch-events-on-macos-x)). **Absolute-trackpad drawing therefore requires native macOS code bridged into the web canvas** — the project's stated tension is real and confirmed from all angles.

### The lowest-risk architecture (recommended): public **AppKit NSTouch**, no private framework

A small native `NSView` subclass, attached to Anki's reviewer webview via PyObjC, opts into indirect (trackpad) touches and streams absolute finger positions into the canvas through Anki's existing JS↔Python bridge.

- **API:** `NSView.allowedTouchTypes = [.indirect]` (legacy: `acceptsTouchEvents = YES`), implement `touchesBegan/Moved/Ended/Cancelled`. Each `NSTouch` exposes **`normalizedPosition`** — a `CGPoint` in `0.0…1.0` with **origin at the LOWER-LEFT** of the physical trackpad ([Apple docs](https://developer.apple.com/documentation/appkit/nstouch/normalizedposition), [Handling Trackpad Events](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/HandlingTouchEvents/HandlingTouchEvents.html)). This is a **true absolute position**, not a delta and not cursor-relative — exactly the "finger at top-left of trackpad = top-left of region" graphics-tablet mapping. Apple's own SwiftUI sample does this verbatim: `position(x: width*touch.x, y: height*(1 - touch.y))` ([writeup](https://levelup.gitconnected.com/swiftui-macos-map-finger-position-on-trackpad-to-view-6e5c5b872f43)).
- **Private framework needed? No.** `NSTouch`, the Core Graphics cursor calls, and `NSPressureConfiguration` are all **public, App-Store/notarization-safe** AppKit/Quartz APIs. This is Apple's explicitly sanctioned alternative to the private framework.
- **Critical gotchas (well-documented, cost us if missed):**
  - For indirect touches, `NSTouch.location(in:)` **throws** `NSInternalInconsistencyException`. You **must** use `normalizedPosition` (and `deviceSize` only if you want physical mm to correct aspect ratio).
  - Use `touch.identity` to follow **one** drawing finger across phases; treat a second finger (or a key) as the lock/unlock toggle. `wantsRestingTouches` controls whether a resting thumb counts.
  - `NSTouch` gives position but **not** pressure on classic Multi-Touch trackpads. Force Touch pressure is a separate public stream via `NSEvent.pressure` in `pressureChangeWithEvent:`; set `pressureConfiguration = .primaryGeneric` so a firm stroke doesn't fire the system deep-click ([NSPressureConfiguration](https://developer.apple.com/documentation/appkit/nspressureconfiguration)). Treat pressure as nice-to-have polish, not v1.
- **Bridge to the canvas:** Anki already provides this. JS `pycmd(str)` → Python `onBridgeCmd(str)`; Python pushes back via `webview.eval(...)` / `page().runJavaScript(...)` ([Anki webview](https://github.com/ankitects/anki/blob/main/qt/aqt/webview.py), [DeepWiki](https://deepwiki.com/ankitects/anki/2.8-webview-integration-and-media-server)). The native NSView maps `normalizedPosition` into the locked canvas rect and calls e.g. `window.ankiTrackpad.draw(x, y, phase)`. PyObjC is the natural glue since Anki is already PyQt6/Python — selectors map colon→underscore (`touchesBeganWithEvent_`); attach the view via `QWidget.winId()`, which returns an `NSView*` on macOS ([PyObjC](https://github.com/ronaldoussoren/pyobjc), [Qt](https://doc.qt.io/qt-5/qmacnativewidget.html)).

### The lock-in / outline / mapping / unlock UX (all public Core Graphics)

1. **Lock in** (user presses/taps to commit): present a borderless overlay NSView that owns the trackpad touches while locked; call `CGAssociateMouseAndMouseCursorPosition(false)` to decouple the cursor from trackpad motion (input still arrives, cursor stays put) and `CGDisplayHideCursor(kCGNullDirectDisplay)` to hide the pointer (hide/show calls must be **balanced**) ([Controlling the Mouse Cursor](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/QuartzDisplayServicesConceptual/Articles/MouseCursor.html), [CGAssociate…](https://developer.apple.com/documentation/coregraphics/cgassociatemouseandmousecursorposition(_:))).
2. **Outline:** draw a small trackpad-shaped rectangle on the canvas marking the locked region; render your own brush indicator from `normalizedPosition` (the OS cursor is hidden/frozen).
3. **Absolute mapping:** invert y (`1 - touch.y`) and linearly scale the touch's `normalizedPosition` into the locked-region rect. Follow a single finger via `touch.identity`.
4. **Unlock:** `CGAssociateMouseAndMouseCursorPosition(true)` + `CGDisplayShowCursor(...)`, tear down the overlay, return to normal cursor → user pans/zooms the canvas, then locks a new region (just recompute the mapping rect).

### v1 vs v2

- **v1 (ship-safe, no native code):** the Excalidraw editor with **relative pointer/mouse drawing + photo-upload fallback**, injected via `gui_hooks.webview_will_set_content`. Independently shippable, low-risk, precedented by AnkiDraw/Tldraw/anki-canvas. This delivers Goal A and the judging graph today.
- **v2 (full absolute-trackpad, opt-in mode):** the public-API NSTouch lock-in layer above, bridged via `pycmd`/`onBridgeCmd`. Public APIs only — **do not** touch the private `MultitouchSupport.framework` (it adds richer data like contact-ellipse/pressure but is undocumented, breaks under App Sandbox, triggers App-Store rejection ITMS-90338, and can break on OS point releases — [Apple recommends NSTouch](https://groups.google.com/g/kivy-users/c/JbI_hu9lWk0)). A single finger's absolute position is all this feature needs, so the private route adds risk without needed capability.

### Honest risk assessment

- **The one genuinely unproven integration point:** no one has published a confirmed example of an overlay/sibling `NSView` reliably winning indirect `NSTouch` events while `QWebEngineView`'s Chromium NSView is in the responder chain. All three relevant research angles flagged this independently. **De-risk it first with a throwaway PyObjC + PyQt6 spike** that just logs `normalizedPosition` from a child NSView over a `QWebEngineView`. The borderless-overlay-while-locked design is the most promising mitigation (it sidesteps Chromium's gesture handling entirely while active).
- **Fallback if the bridge fights Chromium gestures:** render the *draw step* in a native Qt surface (`QGraphicsScene`/QML Canvas) fed by the same NSTouch stream, then serialize the diagram (SVG/JSON nodes+edges) back into the card. This eliminates Chromium from the draw path but costs a second rendering tech + a serialization layer. Keep it in pocket; try the web bridge first.
- **Hardware caveat:** pressure (the v2 polish) only grades on Force Touch trackpads, and external Magic Trackpads report weaker/limited pressure. Position works on all Multi-Touch trackpads regardless.
- **Always keep the mouse-draw + photo-upload fallbacks live** so the feature degrades gracefully if a future macOS changes touch behavior.

---

## 3. Build order

1. **Editor v1 (Goal A).** Stand up Excalidraw as a React island inside the reviewer webview via `gui_hooks.webview_will_set_content`; self-host assets (`EXCALIDRAW_ASSET_PATH`). Mouse/stylus drawing + photo-upload fallback. **Ship this.**
2. **Judging graph extraction.** Wire `getSceneElements()` → typed node/edge graph (shapes→nodes, `boundElements`/bindings→edges, text→labels). Store it in the card and feed self/AI judging. Validates the whole judging story on real cards before any native work.
3. **NSTouch spike (de-risk).** Throwaway PyObjC + PyQt6 prototype: a child/overlay NSView over a `QWebEngineView` that logs `normalizedPosition`. Confirm it wins indirect touches over Chromium. **Go/no-go gate for v2.**
4. **Lock-in v2 (Goal B).** On spike success: borderless overlay NSView (`allowedTouchTypes=[.indirect]`), single-finger `identity` tracking, lower-left→top-left mapping into the locked rect, Core Graphics cursor decouple/hide on lock + restore on unlock, trackpad outline + custom brush indicator, points forwarded via `pycmd`/`onBridgeCmd` into the Excalidraw/Svelte canvas. Ship as **opt-in**.
5. **Polish (optional).** Force Touch pressure → stroke width via `NSEvent.pressure` + `pressureConfiguration = .primaryGeneric`; pipe pressure into perfect-freehand on the fallback path.

**If the spike fails at step 3:** fall back to a native `QGraphicsScene` draw surface fed by the same NSTouch stream, serialized back into the card — not the private framework.

---

**Evidence confidence:** Strong and cross-confirmed for the editor choice, the public-NSTouch absolute-position route, the private-framework risks, and the Anki bridge. **Thin in exactly one place** — the NSView-over-QWebEngineView responder-chain interaction has no published end-to-end example; treat step 3 as a real gate, not a formality.