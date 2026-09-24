# Moment analysis

Method for showing that a moment is disproportionate: that how it goes changes the actor's outcome, or the organization's, far more than an ordinary node does. Use it in workflow steps 1–6 (candidates, outcome at stake, evidence, type, counterfactual, ranking). The result fills `assets/moment-register.csv`, plus a list of rejected candidates.

Pain, emotion, volume, and seniority of the person asking are reasons to look at a node, not reasons to select it. A moment is selected on the size of the consequence attached to it, and each part of that claim carries its own `evidence_status`.

Grounding: the critical incident technique (Flanagan 1954) and its service application (Bitner, Booms & Tetreault 1990); outcome-conditioned comparison and stratification from standard epidemiological practice; relative-importance analysis and its limits (Johnson & LeBreton 2004; Grömping 2006); the peak-end rule (Kahneman et al. 1993; Redelmeier & Kahneman 1996; Alaybek et al. 2022) and the service recovery paradox (de Matos, Henrique & Rossi 2007), both used with the cautions below.

## Output

1. A candidate log: every node proposed, its source, and the outcome it might affect.
2. For each candidate, a claim table:

| claim | test applied | result | evidence_ids | evidence_status |
|---|---|---|---|---|

3. Moment register rows for the selected moments.
4. Rejected candidates, each with the reason and where it was routed (usability backlog, research question, monitor).

## Step 1 — Generate candidates from more than one source

Collect candidates from at least three of these sources. A candidate list from a single source reproduces that source's bias.

| Source | What it surfaces | Bias to correct for |
|---|---|---|
| Outcome data (cohorts, funnels) | Nodes after which outcomes diverge | Only what is instrumented |
| Critical incidents (Step 4) | Moments actors remember as decisive | Recall favors vivid and recent events |
| Complaints and support logs | Nodes that generate contact | Only actors who complain; volume ≠ consequence |
| Service blueprint failure points | Backstage failures that surface later | Internal view of where things break |
| Journey map emotion curve | Low and high points | Emotion ≠ consequence |
| Stakeholder nominations | Nodes leaders believe matter | Status is `hypothesis` until tested |

Rules:

- Name each candidate by its node ID. A candidate that is not a node yet ("the whole mortgage process") is too broad; split it into the node where the outcome diverges.
- Record who nominated it and from which source. A stakeholder nomination stays in the log even if rejected, so the rejection is visible.
- Include at least one candidate that nobody has complained about: waiting nodes, handoffs, and irreversible commitments are often silent.

## Step 2 — Name the outcome at stake

A moment matters because of an outcome. For each candidate write:

`If [node] goes badly, [actor outcome] is less likely / later / worse, and [organizational outcome] follows.`

- Use the journey's actor-outcome metric where one exists. If the outcome is not measured, say so; the claim can still proceed as `inferred` or `hypothesis`.
- The outcome must be later than the node. "Customers are frustrated at this step" is the moment's own quality, not an outcome.
- One primary outcome per moment. Secondary outcomes go in `failure_consequence`.

## Step 3 — Outcome-conditioned comparison

This is the test that can earn `observed` for a disproportion claim.

1. **Define "goes well" and "goes badly" at the node operationally**, from records, before looking at outcomes: "two or more document requests after submission" versus "zero or one". Do not choose the cut point after seeing which one gives the largest gap; if several cuts are tried, report all.
2. **Build a cohort** of actors who reached the node in a fixed window, and follow them to the outcome. Actors who left before the node are outside this comparison; report their number.
3. **Compute the outcome rate in both groups**, the difference, and the ratio, with group sizes. With small groups, report an interval, not only the point value.
4. **Stratify.** List the variables that could cause both a bad moment and a bad outcome (segment, channel, product, case complexity, prior history). Compare within each stratum. If the gap shrinks sharply within strata, the moment is partly a marker of a harder case, not a cause.
5. **Check direction.** Could the bad outcome already be under way before the node? An actor who has decided to leave behaves differently at every later node. Use timing: did the moment precede the change in behavior?
6. **Check dose.** Does the outcome worsen as the moment worsens (one request, two, three)? A graded relationship strengthens the claim.
7. **Size the consequence at population level:**

