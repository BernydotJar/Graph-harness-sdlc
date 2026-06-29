# 001-auth Requirements

## Summary

Add email sign-in for an example product.

## Mode

SHIP

## Acceptance Criteria

- [ ] User can request a sign-in link with a valid email.
- [ ] Invalid email input shows a safe validation error.
- [ ] Auth/session boundaries are enforced server-side.
- [ ] Private session values are not logged.
- [ ] English and Spanish copy exists.

## Non-Goals

- Password auth
- Social login
- User profile management

## SHIP Criteria

- security: validate input and protect session boundaries
- data correctness: use schema-backed user/session fields only
- performance: bound auth lookups
- failure modes: invalid email, expired link, service failure
- observability readiness: log event names only, no raw tokens
- testing: happy path, invalid input, expired link, permission boundary
- UX/accessibility: labeled form and readable errors
- operations: env vars documented and approved

