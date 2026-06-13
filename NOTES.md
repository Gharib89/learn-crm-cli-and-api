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
- **L03** (next) — the `{ok, data, meta}` envelope + exit codes 0/1/2.

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
