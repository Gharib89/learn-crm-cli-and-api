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
- **Skin:** the itWorx/Roboto design system lives in `assets/site.css`. New lessons link it
  (`../assets/site.css`, last in `<head>`) and use Roboto / Roboto Mono — matching the upstream
  crm docs site. (Supersedes the older "frontend-design / distinctive aesthetic" note.)
- **Deploy:** automatic via `.github/workflows/pages.yml` on push to `main`.
- **Privacy rule:** never write the real cloud org URL or internal on-prem host into any
  committed file. Lessons use the consistent example env instead:
  `https://orgexample.crm.dynamics.com` (cloud) and `http://crm.contoso.local/Contoso`
  (on-prem). Live `/teach` sessions still run against the real orgs — only the published
  artifacts use the example env.
