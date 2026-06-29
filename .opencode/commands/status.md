# status

MODE:
Read-only.

FEATURE:
All features, with emphasis on the active feature if one exists.

STATE:
No state changes.

SOURCE OF TRUTH:
- `feature_list.json`
- `progress/current.md`
- `progress/history.md`
- `specs/**`

FILES YOU MAY READ:
- `feature_list.json`
- `progress/**`
- `specs/**`
- `docs/**`

FILES YOU MAY TOUCH:
- none

FILES YOU MUST NOT TOUCH:
- all files

DO:
- Summarize feature states.
- Identify the next valid command.
- Report active feature count.
- Report blockers.

DON'T:
- Edit files.
- Change status.
- Infer approval.

OUTPUT:
- Current feature table
- Active feature
- Next recommended command
- Blockers

STOP:
Stop after reporting status.
