# Audit rubric

Anchored rubric for scoring a journey artifact on eleven dimensions (A–K), with tests for generic or unsupported content, a rule for separating blockers from ordinary findings, and a procedure that lets two auditors reach the same scores. Use it in workflow steps 2–4. The result fills `assets/audit-scorecard.md`.

A score is a summary of findings, not a substitute for them. Every score cites the criteria it met and missed, and every finding has its own `evidence_status`.

Grounding: analytic rubrics with described performance levels (Brookhart 2013; Jonsson & Svingby 2007, who found that rubrics improve scoring consistency mainly when anchors are explicit and raters are trained with examples); inter-rater agreement statistics (Cohen 1968; Landis & Koch 1977); graphical integrity (Tufte).

## How to read the anchors

- Each level lists observable criteria: things you can point to in the artifact, its registers, or its cited sources.
- **Award a level only if all its criteria are met, and all criteria of the levels below it.** If an artifact meets most of level 3 but misses one criterion of level 2, it scores 1.
- Score against the artifact's stated purpose. A hypothesis map built to plan research is not marked down for having `hypothesis` claims; it is marked down if it presents them as `observed`.
- If a dimension cannot be assessed from the material provided, record `unknown`, not 0. Missing material and bad material are different findings.
- A dimension that does not apply to the purpose (for example, service linkage for a first-draft hypothesis map) is marked `n/a` with the reason.

## Anchors by dimension

### A. Scope and boundaries

- **0** — No stated actor, or the "journey" is an organizational process, channel, or product area; start and end are absent.
- **1** — Actor, trigger, start, and end are stated, but at least one is ambiguous (two actors, an end defined by the organization such as "case closed"), or current and target states are mixed.
- **2** — One actor; trigger, start, end, and `state` stated; end is an actor outcome; exclusions listed.
- **3** — As 2, plus the journey has an ID in the registry, its level (L2) and parent are stated, and neighboring journeys are linked by relations rather than absorbed.

### B. Actor centricity

- **0** — Stages or steps are named after teams, systems, or internal milestones ("KYC", "Underwriting", "Fulfilment").
- **1** — Stage names are actor-worded, but goals and actions underneath are the organization's activities.
- **2** — Each stage has an actor goal and actor actions; organizational activity appears only in backstage or linked blueprints.
- **3** — As 2, plus stage boundaries are points the actor would notice, and the stated job or desired outcome is solution-independent.

### C. Evidence

- **0** — No sources, or claims are labeled `observed` without any cited evidence (status inflation).
- **1** — Some evidence cited, but claims cannot be traced to specific sources, or behavior and attitude are conflated, or sample and limitations are absent.
- **2** — Stage-level claims cite evidence IDs; each ID resolves to a source, date, and sample; `evidence_status` is used and no claim is stronger than its evidence; `stakeholder-input` supports `hypothesis` at most.
- **3** — As 2, plus unknowns are registered as evidence gaps, contradictions are recorded with a resolution, and evidence is within the journey's freshness rule.

### D. Journey coherence

- **0** — Stages are a list of touchpoints or topics with no progression.
- **1** — Stages progress but overlap, skip a step the actor must take, or include waiting and handoffs only implicitly.
- **2** — Stages are mutually exclusive, in the actor's order, each with an entry and exit condition; waiting stages are explicit where they exist.
- **3** — As 2, plus the stage model is derived from evidence (for example, a synthesis trail) and stage granularity is consistent across the journey.

### E. Variation and nonlinearity

- **0** — A single straight path is shown although the evidence shows branches, loops, or segments with different paths.
- **1** — Variation is mentioned in notes but not modeled.
- **2** — Material branches, loops, and alternative contexts are modeled as variants or branches with the condition that triggers them.
- **3** — As 2, plus the share or frequency of each path is stated where known, and unrepresented segments are named as gaps.

### F. Experience integrity

