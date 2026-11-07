"""Offline tests for the platform adapters (httpx.MockTransport, no network)."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from contentfactory.config import BrandProfile, Settings
from contentfactory.publish import MissingCredentials, PublishError, PublishRequest
from contentfactory.publish._text import count_hashtags, fit_caption
from contentfactory.publish.facebook import FacebookPublisher
from contentfactory.publish.instagram import InstagramPublisher
from contentfactory.publish.postiz import PostizPublisher
from contentfactory.publish.threads import ThreadsPublisher
from contentfactory.publish.tiktok import TikTokPublisher, chunk_plan, chunk_ranges
from contentfactory.publish.youtube import YouTubePublisher
from contentfactory.publish import oauth

DISCLOSURE = "Visuals and voice made with AI tools. Not financial advice."

ALL_ENV = ["IG_USER_ID", "IG_ACCESS_TOKEN", "IG_API_HOST", "IG_SEND_AI_LABEL", "YT_CLIENT_ID", "YT_CLIENT_SECRET",
           "YT_REFRESH_TOKEN", "YT_PRIVACY", "YT_CATEGORY_ID", "TIKTOK_ACCESS_TOKEN", "TIKTOK_PRIVACY",
           "TIKTOK_UPLOAD_MODE", "FB_PAGE_ID", "FB_PAGE_TOKEN", "THREADS_USER_ID", "THREADS_ACCESS_TOKEN",
           "POSTIZ_URL", "POSTIZ_API_KEY", "POSTIZ_INTEGRATION_IDS"]


# --------------------------------------------------------------------------- helpers
class Router:
    """MockTransport handler: routes by (METHOD, substring of URL); records calls."""

    def __init__(self):
        self.routes: list[tuple[str, str, object]] = []
        self.calls: list[httpx.Request] = []

    def add(self, method: str, fragment: str, response):
        self.routes.append((method, fragment, response))
        return self

    def __call__(self, request: httpx.Request) -> httpx.Response:
        request.read()
        self.calls.append(request)
        url = str(request.url)
        for method, frag, resp in self.routes:
            if request.method == method and frag in url:
                out = resp(request) if callable(resp) else resp
                if isinstance(out, httpx.Response):
                    return out
                return httpx.Response(200, json=out)
        return httpx.Response(404, json={"error": {"message": f"unrouted {request.method} {url}"}})

    def find(self, method: str, fragment: str) -> list[httpx.Request]:
        return [c for c in self.calls if c.method == method and fragment in str(c.url)]

    @property
    def transport(self):
        return httpx.MockTransport(self)


def form(req: httpx.Request) -> dict:
    return {k: v[0] for k, v in parse_qs(req.content.decode()).items()}


def body_json(req: httpx.Request) -> dict:
    return json.loads(req.content)


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for k in ALL_ENV:
        monkeypatch.delenv(k, raising=False)
    out = tmp_path / "output"
    out.mkdir()
    return Settings(home=tmp_path, db_path=tmp_path / "f.db", output_dir=out, brands_dir=tmp_path / "brands",
                    dry_run=False)


@pytest.fixture
def brand():
    return BrandProfile(slug="mms", name="Money Made Simple", niche="finance", audience="20s",
                        ai_disclosure=DISCLOSURE)


@pytest.fixture
def files(tmp_path):
    video = tmp_path / "output" / "v.mp4"
    video.parent.mkdir(exist_ok=True)
    video.write_bytes(b"\x00" * 2048)
    imgs = []
    for i in range(3):
        p = tmp_path / "output" / f"s{i}.jpg"
        p.write_bytes(b"\xff\xd8" + b"\x00" * 100)
        imgs.append(p)
    thumb = tmp_path / "output" / "thumb.png"
    thumb.write_bytes(b"\x89PNG" + b"\x00" * 50)
    return {"video": video, "images": imgs, "thumb": thumb}


def make_req(brand, settings, platform, fmt, files, public=True, **kw) -> PublishRequest:
    urls = {}
    if public:
        for p in [files["video"], files["thumb"], *files["images"]]:
            urls[str(p)] = f"https://cdn.example.com/{p.name}"
    defaults = dict(platform=platform, brand=brand, settings=settings, format=fmt, title="Roth IRA in 60 seconds",
                    caption=f"One money move.\n\n{DISCLOSURE}\n\n#money #roth", description="Long description",
                    tags=["money", "roth ira"], video_path=files["video"], image_paths=files["images"],
                    thumbnail_path=files["thumb"], public_urls=urls)
    defaults.update(kw)
    return PublishRequest(**defaults)


def noop_sleep(_):
    pass


# --------------------------------------------------------------------------- captions
def test_fit_caption_trims_hashtags_first_and_keeps_disclosure():
    tags = " ".join(f"#tag{i}" for i in range(40))
    text = f"Body text here.\n\n{DISCLOSURE}\n\n{tags}"
    out = fit_caption(text, 2200, 30, protected=[DISCLOSURE])
    assert count_hashtags(out) == 30 and DISCLOSURE in out and "#tag29" in out and "#tag30" not in out
    long_text = "x" * 3000 + f"\n\n{DISCLOSURE}\n\n#a #b"
    out = fit_caption(long_text, 2200, 30, protected=[DISCLOSURE])
    assert len(out) <= 2200 and DISCLOSURE in out and "#a" not in out


# --------------------------------------------------------------------------- credentials
@pytest.mark.parametrize("cls", [InstagramPublisher, YouTubePublisher, TikTokPublisher, FacebookPublisher,
                                 ThreadsPublisher, PostizPublisher])
def test_missing_credentials(cls, settings, brand, files):
    pub = cls(settings, transport=Router().transport, sleep=noop_sleep)
    with pytest.raises(MissingCredentials) as e:
        pub.publish(make_req(brand, settings, pub.platform, "short", files))
    assert e.value.keys == cls.required_env


# --------------------------------------------------------------------------- Instagram
@pytest.fixture
def ig_env(monkeypatch):
    monkeypatch.setenv("IG_USER_ID", "1789")
    monkeypatch.setenv("IG_ACCESS_TOKEN", "igtok")


def test_instagram_reel_happy_path(settings, brand, files, ig_env):
    statuses = iter(["IN_PROGRESS", "FINISHED"])
    r = (Router()
         .add("POST", "/1789/media_publish", {"id": "M1"})
         .add("POST", "/1789/media", {"id": "C1"})
         .add("GET", "/C1", lambda q: {"status_code": next(statuses)})
         .add("GET", "/M1", {"permalink": "https://www.instagram.com/reel/abc/"}))
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    res = pub.publish(make_req(brand, settings, "instagram", "short", files))
    assert res.remote_id == "M1" and res.url.endswith("/reel/abc/")
    create = form(r.find("POST", "/1789/media")[0])
    assert create["media_type"] == "REELS" and create["share_to_feed"] == "true"
    assert create["video_url"] == "https://cdn.example.com/v.mp4" and create["is_ai_generated"] == "true"
    assert DISCLOSURE in create["caption"] and "cover_url" not in create  # thumbnail is PNG, not JPEG
    assert "/v25.0/" in str(r.calls[0].url)
    assert form(r.find("POST", "media_publish")[0])["creation_id"] == "C1"
    assert len(r.find("GET", "/C1")) == 2


@pytest.mark.parametrize("value, expected", [("SS_PERFORMANCE", "SS_PERFORMANCE"), ("manual", "MANUAL"),
                                             ("1", "SS_PERFORMANCE"), ("", None)])
def test_instagram_trial_reels(settings, brand, files, ig_env, monkeypatch, value, expected):
    import json as _json
    monkeypatch.setenv("IG_TRIAL_REELS", value)
    r = (Router()
         .add("POST", "/1789/media_publish", {"id": "M1"})
         .add("POST", "/1789/media", {"id": "C1"})
         .add("GET", "/C1", {"status_code": "FINISHED"})
         .add("GET", "/M1", {"permalink": "https://www.instagram.com/reel/abc/"}))
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    res = pub.publish(make_req(brand, settings, "instagram", "short", files))
    create = form(r.find("POST", "/1789/media")[0])
    if expected:
        assert _json.loads(create["trial_params"]) == {"graduation_strategy": expected}
    else:
        assert "trial_params" not in create
    assert res.raw["trial_reel"] is bool(expected)


def test_instagram_trial_reels_not_on_carousels_and_bad_value(settings, brand, files, ig_env, monkeypatch):
    monkeypatch.setenv("IG_TRIAL_REELS", "SS_PERFORMANCE")
    ids = iter(["K1", "K2", "K3", "P1"])
    r = (Router()
         .add("POST", "/1789/media_publish", {"id": "M2"})
         .add("POST", "/1789/media", lambda q: {"id": next(ids)})
         .add("GET", "fields=status_code", {"status_code": "FINISHED"})
         .add("GET", "/M2", {"permalink": "https://www.instagram.com/p/x/"}))
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    pub.publish(make_req(brand, settings, "instagram", "carousel", files))
    assert all("trial_params" not in form(c) for c in r.find("POST", "/1789/media"))
    monkeypatch.setenv("IG_TRIAL_REELS", "sometimes")
    with pytest.raises(PublishError):
        InstagramPublisher(settings, transport=Router().transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "instagram", "short", files))


def test_instagram_carousel_children_then_parent(settings, brand, files, ig_env):
    ids = iter(["K1", "K2", "K3", "P1"])
    r = (Router()
         .add("POST", "/1789/media_publish", {"id": "M2"})
         .add("POST", "/1789/media", lambda q: {"id": next(ids)})
         .add("GET", "fields=status_code", {"status_code": "FINISHED"})
         .add("GET", "/M2", {"permalink": "https://www.instagram.com/p/x/"}))
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    res = pub.publish(make_req(brand, settings, "instagram", "carousel", files))
    creates = [form(c) for c in r.find("POST", "/1789/media") if "media_publish" not in str(c.url)]
    assert [c.get("is_carousel_item") for c in creates[:3]] == ["true"] * 3
    assert all("caption" not in c for c in creates[:3])
    assert creates[3]["media_type"] == "CAROUSEL" and creates[3]["children"] == "K1,K2,K3"
    assert res.raw["children"] == ["K1", "K2", "K3"]


def test_instagram_missing_public_url(settings, brand, files, ig_env):
    r = Router()
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    with pytest.raises(PublishError) as e:
        pub.publish(make_req(brand, settings, "instagram", "short", files, public=False))
    assert "PUBLIC_MEDIA_BASE_URL" in str(e.value) and not e.value.retryable and not r.calls


def test_instagram_rejects_png_without_jpeg(settings, brand, files, ig_env):
    pub = InstagramPublisher(settings, transport=Router().transport, sleep=noop_sleep)
    req = make_req(brand, settings, "instagram", "image", files, image_paths=[files["thumb"]])
    with pytest.raises(PublishError, match="JPEG"):
        pub.publish(req)


def test_instagram_error_classification(settings, brand, files, ig_env):
    r = Router().add("POST", "/1789/media", httpx.Response(400, json={"error": {
        "message": "(#10) Application does not have permission", "code": 10, "type": "OAuthException"}}))
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    with pytest.raises(PublishError) as e:
        pub.publish(make_req(brand, settings, "instagram", "short", files))
    assert not e.value.retryable and "does not have permission" in str(e.value)
    assert "igtok" not in str(e.value)

    r2 = Router().add("POST", "/1789/media", httpx.Response(400, json={"error": {
        "message": "Application request limit reached", "code": 4}}))
    pub2 = InstagramPublisher(settings, transport=r2.transport, sleep=noop_sleep)
    with pytest.raises(PublishError) as e2:
        pub2.publish(make_req(brand, settings, "instagram", "short", files))
    assert e2.value.retryable

    r3 = Router().add("POST", "/1789/media", httpx.Response(503, text="down"))
    with pytest.raises(PublishError) as e3:
        InstagramPublisher(settings, transport=r3.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "instagram", "short", files))
    assert e3.value.retryable


def test_instagram_container_error(settings, brand, files, ig_env):
    r = (Router().add("POST", "/1789/media", {"id": "C9"})
         .add("GET", "/C9", {"status_code": "ERROR", "status": "Error: video too long"}))
    pub = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep)
    with pytest.raises(PublishError, match="video too long") as e:
        pub.publish(make_req(brand, settings, "instagram", "short", files))
    assert not e.value.retryable


def test_instagram_metrics_per_metric_fallback(settings, ig_env):
    def insights(q):
        metric = q.url.params["metric"]
        if "," in metric or metric == "ig_reels_video_view_total_time":
            return httpx.Response(400, json={"error": {"message": f"metric {metric} not supported", "code": 100}})
        return {"data": [{"name": metric, "period": "lifetime", "values": [{"value": 7}]}]}
    r = (Router().add("GET", "/M1/insights", insights)
         .add("GET", "/M1", {"media_type": "VIDEO", "media_product_type": "REELS", "like_count": 3}))
    snap = InstagramPublisher(settings, transport=r.transport, sleep=noop_sleep).fetch_metrics("M1")
    assert snap.views == 7 and snap.saves == 7 and snap.reach == 7
    assert "ig_reels_video_view_total_time" in snap.raw["errors"]


# --------------------------------------------------------------------------- YouTube
@pytest.fixture
def yt_env(monkeypatch):
    monkeypatch.setenv("YT_CLIENT_ID", "cid")
    monkeypatch.setenv("YT_CLIENT_SECRET", "csec")
    monkeypatch.setenv("YT_REFRESH_TOKEN", "rtok")


def yt_router(final=None):
    session = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&upload_id=XYZ"
    return (Router()
            .add("POST", "oauth2.googleapis.com/token", {"access_token": "at", "expires_in": 3600})
            .add("POST", "upload/youtube/v3/videos", httpx.Response(200, headers={"Location": session}))
            .add("PUT", "upload_id=XYZ", final or (lambda q: httpx.Response(201, json={"id": "VID1", "status": {"uploadStatus": "uploaded"}})))
            .add("POST", "thumbnails/set", {"items": []})
            .add("GET", "youtube/v3/videos", {"items": [{"statistics": {"viewCount": "120", "likeCount": "9", "commentCount": "2"}}]}))


def test_youtube_long_upload(settings, brand, files, yt_env):
    r = yt_router()
    pub = YouTubePublisher(settings, transport=r.transport, sleep=noop_sleep)
    res = pub.publish(make_req(brand, settings, "youtube", "long", files, realistic_synthetic=True,
                               title="A <bad> title " + "x" * 120))
    assert res.remote_id == "VID1" and res.url == "https://www.youtube.com/watch?v=VID1"
    init = r.find("POST", "upload/youtube/v3/videos")[0]
    assert init.url.params["uploadType"] == "resumable" and init.headers["X-Upload-Content-Length"] == "2048"
    assert init.headers["Authorization"] == "Bearer at"
    meta = body_json(init)
    assert meta["status"] == {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}
    assert len(meta["snippet"]["title"]) <= 100 and "<" not in meta["snippet"]["title"]
    assert meta["snippet"]["tags"] == ["money", "roth ira"]
    put = r.find("PUT", "upload_id=XYZ")[0]
    assert len(put.content) == 2048
    assert r.find("POST", "thumbnails/set")[0].url.params["videoId"] == "VID1" and res.raw["thumbnail"]["ok"]
    assert form(r.find("POST", "oauth2.googleapis.com/token")[0])["grant_type"] == "refresh_token"
    snap = pub.fetch_metrics("VID1")
    assert (snap.views, snap.likes, snap.comments) == (120, 9, 2)


def test_youtube_short_no_thumbnail_and_schedule(settings, brand, files, yt_env):
    r = yt_router()
    pub = YouTubePublisher(settings, transport=r.transport, sleep=noop_sleep)
    res = pub.publish(make_req(brand, settings, "youtube", "short", files, scheduled_at="2026-12-01T17:00:00Z"))
    meta = body_json(r.find("POST", "upload/youtube/v3/videos")[0])
    assert meta["status"]["containsSyntheticMedia"] is False and meta["status"]["publishAt"] == "2026-12-01T17:00:00Z"
    assert res.url.endswith("/shorts/VID1") and not r.find("POST", "thumbnails/set")


def test_youtube_resumes_after_server_error(settings, brand, files, yt_env):
    calls = {"n": 0}

    def put(q):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, json={"error": {"message": "backend error"}})
        if q.headers.get("Content-Range") == "bytes */2048":
            return httpx.Response(308, headers={"Range": "bytes=0-1023"})
        assert q.headers["Content-Range"] == "bytes 1024-2047/2048" and len(q.content) == 1024
        return httpx.Response(201, json={"id": "VID2"})
    r = yt_router(final=put)
    res = YouTubePublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "youtube", "long", files, thumbnail_path=None))
    assert res.remote_id == "VID2"


def test_youtube_quota_error_not_retryable(settings, brand, files, yt_env):
    r = yt_router()
    r.routes.insert(0, ("POST", "upload/youtube/v3/videos", httpx.Response(403, json={"error": {
        "code": 403, "message": "The request cannot be completed because you have exceeded your quota.",
        "errors": [{"reason": "quotaExceeded"}]}})))
    with pytest.raises(PublishError) as e:
        YouTubePublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "youtube", "long", files))
    assert not e.value.retryable and "quotaExceeded" in str(e.value)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_youtube_short_must_be_vertical(settings, brand, files, yt_env, tmp_path):
    wide = tmp_path / "wide.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=320x180:d=1",
                    "-pix_fmt", "yuv420p", str(wide)], check=True)
    r = yt_router()
    with pytest.raises(PublishError, match="vertical"):
        YouTubePublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "youtube", "short", files, video_path=wide))
    assert not r.find("POST", "upload/youtube")


# --------------------------------------------------------------------------- TikTok
@pytest.fixture
def tt_env(monkeypatch):
    monkeypatch.setenv("TIKTOK_ACCESS_TOKEN", "tt")


OK = {"code": "ok", "message": "", "log_id": "L"}
CREATOR = {"data": {"creator_username": "mms", "privacy_level_options": ["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"],
                    "comment_disabled": False, "duet_disabled": True, "stitch_disabled": False,
                    "max_video_post_duration_sec": 600}, "error": OK}


def tt_router(init=None, status=None):
    return (Router()
            .add("POST", "creator_info/query", CREATOR)
            .add("POST", "video/init", init or {"data": {"publish_id": "v_pub_file~1", "upload_url": "https://open-upload.tiktokapis.com/upload?id=1"}, "error": OK})
            .add("PUT", "open-upload.tiktokapis.com", httpx.Response(201))
            .add("POST", "status/fetch", status or {"data": {"status": "PUBLISH_COMPLETE"}, "error": OK}))


def test_tiktok_file_upload_private_by_default(settings, brand, files, tt_env):
    r = tt_router()
    pub = TikTokPublisher(settings, transport=r.transport, sleep=noop_sleep)
    res = pub.publish(make_req(brand, settings, "tiktok", "short", files, public=False, has_paid_promotion=True))
    body = body_json(r.find("POST", "video/init")[0])
    info, src = body["post_info"], body["source_info"]
    assert info["privacy_level"] == "SELF_ONLY" and info["is_aigc"] is True
    assert info["brand_content_toggle"] is True and info["disable_duet"] is True and DISCLOSURE in info["title"]
    assert src == {"source": "FILE_UPLOAD", "video_size": 2048, "chunk_size": 2048, "total_chunk_count": 1}
    put = r.find("PUT", "open-upload")[0]
    assert put.headers["Content-Range"] == "bytes 0-2047/2048" and put.headers["Content-Type"] == "video/mp4"
    assert r.find("POST", "creator_info")[0].headers["Authorization"] == "Bearer tt"
    assert res.remote_id == "v_pub_file~1" and res.url == ""


def test_tiktok_pull_from_url_and_allowed_privacy(settings, brand, files, tt_env, monkeypatch):
    monkeypatch.setenv("TIKTOK_PRIVACY", "public_to_everyone")
    status = {"data": {"status": "PUBLISH_COMPLETE", "publicaly_available_post_id": [7300000000000000001]}, "error": OK}
    r = tt_router(init={"data": {"publish_id": "v_pub_url~2"}, "error": OK}, status=status)
    res = TikTokPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "tiktok", "short", files))
    body = body_json(r.find("POST", "video/init")[0])
    assert body["source_info"] == {"source": "PULL_FROM_URL", "video_url": "https://cdn.example.com/v.mp4"}
    assert body["post_info"]["privacy_level"] == "PUBLIC_TO_EVERYONE"
    assert res.remote_id == "7300000000000000001" and res.url == "https://www.tiktok.com/@mms/video/7300000000000000001"
    assert not r.find("PUT", "open-upload")


def test_tiktok_disallowed_privacy_falls_back(settings, brand, files, tt_env, monkeypatch):
    monkeypatch.setenv("TIKTOK_PRIVACY", "FOLLOWER_OF_CREATOR")
    r = tt_router()
    res = TikTokPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "tiktok", "short", files, public=False))
    assert body_json(r.find("POST", "video/init")[0])["post_info"]["privacy_level"] == "SELF_ONLY"
    assert "not allowed" in res.raw["note"]


def test_tiktok_unverified_domain_falls_back_to_file_upload(settings, brand, files, tt_env):
    def init(q):
        if body_json(q)["source_info"]["source"] == "PULL_FROM_URL":
            return httpx.Response(403, json={"data": {}, "error": {"code": "url_ownership_unverified", "message": "verify", "log_id": "x"}})
        return {"data": {"publish_id": "p3", "upload_url": "https://open-upload.tiktokapis.com/u"}, "error": OK}
    r = tt_router(init=init)
    res = TikTokPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "tiktok", "short", files))
    assert res.raw["source"] == "FILE_UPLOAD" and "pull_fallback" in res.raw


def test_tiktok_errors(settings, brand, files, tt_env):
    r = tt_router(init={"data": {}, "error": {"code": "spam_risk_too_many_posts", "message": "cap", "log_id": "x"}})
    with pytest.raises(PublishError) as e:
        TikTokPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "tiktok", "short", files, public=False))
    assert not e.value.retryable and "spam_risk_too_many_posts" in str(e.value)

    r2 = Router().add("POST", "creator_info/query", httpx.Response(429, json={"error": {"code": "rate_limit_exceeded", "message": "slow"}}))
    with pytest.raises(PublishError) as e2:
        TikTokPublisher(settings, transport=r2.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "tiktok", "short", files))
    assert e2.value.retryable

    r3 = tt_router(status={"data": {"status": "FAILED", "fail_reason": "duration_check_failed"}, "error": OK})
    with pytest.raises(PublishError, match="duration_check_failed") as e3:
        TikTokPublisher(settings, transport=r3.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "tiktok", "short", files, public=False))
    assert not e3.value.retryable


def test_tiktok_chunk_plan():
    mb = 1024 * 1024
    assert chunk_plan(3 * mb) == (3 * mb, 1)
    size = 50_000_123
    cs, n = chunk_plan(size, 10_000_000)
    assert (cs, n) == (10_000_000, 5)
    ranges = chunk_ranges(size, cs, n)
    assert ranges[-1] == (40_000_000, size - 1) and ranges[0] == (0, 9_999_999)
    cs, n = chunk_plan(7 * mb)
    assert n == 1 and cs == 7 * mb


def test_tiktok_metrics(settings, tt_env):
    r = Router().add("POST", "video/query", {"data": {"videos": [{"id": "73", "view_count": 50, "like_count": 4,
                                                                    "comment_count": 1, "share_count": 2}]}, "error": OK})
    pub = TikTokPublisher(settings, transport=r.transport, sleep=noop_sleep)
    snap = pub.fetch_metrics("73")
    q = r.find("POST", "video/query")[0]
    assert "view_count" in q.url.params["fields"] and body_json(q) == {"filters": {"video_ids": ["73"]}}
    assert (snap.views, snap.likes, snap.shares) == (50, 4, 2)
    r2 = Router().add("POST", "status/fetch", {"data": {"status": "PUBLISH_COMPLETE"}, "error": OK})
    snap2 = TikTokPublisher(settings, transport=r2.transport, sleep=noop_sleep).fetch_metrics("v_pub_file~1")
    assert snap2.views == 0 and "no public post id" in snap2.raw["note"]
    r3 = Router().add("POST", "video/query", httpx.Response(401, json={"error": {"code": "scope_not_authorized", "message": "no"}}))
    snap3 = TikTokPublisher(settings, transport=r3.transport, sleep=noop_sleep).fetch_metrics("73")
    assert "video.list" in snap3.raw["note"]


# --------------------------------------------------------------------------- Facebook
@pytest.fixture
def fb_env(monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "PAGE")
    monkeypatch.setenv("FB_PAGE_TOKEN", "ptok")


def test_facebook_reel_local_upload(settings, brand, files, fb_env):
    def reels(q):
        f = form(q)
        if f["upload_phase"] == "start":
            return {"video_id": "RV1", "upload_url": "https://rupload.facebook.com/video-upload/v25.0/RV1"}
        assert f["video_state"] == "PUBLISHED" and f["video_id"] == "RV1" and DISCLOSURE in f["description"]
        return {"success": True}
    r = (Router().add("POST", "/PAGE/video_reels", reels)
         .add("POST", "rupload.facebook.com/video-upload", {"success": True})
         .add("GET", "/RV1", {"status": {"video_status": "ready", "publishing_phase": {"status": "complete"}}}))
    res = FacebookPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "facebook", "short", files, public=False))
    up = r.find("POST", "rupload")[0]
    assert up.headers["Authorization"] == "OAuth ptok" and up.headers["offset"] == "0"
    assert up.headers["file_size"] == "2048" and len(up.content) == 2048
    assert res.remote_id == "RV1" and res.url.endswith("/reel/RV1")


def test_facebook_carousel_multi_photo(settings, brand, files, fb_env):
    ids = iter(["P1", "P2", "P3"])
    r = (Router().add("POST", "/PAGE/photos", lambda q: {"id": next(ids)})
         .add("POST", "/PAGE/feed", {"id": "PAGE_99"})
         .add("GET", "/PAGE_99", {"permalink_url": "https://www.facebook.com/x/posts/99"}))
    res = FacebookPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "facebook", "carousel", files))
    photos = [form(c) for c in r.find("POST", "/PAGE/photos")]
    assert all(p["published"] == "false" and p["url"].startswith("https://cdn.example.com/") for p in photos)
    feed = form(r.find("POST", "/PAGE/feed")[0])
    assert json.loads(feed["attached_media[2]"]) == {"media_fbid": "P3"} and DISCLOSURE in feed["message"]
    assert res.remote_id == "PAGE_99" and res.url.endswith("/posts/99")


def test_facebook_permission_error(settings, brand, files, fb_env):
    r = Router().add("POST", "/PAGE/photos", httpx.Response(403, json={"error": {
        "message": "(#200) Requires pages_manage_posts permission", "code": 200}}))
    with pytest.raises(PublishError) as e:
        FacebookPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "facebook", "image", files))
    assert not e.value.retryable and "pages_manage_posts" in str(e.value)


# --------------------------------------------------------------------------- Threads
@pytest.fixture
def th_env(monkeypatch):
    monkeypatch.setenv("THREADS_USER_ID", "TU")
    monkeypatch.setenv("THREADS_ACCESS_TOKEN", "thtok")


def test_threads_carousel(settings, brand, files, th_env):
    ids = iter(["C1", "C2", "C3", "PARENT"])
    r = (Router().add("POST", "/TU/threads_publish", {"id": "TM1"})
         .add("POST", "/TU/threads", lambda q: {"id": next(ids)})
         .add("GET", "fields=status", {"status": "FINISHED"})
         .add("GET", "/TM1", {"permalink": "https://www.threads.com/@mms/post/x"}))
    res = ThreadsPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "threads", "carousel", files))
    creates = [form(c) for c in r.find("POST", "/TU/threads") if "publish" not in str(c.url)]
    assert all(c["is_carousel_item"] == "true" and "is_made_with_ai" not in c for c in creates[:3])
    assert creates[3]["media_type"] == "CAROUSEL" and creates[3]["is_made_with_ai"] == "true"
    assert len(creates[3]["text"].encode()) <= 500 and DISCLOSURE in creates[3]["text"]
    assert res.remote_id == "TM1" and "graph.threads.com/v1.0" in str(r.calls[0].url)


def test_threads_container_error(settings, brand, files, th_env):
    r = (Router().add("POST", "/TU/threads", {"id": "C1"})
         .add("GET", "/C1", {"status": "ERROR", "error_message": "FAILED_DOWNLOADING_VIDEO"}))
    with pytest.raises(PublishError, match="FAILED_DOWNLOADING_VIDEO"):
        ThreadsPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "threads", "short", files))


# --------------------------------------------------------------------------- Postiz
@pytest.fixture
def pz_env(monkeypatch):
    monkeypatch.setenv("POSTIZ_URL", "https://postiz.example.com/")
    monkeypatch.setenv("POSTIZ_API_KEY", "pzkey")
    monkeypatch.setenv("POSTIZ_INTEGRATION_IDS", json.dumps({"tiktok": "int-tt", "youtube": "int-yt"}))


def test_postiz_upload_and_schedule(settings, brand, files, pz_env):
    r = (Router().add("POST", "/api/public/v1/upload", {"id": "m1", "path": "https://uploads.example.com/v.mp4"})
         .add("POST", "/api/public/v1/posts", [{"postId": "pp1", "integration": "int-tt"}]))
    res = PostizPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
        make_req(brand, settings, "tiktok", "short", files, scheduled_at="2026-12-01T17:00:00Z"))
    post = body_json(r.find("POST", "/posts")[0])
    assert r.find("POST", "/upload")[0].headers["Authorization"] == "pzkey"
    assert post["type"] == "schedule" and post["date"] == "2026-12-01T17:00:00Z" and len(post["posts"]) == 1
    p = post["posts"][0]
    assert p["integration"] == {"id": "int-tt"} and p["value"][0]["image"] == [{"id": "m1", "path": "https://uploads.example.com/v.mp4"}]
    assert p["settings"]["__type"] == "tiktok" and p["settings"]["video_made_with_ai"] is True
    assert p["settings"]["privacy_level"] == "SELF_ONLY"
    assert res.remote_id == "pp1"


def test_postiz_refuses_realistic_synthetic_on_youtube(settings, brand, files, pz_env):
    r = Router().add("POST", "/upload", {"id": "m1", "path": "https://u/x.mp4"})
    with pytest.raises(PublishError, match="containsSyntheticMedia"):
        PostizPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "youtube", "long", files, realistic_synthetic=True, thumbnail_path=None))
    assert not r.find("POST", "/posts")


def test_postiz_comma_ids_and_server_error(settings, brand, files, pz_env, monkeypatch):
    monkeypatch.setenv("POSTIZ_INTEGRATION_IDS", "int-ig")
    r = (Router().add("GET", "/integrations", [{"id": "int-ig", "identifier": "instagram-standalone"}])
         .add("POST", "/upload", {"id": "m1", "path": "https://u/x.jpg"})
         .add("POST", "/posts", httpx.Response(502, text="bad gateway")))
    with pytest.raises(PublishError) as e:
        PostizPublisher(settings, transport=r.transport, sleep=noop_sleep).publish(
            make_req(brand, settings, "instagram", "image", files))
    assert e.value.retryable


# --------------------------------------------------------------------------- oauth helpers
def test_oauth_urls_and_exchanges():
    v, c = oauth.pkce_pair()
    assert 43 <= len(v) <= 128 and "=" not in c
    url = oauth.youtube_auth_url("cid", "http://127.0.0.1:5555/", "st", c)
    q = httpx.URL(url).params
    assert q["access_type"] == "offline" and "youtube.upload" in q["scope"] and "youtube.readonly" in q["scope"]
    _, hexc = oauth.pkce_pair("hex")
    assert len(hexc) == 64
    t = httpx.URL(oauth.tiktok_auth_url("ck", "http://127.0.0.1:8765/callback/", "st", hexc)).params
    assert t["scope"].split(",")[:3] == ["user.info.basic", "video.publish", "video.upload"] and t["code_challenge_method"] == "S256"

    r = (Router().add("POST", "open.tiktokapis.com/v2/oauth/token", {"access_token": "a", "refresh_token": "r", "open_id": "o"})
         .add("GET", "/oauth/access_token", {"access_token": "LL", "expires_in": 5183944})
         .add("GET", "/PAGE?", {"instagram_business_account": {"id": "IG1"}}))
    tok = oauth.tiktok_exchange_code("ck", "cs", "code", "http://127.0.0.1:8765/callback/", "ver", transport=r.transport)
    assert tok["refresh_token"] == "r" and form(r.calls[0])["code_verifier"] == "ver"
    assert oauth.meta_long_lived_user_token("app", "sec", "short", transport=r.transport)["access_token"] == "LL"
    assert r.calls[1].url.params["grant_type"] == "fb_exchange_token"
    assert oauth.meta_find_ig_user_id("PAGE", "ptok", transport=r.transport) == "IG1"


def test_local_callback_server():
    with oauth.LocalCallbackServer(port=0, path="/cb") as srv:
        httpx.Client(trust_env=False).get(srv.redirect_uri + "?code=abc&state=xyz", timeout=5)
        res = srv.wait(5)
    assert res.code == "abc" and res.state == "xyz"
