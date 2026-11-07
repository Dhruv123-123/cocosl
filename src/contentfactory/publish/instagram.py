"""Instagram publishing via the official Instagram Graph API (content publishing).

Docs used:
- Content publishing (containers, media_publish, status_code polling, limits):
  https://developers.facebook.com/docs/instagram-platform/content-publishing
- IG User media params (media_type, share_to_feed, cover_url, is_carousel_item,
  children <=10, caption <=2200 chars / 30 hashtags, is_ai_generated):
  https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media
- Media insights (views, reach, likes, comments, shares, saved, total_interactions,
  ig_reels_avg_watch_time, ...; `impressions` deprecated for media after 2024-07-02):
  https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media/insights

Setup / review:
- Instagram professional (Business or Creator) account. With Facebook Login
  (default host graph.facebook.com) it must be linked to a Facebook Page; use a
  Page/user token with `instagram_basic`, `instagram_content_publish`,
  `pages_read_engagement`, `instagram_manage_insights` (+`pages_show_list`).
  With Instagram Login set IG_API_HOST=graph.instagram.com and use
  `instagram_business_basic`, `instagram_business_content_publish`,
  `instagram_business_manage_insights`.
- Posting to accounts you own works in Development mode with the account
  added as an app role; anything else needs Meta App Review (Advanced Access)
  and Business Verification.
- Limits: 100 API-published posts per rolling 24h (carousel = 1).
- Media must be reachable at public HTTPS URLs when the container is created
  (Meta fetches them). Images must be JPEG. Set PUBLIC_MEDIA_BASE_URL.
"""
from __future__ import annotations

from pathlib import Path

from ._http import GRAPH_API_VERSION, HttpPublisher, public_url
from ._text import disclosures, fit_caption
from .base import MetricsSnapshot, PublishError, PublishRequest, PublishResult
from .oauth import instagram_login_refresh_token, meta_long_lived_user_token  # noqa: F401 (re-export)

CAPTION_MAX = 2200
HASHTAG_MAX = 30
CAROUSEL_MIN, CAROUSEL_MAX = 2, 10
REEL_METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions",
                "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
FEED_METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions",
                "follows", "profile_visits"]


def refresh_long_lived_token(token: str, app_id: str = "", app_secret: str = "", transport=None) -> dict:
    """Extend an IG_ACCESS_TOKEN.

    Facebook Login tokens: pass app_id/app_secret (fb_exchange_token).
    Instagram Login tokens: no app credentials needed (ig_refresh_token).
    Returns {access_token, token_type, expires_in}; never printed.
    """
    if app_id and app_secret:
        return meta_long_lived_user_token(app_id, app_secret, token, transport=transport)
    return instagram_login_refresh_token(token, transport=transport)


def _jpeg_url(urls: dict[str, str], path: Path) -> str | None:
    """Public URL of a JPEG version of `path` (Instagram accepts JPEG only)."""
    path = Path(path)
    for cand in (path, path.with_suffix(".jpg"), path.with_suffix(".jpeg")):
        if cand.suffix.lower() in (".jpg", ".jpeg") and (u := urls.get(str(cand))):
            return u
    png_url = urls.get(str(path))
    for suffix in (".jpg", ".jpeg"):
        sibling = path.with_suffix(suffix)
        if png_url and sibling.exists() and png_url.endswith(path.name):
            return png_url[: -len(path.name)] + sibling.name
    return None


