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

def test_inject_nav_after_body():
    out = build.inject_nav("<html><body><h1>hi</h1></body></html>", "<nav>NAV</nav>")
    assert "<body><nav>NAV</nav>" in out.replace("\n", "")
    assert "<h1>hi</h1>" in out

def test_inject_nav_without_body_raises():
    with pytest.raises(SystemExit):
        build.inject_nav("<html>no body</html>", "<nav>NAV</nav>")

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

def test_order_lessons_flattens_publish_order():
    flat = build.order_lessons(_two_lessons())
    assert [L["lesson"] for L in flat] == [1, 2]

NEXT_BLOCK = (
    '<div class="next reveal">'
    '<span class="pill t">next up</span>'
    '<h2>Lesson 02 — WhoAmI</h2>'
    '<p>Prove it works. <span class="live-only">Just say <strong>"next lesson"</strong>.</span></p>'
    '</div>'
)

def test_wire_next_strips_live_only_and_links_to_next():
    nxt = build.extract_meta(LESSON_B); nxt["file"] = "0002-whoami.html"
    out = build.wire_next(NEXT_BLOCK, nxt)
    assert "live-only" not in out and "Just say" not in out
    assert 'class="next-go" href="0002-whoami.html"' in out
    assert "Lesson 02 · WhoAmI" in out

def test_wire_next_last_lesson_strips_cta_without_link():
    out = build.wire_next(NEXT_BLOCK, None)
    assert "live-only" not in out and "Just say" not in out
    assert "next-go" not in out
