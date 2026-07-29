# Reasoning Modes and Human Evaluation Cadence

Graph Harness SDLC does not expose or require a model's private chain of thought.

Instead, it controls the level of **observable reasoning artifacts** produced during execution: decisions, alternatives, tradeoffs, risks, acceptance criteria, verification results, and evidence.

## Reasoning modes

```yaml
reasoning:
  mode: minimal
```

Supported modes:

```yaml
reasoning:
  mode: minimal      # decisions and evidence only

reasoning:
  mode: standard     # decisions, alternatives, and concise justification

reasoning:
  mode: engineering  # ADRs, tradeoffs, acceptance criteria, and risks

reasoning:
  mode: audit        # maximum observable traceability for compliance
```

### Minimal

Use for low-risk, well-specified, repetitive work.

Required observable artifacts:

- decision;
- result;
- verification status;
- evidence reference.

### Standard

Use as the default for normal product development.

Required observable artifacts:

- decision;
- concise rationale;
- meaningful alternatives considered;
- verification status;
- evidence reference.

### Engineering

Use for architectural, security-sensitive, data-sensitive, or production-critical work.

Required observable artifacts:

- decision record;
- assumptions;
- alternatives and tradeoffs;
- risks and mitigations;
- acceptance criteria;
- verification strategy;
- evidence;
- remaining work or blockers.

### Audit

Use when regulated delivery, formal governance, or compliance evidence is required.

It includes the engineering artifacts plus:

- timestamps;
- actor or executor identity;
- node and revision identifiers;
- artifact hashes;
- evaluator identity;
- gate outcomes;
- approval references;
- CI and release evidence;
- complete decision provenance.

`audit` means maximum **observable traceability**. It does not mean revealing hidden model reasoning.

## Harness before graph

A project does not always begin with a stable execution graph.

When requirements, evaluation criteria, product behavior, or risk boundaries are still uncertain, Graph Harness SDLC may begin in a **harness-first phase**.

```text
User intent
    -> Harness calibration
    -> Frequent human evaluation
    -> Stable criteria and evidence contracts
    -> Executable graph
    -> Autonomous graph execution
```

The harness-first phase is used to discover and stabilize:

- expected behavior;
- failure classes;
- evaluator rubrics;
- acceptable evidence;
- safety boundaries;
- domain-specific quality thresholds;
- which decisions must remain human-gated.

During this phase, human evaluations are intentionally stricter and more frequent. The purpose is not permanent manual supervision. The purpose is to produce reliable contracts that can later become graph gates.

## Human evaluation cadence

```yaml
governance:
  human_eval_frequency: frequent
```

Supported values:

```yaml
governance:
  human_eval_frequency: frequent   # evaluate most meaningful increments

governance:
  human_eval_frequency: gated      # evaluate only configured risk or release gates

governance:
  human_eval_frequency: exception  # evaluate only ambiguity, failure, or escalation
```

### Frequent

Recommended during harness calibration, early product discovery, high-risk changes, or weak automated evaluation coverage.

Human evaluation may occur after:

- requirement interpretation;
- specification creation;
- first implementation;
- critic or red-team findings;
- repair;
- release candidate generation.

### Gated

Recommended after evaluation contracts are stable.

Human evaluation occurs only at explicit graph gates, such as:

- architecture approval;
- security approval;
- production infrastructure approval;
- data migration approval;
- release approval.

### Exception

Recommended for mature, low-risk execution graphs with strong automated gates.

Human evaluation is requested only when:

- evidence is insufficient;
- evaluators disagree;
- a node repeatedly fails;
- execution crosses a configured risk threshold;
- an external effect requires authorization.

## Transition rule

A repository may move from harness-first execution to graph execution when:

1. acceptance criteria are explicit;
2. evaluator rubrics are repeatable;
3. required evidence is defined;
4. failure and repair paths are known;
5. human-only decisions are represented as gates;
6. the graph can determine `READY`, `BLOCKED`, `REPAIR_REQUIRED`, and `DONE` without relying on an informal conversation.

The transition is progressive. Some subgraphs may operate autonomously while uncertain or high-risk subgraphs remain under frequent human evaluation.

## Recommended defaults

```yaml
execution:
  mode: ship

reasoning:
  mode: standard

governance:
  human_eval_frequency: gated
```

For a new or poorly specified product:

```yaml
execution:
  mode: harness-first

reasoning:
  mode: engineering

governance:
  human_eval_frequency: frequent
```

For a mature, low-risk repository:

```yaml
execution:
  mode: graph

reasoning:
  mode: minimal

governance:
  human_eval_frequency: exception
```
