# Public Pages Site for the crm-CLI Lessons — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the crm-CLI lessons as a branded GitHub Pages site (home + navbar + glossary), re-skinned to the itWorx/Roboto look of the upstream crm docs, after scrubbing all sensitive infra strings from the repo and its history, then make the repo public.

**Architecture:** A small Python build (`scripts/build.py`) reads each lesson's embedded `#lesson-meta` JSON, generates `_site/index.html` + `_site/glossary.html`, and injects a shared navbar into every lesson — writing the deployable site to `_site/`. GitHub Actions runs the build on push to `main` and deploys `_site/` to Pages. Shared styling lives in `assets/site.css`; lessons keep their inline component CSS but re-point their design tokens + fonts to itWorx/Roboto. Privacy is enforced by a scrub-then-squash step gated before the repo goes public.

**Tech Stack:** Python 3.12 stdlib + `markdown` (single dep), HTML/CSS (no framework), GitHub Actions Pages deploy, `gh` CLI for repo/Pages administration.

**Spec:** `docs/superpowers/specs/2026-06-13-public-pages-site-design.md`

---

## File Structure

| Path | Responsibility | New/Mod |
|---|---|---|
| `requirements.txt` | Pin the one build dep (`markdown`) | New |
| `scripts/build.py` | Read lesson metadata + GLOSSARY.md → render `_site/` (index, glossary, nav-injected lessons, assets) | New |
| `tests/test_build.py` | Unit tests for the build's pure functions | New |
| `assets/site.css` | itWorx design system: tokens, lesson-token aliases, base type, navbar, index/timeline/glossary components | New |
| `.github/workflows/pages.yml` | Build + deploy to Pages on push | New |
| `README.md` | Public landing doc: what this is, live link, how to build | New |
| `lessons/0001-install-configure-profiles.html` | Re-skin (link site.css, Roboto, recolor) + add `#lesson-meta` | Mod |
| `lessons/0002-the-whoami-handshake.html` | Re-skin + add `#lesson-meta` | Mod |
| `CLAUDE.md` | Add "Lessons site" section for future agents | Mod |
| `NOTES.md` | Authoring-standard update | Mod |
| `GLOSSARY.md`, `NOTES.md`, both lessons | Privacy scrub (org URL / on-prem host → placeholders) | Mod |
| `.gitignore` | Add `_site/` | Mod |

Generated into `_site/` (gitignored, never committed): `index.html`, `glossary.html`, `lessons/*.html`, `assets/*`.

---

## Task 1: Project scaffold

**Files:**
- Create: `requirements.txt`, `tests/test_build.py` (stub), `scripts/build.py` (empty)
- Modify: `.gitignore`

- [ ] **Step 1: Create `requirements.txt`**

```
markdown==3.7
```

- [ ] **Step 2: Add `_site/` to `.gitignore`**

Append a line to `.gitignore`:

```
_site/
```

- [ ] **Step 3: Create empty module files**

```bash
cd /home/gharib/wip/learn/learn-crm-cli-and-api
mkdir -p scripts tests
: > scripts/build.py
```

- [ ] **Step 4: Install the dependency**

Run: `pip install -r requirements.txt`
Expected: `markdown` installs without error. Confirm: `python -c "import markdown; print(markdown.version)"` prints `3.7`.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore scripts/build.py
git commit -m "chore: scaffold Pages build (requirements, scripts dir, gitignore _site)"
```

---

## Task 2: Add `#lesson-meta` to both lessons

The build's single source of truth. Insert one JSON block per lesson, just before `</body>`.

**Files:**
- Modify: `lessons/0001-install-configure-profiles.html`, `lessons/0002-the-whoami-handshake.html`

- [ ] **Step 1: Add the meta block to lesson 0001**

Insert immediately before the closing `</body>` tag of `lessons/0001-install-configure-profiles.html`:

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

- [ ] **Step 2: Add the meta block to lesson 0002**

Insert immediately before the closing `</body>` tag of `lessons/0002-the-whoami-handshake.html`:

```html
<script type="application/json" id="lesson-meta">
{ "milestone": {"num": 1, "name": "Foundations & Connect"},
  "lesson": 2,
  "title": "The WhoAmI Handshake",
  "slug": "the-whoami-handshake",
  "topics": ["connection","identity","web-api"],
  "summary": "Prove which live org answers, and who you are to it.",
  "order": 2,
  "status": "published" }
</script>
```

- [ ] **Step 3: Verify both parse as JSON**

Run:
```bash
python - <<'PY'
import json, re, pathlib
rx = re.compile(r'<script[^>]*id=["\']lesson-meta["\'][^>]*>(.*?)</script>', re.DOTALL)
for f in pathlib.Path("lessons").glob("*.html"):
    m = rx.search(f.read_text())
    assert m, f"{f}: no meta"
    d = json.loads(m.group(1))
    print(f.name, "->", d["milestone"]["num"], d["lesson"], d["title"])
PY
```
Expected: two lines printing milestone/lesson/title, no assertion error.

- [ ] **Step 4: Commit**

```bash
git add lessons/0001-install-configure-profiles.html lessons/0002-the-whoami-handshake.html
git commit -m "feat: add lesson-meta blocks to M01 lessons"
```

---

## Task 3: Build — metadata extraction + lesson loading (TDD)

**Files:**
- Modify: `scripts/build.py`
- Test: `tests/test_build.py`

- [ ] **Step 1: Write the failing tests**

Write `tests/test_build.py`:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import pytest
import build

