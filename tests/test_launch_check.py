from datetime import datetime, timedelta, timezone

from contentfactory.launch_check import check_url, render_text, run


def _scheduled(f, caption, days=3, platform="instagram", meta=None, title="A post"):
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "scheduled",
                                "title": title, "caption": caption, "script": {"title": title}, "hashtags": [],
                                "disclosure": "", "meta": meta or {}, "assets": {}})
    at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    f.db.insert("publications", {"post_id": pid, "platform": platform, "status": "queued", "scheduled_at": at})
    return pid


def test_check_url():
    assert check_url("https://moneymadesimple.co/budget?utm_source=ig&utm_medium=bio&utm_campaign=w1") == []
    assert check_url("https://example.com/go/x")[0][0] == "yellow"
    assert any(lvl == "red" and "bad UTM" in m for lvl, m in check_url("https://a.co/x?utm_source=in%20sta"))
    assert any("without utm_source" in m for _, m in check_url("https://a.co/?utm_campaign=x"))
    assert check_url("https://nodot/")[0][0] == "red"


def test_report_levels(factory):
    rep = run(factory)
    assert rep.status == "yellow"  # example brand files carry placeholder product links
    _scheduled(factory, "Save more with this. Made with AI tools. https://moneymadesimple.co/go/hysa")
    _scheduled(factory, "Grab the kit: REPLACE_ME. Made with AI tools.", days=5)
    _scheduled(factory, "Far away REPLACE_ME", days=40)  # outside the 14-day window
    _scheduled(factory, ("x" * 600) + " Made with AI tools.", platform="threads")
    rep = run(factory)
    text = render_text(rep, 14)
    assert rep.status == "red" and text.startswith("Launch check: RED")
    assert "affiliate link without a disclosure" in text
    assert text.count("placeholder left") == 1, text
    assert "threads takes 500" in text


def test_green_when_clean(factory, monkeypatch):
    brand = factory.brand("money-made-simple")
    brand.link_in_bio, brand.products, brand.affiliates = "https://moneymadesimple.co/links", [], []
    monkeypatch.setattr(factory, "brands", lambda: {"money-made-simple": brand})
    monkeypatch.setattr(factory, "brand", lambda slug: brand)
    _scheduled(factory, "One money move a week. Affiliate link: https://moneymadesimple.co/go/hysa. Made with AI tools.")
    rep = run(factory)
    assert rep.status == "green", render_text(rep, 14)


def _video(f, fmt, title, narration, segs=4, **seg_extra):
    script = {"title": title, "hook": title, "segments": [dict({"narration": narration}, **seg_extra) for _ in range(segs)]}
    return f.db.insert("posts", {"brand": "money-made-simple", "format": fmt, "status": "approved", "title": title,
                                 "caption": "", "script": script, "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})


def test_originality_signal(factory):
    for k in range(2):  # too few videos: no signal
        _video(factory, "long", f"Thin video {k}", "Short narration here about money and budgets for everyone today.")
    rep = run(factory)
    assert not any("originality" in f.where for f in rep.findings)
    for k in range(2, 4):
        _video(factory, "long", f"Thin video {k}", "Short narration here about money and budgets for everyone today.")
    rep = run(factory)
    hits = [f for f in rep.findings if "originality" in f.where]
    assert hits and hits[0].level == "red" and "audit-originality" in hits[0].message
    assert "originality risk" in render_text(rep, 14)


def test_originality_medium_is_yellow(factory):
    import random
    rnd = random.Random(1)
    words = "budget rent savings card loan interest paycheck grocery coupon refund bill debt fund goal".split()
    for k in range(4):
        text = " ".join(" ".join(rnd.choice(words) for _ in range(12)) + "." for _ in range(80))
        _video(factory, "long", f"Topic number {k} {rnd.choice(words)}", text, segs=1, chart={"kind": "bar"})
    rep = run(factory)
    hits = [f for f in rep.findings if "originality" in f.where]
    assert hits and hits[0].level == "yellow", hits


def test_disclosure_honesty_and_facebook_reminder(factory, monkeypatch):
    from contentfactory.launch_check import HUMAN_WRITTEN_RE
    assert HUMAN_WRITTEN_RE.search("Script written and fact-checked by a human.")
    assert HUMAN_WRITTEN_RE.search("Researched and written by a human; sources below")
    assert not HUMAN_WRITTEN_RE.search("Script drafted with AI help and fact-checked by a person.")
    brand = factory.brand("money-made-simple")
    assert "drafted with AI help" in brand.ai_disclosure and brand.scripts_by == "ai_assisted"
    brand.ai_disclosure = "Visuals made with AI tools. Script written and fact-checked by a human."
    monkeypatch.setattr(factory, "brands", lambda: {"money-made-simple": brand})
    rep = run(factory)
    assert any(f.level == "red" and "ai_disclosure" in f.where for f in rep.findings)
    brand.scripts_by = "person"
    rep = run(factory)
    assert not any("ai_disclosure" in f.where for f in rep.findings)
    if brand.account("facebook"):
        assert "AI info" in render_text(rep, 14)
