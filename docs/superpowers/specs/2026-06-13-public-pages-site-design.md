# Public GitHub Pages site for the crm-CLI lessons — Design

**Date:** 2026-06-13
**Status:** Approved (design); pending implementation plan
**Repo:** `Gharib89/learn-crm-cli-and-api` (currently private → going public)

## Problem

The lessons (`lessons/*.html`) are complete, self-contained HTML but there is no way to
browse or share them. Goal: make the repo public and publish a branded GitHub Pages site
that presents the lessons as a shareable course — a home page with general info + goal, a
persistent top navbar (home + jump to any lesson), lessons grouped by milestone, topic
facets, and a rendered Glossary page — visually matching the upstream crm docs site
(`crm-cli-docs.pages.dev`).

## Success criteria

1. `git grep` over **all** refs finds zero sensitive strings (the real cloud org-id prefix
   `org<id>` and the internal host `internalcrm.<internal>.local` / `<internal>.local` — exact
   values read from `NOTES.md` at scrub time; not reproduced here to keep this spec publishable).
2. `python scripts/build.py` produces `_site/index.html` and `_site/lessons/<each>.html`,
   each lesson carrying the shared navbar with both lessons listed.
3. GitHub Pages workflow is green; `https://gharib89.github.io/learn-crm-cli-and-api/` serves
   the home page.
4. Navbar navigates home ↔ any lesson; the topic filter narrows the timeline; both lessons
   render in the itWorx skin with their quizzes still working.
5. `_site/glossary.html` renders `GLOSSARY.md` in the itWorx skin; "Glossary" is reachable
   from the navbar on every page.
6. Repo is public.

## Decisions (locked during brainstorming)

| Topic | Decision |
|---|---|
| Privacy | Scrub working tree **and** squash history, then publish all docs sanitized |
| Build | Generated index + CI (GitHub Actions), not a static-site generator |
| Metadata | Embedded per-lesson JSON block (single source of truth) |
| Home scope | Published-only, grows organically (no full roadmap UI yet) |
| Layout | C — vertical milestone timeline + top navbar + intro/goal section |
| Palette/font | itWorx indigo/red + Roboto, **whole site** (re-skin existing lessons); new standard |
| Navbar sync | Build injects nav into each lesson → deploy `_site/` via Actions |
| Build language | Python + one dep (`markdown`) for rendering MD pages; otherwise stdlib |
| Glossary | Rendered from `GLOSSARY.md` → `_site/glossary.html`; "Glossary" added to navbar |
| Agent docs | `CLAUDE.md` updated so future Claude understands the site, build & authoring standard |
| Search | Dropped for v1 (YAGNI) |

## A. Privacy scrub (gate before "public")

The real cloud org URL and internal on-prem host appear in **four** tracked files — and two of
them are *published site content*:
- `NOTES.md` — org URL + internal host
- `GLOSSARY.md` — org URL (example)
- `lessons/0001-install-configure-profiles.html` — org URL + internal host in the profile-list
  output (multiple rows, incl. the `crmworx` profile)
- `lessons/0002-the-whoami-handshake.html` — org URL in the livechip target + body prose

They span the current history (commits `a22d2a9` and `5608a43`); HEAD now has **5 commits**.
The two real values are read from the repo during implementation; they are **not** written into
this spec, the README, or any committed file (doing so would re-leak them when public).

Steps:
1. Working tree: replace every occurrence of the live cloud org URL →
   `https://orgexample.crm.dynamics.com` and the internal on-prem URL →
   `http://crm.contoso.local/Contoso` (a consistent fictitious **example env** — Contoso, reads
   naturally as captured output), across all four files above. Scan every tracked + new file
   (`git grep` for the real patterns) to confirm none missed. Live `/teach` still runs against
   the real orgs; only the published artifacts use the example env, and all new lessons adopt it
   from the start.
2. Squash the entire current history into one clean initial commit (no commit carries the
   sensitive strings).
3. Verify: `git grep` the two real patterns (org-id prefix + internal domain) across
   `$(git rev-list --all)` — must return empty.
4. Make repo public only **after** the verify passes.

## B. Design system — `assets/site.css` (shared)

Single source of truth for the itWorx look, linked by `index.html` and every lesson via a
relative path (works under `file://` for local authoring).

