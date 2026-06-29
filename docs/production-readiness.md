# Production Readiness

SHIP mode requires production-grade review before closure.

## Security

- input validation
- authorization boundaries
- private data exposure risks
- abuse cases
- safe error handling
- secret handling

## Data Correctness

- exact schema-backed fields used
- read vs write behavior
- mutation boundaries
- consistency rules
- missing, stale, or incomplete data handling

## Performance

- bounded queries
- pagination or result limits
- no avoidable N+1 behavior
- minimal field selection
- indexing assumptions where relevant

## Failure Modes

- empty states
- invalid inputs
- missing records
- database/API failure behavior
- safe fallback behavior

## Observability Readiness

- future logging hook location
- what should be logged
- what must not be logged
- no secrets or raw sensitive values

## Testing

- happy path
- negative path
- invalid input
- empty state
- permission/visibility boundary
- i18n copy keys
- regression cases

## UX And Accessibility

- semantic structure
- labels
- keyboard support
- readable empty and error states
- responsive behavior

## Operations

- no unapproved schema changes
- no unapproved dependencies
- no database commands without explicit approval
- no secrets exposure
- release notes or review artifact for SHIP mode

