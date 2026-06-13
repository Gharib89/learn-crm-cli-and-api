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

**`@odata.context`**
A URL the server echoes back in every response, showing the exact host + API version that
answered. The proof of *which org* you actually hit — checked before any mutation. _Met: M01 L02._

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
an array under `data.value` (+ `meta.count`), even for one or zero matches. Both are GETs.
_Met: M01 L06._

**`--select` / `--filter` / `--top`**
The query workhorses. `--select` = which columns (omit ⇒ every column — always name
them). `--filter` = which rows in OData syntax (`eq`, `ne`, `gt`/`lt`, `contains(f,'x')`,
`and`/`or`). `--top` = max rows. Empty result = `value:[]`, `count:0`, still `ok:true`,
exit 0 ("no match" is an answer, not a failure). _Met: M01 L06._

**`@odata.etag`**
A row-version tag (`W/"2503282"`) returned on reads. The value the server compares for
optimistic concurrency — the other half of L04's update `If-Match` header. _Met: M01 L06._

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
