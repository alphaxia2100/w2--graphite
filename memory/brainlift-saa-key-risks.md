---
name: brainlift-saa-key-risks
description: "The honest verdict/bounds from the graph-construction flashcard BrainLift (revised 2026-07-01): what the evidence supports and where it stops"
metadata: 
  node_type: memory
  type: project
  originSessionId: 05e70ab0-76cc-408e-a217-85db27556b01
---

Findings from the research-backed BrainLift for the graph-construction flashcard ([[speedrun-project]]), **revised 2026-07-01**. Verdict moved from "measurement instrument only" to **GO as a genuine learning tool for graph-shaped topics, with the honesty layer as the guardrail — bolder but bounded.**

**The doc now has 3 (not 7) Spiky POVs, consolidated to remove overlap (Why / Effort / Honesty):**
- **SPOV 1 (WHY):** if a topic is really a graph, understanding it beats memorizing it — even for a 100% MCQ exam. Grounded: SAA-C03 is scenario/application-based (not rote); concept-map *construction* meta g=0.58 (constructing 0.72 > studying 0.43, n=11,814); retrieval transfers best to application/inference (Pan & Rickard). Key reframe: **"construct the graph from memory," not loose "drawing."**
- **SPOV 2 (EFFORT):** people are lazy, so friction is the whole game — keep the friction that teaches (draw from blank; desirable difficulties; generation d=0.40), kill the friction that doesn't (grading). The AI's only job is to collapse *grading* time (describe + check), never grade of record (models describe > judge hand-drawn topology: Henkel κ 0.20→0.47; SketchJudge best 78.4% vs human 83.3%). The equal-time bar lives here.
- **SPOV 3 (HONESTY):** people accept fuzzy answers even when it hurts them → force a crisp standard (reference + item checklist, revealed *after* the attempt) and refuse fuzzy numbers (refuse-to-score when data thin / AI can't see; FSRS already discounts same-day massing — verified in `reviews_for_fsrs`). Anchored self-grade fixes inflation (Dunlosky standards; León g=0.206; Kruger-Dunning 12th→62nd). A clean drawing *widens* the readiness band, never raises it (Soderstrom & Bjork; Lawson & Mayer drawing-quality R² 0.35 immediate → 0.02 delayed).

**Honest bounds (still load-bearing):** it's understanding-beats-memorizing, **NOT** drawing-beats-equal-time-MCQ-drilling (response congruency; the ~2–3× time cost must clear the equal-time bar or it's reported as a loss). Only for genuinely graph-shaped material and construct-from-memory (loose drawing during visual lessons collapses to copying — the Lawson & Mayer null). AI judging hand-drawn diagrams is still unproven for this exact task → assist only, gated on beating a graph-edit-distance baseline, UNSURE-by-default topology, multi-model panel (LLM-judge overconfidence — Tian et al. 2025).

**Verification:** every load-bearing citation was re-checked against primary sources this pass (see BrainLift **Appendix B** ledger); no carried-over figures were wrong. Fixed one attribution — the factual-vs-conceptual MCQ study is **Haycocks et al. (2024)**, and its durability result is *inconclusive* per the authors, so SPOV 1 leans on it lightly. **How to apply:** keep the falsifiable ablation two-sided and measure construction quality as a *separate* outcome from projected MC readiness.
