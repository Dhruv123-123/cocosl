"""TikTok Direct Post via the official Content Posting API.

NOT USED BY DEFAULT. TikTok's guidelines don't allow tools that upload to accounts you or your team
manage, so TikTok is post-by-hand (see contentfactory/manual.py, MANUAL_PLATFORMS). This publisher only
runs if you remove tiktok from MANUAL_PLATFORMS, i.e. you operate an audited app other creators use.

Docs used:
- Direct Post reference (video/init, post_info incl. is_aigc,
  brand_content_toggle, brand_organic_toggle; source_info; unaudited clients):
  https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post
- Query creator info (privacy_level_options, *_disabled, max_video_post_duration_sec):
  https://developers.tiktok.com/docs/en/content-posting-api-reference-query-creator-info
- Media transfer guide (chunks 5-64MB, floor count, last chunk absorbs the
  remainder up to 128MB, <5MB uploaded whole, PULL_FROM_URL domain verification):
  https://developers.tiktok.com/docs/en/content-posting-api-media-transfer-guide
- Get post status (publish/status/fetch, publicaly_available_post_id):
  https://developers.tiktok.com/docs/en/content-posting-api-reference-get-video-status
- Display API video query (metrics, scope video.list):
  https://developers.tiktok.com/docs/en/tiktok-api-v2-video-query

Setup / review:
- TikTok developer app with Login Kit + Content Posting API (Direct Post
  enabled). Scopes: user.info.basic, video.publish (+video.upload, and
  video.list for metrics). Get the token with `factory auth tiktok`; access
  tokens last 2h, so keep TIKTOK_REFRESH_TOKEN + TIKTOK_CLIENT_KEY/SECRET and
  refresh before publishing (oauth.tiktok_refresh).
- Until the app passes TikTok's audit, every post is restricted to private
  (SELF_ONLY) viewing and posting to public accounts may be refused with
  `unaudited_client_can_only_post_to_private_accounts`. The audit checks the
  Content Sharing Guidelines UX (show creator nickname, let the user pick
  privacy and interaction settings, disclose branded content, get consent).
- PULL_FROM_URL needs the media domain/URL prefix verified under "URL
  properties" in the developer portal; otherwise we fall back to FILE_UPLOAD.
- Rate limits: init 6/min, creator_info 20/min, status 30/min per token.
"""
from __future__ import annotations

from pathlib import Path

from ._http import HttpPublisher, guess_video_mime, poll, probe_video, public_url
from ._text import disclosures, fit_caption, utf16_len
from .base import MetricsSnapshot, PublishError, PublishRequest, PublishResult

