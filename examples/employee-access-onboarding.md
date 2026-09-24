# Example — Employee access onboarding

> Fictional example.

## Journey header

- ID: `JRN-EMP-ACCESS-001`
- Actor: newly hired knowledge worker
- Trigger: employment begins
- Desired outcome: can perform core role tasks using required systems
- State: hypothesis

| Stage | Employee goal | Employee action | Service dependency | Candidate friction |
|---|---|---|---|---|
| Know what is needed | Understand required tools/access | Check onboarding info, ask manager | HR + manager role profile | Requirements differ by team |
| Request/access | Get accounts | Follow links, authenticate | IAM + ITSM | Multiple separate requests |
| Resolve gaps | Fix missing permissions | Ask manager/IT | Manager approvals + service desk | Ownership unclear |
| Become productive | Use tools for real work | Perform first role tasks | Apps + knowledge + team | Access exists but context missing |

## Blueprint implication

Potential backstage layers:
- HR creates employee record;
- manager supplies role/access profile;
- IAM provisions baseline permissions;
- app owners approve exceptions;
- service desk resolves failures.

## Metrics candidates

- time to role-ready access;
- % baseline access ready by start;
- access-related contacts per new hire;
- time lost waiting for approval;
- first successful role-critical task.
