# Product Memory

This directory contains stable strategic context that helps agents understand where a product is going without granting implementation authority.

Product-memory documents:

- preserve product direction, architecture intent, repository boundaries, shared vocabulary, and safety constraints;
- may inform future features and specifications;
- must not bypass `feature_list.json`, approved specs, file boundaries, verification, or review;
- are subordinate to the harness source-of-truth order for executable work.

## Current memories

- [`campaign-os-north-star.md`](./campaign-os-north-star.md) — CampaignOS product thesis, virtual campaign-team operating model, War Room workflow, relationship between `harness-sdlc`, `OS-Electoral`, and `LA_muni_RAG`, SaaS direction, safety boundaries, and roadmap.
- [`premium-slate-ui-capability.md`](./premium-slate-ui-capability.md) — optional global design capability for obsidian-slate interfaces, interactive canvas patterns, circular view transitions, accessibility fallbacks, and portability rules.

## Related long-session assets

- [`../../templates/long-session/autonomous-implementation-goal.md`](../../templates/long-session/autonomous-implementation-goal.md) — reusable autonomous implementation contract.
- [`../../examples/campaign-os/C1-FRONT-002-long-session-goal.md`](../../examples/campaign-os/C1-FRONT-002-long-session-goal.md) — first CampaignOS goal draft for the Campaign Team Command Center.
- [`../../examples/campaign-os/C1-FRONT-002-premium-slate-ui-guidance.md`](../../examples/campaign-os/C1-FRONT-002-premium-slate-ui-guidance.md) — optional UI guidance for using `premium-slate-ui` during the approved implementation of C1-FRONT-002.

Rule:

> Product memory explains why and where. Approved specifications define what may be built now.
