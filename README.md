# w2--graphite

Week-2 **Speedrun** project: a desktop + mobile study app built on Anki for **one** graduate-level exam — **AWS Certified Solutions Architect – Associate (SAA-C03)**.

The headline study feature is a **hand-drawn architecture-diagram flashcard**: the learner draws an AWS architecture from a blank prompt, uploads a photo, a multimodal AI describes and checks it against a reference shown *only after* the attempt, and the **learner makes the final self-grade**. The app measures and displays three *separate* things — **memory**, **performance**, and **readiness** — each with an honest uncertainty range, and refuses to show a number it can't back up.

![The draw-it-from-blank study loop](assets/learning-loop.svg)

## Contents

| Path | What |
|---|---|
| [`BrainLift.md`](BrainLift.md) | The research-backed BrainLift for the study feature: purpose, 7 spiky points of view, experts, insights, a sourced knowledge tree, and an honest viability verdict + falsifiable ablation hypothesis. |
| [`memory/`](memory/) | The project's context/memory system — the persistent notes that ground the work ([index](memory/MEMORY.md), [project](memory/speedrun-project.md), [key risks](memory/brainlift-saa-key-risks.md)). |
| [`assets/`](assets/) | Figures. |

## Status

- ✅ Research, BrainLift, and viability verdict — **done**.
- ⏳ Fork Anki into this repo; the real Rust engine change, the two-stage AI diagram judge, and the three-score honesty layer — **to be built here**.

## Verdict (from the BrainLift)

Build it — but as a tool for **measuring and calibrating skill honestly**, not as a tool that promises to raise the SAA-C03 score faster than plain Anki. The exam is 100% multiple-choice, so the open question is whether drawing transfers and whether it's worth the per-minute cost; that gets settled by the equal-time ablation, not by assertion.

## License

To be added when the Anki engine is forked in: **AGPL-3.0-or-later**, with credit to [Anki](https://github.com/ankitects/anki) (some Anki components are BSD-3-Clause).
