---
name: service-blueprinting
description: Builds service blueprints that connect customer or employee actions to frontstage interactions, backstage work, supporting processes, people, policies, data, systems, partners, automation, and AI. Use when a journey problem requires root-cause analysis, handoff analysis, operational redesign, service delivery architecture, or visibility into how an experience is produced. Prefer it over a generic process map or swimlane whenever the question is why customers or employees wait, get stuck, repeat themselves, or receive inconsistent service, even when the request says 'process map'.
license: MIT
metadata:
  author: journey-architecture-os
  version: "2.0.0"
  domain: experience-architecture
---

# Service Blueprinting

## Goal

Explain how an experience is produced so teams can change root causes, not only touchpoints.

## Prerequisite

Have at least a provisional actor journey. A blueprint without an actor experience often becomes an internal process map.

## Recommended layers

1. Actor actions.
2. Frontstage interactions.
3. Backstage actions.
4. Supporting processes/teams.
5. Policies/rules.
6. Data/information.
7. Systems/platforms.
8. Partners/vendors.
9. Automation/AI.
10. Evidence/metrics/failure modes.

Use only the layers needed.

## Workflow

### 1. Select journey scope
Blueprint one journey or episode at a useful level.

### 2. Place actor actions first
Keep actor progress visible across the top.

### 3. Map frontstage
Capture human and digital service interactions visible to the actor.

### 4. Map backstage
Show invisible work directly enabling frontstage.

### 5. Add supporting capability
Processes or teams that enable backstage delivery.

### 6. Add policies and decision rules
Many experience failures are policy failures disguised as UX problems.

### 7. Add data and systems
Show critical data creation, handoff, lookup, decision, and state changes.

### 8. Add automation and AI
For each automated/AI step capture:
- trigger;
- inputs;
- output/action;
- confidence/uncertainty handling;
- human review/override;
- escalation;
- failure behavior;
- audit trail;
- user communication.

### 9. Identify handoffs and failure points
Look for:
- queueing;
- rekeying;
- ownership gaps;
- asynchronous delay;
- channel mismatch;
- inconsistent policy;
- data mismatch;
- hidden manual work;
- brittle automation.

### 10. Connect metrics
Attach operational metrics to causal layers, not only to the actor row.

### 11. Connect opportunities
Create root-cause-based opportunities. Trace each failure point from symptom to evidenced cause with `references/root-cause-analysis.md` before writing the opportunity.

## Conventions

Follow `references/conventions.md` for IDs, evidence statuses, and register columns.

## Output contract

Return a linked blueprint whose rows carry `node_id`, `evidence_status`, `evidence_ids`, and `metric_ids`. Backstage steps taken from process documents or owner interviews describe intended work: mark them `hypothesis` until observed in records, timestamps, or observation. Then add:

- critical dependencies;
- failure modes;
- ownership gaps;
- service risks;
- candidate root causes;
- metrics;
- opportunities.

## Quality gates

- actor journey remains visible;
- frontstage/backstage are distinguishable;
- systems are not treated as causes by default;
- policies and human decisions are captured when material;
- AI has escalation/failure behavior;
- failure points link back to actor impact.

## References

Read `references/conventions.md` for IDs, evidence statuses, and register columns.
Read `references/blueprint-layers.md`.
Read `references/root-cause-analysis.md` when a failure point needs a verified cause.
Use `assets/service-blueprint-template.md`.
