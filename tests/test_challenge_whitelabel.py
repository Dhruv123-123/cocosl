import json
from datetime import date

import pytest
from PIL import Image

from contentfactory.challenge import amounts, build, import_posts, plan, schedule
from contentfactory.guardrails import jaccard, script_text, shingles
from contentfactory.whitelabel import export, leftovers, load_client, rewrite, _ours

BRAND = "money-made-simple"


def test_amounts_and_totals():
    assert sum(amounts("ladder", 30)) == 465 and plan("ladder", 30)[-1].total == 465
    assert sum(amounts("fixed", 30, target=1000)) == 1000
    env = amounts("envelope", 30, seed="x")
    assert sorted(env) == list(range(1, 31)) and env != list(range(1, 31))
    assert amounts("envelope", 30, seed="x") == env  # same seed, same order
    assert plan("no-spend", 14)[-1].total == 0
    with pytest.raises(ValueError):
        amounts("fixed", 30)


def test_challenge_build_import_schedule(factory, monkeypatch):
    built = build(factory, BRAND, "ladder", 14, start=date(2030, 1, 1))
    d = built["dir"]
    assert Image.open(d / "tracker.png").size == (2480, 3508) and (d / "tracker.pdf").exists()
    assert Image.open(d / "day-07.png").size == (1080, 1350)
    cap = (d / "captions" / "day-07.txt").read_text()
    assert "save $7 today" in cap and "$28 so far of the $105 goal" in cap
    assert len(json.loads((d / "kickoff.json").read_text())) == 3
    ids = import_posts(factory, built, render_videos=False)
    days = [factory.db.get("posts", i) for i in ids[:14]]
    assert all(p["format"] == "image" and p["status"] in ("in_review", "approved") for p in days)
    a, b = (shingles(script_text(p["script"]) + " " + p["caption"]) for p in days[:2])
    assert jaccard(a, b) < 0.35  # different tip each day: not near-duplicates
    assert factory.render(ids[0])["slides"] == days[0]["assets"]["slides"]  # re-render keeps the tracker
    monkeypatch.setattr("contentfactory.publish.preflight.check_post", lambda *a, **k: [])
    for p in days:
        factory.db.update("posts", p["id"], {"status": "approved"})
    pubs = schedule(factory, BRAND, built["slug"])
    first = [factory.db.get("publications", x) for x in pubs if factory.db.get("publications", x)["post_id"] == ids[0]]
    assert first and all(p["scheduled_at"].startswith("2030-01-01") for p in first)


def _client(tmp_path, **kw):
    cfg = {"slug": "acme-cu", "name": "Acme Community Credit Union", "short": "Acme CU", "handle": "@acmecu",
           "website": "https://www.acmecu.example.org", "color": "#0f2a44", "accent": "#f2b134",
           "cta": "Questions? Call Acme CU.", **kw}
    p = tmp_path / "acme.json"
    p.write_text(json.dumps(cfg))
    return p


def test_rewrite_swaps_brand_links_and_affiliates(factory, tmp_path):
    src = factory.brand(BRAND)
    cfg = load_client(_client(tmp_path))
    ours = _ours(src)
    text = (f"{src.name} tip. Get the kit: {src.products[0]['url']} or https://moneymadesimple.co/go/hysa "
            f"#moneymadesimple {src.cta} Call {{{{CLIENT_PHONE}}}}")
    out = rewrite(text, src, cfg, ours)
    assert "Acme Community Credit Union tip" in out and "Questions? Call Acme CU." in out
    assert "/go/" not in out and src.products[0]["url"] not in out and "#acmecu" in out
    assert leftovers(out, src, ours) == ["{{CLIENT_PHONE}}"]  # no phone in the config: flagged, not shipped


def test_whitelabel_export_text_only(factory, tmp_path):
    src = factory.brand(BRAND)
    pid = factory.db.insert("posts", {"brand": BRAND, "format": "short", "status": "approved", "title": "t",
                                      "caption": f"Follow {src.visual.watermark} for more.", "hashtags": ["budget", "moneymadesimple"],
                                      "script": {"title": f"{src.name} budget", "hook": "h", "segments": [
                                          {"heading": "a", "narration": f"At {src.name} we keep it simple.",
                                           "on_screen_text": "x"}], "claims_to_verify": ["Rates as of Nov 2026"]}})
    res = export(factory, BRAND, _client(tmp_path), [pid], render=False, out_root=tmp_path / "out")
    d = res["dir"] / "posts" / "01-short"
    cap = (d / "caption.txt").read_text()
    assert "@acmecu" in cap and "#acmecu" in cap and "AI" in cap and "moneymadesimple" not in cap.lower()
    assert "Acme Community Credit Union" in (d / "script.md").read_text()
    assert "Rates as of Nov 2026" in (res["dir"] / "sources.md").read_text() and res["zip"].exists()
    bad = factory.db.insert("posts", {"brand": BRAND, "format": "short", "status": "approved", "title": "t",
                                      "caption": "See {{BRANCH_HOURS}}", "script": {"title": "x", "segments": []}})
    with pytest.raises(ValueError, match="BRANCH_HOURS"):
        export(factory, BRAND, _client(tmp_path), [bad], render=False, out_root=tmp_path / "out")
    ok = export(factory, BRAND, _client(tmp_path, tokens={"BRANCH_HOURS": "Mon-Fri 9-5"}), [bad], render=False,
                out_root=tmp_path / "out")
    assert "Mon-Fri 9-5" in (ok["dir"] / "posts" / "01-short" / "caption.txt").read_text()
