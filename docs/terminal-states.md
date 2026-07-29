# Program Terminal States

Program terminal states describe the final outcome of an entire execution program. They are not node statuses and are not replacements for `done`, `blocked` or `repair_required`.

## `COMPLETED`

Use `COMPLETED` when:

- every required product node is complete;
- all required evidence is current and passing;
- all mandatory quality and release gates are satisfied;
- no unresolved blocker prevents the declared product objective;
- the graph and event ledger validate.

A repository may still contain optional backlog work. `COMPLETED` means the declared execution objective is finished.

## `PARTIAL_WITH_DOCUMENTED_BLOCKERS`

Use `PARTIAL_WITH_DOCUMENTED_BLOCKERS` when useful, verified work is complete but the declared objective cannot be fully reached because of blockers outside the currently executable graph.

Required evidence includes:

- completed and preserved nodes;
- unresolved blocker descriptions;
- affected scope;
- attempted mitigations;
- owner or external dependency;
- exact resume conditions;
- remaining risks and limitations.

This state must not disguise ordinary unfinished work. It is valid only when further autonomous progress is not currently possible and the partial result remains useful and auditable.

## `SAFETY_STOP`

Use `SAFETY_STOP` when continuing would violate a safety, legal, security, privacy, authorization or destructive-operation boundary.

Required evidence includes:

- the triggering rule or risk;
- the last safe checkpoint;
- actions explicitly not taken;
- affected nodes and preserved evidence;
- the human authority required to resume, when resumption is possible.

A safety stop takes precedence over throughput or completion pressure.

## Derivation from node state

Program outcomes are derived from the graph, gates and declared objective. A simple policy may be expressed as:

```text
all required nodes done and all gates pass
    -> COMPLETED

useful verified subset complete and external blockers documented
    -> PARTIAL_WITH_DOCUMENTED_BLOCKERS

continuation crosses a prohibited safety or authority boundary
    -> SAFETY_STOP
```

A single blocked node does not automatically determine the program outcome. The scheduler or repository policy must evaluate whether other useful nodes can still run.

## Evidence requirement

A terminal-state declaration is itself an auditable decision. It should be recorded with:

- graph revision;
- repository commit;
- checkpoint identifier;
- evidence summary;
- unresolved risks;
- responsible human or policy actor.
