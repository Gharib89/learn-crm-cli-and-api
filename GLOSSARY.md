# GLOSSARY — learned D365 / crm vocabulary

The learner's growing record of D365/crm terms, in their own words, as evidence of
understanding. Adopts upstream language (crm repo `CONTEXT.md`/`D365.md`, the crm skill,
Microsoft Learn) — never invents. See `CONTEXT.md` for how this differs from the workspace
contract glossary.

Each entry: the term, a one-line plain-English grasp, and where it was first met.

---

## Install & profiles — *M01 L01*

**Profile (connection profile)**
A named, saved connection: URL (which org) + auth scheme (how to prove identity) + the
secret + optional defaults (default solution, publisher prefix). The CLI is stateful — one
profile is *active* at a time and unflagged commands run against it. _Met: M01 L01._

**Auth scheme (inferred)**
How the CLI authenticates: `oauth` (cloud) or `ntlm` (on-prem). **Inferred from the URL** —
`*.dynamics.com` → OAuth, anything else → NTLM. Override with `--auth-scheme`. _Met: M01 L01._

**NTLM / OAuth client-credentials**
The two supported schemes. NTLM = Windows Integrated auth for on-prem (username + domain +
password). OAuth client-credentials = cloud, using an app registration's tenant-id +
client-id + client-secret. _Met: M01 L01._

**Secret storage (keyring XOR plaintext)**
Where the credential rests *on disk*: the OS keyring when available, else a `0600` plaintext
field in the profile file (WSL/headless, or forced with `--store-password-plaintext`). One
store, never both. "plaintext" is about disk, not the wire. Resolution at run time:
`--password` > stored secret > TTY prompt. No env-var fallback (only `CRM_HOME`). _Met: M01 L01._

**Profile lifecycle verbs**
`add` (create+save+test+activate) · `list` (● marks active) · `use` (switch active; `--none`
clears) · `edit` (change fields — *not* the secret) · `set-password` (rotate the secret) ·
`delete-password` / `rm` (destructive). Key trap: rotate secrets with `set-password`, not
`edit`. _Met: M01 L01._

---

## Connection & identity — *M01 L02*

**Environment / org**
An isolated Dynamics 365 CE instance — its own database plus its own web address
(e.g. `https://orgexample.crm.dynamics.com`). "Environment" and "org" are used
interchangeably. Identified by an `OrganizationId` GUID. _Met: M01 L02._

**Dataverse Web API**
The single HTTP door into an org, at `<org url>/api/data/v9.x/`. Speaks OData v4 over
HTTPS. The `crm` CLI is a thin wrapper over it — every command is one request here; no
local database, no GUI clicking, no SOAP. _Met: M01 L02._

**API version (`v9.1` / `v9.2`)**
The version segment in the Web API path. **Cloud (OAuth) → `v9.2`; on-prem (NTLM) →
`v9.1` max** (asking v9.2 on-prem returns HTTP 501). Visible in `@odata.context`, so the
version doubles as a tell for which kind of org you're on. _Met: M01 L02._

**WhoAmI**
The Web API's read-only "are you there, and who am I?" function. No input; returns three
GUIDs — `UserId`, `BusinessUnitId`, `OrganizationId`. The canonical first/confirm call.
CLI: `crm --json connection whoami`. _Met: M01 L02._

**`connection test` (host + version confirm)**
Sibling of whoami that reports `api_base` (the live host) and `api_version` as first-class
fields — the **v4.7.0** way to confirm *which org + which API version* you're hitting. (whoami
now returns only the three identity GUIDs; older versions exposed host/version inside
`@odata.context`.) Also `connection status` (active session/profile, no network) and
`connection doctor` (DNS/TLS/auth diagnosis). _Met: M01 L02 (added v4.7.0)._

**`@odata.context`**
An OData URL the *Web API* echoes back showing the host + API version that answered. In crm
**v4.7.0** the CLI no longer surfaces it in `--json` output — confirm host + version with
[[connection-test]] `connection test` (`api_base` / `api_version`) instead. _Met: M01 L02
(CLI behavior updated v4.7.0)._

**GUID**
A 32-hex universal identifier (`bf40e4d2-ee3e-f111-…`). Dataverse's primary key: every
record, table, user, and org has one. _Met: M01 L02._

