# Working Notes

## Starting state (2026-06-13)

- `crm` **v3.9.0** installed (WSL2 Linux). Secrets stored as `0600` plaintext (no keyring on WSL).
- Two profiles configured, **both mutate-safe dev orgs**:
  - **`agent-cloud`** (ACTIVE — primary target): `https://orgexample.crm.dynamics.com` — OAuth,
    v9.2, publisher prefix `itworx`. Always reachable.
  - **`agent-on-prem`** (secondary — VPN-gated): `http://crm.contoso.local/Contoso` — NTLM,
    caps at v9.1, default solution `CRMWorx`, publisher prefix `cwx`.
- **Practice policy:** cloud-first for all lessons; on-prem only for the on-prem-only differences
  (milestone 9) and when on VPN.

## Teaching preferences

- Pure D365 **beginner**: build the platform mental model BEFORE CLI mechanics in each milestone.
- Always invoke `crm` with `--json` (the agent contract) and preview mutations with `--dry-run`
  before committing them.
- Cite trusted sources in every lesson (`RESOURCES.md`). Never parametric.
- Codebase track is high-level / on-demand only (see `MISSION.md` → Out of scope).
- **Author lesson HTML in the itWorx/Roboto site skin** (colors + fonts mirror the crm docs
  site): link `../assets/site.css` (last in `<head>`), use Roboto / Roboto Mono. Every lesson
  carries a `#lesson-meta` JSON block; the navbar is build-injected — never hand-add it. Build
  + preview with `python scripts/build.py` → `_site/`. Published lessons use the **example env**
  (`https://orgexample.crm.dynamics.com`, `http://crm.contoso.local/Contoso`), never the real
  org URL/host — live `/teach` still runs against the real orgs. (pref updated 2026-06-13;
  supersedes the earlier frontend-design/distinctive-aesthetic note.)
- **Open lessons in Windows Chrome**, not `xdg-open`. WSL → convert with `wslpath -w` and
  launch `chrome.exe`. (pref, 2026-06-13)

## M01 lesson sequence (decided 2026-06-13)

Profiles are the prerequisite to connecting, so within M01:
- **L01** — install, configure & the **profile lifecycle** (`add`/`list`/`use`/`edit`/
  `set-password`/`rm`; auth-scheme inference; secret storage). `lessons/0001-install-configure-profiles.html`
- **L02** — the **WhoAmI handshake** (confirm which live org answers + identity).
  `lessons/0002-the-whoami-handshake.html`
- **L03** — the `{ok, data, meta}` envelope + exit codes 0/1/2 (operational failure vs
  usage error; `meta` diagnostic fields). `lessons/0003-the-envelope-and-exit-codes.html`
- **L04** — `--dry-run`: previewing a write before it lands ("no writes, not no traffic";
  read `method`/`url`/`body`; pairs with `--validate`). `lessons/0004-dry-run-preview-the-write.html`
- **L05** — first real write: full safe-write loop (validate+dry-run → create → get →
  delete). Live create→get→delete round-trip captured on agent-cloud, then deleted (org
  left clean). `lessons/0005-your-first-real-write.html`
- **L06** — read it back: `entity get` (by GUID) + `query odata` (`--select`/`--filter`/
  `--top`) + `query count` (logical-name + cached gotcha). `lessons/0006-read-it-back-get-and-query.html`
- **L07** — the command surface: `--help` (3 levels) + `crm describe`; group/verb/flag tree.
  Closes M01. `lessons/0007-the-command-surface.html`

**✅ M01 COMPLETE — 7 lessons** (locked + batched 2026-06-13). Spine: profiles → whoami →
envelope → dry-run → create → read → discover. (Update/delete shown in passing — L04 PATCH
preview, L05 delete, L07 help — not their own lessons; revisit as M01.5 if user wants
dedicated CRUD-write drills.)

## M02 lesson sequence (started 2026-06-15)