LESSON_A = (
    '<html><head></head><body><h1>x</h1>'
    '<script type="application/json" id="lesson-meta">'
    '{"milestone":{"num":1,"name":"Foundations & Connect"},"lesson":1,'
    '"title":"Install","slug":"install","topics":["install","auth"],'
    '"summary":"S1","order":1,"status":"published"}'
    '</script></body></html>'
)

def test_extract_meta_returns_dict():
    m = build.extract_meta(LESSON_A)
    assert m["lesson"] == 1
    assert m["milestone"]["name"] == "Foundations & Connect"
    assert m["topics"] == ["install", "auth"]

def test_extract_meta_missing_raises():
    with pytest.raises(ValueError):
        build.extract_meta("<html><body>no meta</body></html>")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_build.py -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'extract_meta'`.

- [ ] **Step 3: Implement extraction + loading**

Write `scripts/build.py`:

```python
#!/usr/bin/env python3
"""Build the static lessons site into _site/ from lessons/*.html + GLOSSARY.md."""
import json
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
ASSETS_DIR = ROOT / "assets"
GLOSSARY_MD = ROOT / "GLOSSARY.md"
OUT = ROOT / "_site"

REPO_URL = "https://github.com/Gharib89/learn-crm-cli-and-api"
RESOURCES_URL = f"{REPO_URL}/blob/main/RESOURCES.md"

META_RE = re.compile(
    r'<script[^>]*id=["\']lesson-meta["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
BODY_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)


def extract_meta(html):
    m = META_RE.search(html)
    if not m:
        raise ValueError('missing <script id="lesson-meta"> block')
    return json.loads(m.group(1))


