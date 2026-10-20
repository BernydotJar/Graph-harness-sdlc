# Product acceptance: business-action proof, not E2E count

`graph-harness product-acceptance` is an additional **SHIP release gate** for a complete product capability. It is not a substitute for a typed execution graph, security tests, accessibility audits, or a customer sign-off.

A passing API test, one green browser journey, a loaded dashboard, or an HTTP 200 production route is **not** approval of an operational module.

## Four independent axes per customer action

| Axis | Required evidence |
| --- | --- |
| `implementation` | Passing assertion tied to the exact code revision; code-file existence alone is insufficient |
| `ui` | Authenticated persona actually clicks or performs the action; screenshots without interaction do not count |
| `journey` | Real provider/backing-service business outcome, with persisted state assertions for mutating actions; mocks and emulators can provide CI confidence but cannot be final client acceptance |
| `production` | The same exact source revision published, and the same persona/action exercised in production with external deployment attestation |

Every action belongs to a multi-action business workflow. Each required persona has a workflow. A separate independent, explicit **coverage review** must attest all critical actions and personas; the test author cannot serve as their own verifier. `NO_GO` is the safe default for absent, stale, unreviewed or incomplete evidence. Distinct action IDs cannot reuse the same evidence as a substitute for testing that action.

The input files are intentionally separate:

- `graph-harness.product-acceptance.v1` describes the canonical **critical customer actions**, personas, expected outcomes, workflows, mutation requirements, and evidence IDs. It should be reviewed with the Product Owner/BA and client before code acceptance.
- `graph-harness.product-evidence.v1` maps proof IDs to actual, non-empty artifacts with SHA-256, tested revision, real-versus-synthetic mode, asserted UI interactions, persisted effects, and a reviewer distinct from its producer.
- `--production-revision` must come from the authenticated deployment / runtime attestation, **not** from the source manifest itself. An unavailable production revision holds release, even if every local check is green.

```bash
python3 -m graph_harness product-acceptance \
  --manifest docs/enterprise/live-classroom-acceptance.json \
  --evidence evidence/live-classroom-acceptance/proofs.json \
  --repo-root . \
  --source-revision "$(git rev-parse HEAD)" \
  --production-revision "$DEPLOYMENT_ATTESTED_COMMIT" \
  --pretty
```

Exit `0` is GO; exit `2` means NO_GO or invalid input (reported on stderr). Source/current revisions must match all proofs as well as the observed production commit. Run this command in the **actual release promotion workflow**; it must not be bypassed by saying a test suite passed.

## Customer breadth examples

For LUMA synchronous training: organizer creates cohort and class, enrolls or invites an eligible learner; assigned instructor opens, shares screen, moderates and finishes the room; enrolled learner opens agenda, checks devices, joins, uses media/chat, reconnects, and has attendance recorded. Validate refund-based revocation and participant removal while already connected, without conflating attendance and mastery. Compare the current `main` implementation, reachable controls, recorded multi-person browser/provider journeys and **deployed** revision.

For I-DO agrochemical customer: request institution onboarding/approval, provision the first authorized administrator, configure tenant-specific catalog/pricing/inventory, place and fulfill an order, handle approvals, invoices and after-sale changes, verify unauthorized users cannot read other tenants. A loaded product screen or a successful narrow checkout does not certify the complete module. Its own BA must enumerate real, client-confirmed workflows and outcomes; this example **does not assert** these are all implemented or accepted today.

## Threats to evidence quality

- Screenshots without actual actions -> `ui` gate fails.
- Synthetic data can help reproduce a regression but not supply final real-client/provider proof.
- A one-action "journey" or missing persona -> coverage gate fails.
- Evidence for an older SHA -> stale; localized repair invalidates only affected actions and downstream release gate.
- UI that renders data without create/edit/approve/revoke/export paths where required -> unverified customer action and NO_GO.
- Production screenshot without matching runtime revision -> deployment gate fails.
- One proof ID reused to approve multiple actions -> action-specific gate fails.

The evaluator validates artifact hashes but cannot prove a human-created artifact is truthful or that a production SHA supplied by a caller is trustworthy. The release pipeline must fetch attestation from the deployment provider independently and retain reviewers' identity/access policy. Fraud-resistant signed attestations are a future extension; do not claim the JSON alone certifies production.
