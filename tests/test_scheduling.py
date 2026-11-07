from datetime import datetime, timezone

import pytest

from contentfactory.guardrails import check_cadence
from contentfactory.scheduler import next_slot


def _approved(factory, n):
    ids = []
    for idea in factory.ideas("money-made-simple", n=n + 2, online=False)[:n]:
        pid = factory.produce(idea)
        factory.approve(pid)
        ids.append(pid)
    return ids


def test_schedule_all_fills_slots_without_breaking_caps(factory, fake_render):
    ids = _approved(factory, 5)
    res = factory.schedule_approved()
    assert set(res["scheduled"]) == set(ids) and not res["skipped"]
    brand = factory.brand("money-made-simple")
    per_day: dict = {}
    for row in factory.db.query("SELECT platform, scheduled_at FROM publications WHERE status='queued'"):
        from zoneinfo import ZoneInfo
        day = datetime.fromisoformat(row["scheduled_at"]).astimezone(ZoneInfo(brand.cadence.timezone)).date()
        per_day[(row["platform"], day)] = per_day.get((row["platform"], day), 0) + 1
    assert max(per_day.values()) <= brand.cadence.max_posts_per_day_per_platform


def test_cadence_uses_brand_local_day(factory):
    brand = factory.brand("money-made-simple")
    brand.cadence.timezone = "America/New_York"
    brand.cadence.max_posts_per_day_per_platform = 1
    pid = factory.db.insert("posts", {"brand": brand.slug, "format": "short", "status": "scheduled", "title": "t"})
    # 23:30 New York on Nov 10 is 04:30 UTC Nov 11: same local day as 09:00 New York Nov 10
    factory.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "queued",
                                       "scheduled_at": "2026-11-11T04:30:00+00:00", "created_at": "x"})
    assert check_cadence(factory.db, brand, "youtube", datetime(2026, 11, 10, 14, 0, tzinfo=timezone.utc)).level == "block"
    assert check_cadence(factory.db, brand, "youtube", datetime(2026, 11, 11, 14, 0, tzinfo=timezone.utc)).level == "ok"
    slot = next_slot(factory.db, brand, "youtube", after=datetime(2026, 11, 10, 13, 0, tzinfo=timezone.utc))
    assert slot.astimezone(timezone.utc).date().isoformat() >= "2026-11-11"


def test_blocked_schedule_leaves_nothing_half_done(factory, fake_render):
    (pid,) = _approved(factory, 1)
    brand = factory.brand("money-made-simple")
    at = datetime(2026, 12, 1, 17, 30, tzinfo=timezone.utc)
    other = factory.db.insert("posts", {"brand": brand.slug, "format": "short", "status": "scheduled", "title": "o"})
    platforms = ["instagram", "youtube"]
    for _ in range(brand.cadence.max_posts_per_day_per_platform):  # fill the LAST platform's day
        factory.db.insert("publications", {"post_id": other, "platform": platforms[-1], "status": "queued",
                                           "scheduled_at": at.isoformat(), "created_at": "x"})
    with pytest.raises(PermissionError):
        factory.schedule(pid, platforms=platforms, at=at)
    assert factory.db.scalar("SELECT COUNT(*) FROM publications WHERE post_id = ?", [pid]) == 0
    assert factory.db.get("posts", pid)["status"] == "approved"


def test_unschedule_returns_post_to_approved(factory, fake_render):
    (pid,) = _approved(factory, 1)
    factory.schedule(pid)
    assert factory.unschedule(pid) >= 1
    assert factory.db.get("posts", pid)["status"] == "approved"
    assert factory.schedule(pid)                           # can be rescheduled
