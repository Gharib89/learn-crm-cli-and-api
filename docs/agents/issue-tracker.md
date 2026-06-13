# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.
This repo's remote is `Gharib89/learn-crm-cli-and-api`.

## Item routing (see ADR-0001)

This is a `/teach` learning workspace. Three kinds of item route to three places — **do not
file them all here**:

- **crm CLI tool defects / missing features** → file **upstream**:
  `gh issue create --repo Gharib89/crm --label needs-triage` (crm skill `feedback.md` flow).
  Offer first, never file silently.
- **Learning insights** (something now understood) → `learning-records/` (a `/teach` record).
- **Learning backlog** (what to learn / build next) → **this repo's GitHub issues** (the only
  thing that belongs here).

So when the `qa` skill surfaces a crm bug, it routes **upstream**; this repo's issues hold
only the learning backlog.

## When a skill says "publish to the issue tracker"

Create a GitHub issue **in this repo** — these are learning-backlog items only.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