def load_lessons(lessons_dir):
    lessons = []
    for path in sorted(lessons_dir.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        try:
            meta = extract_meta(html)
        except ValueError as e:
            raise SystemExit(f"build: {path.name}: {e}")
        except json.JSONDecodeError as e:
            raise SystemExit(f"build: {path.name}: invalid lesson-meta JSON: {e}")
        meta["file"] = path.name
        meta["html"] = html
        lessons.append(meta)
    return lessons
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_build.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_build.py
git commit -m "feat: build extracts lesson-meta and loads lessons"
```

---

## Task 4: Build — milestone grouping + nav HTML (TDD)

**Files:**
- Modify: `scripts/build.py`, `tests/test_build.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_build.py`:

```python
LESSON_B = (
    '<html><head></head><body>'
    '<script type="application/json" id="lesson-meta">'
    '{"milestone":{"num":1,"name":"Foundations & Connect"},"lesson":2,'
    '"title":"WhoAmI","slug":"whoami","topics":["identity"],'
    '"summary":"S2","order":2,"status":"published"}'
    '</script></body></html>'
)

def _two_lessons():
    a = build.extract_meta(LESSON_A); a["file"] = "0001-install.html"
    b = build.extract_meta(LESSON_B); b["file"] = "0002-whoami.html"
    return [b, a]  # deliberately out of order

def test_group_by_milestone_orders_lessons():
    groups = build.group_by_milestone(_two_lessons())
    assert len(groups) == 1
    assert groups[0]["num"] == 1
    assert [L["lesson"] for L in groups[0]["lessons"]] == [1, 2]

def test_nav_html_lists_lessons_and_links():
    nav = build.nav_html(_two_lessons(), prefix="../")
    assert "Install" in nav and "WhoAmI" in nav
    assert 'href="../lessons/0001-install.html"' in nav
    assert 'href="../glossary.html"' in nav
    assert "M01 · Foundations & Connect" in nav
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_build.py -v`
Expected: FAIL — `module 'build' has no attribute 'group_by_milestone'`.

- [ ] **Step 3: Implement grouping + nav**

Append to `scripts/build.py`:

```python
def group_by_milestone(lessons):
    groups = {}
    for lesson in lessons:
        ms = lesson["milestone"]
        g = groups.setdefault(ms["num"], {"num": ms["num"], "name": ms["name"], "lessons": []})
        g["lessons"].append(lesson)
    ordered = [groups[k] for k in sorted(groups)]
    for g in ordered:
        g["lessons"].sort(key=lambda L: L.get("order", L["lesson"]))
    return ordered


def nav_html(lessons, prefix):
    items = []
    for g in group_by_milestone(lessons):
        items.append(f'<div class="navmenu-label">M{g["num"]:02d} · {g["name"]}</div>')
        for L in g["lessons"]:
            items.append(
                f'<a href="{prefix}lessons/{L["file"]}">'
                f'<span class="navmenu-no">L{L["lesson"]:02d}</span>'
                f'<span class="navmenu-t">{L["title"]}</span></a>'
            )
    menu = "\n      ".join(items)
    return f"""<nav class="site-nav">
  <a class="brand" href="{prefix}index.html"><span class="brand-gem">c</span>crm·learn</a>
  <span class="nav-spacer"></span>
  <a class="navlink" href="{prefix}index.html">Home</a>
  <div class="navdrop">
    <button class="navlink navtrigger" type="button" aria-haspopup="true">Lessons ▾</button>
    <div class="navmenu">
      {menu}
    </div>
  </div>
  <a class="navlink" href="{prefix}glossary.html">Glossary</a>
  <a class="navlink" href="{RESOURCES_URL}">Resources</a>
  <a class="navlink nav-gh" href="{REPO_URL}">GitHub ↗</a>
</nav>"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_build.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_build.py
git commit -m "feat: build groups lessons by milestone and renders navbar"
```

---

## Task 5: Build — nav injection into lessons (TDD)

**Files:**
- Modify: `scripts/build.py`, `tests/test_build.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build.py`:

```python
def test_inject_nav_after_body():
    out = build.inject_nav("<html><body><h1>hi</h1></body></html>", "<nav>NAV</nav>")
    assert "<body><nav>NAV</nav>" in out.replace("\n", "")
    assert "<h1>hi</h1>" in out

def test_inject_nav_without_body_raises():
    with pytest.raises(SystemExit):
        build.inject_nav("<html>no body</html>", "<nav>NAV</nav>")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_build.py -v`
Expected: FAIL — `module 'build' has no attribute 'inject_nav'`.

- [ ] **Step 3: Implement injection**

Append to `scripts/build.py`:

```python
def inject_nav(html, nav):
    if not BODY_RE.search(html):
        raise SystemExit("build: lesson missing <body>")
    return BODY_RE.sub(lambda m: m.group(1) + "\n" + nav, html, count=1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_build.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_build.py
git commit -m "feat: build injects navbar after <body> in each lesson"
```

---

## Task 6: Build — page shell, index render, glossary render (TDD)

**Files:**
- Modify: `scripts/build.py`, `tests/test_build.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_build.py`:

```python
def test_render_index_has_lessons_and_topics():
    html = build.render_index(_two_lessons())
    assert "Install" in html and "WhoAmI" in html
    assert 'data-topic="install"' in html        # topic filter chip
    assert 'data-topics="install auth"' in html  # card facet
    assert 'href="lessons/0001-install.html"' in html
    assert "The goal" in html                     # intro/goal block
    assert "assets/site.css" in html

def test_render_glossary_renders_markdown_and_nav():
    html = build.render_glossary("## Terms\n\n**Profile**\nA saved connection.\n", _two_lessons())
    assert "<h2" in html and "Profile" in html
    assert 'class="site-nav"' in html
    assert "assets/site.css" in html
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_build.py -v`
Expected: FAIL — `module 'build' has no attribute 'render_index'`.

- [ ] **Step 3: Implement the page shell + renderers**

Append to `scripts/build.py`:

```python
LEAD = (
    "A hands-on course on the <em>crm CLI</em> and the Dataverse Web API — built for "
    "D365 beginners who'd rather drive customizations through a <em>repeatable, reviewable</em> "
    "agentic workflow than click through the GUI."
)
GOAL = (
    "Take a real customization requirement and ship it end-to-end with Claude Code + the crm "
    "CLI — and understand the D365 platform underneath as you go."
)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_prefix}assets/site.css">
</head>
<body>
{nav}
{body}
</body>
</html>
"""


def _all_topics(lessons):
    seen = []
    for L in lessons:
        for t in L.get("topics", []):
            if t not in seen:
                seen.append(t)
    return seen


def render_index(lessons):
    nav = nav_html(lessons, "")
    chips = '<button class="topic-chip is-on" data-topic="all">all</button>' + "".join(
        f'<button class="topic-chip" data-topic="{t}">{t}</button>' for t in _all_topics(lessons)
    )
    nodes = []
    for g in group_by_milestone(lessons):
        cards = []
        for L in g["lessons"]:
            tags = "".join(f'<span class="lc-tag">{t}</span>' for t in L.get("topics", []))
            cards.append(
                f'<a class="lcard" href="lessons/{L["file"]}" data-topics="{" ".join(L.get("topics", []))}">'
                f'<span class="lc-no">L{L["lesson"]:02d}</span>'
                f'<span class="lc-body"><span class="lc-t">{L["title"]}</span>'
                f'<span class="lc-sum">{L.get("summary", "")}</span>'
                f'<span class="lc-tags">{tags}</span></span>'
                f'<span class="lc-arrow">→</span></a>'
            )
        nodes.append(
            f'<div class="ms-node"><div class="ms-label">M{g["num"]:02d} · {g["name"]}</div>'
            f'{"".join(cards)}</div>'
        )
    n = len(lessons)
    body = f"""<div class="wrap">
  <div class="eyebrow">crm cli + d365 ce <span class="dot">/</span> learning workspace</div>
  <h1 class="hero">Drive D365 customizations <em>from the shell.</em></h1>
  <div class="intro">
    <p class="lead">{LEAD}</p>
    <div class="goal"><div class="goal-label">The goal</div><p>{GOAL}</p></div>
  </div>
  <div class="facts"><span class="fact"><b>beginner-first</b></span><span class="fact">source-cited</span><span class="fact">cloud + on-prem</span><span class="fact"><b>{n}</b> lessons live</span></div>
  <div class="topic-filter">{chips}</div>
  <div class="sec-rule">The path <span class="r"></span> published so far</div>
  <div class="spine">{"".join(nodes)}</div>
</div>
<script>
(function(){{
  var chips=document.querySelectorAll('.topic-chip'),cards=document.querySelectorAll('.lcard');
  chips.forEach(function(c){{c.addEventListener('click',function(){{
    chips.forEach(function(x){{x.classList.remove('is-on');}});c.classList.add('is-on');
    var t=c.dataset.topic;
    cards.forEach(function(card){{
      var has=t==='all'||((' '+card.dataset.topics+' ').indexOf(' '+t+' ')>-1);
      card.style.display=has?'':'none';
    }});
    document.querySelectorAll('.ms-node').forEach(function(node){{
      var vis=node.querySelectorAll('.lcard:not([style*="none"])').length;
      node.style.display=vis?'':'none';
    }});
  }});}});
}})();
</script>"""
    return PAGE.format(
        title="crm·learn — drive D365 customizations from the shell",
        nav=nav, css_prefix="", body=body,
    )


def render_glossary(md_text, lessons):
    nav = nav_html(lessons, "")
    rendered = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    body = (
        '<div class="wrap glossary">'
        '<div class="eyebrow">crm cli + d365 ce <span class="dot">/</span> glossary</div>'
        f"{rendered}</div>"
    )
    return PAGE.format(title="Glossary — crm·learn", nav=nav, css_prefix="", body=body)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_build.py -v`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_build.py
git commit -m "feat: build renders index (timeline + topic filter) and glossary"
```

---

## Task 7: Build — `main()` assembling `_site/`

**Files:**
- Modify: `scripts/build.py`

(No new unit test — verified by running the build after `assets/site.css` exists, in Task 9.)

- [ ] **Step 1: Implement `main()`**

Append to `scripts/build.py`:

```python
def main():
    lessons = load_lessons(LESSONS_DIR)
    if not lessons:
        raise SystemExit("build: no lessons found")
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "lessons").mkdir(parents=True)

    (OUT / "index.html").write_text(render_index(lessons), encoding="utf-8")

    md_text = GLOSSARY_MD.read_text(encoding="utf-8")
    (OUT / "glossary.html").write_text(render_glossary(md_text, lessons), encoding="utf-8")

    lesson_nav = nav_html(lessons, "../")
    for L in lessons:
        (OUT / "lessons" / L["file"]).write_text(inject_nav(L["html"], lesson_nav), encoding="utf-8")

    if ASSETS_DIR.exists():
        shutil.copytree(ASSETS_DIR, OUT / "assets")

    print(f"build: wrote {OUT} ({len(lessons)} lessons)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Confirm import still clean**

Run: `python -c "import sys; sys.path.insert(0,'scripts'); import build; print('ok')"`
Expected: `ok` (no syntax/import error).

- [ ] **Step 3: Commit**

```bash
git add scripts/build.py
git commit -m "feat: build assembles full _site (index, glossary, lessons, assets)"
```

---

## Task 8: `assets/site.css` — the itWorx design system

Defines the new palette + aliases the lessons' existing token names so re-skinning a lesson is link-and-recolor, not a rewrite. Styles the navbar and the generated pages.

**Files:**
- Create: `assets/site.css`

- [ ] **Step 1: Write `assets/site.css`**

```css
/* itWorx design system for the crm-learn site. Palette + fonts mirror crm-cli-docs. */
:root{
  --indigo:#1B1F8F; --indigo-royal:#353A9C; --indigo-dark:#12156B;
  --red:#C83428; --red-light:#E0594D;
  --bg:#ffffff; --surface:#f4f5fa; --surface2:#eceefb;
  --ink:rgba(0,0,0,.87); --ink-soft:rgba(0,0,0,.6); --ink-mute:rgba(0,0,0,.44);
  --line:#e3e5f2; --line2:#d3d6ec;
  --shadow:0 1px 2px rgba(18,21,107,.06),0 6px 22px -14px rgba(18,21,107,.4);

  /* ---- aliases so the existing lessons' inline CSS recolors to itWorx ---- */
  --paper:var(--bg); --card:#ffffff;
  --teal:var(--indigo); --teal-deep:var(--indigo-dark); --teal-soft:var(--surface2);
  --amber:var(--red); --amber-soft:#f7e3e1;
  --guid:var(--indigo-royal); --guid-soft:var(--surface2);
  --term-bg:#12161f; --term-bg2:#1a2030; --term-ink:#e7ebf6;
  --ok:var(--indigo); --bad:var(--red);
}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);background:var(--bg);
  font-family:"Roboto",system-ui,sans-serif;font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--indigo-royal)}

