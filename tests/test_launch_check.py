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
