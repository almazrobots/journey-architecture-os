# Jobs method

Method for stating what an actor is trying to accomplish, independently of the product, channel, or internal workflow, and for connecting that statement to journey stages and metrics. Use it in workflow steps 1–7. The result is the output table in the skill, plus a job map and desired outcome statements where they are useful.

"Jobs to be done" is not one method. Three traditions share the name and disagree on what a job is. This guide names each, says when to use it, and does not mix their vocabularies within one statement.

## The three traditions

| Tradition | What a job is | Unit of analysis | Main artifacts | Evidence it expects |
|---|---|---|---|---|
| Christensen, jobs theory (Christensen, Hall, Dillon & Duncan 2016) | The progress a person is trying to make in a particular circumstance; people "hire" products to make it and "fire" them when they do not | A struggle in a circumstance, with functional, social, and emotional dimensions | Job narrative; hiring and firing criteria; competing solutions including non-consumption | Stories of actual purchases, switches, and workarounds |
| Ulwick, Outcome-Driven Innovation (Ulwick 2002, 2016; Bettencourt & Ulwick 2008) | A stable functional task the customer executes, independent of any solution | The core functional job, broken into a job map; each step has measurable desired outcomes | Job map; desired outcome statements; importance/satisfaction survey; opportunity scores | Qualitative interviews to write outcomes, then a quantitative survey |
| Klement, job stories and progress (Klement 2013, 2018) | The actor's desire to change their situation (and themselves); a job story frames one situation-motivation-outcome | A situation with a triggering context and a motivation | Job stories: "When…, I want to…, so I can…" | Interviews about the situation that triggered action; switch/timeline interviews (Moesta) |

Where they disagree:

- **Task versus progress.** Ulwick treats the job as an activity with steps that can be measured ("get to a destination on time"). Christensen and Klement treat it as progress toward a changed situation, which can be served by very different activities. Klement explicitly argues against defining jobs as tasks.
- **Measurement.** ODI quantifies needs through a survey of outcome statements. Jobs theory and job stories are mostly qualitative and explanatory: why people switched, what they were struggling with.
- **Granularity.** ODI's core functional job is deliberately broad and stable over decades; a job story is small enough to guide a single design decision.

## When to use which

| Situation | Use | Why |
|---|---|---|
| Stages of a journey are named after the organization's process | Christensen's progress framing to name the journey outcome; ODI job map to test stage coverage | Progress gives the outcome; the job map checks that no actor step is missing |
| Need to rank many unmet needs in a known domain with enough respondents for a survey | ODI desired outcome statements and importance/satisfaction | Gives a comparable, quantitative view of underserved outcomes |
| Need to explain why actors switch, stall, or leave | Jobs theory with switch/timeline interviews | Recovers the circumstances and forces behind choices |
| A design team needs to state the context for one feature or episode | Klement job story at the episode node | Small, situation-bound, tests the design against a motivation |
| Employee journeys | Progress framing plus job map; ODI survey only for large, homogeneous roles | Employee populations are often too small for stable outcome surveys |

Record which tradition each statement comes from. A "job" column that mixes a Christensen progress statement, an ODI outcome, and a job story compares unlike things.

## Step 1 — Gather evidence about the situation

Jobs are inferred from what actors did, not from what they say they want. Use interviews about a recent, real decision.

Switch or timeline interview (Moesta & Spiek, jobs theory practice):

1. Pick people who recently made the change you care about: started, switched to, or left the service within the last few months.
2. Reconstruct the timeline: first thought ("when did you first realize you needed something different?"), passive looking, the event that turned it into active looking, deciding, first use, and what they stopped doing.
3. For each step, ask what happened, where they were, who else was involved, what they tried, and what almost stopped them.
4. Map the forces: push of the current situation, pull of the new one, anxiety about the new, habit of the present. A switch happens when push and pull exceed anxiety and habit.
5. Include people who considered the change and did not make it; they show the anxieties and habits.

Rules:

- Interview about behavior in a specific episode. "What would you want?" produces features.
- Capture workarounds (spreadsheets, calling twice, asking a friend). They show the job being done without the service.
- A job described only by product managers or stakeholders is `hypothesis` until actors describe the same progress in their own words.

## Step 2 — Write the job at the right level

