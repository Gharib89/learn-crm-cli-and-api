# learn-crm-cli-and-api

A hands-on course on the [`crm` CLI](https://github.com/Gharib89/crm) and the Dynamics 365 CE
Dataverse Web API — for D365 beginners who'd rather drive customizations through a repeatable,
reviewable, agentic workflow (Claude Code + the `crm` CLI) than click through the GUI.

**▶ Live site:** https://gharib89.github.io/learn-crm-cli-and-api/

## What's here

- `lessons/` — self-contained HTML lessons, grouped by milestone. Each carries a
  `#lesson-meta` JSON block the build reads.
- `GLOSSARY.md` — the learner's growing D365/crm vocabulary (rendered to a Glossary page).
- `MISSION.md`, `CONTEXT.md`, `RESOURCES.md`, `docs/` — the learning workspace's mission,
  domain language, trusted sources, and agent/ADR docs.

## How the site builds

`python scripts/build.py` reads `lessons/*.html` + `GLOSSARY.md` and writes the deployable
site to `_site/` (gitignored): a generated home page, a glossary page, and every lesson with a
shared navbar injected. GitHub Actions runs this on every push to `main` and deploys `_site/`
to GitHub Pages.

Build locally:

```bash
pip install -r requirements.txt
python scripts/build.py
# open _site/index.html
```

## Credits

Design colors + fonts mirror the [crm CLI docs](https://crm-cli-docs.pages.dev/) (itWorx brand).
