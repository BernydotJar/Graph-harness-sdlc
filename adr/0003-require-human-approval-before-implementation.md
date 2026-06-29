# 0003 Require Human Approval Before Implementation

Status: accepted

## Context

Agents can overbuild, change scope, or implement assumptions when specs are treated as suggestions.

## Decision

Implementation begins only after explicit human approval moves a feature from `spec_ready` to `approved`.

## Consequences

- humans control scope
- implementation is easier to review
- missing approval becomes a hard stop