Tokens (sampled from the docs site's `extra.css`):

```
--indigo:#1B1F8F;  --indigo-royal:#353A9C;  --indigo-dark:#12156B;
--red:#C83428;     --red-light:#E0594D;
--bg:#ffffff;      --surface:#f4f5fa;        --surface2:#eceefb;
--ink:rgba(0,0,0,.87); --ink-soft:rgba(0,0,0,.6); --ink-mute:rgba(0,0,0,.44);
--line:#e3e5f2;    --line2:#d3d6ec;
```

Fonts: **Roboto** (300/400/500/700 + italic) body, **Roboto Mono** (400/500/700) code —
loaded from Google Fonts. `site.css` owns: tokens, base typography, the navbar, and the
shared lesson furniture (eyebrow, callouts, cards, code/terminal, quiz, footer). Lesson-unique
layout stays inline in each lesson.

Code styling: keep a **dark treatment for shell/`crm` command transcripts** (readable signal),
Material light-gray for inline code. (Open to all-light if preferred — minor.)

## C. Home page — generated `_site/index.html`, layout C

(No committed root `index.html`; the build generates it into `_site/` from the lesson
metadata. Source of truth = `scripts/build.py` + the `#lesson-meta` blocks.)

Top→bottom: indigo Material app bar (the navbar) → eyebrow + hero title → **intro paragraph +
"The goal" callout** (sourced from `MISSION.md`) → facts strip (beginner-first · source-cited ·
cloud + on-prem · N lessons live) → section rule → **milestone timeline**: a vertical spine
where each milestone is a node and its lessons hang off as cards (lesson no, title, topic tags,
→). Future milestones render dimmed as "coming next." → footer.

Topic axis: per-lesson topic tags **plus a lightweight client-side filter** — a row of topic
chips; clicking one shows only lessons carrying that topic (small inline JS over the rendered
cards). Published-only: the index shows only milestones/lessons that exist.

### Glossary page — generated `_site/glossary.html`

`GLOSSARY.md` (the learner's growing D365/crm vocabulary, already grouped by milestone) is
rendered to a styled page in the itWorx skin, carrying the same navbar. The build converts the
markdown with the `markdown` library; `GLOSSARY.md` stays the single source of truth (kept as
markdown so the `/teach` flow keeps maintaining it). Terms and milestone sections map straight
to the page; an in-page table of contents is deferred (YAGNI).

## D. Navbar — shared, build-injected

Markup + styling defined once (styling in `site.css`). Contents: brand → home · **Lessons ▾**
dropdown (grouped by milestone, every lesson) · Glossary · Resources · GitHub link. Identical
on home, the glossary page, and every lesson page. Injected by the build (not committed into
lesson source).

Link targets: brand + "Home" → site root; "Lessons" entries → each lesson page; "Glossary" →
`/glossary.html`; "Resources" → the repo's `RESOURCES.md` on GitHub (v1 — no rendered Resources
page); "GitHub" → the repo.

## E. Lesson metadata contract

Each lesson embeds exactly one block — the single source the build reads:

```html
<script type="application/json" id="lesson-meta">
{ "milestone": {"num": 1, "name": "Foundations & Connect"},
  "lesson": 1,
  "title": "Install, Configure & the Profile Lifecycle",
  "slug": "install-configure-profiles",
  "topics": ["install","profiles","auth"],
  "summary": "Saved connections: URL + auth scheme + secret storage.",
  "order": 1,
  "status": "published" }
</script>
```

Build behavior on missing/invalid meta: fail loudly (non-zero exit, name the file) — never
silently skip a lesson.

## F. Build & deploy

`scripts/build.py` (Python stdlib + the `markdown` lib for MD pages). Pure function:
read → transform → write `_site/`.

1. Glob `lessons/*.html`; extract + JSON-parse each `#lesson-meta`.
2. Group by milestone, order by `order`/lesson number.
3. Render `_site/index.html` (hero, intro/goal, facts, timeline, topic filter) from the
   metadata.
4. For each lesson: inject the shared `<nav>` (built from the full lesson list) and copy to
   `_site/lessons/<file>`.
5. Render `GLOSSARY.md` → `_site/glossary.html` (markdown → HTML, wrapped in the itWorx page
   shell + the same injected `<nav>`).
6. Copy `assets/` into `_site/assets/`.

Dependency: `markdown` only, pinned in `requirements.txt`. Local build = `pip install -r
requirements.txt` then `python scripts/build.py` (the user already runs a Python venv).

`.github/workflows/pages.yml`: trigger on push to `main`; checkout → setup Python →
`pip install -r requirements.txt` → `python scripts/build.py` → `actions/upload-pages-artifact`
(path `_site`) → `actions/deploy-pages`. Repo Settings → Pages source = **GitHub Actions**.
`_site/` is gitignored. Adding a lesson later = author the file with its meta block + push; CI
rebuilds every nav menu automatically.

## G. Re-skin the 2 existing lessons

`lessons/0001-install-configure-profiles.html`, `lessons/0002-the-whoami-handshake.html`:
link `assets/site.css`, drop the now-duplicated inline tokens, swap fonts to Roboto/Roboto
Mono, restyle components to the itWorx palette. **Keep** all content, the quiz + its script,
the references, and the reveal animations. Add the `#lesson-meta` block. Do not hand-add the
navbar (build injects it). **Also scrub** the real org URL/host embedded in these lessons to
the §A placeholders — this is published content, so the scrub and the re-skin land together.

## H. Repo hygiene

- New public `README.md`: what this is, live link, how to read, how lessons build, links to
  the crm repo + docs site.
- Update `NOTES.md` authoring preference → the new itWorx/Roboto standard + required
  `#lesson-meta` block + build-injected navbar.
- Update the `lesson-authoring-prefs` memory to match the new standard.
- **Update `CLAUDE.md`** so future Claude understands the repo's new shape. Add a "Lessons
  site (GitHub Pages)" section covering: the site builds from `lessons/*.html` + `GLOSSARY.md`
  via `python scripts/build.py` into `_site/` (generated, gitignored — never edit/commit
  `_site/`); each lesson must carry a `#lesson-meta` JSON block (the build's source of truth);
  the navbar is **build-injected** (don't hand-add it to lessons); the itWorx/Roboto skin lives
  in `assets/site.css`; deploy is automatic via GitHub Actions on push to `main`; and the
  **privacy rule** — never write the real cloud org URL or internal on-prem host into any
  committed file; lessons use the example env (`orgexample.crm.dynamics.com` /
  `crm.contoso.local/Contoso`). Live `/teach` still uses the real orgs.
- `.gitignore`: add `_site/` (and `.superpowers/` — already added).
- No custom domain (default `gharib89.github.io/learn-crm-cli-and-api`).

## I. File inventory

New:
- `assets/site.css`
- `scripts/build.py`
- `requirements.txt` (`markdown`)
- `.github/workflows/pages.yml`
- `README.md`
- `docs/superpowers/specs/2026-06-13-public-pages-site-design.md` (this file)

Generated (into `_site/`, gitignored — not committed): `index.html`, `glossary.html`,
`lessons/*.html` (nav-injected), `assets/*`.

Modified:
- `lessons/0001-install-configure-profiles.html`, `lessons/0002-the-whoami-handshake.html`
  (re-skin + meta block + **scrub embedded org URL/host**)
- `NOTES.md` (scrub + authoring standard), `GLOSSARY.md` (scrub)
- `CLAUDE.md` (new "Lessons site" section)
- `.gitignore` (`_site/`)

## J. Out of scope (deferred)

Full M01–M09 roadmap UI · site search · dark-mode toggle · SSG migration · per-lesson
prev/next beyond the navbar.

## K. Verification plan

1. `pip install -r requirements.txt` then `python scripts/build.py` exits 0; `_site/index.html`
   lists M01 with L01 + L02; each `_site/lessons/*.html` and `_site/glossary.html` contains
   `<nav>` with both lessons + the Glossary link.
2. Open `_site/index.html` locally (Windows Chrome): navbar, intro/goal, timeline, topic
   filter, and the Glossary link all render and work; `_site/glossary.html` shows the rendered
   vocabulary.
3. `git grep` privacy check empty across all refs.
4. After push: Pages workflow green; live URL serves home; navigate home↔lessons↔glossary;
   quizzes work.
5. Repo visibility = public.
