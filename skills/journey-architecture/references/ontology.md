# Journey architecture ontology

## Minimum object model

### ExperienceDomain
Broad area of human experience managed as a portfolio.

### Lifecycle
Long-running relationship or progression containing multiple journeys.

### Journey
Bounded progress toward a meaningful outcome.

### Episode
Coherent sub-goal within a journey.

### Interaction
Specific exchange, action, or touchpoint.

## Naming pattern

Prefer verbs and actor outcomes:

Good:
- Become a customer
- Start using the service
- Resolve a billing problem
- Return to work after leave

Weak:
- CRM process
- Onboarding workflow
- Contact center
- HRIS

## ID pattern

`JRN-{ACTOR}-{DOMAIN}-{NNN}`

Examples:

- `JRN-CUST-ONBOARD-001`
- `JRN-EMP-CAREER-004`

For nodes:

`NOD-{journey_id}-{NN}`

Do not embed current team or system names in stable IDs.

## State

Use:
- `current`
- `target`
- `transitional`

## Lifecycle status

Use:
- `draft`
- `validated`
- `active`
- `stale`
- `archived`
