# Deterministic Workflows Are Optional Capabilities

Graph Harness SDLC is not an RPA framework and does not require a deterministic workflow engine.

Many products are correctly implemented with application code, AI models, APIs, data systems, and infrastructure alone. Other products contain tasks where deterministic orchestration is safer, cheaper, easier to audit, or easier to operate than asking an LLM to decide every step.

The Harness supports both without making either style universal.

## Decision rule

Use an AI/agent executor when the task benefits from probabilistic reasoning, semantic interpretation, synthesis, planning, or adaptation.

Use deterministic code or workflow orchestration when the task has stable rules, explicit state transitions, strong idempotency requirements, transactional effects, predictable integration steps, or a need for mechanically reproducible behavior.

A hybrid node may use both, but its graph contract still defines dependencies, capabilities, evidence, and gates.

## Architectural placement

```text
Graph node
  -> required capability
      -> executor / adapter
          -> AI model or agent
          -> application code
          -> deterministic workflow
          -> infrastructure tool
```

The graph cares about the capability and evidence, not the vendor.

## Technology-specific knowledge

Technology-specific procedures belong outside the execution kernel:

- reusable procedure -> `skills/`;
- runtime/integration binding -> consuming repository adapter;
- coding-agent instruction projection -> `graph_harness.providers`;
- application-specific implementation -> consuming repository.

UiPath is one possible deterministic-workflow or coded-agent technology. If a project uses it, UiPath-specific lifecycle knowledge should be packaged as an optional skill or adapter. A project that has never used RPA should not load, install, or depend on UiPath merely to use Graph Harness SDLC.

## Evidence remains consistent

Whether a node is executed by an LLM, Python code, a CI job, or a deterministic workflow, completion should still be grounded in evidence:

```text
execution
  -> artifact/result
  -> evidence record
  -> gate evaluation
  -> state transition
```

This is the stable abstraction. Executor technology remains replaceable.
