# Target design method

Method for moving from prioritized opportunities to a target experience that guides decisions, can be built, can be rolled out, and can be tested. Use it in workflow steps 1–9; step 9 hands off to `references/experiment-design.md`.

The target state is a designed claim, not a finding. Everything it says about how actors will respond is `hypothesis` until tested; everything it says about the current state keeps the status it had in research.

Grounding: service promises (Bitner 1995); service recovery (Hart, Heskett & Sasser 1990); human–AI interaction guidelines (Amershi et al. 2019) and AI risk management (NIST AI RMF 1.0, 2023); assumption mapping (Bland & Osterwalder 2019).

## Inputs and output

Inputs: opportunity rows with `decision` `act-now`, `investigate`, or `sequence` (from the experience-opportunity-prioritization skill); moments that matter; the current journey and its metric tree; root-cause tables from service blueprinting.

Output: principles with the trade-off each resolves; target outcomes per metric layer with guardrails; a scenario set; service promises and recovery design; service implications by layer; a capability-gap table; transitional journeys with their rollout map; an assumption map; initiative rows.

## Step 1 — Anchor on opportunities, not features

List the opportunities in scope with their `OPP-` IDs, root cause, and `root_cause_status`. For each, write the actor outcome it serves. A target element that traces to no opportunity and no named strategic hypothesis is out of scope; record it as a parking-lot idea, not as part of the target.

- `investigate` opportunities enter the target as options with an explicit open question, not as settled design.
- `sequence` opportunities enter a later transitional state, after their dependency.

## Step 2 — Write decision-guiding principles

A principle is a rule that tells a designer which way to go when two good things conflict. Write 3–6.

Template: `[Actor] [always / never] [observable condition], even when [the thing it wins against].`

The trade-off test: for each principle, name one real decision in this journey where two options are both reasonable and the principle picks one. If you cannot name the decision, or the principle picks both, rewrite or drop it.

| Weak | Why it fails | Decision-guiding |
|---|---|---|
| "Seamless experience" | No option is ever "seamed"; resolves nothing | "A patient can change an appointment when they discover the conflict, even outside staff hours" (beats: staff-controlled slot allocation) |
| "Delightful" | Untestable; invites surprise features | "A patient always knows what to do before the visit from the message they will read, not the letter" (beats: one authoritative document) |
| "Patient-centric" | Every option claims it | "Clinical urgency outranks convenience: no automated action moves an urgent patient later" (beats: full self-service) |

Checks: each principle is observable in a prototype review; principles do not contradict one another without a stated priority order; at least one principle protects a guardrail.

## Step 3 — Set target outcomes per layer, with guardrails

For each metric layer the opportunities touch, state baseline, target direction and range, and the metric ID. Targets follow the journey-metrics skill's rules: no target without a baseline; no target on a leading metric whose edge to the outcome is `hypothesis`.

| Layer | Question |
|---|---|
| actor-outcome | What result does the actor reach, by when? |
| behavior | What will actors do differently? |
| experience | What will actors perceive differently? |
| operational | What service condition changes? |
| employee-service | What changes for the staff who deliver it? |
| business | What organizational result follows (context, not the aim)? |
| guardrail | What must not get worse, for whom, with what threshold and owner? |

Every optimized metric has a guardrail, and every segment the change could exclude has one.

## Step 4 — Build the scenario set

A target described only by its happy path is a sales pitch. Write four kinds of scenario, each as a short sequence of actor steps, frontstage responses, and backstage actions:

1. **Happy path** — the common case under the target design.
2. **Failure and recovery** — what happens when the target design's own mechanism fails (no slot available, system down, message not delivered). Recovery is part of the target.
3. **High-risk edge** — the case where a wrong action causes serious or irreversible harm. Design the safe path first; it often sets decision rights.
4. **Segment variants** — actors for whom the default path does not work (no smartphone, language, disability, low trust, proxy users). Each variant must reach the same outcome by another route.

Test each scenario against every principle; a scenario that breaks a principle means one of them is wrong.

## Step 5 — Write service promises and design recovery

A service promise is a specific commitment the actor can check: what will happen, by when, and what the organization will do if it does not (Bitner 1995). Promises set expectations; unkept promises cost more trust than no promise.

For each moment that matters in scope:

