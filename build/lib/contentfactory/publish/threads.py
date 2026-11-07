"""Threads publishing via the official Threads API.

Docs used:
- Posts (containers: media_type IMAGE/VIDEO/CAROUSEL, image_url, video_url,
  is_carousel_item, children 2-20, text <=500, is_made_with_ai, threads_publish):
  https://developers.facebook.com/documentation/threads/posts
- Container status (status, error_message) and publishing limits:
  https://developers.facebook.com/documentation/threads/troubleshooting
- Insights (views, likes, replies, reposts, quotes, shares):
  https://developers.facebook.com/documentation/threads/insights
- Long-lived tokens: https://developers.facebook.com/documentation/threads/get-started/long-lived-tokens

Setup / review:
- A Meta app with the Threads use case. Permissions: threads_basic,
  threads_content_publish (+ threads_manage_insights for metrics).
- Without Advanced Access (App Review) you can only post for users added as
  Threads testers on the app; your own account as tester is enough here.
- Media must be at public URLs (set PUBLIC_MEDIA_BASE_URL).
- Long-lived tokens last ~60 days; refresh with oauth.threads_refresh_token.
"""
from __future__ import annotations

from pathlib import Path

from ._http import THREADS_API_VERSION, HttpPublisher, poll, public_url
from ._text import disclosures, fit_caption, utf8_len
from .base import MetricsSnapshot, PublishError, PublishRequest, PublishResult

BASE = f"https://graph.threads.com/{THREADS_API_VERSION}"
TEXT_MAX = 500
CAROUSEL_MIN, CAROUSEL_MAX = 2, 20
METRICS = ["views", "likes", "replies", "reposts", "quotes", "shares"]


class ThreadsPublisher(HttpPublisher):
    platform = "threads"
    required_env = ["THREADS_USER_ID", "THREADS_ACCESS_TOKEN"]

    def supports(self, fmt: str) -> bool:
        return fmt in ("short", "long", "image", "carousel")

    def _post(self, path: str, what: str, **data) -> dict:
        return self.http.json("POST", f"{BASE}/{path}", what=what,
                              data={"access_token": self.settings.env("THREADS_ACCESS_TOKEN"), **data})

    def _get(self, path: str, what: str, **params) -> dict:
        return self.http.json("GET", f"{BASE}/{path}", what=what,
                              params={"access_token": self.settings.env("THREADS_ACCESS_TOKEN"), **params})

    def _url(self, req: PublishRequest, path) -> str:
        url = public_url(req.public_urls, path)
        if not url:
            raise PublishError(f"threads: no public HTTPS URL for {Path(str(path)).name}; set PUBLIC_MEDIA_BASE_URL "
                               "so Threads can fetch the media.", retryable=False)
        return url

    def text(self, req: PublishRequest) -> str:
        # Threads counts emoji by UTF-8 bytes, so measure in bytes to be safe.
        return fit_caption(req.caption, TEXT_MAX, None,
                           protected=disclosures(req.caption, req.brand.ai_disclosure), length=utf8_len)

    def wait(self, container: str) -> None:
        def check():
            body = self._get(container, "container status", fields="status,error_message")
            s = body.get("status")
            if s in ("FINISHED", "PUBLISHED"):
                return True, s
            if s in ("ERROR", "EXPIRED"):
                raise PublishError(f"threads: container {s}: {body.get('error_message', '')}",
                                   retryable=s == "EXPIRED")
            return False, s
        poll(check, platform=self.platform, what=f"container {container}", sleep=self.sleep,
             first_wait=self.env_float("THREADS_POLL_FIRST_SECONDS", 10), max_interval=60,
             max_wait=self.env_float("THREADS_POLL_MAX_SECONDS", 300))

    def publish(self, req: PublishRequest) -> PublishResult:
        self.ensure_credentials()
        self.require_format(req.format)
        user = self.settings.env("THREADS_USER_ID")
        text = self.text(req)
        ai = {"is_made_with_ai": "true"} if req.ai_generated else {}
        children: list[str] = []
        if req.format in ("short", "long"):
            container = self._post(f"{user}/threads", "create video container", media_type="VIDEO",
                                   video_url=self._url(req, req.video_path), text=text, **ai)["id"]
        elif req.format == "image":
            if not req.image_paths:
                raise PublishError("threads: image post has no image", retryable=False)
            container = self._post(f"{user}/threads", "create image container", media_type="IMAGE",
                                   image_url=self._url(req, req.image_paths[0]), text=text, **ai)["id"]
        else:
            images = req.image_paths[:CAROUSEL_MAX]
            if len(images) < CAROUSEL_MIN:
                raise PublishError(f"threads: carousel needs {CAROUSEL_MIN}-{CAROUSEL_MAX} images", retryable=False)
            urls = [self._url(req, p) for p in images]
            for u in urls:  # AI flag goes on the parent only (children reject it)
                children.append(self._post(f"{user}/threads", "create carousel item", media_type="IMAGE",
                                           image_url=u, is_carousel_item="true")["id"])
            for c in children:
                self.wait(c)
            container = self._post(f"{user}/threads", "create carousel container", media_type="CAROUSEL",
                                   children=",".join(children), text=text, **ai)["id"]
        self.wait(container)
        media_id = self._post(f"{user}/threads_publish", "threads_publish", creation_id=container)["id"]
        try:
            permalink = self._get(media_id, "permalink", fields="permalink").get("permalink", "")
        except PublishError:
            permalink = ""
        return PublishResult(remote_id=media_id, url=permalink,
                             raw={"container_id": container, "children": children, "is_made_with_ai": bool(ai)})

    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        self.ensure_credentials()
        values, errors = {}, {}
        try:
            body = self._get(f"{remote_id}/insights", "insights", metric=",".join(METRICS))
            values = _parse(body)
        except PublishError as e:
            if e.retryable:
                raise
            for m in METRICS:
                try:
                    values.update(_parse(self._get(f"{remote_id}/insights", f"insight {m}", metric=m)))
                except PublishError as e2:
                    if e2.retryable:
                        raise
                    errors[m] = str(e2)
        return MetricsSnapshot(views=int(values.get("views", 0)), likes=int(values.get("likes", 0)),
                               comments=int(values.get("replies", 0)),
                               shares=int(values.get("reposts", 0)) + int(values.get("shares", 0)),
                               raw={"insights": values, "errors": errors})


def _parse(body: dict) -> dict:
    out = {}
    for item in body.get("data", []):
        if item.get("values"):
            out[item["name"]] = item["values"][0].get("value", 0)
        elif isinstance(item.get("total_value"), dict):
            out[item["name"]] = item["total_value"].get("value", 0)
    return out