Write one statement per tradition you use.

- **Progress statement (Christensen):** "Help me [make progress] when [circumstance], without [what I want to avoid]." Include the circumstance; a job without a circumstance is a category.
- **Core functional job (Ulwick):** verb + object + contextual clarifier, with no solution and no adjectives of quality: "maintain home internet access across a change of address".
- **Job story (Klement):** "When [situation], I want to [motivation], so I can [expected outcome]." The situation is specific and triggering; the motivation is not a feature.

Level test: move up by asking "why?" and down by asking "how?". The statement is at the right level for journey work when it (1) matches the boundary of the journey or stage you are working on, (2) could be served by at least three different solutions, and (3) would survive a redesign of every channel.

## Step 3 — Build a job map

Bettencourt and Ulwick describe eight universal steps. Use them as a checklist of what the actor must accomplish, not as journey stages.

| Job step | Actor must… |
|---|---|
| Define | determine goals and plan the approach |
| Locate | gather the inputs and information needed |
| Prepare | set up the environment and inputs |
| Confirm | verify everything is ready before executing |
| Execute | carry out the core of the job |
| Monitor | check that execution is going as intended |
| Modify | make changes when it is not |
| Conclude | finish the job and close out |

Rules:

- Write each step as what the actor accomplishes, not what the organization does.
- Map job steps to journey stages in a table. Several steps may sit in one stage; a step with no stage means the journey omits part of the actor's work (often "confirm", "monitor", or "conclude"), and it is a finding.
- Journey stages remain the stages the actor recognizes in research. The job map checks them; it does not replace them.

## Step 4 — Write desired outcome statements

ODI outcome statements describe how the actor measures success on a job step. Structure: direction + metric + object of control + contextual clarifier.

- "Minimize the time it takes to find out whether service is available at the new address."
- "Minimize the likelihood of paying for service at two addresses at once."

Rules:

- One metric per statement: time, likelihood, number, or amount.
- No solution words ("using the app"), no ambiguous adjectives ("easily", "quickly"), no compound statements joined by "and".
- Written from the actor's view, stable across solutions.
- Aim for coverage across job steps, not dozens per step. For journey work, 3–8 outcomes per L2 journey that link to metrics are more useful than a full ODI inventory of 50–150.

Importance and satisfaction: in a survey, respondents rate each outcome's importance and their satisfaction with how they get it done today, usually on 5-point scales. In ODI practice each is converted to a top-two-box share (the percentage rating 4 or 5) and divided by 10, so importance and satisfaction each run from 0 to 10. The opportunity score is importance + max(importance − satisfaction, 0), which runs from 0 to 20. (Ulwick's 2002 article used mean ratings on a 1–10 scale; if you use means, say so, because the thresholds below do not transfer.)

Bands used in this guide, following common ODI practice:

| Condition | Band |
|---|---|
| Satisfaction > importance | overserved, whatever the score |
| Score ≥ 15 | extremely underserved |
| 12 ≤ score < 15 | underserved |
| 10 ≤ score < 12 | borderline; watch |
| Score < 10 | appropriately served |

Use the scores with these cautions:

- The inputs are ordinal ratings, so small score differences are noise; read the scores as bands (underserved, appropriately served, overserved), not a ranking to one decimal.
- The survey population must be the actors in the job, segmented by circumstance; averaging across segments hides underserved groups.
- Satisfaction is with the current way of getting the job done, which may not be your service.
- Scores are `observed` for "respondents rate this outcome as important and unsatisfied". That the outcome drives behavior is a separate claim and needs behavioral evidence.

## Step 5 — Separate functional, emotional, and social dimensions

- **Functional:** what must get done ("working connection on moving day").
- **Emotional:** how the actor wants to feel or avoid feeling ("in control during a chaotic week").
- **Social:** how the actor wants to be seen by others ("not the one who leaves the family without internet").

Rules:

- Emotional and social dimensions need evidence of their own: quotes, observed behavior (checking, reassurance-seeking, involving others). Without it, mark them `hypothesis`.
- Do not write a feeling as a job step. Emotional dimensions qualify a job; they are not a separate process.
- Also record enabling jobs (jobs the actor must do to do the main job, such as "find my account number") and adjacent jobs (jobs before or after that the actor experiences as connected, such as "set up utilities at the new home").