**Application user**
The non-human identity the cloud CLI authenticates *as* via OAuth client-credentials —
an app registration granted a security role in the org. `UserId` in WhoAmI points to it.
_Met: M01 L01 (in passing; expanded in security milestone)._

---

## Agent contract & results — *M01 L03*

**The envelope (`{ok, data, meta}`)**
The single, stable shape every `--json` command answers in. Two forms only:
`{ok:true, data, meta?}` (worked) or `{ok:false, error, meta?}` (didn't). `data` and
`error` are mutually exclusive; `meta` is optional. The contract an agent branches on
instead of parsing prose. _Met: M01 L03._

**`ok` / `data` / `error` / `meta`**
`ok` = the boolean branch ("did it take effect?") — read first. `data` = payload, only
when `ok:true`. `error` = human message, only when `ok:false`. `meta` = optional
structured *footnotes about* the result (status, category, count, dry_run, warnings) —
present only when there's something to report (whoami carries none). _Met: M01 L03._

**Exit codes 0 / 1 / 2**
`crm` also sets `$?`, redundant with `ok` so a shell can branch without parsing JSON.
**0** = success. **1** = operational failure (well-formed request, *server/guard* said
no — 404, validation, declined). **2** = usage error (malformed command — bad flag,
missing arg, bare `crm`; *server never contacted*). Non-zero = didn't take effect.
_Met: M01 L03._

**Operational failure vs usage error**
The reason the 1-vs-2 split matters: on **2** you *fix your invocation* (re-running the
same string fails identically); on **1** you *handle the server's answer* (a retry might
help — check `meta.retryable`). Conflating them = retrying a typo forever, or giving up
on a transient error. _Met: M01 L03._

**`meta` diagnostic fields**
On an operational failure `meta` carries `status` (HTTP), `code` (Dataverse hex),
`category` (coarse: `not_found`/`auth`/`validation`…), `retryable` (bool). On queries:
`entity_set`, `count`. `meta.warnings[]` = non-fatal advisories channel.
`meta.dry_run:true` = the canonical "this was a preview, no write issued" signal — so
`ok:true` means "valid request," not always "write landed." _Met: M01 L03._

---

## Write safety — *M01 L04*

**`--dry-run`**
Add to any mutating command → it runs everything up to the write, then stops and returns
the request it *would* have sent (`data._dry_run:true`, `meta.dry_run:true`, `ok:true`,
exit 0). The seatbelt: preview → read the plan → confirm → re-run without it to commit.
Composes with `--validate`. _Met: M01 L04._

