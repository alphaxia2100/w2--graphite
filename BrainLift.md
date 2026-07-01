# BrainLift — The Draw-It-From-Blank Card: Constructing Graph-Shaped Knowledge from Memory (AWS SAA-C03 as the proving ground)

## Owners

- **Andrew Xia**

_Revised 2026-07-01. This revision consolidates seven overlapping Spiky POVs into three, re-grounds every claim against the primary sources (see Appendix B — Source Verification Ledger), and moves the verdict from "measurement instrument only" to "a genuine learning tool for graph-shaped knowledge, with the honesty layer as the guardrail" — because the evidence supports the bolder claim, within stated bounds._

---

## Purpose

**Purpose (north-star mission):**
Build the flashcard that refuses to let a comfortable retention number stand in for real understanding. For any topic that is *really a graph* — an AWS architecture, a network topology, a state machine, the water cycle — the card prompts the learner to **construct the graph from a blank page** (draw the boxes, connectors, and labels from memory; e.g., "design a multi-AZ resilient web tier with a private DB and S3 static assets"), then reveals a canonical **reference graph**, lets an optional multimodal AI **describe the drawing and check it against the reference as a per-item checklist** (with explicit UNSURE states), and hands the **final Again/Hard/Good/Easy grade to the learner**. The feature measures and displays three *separate* things — MEMORY (can you recall a taught fact now?), PERFORMANCE (can you construct a correct structure for a new prompt?), and READINESS (projected real-exam score) — each with an honest uncertainty range and a single best next thing to study.

The AWS Certified Solutions Architect – Associate (SAA-C03) is the headline proving ground, but the card is **domain-agnostic**: it is driven by a topic's reference graph, not hard-coded to any one exam.

**In Scope:**
- A free-recall *construction* card for graph-shaped topics — build the node-link structure from memory, distinct from recognition/cloze/image-occlusion cards.
- Hand-drawing (in-app editor or photo) as the input modality, with the drawing parsed into a typed candidate graph (nodes / directed edges / labels).
- A two-stage AI **describe-then-check** assist: extract a typed graph from the drawing, then compare it to the reference, surfaced as a per-rubric checklist with explicit UNSURE items. The AI is an assist to honest self-grading, **never the grader of record**.
- Reveal-after: the reference and AI checklist appear only *after* the attempt; the grade buttons unlock only then.
- Honest measurement: separate MEMORY (FSRS retrievability), PERFORMANCE (judged construction on novel prompts), and READINESS (domain-weighted projection) with ranges, calibration history, and a "refuse to score" rule when data is thin.
- The mandated ablation: full card vs. AI-and-reference-off vs. plain Anki at **equal study time**.

**Out of Scope:**
- Replacing FSRS or Anki's Rust scheduling core (we reuse it; MEMORY rides on it).
- AI as grader of record. The AI is an assist to honest self-grading, never the verdict.
- **List-shaped** content — S3 pricing tiers, IAM policy syntax — which stays ordinary MCQ/cloze. Construction is reserved for topology-heavy, genuinely graph-shaped material.
- A promise that drawing raises the SAA-C03 *scaled score* faster than the same minutes spent drilling multiple-choice questions. We claim understanding-beats-memorizing for graph-shaped material; we do **not** claim drawing-beats-equal-time-MCQ-practice on the score. That is measured, not promised.
- Generating diagrams from prompts, or auditing production diagrams/IaC (the inverse job done by existing tools).

---

## DOK 4 — Spiky Points of View

Three claims, each a single sharp, non-consensus, decision-driving stance — **Why** build the graph, how **Effort** must be spent, and how **Honesty** is enforced. Each names the tension it has to survive.

### SPOV 1 (WHY) — If a topic is really a graph, understanding it beats memorizing it — even when the test is 100% multiple choice.

Elaboration: The received wisdom of certification prep is to grind a recognition deck — hundreds of facts and practice questions — until the number goes up. For a graph-shaped topic that is a trap, because what the exam actually tests is not the facts but the structure. The SAA-C03 is the clean case: it is entirely multiple-choice in *format*, and yet it is designed around scenario/application questions that hand you a business constraint and ask which architecture fits — the official guide frames every domain as "design architectures," and practitioner consensus is that success "is not possible for those who have only memorized facts." The *response* format (pick one of four) differs from drawing, but the *cognitive demand* — reason over how the pieces connect — is exactly what constructing the architecture from a blank page trains. The learning science lines up: constructing a node-link representation (a concept map is literally a typed graph) beats studying a ready-made one, with a moderate, robust meta-analytic effect (g = 0.58 overall; constructing g = 0.72 > studying g = 0.43; n = 11,814), across STEM and non-STEM. Conceptual understanding also holds up at least as well as rote on multiple-choice tests over time (in the one longitudinal MCQ study, rote knowledge showed the clearer decline), and retrieval practice transfers best precisely to application and inference questions (Pan & Rickard, 2018). So the spiky claim is not "drawing is nice." It is that for a graphable topic, building the graph is the most direct route to the understanding a scenario exam rewards, and memorization is the detour that feels faster and decays first.

