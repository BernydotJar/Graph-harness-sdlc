# Reference

## Contracts

- Project schema: [`schemas/project-v1.schema.json`](../schemas/project-v1.schema.json)
- Event schema: [`schemas/event-v1.schema.json`](../schemas/event-v1.schema.json)
- Python package: [`graph_harness/`](../graph_harness/)

## Node statuses

```text
pending
spec_ready
approved
ready
running
review
done
blocked
repair_required
superseded
```

See [`graph_harness/model.py`](../graph_harness/model.py) for the normative enum.

## Event types

```text
approval.recorded
evidence.recorded
gate.evaluated
node.transitioned
failure.recorded
node.invalidated
repair.plan_created
checkpoint.recorded
```

## Gate results

```text
PASS
FAIL
BLOCKED
```

## CLI commands

```text
validate
status
ready
record-approval
record-evidence
evaluate-gate
transition
fail
checkpoint
```

Run:

```sh
python3 -m graph_harness --help
```

## Program terminal states

```text
COMPLETED
PARTIAL_WITH_DOCUMENTED_BLOCKERS
SAFETY_STOP
```

These are documented program outcomes, not values of the node-status enum. See [Program terminal states](terminal-states.md).

## Operational instructions

- Repository tool contract: [`RTK.md`](../RTK.md)
- Agent entry point: [`AGENTS.md`](../AGENTS.md)
- Claude entry point: [`CLAUDE.md`](../CLAUDE.md)
- Quality gates: [`quality-gates.md`](quality-gates.md)
- Verification: [`verification.md`](verification.md)
