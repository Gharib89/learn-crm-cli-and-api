## crm CLI source

The `crm` CLI these lessons teach is developed at <https://github.com/Gharib89/crm>.
When answering a question about its behavior, flags, or internals, consult that source —
read the implementation, don't guess. A local clone path may be recorded in
`CLAUDE.local.md` (gitignored).

### The CLI is evolving — versioned and subject to change

Behavior, flags, the `{ok,data,meta}` envelope, and result shapes can shift between releases.
A real example: **v3.9.x → v3.12.x** changed `query odata` from a `data.value` wrapper to a
**bare `data` array**, and made `meta.count` **opt-in via `--count`** (M01 L06 was authored on
the old shape and corrected on 2026-06-17). Treat every lesson as version-pinned to the CLI it
was captured against. Therefore, as a standing rule:

- **Live-verify before authoring.** Run every command/flag against the installed CLI
  (`crm --version` first) and capture real output. Never trust prose — skill docs, older
  lessons, or memory — over the running binary when they disagree.
- **Capture the new info.** When you notice drift, record old-vs-new behavior **with the
  version** in `NOTES.md`, and add/refresh the affected `GLOSSARY.md` term.
- **Update affected lessons.** Older lessons go stale silently. When a change touches something
  a published lesson shows (a flag, an output shape, an exit code), fix that lesson surgically,
  note the correction + version + date in its footer `.ft` line, rebuild, and re-deploy — don't
  leave contradictory shapes across the milestone.
- **Footer the version.** Each lesson's footer records the capture date; when output is
  version-sensitive, name the verified `crm` version too.

## Agent skills

### Issue tracker

Issues and PRDs live as GitHub issues, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles mapped to their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Lessons site (GitHub Pages)

The lessons are published as a static site at
https://gharib89.github.io/learn-crm-cli-and-api/.

- **Build:** `python scripts/build.py` reads `lessons/*.html` + `GLOSSARY.md` and writes the
  site to `_site/`. `_site/` is **generated and gitignored — never edit or commit it.**
- **Lesson metadata:** every lesson MUST embed one `<script type="application/json"
  id="lesson-meta">` block (milestone, lesson, title, slug, topics, summary, order, status).
  It is the build's source of truth — no meta block ⇒ the build fails loudly.
- **Navbar:** the shared navbar is **build-injected** into every lesson. Do NOT hand-add a
  navbar to lesson source.
- **Next-up link:** every lesson ends with a `<div class="next reveal">` block (narrative:
  "what's next + why"). The build **auto-injects** a clickable `Continue → Lesson NN · Title`
  link into it, computed from milestone + `order`, and **only when the next lesson exists** —
  so adding a new lesson wires the prior lesson's link automatically. Do NOT hand-add a
  next-lesson `<a>`. Any live-/teach-session-only call to action (e.g. *Just say "next
  lesson"*) MUST be wrapped in `<span class="live-only">…</span>`: the build strips it from
  the published site but it stays visible in the raw lesson used during live teaching.
- **Skin:** the itWorx/Roboto design system lives in `assets/site.css`. New lessons link it
  (`../assets/site.css`, last in `<head>`) and use Roboto / Roboto Mono — matching the upstream
  crm docs site. (Supersedes the older "frontend-design / distinctive aesthetic" note.)
- **Deploy:** automatic via `.github/workflows/pages.yml` on push to `main`.
- **Privacy rule:** never write the real cloud org URL or internal on-prem host into any
  committed file. Lessons use the consistent example env instead:
  `https://orgexample.crm.dynamics.com` (cloud) and `http://crm.contoso.local/Contoso`
  (on-prem). Live `/teach` sessions still run against the real orgs — only the published
  artifacts use the example env.
