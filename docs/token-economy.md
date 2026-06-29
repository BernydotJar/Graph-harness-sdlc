# Token Economy

The harness should reduce wasted context, not encourage larger prompts.

## Read Less First

Start from:

1. `feature_list.json`
2. active feature spec
3. command contract
4. directly relevant files

Do not read the whole repo by default.

## Ask For Context When

- requirements are ambiguous
- file ownership is unclear
- data contracts are missing
- multiple features overlap
- a command would exceed approved scope

## Do Not Ask For Context When

- the answer is in the active spec
- the change is markdown-only and local
- `init.sh` can validate the question
- a small targeted search can resolve it

## Use Summaries

Prefer concise summaries for:

- prior review findings
- large docs
- long command outputs
- repeated verification evidence

Keep exact output only when it affects a decision.

## Bound File Reads

Every operational command must define:

- FILES YOU MAY READ
- FILES YOU MAY TOUCH
- FILES YOU MUST NOT TOUCH

## Stop Early

Stop instead of spending tokens when:

- approval is missing
- scope changed
- verification cannot run
- required current docs are unavailable
- implementation requires an unapproved dependency or schema change

