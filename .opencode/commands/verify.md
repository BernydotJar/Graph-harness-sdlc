# verify

MODE:
Use the mode in `feature_list.json` when verifying a feature. Use harness mode when verifying repo structure.

FEATURE:
Use the named feature, active feature, or harness structure.

STATE:
No state changes unless a human explicitly asks to record verification.

SOURCE OF TRUTH:
- `feature_list.json`
- `docs/verification.md`
- `specs/<feature-id>/tasks.md`
- `init.sh`

FILES YOU MAY READ:
- `feature_list.json`
- `docs/**`
- `specs/**`
- `progress/**`
- files required by the spec verification plan

FILES YOU MAY TOUCH:
- `progress/current.md` only if recording verification was requested
- `progress/history.md` only if recording verification was requested

FILES YOU MUST NOT TOUCH:
- production source files
- test source files
- dependency manifests
- lockfiles
- environment files

DO:
- Run `./init.sh` for harness validation.
- Run feature verification commands from the approved spec.
- Capture command results.

DON'T:
- Fix failures during verification unless explicitly asked.
- Mark features done.
- Hide failed commands.

OUTPUT:
- Commands run
- Pass/fail result
- Relevant output summary
- Follow-up required

STOP:
Stop after reporting verification results.
