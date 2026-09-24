---
name: jobs-and-outcomes
description: Frames what a customer, employee, or other actor is trying to accomplish using jobs, progress, context, desired outcomes, constraints, and success criteria independent of a specific solution. Use when journey stages are organization-centric, requirements are feature-led, user needs are vague, or opportunity statements need stronger outcome language.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Jobs and Outcomes

## Goal

Anchor journey work in actor progress rather than products, channels, or internal workflow.

## Workflow

### 1. Identify the situation
Capture trigger, context, constraints, and why the actor is acting now.

### 2. State the job
Use a solution-independent form:

`When [situation], I want to [make progress], so I can [meaningful outcome].`

Treat this as a framing device, not a formula that must fit every case.

This is Klement's job-story form. Before choosing a form, read `references/jobs-method.md`: it separates the Christensen, Ulwick (ODI), and Klement traditions, says when to use each, and covers switch interviews as evidence.

### 3. Separate job layers
When useful distinguish:

- functional progress;
- emotional progress;
- social progress;
- enabling jobs;
- adjacent jobs.

### 4. Define outcomes
Describe desired results independently of a proposed feature.

Good outcomes are:
- observable or assessable;
- relevant to the actor;
- specific enough to guide decisions;
- not a disguised solution.

For a job map and desired outcome statements ("Minimize the time it takes to…"), follow Steps 3–4 of `references/jobs-method.md`.

### 5. Add constraints/trade-offs
Time, risk, effort, cost, privacy, control, confidence, coordination.

### 6. Connect to journey
Attach jobs/outcomes to stages or episodes.

### 7. Detect organization-centric language
Rewrite:
- "submit form" → what progress requires the form?
- "call support" → what outcome drives the call?
- "complete training" → what capability should result?

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

A jobs table is a view, not a register: jobs have no IDs of their own. Link each job to the journey nodes it explains (`node_ids`) and to the evidence behind it.

| context | job/progress | desired_outcomes | constraints | current_workarounds | node_ids | evidence_ids | evidence_status |
|---|---|---|---|---|---|---|---|

A job written from product or stakeholder knowledge is `hypothesis` until actors describe that progress in their own words.

## Quality gates

- job is not a feature;
- outcome is not "use the product";
- emotional/social dimensions are evidenced or explicitly hypothesized;
- the wording can survive a channel or product redesign.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/jobs-method.md` before stating jobs or desired outcomes, and when attaching them to journey stages and metrics.