The tension (honest bound): this is understanding-beats-memorizing, **not** a promise that drawing beats an equal number of minutes on same-format MCQ drilling for the score. Transfer is capped by response congruency (Pan & Rickard: without congruency d ≈ 0.28, and the intercept can fall to no positive transfer when the moderators are absent), and the one clean equal-time study of drawing during a heavily visual lesson found *no* benefit because the task degraded into copying (Lawson & Mayer, 2024). Two commitments keep the claim defensible: reserve the card for genuinely graph-shaped material (topology, data flow, state machines, the water cycle), and make the task *construct-from-memory*, not trace-a-picture — so it sits on the concept-map evidence rather than the copying null.

### SPOV 2 (EFFORT) — People are lazy, so friction is the whole game: keep the friction that teaches, and ruthlessly kill the friction that doesn't.

Elaboration: Two facts are both true and in tension. First, the effort of building a graph from nothing is not a cost to be minimized — it *is* the mechanism. Effortful generation beats passive review (generation effect d = 0.40; constructing maps beats studying them), and "desirable difficulties" are difficult on purpose: the conditions that make practice feel hard and slow are often the ones that produce durable, transferable learning, while the smooth ones produce confident forgetting (Bjork; Soderstrom & Bjork, 2015). Second, people are lazy — they take the lowest-friction path available, every time. Put those together and the design almost writes itself: protect the friction that teaches (draw from blank, no reference in sight, no autocomplete of the structure) and attack every gram of friction that does not. The biggest non-teaching friction here is **grading**: comparing your graph to a reference, node by node, is slow and tedious, and a slow grade is exactly where lazy humans defect — they abandon the deck, or they glance, shrug, and tap "Good." That is the one and only job of the AI in this feature: collapse grading *time* by turning the drawing into an explicit component list and checking it against the reference so the comparison takes seconds. It is emphatically **not** the AI's job to be the grader of record — partly for the honesty reasons in SPOV 3, and partly because today's models are far better describers than judges of hand-drawn topology (Henkel, 2025: κ ≈ 0.20 grading a drawing directly vs. κ ≈ 0.47 given a text description; Kortemeyer, 2024; SketchJudge, 2026: best model 78.4% vs. human 83.3%, worst on relational/topological errors).

The tension (honest bound): this only pays if the whole loop beats the lazy alternative — plain multiple-choice Anki — **at equal study time**, not per card. Drawing costs roughly 2–3× the minutes of a recognition review (Lawson & Mayer: ~681 s to draw vs. ~281 s to summarize), so the feature is on the hook to earn those minutes back. We write the per-minute bar down before running the experiment, measure the real time cost, and if the drawing loop merely ties plain Anki while burning far more time, the app reports that as a loss rather than hiding it. Friction is both the point and the enemy; the discipline is knowing which is which.

### SPOV 3 (HONESTY) — People accept fuzzy answers even when it hurts them, so the system must force a crisp standard and refuse to emit fuzzy numbers. *(the hard tension)*

Elaboration: The comfortable failure mode of every self-graded deck is the fuzzy pass — "yeah, I basically knew that" — and people reach for it because it is easy and it feels kind. It is neither. Self-grading against a vague internal sense is where learning quietly rots: the people who know least overestimate most (Kruger & Dunning, 1999: bottom-quartile performers scored ~12th percentile but rated themselves ~62nd), and self-assessment runs persistently high overall (León et al., 2023: overestimation g = 0.206). The fix is not to take the judgment away from the learner — accountability has to stay with them. The fix is to change *what they grade against*. Self-evaluation gets sharply more accurate when anchored to an explicit standard rather than a feeling (Dunlosky et al., 2011), and the reference graph plus a per-item checklist — is this node present? is this edge pointing the right way? is this trust boundary correct? — is that standard: it converts "I basically knew it" into ticked / missed / UNSURE, which is far harder to wave away. Two rules follow. First, the standard must arrive **after** the attempt: show the reference first and drawing degrades into tracing, and the generation benefit evaporates (generation effect; and the copying null — Mason et al., 2013 found copied diagrams matched the no-drawing group). Second, the same anti-fuzz rule governs the app's own outputs: it **refuses to show a readiness number** when the evidence is thin or the AI could not actually read the diagram — while never withholding the *feedback*. This is not just policy; the memory layer already behaves this way, discounting same-day massing (in Anki's FSRS, multiple same-day reviews collapse to a zero-day interval and add no new memory-state datapoint — `reviews_for_fsrs` in `rslib`), so a readiness estimate built on cramming is measuring the wrong thing by construction.

The tension (honest bound): forcing a crisp grade does not make the grade *true* — it makes it *auditable*. The learner can still tick wrong, and the AI's checklist can still be confidently wrong (LLM judges systematically overstate their own correctness — Tian et al., 2025). So the honest system tracks each learner's calibration over time in both directions (improving learners under-rate themselves too), biases the AI toward abstention on the topology items it is worst at, and treats a single clean drawing as a fast-decaying *performance* signal that **widens** the readiness band rather than raising it (learning ≠ performance — Soderstrom & Bjork, 2015; drawing quality predicted an immediate test at R² = 0.35 but a one-week delayed test at R² = 0.02, p = .509 — Lawson & Mayer, 2024). And the crisp-grade discipline is justified by anchoring and accountability, **not** by any belief that the act of rating teaches — judgment-of-learning reactivity is null on educational materials (Zhao et al., 2023).

---

## Experts

