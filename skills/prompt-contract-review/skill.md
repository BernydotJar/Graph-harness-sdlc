# Prompt Contract Review Skill

Use this skill when editing command files, agent instructions, or operational prompts.

## Inputs

- `.opencode/commands/**`
- `AGENTS.md`
- `RTK.md`
- `CLAUDE.md`
- `docs/conventions.md`

## Checklist

- required command headings exist
- file read/touch/must-not-touch boundaries exist
- output and stop conditions are explicit
- no role is allowed to approve itself
- human approvals are preserved
- command scope matches lifecycle state

