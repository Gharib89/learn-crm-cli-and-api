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
