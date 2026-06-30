# PRD — The Draw-It-From-Blank Card

| | |
|---|---|
| **Owner** | Andrew Xia |
| **Status** | Draft v2 |
| **Date** | 2026-06-30 |
| **Project** | `w2--graphite` — a desktop + mobile study app forked from [Anki](https://github.com/ankitects/anki) |
| **Scope** | A **domain-agnostic** study card for any topic best understood as a graph |
| **Seed domains** | AWS SAA-C03 (the Speedrun exam) and the water cycle (test/dev topic) — see [`examples/reference-graphs/`](examples/reference-graphs/) |
| **Rationale / evidence** | [`BrainLift.md`](BrainLift.md) (learning science) · [`docs/research/trackpad-and-editor.md`](docs/research/trackpad-and-editor.md) (engineering) |

---

## 1. Summary

A new Anki card type for any subject where understanding is *really a graph* — an AWS architecture, the water cycle, a Krebs cycle, a network topology, a state machine. The prompt asks the learner to **build the diagram from memory in an in-app drawing editor** (boxes, lines/connectors, labels, freehand). They then check themselves against a canonical **reference graph** and **grade themselves** (Again/Hard/Good/Easy).

- **Non-AI version (default, and the ablation baseline):** draw it (or upload a photo), reveal the reference, **judge yourself**. No model in the loop.
- **AI version (opt-in):** a multimodal AI additionally *describes* the drawing and *checks* it against the reference as a per-item checklist with explicit "unsure" states — an assist to honest self-grading, **never the grader of record**.

The app measures three *separate* things — **Memory**, **Performance**, **Readiness** — each with an honest uncertainty range, and refuses to show a number it can't back up.

## 2. Problem & motivation

Recognition and cloze flashcards prove you can *recognize* an answer; they never prove you can *construct* the structure from nothing. For anything graph-shaped, a high retention score silently implies a capability it never tested ([BrainLift SPOV 1](BrainLift.md)). The water cycle makes the generality obvious: reservoirs are nodes, processes (evaporation → condensation → precipitation → runoff) are directed edges, and "the cycle closes" is exactly the relational understanding a recognition card can't measure. This feature measures that capability directly and reports readiness honestly.

## 3. Goals, non-goals, success metrics

**Goals**
- G1. A **domain-agnostic** free-recall *construction* card type in the forked engine — driven by a topic's reference graph, not hard-coded to any exam.
- G2. **Drawing happens in the app**: a built-in editor with boxes, connectors, labels, and freehand. Photo upload is a fallback.
- G3. **Trackpad-as-tablet "lock-in"** absolute drawing mode on macOS (opt-in).
- G4. **Honest self-grading**: the learner makes the final call, anchored to the reference (+ AI checklist in the AI version).
- G5. **Memory / Performance / Readiness** shown separately, each with a range, under the honesty rule.

**Non-goals**
- N1. Replacing FSRS / Anki's Rust scheduler (Memory rides on FSRS).
- N2. AI grading "of record" — the learner always decides.
- N3. Claiming the feature raises a multiple-choice *score* faster than plain Anki — measured, not promised ([BrainLift SPOV 6–7](BrainLift.md)).
- N4. Diagram *generation* from prompts, or production diagram/IaC audit.

**Success metric** — at **equal study time** vs feature-off and plain Anki, the full feature yields better self-grade-vs-expert agreement, better delayed transfer on novel construction items, and better-calibrated readiness. Falsifiable hypothesis in §14.

## 4. Users & use cases

Any learner of graph-structured material studying across a desk (drawing) and phone (review, readiness). The **water cycle** is the primary *testing* topic (fast to author, easy to grade, no domain expertise needed to evaluate the mechanics); **AWS SAA-C03** is the headline exam for the Speedrun deliverable.

## 5. Core loop & UI states

```
Prompt (blank)  →  Build diagram in-app (or upload)  →  [AI describes + checks]  →  Reveal reference
      ▲                                                                                    │
      │                                                                                    ▼
 FSRS schedules  ←────────────  Learner self-grades (final call)  ←──────────────  Compare to reference
```

| State | Behavior |
|---|---|
| **S1 Prompt** | Task statement only; optional pre-attempt **confidence** (1–5) for hypercorrection scheduling. Reference hidden. |
| **S2 Build** | The **in-app editor** (§6) — primary. Photo upload available as a fallback (e.g. drew on paper). |
| **S3 Check** | *Non-AI:* skip to reveal. *AI:* two-stage judge runs (§10), produces a per-item checklist with UNSURE. |
| **S4 Reveal** | Reference graph (+ checklist in AI mode). **Grade buttons stay locked until this state** ([SPOV 2 & 4](BrainLift.md)). |
| **S5 Self-grade** | Learner presses Again/Hard/Good/Easy; app logs (confidence, AI verdict if any, self-grade). |
| **S6 Schedule** | FSRS schedules; confident-wrong drawings re-tested sooner. |

## 6. The in-app drawing editor (Goal A)

Runs inside Anki's reviewer webview (`QWebEngineView`), injected via `gui_hooks.webview_will_set_content`.

- **Primary: [Excalidraw](https://github.com/excalidraw/excalidraw) (MIT).** The only mainstream option shipping all four needs out of the box — boxes (rect/ellipse/diamond), connectors that **bind to shapes**, text labels, and high-quality freehand — *and* a documented, inspectable scene graph. License is AGPL-compatible and fully self-hostable (`window.EXCALIDRAW_ASSET_PATH`, no cloud). **Cost:** it requires React, so it mounts as a React "island" in our Svelte shell (acceptable in a desktop webview).
- **Scene-graph → typed graph, nearly for free (FR-1a):** `getSceneElements()` returns elements whose `boundElements` / `startBinding` / `endBinding` map directly to **shapes → nodes, bound arrows → edges, text → labels** — i.e. the candidate graph we judge against the reference. This is the single biggest reason to choose Excalidraw over a toolkit we'd grow into an editor.
- **Lightweight fallback:** [Svelte Flow](https://github.com/xyflow/xyflow) (`@xyflow/svelte`, MIT, native-Svelte, graph-native) + [perfect-freehand](https://github.com/steveruizok/perfect-freehand) (MIT) for strokes — chosen if the React island proves painful. Trade-off: structured node/edge editing, no native freehand.
- **Rejected:** tldraw (production requires a paid license — disqualified for a free redistributable fork); Konva/Fabric (toolkits, not editors); mxGraph/drawio (EOL / not cleanly embeddable); JointJS (polished editor is paid). Detail + citations in [`docs/research/trackpad-and-editor.md`](docs/research/trackpad-and-editor.md).

## 7. Trackpad "lock-in" absolute drawing (Goal B, macOS)

**Desired UX:** press to **lock in** → the canvas shows a small outline shaped like the trackpad; a **single finger's absolute position** on the trackpad maps to an absolute point in that region (finger top-left = region top-left), so you draw as on a graphics tablet. **Unlock** → normal cursor; pan/zoom the canvas; lock a new region.

**Confirmed constraint:** `QWebEngineView`/Chromium does **not** expose raw absolute trackpad touches to JS (only relative pointer + pinch/scroll). Absolute-trackpad drawing therefore needs **native macOS code bridged into the canvas**.

**Architecture (public APIs only — no private framework):**
- A native `NSView` (via PyObjC) sets `allowedTouchTypes = [.indirect]` and reads **`NSTouch.normalizedPosition`** — a `0…1` `CGPoint`, origin lower-left — which is a *true absolute* trackpad position ([Apple docs](https://developer.apple.com/documentation/appkit/nstouch/normalizedposition)). Map it (invert Y) into the locked region rect; follow one finger via `touch.identity`.
- **Lock/unlock** uses public Core Graphics: `CGAssociateMouseAndMouseCursorPosition(false)` + `CGDisplayHideCursor` on lock (decouple + hide the pointer while input still flows), restored on unlock. Draw our own brush indicator + the trackpad outline.
- **Bridge:** native view → Anki's existing `pycmd` / `onBridgeCmd` → `webview.eval(...)` calls into the Excalidraw/Svelte canvas at the mapped point.
- **Gotchas (from research):** `NSTouch.location(in:)` *throws* for indirect touches → must use `normalizedPosition`; pressure isn't available on classic trackpads (Force Touch via `NSEvent.pressure` + `pressureConfiguration = .primaryGeneric` is v-next polish). **The private `MultitouchSupport.framework` is explicitly avoided** (undocumented, App-Store rejection, breaks under sandbox / OS updates) — a single finger's absolute position is all we need.

**v1 vs v2 (de-risked):**
- **v1 (ship-safe):** Excalidraw editor with **relative pointer/stylus drawing + photo-upload fallback**. Delivers Goals A + the judging graph today; no native code.
- **v2 (opt-in):** the NSTouch lock-in layer above. **Gated by a de-risk spike** — the one unproven point is whether a sibling/overlay `NSView` reliably wins indirect touches over Chromium's NSView; build a throwaway PyObjC+PyQt6 prototype that just logs `normalizedPosition` *before* committing. If it fails, fall back to a native `QGraphicsScene` surface fed by the same NSTouch stream (still public API) — **not** the private framework.

## 8. Modes: non-AI vs AI

| | Non-AI (default / ablation baseline / AI-off) | AI (opt-in) |
|---|---|---|
| Capture | In-app editor or photo upload | same |
| Check | Reveal reference; **learner judges self** against it | AI describes + checks vs reference → per-item checklist (✓/✗/UNSURE), *then* learner judges self |
| Grade | Learner: Again/Hard/Good/Easy | same (AI never grades of record) |
| Requirement | App must fully work here with AI off (Speedrun rule) | Every AI output traces to a named model, is eval'd, and beats a baseline (§10) |

## 9. Data model

**Reference graph** (authored per card) — typed nodes / typed directed edges / attributes / weighted rubric items (`node` · `process` · `constraint` · `direction`), each resolving to ✓/✗/UNSURE. Live examples: [`water-cycle.reference.json`](examples/reference-graphs/water-cycle.reference.json), [`aws-multi-az-web-tier.reference.json`](examples/reference-graphs/aws-multi-az-web-tier.reference.json).

**Candidate graph** — extracted from the editor scene (Excalidraw `getSceneElements()` bindings) or, in AI mode from an uploaded photo, from the AI's typed-graph extraction.

**Per-review record** — drawing (scene JSON or image), candidate graph, per-rubric verdicts (+ model confidence in AI mode), pre-attempt confidence, self-grade, timestamp, model/source id, baseline score.

## 10. AI judge specification (AI version only)

Two stages, never fused: **(1) extract** a typed candidate graph from the drawing (low-confidence topology/boundary items default to UNSURE); **(2) judge** candidate vs reference → per-rubric checklist, routing UNSURE items to the learner ([SPOV 3](BrainLift.md)). Gates: a **gold set** with human labels; the LLM judge must **beat a deterministic graph-edit-distance baseline** on held-out data or we ship the baseline + natural-language feedback only; report agreement as a range (multi-model panel); bias abstention strict (a false "you're ready" is the costliest error).

## 11. Three-score model & honesty rule

| Score | Definition | Source | Band |
|---|---|---|---|
| **Memory** | P(recall a fact now) | FSRS retrievability | narrow |
| **Performance** | P(construct a correct diagram for a *new* prompt) | judged construction on novel prompts | wider |
| **Readiness** | projected exam score (e.g. SAA-C03 100–1000, domain-weighted) | Performance × coverage, propagated with FSRS | widest; **may abstain** |

A clean drawing **raises Performance and widens Readiness's confidence**, never nudges the point estimate up on its own ([SPOV 5](BrainLift.md)). **Refuse-to-score** below a stated data threshold — but never withhold the *feedback*, only the *number* ([SPOV 7](BrainLift.md)).

## 12. Rust engine change

A backend **mastery query** in `rslib`: per **topic** (domain-agnostic), mastered-card count + average recall, fast on 50k cards, to power the dashboard. New protobuf message, Python-callable method, ≥3 Rust unit tests + 1 Python-side test, undo-safe, with a note on upstream files touched + future-merge difficulty. Ships to desktop and phone via the shared engine.

## 13. Performance & reliability targets

Grade acknowledged < 50 ms p95; next card < 100 ms p95; dashboard first load < 1 s / refresh < 500 ms; AI judging is async and never blocks review; zero collection corruption in crash tests; both apps run with AI off.

## 14. Milestones / build order

1. **Editor v1 (Goal A).** Excalidraw as a React island in the reviewer; self-hosted assets; mouse/stylus drawing + photo-upload fallback. **Ship.**
2. **Judging-graph extraction.** `getSceneElements()` → typed node/edge graph stored on the card; non-AI self-judge against the reference. Validates the judging story on real cards.
3. **NSTouch spike (de-risk gate).** Throwaway PyObjC+PyQt6 prototype logging `normalizedPosition` from an NSView over the webview. **Go/no-go for v2.**
4. **Lock-in v2 (Goal B).** Borderless overlay NSView, single-finger absolute mapping, cursor decouple/hide on lock, outline + brush indicator, `pycmd` bridge to the canvas. Ship **opt-in**.
5. **Rust mastery query + three-score dashboard.** (Can proceed in parallel with 1–2.)
6. **AI judge + eval gates** (§10), then the **ablation** (§14).
7. **Polish (optional):** Force Touch pressure → stroke width.

## 15. Validation — the ablation

> We expect the **full feature** (draw from blank → [AI checklist +] reference → learner self-grade) to produce **better-calibrated readiness and better scores on a delayed set of new, graph-construction/scenario problems** than the same feature with AI + reference removed, and than plain MCQ Anki, **at equal study time** — measured by (a) self-grade-vs-blinded-expert agreement, (b) delayed transfer on novel prompts, (c) calibration (Brier) of the readiness band. **It fails if**, at equal time: the full arm beats neither plain Anki on the MCQ outcome nor a separate construction outcome; OR the draw arm only ties plain Anki at materially more minutes; OR forcing the human self-grade adds nothing over AI auto-grading after the learner sees the same feedback; OR drawing quality predicts delayed performance no better than chance. *(Runnable on the water-cycle topic for fast iteration before AWS.)*

## 16. Risks & mitigations

| Risk | Mitigation |
|---|---|
| **Trackpad NSView-over-Chromium** touch capture is unproven (only thin evidence). | Spike it first (milestone 3) as a hard go/no-go; `QGraphicsScene` fallback; never the private framework. |
| Drawing trains a skill an **MCQ exam doesn't directly reward**. | Measure construction quality as a *separate* outcome; don't credit it toward the MCQ readiness number absent evidence. |
| **Per-minute cost** — drawing is ~2–3× slower. | Pre-register the per-minute bar; report a tie-at-higher-cost as a loss. |
| **AI misreads** hand-drawn topology. | Extract-then-judge, UNSURE-by-default, beat the GED baseline, strict abstention. |
| **Self-grade inflation**, worst for weakest learners. | Anchor to reference + checklist; unlock grade only after reveal; track per-learner calibration both directions. |
| Excalidraw **React-in-Svelte** integration cost. | Isolate as a React island / own page; fall back to Svelte Flow + perfect-freehand. |

## 17. Open questions

- Give-up thresholds (judged drawings per topic, coverage %).
- Reference-graph authoring at scale (hand-author vs import vs AI-assisted, human-reviewed).
- Tablet/stylus vs trackpad-lock-in vs photo as the dominant capture path in practice.
- Which multimodal model(s) clear the GED-baseline gate.

## 18. Out of scope, dependencies, license

**Out of scope:** non-spatial content (pricing tiers, IAM JSON) stays ordinary MCQ/cloze; diagram generation; production diagram audit. **Dependencies:** the Anki Rust engine + FSRS; Excalidraw (or Svelte Flow + perfect-freehand); on macOS, public AppKit/Quartz (`NSTouch`, Core Graphics); a named multimodal provider (AI mode only); the gold-set eval harness. **License:** AGPL-3.0-or-later, inherited from Anki, with credit to `ankitects/anki`; all bundled libraries are MIT (AGPL-compatible).
