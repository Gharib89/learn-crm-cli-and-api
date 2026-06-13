# Teaching workspace with three-way item routing

This repo is primarily a `/teach` learning workspace for mastering the `crm` CLI
(github.com/Gharib89/crm) and the Dynamics 365 CE Dataverse Web API — **not** a home
for real D365 customization work. A hybrid "lab" (equal-weight engineering repo + learning)
was the alternative; rejected to keep the repo's purpose unambiguous. The matt-pocock
engineering skills are kept as secondary tooling for when learning turns into real building.

Three kinds of item surface while learning, and each routes to a distinct destination —
any overlap is a smell:

- **Tool defect / missing feature** in the crm CLI → filed **upstream** on `Gharib89/crm`
  (`gh issue create --repo Gharib89/crm --label needs-triage`, the crm skill's `feedback.md`
  flow). Never filed in this repo.
- **Learning insight** (a non-obvious thing now understood) → `learning-records/`
  (a `/teach` record — captures understanding, never a task).
- **Learning backlog item** (what to learn / practice / build next) → **this repo's GitHub
  issues**, where `triage`/`to-issues` groom it and an AFK agent can pick up
  `ready-for-agent` lesson-build tasks.

Net rule: **bugs go up, insights go to records, next-steps go to local issues.**

Consequence: `docs/agents/issue-tracker.md` is amended so the `qa`/feedback path sends tool
defects upstream, reserving this repo's GitHub issues for the learning backlog.