`excess failures per 1,000 entrants = share who have the bad moment × (outcome rate when good − outcome rate when bad) × 1,000`

This combines reach and effect. A node with a large effect on 1% of actors and a node with a small effect on 60% can be compared in the same unit.

Decision rules:

- A stratified gap that persists, precedes the outcome, and is large relative to other nodes supports `observed` for "outcome differs when this moment goes badly". The causal reading ("fixing it would move the outcome") stays `inferred` until an intervention or natural experiment tests it.
- Gap disappears within strata: reject as a cause; the node may still be a useful early warning signal, recorded as a metric, not a moment.
- No outcome data linkable at actor level: the disproportion claim is `inferred` at best, built from Steps 4–7, and a linkage gap is registered as evidence with status `unknown`.
- "Large relative to other nodes" is a comparison, not a threshold. Run the same comparison for two or three ordinary nodes as a reference.

## Step 4 — Critical incident technique

Flanagan's technique collects specific, remembered events in which behavior led to a clearly good or clearly bad result. Bitner, Booms and Tetreault applied it to service encounters and showed that recovery from failure, response to special requests, and unprompted employee actions account for much of what customers remember.

Procedure:

1. State the aim: "events during [journey] that made you more or less likely to [outcome]".
2. Ask for a specific incident, not a general opinion: "Think of a time when… What happened, step by step? What did you do next? What would have happened otherwise?"
3. Collect both favorable and unfavorable incidents from the same people.
4. Keep only incidents with a clear sequence, a specific node, and a stated consequence. Discard generalizations.
5. Classify incidents by node, then by what happened; count incidents per node and per consequence.

What it can show: which nodes actors connect to their own decisions, in their words, including nodes the organization does not instrument. What it cannot show: prevalence or effect size. Incident counts describe the sample, not the population; do not report them as percentages of actors.

Status rules: "actors report that this moment changed their decision" is `observed` for the report. "This moment disproportionately affects the outcome" from incidents alone is `inferred`.

## Step 5 — Key-driver analysis and its pitfalls

Key-driver analysis regresses an overall rating (satisfaction, likelihood to recommend) on ratings of individual touchpoints and calls the largest coefficients or correlations "drivers". It is quick and often misread.

| Pitfall | What goes wrong | What to do |
|---|---|---|
| Collinearity | Touchpoint ratings correlate with each other (halo effect), so coefficients are unstable and their ranking can flip between samples | Use relative-importance methods that decompose explained variance (dominance analysis, Shapley/LMG, relative weights); report the ranking's stability across resamples |
| Importance from correlation | "Correlates most with satisfaction" becomes "matters most"; the direction can be reversed (satisfied people rate everything higher) | Treat the output as a list of candidates for Step 3, never as a moment selection |
| Survey-only drivers | Both sides of the equation are survey answers from the same person at the same time, so shared mood inflates every link | Replace the dependent variable with a behavioral or record-based outcome where possible |
| Survivorship | Surveys reach actors who got far enough to be surveyed; those who left at the moment in question are missing | Report who was sampled and compare with who entered the journey |
| Omitted nodes | The model can only rank what was asked about | Check the candidate log for nodes not in the questionnaire |
| Stated importance | Asking people what matters produces socially expected answers (price, speed) | Use stated importance as a hypothesis, not as a weight |

Status rule: a moment supported only by key-driver output is `hypothesis`, or `inferred` when the relative-importance analysis is stable and the reasoning is written down. It is never `observed`.

## Step 6 — Peak-end and recovery, used cautiously

Retrospective evaluations of an experience are influenced by its most intense point and its end (Kahneman et al. 1993; Redelmeier & Kahneman 1996). A 2022 meta-analysis found the peak-end effect large across many contexts, but also found the average of the whole experience predicted evaluations about as well. Recovery research reports a small positive effect of good recovery on satisfaction, and no reliable effect on repurchase or word of mouth (de Matos, Henrique & Rossi 2007).

