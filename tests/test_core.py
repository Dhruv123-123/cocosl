from datetime import datetime, timedelta, timezone

import pytest

from contentfactory import guardrails
from contentfactory.config import load_brands
from contentfactory.llm import _strict_schema
from contentfactory.schemas import Script


def test_brands_load(home):
    brands = load_brands(home / "brands")
    b = brands["money-made-simple"]
    assert b.account("instagram").handle == "@moneymadesimple"
    assert b.require_human_review is True


def test_strict_schema_is_closed():
    schema = _strict_schema(Script)
    seg = schema["$defs"]["Segment"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    assert seg["additionalProperties"] is False


def test_ideas_dedupe(factory):
    first = factory.ideas("money-made-simple", n=8, online=False)
    assert first
    titles = {i["title"] for i in factory.db.query("SELECT title FROM ideas")}
    assert len(titles) == len(first)


def test_full_flow_dry_run(factory, fake_render):
    idea = factory.ideas("money-made-simple", n=4, online=False)[0]
    post_id = factory.produce(idea)
    post = factory.db.get("posts", post_id)
    assert post["status"] == "in_review"
    assert post["checks"]["status"] in ("ok", "warn")

    with pytest.raises(PermissionError):
        factory.schedule(post_id)  # not approved yet

    factory.approve(post_id)
    pubs = factory.schedule(post_id)
    assert len(pubs) >= 1
    # Publish everything regardless of slot time
    results = factory.publish_due(now=datetime.now(timezone.utc) + timedelta(days=30))
    assert results and all(r["status"] == "dry_run" for r in results)
    assert factory.db.get("posts", post_id)["status"] == "published"


def test_blocked_post_cannot_be_approved(factory, fake_render):
    idea = factory.ideas("money-made-simple", n=2, online=False)[0]
    post_id = factory.produce(idea, render=False)
    post = factory.db.get("posts", post_id)
    meta = post["meta"]
    meta["ai_presenter"] = True
    script = post["script"]
    script["segments"][1]["narration"] = "I've been using this app for a month and it changed my life."
    factory.db.update("posts", post_id, {"meta": meta, "script": script})
    result = factory.check(post_id)
    assert result["status"] == "block"
    with pytest.raises(PermissionError):
        factory.approve(post_id)


def test_originality_blocks_near_duplicates(factory):
    s = {"title": "Roth IRA basics", "hook": "Here is how a Roth IRA works",
         "segments": [{"narration": "You put in money after tax and it grows tax free for retirement " * 3}],
         "cta": "Follow"}
    factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "script": s})
    check = guardrails.check_originality(factory.db, "money-made-simple", guardrails.script_text(s))
    assert check.level == "block"


def test_affiliate_requires_disclosure(factory):
    brand = factory.brand("money-made-simple")
    checks = guardrails.check_disclosures(brand, "Open one here: https://example.com/go/hysa", "", True)
    assert any(c.name == "affiliate_disclosure" and c.level == "block" for c in checks)
    checks = guardrails.check_disclosures(brand, "Affiliate link: https://example.com/go/hysa", "Made with AI tools", True)
    assert all(c.level == "ok" for c in checks)


def test_scheduler_respects_daily_cap(factory, fake_render):
    brand = factory.brand("money-made-simple")
    cap = brand.cadence.max_posts_per_day_per_platform
    slots = []
    for _ in range(cap * 2 + 1):
        idea = factory.ideas("money-made-simple", n=1, online=False)
        if not idea:
            continue
        pid = factory.produce(idea[0])
        factory.approve(pid)
        factory.schedule(pid, platforms=["instagram"])
        slots.append(factory.db.query("SELECT scheduled_at FROM publications WHERE post_id = ?", [pid])[0]["scheduled_at"])
    days = {}
    for s in slots:
        d = datetime.fromisoformat(s).date()
        days[d] = days.get(d, 0) + 1
    assert max(days.values()) <= cap
    assert len(set(slots)) == len(slots)


def test_daily_never_auto_approves(factory, fake_render):
    report = factory.daily("money-made-simple", n_ideas=6, n_produce=2, online=False)
    assert len(report["produced"]) == 2
    statuses = {p["status"] for p in factory.db.query("SELECT status FROM posts")}
    assert "approved" not in statuses and "published" not in statuses


def test_repurpose_long_post(factory, fake_render):
    from contentfactory.repurpose import repurpose_post
    idea = factory.db.insert("ideas", {"brand": "tiny-histories", "title": "The history of the fork",
                                       "angle": "it was scandalous", "format": "long", "pillar": "origins"})
    parent = factory.produce(idea)
    kids = repurpose_post(factory, parent, n_shorts=3)
    posts = [factory.db.get("posts", k) for k in kids]
    assert [p["format"] for p in posts].count("short") == 3
    assert any(p["format"] == "carousel" for p in posts)
    assert all(p["meta"]["parent_post"] == parent for p in posts)