- the promise, in the actor's words, with a time or condition;
- the operational metric that shows whether it is kept;
- the recovery: who notices a broken promise (ideally the organization, before the actor), what the actor is told, what is done, and within what time;
- the authority frontline staff have to recover without escalation (Hart, Heskett & Sasser 1990).

Do not promise what the capability-gap analysis (step 7) cannot yet deliver; phase the promise with the transitional state that makes it true.

## Step 6 — Derive service implications by layer

For each scenario step, ask what must be true in each layer:

| Layer | Ask |
|---|---|
| People and roles | Who does new work, stops old work, needs new authority or skills? |
| Process | Which queues, handoffs, and service levels change? |
| Policy | Which rule must change, and who owns it? |
| Data | What data must exist, where, fresh to what latency, and who consumes it? |
| Systems | Which integrations, events, or configurations are needed? |
| AI and automation | See below |
| Partners | Which external party's commitments change? |
| Governance | Who owns the end-to-end state and reviews the new metrics? |

For AI and automation, write four things per automated capability:

- **Decision rights.** What it may decide alone, what it may propose for a human to confirm, and what it may never do. Write the "never" list from the high-risk scenario.
- **Confidence handling.** What the system does when its confidence is low or the input is out of scope: ask a clarifying question, hand off, or refuse. Name the threshold and who sets it.
- **Escalation.** To whom, through which channel, with what context passed along so the actor does not repeat themselves, and within what time.
- **Failure disclosure.** How the actor learns they are dealing with automation, what it did and did not do, and how to reach a person. Make it clear what the system can do and how well (Amershi et al. 2019); treat the automation as a risk to be mapped, measured, and managed with a named owner (NIST AI RMF 1.0).

## Step 7 — Analyze capability gaps

| Capability | Needed for | Current state | Gap | Type | Owner | Dependency | Lands in |
|---|---|---|---|---|---|---|---|

`Type` is build, buy, configure, policy, organization, or partner. `Lands in` names the transitional journey that first delivers it. A target element with a gap nobody owns is fantasy; either assign it or move the element to a later horizon.

## Step 8 — Model transitional states and migration

When rollout is staged, the actor lives in a mix of old and new for months. Model it.

