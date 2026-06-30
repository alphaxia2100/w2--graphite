# BrainLift — The Draw-It-From-Blank Card: Hand-Drawn AWS Architecture Diagrams as a Free-Recall Construction Flashcard

## Owners

- **Andrew Xia**

---

## Purpose

**Purpose (north-star mission):**
Build the flashcard feature that refuses to let a comfortable retention number masquerade as exam readiness. For the AWS Certified Solutions Architect – Associate (SAA-C03) exam, the card prompts the learner to **hand-draw an architecture from a blank page** (e.g., "design a multi-AZ resilient web tier with a private DB and S3 static assets"), uploads a photo, lets a multimodal AI **judge the drawing against a canonical reference as structured evidence**, then hands the **final Again/Hard/Good/Easy grade to the learner**. The feature exists to measure and display three *separate* things — MEMORY (can you recall a taught fact now?), PERFORMANCE (can you construct a correct architecture for a new prompt?), and READINESS (projected real-exam score) — each with an honest uncertainty range and a single best next thing to study.

**In Scope:**
- A free-recall *construction* card type (draw-from-blank), distinct from recognition/cloze/image-occlusion cards.
- A two-stage AI judge: structured graph extraction from the drawing, then comparison to a reference graph, surfaced as a per-rubric-item checklist with explicit UNSURE states.
- Learner-as-grader-of-record: AI feedback + reference are shown *before* the grade buttons unlock; the learner makes the final call.
- Honest measurement: separate MEMORY (FSRS retrievability), PERFORMANCE (judged construction on novel prompts), and READINESS (domain-weighted projection) with ranges, calibration history, and a "refuse to score" rule when data is thin.
- The mandated ablation: full app vs. feature-off vs. plain Anki at **equal study time**.

**Out of Scope:**
- Replacing FSRS or Anki's Rust scheduling core (we reuse it; MEMORY rides on it).
- AI as grader of record. The AI is an assist to honest self-grading, never the verdict.
- Claiming the feature is *superior MCQ practice* for raising the SAA-C03 scaled score (the exam is 100% text MCQ; we do not promise this and the evidence does not support it).
- Non-spatial content (S3 pricing tiers, IAM policy syntax) — those stay ordinary MCQ/cloze cards. Drawing is reserved for topology-heavy task statements.
- Generating diagrams from prompts, or auditing production diagrams/IaC (that is the inverse job done by existing tools).

---

## DOK 4 — Spiky Points of View

### SPOV 1 — A high retention score and the ability to build an architecture from a blank page are different skills, and the app must never let the first stand in for the second.

Elaboration: The most over-trusted number in flashcard study is a high recall rate on a recognition deck. For SAA-C03, which is itself a multiple-choice exam, that number is genuine signal — but it is signal about one skill only. Recognizing the right answer among four options and drawing a multi-AZ topology on an empty page draw on different abilities, and the memory literature has kept them apart for decades: the study that feels most productive — re-reading, recognizing — reliably produces the most confidence and the least durable learning (Roediger & Karpicke, 2006). A recognition deck measures recall well and then quietly implies a design ability it never tested. The draw-from-blank card exists to measure that second ability on its own, so the app can show the distance between "I remember this service" and "I can compose these services into a working architecture" instead of blending them into one comfortable score.

### SPOV 2 — The reference diagram is the most valuable thing on the card — and showing it before the attempt would waste it entirely.

Elaboration: The obvious, friendly design is to put the canonical architecture on screen as a guide. That one choice would gut the feature. The value of drawing comes from generating the structure from memory; the instant the answer is visible, drawing becomes tracing, and a recall task quietly degrades into recognition. The advantage of self-generated over provided answers is one of the steadiest findings in the field (the generation effect; Bertsch et al., 2007), and in studies of diagrams specifically, learners handed a finished diagram have not done better than those who drew their own. So the reference is not the enemy — it is the answer key the learner grades themselves against, and it earns its keep only after the page has been filled. Reveal-after is not a setting to tune later; it is the part that makes the card teach.

### SPOV 3 — The AI should describe the drawing, not grade it — and on the parts that matter most for AWS, its honest answer is "I'm not sure."

