# crm CLI + D365 CE Web API Resources

Trusted sources for this workspace. Explainers draw from here, not parametric guesses.

## Knowledge

### The crm CLI — the tool we're mastering

- [crm repo — github.com/Gharib89/crm](https://github.com/Gharib89/crm)
  Source of truth for the CLI. Use for: command behavior, ADRs (`docs/adr/`), `CONTEXT.md`
  (CLI contract), `D365.md` (on-prem SOP), and the on-demand high-level codebase track.
- [crm docs site — crm-cli-docs.pages.dev](https://crm-cli-docs.pages.dev/)
  Generated docs: install, configure, per-group how-tos, full CLI reference. Use for: looking
  up exact flags and workflows. (Or run `crm describe <group>` / `crm <group> --help` locally.)
- [llms-full.txt](https://crm-cli-docs.pages.dev/llms-full.txt) · [llms.txt index](https://crm-cli-docs.pages.dev/llms.txt)
  Whole docs site in one fetch. Use for: grounding a lesson in the CLI's own docs in one shot.
- crm agent skill — `~/.claude/skills/crm/` (`SKILL.md` + `reference/*.md`: records, metadata,
  authoring, solutions, customizations, automation, security, troubleshooting, feedback).
  Use for: the distilled workflow + gotchas per command domain, and the upstream-issue flow.

### Dynamics 365 CE / Dataverse Web API — the platform

- [Use the Dataverse Web API (overview)](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/overview)
  Use for: the canonical Web API entry point (applies to on-prem too).
- [Perform operations by using the Web API](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/perform-operations-web-api)
  Use for: how to compose requests, query, manage rows, batch. Explicitly covers D365 CE on-prem.
- [Create](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/create-entity-web-api) ·
  [Retrieve](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/retrieve-entity-using-web-api) ·
  [Update & delete](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/update-delete-entities-using-web-api) rows
  Use for: the exact HTTP semantics behind `crm entity create/get/update/delete`.
- [Query data using the Web API](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/query/overview) ·
  [Query data using FetchXML](https://learn.microsoft.com/power-apps/developer/data-platform/fetchxml/overview)
  Use for: `$select`/`$filter`/`$expand` and FetchXML behind `crm query`.
- [Use the Dynamics 365 CE (on-premises) Web API — op-9-1](https://learn.microsoft.com/dynamics365/customerengagement/on-premises/developer/use-microsoft-dynamics-365-web-api?view=op-9-1) ·
  [Authenticate (on-prem)](https://learn.microsoft.com/dynamics365/customerengagement/on-premises/developer/webapi/authenticate-web-api?view=op-9-1)
  Use for: the **on-prem-specific** v9.1 surface and NTLM/IFD auth (milestone 9).
- [Web API versions](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/web-api-versions)
  Use for: the load-bearing M09 fact — v9.0/9.1/9.2 are **behaviorally identical**; the version is a
  path pin, not a feature gate (so the on-prem v9.1 cap is a routing/build difference, not lost API behavior).
- [Authenticate with Dataverse web services](https://learn.microsoft.com/power-apps/developer/data-platform/authentication) ·
  [Authenticate users in D365 CE (on-premises)](https://learn.microsoft.com/dynamics365/customerengagement/on-premises/developer/authenticate-users?view=op-9-1)
  Use for: the OAuth-online vs AD/NTLM-on-prem auth split (M09 L01); the realms behind a 401/403.
- [Service protection API limits](https://learn.microsoft.com/power-apps/developer/data-platform/api-limits) ·
  [API limits overview](https://learn.microsoft.com/power-apps/maker/data-platform/api-limits-overview#service-protection-limits)
  Use for: the cloud-only 429 + `Retry-After` throttling model (5-min window) the `doctor` rate_limit check reflects (M09 L03).
- [Optimize performance for bulk operations](https://learn.microsoft.com/power-apps/developer/data-platform/optimize-performance-create-update#bulk-operation-apis) ·
  [Execute $batch operations](https://learn.microsoft.com/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api)
  Use for: `CreateMultiple`/`UpdateMultiple` availability (cloud-only / per-table) vs the universal OData `$batch` path (M09 L02).
- [Calculated and rollup attributes (D365 CE)](https://learn.microsoft.com/dynamics365/customerengagement/on-premises/developer/calculated-and-rollup-attributes?view=op-9-1)
  Use for: the headline **GUI-only** example (M10 L02/L04) — rollups aggregate over **1:N only** (not N:N),
  can't reference another rollup, recalc on **async scheduled jobs**, max 10/table & 100/org. Grounds why
  `metadata add-attribute` has no `rollup` kind.
- [ALM with Microsoft Power Platform](https://learn.microsoft.com/power-platform/alm/)
  Use for: the dev→test→prod promotion discipline (M10 L05) — build unmanaged in dev, ship **managed**
  downstream, solution layering, and the managed-vs-unmanaged rule the version ceiling enforces.
- [`gh issue create` manual](https://cli.github.com/manual/gh_issue_create)
  Use for: filing an upstream defect from the shell (M10 L06) — `--repo`, `--label`, `--body-file` flags
  behind the `Gharib89/crm` issue recipe in `reference/feedback.md`.

## Wisdom (Communities)

- [Power Platform / Dataverse community forums](https://community.powerplatform.com/)
  Use for: customization how-tos, plugin/workflow troubleshooting from practitioners.
- [Microsoft Q&A — Dynamics 365](https://learn.microsoft.com/answers/tags/365/dynamics-365)
  Use for: getting specific platform questions answered by MS + MVPs.
- [Stack Overflow — `dynamics-365` / `dynamics-crm`](https://stackoverflow.com/questions/tagged/dynamics-365)
  Use for: Web API request-shape and OData/FetchXML edge cases.
- [r/Dynamics365](https://reddit.com/r/Dynamics365) · [r/PowerPlatform](https://reddit.com/r/PowerPlatform)
  Use for: real-world consultant perspective, what's automatable, tooling debates.

## Gaps

- No single beginner-grade "D365 customization surface" map tailored to the CLI yet — the early
  milestones will build one (in `GLOSSARY.md` + a `reference/` cheat sheet).
