"""Rehearsal of a live day with real media: render (ffmpeg) -> approve -> schedule -> publish with
dry run OFF -> metrics, against mocked official APIs. Proves the whole chain without touching a platform."""
import json
import shutil
from datetime import datetime, timedelta, timezone

import httpx
import pytest

import contentfactory.publish as pubmod
from contentfactory.publish.youtube import YouTubePublisher

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                                reason="ffmpeg/ffprobe required")

SCRIPT = {
    "title": "Why your savings account pays so little",
    "hook": "Your savings account is probably paying you almost nothing.",
    "segments": [
        {"heading": "Hook", "narration": "Your savings account is probably paying you almost nothing.",
         "on_screen_text": "Your bank is underpaying you", "visual_prompt": "a piggy bank on a shelf"},
        {"heading": "Fix", "narration": "Compare three high yield accounts tonight and move your emergency fund.",
         "on_screen_text": "Compare three tonight", "visual_prompt": "a checklist"},
    ],
    "cta": "Follow for one money move a week.", "caption": "Same safety, better rate. Compare before you move.",
    "hashtags": ["money", "savings"], "description": "Why big banks pay so little on savings.",
    "thumbnail_text": "Your bank underpays you", "sources": [], "claims_to_verify": [],
}


def test_live_day_rehearsal_youtube(factory, monkeypatch):
    factory.settings.extra.update(video_fps=12, x264_preset="ultrafast")
    for k, v in {"YT_CLIENT_ID": "cid", "YT_CLIENT_SECRET": "sec", "YT_REFRESH_TOKEN": "rt"}.items():
        monkeypatch.setenv(k, v)
    calls = []
    session = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&upload_id=XYZ"

    def handler(req: httpx.Request) -> httpx.Response:
        req.read()
        calls.append(req)
        url = str(req.url)
        if "oauth2.googleapis.com/token" in url:
            return httpx.Response(200, json={"access_token": "at", "expires_in": 3600})
        if req.method == "POST" and "upload/youtube/v3/videos" in url:
            return httpx.Response(200, headers={"Location": session})
        if req.method == "PUT" and "upload_id=XYZ" in url:
            return httpx.Response(201, json={"id": "VID9", "status": {"uploadStatus": "uploaded"}})
        if "thumbnails/set" in url:
            return httpx.Response(200, json={"items": []})
        if req.method == "GET" and "youtube/v3/videos" in url:
            return httpx.Response(200, json={"items": [{"statistics": {"viewCount": "321", "likeCount": "12",
                                                                       "commentCount": "3"}}]})
        return httpx.Response(404, json={"error": {"message": "unrouted " + url}})

    real = pubmod.get_publisher

    def get_publisher(platform, settings, dry_run=None):
        if platform == "youtube" and not (dry_run if dry_run is not None else settings.dry_run):
            return YouTubePublisher(settings, transport=httpx.MockTransport(handler), sleep=lambda s: None)
        return real(platform, settings, dry_run)
    monkeypatch.setattr(pubmod, "get_publisher", get_publisher)
    monkeypatch.setattr("contentfactory.publish.tokens.refresh_long_lived", lambda s: None)

    pid = factory.import_script("money-made-simple", SCRIPT, "short")
    post = factory.db.get("posts", pid)
    assert post["status"] == "in_review", post["checks"]
    video = factory.settings.output_dir / post["assets"]["video"]
    assert video.stat().st_size > 10_000
    factory.approve(pid)
    (pub_id,) = factory.schedule(pid, platforms=["youtube"])

    factory.settings.dry_run = False
    later = datetime.now(timezone.utc) + timedelta(days=30)
    res = factory.publish_due(later)
    assert res == [{"publication": pub_id, "status": "published", "url": "https://www.youtube.com/shorts/VID9"}]
    assert factory.publish_due(later) == []                                     # nothing goes twice

    init = next(c for c in calls if c.method == "POST" and "upload/youtube/v3/videos" in str(c.url))
    meta = json.loads(init.content)
    assert meta["status"]["privacyStatus"] == "private"                          # safe default
    assert "containsSyntheticMedia" in meta["status"]
    assert "AI" in meta["snippet"]["description"]                                # disclosure travels with it
    put = next(c for c in calls if c.method == "PUT")
    assert len(put.content) == video.stat().st_size                              # the real file was uploaded

    assert factory.collect_metrics() == 1
    m = factory.db.one("SELECT * FROM metrics")
    assert m["views"] == 321
    assert factory.db.get("posts", pid)["status"] == "published"
