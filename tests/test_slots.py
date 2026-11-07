from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from contentfactory.scheduler import collisions, next_slot, reslot


def _post(f, fmt="short"):
    out = f.settings.output_dir / "money-made-simple" / f"v{fmt}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b"x")
    return f.db.insert("posts", {"brand": "money-made-simple", "format": fmt, "status": "scheduled", "title": "t",
                                 "caption": "", "script": {}, "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})


def test_platform_times_defaults(factory):
    b = factory.brand("money-made-simple")
    assert b.cadence.times_for("tiktok", "short") == ["18:00"]
    assert b.cadence.times_for("pinterest", "carousel") == ["11:00"]
    assert b.cadence.times_for("youtube", "short") == ["12:30"]
    assert b.cadence.times_for("youtube", "long") == b.cadence.post_times
    ny = ZoneInfo("America/New_York")
    after = datetime(2026, 11, 23, 8, 0, tzinfo=ny)
    assert next_slot(factory.db, b, "tiktok", after=after, fmt="short").astimezone(ny).strftime("%H:%M") == "18:00"
    assert next_slot(factory.db, b, "pinterest", after=after, fmt="carousel").astimezone(ny).strftime("%H:%M") == "11:00"


def test_brand_override_merges():
    from contentfactory.config import Cadence
    c = Cadence(platform_times={"tiktok": ["20:00"]}, platform_weekly_caps={"instagram:short": 3})
    assert c.times_for("tiktok") == ["20:00"] and c.times_for("pinterest") == ["11:00"]
    assert c.weekly_cap("instagram", "mid") == 3 and c.weekly_cap("youtube", "short") is None


def test_reslot_moves_and_caps(factory, monkeypatch):
    b = factory.brand("money-made-simple")
    b.cadence.platform_weekly_caps = {"instagram:short": 3}
    monkeypatch.setattr(factory, "brand", lambda slug: b)
    monkeypatch.setattr(factory, "brands", lambda: {"money-made-simple": b})
    ny = ZoneInfo("America/New_York")
    start = datetime.now(timezone.utc).astimezone(ny).replace(hour=12, minute=30, second=0, microsecond=0) + timedelta(days=2)
    pubs = []
    for k in range(5):  # old plan: everything at 12:30, including TikTok, 5 Reels in 5 days
        pid = _post(factory)
        at = (start + timedelta(days=k)).astimezone(timezone.utc).isoformat()
        for platform in ("tiktok", "instagram"):
            pubs.append(factory.db.insert("publications", {"post_id": pid, "platform": platform, "status": "queued",
                                                           "scheduled_at": at}))
    plan = reslot(factory)
    assert not plan["applied"] and len(plan["dropped"]) == 2
    assert {factory.db.get("publications", p)["status"] for p in pubs} == {"queued"}  # dry run changed nothing
    res = reslot(factory, apply=True)
    assert len(res["dropped"]) == 2 and res["collisions"] == []
    tiktok = factory.db.query("SELECT scheduled_at FROM publications WHERE platform = 'tiktok' AND status = 'queued'")
    assert {datetime.fromisoformat(r["scheduled_at"]).astimezone(ny).strftime("%H:%M") for r in tiktok} == {"18:00"}
    assert factory.db.scalar("SELECT COUNT(*) FROM publications WHERE platform = 'instagram' AND status = 'queued'") == 3
    assert collisions(factory.db) == []