Elaboration: Today's multimodal models are far better at judging a written description of a drawing than at reading the drawing itself: in the closest published study, a model grading hand-drawn work directly agreed with humans only weakly, but agreed at near-human levels when it was handed a text description of the same work (Henkel et al., 2025). The failure is perception, not judgment — and the parts of an AWS diagram that decide correctness are exactly the perceptual ones: is the database in a private subnet, is the load balancer spread across two availability zones, does traffic really reach S3 the way it is drawn. So the AI should first turn the drawing into an explicit, inspectable list of components and connections, then compare that to the reference — and where it cannot read the topology with confidence, it should say so and hand the question to the learner instead of guessing. A model that both reads and grades in one step hides its weakest link inside its most confident-sounding output.

### SPOV 4 — The learner makes the final call — and that is only safe because the reference turns a gut feeling into a checklist. *(the hard tension)*

Elaboration: The project demands that the learner press the final Again/Hard/Good/Easy button, which is also the right hedge against an AI judge that cannot be fully trusted. But self-grading is exactly where things go wrong: the people who know the least overestimate the most, because the gap that causes the error also hides it (the Dunning–Kruger problem), and "tap Good without reading" is a real failure mode of every self-graded deck. The escape is not to take the decision away from the learner — it is to change what they are deciding against. Self-assessment becomes far more accurate when a learner is given an explicit standard to score against rather than a vague sense of "did I know it" (Dunlosky et al., 2011). The reference diagram plus the AI's component-by-component readout is that standard. So the grade buttons stay with the learner, but they unlock only after the checklist and reference are on screen — accountability kept, honesty supplied.

### SPOV 5 — A clean, correct drawing should make the readiness estimate *less* confident, not more.

Elaboration: The intuitive product behavior — good drawing, higher score, tighter range — is backwards for an honest readiness number. How well someone performs during practice is a notoriously unreliable guide to how much they have actually learned; fluent in-the-moment performance and durable, transferable knowledge routinely come apart (Soderstrom & Bjork, 2015). In a controlled drawing study, the quality of a learner's diagram predicted their score on a test taken immediately but predicted essentially nothing on a test a week later (Lawson & Mayer, 2024). A single good drawing is therefore a fresh, fast-decaying data point about today's performance, not evidence about exam day. The app should treat it that way: a strong drawing raises the performance indicator and triggers a follow-up check on a new prompt, but it does not let the readiness number drift upward on its own.

### SPOV 6 — The real test is not "does drawing help?" but "does it help more than the same minutes on plain Anki?" — and we should commit to that harder bar before seeing the results.

Elaboration: Most evidence that drawing aids learning compares it to other activities given the same number of items, not the same number of minutes — and drawing is slow. In one time-controlled study, drawing took well over twice as long as summarizing and produced no benefit at all, while summarizing won (Lawson & Mayer, 2024). The project's required experiment is an equal-time comparison against plain Anki, which is the honest and unforgiving frame: a draw card that costs two to three times the minutes of a recognition card has to earn that cost back. The right move is to write that per-minute bar down in advance and measure the real time cost rather than assume it. If the drawing mode merely ties plain Anki while burning far more study time, that is a loss — and the app should be built to report it as one, not bury it.

### SPOV 7 — The whole feature is built around the word "no": no readiness score from cramming, and none when the AI cannot actually see the diagram.

Elaboration: Every effect the readiness projection leans on — retrieval, spacing, transfer — is a property of delayed, spaced, successful practice, not of a single cramming session; testing only beats re-study after a delay, and the right spacing depends on how far away the test is (Roediger & Karpicke, 2006). A score computed from same-day massed reviews is measuring the wrong thing. Anki's memory model is well-calibrated for recall and already ignores same-day reviews, but the diagram-judge term sitting on top of it is small-sample and shaky, so the combined "how sure are we" has to be dominated by the weaker term. The honest system therefore refuses: it withholds a readiness number when the data is thin or the AI's read of the drawing is low-confidence, and it shows the evidence and the single best next thing to study instead. Refusing to answer when it does not know is the feature, not a flaw in it — and it should keep giving feedback even when it withholds the score.

---

## Experts