/* ---- navbar (build-injected on every page) ---- */
.site-nav{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:16px;
  padding:11px 20px;background:var(--indigo);color:#fff;box-shadow:0 2px 6px rgba(18,21,107,.35)}
.site-nav .brand{display:flex;align-items:center;gap:9px;font-family:"Roboto Mono",monospace;
  font-weight:700;font-size:14px;color:#fff;text-decoration:none;letter-spacing:.02em}
.brand-gem{width:18px;height:18px;border-radius:5px;background:#fff;color:var(--indigo);
  display:grid;place-items:center;font-family:"Roboto",sans-serif;font-weight:700;font-size:12px}
.nav-spacer{flex:1}
.site-nav .navlink{font-size:14px;color:rgba(255,255,255,.84);text-decoration:none;font-weight:500;
  padding:6px 4px;background:none;border:0;cursor:pointer;font-family:inherit}
.site-nav .navlink:hover{color:#fff}
.navdrop{position:relative}
.navmenu{position:absolute;top:32px;right:0;width:320px;background:#fff;color:var(--ink);
  border:1px solid var(--line2);border-radius:12px;box-shadow:0 14px 36px -12px rgba(18,21,107,.5);
  padding:8px;display:none}
.navdrop:hover .navmenu,.navdrop:focus-within .navmenu{display:block}
.navmenu-label{font-family:"Roboto Mono",monospace;font-size:9.5px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-mute);padding:8px 9px 4px}
.navmenu a{display:flex;gap:9px;align-items:baseline;padding:7px 9px;border-radius:8px;
  text-decoration:none;color:var(--ink)}
.navmenu a:hover{background:var(--surface2)}
.navmenu-no{font-family:"Roboto Mono",monospace;font-size:10px;color:var(--red);font-weight:700}
.navmenu-t{font-size:13px}

/* ---- generated page shell ---- */
.wrap{max-width:860px;margin:0 auto;padding:40px 24px 110px}
.eyebrow{font-family:"Roboto Mono",monospace;font-size:11px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--indigo-royal);font-weight:500}
.eyebrow .dot{color:var(--red)}
.hero{font-weight:700;letter-spacing:-.025em;line-height:1.05;font-size:clamp(34px,6vw,52px);
  margin:.18em 0 .1em;color:var(--indigo-dark)}
.hero em{font-style:normal;color:var(--red)}
.intro{display:grid;grid-template-columns:1.4fr 1fr;gap:20px;align-items:start;margin:26px 0 0}
.lead{font-size:18px;line-height:1.55;margin:0}
.lead em{font-style:normal;color:var(--indigo-royal);font-weight:500}
.goal{background:var(--surface2);border-left:4px solid var(--indigo);border-radius:0 10px 10px 0;padding:14px 17px}
.goal-label{font-family:"Roboto Mono",monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--indigo);font-weight:700}
.goal p{margin:6px 0 0;font-size:14px;color:var(--ink-soft)}
.facts{display:flex;gap:9px;flex-wrap:wrap;margin:22px 0 0}
.fact{font-family:"Roboto Mono",monospace;font-size:11px;color:var(--ink-soft);background:#fff;
  border:1px solid var(--line2);border-radius:999px;padding:5px 12px}