def test_insights_rescore(factory):
    from contentfactory.insights import report, rescore_backlog
    db = factory.db
    for i, (fmt, views) in enumerate([("short", 100)] * 3 + [("carousel", 1000)] * 3):
        idea = db.insert("ideas", {"brand": "money-made-simple", "title": f"t{i}", "format": fmt, "pillar": "p", "status": "used"})
        post = db.insert("posts", {"brand": "money-made-simple", "idea_id": idea, "format": fmt, "status": "published"})
        pub = db.insert("publications", {"post_id": post, "platform": "instagram", "status": "published",
                                         "published_at": "2099-01-01T12:00:00+00:00"})
        db.insert("metrics", {"publication_id": pub, "captured_at": "2099-01-02T00:00:00+00:00", "views": views, "likes": 10})
    r = report(db, days=36500 * 2)
    assert r["by_format"][0]["format"] == "carousel"
    db.insert("ideas", {"brand": "money-made-simple", "title": "new carousel", "format": "carousel", "pillar": "p", "score": 5})
    db.insert("ideas", {"brand": "money-made-simple", "title": "new short", "format": "short", "pillar": "p", "score": 5})
    assert rescore_backlog(db, "money-made-simple") == 2
    scores = {i["format"]: i["score"] for i in db.query("SELECT * FROM ideas WHERE status='new'")}
    assert scores["carousel"] > scores["short"]


def test_niche_and_brand_generation(factory):
    from contentfactory.config import load_brands
    from contentfactory.niche import generate_brand, score_niche, write_brand
    good = score_niche("personal finance software for freelancers", online=False)
    bad = score_niche("crypto reddit stories", online=False)
    assert good.score > bad.score and bad.risk_flags
    data, slug = generate_brand(factory.llm, "home espresso", "new coffee nerds")
    write_brand(factory.settings.brands_dir, data, slug)
    assert slug in load_brands(factory.settings.brands_dir)


def test_write_env(tmp_path, monkeypatch):
    from contentfactory.publish.tokens import write_env
    env = tmp_path / ".env"
    env.write_text("A=1\nYT_REFRESH_TOKEN=old\n")
    write_env(env, {"YT_REFRESH_TOKEN": "new=val", "B": "2"})
    text = env.read_text()
    assert "YT_REFRESH_TOKEN=new=val" in text and "A=1" in text and "B=2" in text
    monkeypatch.delenv("B", raising=False)


def test_weekly_report(factory, fake_render):
    from contentfactory.reports import save_report, to_markdown, weekly_report
    idea = factory.ideas("money-made-simple", n=2, online=False)[0]
    factory.produce(idea)
    factory.db.insert("revenue", {"date": __import__("datetime").date.today().isoformat(), "source": "ugc",
                                  "amount_cents": 24900})
    r = weekly_report(factory)
    assert r["money"]["revenue_week"] == 24900 and r["content"]["in_review"] == 1
    md = to_markdown(r)
    assert "Review 1 post" in md and "$249.00" in md
    assert save_report(factory).endswith(".md")


def test_weekly_report_posted_platforms_and_campaigns(factory, fake_render):
    from datetime import date, datetime, timedelta, timezone

    from contentfactory.reports import to_markdown, weekly_report
    idea = factory.ideas("money-made-simple", n=2, online=False)[0]
    pid = factory.produce(idea)
    factory.approve(pid)
    (pub,) = factory.schedule(pid, platforms=["youtube"])
    factory.publish_due(datetime.now(timezone.utc) + timedelta(days=3))
    factory.db.execute("UPDATE publications SET status='published', url='https://youtu.be/x', published_at=? WHERE id=?",
                       [datetime.now(timezone.utc).isoformat(), pub])
    factory.db.insert("metrics", {"publication_id": pub, "captured_at": datetime.now(timezone.utc).isoformat(),
                                  "views": 1500, "likes": 40, "link_clicks": 12})
    factory.db.insert("revenue", {"date": date.today().isoformat(), "source": "product", "brand": "money-made-simple",
                                  "amount_cents": 1200, "note": "Gumroad | utm_source=youtube utm_campaign=budget-launch"})
    r = weekly_report(factory)
    md = to_markdown(r)
    assert "money-made-simple · youtube: 1 post(s); 1,500 views, 40 likes, 12 link clicks" in md
    assert "budget-launch: 1 sale(s), $12.00 (from youtube)" in md


def test_repurpose_text_drafts(factory):
    import pytest

    from contentfactory.repurpose import text_drafts
    from contentfactory.writer import _offline_script
    brand = factory.brand("money-made-simple")
    script = _offline_script(brand, "How a high-yield savings account works", "the math", "long")
    pid = factory.db.insert("posts", {"brand": brand.slug, "format": "long", "status": "approved",
                                      "title": script.title, "script": script.model_dump()})
    with pytest.raises(ValueError, match="isn't published"):
        text_drafts(factory, pid)
    factory.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "published",
                                       "url": "https://www.youtube.com/watch?v=VID9"})
    paths = text_drafts(factory, pid)
    assert set(paths) == {"blog.md", "newsletter.md", "pins.md", "thread.md"}
    blog = paths["blog.md"].read_text()
    assert blog.startswith("---\n") and "draft: true" in blog and "DRAFT" in blog
    assert "utm_source=blog" in blog and "watch?v=VID9" in blog
    assert paths["pins.md"].read_text().count("## Pin") == 3
    thread = paths["thread.md"].read_text()
    assert thread.count("---") >= 4 and all(len(p) <= 300 for p in thread.split("---"))
    assert factory.db.get("posts", pid)["meta"]["text_drafts"]["blog.md"].endswith("blog.md")
