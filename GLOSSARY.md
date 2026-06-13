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
