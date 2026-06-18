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

## M03 lesson sequence (shipped 2026-06-17)

Milestone: **Metadata model (read)** (issue #3). "Done when": describe a table's columns +
relationships and explain logical-vs-set naming. Read-only on cloud. All five live-verified
against **crm v4.12.0** (CLI bumped 4.7.0 → 4.12.0 since last session — see version note below).

- **L01** — **The Three Names** (`lessons/0018-the-three-names.html`). `metadata entities`
  (`--top`/`--custom-only`). logical (lowercase, canonical — metadata/count/FetchXML/$filter) vs
  schema (PascalCase — solution XML/design-time) vs entity-set (plural — URL path) vs DisplayName
  (localized label, never for code). Closes the M01 L06 400-trap loop. Real: `account`/`Account`/
  `accounts`; `aaduser` is a managed add-in (`IsCustomEntity:true` ≠ "yours").
- **L02** — **Columns Are Typed** (`0019`). `metadata attributes <logical>` (list) +
  `metadata attribute <logical> <attr>` (full def). AttributeType, IsValidForCreate/Read/Update,
  RequiredLevel, IsPrimaryId/IsPrimaryName. **Shadow attributes**: every Lookup spawns read-only
  `<x>name`/`<x>yominame` String mirrors (explains M02 L01 lookup annotations). **Drift caught:**
  the **single-attribute** view returns `RequiredLevel` as an OBJECT `{Value, CanBeChanged,
  ManagedPropertyLogicalName}`; the **attributes list** flattens it to a bare string. Lesson §02
  shows the object shape + a callout on the list/single difference. `contact.fullname` is
  IsValidForCreate:false (computed); `account.name` RequiredLevel.Value = `ApplicationRequired`.
- **L03** — **Option Sets: Local vs Global** (`0020`). `metadata picklist <logical> <attr>`
  (`--no-global`), `list-optionsets`, `get-optionset <name>`. `IsGlobal` flag is the whole
  distinction; local Name = `<table>_<column>` (`contact_gendercode`, IsGlobal:false; 1→Male,
  2→Female — confirms M02's faith). Global demo: `componentstate` (IsGlobal:true; 0 Published /
  1 Unpublished / 2 Deleted / 3 Deleted Unpublished). picklist EXPANDS bound globals by default;
  `--no-global` skips. Label arrives as localized-label object (trimmed in lesson).
- **L04** — **Reading the Wiring** (`0021`). `metadata relationships <logical>` → groups
  OneToMany / ManyToOne / ManyToMany. Referenced=the "one"/parent, Referencing=the "many"/child
  (holds the FK). ReferencingAttribute=lookup column; **ReferencingEntityNavigationPropertyName=
  the @odata.bind target** — exactly M02 L02's `parentcustomerid_account`. Polymorphic customer
  lookup = `parentcustomerid` appears twice (→account, →contact), one nav prop per target. N:N =
  symmetric Entity1/Entity2 + `IntersectEntityName`, no FK column → link via `associate`.
- **L05** — **describe: the Write-Readiness Brief** (`0022`, capstone). `metadata describe
  <logical>` = ONE read-only call fusing L01–L04: `logical_name`, `entity_set_name`, `primary_id`,
  `primary_name`, `writable_attributes[]` (only IsValidForCreate/Update; 191 on contact) each with
  `attribute_type` + `required_level`; picklist → inline flat `options[{value,label}]` (+
  `global_optionset_id` when global-bound); lookup → `bind_key` (`<Nav>@odata.bind`) + `targets[]`
  ({logical, set_name}). The agentic contract: the read Claude makes before building a payload.
  Plus `metadata keys` (alt keys; contact has none → `[]` → no business-key upsert path). Bridges
  to M04. describe top keys verified: logical_name/entity_set_name/primary_id/primary_name/
  writable_attributes. Lookup sample: `msa_managingpartnerid` → targets account.

**✅ M03 COMPLETE — 5 lessons** (L01–L05, lessons 0018–0022; shipped 2026-06-17). Spine: names →
columns → option sets → relationships → describe. Done-when satisfied: L01 (logical-vs-set naming),
L02+L05 (columns), L04 (relationships). Build green (22 lessons). Next-link chain verified
0017→0018→…→0022; 0022's auto-Continue currently points to M11 L01 (0008) because M04–M10 have no
lessons yet — narrative names M04, button auto-rewires when M04 ships (same pattern 0017 had pre-M03).

### crm version bump 4.7.0 → 4.12.0 (noted 2026-06-17)

`crm --version` now reports **4.12.0** (was 4.7.0 earlier today). M03 read-metadata verbs
(entities/entity/attributes/attribute/picklist/relationships/keys/describe/list-optionsets/
get-optionset) all behave as captured above on 4.12.0. No re-verification of M01/M02 lessons done
this session (those touch CRUD/query, not metadata-read) — flag for a pass if drift surfaces.

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

## M04 lesson sequence (shipped 2026-06-17)

Milestone: **Schema authoring (write)** (issue #4). "Done when": create a custom table with 3+
typed columns via BOTH imperative verbs AND `apply -f`, then publish. First WRITE-to-schema
milestone. All live-verified against **crm v4.12.0** on agent-cloud (full create→delete round-trip,
org left clean). Running example: a **Project** table; published lessons use example env (prefix
`itworx`, solution `itworx_dev`, host orgexample.crm.dynamics.com).

- **L01** — **What a Custom Table Really Is** (`0023`, mental model, no big write). Auto-provisioned:
  primary id GUID, primary-name col, system cols, privileges, entity set. Publisher prefix
  (schema=`<Prefix>_<Display>`) + solution-as-container; prefix must match solution's publisher.
  Ownership UserOwned/OrganizationOwned (near-permanent). Preview via `scaffold --dry-run`. Publish
  = PublishAllXml (unpublished staging layer); imperative publishes per-call, batch once.
- **L02** — **Imperative Create** (`0024`). `create-entity --display` (envelope: created/schema_name/
  logical_name/entity_set_name/primary_attribute/solution/published) then `add-attribute <logical>
  --kind …`. Full `--kind` palette + per-kind flags. `--no-publish` staging. Verify w/ describe.
- **L03** — **scaffold table** (`0025`). `scaffold table "X" --column "Disp:KIND[:opts]"`,
  `{applied,skipped,planned,failed}`, idempotent skip, `--dry-run`/`--stage-only`, one publish.
- **L04** — **Declarative apply -f** (`0026`). YAML spec (`entities[]` + `optionsets[]`), if-exists=skip
  in dependency order, one publish, idempotent re-apply. Global vs local option set. `create-optionset`
  in declarative form. The reviewable/agentic default.
- **L05** — **Choose, Capture, Clean up** (`0027`, capstone). Decision matrix imperative/scaffold/apply;
  `export-spec` (round-trip + warnings + `_Base` money companion); clean delete via `delete-entity
  --check-dependencies` + `delete-optionset`. Done-when satisfied (L02 imperative + L04 apply).

**✅ M04 COMPLETE — 5 lessons** (L01–L05, lessons 0023–0027; shipped 2026-06-17). Build green
(27 lessons). Next-link chain 0022→0023→…→0027 verified; 0027 auto-Continue points to 0008 (M11 L01)
since M05–M10 unbuilt — narrative names M05, button auto-rewires when M05 ships (same pattern 0022 had).

### M04 live-CLI facts (crm v4.12.0, captured from agent-cloud)

- **Profile was stale → fixed.** `agent-cloud` had `publisher_prefix=cwxdf` / `default_solution=
  cwxdf_dogfood`, but NO publisher/solution with that prefix exists on the org → every create 404'd
  (`"solution unique name (cwxdf_dogfood) is not valid"`). Real working setup on the org: unmanaged
  solution **`agsol`** ("Agent Solution") ↔ publisher **`agpublisher`** prefix **`ag`**. Ran
  `crm profile edit agent-cloud --default-solution agsol --publisher-prefix ag`. Live captures use
  `ag_`/`agsol`; published lessons scrub to `itworx_`/`itworx_dev` (privacy rule).
- **create-entity** auto-creates primary name `<prefix>_name` (ApplicationRequired); PK `<prefix>_<table>id`
  (Uniqueidentifier, SystemRequired). 16 writable attrs on a 5-custom-col table (rest = system cols).
- **add-attribute** `--kind` ∈ string|memo|integer|bigint|decimal|double|money|boolean|datetime|picklist|
  multiselect|lookup|image|file. **decimal/double/money REQUIRE `--precision`** (`"--precision is
  required for this kind."`). Inline `--option` MUST be `value:label` or `:label` (auto-value);
  bare label rejected. Local picklist auto-values base = publisher's option base (was 550000000 on
  this org; lessons show conventional 100000000). `--no-publish` → no `published` key in envelope.
- **scaffold** column opts allowed: `description,max_length,optionset_name,required,target_entity`
  ONLY (no precision/format/min/max/inline-options). decimal in scaffold → `failed`
  ("--precision is required"). Partial-apply: entity+prior cols stay `applied`, bad col `failed`,
  rest skipped; re-run recovers (skip). `--dry-run`→planned (1 existence GET); `--stage-only`→staged.
- **apply** spec: top-level `solution` must be a MAPPING (string → `"solution must be a mapping."`)
  → pass `--solution` flag. optionset spec keys: `name`, `display_name`, `options:[{value,label}]`
  (NOT `display`). entity: schema_name/display_name/display_collection_name/ownership/
  primary_attr{schema_name,label}/attributes[{kind,schema_name,display_name,required,max_length,
  precision,format_name,optionset_name}]. Dependency order (optionset before its picklist col),
  one publish. Re-apply unchanged → all `skipped`. Global `--dry-run` supported.
- **export-spec** warns + drops: local picklist (`OptionSet IsGlobal='False' … cannot be retrieved`),
  `VirtualType` `*name` shadow cols (boolean also spawns `<col>name`). **money auto-spawns `_Base`
  companion** (`<col>_Base`, "X (Base)", base currency) — appears in the spec.
- **delete-entity**/`delete-optionset` need `--yes` in JSON mode (else `"aborted by user"`).
  `delete-entity --dry-run --check-dependencies` → `{would_delete, can_delete, blockers[]}`. Envelope
  `{deleted, logical_name|name, solution}`. Global optionset survives entity delete (delete separately).

## M05 — Relationships (issue #5) — shipped 2026-06-18

Milestone: **Relationships** (issue #5). "Done when": create a 1:N to account and an N:N, then
create a child row via the lookup — all satisfied (L02 1:N, L05 N:N, L04 child-via-lookup;
L05 capstone runs the full round-trip). All live-verified against **crm v4.12.0** on agent-cloud
(full table→1:N→child-row→N:N→associate→cleanup, then org left clean).

**5 lessons, 0028–0032:**
- **L01** — **What a relationship is** (`0028`). Concept: only two real types (1:N, N:N); N:1 = 1:N
  from the child. A lookup column *is* a 1:N on the referencing/child side; N:N = intersect table.
  Read with `metadata relationships` → OneToMany/ManyToOne/ManyToMany; Referenced/Referencing/
  ReferencingAttribute/NavigationProperty. Read-only. (Adds a `.diagram` CSS block — self-contained.)
- **L02** — **Create a 1:N to account** (`0029`). `create-one-to-many` (atomic rel+lookup), four
  required ideas mapped to referenced/referencing/lookup, `--dry-run` shows full RelationshipDefinitions
  body + cascade defaults + `references[]` existence check, envelope `referencing_attribute`=lookup
  logical name, verify with relationships/attribute.
- **L03** — **Cascade behaviors** (`0030`). Six actions (Delete/Assign/Reparent/Share/Unshare/Merge),
  cascade types, parental vs referential vs restrict-delete, CLI default = referential, set at create
  with `--cascade-*`, change later with `update-relationship` (retrieve-merge-write).
- **L04** — **Child row via the lookup** (`0031`). Lookup's three runtime names; `@odata.bind` on
  create (nav property, case-sensitive, `/set(guid)`); `set-lookup`/`clear-lookup` on existing rows;
  read back via `$expand` (child) + `entity children` (parent). Ties M05↔M02.
- **L05** — **N:N + clean up** (`0032`, capstone). `create-many-to-many` + intersect (no lookup/cascade);
  `entity associate` (NAV = relationship schema name); 1:N-vs-N:N matrix + manual-intersect pattern;
  `delete-relationship --dry-run --check-dependencies`; teardown order. Full done-when round-trip.

**✅ M05 COMPLETE — 5 lessons** (L01–L05, lessons 0028–0032; shipped 2026-06-18). Build green
(32 lessons). Next-link chain 0027→0028→…→0032 verified; **0027's auto-Continue rewired from 0008
(M11 L01) → 0028 (M05 L01)** automatically once M05 shipped (the predicted behaviour). 0032 has no
Continue yet (M06 unbuilt) — narrative names M06, button auto-rewires when M06 ships.

### M05 live-CLI facts (crm v4.12.0, captured from agent-cloud 2026-06-18)

- **create-one-to-many** required: `--schema-name --referenced-entity --referencing-entity
  --lookup-schema --lookup-display`. Atomic (one POST to `RelationshipDefinitions`). Both tables
  must pre-exist (dry-run `references[]._exists` pre-checks). Default `CascadeConfiguration` =
  `{Assign:NoCascade, Delete:RemoveLink, Reparent:NoCascade, Share:NoCascade, Unshare:NoCascade,
  Merge:NoCascade}` (referential). Default `AssociatedMenuConfiguration` = `{Behavior:UseCollectionName,
  Group:Details, Order:10000}`. Envelope: `created, kind:"OneToMany", schema_name, referenced_entity,
  referencing_entity, referencing_attribute (=lookup logical, lowercased), relationship_id, solution,
  published`. `--dry-run` is **global** (no per-command flag) and works.
- **lookup nav property** = the lookup **schema name** (`ag_AccountId`), returned as
  `ReferencingEntityNavigationPropertyName` in `metadata relationships` (under the child's `ManyToOne`).
  Lookup logical = `ag_accountid`; read form = `_ag_accountid_value`.
- **@odata.bind on create**: `"ag_AccountId@odata.bind":"/accounts(<guid>)"` → record returns with
  `_ag_accountid_value` populated. `$expand=ag_AccountId($select=name)` resolves parent inline (object).
  `entity set-lookup SET ID NAV REL_SET REL_ID` / `clear-lookup SET ID NAV` are the existing-row twins.
- **entity children** `accounts <id> --filter-entities ag_ --non-empty` → `[{entity, attribute, set,
  count}]` (1:N where the record is parent; chunked $batch).
- **create-many-to-many** required: `--schema-name --entity1 --entity2 --intersect-entity`. No lookup,
  no cascade. Envelope: `created, kind:"ManyToMany", schema_name, intersect_entity, relationship_id,
  solution, published`. **N:N nav property names came back `null`** in `metadata relationships`
  (Entity1/2NavigationPropertyName=null) but **`entity associate` works using the relationship
  SCHEMA NAME as the NAV arg**. Associate envelope `{associated, target, related}`; `$expand`
  schema-name → **array** of related rows. `disassociate` = inverse.
- **update-relationship** `<schema> --cascade-*` → `{updated, path, schema_name, published}`
  (retrieve-merge-write; only passed flags change). cascade enum: `NoCascade|Cascade|Active|UserOwned|
  RemoveLink|Restrict` (Delete-only: RemoveLink/Restrict; Merge-only: Cascade/NoCascade).
- **delete-relationship** `<schema> --yes` (required in JSON mode). `--dry-run --check-dependencies`
  → `{would_delete, schema_name, solution, can_delete, blockers[]}`. Deleting a 1:N also drops its
  lookup column. Real delete envelope `{deleted, schema_name|logical_name, solution}`. Teardown order:
  relationships before the tables.

## M06 lesson sequence (shipped 2026-06-18)

Milestone: **Solutions & ALM** (issue #6). "Done when": put a custom table into an unmanaged
solution, export the zip, and re-import it. All 5 lessons live-verified against **crm v1.0.0**
(version reset from pre-launch 4.31.1 — same binary, same commands). Cloud only; no on-prem
differences in this milestone.

- **L01** — **What is a solution?** (`0033`). Publisher → solution → component hierarchy;
  managed vs unmanaged (table); ALM pipeline (dev unmanaged → export → import managed to prod);
  automatable vs GUI-only tasks map (create-publisher/create/export/import = CLI; Solution
  Checker/history UI = GUI only). Concept lesson, no CLI exercise.
- **L02** — **Inspect solutions** (`0034`). `solution list` (ismanaged flag, version);
  `solution info` (solutiontype, _publisherid_value); `solution components` (componenttype 1=Entity,
  objectid=MetadataId); component type table (1/2/26/29/59/60/61/80/300). `--save inventory.json`
  + `--diff` for CI drift detection.
- **L03** — **Build a solution** (`0035`). `create-publisher` (prefix 2-8 chars, option-value-prefix
  offsets picklist values); `solution create` (--no-set-default important); `metadata create-entity
  --solution`; `add-component --type 1 --id <MetadataId from metadata_id_url>`. AddRequiredComponents
  silently pulls forms/views/ribbon.
- **L04** — **Export & import** (`0036`). `solution export` async (ExportSolutionAsync, polls);
  ZIP = solution.xml + customizations.xml + [Content_Types].xml. `solution import` async with
  progress lines; `components[]` array in result; `--overwrite` = OverwriteUnmanagedCustomizations;
  `--yes` required in JSON mode. Done-when: re-imported same org.
- **L05** — **Layers & what's not automatable** (`0037`, capstone). Managed/unmanaged layer stack;
  `layer-conflicts --solution <managed> --unmanaged-solution <yours>` (live result: empty array for
  AccessTeam vs itworx_dev); `set-version` (4-part version bump); GUI-only table (Solution Checker,
  history, ZIP diff, patch mgmt); cleanup: `delete-entity` first, then `solution uninstall`
  (removes container only, not components). Full 9-step round-trip capstone script.

**✅ M06 COMPLETE — 5 lessons** (L01–L05, lessons 0033–0037; shipped 2026-06-18). Build green
(37 lessons). 0032's auto-Continue rewired to 0033 automatically once M06 shipped.

### M06 live-CLI facts (crm v1.0.0, captured from agent-cloud 2026-06-18)

- **crm version reset**: `crm --version` now reports `1.0.0` (was auto-bumped to pre-launch
  4.31.1, then reset). Same binary/commands as v4.12.0 sessions.
- **create-publisher**: `--name --display --prefix --option-value-prefix` (required); `--if-exists
  [error|skip]`; `--no-set-default` (don't write publisher_prefix back to profile). Envelope:
  `{created, uniquename, friendlyname, customizationprefix, customizationoptionvalueprefix, publisherid}`.
- **solution create**: `--name --publisher` (required; or `--publisher-id`); `--display --version
  --if-exists --no-set-default`. Envelope: `{created, uniquename, friendlyname, version, publisherid, solutionid}`.
- **add-component**: `--solution --type --id` (required). `--type 1` = Entity (integer or friendly
  name). `--id` = component MetadataId (from `metadata_id_url` in create-entity envelope). Envelope:
  `{added, solution, component_id, component_type}` + `meta.note` about AddRequiredComponents.
  `--no-add-required` / `--no-subcomponents` to suppress.
- **solution components --save**: writes `[{componenttype, objectid, rootcomponentbehavior}]` (no
  solutioncomponentid). `--diff` compares live vs saved file, non-zero exit on drift.
- **export**: `solution export <name> -o <file>` (async, ExportSolutionAsync). Envelope: `{output,
  bytes, managed, solution, async_operation_id, export_job_id, duration_ms, action}`. ZIP = 3 files:
  solution.xml (manifest), customizations.xml (component defs), [Content_Types].xml.
- **import**: `solution import <zip> --overwrite --yes`. Async with stderr progress lines. Envelope:
  `{import_job_id, async_operation_id, status, progress, started_on, completed_on, duration_ms,
  managed, action, result, components[]}`. `components[]` = `[{name, type, result}]` for each
  processed component (entity, savedQuery, formXml, entityRibbon, etc.).
- **layer-conflicts**: `--solution <managed-name> --unmanaged-solution <yours>`. Returns
  `[{...}]` per conflict; empty array = no conflicts. AccessTeam vs m06sol → `[]` (no conflicts).
- **solution uninstall**: removes the solution container only (not its components). Components must
  be deleted separately first.
- **agsol current state**: 2 components (account + contact, both componenttype 1 from M05
  relationship work). m06sol was created+used for M06 lessons then cleaned up (m06_project deleted,
  m06sol uninstalled).

## M07 lesson sequence (shipped 2026-06-18)

Milestone: **Forms, Views & Apps** (issue #7). "Done when": create a view and a model-driven app
exposing the custom table, and add a ribbon button. All 5 lessons live-verified against **crm v1.0.0**
on agent-cloud. Running example: `ag_ticket` entity (ag_name, ag_status picklist, ag_priority integer).

- **L01** — **The UI surface layer** (`0038`). The five UI artefacts: form (type=2 main), view
  (savedquery), sitemap, model-driven app (appmodule), ribbon/web resource. CLI coverage map per
  artefact. Auto-provisioned artefacts on entity create: Information main form + Active/Inactive
  public views. GUI-only limits. Running example ag_ticket introduced.
- **L02** — **Create a system view** (`0039`). `view list` (auto-created Active/Inactive views);
  `view create` (`--otc` = integer ObjectTypeCode from `metadata entity` — org-specific for custom
  entities, `--column logicalname[:width]`, `--filter-active`, `--order`, `--query-type`).
  querytype values: 0=public, 1=advanced-find, 2=associated, 4=quick-find, 64=lookup.
  No `crm view delete` → delete via `entity delete savedqueries <id> --yes`.
- **L03** — **Build a model-driven app** (`0040`). `app create` (envelope includes `app_lookup_error`
  read-back race warning — not a failure); `app build-sitemap` (`--area 'id[:Title]'`,
  `--group 'areaId/groupId[:Title]'`, `--subarea 'areaId/groupId:entity=<logical>[:Title]'`,
  `--unique-name` links sitemap to app); `app add-components <appmoduleid> --component kind:guid`
  (kinds: view|chart|form|dashboard|sitemap|bpf); `app delete --yes` (sweeps FK dependents;
  sitemap orphaned but not deleted).
- **L04** — **Web resources & ribbon buttons** (`0041`). `webresource create/list/get/update/delete`;
  type inferred from extension (3=JScript); naming `<prefix>_/path/file.js`. `ribbon add-button`
  async (export-modify-import cycle ~60s); button_id = `entity.location.LabelNoSpaces.CustomAction`;
  `--param PrimaryControl` (form) vs `SelectedControlSelectedItemIds` (grid); `ribbon list/export/remove`
  (remove also async). `--dry-run` on add-button shows only ExportSolutionAsync step.
- **L05** — **Forms: fields and layout** (`0042`, capstone). `form list` (type=2 main, auto-provisioned
  'Information'); `form add-field <entity> <attr>` (classid auto from AttributeType; `--form/--tab/--section`
  for targeting); `form remove-field`; `form export <entity> <form-name>` (returns formXml); `form set-field`
  (move) and `form clone` (copy to other entity). Full 12-step capstone script. Done-when satisfied.
  GUI-only limits: form designer, Ribbon Workbench, BPF editor, app validation UI.

**✅ M07 COMPLETE — 5 lessons** (L01–L05, lessons 0038–0042; shipped 2026-06-18). Build green
(42 lessons). 0037's auto-Continue rewired to 0038 automatically once M07 shipped.

### M07 live-CLI facts (crm v1.0.0, captured from agent-cloud 2026-06-18)

- **ag_ticket entity** created for M07 demos: logical `ag_ticket`, schema `ag_Ticket`, set `ag_tickets`,
  OTC **10828** (agent-cloud; org-specific for custom entities), primary attr `ag_name`.
  Columns added: `ag_status` (Picklist: 100000000=Open, 100000001=In Progress, 100000002=Closed),
  `ag_priority` (Integer). Entity remains on agent-cloud (lessons tear it down in the capstone).
- **view create** requires `--otc <integer>` (NOT MetadataId GUID). OTC from `metadata entity <logical>`.
  Auto-provisioned views on create: "Active Tickets" (isdefault:true, querytype:0) + "Inactive Tickets"
  (querytype:0). Column syntax: `logicalname[:width]`. No `crm view delete` command.
- **app create** envelope includes `app_lookup_error` + `meta.warnings` when platform read-back races
  the create — not a failure; appmoduleid is correct. `app delete` sweeps FK-blocking rows
  (`dvtablesearch`, `appsetting`); `appmodulecomponent` rows listed as `dependents_skipped`.
- **app build-sitemap** generates SiteMapXml; `--unique-name <app-uniquename>` links sitemap to app
  at creation time. Sitemap is a separate record, NOT deleted by `app delete`.
- **webresource create** infers webresourcetype from extension: .js → 3 (JScript). Types: 1=HTML,
  2=CSS, 3=JScript, 4=XML, 5=PNG, 6=JPG, 7=GIF, 9=XSL, 10=ICO, 11=SVG, 12=RESX.
  Naming: `<prefix>_/scripts/foo.js` (path-style). `webresource delete --yes` (no prompt in JSON mode).
- **ribbon add-button** async (ExportSolutionAsync → patch RibbonDiffXml → ImportSolutionAsync);
  ~60s; stderr progress lines. button_id = `<entity>.<location>.<LabelNoSpaces>.CustomAction`;
  default group = `Mscrm.Form.<entity>.MainTab.Save` for form location. `ribbon remove --button-id
  <id> --yes --solution <sol>` also async.
- **form list** default: main forms only (type=2). `--all` lists every type. `--type` accepts:
  dashboard|main|quickview|quickcreate|dialog|card. Auto-provisioned 'Information' form: ag_name +
  ownerid only; custom columns not on it until `form add-field`. `form add-field` resolves classid
  automatically from AttributeType (Picklist→`{3EF3...}`, Integer→`{C6D1...}`, String→`{4273...}`).
  `form export <entity> <form-name>` (BOTH positional args required; missing FORM_NAME → exit 2).

## M08 lesson sequence (shipped 2026-06-18)

Milestone: **Automation & business logic** (issue #8). "Done when": register a workflow (trigger it)
and register a plug-in step, and articulate what needs other tools. All 5 lessons live-verified against
**crm v1.0.0** on agent-cloud. Cloud only.

- **L01** — **The automation landscape** (`0043`). Four automation tiers: business rule (cat 2), classic
  workflow (cat 0), Power Automate flow (cat 5), plug-in/webhook (event pipeline). Category deep-dive
  (0=workflow, 1=dialog, 2=businessrule, 3=action, 4=bpf, 5=flow). CLI coverage map per tier.
- **L02** — **Classic workflows: lifecycle** (`0044`). `workflow list` (statecode 0/1, statuscode 1/2,
  ondemand, --entity/--activated filters). `workflow activate/deactivate --yes`. `workflow export -o`/
  `import --file [--activate]`. `workflow run <id> --target <guid>` (on-demand only; async_operation_id
  null = normal). `migration-assess` (verdict: ready|blocked; blockers: custom_activity/real_time/
  wait_condition). Live: ran "Reset Security Stamp" on Sara Mitchell (contact).
- **L03** — **The event pipeline** (`0045`). Three stages: pre-validation (10, outside tx, sync only),
  pre-operation (20, inside tx before DB write, sync only, can modify Target), post-operation (40,
  inside/after tx, sync or async). Async requires postoperation (platform constraint). `plugin list-types`
  [--assembly name]. `register-assembly PATH --isolation-mode sandbox|none (sandbox=2 default); --update`.
  `register-step --message --plugin-type|--service-endpoint --entity --stage --mode --filtering-attributes
  --async-auto-delete`. `register-image --step --type pre|post|both --alias --attributes`. `set-step-state
  enable|disable`. `unregister-step/image/assembly --yes`. post-image requires postoperation step.
- **L04** — **Webhooks: the no-DLL step** (`0046`). `register-webhook --name --url --auth
  (webhookkey=4/httpheader=5/httpquerystring=6) --auth-value (write-only, never returned)`. Envelope:
  created/name/url/auth_type/serviceendpointid/solution. `register-step --service-endpoint <webhook-name>`
  (mutually exclusive with --plugin-type). Standard pattern: postoperation+async. Platform POSTs
  RemoteExecutionContext JSON (MessageName, PrimaryEntityName, PrimaryEntityId, InputParameters.Target,
  UserId, CorrelationId). NO `unregister-webhook` command: delete via `entity delete serviceendpoints
  <id> --yes`. Teardown: unregister-step BEFORE entity delete serviceendpoints.
- **L05** — **The automation boundary** (`0047`, capstone). `action function WhoAmI/RetrieveCurrentOrganization
  [--params JSON] [--bind-set/--bind-id]` = OData GET. `action invoke NAME [--body JSON] [--bind-set --bind-id]`
  = OData POST. `sla activate <id>` = activates backing workflows then SLA (creation/KPI = GUI-only). Full
  automation decision matrix. GUI-only: flow designer, BPF, SLA KPI items, .NET build. Done-when satisfied.

**✅ M08 COMPLETE — 5 lessons** (L01–L05, lessons 0043–0047; shipped 2026-06-18). Build green (47 lessons).
0042's auto-Continue rewired to 0043 automatically once M08 shipped.

### M08 live-CLI facts (crm v1.0.0, captured from agent-cloud 2026-06-18)

- **workflow list** fields: workflowid, name, category, statecode (0=Draft, 1=Activated), statuscode
  (1=Draft, 2=Activated), ondemand, primaryentity. Filters: `--category <name-or-int>`, `--entity <logical>`,
  `--activated`, `--on-demand`.
- **workflow run** POSTs to `workflows(<id>)/Microsoft.Dynamics.CRM.ExecuteWorkflow` with body
  `{"EntityId":"<contactid>"}`. `async_operation_id: null` in envelope is normal — job queued. Live run
  against Sara Mitchell (a1b2c3d4-1111-...) succeeded.
- **migration-assess** live results on agent-cloud: "Reset Security Stamp" contact → blocked (custom_activity);
  "ADX Sign Up Email" adx_invitation → ready. Verdict "blocked" ≠ impossible, means redesign needed.
- **action function WhoAmI** → `{BusinessUnitId, UserId, OrganizationId}`. Live-verified.
- **action function RetrieveCurrentOrganization** `--params '{"AccessType":"Default"}'` → org metadata
  (OrganizationVersion, FriendlyName, Geo, EnvironmentId). Live-verified.
- **slas query** on agent-cloud → empty array (no SLAs defined). `sla activate` explained conceptually.
- **plugin list-types** → large list of platform-registered types (Microsoft.* assemblies). `--assembly` scopes.
- **No crm workflow or SLA creation verb** — only management (activate/deactivate/run/export/import).
- **No unregister-webhook** in `plugin` group — webhook service endpoint deleted via `entity delete
  serviceendpoints <id> --yes`.
