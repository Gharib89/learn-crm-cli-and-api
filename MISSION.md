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
- Studying the `crm` CLI Python codebase for its own sake — kept **high-level / on-demand** only
  (to write better upstream bug reports, or explain surprising CLI behavior).
- Contributing code / PRs to the crm repo (we file issues, not fixes).
- GUI-only / non-API-automatable customizations, beyond *recognizing* them as such.
