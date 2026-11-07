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


def _approved(f, fmt="short", day=None, n=[0]):
    n[0] += 1
    d = f.settings.output_dir / "money-made-simple" / f"post-{n[0]}"
    d.mkdir(parents=True, exist_ok=True)
    name = "slide-01.png" if fmt == "carousel" else "video.mp4"
    (d / name).write_bytes(f"unique {n[0]} {fmt}".encode())
    rel = f"money-made-simple/post-{n[0]}/{name}"
    assets = {"slides": [rel]} if fmt == "carousel" else {"video": rel}
    meta = {"plan_date": day} if day else {}
    return f.db.insert("posts", {"brand": "money-made-simple", "format": fmt, "status": "approved", "title": f"t{n[0]}",
                                 "caption": "c", "script": {}, "hashtags": [], "disclosure": "", "meta": meta,
                                 "assets": assets})


def _local(f, pid):
    ny = ZoneInfo("America/New_York")
    return {r["platform"]: datetime.fromisoformat(r["scheduled_at"]).astimezone(ny)
            for r in f.db.query("SELECT platform, scheduled_at FROM publications WHERE post_id = ? AND status = 'queued'", [pid])}


def test_one_post_one_day_everywhere(factory):
    """Day 2's Short used to land on Facebook at 19:00 on Day 1 (a free evening slot) while YouTube had Day 2."""
    a = _approved(factory)
    factory.schedule(a)
    b = _approved(factory)
    factory.schedule(b)
    days = {p: t.date() for p, t in _local(factory, b).items()}
    assert len(set(days.values())) == 1, days
    assert min(_local(factory, a).values()).date() < next(iter(days.values()))


def test_plan_date_sets_the_day(factory):
    ny = ZoneInfo("America/New_York")
    base = (datetime.now(timezone.utc).astimezone(ny) + timedelta(days=3)).date()
    # seven planned Shorts on seven days: the plan wins over shorts_per_week (5), like LAUNCH_WEEK.md
    ids = [_approved(factory, "short", (base + timedelta(days=k)).isoformat()) for k in range(7)]
    car = _approved(factory, "carousel", base.isoformat())
    long_ = _approved(factory, "long", (base + timedelta(days=1)).isoformat())  # its Pinterest pin would take 11:00
    res = factory.schedule_approved("money-made-simple")
    assert not res["skipped"], res
    for k, pid in enumerate(ids):
        assert {t.date() for t in _local(factory, pid).values()} == {base + timedelta(days=k)}
    shorts = _local(factory, ids[0])
    assert shorts["youtube"].strftime("%H:%M") == "12:30" and shorts["tiktok"].strftime("%H:%M") == "18:00"
    assert _local(factory, long_)["youtube"].strftime("%H:%M") == "19:00"  # the Short took 12:30 first
    assert _local(factory, car)["instagram"].strftime("%H:%M") == "19:00" and _local(factory, car)["instagram"].date() == base
    # a past plan date falls back to the next free slot
    old = _approved(factory, "short", "2020-01-01")
    factory.schedule(old)
    assert min(_local(factory, old).values()) > datetime.now(timezone.utc)


def test_reslot_keeps_each_post_on_its_day(factory):
    ny = ZoneInfo("America/New_York")
    day = (datetime.now(timezone.utc).astimezone(ny) + timedelta(days=4)).replace(hour=9, minute=0, second=0, microsecond=0)
    pid = _post(factory)
    pub = factory.db.insert("publications", {"post_id": pid, "platform": "tiktok", "status": "queued",
                                             "scheduled_at": day.astimezone(timezone.utc).isoformat()})
    reslot(factory, apply=True)
    moved = datetime.fromisoformat(factory.db.get("publications", pub)["scheduled_at"]).astimezone(ny)
    assert moved.date() == day.date() and moved.strftime("%H:%M") == "18:00"  # not pulled forward to an earlier day


def test_import_date_is_saved(factory, tmp_path):
    import json
    from contentfactory.cli import main
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps([{"format": "carousel", "date": "2026-11-09", "script": {
        "title": "Dated", "hook": "h", "cta": "", "description": "", "thumbnail_text": "", "sources": [], "segments": [{"heading": "a", "narration": "", "on_screen_text": "a",
                                                    "visual_prompt": "a"}], "caption": "c", "hashtags": [],
        "claims_to_verify": []}}]))
    main(["--home", str(factory.settings.home), "import", str(pack), "--brand", "money-made-simple", "--no-render"])
    pid = factory.db.scalar("SELECT id FROM posts WHERE title = 'Dated'")
    assert factory.db.get("posts", pid)["meta"]["plan_date"] == "2026-11-09"
