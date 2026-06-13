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
# The end-of-lesson .next block has no nested divs, so a non-greedy match to the
# first </div> reliably captures it.
NEXT_DIV_RE = re.compile(r'(<div class="next reveal">)(.*?)(</div>)', re.DOTALL | re.IGNORECASE)
# Live-/teach-session-only call to action, stripped from the published copy.
LIVE_ONLY_RE = re.compile(r'\s*<span class="live-only">.*?</span>', re.DOTALL | re.IGNORECASE)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
        except json.JSONDecodeError as e:
            raise SystemExit(f"build: {path.name}: invalid lesson-meta JSON: {e}")
        except ValueError as e:
            raise SystemExit(f"build: {path.name}: {e}")
        meta["file"] = path.name
        meta["html"] = html
        lessons.append(meta)
    return lessons


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


def inject_nav(html, nav):
    if not BODY_RE.search(html):
        raise SystemExit("build: lesson missing <body>")
    return BODY_RE.sub(lambda m: m.group(1) + "\n" + nav, html, count=1)


def order_lessons(lessons):
    """Flat publish order: milestones ascending, lessons by `order` within each."""
    flat = []
    for g in group_by_milestone(lessons):
        flat.extend(g["lessons"])
    return flat


def wire_next(html, nxt):
    """Strip the live-session CTA, then link the .next block to the following lesson.

    `nxt` is the next lesson's meta, or None for the last published lesson (no link)."""
    html = LIVE_ONLY_RE.sub("", html)
    if nxt is None:
        return html
    link = (
        f'\n  <a class="next-go" href="{nxt["file"]}">'
        f'<span class="next-go-k">Continue</span>'
        f'<span class="next-go-t">Lesson {nxt["lesson"]:02d} · {esc(nxt["title"])}</span>'
        f'<span class="next-go-x">→</span></a>'
    )
    if not NEXT_DIV_RE.search(html):
        raise SystemExit('build: lesson missing <div class="next reveal"> block')
    return NEXT_DIV_RE.sub(
        lambda m: m.group(1) + m.group(2).rstrip() + link + "\n" + m.group(3),
        html, count=1,
    )


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
    flat = order_lessons(lessons)
    next_by_file = {L["file"]: (flat[i + 1] if i + 1 < len(flat) else None) for i, L in enumerate(flat)}
    for L in lessons:
        html = inject_nav(L["html"], lesson_nav)
        html = wire_next(html, next_by_file[L["file"]])
        (OUT / "lessons" / L["file"]).write_text(html, encoding="utf-8")

    if ASSETS_DIR.exists():
        shutil.copytree(ASSETS_DIR, OUT / "assets")

    print(f"build: wrote {OUT} ({len(lessons)} lessons)")


if __name__ == "__main__":
    main()
