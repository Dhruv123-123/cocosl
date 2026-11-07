from datetime import datetime, timedelta, timezone

import pytest

from contentfactory.manual import is_manual, mark_done, pending
from contentfactory.planner import entries, to_ics


def _tiktok(f, minutes=-5, platform="tiktok"):
    out = f.settings.output_dir / "money-made-simple" / "v.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b"fake video")
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "scheduled",
                                "title": "Budget in 3 steps", "caption": "The 3-step budget.", "script": {"title": "x"},
                                "hashtags": ["budget"], "disclosure": "", "meta": {},
                                "assets": {"video": "money-made-simple/v.mp4"}})
    at = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
    pub = f.db.insert("publications", {"post_id": pid, "platform": platform, "status": "queued", "scheduled_at": at})
    return pid, pub


def test_tiktok_is_packaged_not_uploaded(factory, monkeypatch):
    assert is_manual("tiktok") and not is_manual("youtube")
    import contentfactory.publish as publish
    monkeypatch.setattr(publish, "get_publisher", lambda *a, **k: pytest.fail("must not upload to TikTok"))
    pid, pub = _tiktok(factory)
    res = factory.publish_due()
    assert res[0]["status"] == "manual"
    row = factory.db.get("publications", pub)
    assert row["status"] == "manual"
    d = factory.settings.output_dir / row["meta"]["manual"]["dir"]
    assert (d / "video.mp4").read_bytes() == b"fake video"
    assert "The 3-step budget." in (d / "caption.txt").read_text()
    assert f"factory manual done {pub}" in (d / "POST_AT.txt").read_text()
    items = pending(factory)
    assert items[0]["due"] and "The 3-step budget." in items[0]["caption"]
    assert factory.publish_due() == []  # not picked up again
    with pytest.raises(ValueError):
        mark_done(factory, pub, "tiktok.com/x")
    mark_done(factory, pub, "https://www.tiktok.com/@mms/video/1")
    assert factory.db.get("publications", pub)["status"] == "published"
    assert factory.db.get("posts", pid)["status"] == "published"


def test_calendar_and_today_say_post_by_hand(factory):
    _tiktok(factory, minutes=24 * 60)
    rows = entries(factory, 7)
    assert rows[0]["by_hand"]
    assert "POST BY HAND" in to_ics(rows)


def test_api_mode_when_not_manual(factory, monkeypatch):
    monkeypatch.setenv("MANUAL_PLATFORMS", "")
    assert not is_manual("tiktok")