Milestone: **Records & queries** (issue #2). "Done when": create→read→update→delete a contact
end-to-end + one OData + one FetchXML query. M01 already covered create/read/delete mechanically,
so M02 = the **record mental model first**, then the not-yet-taught verbs (update, deeper query,
FetchXML).

- **L01** — **Anatomy of a Record** (the GUI→API mapping). `lessons/0014-anatomy-of-a-record.html`.
  One skill: read a record's JSON and map every field back to the form. Covers entity-set vs
  logical name (formalizes L06's count trap), the four field shapes (PK GUID · plain/datetime ·
  option-set code+FormattedValue · lookup `_x_value`+3 annotations), and annotated vs `--minimal`
  (form view vs storage view). **Shipped + built 2026-06-15.** Mission rule honored: platform
  mental model before CLI mechanics.
- **L02** — **Update a Record** (`entity update` PATCH). `lessons/0015-update-a-record.html`.
  One skill: change a record safely via PATCH — scalar + option-set (by code) + lookup (by
  GUID+table). Covers PATCH-is-partial/silent, `If-Match:*` default (update-only) vs `--allow-create`,
  the three write shapes, the `set-lookup`/`clear-lookup` verbs, and the full live loop. **Shipped +
  built 2026-06-15.** Verified by a real reversible round-trip on seed contact Sara Mitchell
  (jobtitle, gendercode 2→1, parentcustomerid→account bind), org left clean.
- **L03** — **Querying Deeper: OData $filter** (`lessons/0016-querying-deeper-odata.html`).
  Filter sets on stored values (option-set code, lookup `_x_value` GUID), `--orderby`/`--count`,
  `--top` vs `--page-size`/`meta.next_link` (5000-row page cap). **Shipped + built 2026-06-15.**
- **L04** — **FetchXML: the other query language** (`lessons/0017-fetchxml-query.html`).
  `query fetchxml --xml/--file`; the aggregate/groupby superpower OData lacks; OData-vs-FetchXML
  decision; `query saved`/`user` run views by GUID. **Shipped + built 2026-06-15.**

**✅ M02 COMPLETE — 4 lessons** (L01–L04, lessons 0014–0017; shipped 2026-06-15). Spine: anatomy →
update → query-deeper → fetchxml. Milestone "Done when" satisfied across M01+M02: create (M01 L05),
read (M01 L06), update (M02 L02), delete (M01 L05), one OData (L03) + one FetchXML (L04).

### ⚠️ Drift to fix: M01 L06 query result shape

L03 live-verified that **v3.12.6 `query odata` returns `data` as a bare array** (unwraps OData's
`value`); `meta` carries `entity_set`/`count`/`next_link`. The older **M01 L06** lesson (and its
quiz) shows `data.value` — the pre-3.12 shape. Not fixed (out of this task's scope); flag for a
surgical L06 fix-up pass. L03 §01 calls out the current shape explicitly so learners aren't lost.

### L03/L04 live-CLI facts (read-only, all captured from agent-cloud)

- `query odata` flags: `--select/--filter/--top/--orderby/--expand/--count/--page-size/--annotations/
  --minimal`. NO inline `?`/`$` (rejected client-side); options via flags only. `--count` →
  `meta.count` (exact, filtered). `--page-size N` → `meta.next_link` (@odata.nextLink + skiptoken).
- Filter on code: `gendercode eq 1`. On lookup: `_ownerid_value eq <guid>` (bare GUID, no quotes).
- `query fetchxml --xml '<fetch>…'` or `--file`. `<entity name="contact">` = logical name → crm
  resolves to entity-set via 1 metadata GET (or pass set positionally). Aggregate verified:
  `<fetch aggregate="true">` + `groupby="true"` + `aggregate="count"` + `alias` → `[{num:3,gender:2},
  {num:2,gender:1}]` (3 Female / 2 Male in agent-cloud seed). Also `query saved`/`user` (views by GUID).

## crm v4.7.0 upgrade — full re-verification + lesson pass (2026-06-17)

CLI bumped **3.12.6 → 4.7.0** (major). Re-verified everything the lessons touch against the
installed binary (per the CLAUDE.md evolving-CLI policy). **Drift found — two output changes:**

1. **`@odata.context` and `@odata.etag` dropped** from `entity get`, `entity create`, `whoami`,
   and `query` output (confirmed absent even with `--full`). Replaced by `_entity_id` +
   `_entity_id_url` (the url carries host + `/api/data/v9.2/` + entity-set).
2. **New `connection test`** verb → reports `api_base` + `api_version` as first-class fields;
   also `connection status` (no network) and `connection doctor`. This is now the way to confirm
   host/version (whoami is identity-GUIDs-only).

**Unchanged (re-verified):** field-level annotations (FormattedValue / lookuplogicalname /
associatednavigationproperty) with `--annotations`; `query odata` bare-`data` array + `--count`
+ `--page-size`/`next_link`; `entity update` PATCH/partial/silent/`If-Match:*` + flags; lookup
verbs (`set-lookup`/`clear-lookup`); FetchXML aggregate. New `entity get --full` flag (human-mode
nulls).

**Lessons updated (full pass, 7):** 0002 (whoami → pivot host/version to `connection test`),
0003 (envelope examples: drop context; query → bare `data` array), 0005 (create: drop context/etag),
0006 (get: drop context/etag; etag bullet reframed — concept kept, CLI-no-longer-prints note),
0010 (M11 enrichment: drop `@odata.etag` "API control" example), 0014 (M02 L01: §03 JSON +
rule-of-thumb → `_entity_id_url` + `--minimal` prose), 0015 (M02 L02: `--if-match` note + ask).
Etag decision: **keep the optimistic-concurrency concept**, note v4.7.0 doesn't surface the value,
teach `--if-match "*"` as the practical guard. GLOSSARY: `@odata.context`/`@odata.etag` reframed +
new `connection test` entry. Footers stamped "verified against crm v4.7.0 on 2026-06-17".

### Live-CLI facts caught while authoring L01 (v3.12.6 — note: CLI bumped from 3.9.x)

- `crm --version` now reports **3.12.6** (was 3.9.0/3.9.1 in earlier notes).
- **`entity get` is annotated by DEFAULT.** `--annotations / --no-annotations` toggles; default ON.
  `--minimal` drops every `@`-key (etag, FormattedValues, lookup annotations) but keeps business
  fields, `_*_value` GUIDs, primary id. Also new on `entity get`: `--expand`, `--expect ATTR=VALUE`.
- Live anatomy captured from agent-cloud contact "Sara Mitchell": `gendercode 2 → "Female"`,
  `statecode 0`/`statuscode 1 → "Active"`, `_ownerid_value` → `lookuplogicalname: "systemuser"`,
  `associatednavigationproperty: "ownerid"`. Real host `orgd080ee1e…` + owner id/name **scrubbed**
  to the example env in the published lesson (privacy rule).
- Seed contacts in agent-cloud use the same placeholder-looking GUIDs as the L06 lesson
  (`a1b2c3d4-…`) — convenient, reuse them. No contacts currently have `_parentcustomerid_value`
  set; used the always-populated `ownerid` lookup to demo the foreign-key shape instead.

L02 (`entity update`) facts, all server-confirmed by the live round-trip:
- `entity update` = PATCH, **silent by default** (returns only `_entity_id`); `--return-record`
  asks for the row. Sends **`If-Match: "*"` by default** → update-only (blocks accidental upsert);
  `--allow-create` drops the header, or use the `entity upsert` verb.
- Lookup write: read-only `_x_value` can't be set; use nav-property `@odata.bind`:
  `"parentcustomerid_account@odata.bind":"/accounts(<id>)"`. Server echoed
  `associatednavigationproperty: parentcustomerid_account`, `lookuplogicalname: account` — bind
  syntax **confirmed** (dry-run alone wouldn't prove this; the real PATCH did).
- crm has dedicated lookup verbs: `entity set-lookup ES ID NAV RELATED_SET RELATED_ID` and
  `entity clear-lookup ES ID NAV` (→ `{cleared:true}`, DELETE /$ref). Also `entity associate`,
  `disassociate`, `clone`, `children`, `upsert` exist (seen in `crm entity --help`).
- Available accounts in agent-cloud for lookup demos: ITWorx, Reliance, Contoso Ltd. Published
  lesson scrubs the bound account to "Contoso Ltd" + placeholder guid (example-env convention).
- Write grant: user re-created `.claude/settings.local.json` (`allow: ["Bash(crm:*)"]`) this
  session so real writes run; still gitignored, agent still can't self-write the rule.

## M11 (appendix) — "Under the Hood: how crm works" (decided 2026-06-13)

User pivoted: wants a **dedicated milestone on the crm codebase itself** — architecture, structure,
request handling, enrichment. Reverses the original MISSION "codebase out of scope" note (now
amended). Decisions:
- **Slot:** appendix **M11**, milestone num 11 → sorts after the M10 capstone; optional deep-dive.
  M01–M10 spine untouched. GitHub issue #11 opened (learning-milestone label).
- **Depth:** **full codebase deep-dive** — module design, classes, control flow, how you'd modify
  it (contributor-level *understanding*; mission still = file issues, not PRs).
- **Source of truth:** github.com/Gharib89/crm, cloned at `~/wip/projects/crm` (CLAUDE.local.md).
  Cite file:line + GitHub blob URLs.
- **Planned spine:** L01 architecture map (argv→command→core→backend) · L02 request layer
  (auth/headers/session, `utils/d365_backend.py`) · L03 enrichment vs raw API (FormattedValue/
  lookuplogicalname annotations, `--annotations`/`--minimal`) · **L04 the architecture, drawn**
  (3 Mermaid diagrams: package map, one-way dependency rule, request sequence — vendored
  `assets/mermaid.min.js`, shipped 2026-06-13) · L05 resilience (retry/backoff, paging
  `@odata.nextLink`, `$batch`, error classification — shipped 2026-06-13) · **L06 from source to
  issue** (capstone: localise via `connection doctor` + exit code, then file a fileable upstream
  issue — repro/envelope/env/layer/expected-vs-actual, org scrubbed — shipped 2026-06-13).
- **M11 COMPLETE** (L01–L06, lessons 0008–0013). Mission capstone (L06) ties the deep-dive to
  filing precise crm bug reports.
- **Diagrams = Mermaid, vendored.** Chosen over Excalidraw MCP (renders in chat / shares a URL —
  no embeddable file) and hand-authored inline SVG (no live edit). `assets/mermaid.min.js` is the
  UMD build (exposes `globalThis.mermaid`, self-contained, no chunk fetches). Lessons embed
  `<div class="mermaid">` + a local `<script src="../assets/mermaid.min.js">` — the same relative
  path works in raw `lessons/` AND built `_site/lessons/`, so diagrams render during live teaching
  too, and no `build.py` change is needed (`build.py` already copies `assets/` → `_site/`). The
  1 MB lib only loads on lessons that include the script.

## Live-CLI gotchas caught while authoring (v3.9.1)

- **`--validate` is a per-verb flag, NOT global.** `crm --json --validate --dry-run entity
  create …` → exit-2 "No such option". Correct: `… entity create … --data '…' --validate`.
  L04 was written with the wrong position from the skill doc and **corrected** after live
  test. Lesson: verb-specific flags go after the verb (reinforces L07). Always live-verify
  flag position, don't trust doc prose alone.
- **`query count` wants the logical name** (`contact`), not the set (`contacts`) — and is
  cached/approximate (read 0 while rows existed). Captured into L06.
- **Permission:** authoring real writes needs a user-side grant — auto-mode classifier
  denies both the live non-dry-run write AND the agent self-writing a `Bash(crm:*)` allow
  rule. User created `.claude/settings.local.json` themselves (via `! …`); then writes ran.

Rationale: a saved profile is just config; teach how to create/manage it before the
command that proves it works. (User correction — mechanic before confirmation.)

## Two glossaries — don't confuse them

- **`CONTEXT.md`** (root): thin *workspace-contract* glossary (item-routing terms). Defers to
  upstream for all D365 language.
- **`GLOSSARY.md`** (`/teach`, created lazily): the **learner's** growing D365/crm glossary —
  terms compressed in the user's own words as evidence of understanding. Adopts upstream terms,
  never invents.

## Item routing (ADR-0001)

Tool defect → upstream `Gharib89/crm`. · Learning insight → `learning-records/`. ·
Learning backlog → this repo's GitHub issues.
