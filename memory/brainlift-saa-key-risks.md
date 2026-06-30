---
name: brainlift-saa-key-risks
description: "The honest risks/verdict from the AWS SAA diagram-flashcard BrainLift — what the evidence does and doesn't support"
metadata: 
  node_type: memory
  type: project
  originSessionId: 05e70ab0-76cc-408e-a217-85db27556b01
---

Findings from the research-backed BrainLift for the diagram-flashcard feature ([[speedrun-project]]). Verdict = **GO, but reframed**: build it as a **PERFORMANCE-measurement + calibration instrument**, not as a "learn AWS faster than Anki" tool.

**Biggest threat:** the feature trains a capability (constructing architectures from blank) that the **exam does not directly reward** (SAA-C03 is 100% text MCQ). Under an equal-*time* ablation, the draw arm could tie/lose to plain MCQ Anki on projected score while costing ~2–3× the minutes/card → a per-minute loss on the metric users care about.

**Strongly supported:** the Memory/Performance/Readiness separation + the refuse-to-score / FSRS×judge uncertainty propagation; reveal-the-reference-*after* the attempt (generation effect; handed-diagram null/harm); **anchored** self-grading (the reference diagram + AI checklist = the standard that fixes self-grade inflation).

**Only moderately supported / hedge loudly:** transfer of drawing to a text-MCQ score (response-congruency mismatch; transfer is drawing's weakest outcome); equal-time viability; AI reliability judging *hand-drawn* AWS diagrams (no peer-reviewed benchmark; all evidence adjacent). Key design: **AI never both reads & grades in one prompt** — extract a typed graph, then judge graph-vs-graph; topology/boundary items default to UNSURE and route to the learner; gate the LLM on beating a deterministic graph-edit-distance baseline.

**Honesty nuance:** the human-final-grade is justified by *accountability + anchored calibration + an AI-reliability hedge*, NOT by "the rating act teaches" (JOL-reactivity is null on educational materials — Zhao et al. 2023). **How to apply:** when extending this, keep the falsifiable ablation hypothesis two-sided and measure construction quality as a *separate* outcome from projected MC readiness.