- The target and each transitional state are separate L2 journeys with their own `JRN-` IDs, `state` `target` or `transitional`, and `baseline_journey_id` pointing at the `current` journey (the journey-architecture skill's ontology). The current journey keeps its evidence; do not edit it into the target.
- For each transitional state, write who experiences what: which segments, sites, or channels are on the new path, which are on the old, and which see a hybrid.
- Check each hybrid for broken promises: an actor told "reschedule any time" at a site where the link is not live yet is a new failure the current state did not have.
- Order transitional states by dependency and by risk: reversible, low-harm changes first; changes needing a policy or partner commitment after the evidence from earlier states.
- Record which opportunities each transitional state realizes, so portfolio views can link them.

## Step 9 — Map assumptions and convert them into experiments

List every assumption the target depends on: desirability (actors will use and value it), feasibility (we can build and run it), viability (it is worth it and allowed), and safety (it will not harm anyone). Rate each by importance (does the target fail if it is wrong?) and evidence (status of what supports it). Assumptions that are important and weakly evidenced are tested first (Bland & Osterwalder 2019).

For each assumption to test:

1. state it as a metric edge or a guardrail claim with `MET-` IDs;
2. choose a design, sample, and stop rules using `references/experiment-design.md`;
3. write the initiative row: `hypothesis` holds the assumption, `change` the smallest change that tests it, `expected_effect` the pre-registered movement and MDE;
4. state the decision each result leads to.

Important assumptions that cannot be tested before commitment are named as risks with a monitoring plan and a rollback trigger.

## Anti-patterns

- **Feature backlog dressed as vision.** The target is a list of features with no principles, outcomes, or scenarios. Test: remove every feature name; if nothing is left, it is a backlog.
- **"Seamless", "delightful", "frictionless" principles.** They resolve no trade-off. Replace with the conflict they are meant to win.
- **Target mixed into current.** Current-state maps updated with planned changes, so evidence and aspiration cannot be told apart. Keep separate journeys linked by `baseline_journey_id`.
- **Happy path only.** No failure, recovery, or high-risk scenario, so automation gets decision rights nobody examined.
- **Promise without capability.** A promise published before the transitional state that can keep it.
- **Automation without disclosure.** Actors cannot tell what a bot did or how to reach a person.
- **Every assumption treated as fact.** No assumption map; the first real test is the full rollout.

## Worked example

Fictional scenario shared with the experiment-design method. Current journey `JRN-CUST-CLINIC-BOOK-001`, "Get a specialist appointment and attend it"; stages 01 Get referred, 02 Book a slot, 03 Prepare and attend, 04 Change or recover an appointment. Actor: referred patient.

Opportunities in scope:

| opportunity_id | node_id | problem | root_cause | root_cause_status | decision |
|---|---|---|---|---|---|
| OPP-0851 | NOD-CUST-CLINIC-BOOK-001-04 | Patients who cannot attend do not come; 12% no-show | Appointments can be changed only by phone, weekdays 9–17; 38% of calls abandoned | observed | act-now |
| OPP-0852 | NOD-CUST-CLINIC-BOOK-001-03 | Patients arrive unprepared and the visit is cancelled on the day | Preparation instructions sent only in the referral letter | inferred | act-now |
| OPP-0853 | NOD-CUST-CLINIC-BOOK-001-02 | Freed slots are not reused, so waits stay long | No waiting-list process for released slots | hypothesis | investigate |

Principles, each with the decision it resolves:

1. "A patient can change an appointment when they discover the conflict, even outside staff hours." Decides: self-service rescheduling from the reminder rather than a callback request.
2. "Clinical urgency outranks convenience: no automated action moves an urgent patient later." Decides: the assistant hands urgent-flagged patients to a nurse even when a later slot is free and the patient asks for it.
3. "A patient always knows what to do before the visit from the message they will read." Decides: preparation steps go in the reminder sequence, and the letter points to them, not the reverse.
4. "A released slot goes to someone waiting before it goes unused." Decides: release triggers a waiting-list offer, even though the front desk loses manual control of that slot.

Target outcomes (abridged):

| Layer | Metric | Baseline | Target |
|---|---|---|---|
| actor-outcome | `MET-0851` seen within 21 days of referral | 58% | read as trend; no target until the `MET-0852` edge is tested |
| behavior | `MET-0852` no-show per booked appointment | 12% | ≤9% |
| behavior | `MET-0853` self-reschedule among reminded patients | not yet measured | baseline first |
| operational | `MET-0854` freed slots rebooked within 48 h | 35% | set after `OPP-0853` investigation |
| guardrail | `MET-0855` urgent-flagged appointments moved beyond clinical window, per 1,000 bookings | 0.8 | ≤0.8; owner: clinical safety lead |
| guardrail | `MET-0856` no-show, patients 75+ | 13% | no worse than +2 points |

Scenarios:

- **Happy path.** Reminder 7 days ahead with preparation steps and a "change" link; patient picks a new slot; old slot released to the waiting list.
- **Failure and recovery.** No slot within 21 days of referral: the patient is placed on the waiting list and promised a call from the booking team by the next working day; the team sees the list each morning.
- **High-risk edge.** An urgent-flagged patient replies "can I move this to next month?": the assistant does not offer slots, says a nurse will call today, and passes the reply and the flag to the nurse queue.
- **Segment variants.** Patients without a mobile number get the reminder by automated call with a keypad option to speak to the booking team; interpreter-flagged patients get a staff call, not the assistant.

Service promise at stage 04: "Tell us by 18:00 the day before and your place is kept: you get a new date within 21 days of referral, or someone calls you by the next working day." Kept-promise metric: share of released-slot patients rebooked within 21 days or called within one working day. Recovery: the morning list of unfulfilled promises goes to the booking lead, who may offer an overbook slot without escalation.

AI decision rights for the reply assistant:

| May decide | May propose, human confirms | Never |
|---|---|---|
| Offer routine slots within the clinical window; release the old slot | Moves that cross clinics | Move an urgent-flagged appointment; give clinical advice; cancel without offering a new date |

Confidence: intent confidence below the threshold set by the booking lead, or any clinical wording, routes the reply to staff. Disclosure: every assistant message says it is automated and how to reach a person; after a handoff it tells the patient who will call and when.

Capability gaps:

| Capability | Gap | Type | Owner | Lands in |
|---|---|---|---|---|
| Self-reschedule link in reminders | Booking system exposes no patient-facing change endpoint | configure | Booking platform owner | `JRN-CUST-CLINIC-BOOK-003` |
| Urgent flag visible to automation | Flag lives in the clinical record only | build | Clinical systems lead | `JRN-CUST-CLINIC-BOOK-003` (before the assistant goes live) |
| Waiting-list offer on release | No waiting-list process | organization and build | Head of outpatient operations | `JRN-CUST-CLINIC-BOOK-002` |

Journey versions (abridged registry rows):

| journey_id | state | baseline_journey_id | name |
|---|---|---|---|
| JRN-CUST-CLINIC-BOOK-001 | current | — | Get a specialist appointment and attend it |
| JRN-CUST-CLINIC-BOOK-003 | transitional | JRN-CUST-CLINIC-BOOK-001 | Get a specialist appointment and attend it: reminder link and preparation steps, no waiting list |
| JRN-CUST-CLINIC-BOOK-002 | target | JRN-CUST-CLINIC-BOOK-001 | Get a specialist appointment and attend it: self-service change with waiting-list refill |

Who experiences what during rollout of `JRN-CUST-CLINIC-BOOK-003`: patients in the test's treatment arm get the link and the assistant; control patients and interpreter-flagged patients keep the phone path. Released slots are not yet refilled automatically, so the step 5 promise is not published until the waiting list lands in `JRN-CUST-CLINIC-BOOK-002`; in the meantime the reminder says only that the slot will be offered to someone else.

Assumption map (abridged):

| Assumption | Kind | Importance | Evidence | Next step |
|---|---|---|---|---|
| Patients who can reschedule themselves will do so instead of not coming (`MET-0853` drives `MET-0852`) | desirability | high | `inferred` (a volunteer-clinic pilot) | Randomized test `INI-0851` |
| The assistant never moves an urgent patient later (`MET-0855` protects `MET-0852`) | safety | high | `hypothesis` | Remove by design (decision right withheld); trace every urgent reply |
| Patients 75+ are not left behind | safety | high | `unknown` | Pre-registered non-inferiority cut in `INI-0851` |
| Released slots can be refilled within 48 h | feasibility | medium | `hypothesis` | `investigate`: one-clinic manual waiting-list trial |

Initiative rows (abridged):

| initiative_id | opportunity_ids | hypothesis | change | expected_metric_ids | expected_effect | status |
|---|---|---|---|---|---|---|
| INI-0851 | OPP-0851 | Self-rescheduling from the reminder reduces no-shows | Reminder with change link and reply assistant, individually randomized | MET-0853;MET-0852;MET-0855;MET-0856 | No-show −3 points; MDE 3 at 1,634 per arm | accepted |
| INI-0852 | OPP-0852 | Preparation steps in the reminder reduce on-the-day cancellations | Add preparation steps to the reminder sequence | MET-0852 | Monitored before/after; reversible, no harm path | accepted |

`INI-0852` is not tested: the change is cheap, reversible, and has no plausible harm path, so the decision would not change with a result.

## Quality checks

- Every target element traces to an `OPP-` ID or a named strategic hypothesis.
- Every principle names the trade-off it resolves; none is an adjective.
- Outcomes and guardrails are set per layer, with baselines, owners, and segment guardrails.
- The scenario set includes failure and recovery, a high-risk edge, and segment variants.
- Every promise has a kept-promise metric and a recovery; no promise precedes the capability that keeps it.
- Every automated capability has decision rights, confidence handling, escalation, and disclosure.
- Target and transitional journeys have their own IDs and `baseline_journey_id`; the current journey is untouched.
- Important, weakly evidenced assumptions have an experiment or an explicit reason not to run one.

## Sources

- Mary Jo Bitner, "Building service relationships: It's all about promises", *Journal of the Academy of Marketing Science* 23(4), 246–251, 1995: https://doi.org/10.1177/009207039502300403
- Christopher W. L. Hart, James L. Heskett, W. Earl Sasser Jr., "The Profitable Art of Service Recovery", *Harvard Business Review* 68(4), 148–156, 1990: https://hbr.org/1990/07/the-profitable-art-of-service-recovery
- Saleema Amershi et al., "Guidelines for Human-AI Interaction", *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, 2019: https://doi.org/10.1145/3290605.3300233
- National Institute of Standards and Technology, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, 2023: https://doi.org/10.6028/NIST.AI.100-1
- David J. Bland, Alexander Osterwalder, *Testing Business Ideas: A Field Guide for Rapid Experimentation*, Wiley, 2019: https://www.wiley.com/en-us/Testing+Business+Ideas:+A+Field+Guide+for+Rapid+Experimentation-p-9781119551447
