# Loop Engineering

Loop Engineering designs the repeatable work loops around the model.

The loop is:

```text
input -> context -> decision -> tool action -> verification -> review -> next state
```

## Spec Loop

- read feature registry
- select one pending feature
- write requirements/design/tasks
- validate harness
- stop for approval

## Implementation Loop

- confirm approved state
- read approved spec
- edit only allowed files
- run verification
- record evidence
- move to review

## Review Loop

- compare implementation to spec
- inspect tests and verification
- write review artifact
- reject, block, or recommend closure

## Production Hardening Loop

- apply SHIP mode gates
- document risks and operational constraints
- require fixes before close when production gaps remain

## Blocker Loop

- name the blocker
- record required human input
- set `blocked` only when work cannot continue
- resume from the same feature after clarification

## Close Loop

- confirm review passed
- confirm verification passed
- confirm human closure approval
- record closure
- mark `done`