## Step 6 — Attach jobs to the journey and metrics

- The journey's `desired_outcome` should read as the progress statement's outcome, in the actor's terms.
- Job steps map to stage nodes (Step 3); job stories attach to the episode or step node whose design they guide; record the node IDs in `node_ids`.
- Each desired outcome statement is a candidate metric. "Minimize the time between arriving and having a working connection" becomes an actor-outcome or experience metric with a numerator, denominator, population, and window. An outcome with no feasible measurement is kept and marked as an instrumentation gap.
- Outcomes with high importance and low satisfaction at a node are inputs to moment analysis and to opportunity statements.

## Common errors

| Error | Example | Fix |
|---|---|---|
| Feature as job | "Use the move-home portal" | Ask what the portal is for: "have a working connection at the new home" |
| Job too broad | "Live a connected life" | Narrow to the circumstance and the journey boundary |
| Job too narrow | "Enter the new postcode" | That is a step or a task; move up with "why?" |
| Persona as job | "Busy young professionals" | A persona describes who; a job describes the progress, in a circumstance anyone can be in |
| Organization's job | "Reduce move-related churn" | That is a business metric; restate the actor's progress |
| Outcome with a solution | "Minimize time to book an engineer online" | Remove the channel: "minimize time to arrange activation at the new address" |
| Tradition mixing | An ODI outcome written as a job story | Pick one form per statement |
| Stated wants as jobs | "Customers want a chatbot" | Return to a real episode; ask what happened |

## Worked example

Journey `JRN-CUST-TELCO-MOVE-001`, "Move home and stay connected". Stages: `NOD-CUST-TELCO-MOVE-001-01` Plan the move of my service; `-02` Arrange service at the new address; `-03` Get connected at the new home; `-04` Settle the old account.

Evidence: 12 switch interviews with customers who moved in the last 90 days, 6 who stayed and 6 who left (`EVD-2025-0721`); a survey of 410 recent movers rating 9 outcome statements (`EVD-2025-0722`); billing records of movers (`EVD-2025-0723`).

Timeline pattern: first thought at exchange of contracts; active looking 3–4 weeks before the move, triggered by realizing they would work from home the day after moving; leavers decided when told the earliest activation was 10+ days after the move date. Forces: push, fear of a gap in home working; pull, a competitor promising activation on the move date; anxiety, an early termination fee; habit, the bundled email address.

Statements:

- Progress (Christensen): "Help me keep my household working and in touch through a move, without a gap or paying twice."
- Core functional job (Ulwick): "Maintain home internet access across a change of address."
- Job story (Klement), for episode `NOD-CUST-TELCO-MOVE-001-02-01` "Choose an activation date": "When I have a confirmed moving date, I want to know the date my service will work at the new home, so I can plan to work from home the next day."

Job map to stages:

| job step | actor must… | stage |
|---|---|---|
| Define | decide what service is needed at the new home | 01 |
| Locate | find out availability and the earliest activation date | 01 |
| Prepare | arrange activation and equipment | 02 |
| Confirm | verify the activation date matches the move | 02 (no step in the current journey; finding) |
| Execute | get the connection working | 03 |
| Monitor | check that it works as expected | 03 |
| Modify | fix problems or reschedule | 03 |
| Conclude | close the old service and settle the final bill | 04 |

Desired outcomes, with survey results (top-two-box shares ÷ 10; score = importance + max(importance − satisfaction, 0)):

| desired outcome statement | importance | satisfaction | opportunity score | band | metric candidate |
|---|---|---|---|---|---|
| Minimize the time between arriving at the new home and having a working connection | 9.1 | 4.2 | 14.0 | underserved | MET-0721 |
| Minimize the likelihood of paying for service at two addresses at once | 8.4 | 3.9 | 12.9 | underserved | MET-0722 |
| Minimize the likelihood that the activation date differs from the moving date | 8.8 | 4.6 | 13.0 | underserved | MET-0723 |
| Minimize the time it takes to find out whether service is available at the new address | 7.2 | 7.5 | 7.2 | overserved (satisfaction > importance) | — |

Output rows:

| context | job/progress | desired_outcomes | constraints | current_workarounds | node_ids | evidence_ids | evidence_status |
|---|---|---|---|---|---|---|---|
| Household moving home with a fixed date; at least one person works from home | Keep the household working and in touch through a move without a gap or paying twice | Minimize time without a working connection after arrival; minimize likelihood of double billing; minimize likelihood that activation date differs from moving date | Moving date set by the property chain; contract notice period; landlord access for installation | Mobile hotspot for 1–3 weeks; working from a relative's home; calling repeatedly to move the date | NOD-CUST-TELCO-MOVE-001-01;NOD-CUST-TELCO-MOVE-001-02;NOD-CUST-TELCO-MOVE-001-03;NOD-CUST-TELCO-MOVE-001-04 | EVD-2025-0721;EVD-2025-0722;EVD-2025-0723 | inferred |
| Same household, emotional dimension | Feel in control during a disrupted week | — | — | Asking for written confirmation of dates | NOD-CUST-TELCO-MOVE-001-02 | EVD-2025-0721 | inferred |
| Same household, social dimension | Not be the one who leaves the family without internet | — | — | — | NOD-CUST-TELCO-MOVE-001-03 | — | hypothesis |

Status reasoning: the workarounds, timelines, and survey ratings are `observed` in their evidence rows, but the job itself is an interpretation of them, so the job row is `inferred`, with the reasoning above. A job statement is always an interpretation, so its status is `inferred` at best, and `hypothesis` when it rests on stakeholder input or a single source.

Connections made:

- The journey's `desired_outcome` became "working connection at the new home from the day of the move, with no double billing".
- `MET-0721` (days from move date to first working connection, per mover, median and p90) became the actor-outcome metric at the journey level.
- The missing "confirm" step became an input to moment analysis for stage 02.
- The social dimension appeared in two interviews only and is kept as a hypothesis.

## Quality checks

- Each statement names its tradition; forms are not mixed.
- Jobs come from episodes actors described, with workarounds recorded; stakeholder-only jobs are `hypothesis`.
- The job passes the level test: right boundary, three possible solutions, survives channel redesign.
- The job map is compared with journey stages and gaps are recorded as findings.
- Outcome statements have one metric, no solution words, and a candidate metric or an instrumentation gap.
- Opportunity scores are read as bands, by segment.
- Emotional and social dimensions carry their own evidence status.

## Sources

- Clayton M. Christensen, Taddy Hall, Karen Dillon, David S. Duncan, "Know Your Customers' 'Jobs to Be Done'", *Harvard Business Review* (September 2016): https://hbr.org/2016/09/know-your-customers-jobs-to-be-done
- Clayton M. Christensen, Taddy Hall, Karen Dillon, David S. Duncan, *Competing Against Luck: The Story of Innovation and Customer Choice* (2016), HarperBusiness: https://www.hbs.edu/faculty/Pages/item.aspx?num=51754
- Anthony W. Ulwick, "Turn Customer Input into Innovation", *Harvard Business Review* (January 2002): https://hbr.org/2002/01/turn-customer-input-into-innovation
- Lance A. Bettencourt & Anthony W. Ulwick, "The Customer-Centered Innovation Map", *Harvard Business Review* (May 2008): https://hbr.org/2008/05/the-customer-centered-innovation-map
- Anthony W. Ulwick, *Jobs to be Done: Theory to Practice* (2016), Idea Bite Press: https://anthonyulwick.com/2016/10/25/jobs-to-be-done-from-theory-to-practice/
- Alan Klement, "Replacing The User Story With The Job Story" (2013): https://medium.com/the-job-to-be-done/replacing-the-user-story-with-the-job-story-af7cdee10c27
- Alan Klement, *When Coffee and Kale Compete* (2018): https://www.revealed.market/when-coffee-and-kale-compete
- Bob Moesta with Greg Engle, *Demand-Side Sales 101: Stop Selling and Help Your Customers Make Progress* (2020), Lioncrest Publishing: https://lioncrest.com/books/demand-side-sales-101-stop-selling-and-help-your-customers-make-progress
- Bob Moesta & Chris Spiek, Jobs-to-be-Done switch interview training: https://jobstobedone.org/
- Jim Kalbach, *The Jobs To Be Done Playbook* (2020), Rosenfeld Media: https://rosenfeldmedia.com/books/jobs-to-be-done-book/
