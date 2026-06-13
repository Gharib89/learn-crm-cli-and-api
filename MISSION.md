# Mission: Apply D365 CE customizations with the crm CLI + Claude Code

## Why
Shift Dynamics 365 Customer Engagement customization work from GUI/SOAP clicking to a
repeatable, reviewable **agentic workflow** — Claude Code driving the `crm` CLI. The learner
is a D365 beginner who wants to take a real customization requirement and implement it
end-to-end through the CLI, learning the D365 platform itself along the way.

## Success looks like
- Given a real requirement ("add a custom table with these columns, a 1:N to account, inside a
  solution, plus a plug-in step"), drive it end-to-end with Claude Code + the `crm` CLI: pick
  the right command group, choose `apply -f` vs imperative verbs, preview with `--dry-run`,
  verify via the `--json` envelope.
- Explain the D365 customization surface and, for any requirement, judge **what is automatable**
  via the `crm` CLI / Dataverse Web API and what is not.
- Handle the on-prem (NTLM, v9.1) vs cloud (OAuth, v9.2) split correctly.
- Recognize when a failure is a **tool defect** (vs user error) and file a high-quality issue
  upstream to `Gharib89/crm`.

## Constraints
- **Pure beginner in D365 CE** — build the platform mental model *before* CLI mechanics in each
  milestone.
- Two **mutate-safe dev orgs**: `agent-cloud` (active, primary; OAuth, v9.2) and `agent-on-prem`
  (VPN-gated; NTLM, v9.1). Destructive practice allowed on both. (See `NOTES.md`.)
- `crm` v3.9.0 already installed (WSL2; secrets stored as `0600` plaintext — no keyring).
- Lessons cite trusted sources (`RESOURCES.md`); never lean on the agent's parametric knowledge.

## Out of scope
- Contributing code / PRs to the crm repo (we file issues, not fixes) — true even in M11: the goal
  there is *understanding* the codebase, not upstreaming changes.
- GUI-only / non-API-automatable customizations, beyond *recognizing* them as such.

## Appendix track — M11 "Under the Hood" (added 2026-06-13)
Codebase study is **no longer globally out of scope** — it gets its own optional milestone, **M11**,
sitting after the M10 capstone. Full deep-dive depth: package architecture, request handling,
enrichment, control flow, how the code is structured (contributor-level *understanding*, not PRs).
Within the M01–M10 spine, codebase detail still stays on-demand / high-level — M11 is where the
deep-dive lives. Source of truth: <https://github.com/Gharib89/crm> (read directly, cite file:line).