.fact b{color:var(--indigo)}
.topic-filter{display:flex;gap:8px;flex-wrap:wrap;margin:26px 0 0}
.topic-chip{font-family:"Roboto Mono",monospace;font-size:11px;color:var(--ink-soft);background:#fff;
  border:1px solid var(--line2);border-radius:999px;padding:5px 12px;cursor:pointer}
.topic-chip.is-on{background:var(--indigo);color:#fff;border-color:var(--indigo)}
.sec-rule{display:flex;align-items:center;gap:11px;margin:30px 0 16px;font-family:"Roboto Mono",monospace;
  font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);font-weight:500}
.sec-rule .r{height:1px;background:var(--line2);flex:1}
.spine{position:relative;margin-left:16px;padding-left:26px;border-left:2px solid var(--line2)}
.ms-node{position:relative;margin-bottom:22px}
.ms-node::before{content:"";position:absolute;left:-33px;top:2px;width:13px;height:13px;border-radius:50%;
  background:var(--red);border:2px solid #fff;box-shadow:0 0 0 2px var(--surface2)}
.ms-label{font-family:"Roboto Mono",monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  font-weight:700;color:var(--indigo);margin-bottom:10px}
.lcard{display:flex;gap:13px;align-items:flex-start;background:#fff;border:1px solid var(--line);
  border-radius:11px;padding:14px 16px;box-shadow:var(--shadow);margin:9px 0;text-decoration:none;
  color:var(--ink);transition:border-color .15s,transform .15s}
.lcard:hover{border-color:var(--indigo-royal);transform:translateY(-1px)}
.lc-no{font-family:"Roboto Mono",monospace;font-size:11px;color:var(--red);font-weight:700;padding-top:2px}
.lc-body{display:flex;flex-direction:column;gap:4px}
.lc-t{font-weight:700;font-size:16px;line-height:1.2;color:var(--ink)}
.lc-sum{font-size:13.5px;color:var(--ink-soft)}
.lc-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:2px}
.lc-tag{font-family:"Roboto Mono",monospace;font-size:9.5px;color:var(--indigo-royal);
  background:var(--surface2);border-radius:5px;padding:2px 7px}
.lc-arrow{margin-left:auto;color:var(--indigo-royal);font-size:18px;align-self:center}

/* ---- glossary prose ---- */
.glossary h2{font-weight:700;color:var(--indigo-dark);margin:34px 0 10px;font-size:22px;
  border-bottom:1px solid var(--line2);padding-bottom:6px}
.glossary h3{font-weight:700;color:var(--ink);margin:18px 0 4px;font-size:16px}
.glossary strong{color:var(--indigo-dark)}
.glossary code{font-family:"Roboto Mono",monospace;font-size:.86em;background:var(--surface);
  border:1px solid var(--line2);border-radius:5px;padding:1px 5px}
.glossary hr{border:0;border-top:1px solid var(--line2);margin:26px 0}
.glossary em{color:var(--ink-mute)}