- **0** — Emotions, expectations, quotes, or numbers appear with no source, or sources exist but do not say what the artifact claims.
- **1** — Experience layers are present and plausible, but most points lack evidence IDs or are generic across stages.
- **2** — Each emotion point, expectation, workaround, and quote cites evidence; unevidenced layers are omitted or labeled `hypothesis`.
- **3** — As 2, plus experience claims differ by segment where the evidence differs, and intensity is shown only where it was measured or rated by actors.

### G. Service linkage

- **0** — Pain points are listed with no link to what produces them.
- **1** — Causes are named, but at the level of symptoms or blame ("agents don't update").
- **2** — Material pain points link to blueprint layers or root causes with `evidence_status` per causal link.
- **3** — As 2, plus root causes are tested (counterfactual, timing, dose, or mechanism trace) or labeled as untested, and owners are named.

### H. Metrics

- **0** — No metrics, or only organizational activity counts.
- **1** — Metrics named but not defined (no numerator, denominator, population, or window), or not attached to nodes.
- **2** — One actor-outcome metric for the journey; stage metrics defined and attached to nodes; baselines stated or marked "not yet measured".
- **3** — As 2, plus causal links between metrics carry `evidence_status`, and each optimized metric has a guardrail.

### I. Opportunities

- **0** — "Opportunities" are features or projects.
- **1** — Problems are stated, but not separated from root causes, or not linked to nodes and evidence.
- **2** — Opportunities are solution-independent, one per root cause, linked to a node, evidence, and `root_cause_status`.
- **3** — As 2, plus each links `moment_ids` and `metric_ids`, has a decision with recorded criteria, and expected movement is stated.

### J. Governance

- **0** — No owner, version, or date.
- **1** — An owner or date exists, but no version, review cadence, or freshness rule.
- **2** — Named owner role, version, last review date, review interval, and freshness rule; `status` matches the evidence.
- **3** — As 2, plus a change log records material changes with reasons, evidence, affected nodes, and approvers.

### K. Visual and model integrity

