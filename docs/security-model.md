# Security Model

SHIP mode requires explicit security review before closure.

## Secrets

- Never print secrets in logs, progress files, specs, reviews, or examples.
- Never commit `.env` files.
- Redact tokens, session values, API keys, private URLs, and credentials.

## Environment Variables

- New environment variables require human approval.
- Specs must document name, purpose, runtime scope, and whether a value is secret.
- Reviews must verify that secrets are not exposed to client code or logs.

## Auth And Session Boundaries

- Identify the authenticated actor.
- Validate authorization before reads and writes.
- Do not trust client-provided identity, role, tenant, or ownership fields.
- Include permission/visibility boundary tests for SHIP mode.

## Input Validation

- Validate user input at trust boundaries.
- Treat URL params, request bodies, query strings, headers, files, webhooks, and AI output as untrusted.
- Return safe errors that do not reveal internals.

## Private Data

- Minimize selected fields.
- Avoid raw private values in telemetry.
- Document PII/private data handling in SHIP specs.

## Dependency Approval

- No new dependency without explicit human approval.
- Review dependency purpose, license, maintenance, attack surface, and alternatives.

## Destructive Operations

Human approval is required before:

- deleting data
- running migrations
- running database write scripts
- removing files outside approved scope
- rotating or changing secrets

