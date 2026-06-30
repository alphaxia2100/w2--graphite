---
name: speedrun-project
description: "Andrew's \"Speedrun\" build — fork Anki, AWS SAA-C03 exam, diagram-flashcard study feature; deliverables incl. a BrainLift"
metadata: 
  node_type: memory
  type: project
  originSessionId: 05e70ab0-76cc-408e-a217-85db27556b01
---

Andrew Xia is building the **"Speedrun"** project (a Gauntlet-AI-style brief, owner "Patrick"): fork **Anki**, pick **one exam**, ship a **desktop app + phone companion sharing Anki's Rust engine**, make a real Rust engine change, and measure/display **three separate scores — Memory, Performance, Readiness** — each with an uncertainty *range*, under an "honesty rule" (never show a number without its evidence/missing-data/past-calibration/range/next-best-action; **refuse to score** when data is thin). Requires picking **one study feature grounded in learning science** + a falsifiable hypothesis tested via **ablation** (full app vs feature-off vs plain Anki at equal study time). AGPL-3.0, credit Anki. Deliverables: GitHub fork, 3–5 min demo, model descriptions, and a **BrainLift**.

- **Chosen exam:** AWS Certified Solutions Architect – Associate (**SAA-C03**) — 65 Q, 130 min, scaled 100–1000, pass 720, 100% text MCQ/MRQ; domains: Secure 30% / Resilient 26% / High-Performing 24% / Cost-Optimized 20%.
- **Chosen study feature:** hand-drawn AWS architecture diagram flashcards — learner draws an architecture from a blank prompt, uploads a photo, a multimodal AI judges it vs a reference diagram, and the **learner makes the final Again/Hard/Good/Easy self-grade** (Anki-style accountability). AI is an assist to honest self-grading, never grader of record.
- The BrainLift template + 3 worked examples (Scribble x2, Board) live in `source/*.webarchive`; the brief is `source/Speedrun_*.pdf`. BrainLift format = Owners / Purpose(+In/Out scope) / DOK4 named Spiky POVs / Experts / DOK3 Insights / DOK2 Knowledge Tree.
- Delivered `BrainLift.md` (2026-06-29): verdict **GO** as a Performance-measurement + calibration instrument, NOT as a "raise the SAA score faster than Anki" tool. See [[brainlift-saa-key-risks]].