- **0** — The visual contradicts the model or the evidence: nodes appear in the picture that exist in no register (or vice versa), current and target are drawn as one path, or graphical encodings imply data that does not exist (an emotion curve with measured-looking heights and no measurement).
- **1** — The visual matches the model's content, but IDs are absent, so claims in the picture cannot be traced; or uncertainty is not distinguishable from fact.
- **2** — Every stage and moment in the visual carries its ID and matches the node and moment registers; `hypothesis` and `unknown` content is visually distinguished; a legend explains every encoding.
- **3** — As 2, plus encodings are proportional to the data they represent (Tufte's graphical integrity: no exaggerated scales, no area encodings for linear quantities), and the visual is a view generated from or checked against the registers, with the check date recorded.

## Blockers and non-blockers

A **blocker** means the artifact must not be used for its stated decision until fixed. Blockers override scores: an artifact with one blocker is not fit for purpose, however well it scores elsewhere.

| Blocker | Typical dimension |
|---|---|
| Wrong scope: the artifact models a different actor, journey, or state than the decision requires | A |
| Process flow presented as an actor journey | B |
| Status inflation: `observed` claims without observed evidence, or stakeholder input presented as actor evidence | C |
| Current and target states mixed in one model | A, K |
| Fabricated content: quotes, numbers, or emotion data that no source contains | F, K |
| Visual contradicts the registers the decision will use | K |

**Non-blockers** reduce value but do not invalidate the decision: missing variation where the evidence shows little of it, undefined metrics on a draft, opportunities not yet prioritized, governance gaps on a new artifact, formatting. They go into the remediation sequence after blockers.

Decision rule: fix blockers first, then the lowest-scoring dimension that the stated decision depends on. Visual polish comes last.

## Tests for generic or unsupported content

Artifacts produced quickly, by a template, a workshop alone, or a text generator, share recognizable failures. Run these tests; each produces an observed finding about the artifact. Do not record a claim about how the artifact was made unless someone states it; the finding is about content, and the origin is at most a `hypothesis`.

| Test | Procedure | Flag when |
|---|---|---|
| Provenance sample | Pick 5 claims at random (stage goals, pain points, quotes, numbers); trace each to an evidence ID and its source | Fewer than 4 of 5 trace |
| Template stages | Compare stage names with a generic lifecycle (awareness, consideration, purchase, onboarding, usage, loyalty, advocacy) | 4 or more match and no stage is specific to this journey's trigger or outcome |
| Swap test | Replace the product and industry names with another domain's; reread the pain points | Most pain points remain true, so they say nothing specific |
| Repetition | Count pain points or emotions repeated with near-identical wording across stages | The same phrasing appears in 3 or more stages |
| Unknowns | Count `hypothesis` and `unknown` labels and registered evidence gaps | Zero, in any artifact built on fewer than a few dozen sources |
| Contradictions | Look for recorded disagreement between sources or segments | None recorded |
| Unsourced numbers | List every percentage, count, or duration | Any number without a source and date |
| Quote check | Trace each quote to a session key or transcript | Any quote that cannot be traced; quotes that restate the artifact's own conclusions word for word |
| Vague vocabulary | Search for "seamless", "frictionless", "delightful", "personalized", "omnichannel", "end-to-end experience" | Used without a definition or a measurable meaning |
| Root-cause absence | Check whether any pain point links to a backstage, policy, data, or system cause | No operational cause anywhere |

## Making scores reproducible between auditors

1. **Share the purpose and material first.** Both auditors read the same artifact version, its registers, and its stated decision. Record the version.
2. **Score independently.** No discussion until both scorecards are complete. For each dimension, write the criteria met and missed before writing the number.
3. **Compare.** Differences of 0 need no action. A difference of 1 is resolved by reading the anchors together against the artifact. A difference of 2 or more usually means one auditor used material the other did not, or read the purpose differently; resolve the input first, then rescore.
4. **Resolve on the artifact, not by averaging.** The agreed score is the level whose criteria are all met by the artifact, as checked together. Record the reason in the finding.
5. **Measure agreement on a calibration set.** Agreement on one artifact says little. Before a program of audits, both auditors score the same set of at least 10 artifacts. Report exact agreement, agreement within one level, and weighted kappa (Cohen 1968), which credits near-misses on an ordinal scale. Landis & Koch's labels (for example, 0.61–0.80 "substantial") are conventions, not thresholds with a derivation; agree the target in advance.
6. **Refine anchors where disagreement clusters.** If auditors repeatedly differ on one dimension, the anchor is ambiguous; rewrite the criterion to something observable and rescore the calibration set.

## Failure modes

- Scoring on appearance: a polished map scores high on everything.
- Averaging the eleven scores into one number that hides a blocker.
- Penalizing clearly labeled unknowns as if they were errors.
- Scoring without reading the cited sources, so status inflation goes undetected.
- Accusing an artifact of being machine-generated instead of recording what the tests found.
- Two auditors "agreeing" by splitting the difference.

## Worked mini-audit

Artifact: current-state map of `JRN-CUST-MORTGAGE-SWITCH-001`, "Switch my mortgage to a new deal", version 0.3, prepared for a decision on which stages to redesign next quarter. Seven stages; an emotion curve; 14 pain points; 6 quotes; no registers attached. Two auditors scored independently.

Test results (observed in the artifact): provenance sample 1 of 5 traced; 5 of 7 stage names match the generic lifecycle; 9 of 14 pain points survive the swap test; "frustrating wait times" appears in 4 stages; zero unknowns; "73% of customers feel anxious" has no source; 2 of 6 quotes trace to session notes (`EVD-2025-0741`), 4 do not.

Scores:

| dimension | auditor 1 | auditor 2 | agreed | reason for agreed score |
|---|---:|---:|---:|---|
| A Scope | 2 | 2 | 2 | Actor, trigger, end outcome stated; no registry ID, so not 3 |
| B Actor centricity | 1 | 1 | 1 | Stages actor-worded, content is lender process ("valuation instructed") |
| C Evidence | 1 | 0 | 0 | Stages labeled `observed`; only one source cited; status inflation met the level-0 criterion |
| D Coherence | 2 | 1 | 1 | Stages ordered, but the wait for the new lender's offer is missing, so level 2 not fully met |
| E Variation | 1 | 1 | 1 | Broker versus direct path mentioned in a note only |
| F Experience integrity | 0 | 0 | 0 | Emotion curve and unsourced 73% figure; 4 untraceable quotes |
| G Service linkage | 1 | 1 | 1 | Causes named as blame ("slow underwriters") |
| H Metrics | 0 | 0 | 0 | None |
| I Opportunities | 0 | 1 | 0 | "Build a remortgage app" and "add chatbot" are features; level-0 criterion met |
| J Governance | 1 | 1 | 1 | Version and date; no owner or review cadence |
| K Visual/model integrity | 1 | 0 | 0 | Emotion curve drawn with precise heights and no measurement: level-0 criterion |

Agreement on this artifact: exact 7 of 11, within one level 11 of 11. The four 1-point differences (C, D, I, K) came from scoring on overall impression rather than on the anchors; checking each level's criteria against the artifact together resolved them. (Kappa is not computed on a single artifact.)

Blockers: status inflation (C); fabricated-looking content not traceable to any source (F, K). The map must not be used to choose redesign stages until these are fixed.

Findings (abridged, scorecard format):

| dimension | score_0_3 | finding | evidence_status | evidence_ids | risk | remediation | skill |
|---|---:|---|---|---|---|---|---|
| Evidence | 0 | All stages labeled `observed`; one interview set cited | observed | EVD-2025-0741 | Redesign chosen on stakeholder belief | Relabel to `hypothesis`; run 8–10 interviews with recent switchers | journey-research |
| Experience integrity | 0 | Emotion curve and "73% anxious" have no source; 4 of 6 quotes untraceable | observed | — | Fabricated content reaches executives | Remove unsourced layers until evidenced | customer-journey-mapping |
| Visual/model integrity | 0 | Curve heights imply measurement that does not exist | observed | — | Misreading of intensity | Redraw with evidenced points only, statuses distinguished | customer-journey-mapping |
| Opportunities | 0 | Opportunities are features | observed | — | Solution lock-in | Rewrite as solution-independent opportunities per root cause | experience-opportunity-prioritization |
| Coherence | 1 | Waiting for the new lender's offer is missing | inferred | EVD-2025-0741 | Largest wait unmanaged | Add a waiting stage if interviews confirm | journey-architecture |

Remediation sequence: remove unsourced content and relabel statuses (same week); research to evidence stages; then coherence and opportunities; metrics and governance before the next planning cycle.

## Quality checks

- Every score lists the criteria met and missed; no score without a finding.
- `unknown` and `n/a` are used instead of 0 where material is missing or the dimension does not apply.
- Blockers are listed separately and override scores.
- Generic-content tests are reported as observed findings about content, not claims about authorship.
- Two-auditor scoring was independent, differences were resolved on the artifact, and agreement is reported on a calibration set.

## Sources

- Susan M. Brookhart, *How to Create and Use Rubrics for Formative Assessment and Grading* (2013), ASCD: https://www.ascd.org/books/how-to-create-and-use-rubrics-for-formative-assessment-and-grading
- Anders Jonsson & Gunilla Svingby, "The use of scoring rubrics: Reliability, validity and educational consequences", *Educational Research Review* 2(2), 130–144 (2007): https://doi.org/10.1016/j.edurev.2007.05.002
- Jacob Cohen, "Weighted kappa: Nominal scale agreement with provision for scaled disagreement or partial credit", *Psychological Bulletin* 70(4), 213–220 (1968): https://doi.org/10.1037/h0026256
- J. Richard Landis & Gary G. Koch, "The Measurement of Observer Agreement for Categorical Data", *Biometrics* 33(1), 159–174 (1977): https://doi.org/10.2307/2529310
- Edward R. Tufte, *The Visual Display of Quantitative Information, 2nd Edition* (2001), Graphics Press: https://www.edwardtufte.com/book/the-visual-display-of-quantitative-information/