Use these findings to generate candidates, not to select them:

- The end of a journey and its most intense node are worth testing in Step 3.
- Peak-end concerns remembered evaluation. It does not show that the peak or end changes behavior, and it does not justify neglecting duration or the average experience.
- Do not plan to create failures to recover from. A recovery moment is selected when failure is already common and recovery quality changes the outcome in Step 3.

## Step 7 — Structural tests: decision, irreversibility, vulnerability

Some moments are disproportionate by structure, even before outcome data exists. Each test asks for a record, not an opinion.

| Test | Question | Evidence that can make it `observed` |
|---|---|---|
| Decision or commitment point | Does the actor choose here to continue, switch, or leave, or commit money, time, or data? | Process records showing the choice; withdrawal or switching timestamps clustered at the node |
| Irreversibility | After this node, can a bad result be undone? At what cost? | Policy, contract, or system rules showing what cannot be reversed |
| Vulnerability | Is the actor unusually exposed here: financial strain, health, bereavement, first-time, low literacy, time pressure? | Segment records; research showing the state at this node |
| Trust formation | Is this the first time the actor relies on a promise with something at stake? | Observed behavior change after the node (checking, parallel running, calling) |
| Dependency | Do later nodes, or other journeys, depend on this node's output? | Relation register rows (`depends_on`) and blueprint links |

Decision rules:

- A node that passes the irreversibility or vulnerability test with a record is a candidate for `high-risk` even when volume is small. Its disproportion claim is `inferred` until an outcome comparison exists; say so in `why_disproportionate`.
- A decision point is not a moment by itself. It becomes one when the choice made there differs with the moment's quality (Step 3), or when the choice is irreversible.

## Step 8 — Assign evidence status per claim

Split each candidate into claims and give each its own status. The moment row's `evidence_status` is the status of the disproportion claim, and it can be no stronger than the weakest claim it rests on.

| Claim | `observed` requires | Typical when evidence is weaker |
|---|---|---|
| The node exists and actors pass it | Node row with observed evidence | — |
| The moment goes badly for a share of actors | Records or measurement at the node | `inferred` from interviews |
| The outcome differs when it goes badly | Stratified outcome-linked comparison (Step 3) | `inferred` from critical incidents or structure |
| Improving it would move the outcome | Experiment, staged rollout, or natural experiment | `inferred` from the comparison plus mechanism |
| A stakeholder believes it matters | — | `hypothesis`, always |

`stakeholder-input` evidence supports `hypothesis` at most. A moment whose only support is stakeholder belief stays a candidate.

## Step 9 — Decide how many to select

Select few enough that each can have an owner, a metric, and design attention.

- For one L2 journey, three to five moments is typical; more than seven usually means ordinary pain points were admitted.
- Each selected moment must have an owner who accepts it and at least one metric that can show whether it is going well. If no one can own it, record that as a finding.
- Rank by consequence at population level (Step 3) and by structural severity (Step 7), with evidence status shown beside the rank. A weaker-evidence moment may rank high; the rank and the evidence are reported side by side, not blended.
- Before closing, check the selection against the types: a set containing only `trust` moments often means decision and high-risk points were missed.

## Step 10 — Write the rows

- `node_id`: the lowest node where the moment's quality is decided.
- `outcome_at_stake`: the actor outcome from Step 2.
- `why_disproportionate`: one sentence with the comparison and its size, or the structural test passed, with strata named.
- `evidence_ids`: the evidence behind the disproportion claim, not every related finding.
- `metric_ids`: the metric that shows the moment's quality and, where it exists, the outcome metric.
- `failure_consequence`: what happens to the actor and to the organization, including secondary outcomes.

## Failure modes

