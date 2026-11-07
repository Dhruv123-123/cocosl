from datetime import datetime, timedelta, timezone

import pytest

from contentfactory.planner import entries, export, flag, recordings, to_ics


def _pub(f, brand, platform, at, fmt="short", account=""):
    pid = f.db.insert("posts", {"brand": brand, "format": fmt, "status": "scheduled", "title": f"{brand} post",
                                "script": {}})
    f.db.insert("publications", {"post_id": pid, "platform": platform, "status": "queued", "account": account,
                                 "scheduled_at": at.isoformat()})
    return pid


@pytest.fixture
def two_brands(factory):
    brands = factory.brands()
    assert {"money-made-simple", "tiny-histories"} <= set(brands)
    return factory


def test_flags_caps_and_collisions(two_brands):
    f = two_brands
    day = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=17, minute=0, second=0, microsecond=0)
    for h in range(3):  # cap for money-made-simple is 2/day/platform
        _pub(f, "money-made-simple", "instagram", day + timedelta(hours=h))
    _pub(f, "tiny-histories", "youtube", day + timedelta(minutes=30), account="@same")
    _pub(f, "money-made-simple", "youtube", day + timedelta(minutes=50), account="@same")
    rows = entries(f, 7)
    problems = flag(f, rows)
    assert any(p.startswith("over cap:") and "instagram" in p and "cap 2" in p for p in problems)
    col = [p for p in problems if p.startswith("collision:")]
    assert len(col) == 1 and "youtube" in col[0] and "SAME account" in col[0]
    assert all(r["flags"] for r in rows if r["platform"] == "instagram")


def test_exports(two_brands, tmp_path):
    f = two_brands
    at = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
    _pub(f, "money-made-simple", "tiktok", at)
    res = export(f, tmp_path, days=14)
    ics = res["ics"].read_bytes().decode()
    assert ics.startswith("BEGIN:VCALENDAR\r\n") and ics.count("BEGIN:VEVENT") == 1 and "\r\n" in ics
    assert all(len(line.encode()) <= 75 for line in ics.split("\r\n"))
    page = res["html"].read_text()
    assert "money-made-simple" in page and "tiktok" in page and "every brand is within its caps" in page
    long_title = to_ics([{"at": at, "pub_id": 1, "post_id": 1, "status": "queued", "brand": "b", "platform": "p",
                          "format": "short", "title": "é" * 120, "flags": ["x"]}])
    assert all(len(line.encode()) <= 75 for line in long_title.split("\r\n"))


def test_recordings_todo_and_own_voice_blocks_schedule(two_brands, tmp_path):
    f = two_brands
    seg = {"heading": "h", "narration": "n", "on_screen_text": "o", "visual_prompt": "v"}
    a = f.db.insert("posts", {"brand": "money-made-simple", "format": "long", "status": "in_review", "title": "A",
                              "script": {"segments": [seg], "original_element": "Record the IRS payment page"}})
    b = f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "approved", "title": "B",
                              "script": {"segments": [dict(seg, footage="footage/x.mp4")]},
                              "meta": {"own_voice": True}, "assets": {"video": "v.mp4"}})
    f.db.insert("publications", {"post_id": b, "platform": "tiktok", "status": "queued",
                                 "scheduled_at": "2026-12-01T17:00:00+00:00"})
    todo = recordings(f)
    assert [t["post_id"] for t in todo] == [b, a]  # scheduled first
    assert any("factory voice" in n for n in todo[0]["needs"]) and any("footage/x.mp4" in n for n in todo[0]["needs"])
    assert "IRS payment page" in todo[1]["needs"][0]
    f.db.execute("DELETE FROM publications")
    with pytest.raises(PermissionError, match="Waiting for your narration"):
        f.schedule(b)
