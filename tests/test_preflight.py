"""Media preflight: platform limits checked before scheduling and again before upload."""
from datetime import datetime, timedelta, timezone

import pytest

from contentfactory.publish.preflight import blocking, check


def _post(output, fmt="short", seconds=30.0, slides=0, jpeg=True, video=True, size=10):
    d = output / "b" / "post-1"
    d.mkdir(parents=True, exist_ok=True)
    assets = {"video": None, "slides": [], "images": [], "duration": seconds, "thumbnail": None}
    if fmt in ("short", "mid", "long") and video:
        (d / "video.mp4").write_bytes(b"\x00" * size)
        assets["video"] = "b/post-1/video.mp4"
    for i in range(slides):
        (d / f"slide-{i:02d}.png").write_bytes(b"\x00")
        if jpeg:
            (d / f"slide-{i:02d}.jpg").write_bytes(b"\x00")
        assets["slides"].append(f"b/post-1/slide-{i:02d}.png")
    return {"id": 1, "brand": "b", "format": fmt, "assets": assets}


def msgs(issues):
    return " | ".join(str(i) for i in issues)


def test_limits(tmp_path):
    base = "https://media.example.com"
    assert check(_post(tmp_path, seconds=45), "youtube", tmp_path, base) == []
    assert "limit is 180s" in msgs(check(_post(tmp_path, seconds=200), "youtube", tmp_path, base))
    assert "limit is 90s" in msgs(check(_post(tmp_path, seconds=120), "facebook", tmp_path, base))
    assert "minimum is 3s" in msgs(check(_post(tmp_path, seconds=2), "tiktok", tmp_path, base))
    long = check(_post(tmp_path, "long", seconds=20 * 60), "youtube", tmp_path, base)
    assert [i.level for i in long] == ["warn", "warn"]  # over 15 min (verified channels fine) + no thumbnail
    assert "doesn't take long" in msgs(check(_post(tmp_path, "long"), "instagram", tmp_path, base))
    assert "video file is missing" in msgs(check(_post(tmp_path, video=False), "tiktok", tmp_path, base))
    assert "PUBLIC_MEDIA_BASE_URL" in msgs(check(_post(tmp_path), "instagram", tmp_path, ""))


def test_carousels(tmp_path):
    base = "https://media.example.com"
    assert check(_post(tmp_path, "carousel", slides=5), "instagram", tmp_path, base) == []
    assert "11 slides; instagram takes 2-10" in msgs(check(_post(tmp_path, "carousel", slides=11), "instagram",
                                                            tmp_path, base))
    assert check(_post(tmp_path, "carousel", slides=11), "threads", tmp_path, base) == []
    fresh = tmp_path / "fresh"
    assert "no JPEG" in msgs(check(_post(fresh, "carousel", slides=3, jpeg=False), "instagram", fresh, base))
    assert "doesn't take carousel" in msgs(check(_post(tmp_path, "carousel", slides=3), "youtube", tmp_path, base))


def test_dry_run_ignores_public_url_and_switch(tmp_path, monkeypatch):
    issues = check(_post(tmp_path), "instagram", tmp_path, "")
    assert blocking(issues, dry_run=True) == [] and blocking(issues, dry_run=False)
    monkeypatch.setenv("FACTORY_PREFLIGHT", "0")
    assert blocking(issues, dry_run=False) == []


@pytest.fixture
def live_factory(factory, monkeypatch):
    monkeypatch.setenv("FACTORY_PREFLIGHT", "1")
    return factory


def _approved(f, fmt="short", seconds=30.0):
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": fmt, "status": "approved", "title": "t",
                                "script": {}, "caption": "c", "hashtags": [], "disclosure": "Made with AI tools."})
    post = _post(f.settings.output_dir, fmt, seconds=seconds, slides=3 if fmt == "carousel" else 0)
    f.db.update("posts", pid, {"assets": post["assets"]})
    return pid


def test_schedule_blocks_on_bad_media(live_factory):
    f = live_factory
    platforms = [a.platform for a in f.brand("money-made-simple").accounts if a.enabled and "short" in a.formats]
    assert "youtube" in platforms
    pid = _approved(f, seconds=400)  # too long for a Short
    with pytest.raises(PermissionError, match="Media check failed: youtube"):
        f.schedule(pid)
    assert f.db.get("posts", pid)["status"] == "approved"
    assert not f.db.query("SELECT id FROM publications WHERE post_id = ?", [pid])
    ok = _approved(f, seconds=40)
    assert f.schedule(ok, platforms=["youtube"])


def test_publish_fails_clearly_when_media_vanished(live_factory):
    f = live_factory
    pid = _approved(f, seconds=40)
    [pub] = f.schedule(pid, platforms=["youtube"])
    (f.settings.output_dir / "b" / "post-1" / "video.mp4").unlink()
    res = f.publish_due(datetime.now(timezone.utc) + timedelta(days=30))
    assert res and res[0]["status"] == "failed" and res[0]["retry"] is False
    row = f.db.get("publications", pub)
    assert row["status"] == "failed" and "video file is missing" in row["error"] and row["attempts"] == 0


def test_tiktok_cut_format(tmp_path):
    base = "https://media.example.com"
    assert check(_post(tmp_path, "mid", seconds=75), "tiktok", tmp_path, base) == []
    short_cut = check(_post(tmp_path, "mid", seconds=50), "tiktok", tmp_path, base)
    assert [i.level for i in short_cut] == ["warn"] and "over a minute" in short_cut[0].message
    assert "doesn't take mid" in msgs(check(_post(tmp_path, "mid", seconds=75), "youtube", tmp_path, base))
    assert "doesn't take mid" in msgs(check(_post(tmp_path, "mid", seconds=75), "facebook", tmp_path, base))


def test_mid_posts_go_to_tiktok_only_and_reels_to_facebook(factory, fake_render):
    brand = factory.brand("money-made-simple")
    assert [a.platform for a in brand.accounts if "mid" in a.formats] == ["tiktok"]
    assert "facebook" in [a.platform for a in brand.accounts if "short" in a.formats]
    from contentfactory.writer import FORMAT_SPECS, write_script
    assert "65-90" in FORMAT_SPECS["mid"]
    script = write_script(factory.llm, brand, "Why your budget breaks in week two", "angle", "mid")
    assert len(script.segments) == 9
