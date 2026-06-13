# learn-crm-cli-and-api — Learning Workspace

A `/teach` workspace for mastering the `crm` CLI (github.com/Gharib89/crm) and the
Dynamics 365 CE Dataverse Web API. This glossary covers **only** terms specific to running
the learning process here; it defers to upstream for all D365 / crm domain language.

## Language

### Item routing

**Tool defect**:
A bug or missing capability in the `crm` CLI, surfaced while practising. Filed **upstream**
on `Gharib89/crm`, never in this repo. Offered to the user first, never filed silently.
_Avoid_: bug, issue (ambiguous — could mean a backlog item).

**Learning insight**:
A non-obvious thing now understood about the `crm` CLI or D365. Captured in
`learning-records/` as understanding — never a task to do.
_Avoid_: note, finding, lesson-learned.

**Learning backlog item**:
Something to learn, practise, or build next. The **only** kind of item that lives in this
repo's GitHub issues.
_Avoid_: todo, task, ticket.

## Deferred vocabulary

This repo does not redefine terms owned elsewhere — adopt them as-is:

- **D365 / crm domain language** (entity set, FetchXML, solution, lookup, emit envelope,
  operational failure, dry-run preview, …) → authoritative in the crm repo's `CONTEXT.md`
  and `D365.md`, plus the crm skill's `reference/*.md`.
- **Learning units** (mission, lesson, learning record, reference doc) → defined by the
  `/teach` skill.

Note: `/teach` maintains its own `GLOSSARY.md` — the **learner's** growing record of D365/crm
terms they have demonstrably learned, in their own words. It *adopts* upstream terms and is
evidence of understanding; it does not compete with this file. This `CONTEXT.md` governs the
**workspace contract**; `GLOSSARY.md` records **learned domain vocabulary**.