API = "https://open.tiktokapis.com/v2"
TITLE_MAX_UTF16 = 2200
MIN_CHUNK = 5 * 1024 * 1024
DEFAULT_CHUNK = 10 * 1024 * 1024
MAX_CHUNKS = 1000
PRIVACY_LEVELS = ("PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "SELF_ONLY")
# Error codes that are worth retrying later.
_RETRYABLE = {"rate_limit_exceeded", "internal_error", "internal"}


def chunk_plan(size: int, chunk_size: int = DEFAULT_CHUNK) -> tuple[int, int]:
    """(chunk_size, total_chunk_count) per the media transfer guide."""
    if size <= 0:
        raise PublishError("tiktok: video file is empty", retryable=False)
    if size < MIN_CHUNK:
        return size, 1
    chunk_size = max(MIN_CHUNK, min(chunk_size, size))
    count = size // chunk_size
    if count > MAX_CHUNKS:
        chunk_size = -(-size // MAX_CHUNKS)
        count = size // chunk_size
    return chunk_size, count


def chunk_ranges(size: int, chunk_size: int, count: int) -> list[tuple[int, int]]:
    """Inclusive byte ranges; the final chunk takes the remainder."""
    ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(count)]
    ranges[-1] = (ranges[-1][0], size - 1)
    return ranges


class TikTokPublisher(HttpPublisher):
    platform = "tiktok"
    required_env = ["TIKTOK_ACCESS_TOKEN"]

    def supports(self, fmt: str) -> bool:
        return fmt in ("short", "mid", "long")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.settings.env('TIKTOK_ACCESS_TOKEN')}",
                "Content-Type": "application/json; charset=UTF-8"}

    def _call(self, path: str, what: str, body: dict | None = None, params: dict | None = None) -> dict:
        """POST a JSON API call; TikTok signals errors in `error.code` (even on 200)."""
        data = self.http.json("POST", f"{API}/{path}", what=what, headers=self._headers(),
                              json=body or {}, params=params)
        err = data.get("error") or {}
        code = err.get("code", "ok")
        if code != "ok":
            raise PublishError(f"tiktok: {what} failed: {code}: {err.get('message', '')} (log_id={err.get('log_id', '')})",
                               retryable=code in _RETRYABLE)
        return data.get("data") or {}

    # ------------------------------------------------------------------ steps
    def creator_info(self) -> dict:
        return self._call("post/publish/creator_info/query/", "creator_info")

    def choose_privacy(self, options: list[str]) -> tuple[str, str]:
        """Return (privacy_level, note). Default SELF_ONLY; TIKTOK_PRIVACY is
        used only when the creator's account allows it."""
        wanted = (self.settings.env("TIKTOK_PRIVACY") or "").upper()
        if wanted and wanted in options:
            return wanted, ""
        if "SELF_ONLY" not in options:
            raise PublishError(f"tiktok: creator does not allow SELF_ONLY; options are {options}", retryable=False)
        note = f"TIKTOK_PRIVACY={wanted} not allowed for this creator ({options}); used SELF_ONLY" if wanted else ""
        return "SELF_ONLY", note

    def post_info(self, req: PublishRequest, creator: dict, privacy: str) -> dict:
        title = fit_caption(req.caption, TITLE_MAX_UTF16, None,
                            protected=disclosures(req.caption, req.brand.ai_disclosure), length=utf16_len)
        # TODO(verify): TikTok's UX guidelines say branded content can't be
        # posted as SELF_ONLY once the app is audited; we leave that check to
        # the API response rather than guessing the rule here.
        return {
            "title": title,
            "privacy_level": privacy,
            "disable_duet": bool(creator.get("duet_disabled")),
            "disable_stitch": bool(creator.get("stitch_disabled")),
            "disable_comment": bool(creator.get("comment_disabled")),
            "is_aigc": bool(req.ai_generated),
            "brand_content_toggle": bool(req.has_paid_promotion),
            "brand_organic_toggle": self.settings.env("TIKTOK_BRAND_ORGANIC", "0") in ("1", "true", "yes"),
        }

    def _init(self, post_info: dict, source_info: dict) -> dict:
        return self._call("post/publish/video/init/", "video/init",
                          {"post_info": post_info, "source_info": source_info})

    def _upload_chunks(self, upload_url: str, path: Path, chunk_size: int, count: int) -> None:
        size = path.stat().st_size
        mime = guess_video_mime(path)
        with path.open("rb") as fh:
            for first, last in chunk_ranges(size, chunk_size, count):
                fh.seek(first)
                data = fh.read(last - first + 1)
                self.upload_http.request("PUT", upload_url, what=f"upload bytes {first}-{last}", ok=(201, 206),
                                         headers={"Content-Type": mime, "Content-Length": str(len(data)),
                                                  "Content-Range": f"bytes {first}-{last}/{size}"},
                                         content=data)

    def status(self, publish_id: str) -> dict:
        return self._call("post/publish/status/fetch/", "status/fetch", {"publish_id": publish_id})

    # ------------------------------------------------------------------ publish
    def publish(self, req: PublishRequest) -> PublishResult:
        self.ensure_credentials()
        self.require_format(req.format)
        path = Path(req.video_path) if req.video_path else None
        if not path or not path.exists():
            raise PublishError(f"tiktok: video file not found: {req.video_path}", retryable=False)
        creator = self.creator_info()
        probe = probe_video(path)
        max_sec = creator.get("max_video_post_duration_sec")
        if probe and max_sec and probe["duration"] > float(max_sec):
            raise PublishError(f"tiktok: video is {probe['duration']:.0f}s; this creator can post at most {max_sec}s",
                               retryable=False)
        privacy, note = self.choose_privacy(creator.get("privacy_level_options") or [])
        info = self.post_info(req, creator, privacy)
        raw: dict = {"privacy_level": privacy, "is_aigc": info["is_aigc"],
                     "brand_content_toggle": info["brand_content_toggle"],
                     "creator": creator.get("creator_username", "")}
        if note:
            raw["note"] = note

        url = public_url(req.public_urls, path)
        data = None
        if url and self.settings.env("TIKTOK_UPLOAD_MODE", "auto").lower() != "file":
            try:
                data = self._init(info, {"source": "PULL_FROM_URL", "video_url": url})
                raw["source"] = "PULL_FROM_URL"
            except PublishError as e:
                if "url_ownership_unverified" not in str(e):
                    raise
                raw["pull_fallback"] = "domain not verified in TikTok portal; used FILE_UPLOAD"
        if data is None:
            size = path.stat().st_size
            chunk_size, count = chunk_plan(size)
            data = self._init(info, {"source": "FILE_UPLOAD", "video_size": size,
                                     "chunk_size": chunk_size, "total_chunk_count": count})
            if not data.get("upload_url"):
                raise PublishError("tiktok: init returned no upload_url", retryable=True)
            self._upload_chunks(data["upload_url"], path, chunk_size, count)
            raw.update(source="FILE_UPLOAD", chunks=count)
        publish_id = data["publish_id"]
        raw["publish_id"] = publish_id
        final = self._wait(publish_id)
        raw["status"] = final.get("status", "PENDING")
        post_ids = final.get("publicaly_available_post_id") or []
        if post_ids:
            pid = str(post_ids[0])
            user = creator.get("creator_username", "")
            return PublishResult(remote_id=pid, url=f"https://www.tiktok.com/@{user}/video/{pid}" if user else "", raw=raw)
        # Private (SELF_ONLY) or still in moderation: no public id yet.
        return PublishResult(remote_id=publish_id, url="", raw=raw)

    def _wait(self, publish_id: str) -> dict:
        def check():
            st = self.status(publish_id)
            s = st.get("status")
            if s == "FAILED":
                reason = st.get("fail_reason", "")
                raise PublishError(f"tiktok: post failed: {reason}", retryable=reason == "internal")
            return s in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"), st
        try:
            return poll(check, platform=self.platform, what="publish status", sleep=self.sleep,
                        first_wait=self.env_float("TIKTOK_POLL_FIRST_SECONDS", 5), max_interval=30,
                        max_wait=self.env_float("TIKTOK_POLL_MAX_SECONDS", 300))
        except PublishError as e:
            if "gave up waiting" in str(e):
                return {"status": "PROCESSING"}  # upload accepted; TikTok keeps processing
            raise

    # ------------------------------------------------------------------ metrics
    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        self.ensure_credentials()
        video_id = remote_id
        if not remote_id.isdigit():  # a publish_id: see if a public post id exists now
            st = self.status(remote_id)
            ids = st.get("publicaly_available_post_id") or []
            if not ids:
                return MetricsSnapshot(raw={"note": "no public post id (private/SELF_ONLY or in moderation)",
                                            "status": st.get("status")})
            video_id = str(ids[0])
        try:
            data = self._call("video/query/", "video/query", {"filters": {"video_ids": [video_id]}},
                              params={"fields": "id,view_count,like_count,comment_count,share_count,share_url"})
        except PublishError as e:
            if e.retryable:
                raise
            return MetricsSnapshot(raw={"note": "video.query unavailable (needs video.list scope)", "error": str(e)})
        videos = data.get("videos") or []
        if not videos:
            return MetricsSnapshot(raw={"note": "video not returned", "video_id": video_id})
        v = videos[0]
        return MetricsSnapshot(views=int(v.get("view_count", 0)), likes=int(v.get("like_count", 0)),
                               comments=int(v.get("comment_count", 0)), shares=int(v.get("share_count", 0)),
                               raw={"video": v})