**Robert A. & Elizabeth L. Bjork**
- *Who:* Distinguished Research Professors of Psychology, UCLA.
- *Focus:* "Desirable difficulties," and the distinction between learning and performance.
- *Why Follow:* Their work is the backbone of the three-score idea — that the study which feels best in the moment is often the worst for lasting learning, which is why memory, performance, and readiness have to be measured separately.
- *Where:* [UCLA Bjork Learning & Forgetting Lab](https://bjorklab.psych.ucla.edu/)

**Jeffrey D. Karpicke**
- *Who:* Professor of Psychological Sciences, Purdue University.
- *Focus:* Retrieval practice — whether recalling beats re-studying, and whether it transfers.
- *Why Follow:* The draw-from-blank card is a retrieval task in the strong sense he studies; his work is the basis for preferring recall over recognition.
- *Where:* [Purdue Cognition & Learning Lab](https://learninglab.psych.purdue.edu/)

**John Dunlosky & Katherine Rawson**
- *Who:* Professors of Psychological Sciences, Kent State University.
- *Focus:* How accurately students judge their own learning, and how to fix it.
- *Why Follow:* Their finding that an explicit standard sharply improves self-grading is the direct evidence behind letting the learner make the final call only after seeing the reference.
- *Where:* [Idea-unit standards study (2011)](https://journals.sagepub.com/doi/10.1080/17470218.2010.502239)

**Detlev Leutner**
- *Who:* Professor of Instructional Psychology, University of Duisburg-Essen.
- *Focus:* When drawing-to-learn helps, and the role of comparing your drawing to a model.
- *Why Follow:* His meta-analysis shows the comparison-to-reference step is what makes drawing pay off — the design heart of this card.
- *Where:* [Educational Psychology Review (2025)](https://link.springer.com/article/10.1007/s10648-025-10067-7)

**Owen Henkel**
- *Who:* Researcher on AI for education and assessment.
- *Focus:* Multimodal models grading handwritten and hand-drawn student work.
- *Why Follow:* His result that models grade a description of a drawing far better than the drawing itself is the most useful single guide to how the AI judge should be built.
- *Where:* ["Seeing the Big Picture" (2025)](https://arxiv.org/abs/2510.05538)

**Jarrett Ye & the Open Spaced Repetition team**
- *Who:* Creator and maintainers of FSRS, the scheduler Anki uses.
- *Focus:* Memory modeling and large-scale scheduler benchmarking.
- *Why Follow:* FSRS is the calibrated memory layer this feature builds on, and the place to validate any diagram-card scheduling change.
- *Where:* [open-spaced-repetition (GitHub)](https://github.com/open-spaced-repetition)

---

## DOK 3 — Insights

**On the three scores:**
1. The three layers line up with how settled the science is, which is what makes them honest: memory rests on the strongest evidence in the field, performance on a weaker and more conditional transfer literature, and readiness on the least of all. The app should literally show a wider band on performance than on memory.
2. Anki already hands us a calibrated memory number for free; the honest move is to multiply it by the chance the learner can actually apply the fact, and let that second, shakier term dominate how confident the readiness score looks.

**On the card itself:**
3. The feature is best understood as a fix for the one thing recognition cards cannot do: prove you can produce an answer, not just recognize one. Draw-from-blank is the hardest, least-cued form of recall, which is the whole point.
4. The sequencing is the asset, not the drawing itself: generate first, reveal the reference only afterward, and make the learner compare the two. Get the order wrong and the benefit disappears.
5. A drawing cannot be faked by familiarity the way a recognition card can — either the private subnet and the second availability zone are on the page or they are not — so the card doubles as a direct measure of the gap between how ready a learner feels and what they can actually produce.

**On the AI judge:**
6. The part of an AWS diagram that is hardest for a model to read — how things connect — is the same part the exam cares about most, so the judge is weakest exactly where it matters. That is the case for making it describe rather than score, and abstain when unsure.
7. Because the learner makes the final call, the AI does not need to be a reliable grader — it needs to be a reliable describer, which plays to what these models are actually good at.
8. There is a simple ladder the AI must climb to justify itself: it should have to beat a dumb, deterministic diagram-matcher on held-out, human-labeled examples. If it cannot, ship the matcher and use the model only for written feedback.

**On honesty:**
9. The design lands on the best-known fix for inflated self-grading almost by accident: the reference diagram is the standard, and self-grading against a standard is far more accurate than self-grading against a feeling. The button stays with the learner; the standard is what makes the click trustworthy.
10. Self-grading goes wrong in both directions — improving learners under-rate themselves, too — so the app has to track each learner's own calibration over time and widen or withhold the readiness band when their self-grades and the evidence drift apart.

---

## DOK 2 — Knowledge Tree

### Category: Retrieval Practice & Spacing
**Source — Roediger & Karpicke (2006), *Test-Enhanced Learning*.**
- *DOK-1 Facts:* At 5 min, restudy led (81% vs 75%, d=0.52); at 1 week the tested group led (56% vs 42%, d=0.83). Exp 2: STTT recalled 61% vs SSSS 40% at 1 week (d=1.26). The worst-recall group (SSSS, 40%) rated its own memory *highest* (4.8/7).
- *DOK-2 Summary:* Retrieval beats restudy at delay even though restudy feels better and raises confidence — the crossover and confidence inversion that motivate both the construction card and the honesty rule.
- *Link:* https://journals.sagepub.com/doi/abs/10.1111/j.1467-9280.2006.01693.x

**Source — Pan & Rickard (2018), *Transfer of Test-Enhanced Learning*.**
- *DOK-1 Facts:* 122 experiments, N=10,382. Overall transfer d=0.40; without response congruency d=0.28; with congruency d=0.58; transfer "disappears completely" at very low initial accuracy.
- *DOK-2 Summary:* Transfer is real but bounded by response congruency and initial accuracy — the precise reason to (a) hedge the PERFORMANCE band and (b) not promise drawing raises the MCQ score.
- *Link:* https://pdf.retrievalpractice.org/transfer/Pan_Rickard_2018.pdf

**Source — Cepeda et al. (2008), *Spacing Effects in Learning*.**
- *DOK-1 Facts:* N>1,350; optimal inter-study gap is ~20–40% of a 1-week test delay, falling to ~5–10% of a 1-year delay.
- *DOK-2 Summary:* Optimal spacing is an explicit function of retention interval — the relationship FSRS operationalizes, and the basis for refusing readiness from massed same-day data.
- *Link:* https://laplab.ucsd.edu/articles/Cepeda%20et%20al%202008_psychsci.pdf

### Category: Drawing & Generative Learning
**Source — Bertsch et al. (2007), *The Generation Effect: A Meta-Analytic Review*.**
- *DOK-1 Facts:* Overall d=0.40 across 86 studies, 445 effect sizes; weakest for free recall (d=0.32 vs 0.55 cued).
- *DOK-2 Summary:* Self-generated information is remembered better than provided information — the core mechanism behind reveal-after, with the honest caveat that the effect is smallest in the free-recall/novice regime this feature targets.
- *Link:* https://link.springer.com/article/10.3758/BF03193441

**Source — Leutner & Biele (2025), *Without Integration, Everything Is Nothing*.**
- *DOK-1 Facts:* 14 studies, 16 comparisons, N=1,213, all comparing *supported* vs *unsupported* drawing. Integration support g=+0.35; non-integration support g=−0.15; other moderators non-significant.
- *DOK-2 Summary:* Conditional on drawing, the compare-to-reference integration step is the decisive moderator — justifying the draw+compare-vs-draw-only ablation arm, while reminding us the baseline is unsupported drawing (so it can't speak to drawing-vs-no-drawing).
- *Link:* https://link.springer.com/article/10.1007/s10648-025-10067-7

**Source — Wammes, Meade & Fernandes (2016), *The drawing effect*.**
- *DOK-1 Facts:* Time-equated drawing (fixed ~40s windows) reliably beat writing/encoding controls on later free recall of single concrete words.
- *DOK-2 Summary:* The one clean *time-equated* drawing win in the cited literature — but for single words, not multi-element architecture diagrams, so it supports "drawing can win per-minute in principle" without generalizing to our high-element-interactivity task.
- *Link:* https://journals.sagepub.com/doi/10.1177/1747021815621542

**Source — Lawson & Mayer (2024), *When Summarizing Is Effective but Drawing Is Not*.**
- *DOK-1 Facts:* Drawing took ~2.4× the time of summarizing (681s vs 281s) with no benefit over control; summarizing won (d=0.48/0.54). Drawing quality predicted immediate posttest (R²=0.35) but not delayed (R²=0.02, p=.509).
- *DOK-2 Summary:* The per-minute cost and fast decay of diagram-quality predictiveness — the empirical basis for the harsher equal-time bar and the widen-the-band readiness rule.
- *Link:* https://pmc.ncbi.nlm.nih.gov/articles/PMC11402827/

### Category: Metacognition & Self-Grading
**Source — Kruger & Dunning (1999), *Unskilled and Unaware of It*.**
- *DOK-1 Facts:* Bottom-quartile performers (~12th percentile actual) estimated themselves ~62nd percentile; the same incompetence that produces errors blocks detecting them.
- *DOK-2 Summary:* Self-grading is least reliable for the weakest learners — the core risk in learner-as-final-judge. (Caveat: the canonical *curve* is largely a statistical artefact — [Gignac & Zajenkowski, 2020](https://gwern.net/doc/iq/2020-gignac.pdf) — so we don't lean on the chart.)
- *Link:* https://sites.lsa.umich.edu/sasi/wp-content/uploads/sites/275/2015/11/krugerdunning99.pdf

**Source — Dunlosky, Hartwig, Rawson & Lipko (2011), *Idea-Unit Standards*.**
- *DOK-1 Facts:* Without standards, learners over-credit free-recall answers; supplying idea-unit standards markedly improves self-evaluation accuracy, robust to strict/lenient scoring.
- *DOK-2 Summary:* Anchoring self-grading to an explicit standard is the strongest direct fix for inflation — the reference diagram + AI checklist is exactly this standard, which is why grade buttons unlock only after it's shown.
- *Link:* https://journals.sagepub.com/doi/10.1080/17470218.2010.502239

**Source — León, Panadero & García-Martínez (2023), *Self-assessment meta-analysis*, Educational Psychology Review.**
- *DOK-1 Facts:* ~160 studies; self-vs-expert agreement z=0.472 (r≈0.44); *persistent overestimation* g=0.206.
- *DOK-2 Summary:* The most relevant SELF-assessment (not peer-assessment) anchor: self-grading is moderately accurate at best and biased high — the core reason to supply a standard and track per-learner divergence, and the correct citation to use in place of the peer-vs-teacher r≈0.69.
- *Link:* https://link.springer.com/article/10.1007/s10648-023-09819-0

**Source — Zhao et al. (2023), *JOL reactivity on educational materials*, Journal of Intelligence.**
- *DOK-1 Facts:* Three experiments (one preregistered) found *null* judgment-of-learning reactivity on educational materials (Bayesian support for no effect); the earlier d=0.44 reactivity effect did not replicate.
- *DOK-2 Summary:* The act of rating one's own recall is *not* a reliable second learning episode — the strongest refutation of any "the grading click teaches" rationale, so human-final-grade is justified by accountability, anchoring-calibration, and the AI-reliability hedge, not by the rating act itself.
- *Link:* https://www.mdpi.com/2079-3200/11/10/190

**Source — Butterfield & Metcalfe (2001 / 2011), *Hypercorrection*.**
- *DOK-1 Facts:* High-confidence errors are corrected *more* by feedback than low-confidence errors; the effect persists ~1 week but high-confidence errors can return without an intervening test.
- *DOK-2 Summary:* Capturing pre-reveal confidence turns confident wrong drawings into the highest-value learning events — provided the app reschedules a re-test, not just shows feedback.
- *Link:* https://pubmed.ncbi.nlm.nih.gov/21989771/

### Category: AI Visual Judging
**Source — Henkel et al. (2025), *Seeing the Big Picture*.**
- *DOK-1 Facts:* Direct grading of hand-drawn illustrations κ≈0.20; given a *human text description*, κ≈0.47 (human-level); arithmetic grading κ≈0.90. (κ figures independently checked against the paper.)
- *DOK-2 Summary:* The bottleneck is visual perception, not judgment — pointing to a two-stage extract-then-judge pipeline. (Honest caveat: gains used *human* descriptions; an auto-extractor inherits the perception problem.)
- *Link:* https://arxiv.org/abs/2510.05538

**Source — Kortemeyer et al. (2024), *Grading handwritten physics-exam work with multimodal LLMs* (Phys. Rev. PER).**
- *DOK-1 Facts:* Multimodal LLMs "struggled to distinguish essential from irrelevant details" on hand-drawn/handwritten exam work; perception, not judgment, was the limiting factor.
- *DOK-2 Summary:* The closest peer-reviewed anchor for AI-judge *fragility* on hand-drawn inputs — the empirical basis for UNSURE-by-default topology items and routing low-confidence extractions to the learner.
- *Link:* https://arxiv.org/abs/2406.17859

**Source — Stogiannidis et al. (2025), *Mind the Gap: Benchmarking Spatial Reasoning in VLMs*, arXiv 2503.19707.**
- *DOK-1 Facts:* A dedicated benchmark documents systematic, sometimes large, spatial-reasoning shortfalls in current VLMs. (Note: this paper measures spatial reasoning broadly; it does *not* itself establish a clean object-vs-relation dissociation — that nuance is inferred from FlowVQA's cross-condition variance.)
- *DOK-2 Summary:* Independent evidence that VLMs are unreliable on exactly the spatial/relational structure AWS topology depends on — so calibrate per task and keep topology items UNSURE by default.
- *Link:* https://arxiv.org/abs/2503.19707

**Source — Keith et al. (2025), *VLM-as-a-Judge approaches for visual-narrative coherence*, Electronics 14(21):4199.**
- *DOK-1 Facts:* Direct-vision VLM judging reached ICC=0.718 with human raters and in places *beat* caption/extraction pipelines.
- *DOK-2 Summary:* Extract-first is *not* universally better than direct vision — so the two-stage architecture is a defensible default to A/B test, not a proven optimum.
- *Link:* https://www.mdpi.com/2079-9292/14/21/4199

**Source — SketchJudge (2026); SketchMind (2025); FlowVQA (2024).**
- *DOK-1 Facts:* SketchJudge: GPT-5 78.4% / Gemini-2.5-Flash 77.7% vs human 83.3%; worst on relational/topological errors; reference-removal bias is *mixed/model-dependent*. SketchMind: reported same-model lift ~55.6%→77.1% via Sketch Reasoning Graph + GED. FlowVQA: GPT-4V ~90.7% fact-retrieval vs ~58.25% topological, ~−14 pts on rotation. (SketchJudge and SketchMind figures checked against their papers; the two FlowVQA percentages are from *different prompting conditions*, so treat them as illustrative.)
- *DOK-2 Summary:* VLMs read labels better than connectivity, and structured graph rubrics recover *some* of the gap; but the split is messier than the clean figures imply (much of FlowVQA's gap is cross-condition) and GED itself is normalization-sensitive and stage-1-bottlenecked. The judge still trails humans, so it must be an assist with UNSURE-by-default topology items and a multi-model panel for the range.
- *Link:* https://arxiv.org/abs/2601.06944

**Source — Tian et al. (2025), *Overconfidence in LLM-as-a-Judge*; Zheng et al. (2023), *MT-Bench*; Krumdick et al. (2025), *No Free Labels*.**
- *DOK-1 Facts:* Judge confidence "significantly overstates actual correctness" across 14 models; verbosity bias preferred longer no-new-info answers >90% of the time *for weaker judges* (GPT-4 ~9%); reference-free judging inflates false-accepts; majority-voting over one model *compounds* overconfidence.
- *DOK-2 Summary:* The dangerous failure is *systematic over-grading*, not symmetric noise — so condition on the reference, bias abstention strict, and use a multi-model panel (not single-model re-runs) for the range.
- *Link:* https://arxiv.org/abs/2508.06225

### Category: AWS SAA Exam Structure
**Source — AWS SAA-C03 Exam Guide (official).**
- *DOK-1 Facts:* Four scored domains — Secure 30%, Resilient 26%, High-Performing 24%, Cost-Optimized 20%. 65 questions (50 scored), 130 min, scaled 100–1,000, pass=720, compensatory scoring. 100% multiple-choice/multiple-response text scenarios; *no* drawing. Validated against the Well-Architected Framework.
- *DOK-2 Summary:* The exam is pure selection (format mismatch with drawing), Security+Resilient = 56% of weight and are the most diagram-amenable domains, and domain weights drive the READINESS reweighting — so refuse a readiness number until each domain has minimum judged data.
- *Link:* https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html

**Source — AWS Reference Architecture Diagrams & Architecture Icons (official).**
- *DOK-1 Facts:* AWS publishes reusable reference architectures and a quarterly-updated official icon set; diagramming is framed as a core Solutions Architect job task.
- *DOK-2 Summary:* The construct-validity bridge — drawing trains the actual job skill the certification proxies, justifying measuring construction/job-transfer as a *separate* outcome from MC-readiness.
- *Link:* https://aws.amazon.com/architecture/reference-architecture-diagrams/

### Category: Competitive Landscape
**Source — Tutorials Dojo; Brainscape; AWS Skill Builder / Cloud Quest; Image Occlusion; Well-Architected IaC Analyzer; Eraser/Cloudcraft.**
- *DOK-1 Facts:* Tutorials Dojo = 400+ MCQs + cheat-sheets (recognition). Brainscape = learner 1–5 confidence self-grade + SRS but over *text* cards. Cloud Quest = console builds, no recall/scheduling. Image Occlusion = recognition (diagram is on screen). Well-Architected IaC Analyzer = AI judges a diagram but for *production audit*. Eraser/Cloudcraft = generate/scan diagrams, no assessment.
- *DOK-2 Summary:* Every neighbor implements one component of the loop; none closes it. The defensibility is execution + honesty-layer quality, not a patentable primitive — and incumbents (Brainscape, AWS) could fast-follow.
- *Link:* https://www.brainscape.com/subjects/aws-solutions-architect-associate

---

## Appendix — Viability Verdict: Does the Evidence Support the Idea?

**Verdict: build it — but as a tool for measuring and calibrating skill honestly, not as a tool that promises to raise the SAA-C03 score faster than plain Anki.**

The strongest parts of the idea are well supported. Separating memory, performance, and readiness — and refusing to show a number the data cannot back up — sit on decades of learning research and on FSRS's own calibration. Drawing from a blank page and revealing the reference only afterward is the right way to get a generation effect rather than a copying exercise. And letting the learner make the final call is defensible — not because the act of grading teaches anything, but because it keeps accountability with the learner while the reference and checklist supply the standard that keeps the grade honest.

The risky parts are real and worth stating plainly. Whether drawing transfers to a multiple-choice exam is the weakest link: the exam never asks anyone to draw, and practice that does not match the test format transfers less. Whether it is worth the time is the second worry: drawing costs two to three times the minutes of a recognition card, and at equal study time it may not beat plain Anki on the exam score. And whether a model can reliably judge a hand-drawn AWS diagram is genuinely unproven — there is no benchmark for this exact task, only evidence from neighboring ones.

The single biggest threat is that the feature trains a skill the exam does not directly reward. Under an equal-time comparison, the drawing mode could tie or lose to plain multiple-choice Anki on the projected score while costing far more minutes. The mitigation is honesty: measure construction skill as its own outcome — it is the actual job skill the certificate stands for — and commit to the harder per-minute bar before running the test.

So the feature is worth building, with the honesty layer as the headline rather than a learning-speed claim. The right way to settle the open question is the project's own ablation:

> We expect the full feature — draw from blank, then AI checklist and reference, then learner self-grade — to produce better-calibrated readiness estimates and better scores on a delayed set of new, exam-style problems than the same feature with the AI and reference removed, and than plain multiple-choice Anki, at equal study time. It fails if, at equal time, the full version beats neither plain Anki on the multiple-choice outcome nor a separate construction outcome; or if the drawing mode only ties plain Anki while costing materially more minutes; or if forcing the human to self-grade after seeing the AI checklist produces no better calibration than letting the AI grade after the learner sees the same feedback; or if drawing quality predicts later performance on new problems no better than chance.