class InstagramPublisher(HttpPublisher):
    platform = "instagram"
    required_env = ["IG_USER_ID", "IG_ACCESS_TOKEN"]

    def supports(self, fmt: str) -> bool:
        return fmt in ("short", "carousel", "image")

    # ------------------------------------------------------------------ helpers
    @property
    def base(self) -> str:
        host = self.settings.env("IG_API_HOST", "graph.facebook.com")
        return f"https://{host}/{GRAPH_API_VERSION}"

    def _params(self, **extra) -> dict:
        return {"access_token": self.settings.env("IG_ACCESS_TOKEN"), **extra}

    def _post(self, path: str, what: str, **data) -> dict:
        return self.http.json("POST", f"{self.base}/{path}", what=what, data=self._params(**data))

    def _get(self, path: str, what: str, **params) -> dict:
        return self.http.json("GET", f"{self.base}/{path}", what=what, params=self._params(**params))

    def _ai_flag(self, req: PublishRequest) -> dict:
        if req.ai_generated and self.settings.env("IG_SEND_AI_LABEL", "1") not in ("0", "false", "no"):
            return {"is_ai_generated": "true"}
        return {}

    def _need_url(self, req: PublishRequest, path: Path | None, kind: str) -> str:
        if path is None:
            raise PublishError(f"instagram: no {kind} file to publish", retryable=False)
        url = _jpeg_url(req.public_urls, path) if kind == "image" else public_url(req.public_urls, path)
        if url:
            return url
        if kind == "image" and public_url(req.public_urls, path):
            raise PublishError(f"instagram: {Path(path).name} is not JPEG; Instagram only accepts JPEG images. "
                               "Export a .jpg next to it and publish that.", retryable=False)
        raise PublishError(
            f"instagram: no public HTTPS URL for {Path(path).name}. Instagram fetches media from a public URL: "
            "set PUBLIC_MEDIA_BASE_URL to where the output/ folder is served over HTTPS (e.g. a bucket or CDN) "
            "and sync rendered files there before publishing.", retryable=False)

    def caption(self, req: PublishRequest) -> str:
        return fit_caption(req.caption, CAPTION_MAX, HASHTAG_MAX,
                           protected=disclosures(req.caption, req.brand.ai_disclosure))

    def wait_container(self, container_id: str) -> None:
        def check():
            body = self._get(container_id, "container status", fields="status_code,status")
            code = body.get("status_code")
            if code in ("FINISHED", "PUBLISHED"):
                return True, code
            if code in ("ERROR", "EXPIRED"):
                raise PublishError(f"instagram: container {container_id} {code}: {body.get('status', '')}",
                                   retryable=code == "EXPIRED")
            return False, code
        from ._http import poll
        poll(check, platform=self.platform, what=f"container {container_id}", sleep=self.sleep,
             first_wait=self.env_float("IG_POLL_FIRST_SECONDS", 5), max_interval=60,
             max_wait=self.env_float("IG_POLL_MAX_SECONDS", 300))

    # ------------------------------------------------------------------ publish
    def publish(self, req: PublishRequest) -> PublishResult:
        self.ensure_credentials()
        self.require_format(req.format)
        user = self.settings.env("IG_USER_ID")
        caption = self.caption(req)
        children: list[str] = []
        if req.format == "short":
            payload = {"media_type": "REELS", "video_url": self._need_url(req, req.video_path, "video"),
                       "caption": caption, "share_to_feed": "true", **self._ai_flag(req)}
            if req.thumbnail_path and (cover := _jpeg_url(req.public_urls, req.thumbnail_path)):
                payload["cover_url"] = cover
            container = self._post(f"{user}/media", "create reel container", **payload)["id"]
        elif req.format == "image":
            if not req.image_paths:
                raise PublishError("instagram: image post has no image", retryable=False)
            container = self._post(f"{user}/media", "create image container",
                                   image_url=self._need_url(req, req.image_paths[0], "image"),
                                   caption=caption, **self._ai_flag(req))["id"]
        else:  # carousel
            images = req.image_paths[:CAROUSEL_MAX]
            if len(images) < CAROUSEL_MIN:
                raise PublishError(f"instagram: carousel needs {CAROUSEL_MIN}-{CAROUSEL_MAX} images, got {len(images)}",
                                   retryable=False)
            urls = [self._need_url(req, p, "image") for p in images]  # validate all before any API call
            for url in urls:
                children.append(self._post(f"{user}/media", "create carousel item",
                                           image_url=url, is_carousel_item="true")["id"])
            for child in children:
                self.wait_container(child)
            container = self._post(f"{user}/media", "create carousel container", media_type="CAROUSEL",
                                   children=",".join(children), caption=caption, **self._ai_flag(req))["id"]
        self.wait_container(container)
        media_id = self._post(f"{user}/media_publish", "media_publish", creation_id=container)["id"]
        permalink = ""
        try:
            permalink = self._get(media_id, "permalink", fields="permalink").get("permalink", "")
        except PublishError:
            pass  # published fine; link can be looked up later
        return PublishResult(remote_id=media_id, url=permalink, raw={
            "container_id": container, "children": children, "format": req.format,
            "caption_chars": len(caption), "graph_version": GRAPH_API_VERSION,
            "trimmed_caption": caption != req.caption.strip()})

    # ------------------------------------------------------------------ metrics
    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        self.ensure_credentials()
        info = self._get(remote_id, "media info",
                         fields="media_type,media_product_type,like_count,comments_count,permalink")
        is_reel = info.get("media_product_type") == "REELS" or info.get("media_type") == "VIDEO"
        metrics = REEL_METRICS if is_reel else FEED_METRICS
        values, errors = self._insights(remote_id, metrics)
        snap = MetricsSnapshot(
            views=int(values.get("views", 0)),
            reach=int(values.get("reach", 0)),
            likes=int(values.get("likes", info.get("like_count", 0) or 0)),
            comments=int(values.get("comments", info.get("comments_count", 0) or 0)),
            shares=int(values.get("shares", 0)),
            saves=int(values.get("saved", 0)),
            follows=int(values.get("follows", 0)),
            raw={"insights": values, "errors": errors, "media": info},
        )
        # Meta reports Reels watch-time metrics in milliseconds.
        if "ig_reels_video_view_total_time" in values:
            snap.watch_seconds = float(values["ig_reels_video_view_total_time"]) / 1000.0
        return snap

    def _insights(self, media_id: str, metrics: list[str]) -> tuple[dict, dict]:
        """Fetch all metrics in one call; if Meta rejects the set, retry one by
        one so a single unsupported metric doesn't lose the rest."""
        try:
            return self._parse(self._get(f"{media_id}/insights", "insights", metric=",".join(metrics))), {}
        except PublishError as e:
            if e.retryable:
                raise
        values, errors = {}, {}
        for m in metrics:
            try:
                values.update(self._parse(self._get(f"{media_id}/insights", f"insight {m}", metric=m)))
            except PublishError as e:
                if e.retryable:
                    raise
                errors[m] = str(e)
        return values, errors

    @staticmethod
    def _parse(body: dict) -> dict:
        out = {}
        for item in body.get("data", []):
            name = item.get("name")
            if "total_value" in item and isinstance(item["total_value"], dict):
                out[name] = item["total_value"].get("value", 0)
            elif item.get("values"):
                out[name] = item["values"][0].get("value", 0)
        return out
