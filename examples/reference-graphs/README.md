# Reference graphs

A **reference graph** is the answer key for a draw-from-blank card, expressed as an inspectable typed graph. The card type is **domain-agnostic**: anything whose understanding is really a graph — an AWS architecture, the water cycle, a Krebs cycle, a network topology, a state machine — uses the same shape. The two seed domains here exist so the feature can be **tested on more than one topic**.

## Shape

```jsonc
{
  "id": "...", "domain": "...", "title": "...",
  "prompt": "...",                    // what the learner is asked to draw, from memory
  "nodes": [ { "id", "type", "label", "attrs?", "required" } ],
  "edges": [ { "id", "from", "to", "label", "direction?", "required" } ],
  "rubric": [ { "id", "kind", "text", "weight" } ]   // kind: node | process | constraint | direction
}
```

- **nodes / edges** = the canonical diagram. `required: false` marks elements that are correct but not essential, so a learner isn't penalized for omitting them.
- **rubric** = the human-readable checklist the learner (and, in the AI version, the model) grades against. Each item resolves to **✓ / ✗ / UNSURE**. Weights let boundary/direction errors matter more than a missing optional node.
- The learner's drawing is turned into a *candidate* graph of the same shape; judging = comparing candidate vs reference per rubric item.

## Files

| File | Domain | Why it's a good test |
|---|---|---|
| [`water-cycle.reference.json`](water-cycle.reference.json) | Earth science | Reservoirs are nodes; processes (evaporation, condensation, precipitation, runoff) are directed edges. Direction and "the cycle closes" are exactly the kind of relational understanding the card targets. |
| [`aws-multi-az-web-tier.reference.json`](aws-multi-az-web-tier.reference.json) | AWS SAA-C03 | Topology + security boundaries (DB in a private subnet, ALB across ≥2 AZs) are the hard, high-value parts. |
