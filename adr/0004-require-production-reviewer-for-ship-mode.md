# 0004 Require Production Reviewer For SHIP Mode

Status: accepted

## Context

Passing tests does not prove production readiness.

## Decision

SHIP mode requires production review for security, data correctness, performance, failure modes, observability, testing, UX/accessibility, and operations.

## Consequences

- production risk is reviewed explicitly
- features may be rejected after functional tests pass
- review artifacts must document production evidence