@media(max-width:640px){.intro{grid-template-columns:1fr}.site-nav{flex-wrap:wrap;gap:10px}}
```

- [ ] **Step 2: Commit**

```bash
git add assets/site.css
git commit -m "feat: add itWorx site.css (tokens, lesson aliases, navbar, page components)"
```

---

## Task 9: First full build + visual check

**Files:** none changed (verification task)

- [ ] **Step 1: Run the build**

Run: `python scripts/build.py`
Expected: prints `build: wrote .../_site (2 lessons)`; no traceback.

- [ ] **Step 2: Assert the output structure + nav presence**

Run:
```bash
test -f _site/index.html && test -f _site/glossary.html && test -f _site/lessons/0001-install-configure-profiles.html && test -f _site/assets/site.css && echo "files ok"
grep -c 'class="site-nav"' _site/lessons/0002-the-whoami-handshake.html   # expect 1
grep -q 'glossary.html' _site/lessons/0001-install-configure-profiles.html && echo "lesson nav -> glossary ok"
grep -q 'data-topic="install"' _site/index.html && echo "topic filter ok"
```
Expected: `files ok`, `1`, `lesson nav -> glossary ok`, `topic filter ok`.

- [ ] **Step 3: Open locally in Windows Chrome (manual)**

Run:
```bash
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" "$(wslpath -w _site/index.html)"
```
Confirm visually: indigo navbar; hero + intro/goal; facts; topic chips filter the timeline; the Lessons ▾ menu lists both lessons and links work; Glossary link opens the rendered glossary; lesson pages show the navbar at top. (Note: lessons not yet re-skinned — they still look warm here; that's Task 10–11.)

- [ ] **Step 4: Run the unit tests once more**

Run: `python -m pytest tests/test_build.py -v`
Expected: PASS (8 passed).

No commit (no file changes).

---

## Task 10: Re-skin lesson 0001 to itWorx/Roboto

Deterministic edits: load `site.css` (last in `<head>` so it overrides the inline `:root`), swap the font link to Roboto, and recolor the font-family names + hardcoded warm accents. Do **not** touch the org URL here (Task 14 scrubs it).

**Files:**
- Modify: `lessons/0001-install-configure-profiles.html`

- [ ] **Step 1: Swap the Google Fonts link (line 9)**

Replace the existing Fraunces/Hanken/Plex `<link href="https://fonts.googleapis.com/css2?...">` line with:

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Link `site.css` immediately before `</head>`**

Insert directly before the `</head>` tag:

```html
<link rel="stylesheet" href="../assets/site.css">
```

- [ ] **Step 3: Recolor fonts + warm accents (run from repo root)**

```bash
f=lessons/0001-install-configure-profiles.html
sed -i \
  -e 's/"Fraunces",[^;]*serif/"Roboto",system-ui,sans-serif/g' \
  -e 's/Fraunces/Roboto/g' \
  -e 's/Hanken Grotesk/Roboto/g' \
  -e 's/IBM Plex Mono/Roboto Mono/g' \
  -e 's/rgba(12,122,100,/rgba(27,31,143,/g' \
  -e 's/rgba(180,83,10,/rgba(200,52,40,/g' \
  -e 's/rgba(30,28,20,/rgba(18,21,107,/g' \
  "$f"
```

- [ ] **Step 4: Rebuild and visually verify (manual)**

Run:
```bash
python scripts/build.py
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" "$(wslpath -w _site/lessons/0001-install-configure-profiles.html)"
```
Confirm: lesson now reads in Roboto with indigo/red accents and white background; the navbar sits on top; the quiz still works (answer a question → feedback shows); headings/eyebrow/terminal blocks render sensibly.

- [ ] **Step 5: Commit**

```bash
git add lessons/0001-install-configure-profiles.html
git commit -m "style: re-skin lesson 0001 to itWorx/Roboto"
```

---

## Task 11: Re-skin lesson 0002 to itWorx/Roboto

Same deterministic edits as Task 10, applied to lesson 0002.

**Files:**
- Modify: `lessons/0002-the-whoami-handshake.html`

- [ ] **Step 1: Swap the Google Fonts link (line 9)**

Replace the existing Fraunces/Hanken/Plex `<link href="https://fonts.googleapis.com/css2?...">` line with:

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Link `site.css` immediately before `</head>`**

Insert directly before the `</head>` tag:

```html
<link rel="stylesheet" href="../assets/site.css">
```

- [ ] **Step 3: Recolor fonts + warm accents (run from repo root)**

```bash
f=lessons/0002-the-whoami-handshake.html
sed -i \
  -e 's/"Fraunces",[^;]*serif/"Roboto",system-ui,sans-serif/g' \
  -e 's/Fraunces/Roboto/g' \
  -e 's/Hanken Grotesk/Roboto/g' \
  -e 's/IBM Plex Mono/Roboto Mono/g' \
  -e 's/rgba(12,122,100,/rgba(27,31,143,/g' \
  -e 's/rgba(180,83,10,/rgba(200,52,40,/g' \
  -e 's/rgba(30,28,20,/rgba(18,21,107,/g' \
  "$f"
```

- [ ] **Step 4: Rebuild and visually verify (manual)**

Run:
```bash
python scripts/build.py
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" "$(wslpath -w _site/lessons/0002-the-whoami-handshake.html)"
```
Confirm: lesson reads in Roboto with indigo/red accents; navbar present; quiz + livechip + reveal animations still work.

- [ ] **Step 5: Commit**

```bash
git add lessons/0002-the-whoami-handshake.html
git commit -m "style: re-skin lesson 0002 to itWorx/Roboto"
```

---

## Task 12: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add public README with live link and build instructions"
```

---

## Task 13: CLAUDE.md — "Lessons site" section

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Append a new section to `CLAUDE.md`**

Add at the end of `CLAUDE.md`:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document the Pages lessons site in CLAUDE.md"
```

---

## Task 14: Privacy scrub — replace org URL / on-prem host across all four files

Derive the two real values from `NOTES.md` into shell variables (so this plan and every
committed file stay free of the literals), then replace them everywhere.

**Files:**
- Modify: `NOTES.md`, `GLOSSARY.md`, `lessons/0001-install-configure-profiles.html`, `lessons/0002-the-whoami-handshake.html`

- [ ] **Step 1: Capture the real values and scrub**

```bash
cd /home/gharib/wip/learn/learn-crm-cli-and-api
ORG_HOST=$(grep -hoE 'org[0-9a-z]+\.crm\.dynamics\.com' NOTES.md | head -1)
ONPREM_HOST=$(grep -hoE 'internalcrm\.[a-z0-9.]+\.local' NOTES.md | head -1)
ONPREM_ORG=$(grep -hoE "$ONPREM_HOST/[A-Za-z0-9]+" NOTES.md | head -1 | sed "s#$ONPREM_HOST/##")
echo "scrubbing host=$ORG_HOST  onprem=$ONPREM_HOST/$ONPREM_ORG"
[ -n "$ORG_HOST" ] && [ -n "$ONPREM_HOST" ] || { echo "ABORT: could not derive values"; exit 1; }

