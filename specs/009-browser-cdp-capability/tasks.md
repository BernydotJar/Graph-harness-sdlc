# 009 — Browser CDP Capability Tasks

1. Add `graph_harness/browser_cdp.py` with typed errors, discovery client, target resolver, CDP session, and evidence sanitizer.
2. Export stable public types from `graph_harness.__init__`.
3. Add optional `browser-cdp` dependency extra to `pyproject.toml`; keep base dependencies empty.
4. Add `tests/test_browser_cdp.py` covering preflight, malformed/unavailable discovery, target filtering/matching, ambiguity, session timeout/protocol behavior, and redaction.
5. Document setup/security boundaries in README and RTK.
6. Update feature/progress records.
7. Run `./init.sh`, unit tests, compileall, and package install/import checks.
8. Critic/red-team the evidence sanitizer and ambiguous target handling.
9. Fix findings, independently re-run verification, commit, and publish a feature branch/PR without merging until review.