- Selecting the loudest node: complaint volume used as consequence.
- Cutting after looking: the "bad" threshold chosen because it gives the largest gap.
- Marker mistaken for cause: the gap disappears within segments.
- Key-driver output copied into the register as moments.
- Peak-end cited to justify a design without testing that the moment changes behavior.
- Moments named after touchpoints or channels ("the call") rather than what is decided there.
- Every stage listed as a moment.

## Worked example

Journey `JRN-CUST-MORTGAGE-001`, "Get a mortgage and complete a home purchase". Stages: 01 Find out what I can borrow; 02 Apply and prove my income; 03 Wait for a decision; 04 Get the offer and secure the rate; 05 Complete the purchase. Outcome metric `MET-0701`: applications completed on or before the agreed completion date ÷ applications submitted, quarterly cohort; baseline 71%.

Candidate comparisons (applications submitted Q1–Q2, n = 4,580):

| candidate node | "bad" defined as | share bad | on-time completion good vs bad | within strata (employed / self-employed) | excess failures per 1,000 |
|---|---|---|---|---|---|
| `NOD-CUST-MORTGAGE-001-02` document requests after submission | ≥2 further requests | 24% | 78% vs 49% | 81% vs 59% / 58% vs 33% | ~55 (0.24 × ~23 pts × 1,000) |
| `NOD-CUST-MORTGAGE-001-03-02` property valuation | valuation below agreed price | 6% | 74% vs 31% | 75% vs 33% / 70% vs 27% | ~26 |
| `NOD-CUST-MORTGAGE-001-02-01` document upload screen | ≥1 failed upload | 41% | 72% vs 70% | gap ≤2 pts in both | ≤8 |

Self-employed applicants are 38% of the "≥2 requests" group and 12% of the other group, so part of the raw 29-point gap is case mix. The strata reproduce the totals (0.88 × 81% + 0.12 × 58% ≈ 78%; 0.62 × 59% + 0.38 × 33% ≈ 49%), and a gap of 22 points (employed) and 25 points (self-employed) remains; weighted by the bad group's mix it is about 23 points, and in 88% of withdrawn cases the second request came before the withdrawal date.

Other evidence:

- Critical incidents from 40 withdrawn applicants: 14 incidents named "the amount changed" between the initial estimate and the decision; 11 named repeated document requests.
- Key-driver analysis of completer satisfaction ranked "underwriter communication" first; it correlates 0.78 with "speed of decision", and only completers were surveyed. Recorded as a hypothesis for stage 03.
- Offer terms: an offer expires 6 months after issue; after expiry the fixed rate cannot be restored. 3% of offers expired before completion in the last year.
- The sales director nominated the post-completion welcome call. Second-product uptake: 12% with the call, 11% without, matched on product and channel.

Claim table for the first candidate:

| claim | test applied | result | evidence_ids | evidence_status |
|---|---|---|---|---|
| Applicants receive ≥2 requests after submission | case records | 24% of submitted | EVD-2025-0701 | observed |
| On-time completion lower when ≥2 requests | stratified cohort comparison, timing | 22–25 pt gap in both strata | EVD-2025-0702 | observed |
| Fewer requests would raise completion | mechanism: withdrawal reasons cite requests; no intervention yet | — | EVD-2025-0703 | inferred |

Selected moments:

| moment_id | node_id | moment_type | outcome_at_stake | why_disproportionate | evidence_ids | evidence_status | metric_ids | failure_consequence | owner |
|---|---|---|---|---|---|---|---|---|---|
| MTM-0701 | NOD-CUST-MORTGAGE-001-02 | trust | Completion on the agreed date | On-time completion 22–25 pts lower after ≥2 post-submission requests, within both income strata; ~55 excess failures per 1,000 applications | EVD-2025-0701;EVD-2025-0702 | observed | MET-0702;MET-0701 | Applicant withdraws or moves to another lender; purchase chain delayed | Head of mortgage operations |
| MTM-0702 | NOD-CUST-MORTGAGE-001-03-02 | decision | Purchase goes ahead at an affordable price | Below-price valuation cuts on-time completion from 74% to 31%; applicant must renegotiate, add deposit, or withdraw | EVD-2025-0704 | observed | MET-0703;MET-0701 | Purchase collapses; applicant loses fees already paid | Valuation panel manager |
| MTM-0703 | NOD-CUST-MORTGAGE-001-04 | high-risk | Borrowing at the offered rate | Offer expiry is irreversible: the fixed rate cannot be restored; 3% of offers expire before completion; outcome-linked cost not yet measured | EVD-2025-0705 | inferred | MET-0704 | Higher rate for the whole fixed term; complaint and redress exposure | Offer and completions lead |
| MTM-0704 | NOD-CUST-MORTGAGE-001-01 | trust | Applicant's confidence to proceed | Named in 14 of 40 withdrawal incidents; no outcome comparison of estimate gap yet | EVD-2025-0706 | inferred | MET-0705 | Withdrawal after decision; complaints about the estimate | Digital sales lead |

Rejected candidates:

- Document upload screen: high volume of failed uploads, no outcome difference within strata. Routed to the usability backlog as a stage 02 friction item.
- Post-completion welcome call: stakeholder nomination; matched comparison shows no difference in second-product uptake. Recorded with evidence `EVD-2025-0707`; not selected.
- "Underwriter communication": key-driver output only, collinear with speed, completers only. Registered as a research question for stage 03 with status `hypothesis`.

## Quality checks

- Candidates come from at least three sources, including one non-complaint source.
- Every selected moment names an outcome later than the node.
- Each disproportion claim is backed by a stratified outcome comparison, or labeled `inferred`/`hypothesis` with the missing test named.
- "Bad" thresholds were set before looking at outcomes.
- Critical incident counts are not reported as population percentages.
- Key-driver and peak-end findings appear only as candidates or hypotheses.
- Each selected moment has an owner and a metric; rejected candidates are listed with reasons.

## Sources

- John C. Flanagan, "The critical incident technique", *Psychological Bulletin* 51(4), 327–358 (1954): https://doi.org/10.1037/h0061470
- Mary Jo Bitner, Bernard H. Booms, Mary Stanfield Tetreault, "The Service Encounter: Diagnosing Favorable and Unfavorable Incidents", *Journal of Marketing* 54(1), 71–84 (1990): https://doi.org/10.1177/002224299005400105
- Jeff W. Johnson & James M. LeBreton, "History and Use of Relative Importance Indices in Organizational Research", *Organizational Research Methods* 7(3), 238–257 (2004): https://doi.org/10.1177/1094428104266510
- Ulrike Grömping, "Relative Importance for Linear Regression in R: The Package relaimpo", *Journal of Statistical Software* 17(1) (2006): https://doi.org/10.18637/jss.v017.i01
- Jeff Sauro, MeasuringU, "10 Things to Know about a Key Driver Analysis" (2016): https://measuringu.com/key-drivers/
- Daniel Kahneman, Barbara L. Fredrickson, Charles A. Schreiber, Donald A. Redelmeier, "When More Pain Is Preferred to Less: Adding a Better End", *Psychological Science* 4(6), 401–405 (1993): https://doi.org/10.1111/j.1467-9280.1993.tb00589.x
- Donald A. Redelmeier & Daniel Kahneman, "Patients' memories of painful medical treatments: real-time and retrospective evaluations of two minimally invasive procedures", *Pain* 66(1), 3–8 (1996): https://doi.org/10.1016/0304-3959(96)02994-6
- Balca Alaybek et al., "All's well that ends (and peaks) well? A meta-analysis of the peak-end rule and duration neglect", *Organizational Behavior and Human Decision Processes* 170 (2022): https://doi.org/10.1016/j.obhdp.2022.104149
- Celso Augusto de Matos, Jorge Luiz Henrique, Carlos Alberto Vargas Rossi, "Service Recovery Paradox: A Meta-Analysis", *Journal of Service Research* 10(1), 60–77 (2007): https://doi.org/10.1177/1094670507303012