for f in NOTES.md GLOSSARY.md lessons/0001-install-configure-profiles.html lessons/0002-the-whoami-handshake.html; do
  sed -i \
    -e "s#${ONPREM_HOST}/${ONPREM_ORG}#crm.contoso.local/Contoso#g" \
    -e "s#${ONPREM_HOST}#crm.contoso.local#g" \
    -e "s#${ORG_HOST}#orgexample.crm.dynamics.com#g" \
    "$f"
done
```

The canonical example env (use it in all new lessons too): cloud
`https://orgexample.crm.dynamics.com`, on-prem `http://crm.contoso.local/Contoso`.

- [ ] **Step 2: Verify the working tree is clean of the REAL patterns**

The leak check matches the real values only — a hex-only org id and the `internalcrm.*.local`
host — so the example env (`orgexample`, `crm.contoso.local`) does NOT trip it:

```bash
grep -rnE 'org[0-9a-f]{6,}\.crm\.dynamics\.com|internalcrm\.[a-z0-9.]+\.local' \
  NOTES.md GLOSSARY.md lessons/ && echo "!! STILL PRESENT — investigate" || echo "WORKING TREE CLEAN ✓"
```
Expected: `WORKING TREE CLEAN ✓`.

- [ ] **Step 3: Rebuild and confirm the placeholders render naturally (manual)**

Run:
```bash
python scripts/build.py
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" "$(wslpath -w _site/lessons/0001-install-configure-profiles.html)"
```
Confirm the profile-list output now shows `orgexample.crm.dynamics.com` / `crm.contoso.local/Contoso` consistently and reads sensibly.

- [ ] **Step 4: Commit**

```bash
git add NOTES.md GLOSSARY.md lessons/0001-install-configure-profiles.html lessons/0002-the-whoami-handshake.html
git commit -m "security: scrub real org URL + on-prem host to placeholders"
```

---

## Task 15: NOTES.md authoring-standard update + memory

**Files:**
- Modify: `NOTES.md`
- Modify: `/home/gharib/.claude/projects/-home-gharib-wip-learn-learn-crm-cli-and-api/memory/lesson-authoring-prefs.md` (+ `MEMORY.md` pointer if needed)

- [ ] **Step 1: Update the authoring preference in `NOTES.md`**

Find the bullet under "## Teaching preferences" that reads:

```
- **Author lesson HTML via the `frontend-design` skill** — distinctive, production-grade;
  avoid generic AI aesthetics. (pref, 2026-06-13)
```

Replace it with:

```
- **Author lesson HTML in the itWorx/Roboto site skin** (colors + fonts mirror the crm docs
  site): link `../assets/site.css` (last in `<head>`), use Roboto / Roboto Mono. Every lesson
  carries a `#lesson-meta` JSON block; the navbar is build-injected — never hand-add it. Build
  + preview with `python scripts/build.py` → `_site/`. Published lessons use the **example env**
  (`https://orgexample.crm.dynamics.com`, `http://crm.contoso.local/Contoso`), never the real
  org URL/host — live `/teach` still runs against the real orgs. (pref updated 2026-06-13;
  supersedes the earlier frontend-design/distinctive-aesthetic note.)
```

- [ ] **Step 2: Update the `lesson-authoring-prefs` memory**

Edit `/home/gharib/.claude/projects/-home-gharib-wip-learn-learn-crm-cli-and-api/memory/lesson-authoring-prefs.md` so its body reflects the new standard: lessons use the itWorx/Roboto skin via `assets/site.css`, require a `#lesson-meta` block, and the navbar is build-injected; still open lessons in Windows Chrome (not `xdg-open`). Keep the frontmatter `type: feedback`. Update the `MEMORY.md` one-line pointer's hook if its wording no longer fits.

- [ ] **Step 3: Commit (repo file only; memory lives outside the repo)**

```bash
git add NOTES.md
git commit -m "docs: update lesson authoring standard to the itWorx site skin"
```

---

## Task 16: GitHub Actions Pages workflow

**Files:**
- Create: `.github/workflows/pages.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Deploy Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  build-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python scripts/build.py
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site
      - id: deploy
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Lint the YAML locally**

Run: `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/pages.yml')); print('yaml ok')"`
Expected: `yaml ok`. (If PyYAML absent: `pip install pyyaml` first, or skip — GitHub validates on push.)

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/pages.yml
git commit -m "ci: add GitHub Actions workflow to build + deploy Pages"
```

---

## Task 17: Full pre-flight verification

**Files:** none (gate before the irreversible publish steps)

- [ ] **Step 1: Clean build from scratch**

```bash
rm -rf _site && python scripts/build.py && python -m pytest tests/test_build.py -v
```
Expected: build prints `(2 lessons)`; pytest 8 passed.

- [ ] **Step 2: Output sanity**

```bash
for p in _site/index.html _site/glossary.html _site/lessons/0001-install-configure-profiles.html _site/lessons/0002-the-whoami-handshake.html _site/assets/site.css; do test -f "$p" || echo "MISSING $p"; done; echo "checked"
grep -q 'class="site-nav"' _site/glossary.html && echo "glossary nav ok"
```
Expected: `checked` with no MISSING lines; `glossary nav ok`.

- [ ] **Step 3: Working-tree privacy re-check**

```bash
grep -rnE 'org[0-9a-f]{6,}\.crm\.dynamics\.com|internalcrm\.[a-z0-9.]+\.local' \
  --include='*.md' --include='*.html' --include='*.yml' . \
  | grep -v '_site/' && echo "!! FOUND — fix before publishing" || echo "TRACKED SOURCES CLEAN ✓"
