"""Browser accessibility audit of the built site: axe-core (WCAG 2.2 AA + best practice) on every page at
desktop and phone width, plus keyboard and mobile checks axe can't do.

Needs Playwright + Chromium and axe-core. Skips if either is missing; .github/workflows/a11y.yml installs both.
    pip install playwright && python -m playwright install chromium
    npm install --prefix /tmp/axe axe-core@4.10.2 && export AXE_PATH=/tmp/axe/node_modules/axe-core/axe.min.js
"""
import functools
import http.server
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1] / "site"
AXE = os.environ.get("AXE_PATH", "")
pw = pytest.importorskip("playwright.sync_api")
if not AXE or not Path(AXE).exists():
    pytest.skip("set AXE_PATH to axe.min.js (axe-core) to run the browser audit", allow_module_level=True)

TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("a11y") / "public"
    env = {**os.environ, "SITE_OUT": str(out), "SITE_URL": "https://example.org"}
    env.pop("URL", None)
    subprocess.run([sys.executable, str(SITE / "build.py")], check=True, env=env, capture_output=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(out))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pages = sorted("/" + str(p.parent.relative_to(out)).replace(".", "").strip("/") + "/"
                   for p in out.rglob("index.html")
                   if not p.relative_to(out).parts[0] in ("emails", "go")
                   and 'http-equiv="refresh"' not in p.read_text()[:800])
    pages = [p.replace("//", "/") for p in pages] + ["/404.html"]
    yield f"http://127.0.0.1:{srv.server_address[1]}", pages
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None)
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        yield b
        b.close()


def _context(browser, width):
    ctx = browser.new_context(viewport={"width": width, "height": 900})
    ctx.route(lambda url: not url.startswith("http://127.0.0.1"), lambda r: r.abort())  # no network
    return ctx


@pytest.mark.parametrize("width", [1280, 390])
def test_axe_every_page(site, browser, width):
    base, pages = site
    axe = Path(AXE).read_text()
    problems = []
    for start in range(0, len(pages), 20):  # fresh context every 20 pages keeps memory flat
        ctx = _context(browser, width)
        pg = ctx.new_page()
        for path in pages[start:start + 20]:
            pg.goto(base + path, wait_until="load")
            if pg.evaluate("document.documentElement.scrollWidth") > width:
                problems.append(f"{path}: scrolls sideways at {width}px")
            pg.add_script_tag(content=axe)
            res = pg.evaluate("t => axe.run(document, {runOnly: {type: 'tag', values: t}})", TAGS)
            for v in res["violations"]:
                targets = ", ".join(str(n["target"]) for n in v["nodes"][:3])
                problems.append(f"{path} [{v['impact']}] {v['id']}: {v['help']} ({targets})")
        ctx.close()
    assert not problems, "\n".join(problems)


def test_keyboard_skip_link_and_visible_focus(site, browser):
    base, _ = site
    ctx = _context(browser, 1280)
    pg = ctx.new_page()
    pg.goto(base + "/")
    pg.keyboard.press("Tab")
    assert pg.evaluate("document.activeElement.className") == "skip"
    pg.keyboard.press("Enter")
    assert pg.evaluate("location.hash") == "#main"
    # Every element reachable with Tab on the home page shows a focus ring.
    seen = set()
    for _ in range(60):
        pg.keyboard.press("Tab")
        info = pg.evaluate("""() => { const e = document.activeElement, s = getComputedStyle(e);
            return [e.tagName + (e.getAttribute('href') || e.name || ''), s.outlineStyle, parseFloat(s.outlineWidth)] }""")
        if info[0] == "BODY":  # tabbed past the last control
            break
        if info[0] in seen:
            continue
        seen.add(info[0])
        assert info[1] != "none" and info[2] >= 2, f"no visible focus on {info[0]}"
    assert len(seen) > 10
    ctx.close()


def test_quiz_works_with_keyboard_only(site, browser):
    base, _ = site
    ctx = _context(browser, 390)
    pg = ctx.new_page()
    pg.goto(base + "/quiz/")
    for _ in range(6):
        pg.locator(".quiz .opt").first.focus()
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(50)
    assert pg.evaluate("!document.getElementById('result').hidden"), "quiz result not shown"
    ctx.close()


def test_mobile_tap_targets_in_nav_and_forms(site, browser):
    """WCAG 2.5.8 asks for 24px; the main controls get the 44px Apple/Google guideline."""
    base, _ = site
    ctx = _context(browser, 390)
    pg = ctx.new_page()
    for path in ("/", "/free/", "/shop/", "/quiz/"):
        pg.goto(base + path)
        small = pg.evaluate("""() => [...document.querySelectorAll(
              '.site-head nav a, .signup-form button, .signup-form input[type=email], .btn, .quiz .opt')]
            .filter(e => e.offsetParent).map(e => [e.textContent.trim().slice(0, 30) || e.name, e.getBoundingClientRect().height])
            .filter(([, h]) => h < 44)""")
        assert not small, f"{path}: controls under 44px tall on a phone: {small}"
    ctx.close()