**"No writes, not no traffic"**
The key dry-run rule: it suppresses *writes*, not *reads*. GETs (lookup resolution,
existence checks, metadata) still run for real against the live org — so the previewed
plan reflects live facts (e.g. a clone's resolved `would_create` body), not a guess.
Pure-read verbs (`query`, `entity get`) run normally under `--dry-run`. _Met: M01 L04._

**Reading the plan (`method` / `url` / `body`)**
The three preview fields = the three pre-write questions. `method`: which verb —
**POST = create, PATCH = update** (POST when you meant to edit ⇒ duplicate footgun).
`url`: which entity set + which record GUID + **which org host** (the wrong-org seatbelt
at write time). `body`: exactly which fields change (an update sends only the named keys).
_Met: M01 L04._

**`--validate`**
Field-**name** checks a create/update payload via a few read-only metadata GETs; blocks
unknown fields with `{ok:false, error, meta:{unknown_fields, did_you_mean}}` (exit 1 —
operational, not usage) instead of cryptic OData noise. Doesn't check option-set *values*.
It's a **per-verb flag** — goes *after* the verb (beside `--data`), NOT before the group;
wrong position ⇒ exit-2 "No such option". Composes with the global `--dry-run`.
**Validate-first is the recommended default for agent-driven writes.** _Met: M01 L04
(position corrected against live CLI v3.9.1)._

---

## Committing a write — *M01 L05*

**Safe-write loop**
Every real mutation, four beats: **preview** (`--dry-run` + `--validate`) → **commit**
(the *same* command, `--dry-run` removed) → **verify** (`entity get` the new GUID) →
**clean up** (`entity delete`, if a test). The committed command equals the previewed one
minus the safety flag — no surprises between plan and execution. _Met: M01 L05._

**`entity create` (what the server adds)**
A `POST`. The server assigns the primary-key GUID (e.g. `contactid`), computes derived
fields (`fullname` from first+last), stamps `createdon`/owner, sets default
`statecode:0`/`statuscode:1`. The create *response is the created row*. _Met: M01 L05._

**`return=representation` / `--no-return`**
By default create requests `Prefer: return=representation` → echoes back the **whole** new
row (~130 columns, mostly null). `--no-return` skips the firehose and returns just the
GUID. _Met: M01 L05._

**`entity delete` + `--yes`**
A `DELETE` — the first **destructive** verb. Non-interactively without `--yes` it aborts
safely (`{ok:false,"aborted by user"}`, exit 1) rather than guess or hang. `--yes` =
"I mean it." Permanent; no after-the-fact undo (preview *before*). Success:
`{deleted:true, id}`. _Met: M01 L05._

**`@…FormattedValue` annotations**
Twin keys the server attaches to coded fields on reads — `statuscode:1` arrives with
`statuscode@…FormattedValue:"Active"`. The human label behind every option-set number.
_Met: M01 L05/L06._

---

## Reading data — *M01 L06*

**`entity get` vs `query odata` (two read shapes)**
The read splits on whether you know the GUID. `entity get <set> <guid>` = by identity →
one object (OData `$entity`) directly under `data`. `query odata <set>` = by criteria →
an array **as `data` itself** (this CLI unwraps OData's `value`; add `--count` for
`meta.count`), even for one or zero matches. Both are GETs. _Met: M01 L06 (shape corrected
to v3.12.6 in [[querying-sets]] M02 L03)._

**`--select` / `--filter` / `--top`**
The query workhorses. `--select` = which columns (omit ⇒ every column — always name
them). `--filter` = which rows in OData syntax (`eq`, `ne`, `gt`/`lt`, `contains(f,'x')`,
`and`/`or`). `--top` = max rows. Empty result = `data:[]`, still `ok:true`, exit 0 ("no
match" is an answer, not a failure). _Met: M01 L06._

**`@odata.etag`**
A row-version tag (`W/"2503282"`) — the value the server compares for optimistic concurrency,
the other half of `If-Match`. In crm **v4.7.0** the CLI no longer returns it on reads; guard a
write with `--if-match "*"` ("any current version") and let the server enforce the check.
_Met: M01 L06 (CLI behavior updated v4.7.0)._

**`query count` — set-name vs logical-name trap**
Counts rows via `RetrieveTotalRecordCount`. Two edges: (1) takes the **logical name**
(`contact`), NOT the entity-set name (`contacts` — that's what `get`/`query odata` use);
wrong one ⇒ 400 `validation`. (2) **Cached & approximate** (can read 0 while rows exist).
Use for scale, never exactness; for an exact filtered count, run the query. The
set-vs-logical split recurs platform-wide. _Met: M01 L06._

---

## Navigating the CLI — *M01 L07*

**Command tree (group / verb / flags)**
Every call: `crm <global-flags> <group> <verb> <args> <command-flags>`. **Group** = a noun
(domain: `entity`, `query`, `solution`, `metadata`…). **Verb** = the action (`get`,
`create`, `update`…). **Global flags** (`--json`, `--dry-run`, `--profile`,
`--auth-scheme`) go *before* the group; **command flags** (`--select`, `--data`) after the
verb. Locate commands, don't memorize them. _Met: M01 L07._

**`--help` (three levels)**
`crm --help` = list groups + globals. `crm <group> --help` = that group's verbs.
`crm <group> <verb> --help` = that verb's args/flags. Prose, for human eyes — the answer
to "how do I do X" without guessing. _Met: M01 L07._

**`crm describe [GROUP]`**
The same command tree as **machine-readable** catalogue (commands, options, choices) — for
an agent/script to parse and plan a call. No arg = whole tree; with `GROUP` = just that
subtree (loads only that module, faster). `--help` is for you; `describe` is for the agent.
_Met: M01 L07._

---

## Record anatomy — *M02 L01*

**Record (row) vs form**
A record is a **row in a table**; the GUI form is just a *styled view* of that row — dropdowns
rendered as words, GUIDs rendered as names. The Web API returns the raw row underneath. Reading
the API face fluently is the whole skill of M02. _Met: M02 L01._

**EntitySetName vs LogicalName (a table's two names)**
Every table carries both. **EntitySetName** = the plural collection name (`contacts`) — it's in
the Web API URL, so `entity get` / `query odata` use it. **LogicalName** = the singular,
all-lowercase internal name (`contact`) — metadata and `query count` use it. Formalizes L06's
400-error trap. Also `PrimaryIdAttribute` (`contactid`, the GUID key) and `PrimaryNameAttribute`
(`fullname`, the GUI title column). _Met: M02 L01._

**The four field shapes**
Every column is one of: (1) **primary key** — server-assigned GUID (`contactid`); (2) **plain
column** — text/number/datetime, value is the value (dates = raw ISO `Edm.DateTimeOffset`);
(3) **option-set (choice)** — stores a *code* (`gendercode: 2`), label rides along only as the
`@…FormattedValue` twin; (4) **lookup (relationship)** — `_<name>_value` holds *another row's*
GUID. _Met: M02 L01._

**Lookup / foreign key (`_x_value` + 3 annotations)**
A lookup is a foreign key: `_ownerid_value` is a computed, read-only `Edm.Guid` pointing into
another table. Three annotations decode it — `…FormattedValue` (related row's display name),
`…lookuplogicalname` (**which table** it points to, e.g. `systemuser` — the GUID is meaningless
without it), `…associatednavigationproperty` (the name used to `$expand`). You *set* a lookup by
GUID + table, never by name. _Met: M02 L01._

**Annotated vs `--minimal` (two views of one row)**
`entity get` is annotated by default (codes + labels, GUIDs + names/target tables — the *form's*
view, for humans). `--minimal` drops **every key containing `@`** (etag, FormattedValues, lookup
annotations), keeping business fields, `_*_value` GUIDs, and the primary id — the *storage* view,
i.e. exactly what the column holds. You filter and update against the stored values (codes/GUIDs),
not the labels. _Met: M02 L01._

---

## Updating records — *M02 L02*

**`entity update` (PATCH) — surgical & silent**
A `PATCH` against an existing GUID (vs create = `POST` of a whole new row). The body carries
**only the keys you name** — a partial update; unmentioned columns are untouched. **Silent by
default**: returns just `_entity_id`, no row body (opposite of create's `return=representation`).
Use `--return-record` to get the row back, or `entity get` to verify. _Met: M02 L02._

**`If-Match: "*"` default (update-only) / `--allow-create` / `upsert`**
A bare Web API `PATCH` will **create** the row if the id is missing (upsert) — so a typo'd GUID
could spawn a stray record. `crm` blocks this by sending `If-Match: "*"` ("only if it already
exists") by default. Opt into create-if-missing with `--allow-create` or the dedicated
`entity upsert` verb. `--if-match 'W/"…"'` with a real etag (L06) = optimistic concurrency
(reject if the row changed since you read it). _Met: M02 L02._

**Writing the three field shapes**
The L01 read-anatomy, inverted for writing: **plain** column → value straight in `--data`;
**option-set** → the **code, never the label** (`"gendercode": 1`, not `"Male"`); **lookup** →
**not** the read-only `_x_value`, but the *navigation property* + `@odata.bind` naming the related
**set + GUID**: `"parentcustomerid_account@odata.bind": "/accounts(<guid>)"`. GUID + table, never
a name. The nav-property name is the `associatednavigationproperty` annotation you read in L01
(customer lookups suffix the target table: `parentcustomerid_account` vs `…_contact`). _Met: M02 L02._

**`entity set-lookup` / `entity clear-lookup`**
Purpose-built verbs so you don't hand-write `@odata.bind`. `set-lookup ENTITY_SET ID NAV
RELATED_SET RELATED_ID` builds the bind PATCH; `clear-lookup ENTITY_SET ID NAV` does the
`DELETE …/$ref` (`{cleared:true}`). _Met: M02 L02._

**Revert = another update (no undo)**
Dataverse has no undo. You restore a record by writing the *old* values back over the new ones
(and clearing what you set) — which is why the safe-write loop reads originals **before** touching
anything. M02 L02 ran the full loop live (preview→commit→verify→revert), leaving the org clean.
_Met: M02 L02._

---

## Querying sets — *M02 L03*

**`query odata` result shape (v3.12.6)**
Rows come back as **`data` itself — a bare array** (this CLI unwraps OData's `value`); `meta`
carries `entity_set`, optional `count` (with `--count`), and `next_link` (with `--page-size`).
⚠️ Differs from the M01 L06 examples, which show `data.value` (pre-3.12 shape). _Met: M02 L03._

**Filtering on stored values**
A `--filter` is written in the L01 *stored* vocabulary: option-sets by **code** (`gendercode eq 1`,
not `'Male'`), lookups by their **`_x_value` GUID** (`_ownerid_value eq <guid>` — the "my records"
pattern with whoami's UserId). Operators: `eq`/`ne`/`gt`/`lt`/`ge`/`le`, `contains(f,'x')`/
`startswith`, `and`/`or`, `eq null`/`ne null`. String literals in single quotes; codes/GUIDs/dates/
null bare. _Met: M02 L03._

**`--orderby` / `--count` / `--top` vs `--page-size`**
`--orderby "fullname asc|desc"` sorts. `--count` adds the **exact, filtered** total to `meta.count`
(vs `query count`'s cached whole-table estimate, L06). `--top N` = at most N rows (a sample);
`--page-size N` = N at a time **plus** `meta.next_link` (the `@odata.nextLink` + skiptoken cookie)
when more remain. A page maxes at **5,000 rows**; no `next_link` = last page. _Met: M02 L03._

---

## FetchXML — *M02 L04*

**FetchXML (the second query language)**
Dynamics' native query language, written as an **XML document** (`<fetch><entity><attribute>
<filter><condition><order>`), run over the *same* Web API GET as OData, same `data`-array
envelope. `crm query fetchxml --xml '<…>'` or `--file q.xml`. `<entity name="contact">` uses the
**logical name**; crm resolves it to the entity-set (or pass the set positionally). More verbose
than OData for plain filtering. _Met: M02 L04._

**Aggregate & group-by (the OData-can't superpower)**
The reason to choose FetchXML: the OData Web API can't aggregate. `<fetch aggregate="true">` +
an attribute with `aggregate="count|sum|avg|min|max"` + another with `groupby="true"`, each
needing an `alias` (which becomes the output key). Buckets by the **stored code**; map codes to
labels via L01. _Met: M02 L04._

**OData vs FetchXML (when to pick)**
OData = everyday filter/select/sort/page (default — simpler, composable, scriptable). FetchXML =
① aggregation/group-by, ② deep `<link-entity>` joins, ③ running an existing **saved view**. You
rarely hand-write it — build in Advanced Find → *Download FetchXML* → `--file`. _Met: M02 L04._

**`query saved` / `query user`**
System views (`savedquery`) and personal views (`userquery`) are **stored as FetchXML**, so they
run by GUID with no XML: `crm query saved <view-id>` / `crm query user <view-id>`. _Met: M02 L04._

---

## Metadata model — read — *M03*

**The three names (+ a label)**
Every table carries three machine names and one human label. **LogicalName** (lowercase,
`contact`) = the canonical id — metadata, FetchXML `<entity name>`, `query count`, `$filter`
fields. **SchemaName** (PascalCase, `Contact`) = design-time identity, used in solution XML.
**EntitySetName** (plural, `contacts`) = the Web API URL path — `query odata`, `entity get/create`.
**DisplayName** = the localized form label ("Account"); cosmetic, never key code off it. _Met: M03 L01._

**`metadata entities`**
Lists every table's three names side by side, with `IsCustomEntity`. `--top N` caps rows;
`--custom-only` hides stock Microsoft tables — but "custom" includes managed add-ins (e.g.
`aaduser`), not only your own. The naming triad behind M01 L06's `count`-wants-singular 400-trap.
_Met: M03 L01._

**`metadata attributes` / `metadata attribute`**
`attributes <logical>` lists every column compactly (LogicalName, SchemaName, **AttributeType**,
writability flags, RequiredLevel-as-string). `attribute <logical> <col>` returns one column's full
def — including `IsPrimaryId`/`IsPrimaryName` and **RequiredLevel as an object** `{Value,
CanBeChanged,…}` (the list flattens it to a bare string). _Met: M03 L02._

**AttributeType · writability flags · RequiredLevel**
A column = name + **type** (String/Integer/DateTime/Money/Boolean/Picklist/Lookup/Uniqueidentifier
— decides how you encode the value) + **IsValidForCreate/Update** (may you set it? both false =
read-only, leave out of payloads) + **RequiredLevel** (must you? `None` / `ApplicationRequired`
(maker-set, liftable) / `SystemRequired` (platform-locked, `CanBeChanged:false`)). _Met: M03 L02._

**Shadow attribute**
A read-only String mirror the platform maintains beside every Lookup — `<lookup>name` (+ often
`<lookup>yominame` for phonetic sort), both IsValidForCreate/Update:false. Lets a query show the
related record's name without a join; it's where M02 L01's lookup name-annotation lives. You read
it, never set it (set the lookup itself via `@odata.bind`). _Met: M03 L02._

**Option set: local vs global (`IsGlobal`)**
A picklist's allowed values. **Local** (`IsGlobal:false`, Name `<table>_<column>`) belongs to one
column. **Global** (`IsGlobal:true`) is a standalone named list many columns/tables share — edit
once, every binding changes. _Met: M03 L03._

**`metadata picklist` / `list-optionsets` / `get-optionset`**
`picklist <logical> <attr>` resolves a column's options to stored **code → label** pairs (you write
the code, label is for humans); works on `statecode`/`statuscode` too; **expands bound globals by
default** (`--no-global` skips). `list-optionsets` enumerates global sets; `get-optionset <name>`
fetches one directly (no column needed). _Met: M03 L03._

**`metadata relationships` — Referenced vs Referencing**
Returns a table's links grouped **OneToMany** (this table is the parent/"one"), **ManyToOne** (this
table is the child/"many", holds the lookup FK), **ManyToMany** (symmetric peers). In 1:N/N:1:
**ReferencedEntity** = the "one"/parent pointed at; **ReferencingEntity** = the "many"/child that
physically stores the FK; **ReferencingAttribute** = the lookup column;
**ReferencingEntityNavigationPropertyName** = the `@odata.bind` target (M02 L02's
`parentcustomerid_account`). _Met: M03 L04._

**Polymorphic (customer) lookup · N:N intersect**
A polymorphic lookup (e.g. `parentcustomerid`) can point at more than one table — it appears once
per target in `ManyToOne`, each with its own `…_account` / `…_contact` nav property. **N:N** has no
FK on either side: symmetric `Entity1LogicalName`/`Entity2LogicalName` + an `IntersectEntityName`
join table; link rows with `associate`/`disassociate`, not a column write. _Met: M03 L04._

**`metadata describe` (write-readiness brief)**
ONE read-only call returning exactly what a create/update payload needs: `entity_set_name`,
`primary_id`, `primary_name`, and `writable_attributes[]` (only IsValidForCreate/Update) each with
`attribute_type` + `required_level`; picklists carry inline flat `options[{value,label}]` (+
`global_optionset_id` when global-bound); lookups carry `bind_key` (`<Nav>@odata.bind`) + `targets[]`
({logical, set_name}). The agentic contract — what Claude reads before building a write. _Met: M03 L05._

**Alternate key (`metadata keys`)**
An optional business-unique column set (email, order #) you can address a record *by* instead of
its GUID — powers **upsert by business key** (`entity upsert`). Separate from the always-present
GUID primary key. Most stock tables have none (`[]`). Defining one is M04. _Met: M03 L05._

---

## Schema authoring (write) — *M04*

**Custom table (what gets provisioned)**
Creating a table writes far more than the columns you name: an auto **primary id** GUID
(`<table>id`, SystemRequired), an auto **primary-name** column (`<prefix>_name`, String,
ApplicationRequired), the standard **system columns** (`ownerid`, `createdon`/`modifiedon`,
`statecode`/`statuscode`…), **privileges**, and the Web API **entity set**. You pick only the
display name, primary-name label, and **ownership** (`UserOwned` default / `OrganizationOwned`,
near-permanent). _Met: M04 L01._

**Publisher prefix · solution (write side)**
Every custom component is stamped with the **publisher's customization prefix** (schema name =
`<Prefix>_<Display>`) and tracked inside a **solution** (the deployable container, M06). The
profile carries both as defaults. The prefix MUST match the target solution's publisher, else
create 404s with `"solution unique name … is not valid"`. _Met: M04 L01._

**Publish (`PublishAllXml`)**
Metadata changes sit in an **unpublished** staging layer until published; only then are they live
to users/forms. crm verbs publish by default (`--publish`); defer with `--no-publish` (per verb)
or `--stage-only` (scaffold → `meta.staged=true`). Imperative verbs publish **per call**; batch
builders (`scaffold`, `apply`) publish **once** at the end. _Met: M04 L01._

**`create-entity` / `add-attribute` (imperative)**
The explicit write verbs: `create-entity --display` makes the table (envelope returns all three
names + `primary_attribute`); `add-attribute <logical> --kind …` adds one column. `--kind` palette:
string·memo·integer·bigint·decimal·double·money·boolean·datetime·picklist·multiselect·lookup·image·file.
Per-kind rules: decimal/double/**money require `--precision`**; string `--max-length`/`--format`;
boolean `--true/false-label`; datetime `--format DateOnly|DateAndTime`. _Met: M04 L02._

**Local vs global option set (write side)**
**Local** = inline picklist options on one column (`add-attribute --option value:label` or
`:label` auto-value; bare label rejected); private, not reusable. **Global** = a standalone named
set (`create-optionset`, or an `optionsets:` entry in an apply spec) reusable across columns/tables
via `--optionset-name`/`optionset_name`. A global **outlives** the tables that use it. _Met: M04 L02, L04._

**`scaffold table` (shorthand builder)**
One command builds a table + N columns, one publish: `scaffold table "Display" --column
"Disp:KIND[:opts]"`. Opts limited to `max_length, required, description, optionset_name,
target_entity` — **no precision/format/min/max/inline-options**, so decimal/double can't be
scaffolded and picklists must reference an existing global. Idempotent (if-exists=skip);
`--dry-run` (plan only) / `--stage-only` (no publish). _Met: M04 L03._

**`apply -f` (declarative desired-state)**
A reviewable YAML/JSON **spec** (`entities[]`, optional `optionsets[]`) applied with
if-exists=skip in **dependency order** (option set before the picklist that uses it), one publish
at the end. Re-applying an unchanged spec is a **no-op** (all `skipped`). Top-level `solution` must
be a **mapping** — easier to pass `--solution` flag. The agentic default: Claude writes the spec,
you review the diff, apply. _Met: M04 L04._

**`{applied, skipped, planned, failed}` report**
The standard envelope for batch builders (scaffold + apply). `applied`=created now,
`skipped`=already existed, `planned`=would create (dry-run only), `failed`=errored (with reason).
Partial-apply: resources build in order, a failure leaves prior ones created — fix and re-run
(skip recovers). _Met: M04 L01, L03._

**`export-spec` · the `_Base` companion**
Reverse of apply: reads a live table over pure GETs → an apply-consumable spec (`-o FILE`,
`--with-views/--with-relationships`). **Warns** about what it can't round-trip: local option sets
(unreadable via this API path) and read-only `*name` **VirtualType** shadow columns are dropped.
Every **money** column auto-spawns a `_Base` companion (base-currency mirror) that shows up in the
export. _Met: M04 L05._

**`delete-entity` / `delete-optionset` (clean teardown)**
Permanently delete a custom table (+ all its rows) or a global option set — **irreversible**,
`--yes` required in JSON mode (else `"aborted by user"`). Preview with `delete-entity --dry-run
--check-dependencies` → `{would_delete, can_delete, blockers[]}` (empty blockers = safe). Deleting
a table does NOT delete the global option sets it used. _Met: M04 L05._

## Relationships (write side) — *M05*

**1:N / N:1 / N:N — two real types**
There are only **two** relationship types to *create*: **1:N** (one-to-many) and **N:N**
(many-to-many). **N:1** (many-to-one) is not a third type — it's a 1:N *viewed from the child*.
A 1:N is physically a **lookup column on the referencing (N/child) side**; an N:N is a hidden
**intersect table** of GUID pairs. Hence two create verbs. _Met: M05 L01._

**`create-one-to-many` (atomic 1:N + lookup)**
One call creates the relationship metadata **and** its lookup column atomically (POST to
`RelationshipDefinitions`). Required: `--schema-name` (the relationship), `--referenced-entity`
(the "1"/parent), `--referencing-entity` (the "N"/child, gets the lookup), `--lookup-schema`,
`--lookup-display`. Both tables must already exist. Envelope: `{created, kind:"OneToMany",
schema_name, referenced_entity, referencing_entity, referencing_attribute, relationship_id,
solution, published}`. `referencing_attribute` = the lookup column logical name (lowercase of
`--lookup-schema`). Supports global `--dry-run` (prints full body + `references[]` existence
check). _Met: M05 L02 — crm v4.12.0._

**Cascade behaviors (parental vs referential)**
Six actions decide what happens to children when the parent changes: **Delete, Assign, Reparent,
Share, Unshare, Merge** (CLI `--cascade-*`). Cascade types: `NoCascade, Cascade, Active,
UserOwned` (+ `RemoveLink, Restrict` for Delete only; Merge only `Cascade`/`NoCascade`). Named
bundles: **Parental** (all Cascade — children die/move with parent), **Referential** (Delete=
RemoveLink, rest NoCascade — independent), **Referential, Restrict Delete** (Delete=Restrict —
blocks parent delete while children exist). **CLI default = referential** (`Delete:RemoveLink`,
rest `NoCascade`). Limits: a custom table can't be the cascading *parent* of a system table; one
parental rel per table pair. _Met: M05 L03._

**`update-relationship` (retrieve-merge-write)**
Change cascade behaviors (or menu config) on an existing relationship in place — reads current
definition, applies only the `--cascade-*` flags you pass, writes back. Envelope `{updated, path,
schema_name, published}`. Reversible (set `--cascade-delete RemoveLink` to demote to referential).
Publishes by default. _Met: M05 L03._

**A lookup's three runtime names**
Same lookup, three forms: **logical name** (`ag_accountid` — what metadata shows), **navigation
property** (`ag_AccountId` = the lookup schema name — what you *write/bind/expand* with,
**case-sensitive**), and the **read form** (`_ag_accountid_value` — how the GUID comes back in
query results). Write through the nav property; read the GUID from `_..._value`. _Met: M05 L04._

**Set a 1:N link · `@odata.bind` / `set-lookup` / `clear-lookup`**
Set the lookup on **create** by binding the nav property: `"ag_AccountId@odata.bind":
"/accounts(<guid>)"` (path = entity *set* + GUID, never a name). On an **existing** row use
`entity set-lookup ENTITY_SET ID NAV RELATED_SET RELATED_ID` (PATCH @odata.bind) / `clear-lookup
ENTITY_SET ID NAV` (DELETE /$ref). Read the link via `$expand` on the nav property (returns one
object). _Met: M05 L04._

**`create-many-to-many` (N:N) · `entity associate`**
N:N create: `--schema-name --entity1 --entity2 --intersect-entity`. **No** lookup, **no** cascade
(rows are peers); `entity1`/`entity2` interchangeable. Envelope `{created, kind:"ManyToMany",
schema_name, intersect_entity, relationship_id, …}`. Link rows with **`entity associate
TARGET_SET TARGET_ID NAV RELATED_SET RELATED_ID`** where **NAV = the relationship schema name**
(Dataverse writes the intersect pair); `disassociate` removes one link. `$expand` the nav property
returns an **array**. If the link must carry data (role, %), use a **manual intersect** — a real
table with two 1:N lookups — not a stock N:N. _Met: M05 L05._

**`entity children` (parent-side counts)**
Per-relationship related-row counts for the 1:N relationships where a record is the parent:
`entity children ENTITY_SET ID [--filter-entities REGEX] [--non-empty]`. Each row: child entity,
referencing attribute, child set, count. Read-only (chunked `$batch`). _Met: M05 L04._

**`delete-relationship` (clean teardown)**
Delete a 1:N or N:N by schema name; for a 1:N it **also removes the lookup column**. `--yes`
required in JSON mode. Preview with `--dry-run --check-dependencies` → `{would_delete, can_delete,
blockers[]}` (empty blockers = safe; a non-empty list, e.g. lookup on a form, must be cleared
first). Teardown order: **relationships before the tables** they connect. _Met: M05 L05._