```
Expected: `TRACKED SOURCES CLEAN ✓`.

- [ ] **Step 4: Manual final look (Windows Chrome)**

Open `_site/index.html`; click through home → a lesson → glossary → back home; exercise the topic filter; confirm a quiz works. Everything in the itWorx skin, navbar consistent.

No commit.

---

## Task 18: Scrub history — squash to one clean commit

History currently holds the sensitive strings in earlier commits. Replace the whole history
with a single clean commit built from the (already-scrubbed) working tree.

**Files:** none (history rewrite)

- [ ] **Step 1: Confirm a clean working tree**

Run: `git status --short`
Expected: empty (all prior tasks committed). If not, commit/stash first.

- [ ] **Step 2: Create a single orphan commit with the current tree**

```bash
cd /home/gharib/wip/learn/learn-crm-cli-and-api
git checkout --orphan _clean
git add -A
git commit -m "feat: public learning site for the crm CLI + D365 lessons

Lessons grouped by milestone, shared navbar, glossary page; itWorx/Roboto
skin; Python build -> _site -> GitHub Actions Pages. Sensitive infra
strings scrubbed; history squashed to one clean commit before going public.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git branch -D main
git branch -m main
```

- [ ] **Step 3: Verify ALL refs are clean**

```bash
git grep -nE 'org[0-9a-f]{6,}\.crm\.dynamics\.com|internalcrm\.[a-z0-9.]+\.local' $(git rev-list --all) \
  && echo "!! SENSITIVE STRING IN HISTORY — do not push/publish" || echo "ALL HISTORY CLEAN ✓"
git log --oneline   # expect exactly one commit
```
Expected: `ALL HISTORY CLEAN ✓`; one commit.

No remote push yet (Task 19).

---

## Task 19: Force-push clean history, make public, enable Pages

These steps are outward-facing and hard to reverse — run them in order, only after Task 18
prints `ALL HISTORY CLEAN ✓`. Caveat: the old commits were previously pushed to the (private)
remote; after force-push they become unreachable and GitHub will garbage-collect them, though
objects can remain briefly reachable by SHA. For this moderate-sensitivity data that is
acceptable; for stronger guarantees, ask GitHub Support to purge.

**Files:** none (remote + repo settings)

- [ ] **Step 1: Force-push the clean single commit (repo still private)**

```bash
git push --force origin main
```
Expected: remote `main` now points at the single clean commit.

- [ ] **Step 2: Make the repository public**

```bash
gh repo edit Gharib89/learn-crm-cli-and-api --visibility public --accept-visibility-change-consequences
gh repo view Gharib89/learn-crm-cli-and-api --json visibility -q .visibility
```
Expected: `public`.

- [ ] **Step 3: Set Pages source to GitHub Actions**

```bash
gh api -X POST repos/Gharib89/learn-crm-cli-and-api/pages -f build_type=workflow \
  || gh api -X PUT repos/Gharib89/learn-crm-cli-and-api/pages -f build_type=workflow
```
Expected: JSON describing the Pages site (or a 409 on first command → the PUT fallback succeeds).

- [ ] **Step 4: Trigger + watch the deploy**

```bash
gh workflow run "Deploy Pages" --ref main
sleep 5
gh run watch "$(gh run list --workflow='Deploy Pages' -L1 --json databaseId -q '.[0].databaseId')" --exit-status
```
Expected: the run completes successfully (`✓`).

- [ ] **Step 5: Verify the live site**

```bash
curl -sSL -o /dev/null -w "%{http_code}\n" https://gharib89.github.io/learn-crm-cli-and-api/
```
Expected: `200`. Then open the URL in a browser: home renders, navbar works, a lesson opens, the glossary opens, the topic filter works.

- [ ] **Step 6: Done**

The repo is public, history is clean, and the site is live. No further commit needed.

---

## Self-Review (completed by plan author)

**Spec coverage** — every spec section maps to a task:
- §A privacy scrub → Tasks 14, 17, 18, 19 · §B site.css → Task 8 · §C index/timeline/topic filter + glossary page → Tasks 6, 8 · §D navbar → Tasks 4, 5 · §E lesson-meta → Task 2 · §F build + CI → Tasks 3–7, 16 · §G re-skin lessons → Tasks 10, 11 · §H README/NOTES/CLAUDE/memory/gitignore → Tasks 1, 12, 13, 15 · §I inventory → File Structure table · §J out-of-scope → not built (correct) · §K verification → Tasks 9, 17, 19.

**Placeholder scan** — no "TBD/TODO/handle edge cases"; every code step shows complete code; the `<your-org>`/`<on-prem-host>` strings are intended output placeholders, not plan gaps.

**Type/name consistency** — `extract_meta`, `load_lessons`, `group_by_milestone`, `nav_html(lessons, prefix)`, `inject_nav`, `render_index(lessons)`, `render_glossary(md_text, lessons)`, `main()`, and the `PAGE`/`LEAD`/`GOAL` constants are used consistently across Tasks 3–7 and the tests. CSS class names emitted by `build.py` (`site-nav`, `navmenu`, `lcard`, `lc-*`, `ms-node`, `topic-chip`, `goal`, `intro`, `hero`, `eyebrow`) all exist in `assets/site.css` (Task 8).
