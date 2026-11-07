"""YouTube uploads via the official YouTube Data API v3.

Docs used:
- videos.insert (scopes, status.containsSyntheticMedia, publishAt, unverified projects):
  https://developers.google.com/youtube/v3/docs/videos/insert
- Video resource limits (title <=100 chars, description <=5000 bytes, no < >,
  tags <=500 chars, publishAt only with privacyStatus=private):
  https://developers.google.com/youtube/v3/docs/videos
- Resumable upload protocol (Location session URI, 308 + Range, resume):
  https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol
- thumbnails.set (<=50MB JPEG/PNG; Shorts only after processing):
  https://developers.google.com/youtube/v3/docs/thumbnails/set
- containsSyntheticMedia / unverified-project changes: https://developers.google.com/youtube/v3/revision_history
- Token refresh: https://developers.google.com/identity/protocols/oauth2/native-app

Setup / review:
- Google Cloud project with "YouTube Data API v3" enabled, an OAuth consent
  screen, and an OAuth client of type "Desktop app" (YT_CLIENT_ID/SECRET).
- Scopes: youtube.upload (publish) + youtube.readonly (metrics). Run
  `factory auth youtube` once to get YT_REFRESH_TOKEN.
- While the consent screen is in "Testing", refresh tokens expire after 7
  days; publish the consent screen (sensitive scopes => Google verification)
  for a long-lived token.
- Quota: uploads use the separate video-upload bucket (default ~100/day);
  thumbnails.set ~50 units. Custom thumbnails need a verified channel.
- Default privacy is "private" (YT_PRIVACY) so a human flips it public.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from ._http import HttpPublisher, guess_video_mime, probe_video
from ._text import clean_youtube_text, disclosures, fit_caption, utf8_len
from .base import MetricsSnapshot, PublishError, PublishRequest, PublishResult
from .oauth import youtube_refresh

API = "https://www.googleapis.com/youtube/v3"
UPLOAD_API = "https://www.googleapis.com/upload/youtube/v3"
TITLE_MAX = 100
DESCRIPTION_MAX_BYTES = 5000
TAGS_MAX_CHARS = 500
CHUNK = 8 * 1024 * 1024
PRIVACY = ("private", "unlisted", "public")


def fit_tags(tags: list[str], limit: int = TAGS_MAX_CHARS) -> list[str]:
    """Keep tags in order while the YouTube 500-char budget allows (commas
    count; tags with spaces count as quoted)."""
    out, used = [], 0
    for raw in tags:
        tag = clean_youtube_text(raw.lstrip("#").strip())
        if not tag:
            continue
        cost = len(tag) + (2 if " " in tag else 0) + (1 if out else 0)
        if used + cost > limit:
            break
        out.append(tag)
        used += cost
    return out


class YouTubePublisher(HttpPublisher):
    platform = "youtube"
    required_env = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
    _token: str = ""
    _token_expiry: float = 0.0

    def supports(self, fmt: str) -> bool:
        return fmt in ("short", "long")

    # ------------------------------------------------------------------ auth
    def access_token(self) -> str:
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        env = self.settings.env
        body = youtube_refresh(env("YT_CLIENT_ID"), env("YT_CLIENT_SECRET"), env("YT_REFRESH_TOKEN"),
                               client=self.http)
        if not body.get("access_token"):
            raise PublishError("youtube: token refresh returned no access_token", retryable=False)
        self._token = body["access_token"]
        self._token_expiry = time.time() + float(body.get("expires_in", 3600))
        return self._token

    def _auth(self, **extra) -> dict:
        return {"Authorization": f"Bearer {self.access_token()}", **extra}

    # ------------------------------------------------------------------ build
    def video_resource(self, req: PublishRequest) -> dict:
        first_line = req.caption.strip().splitlines()[0] if req.caption.strip() else ""
        title = clean_youtube_text((req.title or first_line or "Untitled").strip())
        if len(title) > TITLE_MAX:
            title = title[: TITLE_MAX - 1].rstrip() + "…"
        desc_src = clean_youtube_text(req.description or req.caption)
        description = fit_caption(desc_src, DESCRIPTION_MAX_BYTES, None,
                                  protected=disclosures(desc_src, clean_youtube_text(req.brand.ai_disclosure)),
                                  length=utf8_len)
        privacy = (self.settings.env("YT_PRIVACY", "private") or "private").lower()
        if privacy not in PRIVACY:
            raise PublishError(f"youtube: YT_PRIVACY must be one of {PRIVACY}", retryable=False)
        status = {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": bool(req.realistic_synthetic),
        }
        if req.scheduled_at:
            if privacy != "private":
                raise PublishError("youtube: publishAt requires YT_PRIVACY=private", retryable=False)
            status["publishAt"] = req.scheduled_at
        snippet = {"title": title, "description": description, "tags": fit_tags(req.tags),
                   "categoryId": self.settings.env("YT_CATEGORY_ID", "22")}
        if req.brand.language:
            snippet["defaultLanguage"] = req.brand.language
            snippet["defaultAudioLanguage"] = req.brand.language
        return {"snippet": snippet, "status": status}

    def check_video(self, req: PublishRequest) -> dict | None:
        if not req.video_path or not Path(req.video_path).exists():
            raise PublishError(f"youtube: video file not found: {req.video_path}", retryable=False)
        info = probe_video(req.video_path)
        if req.format == "short" and info and info["width"] > info["height"]:
            raise PublishError(f"youtube: Shorts must be vertical or square, got {info['width']}x{info['height']}",
                               retryable=False)
        return info

    # ------------------------------------------------------------------ publish
    def publish(self, req: PublishRequest) -> PublishResult:
        self.ensure_credentials()
        self.require_format(req.format)
        probe = self.check_video(req)
        resource = self.video_resource(req)
        path = Path(req.video_path)
        video = self._resumable_upload(path, resource)
        video_id = video.get("id")
        if not video_id:
            raise PublishError("youtube: upload finished but no video id returned", retryable=False)
        raw = {"privacy": resource["status"]["privacyStatus"],
               "containsSyntheticMedia": resource["status"]["containsSyntheticMedia"],
               "probe": probe, "upload_status": (video.get("status") or {}).get("uploadStatus")}
        if req.format == "long" and req.thumbnail_path:
            raw["thumbnail"] = self._set_thumbnail(video_id, Path(req.thumbnail_path))
        url = f"https://www.youtube.com/shorts/{video_id}" if req.format == "short" \
            else f"https://www.youtube.com/watch?v={video_id}"
        return PublishResult(remote_id=video_id, url=url, raw=raw)

    def _resumable_upload(self, path: Path, resource: dict) -> dict:
        total = path.stat().st_size
        mime = guess_video_mime(path)
        init = self.http.request(
            "POST", f"{UPLOAD_API}/videos", what="start resumable upload",
            params={"uploadType": "resumable", "part": "snippet,status"},
            headers=self._auth(**{"Content-Type": "application/json; charset=UTF-8",
                                  "X-Upload-Content-Length": str(total), "X-Upload-Content-Type": mime}),
            content=json.dumps(resource).encode())
        session = init.headers.get("Location")
        if not session:
            raise PublishError("youtube: no upload session URI (Location header) returned", retryable=True)
        start, attempts = 0, int(self.env_float("YT_UPLOAD_RETRIES", 3))
        for attempt in range(attempts + 1):
            try:
                return self._put_from(session, path, start, total, mime)
            except PublishError as e:
                if not e.retryable or attempt == attempts:
                    raise
                self.sleep(min(2 ** attempt, 30))
                start = self._uploaded_bytes(session, total)
                if start is None:  # already complete
                    return self._status_body
        raise PublishError("youtube: upload failed", retryable=True)  # pragma: no cover

    def _put_from(self, session: str, path: Path, start: int, total: int, mime: str) -> dict:
        def body():
            with path.open("rb") as fh:
                fh.seek(start)
                while chunk := fh.read(CHUNK):
                    yield chunk
        headers = self._auth(**{"Content-Type": mime, "Content-Length": str(total - start)})
        if start:
            headers["Content-Range"] = f"bytes {start}-{total - 1}/{total}"
        resp = self.upload_http.request("PUT", session, what="upload video bytes", headers=headers, content=body())
        return resp.json()

    def _uploaded_bytes(self, session: str, total: int) -> int | None:
        """Ask the session how much arrived. None means the upload completed."""
        resp = self.http.request("PUT", session, what="upload status", ok=(308,),
                                 headers=self._auth(**{"Content-Length": "0", "Content-Range": f"bytes */{total}"}))
        if resp.status_code in (200, 201):
            self._status_body = resp.json()
            return None
        rng = resp.headers.get("Range", "")
        return int(rng.rsplit("-", 1)[-1]) + 1 if rng else 0

    def _set_thumbnail(self, video_id: str, thumb: Path) -> dict:
        """Best effort: a failed thumbnail must not fail a finished upload."""
        if not thumb.exists():
            return {"ok": False, "error": "thumbnail file missing"}
        mime = "image/png" if thumb.suffix.lower() == ".png" else "image/jpeg"
        try:
            self.http.request("POST", f"{UPLOAD_API}/thumbnails/set", what="thumbnails.set",
                              params={"videoId": video_id, "uploadType": "media"},
                              headers=self._auth(**{"Content-Type": mime}), content=thumb.read_bytes())
            return {"ok": True}
        except PublishError as e:
            return {"ok": False, "error": str(e)}

    # ------------------------------------------------------------------ metrics
    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        self.ensure_credentials()
        body = self.http.json("GET", f"{API}/videos", what="videos.list",
                              params={"part": "statistics", "id": remote_id}, headers=self._auth())
        items = body.get("items") or []
        if not items:
            return MetricsSnapshot(raw={"note": "video not found or not visible to this account"})
        stats = items[0].get("statistics", {})
        return MetricsSnapshot(views=int(stats.get("viewCount", 0)), likes=int(stats.get("likeCount", 0)),
                               comments=int(stats.get("commentCount", 0)), raw={"statistics": stats})
