# Experiment design

Method for turning an uncertain assumption of a target state into a test whose result can change a decision and can be recorded with an honest `evidence_status`. Use it in workflow steps 9–10 (assumptions into experiments, metric expectations), after `references/target-design-method.md` has produced the assumption map.

Grounding: online controlled experiments and their pitfalls (Kohavi, Tang & Xu 2020); quasi-experimental designs (Shadish, Cook & Campbell 2002; Cunningham 2021 for difference-in-differences; Lopez Bernal, Cummins & Gasparrini 2017 for interrupted time series); cluster and stepped designs (Eldridge & Kerry 2012; Hussey & Hughes 2007); zero-numerator and exact Poisson bounds (Hanley & Lippman-Hand 1983; Garwood 1936); non-inferiority (Piaggio et al. 2012); sequential monitoring (Haybittle 1971; O'Brien & Fleming 1979; Lan & DeMets 1983); pre-registration (Nosek et al. 2018).

## Output

One experiment card per initiative, filled before launch, plus the rows it writes when it reads out:

| Field | Content |
|---|---|
| Initiative | `INI-` ID, the `OPP-` IDs it addresses, the assumption it tests |
| Decision | What will be done if the result is positive, null, or harmful |
| Design | Randomized (individual or cluster), stepped rollout, difference-in-differences, interrupted time series, or before/after; the status it can earn |
| Units | Unit of randomization, unit of analysis, and how the mismatch is handled |
| Primary metric | One `MET-` ID, the minimum detectable effect (MDE), and the arithmetic |
| Guardrails | `MET-` IDs, thresholds or non-inferiority margins, stop rules |
| Timing | Enrollment window, outcome lag, readout dates, interim looks |
| Pre-registered cuts | Segments analyzed, stated before launch |
| Records | Evidence row, metric-edge update, initiative status |

## Step 1 — Start from the decision, not the question

Write: "If the result is X we will do A; if Y, B." If A and B are the same, the experiment has no decision value; do not run it (step 10).

- Name the one assumption under test. An experiment that tests "the new booking flow" tests a bundle and cannot say which part worked.
- Name the metric edge the assumption is about ("`MET-` self-reschedule rate `drives` `MET-` no-show rate"). The experiment updates that edge's status, nothing wider.

## Step 2 — Choose the design and know what it can earn

The ceiling below matches the cause tests of the root-cause method in the service-blueprinting skill and the edge rules of the journey-metrics skill.

| Design | Use when | Main threat | Maximum `evidence_status` for the causal claim |
|---|---|---|---|
| Randomized, individual units | The change is delivered to one actor at a time and one actor's treatment does not change another's outcome | Interference between units; sample-ratio mismatch; peeking | `observed` |
| Randomized, cluster units (sites, teams, regions) | The change is delivered to a group, or individuals in a group would contaminate each other | Few clusters; clustering ignored in analysis | `observed` |
| Staged or stepped rollout, order randomized | Everyone will get the change; operations can only absorb it in waves | Calendar trends confounded with exposure unless modeled | `observed` if the order is randomized and time is in the model |
| Staged rollout, order chosen by the organization | As above, but the keenest sites go first | Early sites differ in more than the change | `inferred` |
| Before/after with comparison group (difference-in-differences) | A change was already made in some units; comparable units did not get it | Non-parallel trends; the comparison group reacts too | `observed` only when it meets the stratified-counterfactual test (comparable groups, same period, stratified on known confounders, pre-period parity checked); otherwise `inferred` |
| Interrupted time series | One population, a clear change date, many stable pre-period points | Another change at the same time; seasonality | `inferred` |
| Pure before/after | Nothing else is possible | Everything that changed at the same time | `inferred` at most; `hypothesis` if the pre-period is a single point |

Decision rules:

- Randomize the unit at which the change is delivered and beyond which its effects stop. If freed capacity, shared staff, or word of mouth passes the effect to controls, move up one level (patient to clinic, agent to team).
- Prefer individual randomization whenever interference is small: it needs far fewer actors (step 4).
- A rollout that is happening anyway can become a stepped design at almost no cost: randomize the order of the waves and record the dates.
- Pure before/after is a monitoring read, not a test. Use it for reversible changes whose decision does not depend on the size of the effect.

## Step 3 — Size the test: minimum detectable effect for proportions

Most journey metrics are proportions (share who attend, share who complete). For two independent groups, two-sided α = 0.05 and 80% power:

- Sample size per arm to detect a change from p₁ to p₂: n = (1.96 + 0.84)² × (p₁(1−p₁) + p₂(1−p₂)) / (p₁ − p₂)², with (1.96 + 0.84)² = 7.84.
- MDE for a given n per arm: MDE ≈ 2.80 × √(2 × p(1−p) / n), using the baseline p in both arms.
- A 95% interval on an observed difference: difference ± 1.96 × √(p₁(1−p₁)/n₁ + p₂(1−p₂)/n₂).

Rules:

- Set the MDE from the decision, not from what is affordable: the smallest effect that would justify the cost and risk of rollout.
- If the achievable MDE is larger than any plausible effect, the test cannot answer the question. Change the design (more units, a more sensitive leading metric, a longer window) or reframe it as a safety pilot whose decision rests on guardrails (step 5).
- Normal approximations hold when each arm expects at least about 10 events and 10 non-events. Below that, use exact methods.
- Lagging outcome metrics usually need many times the sample of the leading metric that drives them. Power the test on the metric the change acts on first; read the outcome as a trend, and keep the outcome edge at the status its own evidence supports.

## Step 4 — Clusters: design effect, unit of randomization vs unit of analysis

When clusters are randomized, observations within a cluster are correlated and carry less information than their count suggests.

- Design effect: DEFF = 1 + (m − 1) × ICC, where m is the average number of analyzed units per cluster and ICC the intracluster correlation of the outcome.
- Required units per arm = individual n × DEFF; clusters per arm = that ÷ m.
- As m grows, clusters per arm approach n × ICC. Adding volume per cluster cannot rescue a design with too few clusters.
- Estimate ICC from pre-period data (between-cluster variance of the outcome relative to total variance). If unavailable, plan with a range and show the MDE at each end.
- With fewer than about 15 clusters per arm, use t-based multipliers with degrees of freedom near the number of clusters minus 2, and consider matching or stratifying clusters before randomizing.

Unit of analysis must respect the unit of randomization. Analyze at the cluster level (cluster means) or with a model that accounts for clustering; a naive per-actor test on cluster-randomized data overstates certainty by about √DEFF. The same holds on a smaller scale when one randomized actor contributes several events (several appointments, several invoices): define one event per actor, or account for the repeat.

## Step 5 — Rare-event guardrails: bounding harm

A guardrail that protects against a rare, serious event (safety, fraud, legal breach) cannot be tested like a conversion rate.

- **Zero events is not zero risk.** With 0 events in n units, the one-sided 95% upper bound on the rate is about 3/n (the rule of three). 0 in 1,000 is consistent with a true rate up to 3 per 1,000.
- **Few events: exact Poisson bounds.** One-sided 95% upper bounds on the expected count for 0, 1, 2, 3 observed events are 3.00, 4.74, 6.30, 7.75. Divide by n for a rate.
- **State a non-inferiority margin before launch.** "The new process is acceptable if the rate is no more than M above baseline." The guardrail passes only when the upper bound of the interval for (new − baseline) is below M. A null result on a superiority test is not a pass.
- **Size the pilot to the margin.** To bound a rate below R with 0 events you need n ≥ 3 / R; if you expect k events, n ≥ (Poisson upper bound for k) / R.
- **Absence of evidence trap.** "No significant increase in harm" from an underpowered pilot is not evidence of safety (Altman & Bland 1995). Report the upper bound and whether it clears the margin.
- **When the pilot cannot be large enough, remove the harm path by design.** Make the harmful action impossible (a hard rule, a decision right withheld), then test the mechanism: trace every case where the rule should have fired. That earns `observed` for the mechanism, not for the rate.

## Step 6 — Timing, seasonality, novelty

- Run at least two full cycles of the natural rhythm (two weeks for weekday effects; a full billing or booking cycle) and avoid holiday weeks unless both arms cover them equally. Randomized concurrent controls neutralize seasonality; before/after and interrupted time series do not.
- Outcome lag: a cohort is readable only after its window closes. The readout date = end of enrollment + outcome window + data latency.
- Novelty and primacy: returning actors may use a new feature out of curiosity, or avoid it out of habit. Plot the effect by week since first exposure; if it decays or grows, read the stable tail, or restrict to first-time actors.
- For interrupted time series, use enough points before and after the change to model trend and season (a full seasonal cycle before the change when the metric is seasonal; a handful of points cannot separate trend from noise), and name any concurrent change.

## Step 7 — Sequential monitoring and stop rules

Looking at a running test and stopping when it crosses p < 0.05 inflates false positives: repeated looks at 1.96 standard errors can double or triple the error rate (Haybittle 1971).

- **Fast signals** (guardrail breaches, rule violations, operational failures) are watched continuously. They stop or pause the test; they never declare success.
- **Confirmatory reads** of the primary metric happen at pre-set information fractions only (for example 50% and 100% of planned sample).
- Simple conservative rule (Haybittle–Peto): stop early for benefit only if |z| > 3.29 (p < 0.001); final analysis at the usual 1.96.
- O'Brien–Fleming boundaries for two equally spaced looks at overall two-sided α = 0.05: about 2.80 at the interim and 1.98 at the final. Alpha spending (Lan & DeMets) allows unequal or unplanned look timing by deciding in advance how much of α is spent by each fraction of information.
- Stopping for futility is allowed at any look, and costs no α: if the interval already excludes the MDE, stop.
- Never extend a test because it is "almost significant" unless the extension rule was pre-registered.

## Step 8 — Pre-register

Before the first unit is assigned, write and date:

1. the assumption and the decision table from step 1;
2. design, units, randomization method, and exclusions;
3. primary metric with its card, MDE, and sample; secondary metrics labeled as such;
4. guardrails with thresholds or margins, and stop rules;
5. segments to be cut (at most a few, each with a reason), and the rule that other cuts are exploratory;
6. interim looks and boundaries;
7. the analysis: estimator, interval, handling of clustering and repeat events.

Anything decided after seeing data is labeled exploratory; it supports `hypothesis` for a new test, not a status change (Nosek et al. 2018).

## Step 9 — Validity checks at readout

- **Sample-ratio mismatch.** Compare assigned counts with the planned split (a chi-square test). A mismatch means assignment or logging is broken; do not interpret the metric.
- **Pre-period balance.** Arms had similar values before exposure.
- **Exposure.** Share of the treatment arm that actually received the change; analyze as assigned (intention to treat).
- **Interference check.** Did control units receive any part of the change?
- **Instrumentation.** The metric's card still describes how it was computed.

## Step 10 — When not to run an experiment

Skip it, and say so in the initiative row, when:

- the decision is the same whatever the result;
- the change is cheap, reversible, and has no plausible harm path: ship it with a guardrail and a before/after monitoring read (`inferred` at most);
- the achievable MDE is far above any plausible effect and no guardrail question needs answering;
- the harm of withholding the change from a control group is unacceptable (a safety fix): ship it, and learn from a stepped rollout or interrupted time series instead;
- the test would take longer than the window in which the decision matters.

## Step 11 — Record the result

| Register | What is written |
|---|---|
| Evidence | One row, `source_type` `experiment` (or `analytics` for quasi-experiments), with design, n, estimate, interval, and limitations; its `evidence_status` is the ceiling from step 2, lowered if a validity check failed |
| Metric edge | The tested edge cites the new evidence ID; its `evidence_status` becomes the design's ceiling if the effect was detected, and stays or is noted as "no effect detected; MDE X" if not. A null result never upgrades an edge to "no effect" |
| Initiative | `expected_effect` holds the pre-registered MDE and expected movement before launch; `status` moves to `done` (adopted) or `rejected`; `hypothesis` is not rewritten after the fact |
| Metric | A new baseline, if the test produced one, goes in `baseline` with its period and n |

Scope the claim to what was randomized: population, period, and variant.

## Worked example

Fictional scenario shared with the target-design method. Journey `JRN-CUST-CLINIC-BOOK-001`, "Get a specialist appointment and attend it", in a network of 24 outpatient clinics with about 2,800 eligible specialist appointments a month. Opportunity `OPP-0851`: patients who cannot attend cannot release or move their slot outside phone-line hours, and do not come (root cause `observed`). Initiative `INI-0851`: the appointment reminder carries a self-reschedule link, and an assistant answers replies within decision rights set by the target design.

Metrics: `MET-0851` actor outcome, seen by the specialist within 21 days of referral (baseline 58%); `MET-0852` no-show rate per booked appointment (baseline 12%, `EVD-2025-0851`); `MET-0853` share of reminded patients who reschedule themselves (not yet measured); `MET-0855` guardrail, urgent-flagged appointments moved beyond their clinical window per 1,000 bookings (baseline 0.8); `MET-0856` guardrail, no-show rate for patients aged 75 and over.

**Decision table.** Adopt network-wide if no-show falls by at least 3 points with guardrails passing; if not, keep the phone path only and redirect effort to `OPP-0853` (slot refill).

**Design.** The link is delivered per patient, and a patient's own attendance does not depend on another's link. Individual randomization, 1:1, stratified by clinic. One appointment per patient (the first in the window) to avoid repeat events. Ceiling: `observed`.

**Size.** For 12% → 9%: n = 7.84 × (0.12 × 0.88 + 0.09 × 0.91) / 0.03² = 7.84 × 0.1875 / 0.0009 = **1,634 per arm**, about 3,270 patients, or five to six weeks of intake. Enrollment is set at six weeks (covering weekday cycles, no holidays), with a readout three weeks after enrollment closes because bookings are made up to 21 days ahead.

**Why not randomize clinics.** With 12 clinics per arm, about 200 analyzed appointments each, and an ICC of 0.01 estimated from last year's clinic-level no-show rates: DEFF = 1 + 199 × 0.01 = 2.99; effective n per arm = 12 × 200 / 2.99 = 803; MDE = 2.80 × √(2 × 0.12 × 0.88 / 803) = **4.5 points** (4.8 with a t-multiplier on 22 degrees of freedom). The target effect is 3 points. Even unlimited appointments per clinic would need about 1,634 × 0.01 = 16 clinics per arm. Clinic randomization is kept only for the slot-refill process of `OPP-0853`, which changes shared clinic work.

**Why not the earlier pilot.** A clinic ran the link in December: no-show 14% → 10%. Comparison clinics moved 13.5% → 11% over the same months. Difference-in-differences: (10 − 14) − (11 − 13.5) = −4 − (−2.5) = **−1.5 points**. Most of the drop was seasonal, the pilot clinic volunteered, and pre-period trends were not checked. Recorded as `EVD-2025-0855`, `inferred`; it motivated the test but cannot settle it.

**Rare-event guardrail.** Baseline 0.8 urgent-window breaches per 1,000 bookings. Non-inferiority margin: +0.5 per 1,000, so the upper bound must stay below 1.3 per 1,000. With zero breaches in 1,634 treated bookings the upper bound is 3 / 1,634 = 1.84 per 1,000: the test cannot clear the margin. Clearing it with 0 events needs 3 / 0.0013 = 2,308 bookings; with the 2 events expected at baseline, 6.30 / 0.0013 = 4,843. So the harm path was removed by design instead: the assistant has no right to move an urgent-flagged appointment and must hand the patient to a nurse. The pilot traces every urgent-flagged reply (fast signal; one breach pauses the test).

**Other guardrail.** `MET-0856`, patients 75+: non-inferiority margin +2 points on no-show.

**Monitoring.** One interim at 50% of sample, O'Brien–Fleming boundary |z| > 2.80; final at 1.98.

**Results** (fictional).

| Read | Control | Treatment | Difference | Interval / statistic |
|---|---|---|---|---|
| Interim, no-show | 103 / 845 = 12.2% | 80 / 850 = 9.4% | −2.8 points | z = −1.84; boundary 2.80 not crossed, continue |
| Final, no-show | 204 / 1,688 = 12.1% | 157 / 1,702 = 9.2% | −2.9 points | SE 0.0106; 95% interval −4.9 to −0.8; z = −2.70 |
| Sample ratio | 1,688 | 1,702 | — | consistent with 1:1 |
| 75+ no-show | 46 / 352 = 13.1% | 44 / 360 = 12.2% | −0.8 points | 95% interval −5.7 to +4.0 |
| Urgent-flagged replies | — | 61 | 61 handed to a nurse, 0 moved by the assistant | mechanism trace |

Reading:

- The primary effect is detected and the interval excludes zero. It is about the size planned for; the lower end (−0.8) is below the 3-point threshold, so the size is uncertain.
- The 75+ guardrail does not clear its margin: the upper bound +4.0 exceeds +2. That is not evidence of harm; it is absence of evidence of safety. Decision: adopt, keep the phone path for patients 75+, and continue the non-inferiority read in the rollout.
- The urgent-window guardrail passes as a mechanism (61 of 61), not as a rate.
- `MET-0851` was not powered: detecting 58% → 60% needs 7.84 × (0.58 × 0.42 + 0.60 × 0.40) / 0.02² ≈ 9,480 per arm. It is read as a trend over the rollout.

Records:

| Register | Row |
|---|---|
| Evidence | `EVD-2025-0854`, `experiment`: individual randomized test, 6 weeks, n = 3,390; no-show −2.9 points (95% CI −4.9 to −0.8); 75+ inconclusive; limitation: first appointment per patient only; `observed` |
| Evidence | `EVD-2025-0856`, `operational-record`: 61 of 61 urgent-flagged replies handed to a nurse; `observed` |
| Metric edge | `MET-0853` `drives` `MET-0852`: `EVD-2025-0854`, `observed`, note "randomized; effect −2.9 points (−4.9 to −0.8); 75+ not established" |
| Metric edge | `MET-0852` `drives` `MET-0851`: unchanged, `inferred` |
| Metric edge | `MET-0855` `protects` `MET-0852`: cites `EVD-2025-0856`, `observed` for the handoff mechanism; rate not bounded below margin |
| Initiative | `INI-0851`: `status` `done`; `expected_effect` kept as pre-registered ("no-show −3 points, MDE 3 at 1,634 per arm") |

## Failure modes

- Declaring success at the first look that crosses p < 0.05.
- Randomizing clinics or teams and analyzing actors as if independent.
- Reporting "no significant harm" from a pilot that could not have detected harm.
- Upgrading an edge to `observed` from a before/after read or a volunteer pilot.
- Testing a bundle of changes and crediting one of them.
- Choosing segments after seeing the data and reporting the best one.
- Powering the test on the lagging outcome and giving up, or on a leading metric and claiming the outcome.

## Quality checks

- The decision table exists and its branches differ.
- Design, ceiling status, and units are stated; clustering is handled in the analysis.
- MDE arithmetic is shown and compared with the smallest effect worth acting on.
- Every guardrail has a threshold or margin; rare-event guardrails show the bound the sample can reach.
- Interim looks and boundaries are pre-registered; fast signals can only stop.
- Results are recorded in evidence, metric-edge, and initiative rows with status no higher than the design allows.

## Sources

- Ron Kohavi, Diane Tang, Ya Xu, *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing*, Cambridge University Press, 2020: https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59
- William R. Shadish, Thomas D. Cook, Donald T. Campbell, *Experimental and Quasi-Experimental Designs for Generalized Causal Inference*, Houghton Mifflin, 2002, ISBN 0-395-61556-9: https://books.google.com/books/about/Experimental_and_Quasi_experimental_Desi.html?id=o7jaAAAAMAAJ
- Scott Cunningham, *Causal Inference: The Mixtape*, Yale University Press, 2021 (difference-in-differences chapter; free online edition): https://mixtape.scunning.com/
- James Lopez Bernal, Steven Cummins, Antonio Gasparrini, "Interrupted time series regression for the evaluation of public health interventions: a tutorial", *International Journal of Epidemiology* 46(1), 348–355, 2017 (see also the 2021 corrigendum): https://doi.org/10.1093/ije/dyw098
- Sandra Eldridge, Sally Kerry, *A Practical Guide to Cluster Randomised Trials in Health Services Research*, Wiley, 2012: https://www.wiley.com/en-us/A+Practical+Guide+to+Cluster+Randomised+Trials+in+Health+Services+Research-p-9781119966722
- Michael A. Hussey, James P. Hughes, "Design and analysis of stepped wedge cluster randomized trials", *Contemporary Clinical Trials* 28(2), 182–191, 2007: https://doi.org/10.1016/j.cct.2006.05.007
- James A. Hanley, Abby Lippman-Hand, "If nothing goes wrong, is everything all right? Interpreting zero numerators", *JAMA* 249(13), 1743–1745, 1983: https://pubmed.ncbi.nlm.nih.gov/6827763/
- F. Garwood, "Fiducial limits for the Poisson distribution", *Biometrika* 28(3–4), 437–442, 1936: https://doi.org/10.1093/biomet/28.3-4.437
- Douglas G. Altman, J. Martin Bland, "Absence of evidence is not evidence of absence", *BMJ* 311, 485, 1995: https://doi.org/10.1136/bmj.311.7003.485
- Gilda Piaggio, Diana R. Elbourne, Stuart J. Pocock, Stephen J. W. Evans, Douglas G. Altman, "Reporting of noninferiority and equivalence randomized trials: extension of the CONSORT 2010 statement", *JAMA* 308(24), 2594–2604, 2012: https://doi.org/10.1001/jama.2012.87802
- J. L. Haybittle, "Repeated assessment of results in clinical trials of cancer treatment", *British Journal of Radiology* 44(526), 793–797, 1971: https://doi.org/10.1259/0007-1285-44-526-793
- Peter C. O'Brien, Thomas R. Fleming, "A multiple testing procedure for clinical trials", *Biometrics* 35(3), 549–556, 1979: https://doi.org/10.2307/2530245
- K. K. Gordon Lan, David L. DeMets, "Discrete sequential boundaries for clinical trials", *Biometrika* 70(3), 659–663, 1983: https://doi.org/10.1093/biomet/70.3.659
- Brian A. Nosek, Charles R. Ebersole, Alexander C. DeHaven, David T. Mellor, "The preregistration revolution", *PNAS* 115(11), 2600–2606, 2018: https://doi.org/10.1073/pnas.1708274114
