# Loop Engineering

Loop Engineering designs repeatable work cycles around the execution graph. A loop must consume typed state, produce traceable evidence and end in a validated transition, checkpoint, blocker or safety decision.

## Primary execution loop

```text
ready node
  -> producer
  -> critic / red team
  -> fixer
  -> independent verifier
  -> release gate
  -> persistent evidence
  -> next ready node
```

## Specification loop

- read the feature registry and current graph;
- select an eligible feature;
- write requirements, design and tasks;
- define file boundaries and verification;
- validate the harness;
- stop for required human approval.

## Implementation loop

- confirm approved and ready state;
- read the approved specification;
- edit only allowed files;
- record implementation evidence;
- checkpoint before long or risky operations;
- move to critique and verification.

## Critic and repair loop

- compare the produced artifact against the specification;
- search for defects, contradictions and missing failure modes;
- record findings as evidence;
- repair the smallest affected scope;
- rerun only invalidated checks.

## Verification loop

- verify independently from the producer;
- confirm evidence belongs to the current node revision;
- evaluate deterministic gates;
- reject stale, incomplete or self-asserted evidence;
- recommend transition only when requirements are demonstrated.

## Blocker loop

- name the blocker precisely;
- record attempted mitigations;
- identify affected and unaffected nodes;
- continue other ready nodes when safe;
- set `blocked` only when the node cannot progress;
- record exact resume conditions.

## Safety loop

- stop before crossing an authorization, security, privacy, legal or destructive-operation boundary;
- preserve the last safe checkpoint;
- record actions not taken;
- require the appropriate human authority before resumption.

## Program closure loop

- validate graph and event integrity;
- compare completed nodes with the declared objective;
- inspect blockers and safety boundaries;
- select the correct program terminal state;
- attach evidence and a final checkpoint;
- do not describe partial or unsafe work as completed.

See [Program terminal states](terminal-states.md).
