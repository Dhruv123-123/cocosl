from datetime import date, datetime, timedelta, timezone

from contentfactory import routine


def _post(f, status="in_review", title="A post"):
    return f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": status, "title": title,
                                 "caption": "Cap. Made with AI tools.", "script": {"title": title}, "hashtags": [],
                                 "disclosure": "", "meta": {}, "assets": {}})


def test_today_routine(factory, monkeypatch):
    for k in range(4):
        _post(factory, title=f"Review me {k}")
    pid = _post(factory, status="scheduled", title="Hand post")
    now = datetime.now(timezone.utc).isoformat()
    factory.db.insert("publications", {"post_id": pid, "platform": "tiktok", "status": "manual", "scheduled_at": now})
    from contentfactory.community.store import ensure_schema
    ensure_schema(factory.db)
    factory.db.insert("comments", {"brand": "money-made-simple", "platform": "youtube", "remote_id": "c1",
                                   "author": "Sam", "text": "How do I start a budget?", "status": "drafted",
                                   "created_at": now, "updated_at": now})
    monkeypatch.setenv("MANUAL_PLATFORMS", "tiktok,pinterest")
    monkeypatch.setenv("FACTORY_LAUNCH_DATE", "2026-11-04")
    sat = date(2026, 11, 14)  # Saturday, LAUNCH codes end, day 10
    r = routine.collect(factory, sat, cap=True)
    assert len(r["review"]) == 2 and r["more"]["review"] == 2
    assert [p["post_id"] for p in r["by_hand"]] == [pid]
    text = routine.to_text(r)
    assert "Hand post" in text and "factory manual done" in text
    assert "Sam: How do I start a budget?" in text and "draft ready" in text
    assert "LAUNCH codes" in text and "Day 10" in text and "batch-record" in text
    assert "Ad studio" not in text  # weekday only
    mon = routine.to_text(routine.collect(factory, date(2026, 11, 16), cap=False))
    assert "factory report" in mon and "Ad studio" in mon and "more waiting" not in mon
    md = routine.to_markdown(r)
    assert md.startswith("# Today") and "## 3. Post by hand" in md and "- [ ] " in md


def test_cli(factory, capsys):
    from contentfactory.cli import main
    main(["today", "--15min", "--date", (date.today() + timedelta(days=1)).isoformat()])
    out = capsys.readouterr().out
    assert "1. Triage" in out and "15 minutes" in out
