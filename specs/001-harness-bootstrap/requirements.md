# 001-harness-bootstrap Requirements

## Summary

Create the initial reusable `harness-sdlc` structure for spec-driven agentic delivery.

The feature establishes repository instructions, feature tracking, command contracts, agent role definitions, docs, templates, progress records, and validation.

## Mode

MVP

This bootstrap feature creates the harness foundation. It does not implement a sample application.

## Acceptance Criteria

- [x] Repository includes `AGENTS.md`, `RTK.md`, `CLAUDE.md`, `README.md`, `feature_list.json`, and `init.sh`.
- [x] Repository includes OpenCode command files for the required workflow commands.
- [x] Every OpenCode command includes required headings.
- [x] Every operational command defines file read/touch/must-not-touch boundaries.
- [x] Repository includes Claude agent role files.
- [x] Repository includes docs for methodology, modes, production readiness, Context7 policy, specs, verification, and conventions.
- [x] Repository includes docs for quality gates, security model, database change policy, token economy, loop engineering, release readiness, human-in-the-loop, roadmap design, anti-patterns, and decision records.
- [x] Repository includes ADRs for lifecycle, modes, approval, and SHIP production review decisions.
- [x] Repository includes reusable skills for spec authoring, production readiness, security, database migration review, i18n/accessibility, prompt contract review, and test strategy.
- [x] Repository includes feature and prompt templates.
- [x] Repository includes review templates for MVP, SHIP, production, security, and database review.
- [x] Repository includes portable examples for feature lists, specs, and progress files.
- [x] Repository includes progress files.
- [x] README includes workflow diagrams and an ASCII mascot to explain the harness model.
- [x] Feature list includes the seven initial harness features.
- [x] `001-harness-bootstrap` is set to `spec_ready`.
- [x] `./init.sh` validates the harness structure.

## Non-Goals

- Do not build a sample application.
- Do not implement Feature 1 beyond the harness bootstrap files.
- Do not add package managers, dependencies, or lockfiles.
- Do not configure deployment.
- Do not add a custom CLI, dashboard, database, or agent runtime.

## i18n

This feature does not create a user-facing application surface.

Future user-facing features must check:

- English copy
- Spanish copy
- layout resilience for both languages
- validation and error messages
- empty states
- accessibility labels

## MVP Criteria

- Initial harness files exist.
- Initial docs and templates exist.
- Validation script passes.
- The first feature is ready for human approval.

## SHIP Criteria

Not required for this MVP bootstrap, but the repository must document SHIP criteria for later features.
