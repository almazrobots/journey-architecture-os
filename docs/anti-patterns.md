# Anti-patterns

## 1. Persona theater
A fictional persona is treated as evidence.

**Correction:** attach source evidence and describe segmentation logic.

## 2. The universal seven-stage journey
A generic lifecycle is reused regardless of actual behavior.

**Correction:** derive stages from evidence of the actor's progression: goal changes, commitment points, experienced waits, knowledge thresholds. A change of channel, department, or system is not a stage boundary on its own.

## 3. The emotion roller coaster
A wavy line is drawn without evidence.

**Correction:** show emotion only with source, method, and uncertainty.

## 4. Touchpoint inventory disguised as a journey
The map lists company channels but does not show actor goals or outcomes.

**Correction:** start with actor progress; channels are supporting attributes.

## 5. Current and future state blended together
Pain points and proposed solutions appear on the same map without state labels.

**Correction:** separate current, transitional, and target state.

## 6. The service blueprint mega-poster
Customer experience, processes, systems, org chart, and roadmap are crammed into one artifact.

**Correction:** keep linked views with stable IDs.

## 7. Workshop consensus equals truth
Internal stakeholders agree on a map and call it validated.

**Correction:** consensus produces a hypothesis map; research validates or invalidates it.

## 8. Opportunity = feature
"Build chatbot" is called an opportunity.

**Correction:** opportunity describes unmet need or outcome; solutions come later.

## 9. Metric wallpaper
Every available KPI is attached to the journey.

**Correction:** one actor-outcome root per journey, 15 metrics or fewer, each linked to the root through `drives` edges (guardrails through `protects`), every edge carrying its own `evidence_status`. `hypothesis` edges are allowed and mark what to test next; a metric may carry a target only when some path to the root has no `hypothesis` edge. A metric that no edge connects to the outcome is dashboard noise.

## 10. Ownerless journey
Nobody is accountable for keeping the model current or moving outcomes.

**Correction:** assign journey owner and contribution model.

## 11. One-time artifact
The map has no version, review date, evidence freshness, or change log.

**Correction:** apply journey governance.

## 12. AI decoration
An "AI" row is added without decisions, data, escalation, or failure modes.

**Correction:** model AI as an operational service actor.

## 13. Root cause by assertion
A problem is well evidenced, so its assumed cause is written down as fact and an opportunity is built on it.

**Correction:** record `problem` and `root_cause` separately, each with its own status. An `observed` problem with a `hypothesis` cause is an `investigate` decision, not `act-now`.

## 14. The confident unknown
Gaps are filled with plausible text so the map looks complete.

**Correction:** register material gaps as `unknown` evidence rows and cite them; an audit penalizes invented content, not labeled gaps.

## 15. Leading indicator by naming
A metric is called "leading" because it happens earlier in the journey.

**Correction:** call it leading only after checking its predictive link in data; until then it is a candidate driver with a `hypothesis` edge.
