# Product Memory

This directory contains stable strategic context that helps agents understand where a product is going without granting implementation authority.

Product-memory documents:

- preserve product direction, architecture intent, repository boundaries, shared vocabulary, and safety constraints;
- may inform future features and specifications;
- must not bypass `feature_list.json`, approved specs, file boundaries, verification, or review;
- are subordinate to the harness source-of-truth order for executable work.

## Current memories

- [`campaign-os-north-star.md`](./campaign-os-north-star.md) — CampaignOS product thesis, virtual campaign-team operating model, War Room workflow, relationship between `harness-sdlc`, `OS-Electoral`, and `LA_muni_RAG`, SaaS direction, safety boundaries, and roadmap.

Rule:

> Product memory explains why and where. Approved specifications define what may be built now.