**Robert A. & Elizabeth L. Bjork**
- *Who:* Distinguished Research Professors of Psychology, UCLA.
- *Focus:* "Desirable difficulties," and the distinction between learning and performance.
- *Why Follow:* The backbone of SPOV 2 (effortful construction is the mechanism, not a cost) and of SPOV 3's widen-the-band rule (in-the-moment performance is an unreliable index of durable learning).
- *Where:* [UCLA Bjork Learning & Forgetting Lab](https://bjorklab.psych.ucla.edu/)

**Richard E. Mayer**
- *Who:* Distinguished Professor of Psychology, UC Santa Barbara.
- *Focus:* Generative learning and multimedia learning — selecting, organizing, and integrating as the engine of understanding.
- *Why Follow:* Generative learning theory is the "construct it from memory" backbone of SPOV 1, and his own work (Lawson & Mayer, 2024) is the sharpest honest bound on when drawing does *not* help.
- *Where:* [Mayer / multimedia learning](https://education.ucsb.edu/faculty/richard-mayer)

**Jeffrey D. Karpicke**
- *Who:* Professor of Psychological Sciences, Purdue University.
- *Focus:* Retrieval practice — whether recalling beats re-studying, and whether it transfers.
- *Why Follow:* Construct-from-blank is retrieval in the strong sense; his work grounds preferring recall over recognition (and his concept-map retrieval work bridges to SPOV 1).
- *Where:* [Purdue Cognition & Learning Lab](https://learninglab.psych.purdue.edu/)

**John Dunlosky & Katherine Rawson**
- *Who:* Professors of Psychological Sciences, Kent State University.
- *Focus:* How accurately students judge their own learning, and how to fix it.
- *Why Follow:* Their finding that an explicit standard sharply improves self-grading is the direct evidence behind SPOV 3 — unlock the grade only after the reference/checklist is shown.
- *Where:* [Idea-unit standards study (2011)](https://journals.sagepub.com/doi/10.1080/17470218.2010.502239)

**Detlev Leutner**
- *Who:* Professor of Instructional Psychology, University of Duisburg-Essen.
- *Focus:* When drawing-to-learn helps, and the role of comparing your drawing to a model.
- *Why Follow:* His meta-analysis shows the compare-to-reference *integration* step is what makes drawing pay off — the design heart of the reveal-after checklist in SPOV 3.
- *Where:* [Educational Psychology Review (2025)](https://link.springer.com/article/10.1007/s10648-025-10067-7)

**Owen Henkel**
- *Who:* Researcher on AI for education and assessment.
- *Focus:* Multimodal models grading handwritten and hand-drawn student work.
- *Why Follow:* His result that models grade a *description* of a drawing far better than the drawing itself is the single best guide to SPOV 2's "describe, don't grade" AI design.
- *Where:* ["Seeing the Big Picture" (2025)](https://arxiv.org/abs/2510.05538)

**Jarrett Ye & the Open Spaced Repetition team**
- *Who:* Creator and maintainers of FSRS, the scheduler Anki uses.
- *Focus:* Memory modeling and large-scale scheduler benchmarking.
- *Why Follow:* FSRS is the calibrated MEMORY layer this feature builds on, and the code that already discounts same-day massing (SPOV 3's refuse-from-cramming rule).
- *Where:* [open-spaced-repetition (GitHub)](https://github.com/open-spaced-repetition)

---

## DOK 3 — Insights

**On SPOV 1 — understanding beats memorizing for graphs:**
1. The card is best understood as *concept-mapping with a scheduler*: the active ingredient (constructing a node-link structure) has its own meta-analytic base (g = 0.58), and construction beats study — so "build it from blank" is the mechanism, not a UI preference.
2. The exam's format hides its content: SAA-C03 is multiple-choice on the surface and scenario-reasoning underneath, which is why aiming a graph-construction card at a selection test is not a category error — but only for the scenario/application items, and only for genuinely graph-shaped material.
3. Rote and conceptual knowledge don't decay identically — in the one longitudinal MCQ study, rote showed the clearer drop — so the spaced intervals a spaced-repetition app runs on tend to favor retained understanding over memorized facts (suggestive, not settled).

**On SPOV 2 — friction and laziness:**
4. Learning friction and grading friction are different substances that look alike; the entire AI design falls out of separating them — remove grading *time*, never remove drawing *effort*.
5. Because the model reads labels better than connectivity, it is weakest exactly where AWS correctness lives (is the DB in a private subnet? is the ALB across two AZs?), so "describe, don't grade" plays to what these models are good at and routes their weakness to the human.
6. The equal-time bar is both the honest frame and a real risk: a 2–3× time cost means the feature can be genuinely good and still *lose per minute*, so the per-minute bar must be pre-registered and the loss reportable.

**On SPOV 3 — honesty:**
7. The best-known fix for inflated self-grading is an explicit standard, and the reference-plus-checklist is that standard almost by accident — the button stays with the learner; the standard is what makes the click trustworthy.
8. Reveal-after is not a tunable setting; it is a load-bearing wall — show the answer first and the card silently becomes recognition.
9. A clean drawing should *lower* confidence in readiness, not raise it: fluent in-the-moment performance is an unreliable index of durable learning, so the app should widen the band on a strong attempt and schedule a fresh check on a new prompt.
10. Refusing to answer is a feature, not a flaw: the memory layer already ignores same-day massing, so the honest move is to let the shakier judge term dominate the combined uncertainty and withhold the *number* when data is thin — while never withholding the *feedback*.

---

## DOK 2 — Knowledge Tree

### Category: Retrieval Practice & Spacing
**Source — Roediger & Karpicke (2006), *Test-Enhanced Learning*.**
- *DOK-1 Facts:* At 5 min, restudy led (81% vs 75%); at 1 week the tested group led (56% vs 42%). Exp 2: STTT recalled 61% vs SSSS 40% at 1 week — even though the study-only group re-read the passage ~14 times vs ~3–4 for the tested group, and rated its own memory highest.
- *DOK-2 Summary:* Retrieval beats restudy at delay even though restudy feels better and raises confidence — the crossover and confidence inversion that motivate both the construction card and the honesty rule.
- *Link:* https://journals.sagepub.com/doi/abs/10.1111/j.1467-9280.2006.01693.x

**Source — Pan & Rickard (2018), *Transfer of Test-Enhanced Learning*.**
- *DOK-1 Facts:* 192 effect sizes, 122 experiments, 67 articles, N=10,382. Overall transfer d=0.40 [0.31, 0.50]; transfer is greatest to application/inference questions; moderated strongly by response congruency and initial test performance; the bias-corrected intercept can indicate *no* positive transfer when moderators are absent.
- *DOK-2 Summary:* Transfer is real but bounded by response congruency — the precise reason to (a) claim understanding-beats-memorizing rather than drawing-beats-MCQ-practice, and (b) hedge the PERFORMANCE band.
- *Link:* https://pdf.retrievalpractice.org/transfer/Pan_Rickard_2018.pdf

**Source — Cepeda et al. (2008), *Spacing Effects in Learning*.**
- *DOK-1 Facts:* N>1,350; the optimal inter-study gap declines from ~20–40% of a 1-week test delay to ~5–10% of a 1-year delay.
- *DOK-2 Summary:* Optimal spacing is an explicit function of retention interval — the relationship FSRS operationalizes, and part of the basis for refusing a readiness number from massed same-day data.
- *Link:* https://laplab.ucsd.edu/articles/Cepeda%20et%20al%202008_psychsci.pdf

### Category: Constructing Graphs & Generative Learning
**Source — Schroeder, Nesbit, Anguiano & Adesope (2018), *Studying and Constructing Concept Maps: a Meta-Analysis*.**
- *DOK-1 Facts:* 142 independent effect sizes (n=11,814). Learning with concept/knowledge maps g=0.58; **creating** maps (g=0.72) beat **studying** maps (g=0.43); effective across STEM and non-STEM.
- *DOK-2 Summary:* A concept map is a typed node-link graph, so this is the closest direct evidence base for the card — and it says construction (our task) is the stronger version. The load-bearing support for SPOV 1.
- *Link:* https://link.springer.com/article/10.1007/s10648-017-9403-9

**Source — Nesbit & Adesope (2006), *Learning With Concept and Knowledge Maps: A Meta-Analysis*.**
- *DOK-1 Facts:* Broad meta-analysis (Review of Educational Research) finding concept/knowledge maps improve knowledge recall and transfer relative to reading text/attending lectures, across conditions.
- *DOK-2 Summary:* The earlier, independent confirmation that graph-shaped external representations aid comprehension and transfer — corroborates SPOV 1 beyond a single meta.
- *Link:* https://www.sfu.ca/~jcnesbit/articles/NesbitAdesope2006.pdf

**Source — Bertsch et al. (2007), *The Generation Effect: A Meta-Analytic Review*.**
- *DOK-1 Facts:* d=0.40 across 86 studies, 445 effect sizes, 17,711 subjects; by test type: free recall 0.32, cued 0.55, recognition 0.46.
- *DOK-2 Summary:* Self-generated information is remembered better than provided information — the core mechanism behind reveal-after (SPOV 3) and effortful construction (SPOV 2), with the honest caveat that the effect is smallest in the free-recall regime this card targets.
- *Link:* https://link.springer.com/article/10.3758/BF03193441

**Source — Wammes, Meade & Fernandes (2016), *The drawing effect*.**
- *DOK-1 Facts:* 7 free-recall experiments; drawing beat writing robustly, and the benefit survived reduced encoding time (as little as ~4 s) and longer lists; not explained by depth-of-processing, imagery, or picture superiority alone.
- *DOK-2 Summary:* Evidence that drawing can win as an encoding act in principle — but for single concrete words, not multi-element architectures, so it supports "construction can pay per-item" without generalizing to our high-element task.
- *Link:* https://journals.sagepub.com/doi/10.1080/17470218.2015.1094494

**Source — Leutner & Biele (2025), *Without Integration, Everything Is Nothing*.**
- *DOK-1 Facts:* 14 studies, 16 comparisons, N=1,213, comparing *supported* vs *unsupported* drawing. Integration support g=+0.35 (p=.048); non-integration support g=−0.15 (p=.186); other moderators non-significant.
- *DOK-2 Summary:* Conditional on drawing, the compare-to-reference *integration* step is the decisive moderator — justifying the reference+checklist as the payoff (SPOV 3), while reminding us the baseline here is unsupported drawing.
- *Link:* https://link.springer.com/article/10.1007/s10648-025-10067-7

**Source — Lawson & Mayer (2024), *When Summarizing Is Effective but Drawing Is Not*.**
- *DOK-1 Facts:* Drawing took ~2.4× the time of summarizing (M=681 s vs 281 s) with no benefit over control; summarizing won (d=0.48 immediate / 0.54 delayed). Drawing quality predicted the immediate posttest (R²=0.35, p<.001) but not the delayed posttest (R²=0.02, p=.509). Authors note drawing was prognostic in prior *text-based* lessons (Mason et al., 2013), suggesting the null is a boundary condition of drawing during an already-visual lesson (copying risk).
- *DOK-2 Summary:* The per-minute cost, the fast decay of drawing-quality predictiveness, and the copying boundary — the empirical basis for SPOV 2's equal-time bar, SPOV 3's widen-the-band rule, and the "construct from memory, don't trace" reframe.
- *Link:* https://pmc.ncbi.nlm.nih.gov/articles/PMC11402827/

### Category: Understanding vs. Memorization & Exam Format
**Source — Haycocks et al. (2024), *Factual vs Conceptual Knowledge via MCQs: A Longitudinal Study*, Advances in Medical Education and Practice.**
- *DOK-1 Facts:* 45 MCQs (categorized recall/verbatim vs concept/inference by a faculty panel) given to a medical cohort in 2020 and re-administered ~2 years later (n=56). In 2020, recall items were answered correctly more often than concept items (82.0% vs 60.9%, p=.002) — conceptual items were *harder*. By 2022 both declined; the recall decline was significant (82.0%→59.8%, p<.001) while the concept decline was only marginal (p=.050). The authors call the differential-decay hypothesis *inconclusive*.
- *DOK-2 Summary:* Direct-in-format evidence that on MCQs, conceptual items are harder to acquire and that rote knowledge showed the clearer decay — weakly consistent with SPOV 1, cited with the paper's own honesty about the inconclusive durability result and its small sample.
- *Link:* https://pmc.ncbi.nlm.nih.gov/articles/PMC11653852/

**Source — AWS SAA-C03 exam nature (official guide + practitioner consensus).**
- *DOK-1 Facts:* AWS frames every domain as "design architectures … secure, resilient, high-performing, cost-optimized," and the guide is task-statement/scenario oriented. Practitioner sources consistently describe the exam as heavily scenario-based (community estimates ~60–70% scenario), rewarding trade-off reasoning over recall of service limits.
- *DOK-2 Summary:* The construct-validity bridge for SPOV 1: an MCQ-format exam can still test relational/architectural understanding, so a graph-construction card is aimed at what the exam actually measures. (The ~60–70% figure is practitioner consensus, not an official AWS statistic.)
- *Link:* https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html

### Category: Metacognition & Self-Grading
**Source — Kruger & Dunning (1999), *Unskilled and Unaware of It*.**
- *DOK-1 Facts:* Across 4 studies, bottom-quartile performers (~12th percentile actual) estimated themselves at ~62nd percentile; the same incompetence that produces errors blocks detecting them.
- *DOK-2 Summary:* Self-grading is least reliable for the weakest learners — the core risk in learner-as-final-judge. (Caveat: the popular "Mount Stupid" curve is largely a statistical artefact — [Gignac & Zajenkowski, 2020](https://gwern.net/doc/iq/2020-gignac.pdf) — so we lean on the miscalibration, not the chart.)
- *Link:* https://sites.lsa.umich.edu/sasi/wp-content/uploads/sites/275/2015/11/krugerdunning99.pdf

**Source — Dunlosky, Hartwig, Rawson & Lipko (2011), *Idea-Unit Standards*.**
- *DOK-1 Facts:* Without standards, learners over-credit their own free-recall answers; supplying idea-unit standards markedly improves self-evaluation accuracy, robust to strict/lenient scoring.
- *DOK-2 Summary:* Anchoring self-grading to an explicit standard is the strongest direct fix for inflation — the reference graph + AI checklist is exactly this standard, so the grade buttons unlock only after it is shown.
- *Link:* https://journals.sagepub.com/doi/10.1080/17470218.2010.502239

**Source — León, Panadero & García-Martínez (2023), *Self-assessment scoring-accuracy meta-analysis*, Educational Psychology Review.**
- *DOK-1 Facts:* ~160 studies, 29,352 participants; self-vs-expert agreement Fisher z=0.472 (r≈0.44); *persistent overestimation* g=0.206; overestimation shrinks with feedback, experience, and content knowledge.
- *DOK-2 Summary:* The most relevant SELF-assessment (not peer) anchor: self-grading is moderately accurate at best and biased high — the reason to supply a standard and track per-learner divergence.
- *Link:* https://link.springer.com/article/10.1007/s10648-023-09819-0

**Source — Zhao et al. (2023), *JOL reactivity on educational materials*, Journal of Intelligence.**
- *DOK-1 Facts:* Three experiments (one preregistered) found *null* judgment-of-learning reactivity on educational materials (Bayesian support for no effect); the earlier d=0.44 reactivity effect did not replicate.
- *DOK-2 Summary:* The act of rating one's own recall is *not* a reliable second learning episode — so human-final-grade is justified by accountability + anchored calibration + the AI-reliability hedge, not by the rating act itself.
- *Link:* https://www.mdpi.com/2079-3200/11/10/190

**Source — Butterfield & Metcalfe (2001 / 2011), *Hypercorrection*.**
- *DOK-1 Facts:* High-confidence errors are corrected *more* by feedback than low-confidence errors; the effect persists ~1 week, though high-confidence errors can return without an intervening test.
- *DOK-2 Summary:* Capturing pre-reveal confidence turns confident-wrong drawings into the highest-value learning events — provided the app reschedules a re-test, not just shows feedback. *(Carried forward from prior research; classic finding, not re-pulled this pass.)*
- *Link:* https://pubmed.ncbi.nlm.nih.gov/21989771/

**Source — Soderstrom & Bjork (2015), *Learning versus Performance: An Integrative Review*.**
- *DOK-1 Facts:* Performance during acquisition is an unreliable index of long-term learning; manipulations can move performance and learning in opposite directions, and people mistake current performance for durable learning.
- *DOK-2 Summary:* The theoretical spine of SPOV 3's widen-the-band rule — a clean drawing today is a performance snapshot, not readiness evidence.
- *Link:* https://journals.sagepub.com/doi/10.1177/1745691615569000

### Category: AI Visual Judging
**Source — Henkel et al. (2025), *Seeing the Big Picture*.**
- *DOK-1 Facts:* Direct grading of hand-drawn illustrations κ≈0.20; given a *human text description* κ≈0.47 (human-level); arithmetic grading κ≈0.90 (95% accuracy).
- *DOK-2 Summary:* The bottleneck is visual perception, not judgment — the pointer to a two-stage describe-then-check pipeline (SPOV 2). (Honest caveat: the gains used *human* descriptions; an auto-extractor inherits the perception problem.)
- *Link:* https://arxiv.org/abs/2510.05538

**Source — Kortemeyer et al. (2024), *Grading a handwritten thermodynamics exam with multimodal LLMs* (Phys. Rev. PER).**
- *DOK-1 Facts:* Grading hand-drawn process diagrams was "less reliable than mathematical derivations due to the difficulty in differentiating essential details from extraneous information"; fine-grained whole-problem rubrics caused bookkeeping failures.
- *DOK-2 Summary:* The closest peer-reviewed anchor for AI-judge *fragility* on hand-drawn inputs — the basis for UNSURE-by-default topology items and routing low-confidence extractions to the learner.
- *Link:* https://arxiv.org/abs/2406.17859

**Source — Stogiannidis et al. (2025), *Mind the Gap: Benchmarking Spatial Reasoning in VLMs*.**
- *DOK-1 Facts:* A dedicated benchmark documents systematic, sometimes large, spatial-reasoning shortfalls in current VLMs. (Measures spatial reasoning broadly; does not by itself establish a clean object-vs-relation dissociation.)
- *DOK-2 Summary:* Independent evidence that VLMs are unreliable on exactly the spatial/relational structure AWS topology depends on — so calibrate per task and keep topology items UNSURE by default. *(Carried forward; not re-pulled this pass.)*
- *Link:* https://arxiv.org/abs/2503.19707

**Source — Keith et al. (2025), *VLM-as-a-Judge for visual-narrative coherence*, Electronics 14(21):4199.**
- *DOK-1 Facts:* Direct-vision VLM judging reached inter-rater ICC=0.718 vs 0.339 for caption-based, but at 10.8× the compute; both only weak-to-moderately correlated with the objective metric (r=0.28–0.36).
- *DOK-2 Summary:* Extract-first is *not* universally better than direct vision — so the two-stage architecture is a defensible default to A/B test, not a proven optimum.
- *Link:* https://www.mdpi.com/2079-9292/14/21/4199

**Source — SketchJudge (2026); SketchMind (2025); FlowVQA (2024).**
- *DOK-1 Facts:* SketchJudge (1,015 hand-drawn STEM answers): GPT-5 78.4% / Gemini-2.5-Flash 77.7% vs human 83.3%, worst on relational/topological errors. SketchMind: reported same-model lift ~55.6%→77.1% via a Sketch Reasoning Graph + graph-edit-distance. FlowVQA: fact-retrieval far above topological understanding, with the caveat that the two figures come from different prompting conditions.
- *DOK-2 Summary:* VLMs read labels better than connectivity, and structured graph rubrics recover *some* of the gap; but the split is messier than clean figures imply, and the judge still trails humans — so it must be an assist with UNSURE-by-default topology and a multi-model panel for the range. *(SketchJudge verified this pass; SketchMind/FlowVQA carried forward as illustrative.)*
- *Link:* https://arxiv.org/abs/2601.06944

**Source — Tian et al. (2025), *Overconfidence in LLM-as-a-Judge*; with Zheng et al. (2023, MT-Bench) and Krumdick et al. (2025).**
- *DOK-1 Facts:* LLM-as-judge confidence "significantly overstates actual correctness" across models; reference-free judging inflates false-accepts; naive majority-voting over one model compounds overconfidence. Mitigation is a multi-model ensemble/fuser.
- *DOK-2 Summary:* The dangerous failure is *systematic over-grading*, not symmetric noise — so condition on the reference, bias abstention strict, and use a multi-model panel (not single-model re-runs) for the range. *(Tian verified this pass; companion cites carried forward.)*
- *Link:* https://arxiv.org/abs/2508.06225

### Category: AWS SAA Exam Structure
**Source — AWS SAA-C03 Exam Guide (official).**
- *DOK-1 Facts:* Four scored domains — Secure 30%, Resilient 26%, High-Performing 24%, Cost-Optimized 20%. 65 questions (50 scored), 130 min, scaled 100–1,000, pass=720, compensatory scoring. 100% multiple-choice/multiple-response text; *no* drawing. Validated against the Well-Architected Framework.
- *DOK-2 Summary:* The exam is pure *selection in format* but *architectural reasoning in content*; Secure+Resilient = 56% of weight and are the most graph-amenable domains, and the domain weights drive the READINESS reweighting — so refuse a readiness number until each domain has minimum judged data.
- *Link:* https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html

**Source — AWS Reference Architecture Diagrams & Architecture Icons (official).**
- *DOK-1 Facts:* AWS publishes reusable reference architectures and a quarterly-updated official icon set; diagramming is framed as a core Solutions Architect job task.
- *DOK-2 Summary:* The construct-validity bridge — constructing the graph trains the actual job skill the certification proxies, justifying measuring construction/job-transfer as a *separate* outcome from MC-readiness.
- *Link:* https://aws.amazon.com/architecture/reference-architecture-diagrams/

### Category: Competitive Landscape
**Source — Tutorials Dojo; Brainscape; AWS Skill Builder / Cloud Quest; Image Occlusion; Well-Architected IaC Analyzer; Eraser/Cloudcraft.**
- *DOK-1 Facts:* Tutorials Dojo = 400+ MCQs + cheat-sheets (recognition). Brainscape = 1–5 confidence self-grade + SRS over *text* cards. Cloud Quest = console builds, no recall/scheduling. Image Occlusion = recognition (diagram is on screen). Well-Architected IaC Analyzer = AI judges a diagram but for *production audit*. Eraser/Cloudcraft = generate/scan diagrams, no assessment.
- *DOK-2 Summary:* Every neighbor implements one component of the loop; none closes it (construct-from-blank → describe-not-grade → anchored self-grade → honest three-score). Defensibility is execution + honesty-layer quality, not a patentable primitive — incumbents could fast-follow.
- *Link:* https://www.brainscape.com/subjects/aws-solutions-architect-associate

---

## Appendix A — Viability Verdict: Does the Evidence Support the Idea?

**Verdict: build it — as a genuine learning tool for graph-shaped knowledge, with the honesty layer as the guardrail, not as a promise to raise the SAA-C03 score faster than the same minutes of multiple-choice drilling.**

This is a deliberate move from the previous verdict ("build it, but only as a measurement/calibration instrument, not a learn-faster tool"). The evidence supports the stronger claim, within bounds. For a topic that is genuinely a graph, constructing the graph from memory builds the relational understanding a scenario-based exam actually tests — and understanding of that kind is more durable and more transferable than memorized facts. That rests on three strong legs plus a tentative fourth, all re-checked against source: the concept-map *construction* literature (g=0.58; constructing > studying), the scenario/application nature of the SAA-C03, retrieval-transfer being strongest to application/inference items, and — more tentatively — a durability signal where rote knowledge decayed more clearly than conceptual on a longitudinal MCQ test (the authors call the differential inconclusive, so we lean on it lightly).

The bounds are real and stated plainly:
- It is **understanding-beats-memorizing, not drawing-beats-equal-time-MCQ-drilling**. Response-format congruency caps transfer (Pan & Rickard), and the fair test is equal study time versus plain Anki — a bar the ~2–3× time cost of drawing has to clear (Lawson & Mayer). We pre-register the per-minute bar and are willing to report a tie-at-higher-cost as a loss.
- It applies to **genuinely graph-shaped material and to construct-from-memory**, not tracing. Loose drawing during already-visual material can collapse into copying and show no benefit; list-shaped content stays ordinary MCQ/cloze.
- Whether a model can reliably read a **hand-drawn** AWS diagram is still unproven for this exact task. The AI is an assist that *describes and abstains*, gated on beating a deterministic graph-edit-distance baseline on held-out human-labeled data, never the grader of record.

The single biggest remaining threat is the equal-time one: the drawing loop could be genuinely good and still lose per minute against plain multiple-choice Anki on the scaled score. The mitigation is the honesty layer itself — measure construction quality as its own outcome (it is the actual job skill the certificate proxies), separate it from the projected MC-readiness number, and commit to the harder per-minute bar before running the test.

So the feature is worth building as a learning tool, with the three spikes doing the work: **Why** (construct graphs for graph-shaped topics), **Effort** (keep drawing friction, kill grading friction, honor the equal-time bar), **Honesty** (anchor self-grading to a revealed standard and refuse fuzzy numbers). The way to settle the open question is the project's own ablation:

> We expect the full card — construct the graph from blank, then the AI checklist and reference, then the learner's anchored self-grade — to produce better delayed performance on new graph-construction and scenario-MCQ problems, and better-calibrated readiness, than the same card with the AI and reference removed, and than plain multiple-choice Anki, at equal study time. It fails if, at equal time: the full version beats neither plain Anki on a scenario-MCQ outcome nor a separate construction outcome; or the drawing loop only ties plain Anki while costing materially more minutes; or forcing the human to self-grade after seeing the AI checklist produces no better calibration than letting the AI grade after the learner sees the same feedback; or drawing quality predicts later performance on new problems no better than chance.

---

## Appendix B — Source Verification Ledger

Every load-bearing citation was checked against the primary source during the 2026-07-01 revision. No inaccuracies were found in the figures carried from the prior draft; the items marked "carried forward" are well-established results not independently re-pulled this pass.

**Independently verified this pass (figures confirmed against the primary source):**
- **Roediger & Karpicke (2006)** — 81% vs 75% at 5 min; 56% vs 42% at 1 week (Exp 1); 61% vs 40% at 1 week (Exp 2). ✓ Accurate.
- **Pan & Rickard (2018)** — 122 experiments, N=10,382, d=0.40 [0.31, 0.50]; congruency- and initial-performance-moderated; intercept can show no transfer without moderators. ✓ Accurate.
- **Cepeda et al. (2008)** — N>1,350; optimal gap ~20–40% of a 1-week delay → ~5–10% of a 1-year delay. ✓ Accurate.
- **Bertsch et al. (2007)** — d=0.40; 86 studies, 445 effect sizes, 17,711 subjects; free recall 0.32 / cued 0.55 / recognition 0.46. ✓ Accurate.
- **Wammes, Meade & Fernandes (2016)** — 7 experiments; drawing > writing; robust at reduced encoding time; single concrete words. ✓ Accurate.
- **Leutner & Biele (2025)** — 14 studies / 16 comparisons, N=1,213; integration g=+0.35 (p=.048), non-integration g=−0.15 (p=.186). ✓ Accurate.
- **Lawson & Mayer (2024)** — authors confirmed (Alyssa P. Lawson & Richard E. Mayer, *Frontiers in Psychology*); draw time M=681.17 s; summarizing d=0.48/0.54; drawing quality R²=0.35 immediate (p<.001) vs R²=0.02 delayed (p=.509); Mason et al. (2013) copying-null referenced within. ✓ Accurate.
- **Schroeder, Nesbit, Anguiano & Adesope (2018)** — concept-map meta g=0.58; constructing 0.72 > studying 0.43; n=11,814, 142 effect sizes. ✓ Accurate (new source).
- **Haycocks et al. (2024), factual-vs-conceptual MCQ longitudinal** — authors confirmed (Haycocks et al., *Adv. Med. Educ. Pract.* 2024; DOI 10.2147/AMEP.S478193); recall 82.0% vs concept 60.9% in 2020; recall decline significant (p<.001), concept decline marginal (p=.050); differential-decay called *inconclusive* by the authors; n=56. ✓ Accurate, cited with the caveat (new source).
- **Kruger & Dunning (1999)** — bottom-quartile ~12th percentile actual, ~62nd estimated. ✓ Accurate.
- **León, Panadero & García-Martínez (2023)** — g=0.206 overestimation; Fisher z=0.472; ~160 studies, 29,352 participants. ✓ Accurate.
- **Zhao et al. (2023)** — 3 experiments (1 preregistered); null JOL reactivity; earlier d=0.44 did not replicate. ✓ Accurate.
- **Soderstrom & Bjork (2015)** — performance is an unreliable index of learning; opposite-direction manipulations. ✓ Accurate (new expert cite).
- **Henkel et al. (2025)** — κ≈0.20 direct / 0.47 with description / 0.90 arithmetic (95%). ✓ Accurate.
- **Kortemeyer et al. (2024)** — hand-drawn process diagrams less reliable than derivations; perception the bottleneck. ✓ Accurate (thermodynamics exam; arXiv 2406.17859).
- **Keith et al. (2025)** — ICC=0.718 direct vs 0.339 caption-based; 10.8× compute; r=0.28–0.36 vs the objective metric. ✓ Accurate.
- **SketchJudge (2026)** — GPT-5 78.4% / Gemini-2.5-Flash 77.7% vs human 83.3%; worst on relational errors. ✓ Accurate (arXiv 2601.06944).
- **Tian et al. (2025)** — LLM-as-judge confidence overstates correctness; ensemble/fuser mitigation. ✓ Accurate (arXiv 2508.06225).
- **AWS SAA-C03 domain weights** — Secure 30% / Resilient 26% / High-Performing 24% / Cost-Optimized 20% (official guide). ✓ Accurate.
- **SAA-C03 scenario nature** — official "design architectures" framing verified; the ~60–70% scenario figure is practitioner consensus, labeled as such.
- **FSRS same-day handling (in-repo)** — `reviews_for_fsrs` (`rslib/src/scheduler/fsrs/params.rs`) computes `delta_t` in whole days, skips cramming entries, and during training emits a memory-state item only when `delta_t > 0`; same-day reviews collapse to a zero-day interval. ✓ Verified in code.

**Carried forward (well-established; not independently re-pulled this pass):**
- **Dunlosky et al. (2011)** — idea-unit standards improve self-evaluation accuracy (consistent with León 2023).
- **Butterfield & Metcalfe (2001/2011)** — hypercorrection of high-confidence errors.
- **Stogiannidis et al. (2025)** — VLM spatial-reasoning shortfalls (arXiv 2503.19707).
- **SketchMind (2025); FlowVQA (2024)** — used illustratively; the doc already flags the cross-condition caveat.
- **Nesbit & Adesope (2006)** — corroborating concept-map meta.
