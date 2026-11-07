"""Two-brand launch: the homepage features only Scam Decoded as a sister site until site.json > launch_stage
moves on, and every calculator on the site has an 'Email me this plan' box right under it."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def _build(tmp_path):
    out = tmp_path / "public"
    e = {**os.environ, "SITE_OUT": str(out), "SITE_URL": "https://example.org", "BLOG_SHOW_SCHEDULED": "1"}
    e.pop("URL", None)
    subprocess.run([sys.executable, str(SITE / "build.py")], check=True, env=e, capture_output=True)
    return out


def test_homepage_shows_only_launch_brands_and_the_flag_opens_the_rest(tmp_path):
    cfg = json.loads((SITE / "site.json").read_text())
    assert cfg["launch_stage"] == "two-brand", "flip launch_stage only after GO_LIVE's week-8 gates pass"
    out = _build(tmp_path)
    home = (out / "index.html").read_text()
    assert "Scam Decoded" in home and "https://scamdecoded.netlify.app/" in home
    for name in ("1099 Money", "Dinero Simple"):
        hits = [str(p.relative_to(out)) for p in out.rglob("*.html") if name in p.read_text()]
        assert not hits, f"{name} shows before its launch stage: {hits[:5]}"

    sys.path.insert(0, str(SITE))
    import build
    saved = dict(build.CFG)
    try:
        build.CFG.clear()
        build.CFG.update(cfg)
        assert [b["slug"] for b in build.visible_brands()] == ["scam-decoded"]
        build.CFG["launch_stage"] = "brand-3"
        assert [b["slug"] for b in build.visible_brands()] == ["scam-decoded", "1099-money"]
        build.CFG["launch_stage"] = "all"  # Dinero Simple also needs show: true (paused for a Spanish reviewer)
        assert "dinero-simple" not in [b["slug"] for b in build.visible_brands()]
    finally:
        build.CFG.clear()
        build.CFG.update(saved)


def test_every_calculator_has_an_email_me_this_plan_box_under_it(tmp_path):
    out = _build(tmp_path)
    embeds = json.loads((SITE / "content" / "data" / "embeds.json").read_text())
    calcs = {k for k, t in embeds["tools"].items() if t["kind"] == "calc"}
    checked = 0
    for slug, key in embeds["articles"].items():
        page = out / "blog" / slug / "index.html"
        if key not in calcs or not page.exists():
            continue
        html = page.read_text()
        m = re.search(r'<div class="tool-embed">.*?<div class="mms-calc".*?</div>(.*?)</div>\s*', html, re.S)
        assert m and f'id="plan-{key}"' in html[m.start():m.start() + 6000], f"{slug}: no plan box under the {key} calculator"
        box = re.search(rf'<div class="plan-optin" data-no-optin id="plan-{key}">(.*?)</form>', html, re.S)
        assert box and "Email me this plan" in box.group(1) and f'value="plan-{key}"' in box.group(1), slug
        checked += 1
    assert checked >= 5
    debt = (out / "debt-payoff" / "index.html").read_text()
    form_end = debt.index("</form>", debt.index('id="debt-calc"'))
    nxt = debt.index('id="plan-debt-payoff"')
    assert form_end < nxt < form_end + 300, "plan box should sit right under the debt calculator's result"
    assert 'id="plan-debt-payoff" hidden' in debt  # debt-calc.js shows it with the result
    assert "plan-debt-payoff" in (SITE / "static" / "debt-calc.js").read_text()


def test_plan_box_copy_matches_the_apps_shared_component():
    o = json.loads((SITE / "site.json").read_text())["plan_optin"]
    shared = ROOT / "apps" / "shared" / "optin.js"
    if shared.exists():  # PR #8; once merged, the two must stay the same
        line = re.search(r"mms: \{ en: \[(.*?)\]", shared.read_text()).group(1)
        title, pitch, button = re.findall(r"'((?:[^'\\]|\\.)*)'", line)[:3]
        assert (o["title"], o["pitch"], o["button"]) == (title, pitch, button)
    else:
        assert o["title"] == "Email me this plan" and o["button"] == "Email me"
