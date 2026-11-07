from datetime import datetime, timedelta, timezone

from contentfactory.cleanup import run


def _post(f, status="published", days=90, pub_status="published", extra_queued=False):
    root = f.settings.output_dir
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": status, "title": "t",
                                "script": {}})
    d = root / "money-made-simple" / f"post-{pid}"
    d.mkdir(parents=True)
    for name in ("video.mp4", "audio.wav", "img-0.png", "thumbnail.png", "captions.srt"):
        (d / name).write_bytes(b"x" * 1000)
    rel = f"money-made-simple/post-{pid}/"
    f.db.update("posts", pid, {"assets": {"video": rel + "video.mp4", "audio": rel + "audio.wav",
                                          "images": [rel + "img-0.png"], "thumbnail": rel + "thumbnail.png",
                                          "captions_srt": rel + "captions.srt"}})
    at = (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat()
    f.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": pub_status, "scheduled_at": at,
                                 "published_at": at if pub_status == "published" else ""})
    if extra_queued:
        f.db.insert("publications", {"post_id": pid, "platform": "tiktok", "status": "queued", "scheduled_at": at})
    return pid, d


def test_cleanup_only_old_finished_posts(factory):
    old, d_old = _post(factory)
    recent, d_recent = _post(factory, days=5)
    pending, d_pending = _post(factory, extra_queued=True)
    res = run(factory, 60)
    assert res == {"posts": 1, "bytes": 3000, "deleted": False} and (d_old / "video.mp4").exists()
    run(factory, 60, confirm=True)
    assert not (d_old / "video.mp4").exists() and not (d_old / "audio.wav").exists()
    assert (d_old / "thumbnail.png").exists() and (d_old / "captions.srt").exists()
    assert factory.db.get("posts", old)["assets"]["cleaned"]["removed"]
    assert (d_recent / "video.mp4").exists() and (d_pending / "video.mp4").exists()
    assert run(factory, 60)["posts"] == 0  # nothing left to free
