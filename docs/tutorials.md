# Tutorials

## 1. Validate an execution graph

Prepare a project definition and an empty event ledger:

```sh
python3 -m graph_harness \
  --project graph-harness.project.json \
  --events graph-harness.events.jsonl \
  validate
```

Inspect derived state:

```sh
python3 -m graph_harness \
  --project graph-harness.project.json \
  --events graph-harness.events.jsonl \
  status --pretty
```

## 2. Execute one feature through gates

1. Create requirements, design and tasks.
2. Record specification evidence.
3. Evaluate the spec gate.
4. Record explicit human approval.
5. Transition the node to `approved`, then `ready`.
6. Assign an executor with the required capability.
7. Record implementation and test evidence.
8. Run critic and verifier roles.
9. Evaluate review and production gates.
10. Transition to `done` only when closure evidence passes.

See the CLI in [Reference](reference.md) and examples under [`examples/`](../examples/).

## 3. Resume a long session

A resumable session should begin from persisted state, not conversational memory:

1. validate the project and event chain;
2. inspect the latest checkpoint;
3. verify repository commit and evidence hashes;
4. list ready nodes;
5. continue only nodes whose dependencies and gates remain valid;
6. record a new checkpoint before a long or risky operation.

## 4. Repair a failed gate

1. Record the failure against the source node and gate.
2. Let the runtime compute affected descendants.
3. Inspect the generated repair plan.
4. preserve unaffected evidence;
5. repair the smallest affected subgraph;
6. rerun only the gates invalidated by the new revision;
7. resume scheduling from the newly ready nodes.

## 5. Declare a terminal outcome

Before declaring a program terminal state:

1. identify the declared product objective;
2. validate the graph and ledger;
3. inspect incomplete or blocked required nodes;
4. evaluate safety and authority boundaries;
5. select `COMPLETED`, `PARTIAL_WITH_DOCUMENTED_BLOCKERS` or `SAFETY_STOP`;
6. attach the terminal decision to a persistent checkpoint.
