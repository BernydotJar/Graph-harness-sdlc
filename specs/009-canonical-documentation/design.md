# Design — 009 Canonical Multilingual Documentation

## Information architecture

- `README.md`: canonical English product overview.
- `README.es.md`: Spanish translation.
- `README.pt.md`: Portuguese translation.
- `README.it.md`: Italian translation.
- `docs/README.md`: documentation landing page.
- `docs/concepts.md`: foundational concepts and vocabulary.
- `docs/runtime-architecture.md`: executable runtime contracts and persistence model.
- `docs/system-architecture.md`: separation of knowledge graph, execution graph, executors and gates.
- `docs/tutorials.md`: progressive paths for first validation, a feature run and recovery.
- `docs/reference.md`: pointers to schemas, CLI, states, events and gates.
- `docs/terminal-states.md`: program-level terminal states.

## State distinction

Node statuses remain runtime execution states:

```text
pending -> spec_ready -> approved -> ready -> running -> review -> done
                                      -> blocked
                                      -> repair_required
```

Program terminal states are derived completion outcomes over the whole graph:

```text
COMPLETED
PARTIAL_WITH_DOCUMENTED_BLOCKERS
SAFETY_STOP
```

No source enum or schema is changed by this documentation feature.

## Translation policy

English is authoritative. Translations are convenience documents and must link to the canonical README. Normative technical contracts remain English identifiers even inside translations.

## Verification

- Run `./init.sh`.
- Run an internal Markdown link checker for repository-relative links.
- Search for contradictory claims about canonical language and terminal states.
- Review generated diff for application-specific language.
