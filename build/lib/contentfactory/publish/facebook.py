"""Facebook Page publishing via the official Graph API.

Docs used:
- Reels publishing (video_reels start/finish, rupload.facebook.com upload,
  status phases, 3-90s 9:16, 30 API reels per 24h):
  https://developers.facebook.com/documentation/video-api/guides/reels-publishing
  https://developers.facebook.com/docs/graph-api/reference/page/video_reels
- Page videos (source | file_url, title, description):
  https://developers.facebook.com/docs/graph-api/reference/page/videos
  https://developers.facebook.com/documentation/video-api/guides/publishing
- Page photos (url | source, caption, published=false) and multi-photo posts
  via /feed attached_media[n]={"media_fbid": ...}:
  https://developers.facebook.com/docs/graph-api/reference/page/photos
  https://developers.facebook.com/docs/graph-api/reference/page/feed
- Posts guide (permissions): https://developers.facebook.com/documentation/pages-api/posts

Setup / review:
- A Facebook Page you manage (CREATE_CONTENT task) and a Meta app using
  Facebook Login for Business. Permissions: pages_show_list,
  pages_read_engagement, pages_manage_posts (+ read_insights for Page/post
  insights). Use a long-lived Page token (`factory auth meta`: exchange a
  user token, then /me/accounts) as FB_PAGE_TOKEN.
- Your own Page works with the app in Development mode; publishing for other
  people's Pages needs App Review + Business Verification.
- Meta has no API field for an AI label on Page posts; the disclosure lives
  in the caption.
"""
from __future__ import annotations

import json
from pathlib import Path

from ._http import GRAPH_API_VERSION, HttpPublisher, poll, public_url
from .base import MetricsSnapshot, PublishError, PublishRequest, PublishResult

GRAPH = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
GRAPH_VIDEO = f"https://graph-video.facebook.com/{GRAPH_API_VERSION}"
RUPLOAD = f"https://rupload.facebook.com/video-upload/{GRAPH_API_VERSION}"


class FacebookPublisher(HttpPublisher):
    platform = "facebook"
    required_env = ["FB_PAGE_ID", "FB_PAGE_TOKEN"]

    def supports(self, fmt: str) -> bool:
        return fmt in ("short", "long", "image", "carousel")

    @property
    def page(self) -> str:
        return self.settings.env("FB_PAGE_ID")

    @property
    def token(self) -> str:
        return self.settings.env("FB_PAGE_TOKEN")

    def _post(self, endpoint_: str, what: str, files: dict | None = None, **data) -> dict:
        return self.http.json("POST", endpoint_, what=what, data={"access_token": self.token, **data}, files=files)

    def _get(self, path: str, what: str, **params) -> dict:
        return self.http.json("GET", f"{GRAPH}/{path}", what=what, params={"access_token": self.token, **params})

    # ------------------------------------------------------------------ publish
    def publish(self, req: PublishRequest) -> PublishResult:
        self.ensure_credentials()
        self.require_format(req.format)
        if req.format == "short":
            return self._reel(req)
        if req.format == "long":
            return self._video(req)
        if req.format == "image":
            return self._photo(req)
        return self._multi_photo(req)

    def _video_file(self, req: PublishRequest) -> Path:
        if not req.video_path or not Path(req.video_path).exists():
            raise PublishError(f"facebook: video file not found: {req.video_path}", retryable=False)
        return Path(req.video_path)

    def _reel(self, req: PublishRequest) -> PublishResult:
        path = self._video_file(req)
        start = self._post(f"{GRAPH}/{self.page}/video_reels", "reel start", upload_phase="start")
        video_id = start["video_id"]
        headers = {"Authorization": f"OAuth {self.token}"}
        url = public_url(req.public_urls, path)
        if url:
            headers["file_url"] = url
            self.upload_http.request("POST", f"{RUPLOAD}/{video_id}", what="reel upload (hosted)", headers=headers)
        else:
            size = path.stat().st_size
            headers.update({"offset": "0", "file_size": str(size), "Content-Type": "application/octet-stream"})
            self.upload_http.request("POST", f"{RUPLOAD}/{video_id}", what="reel upload",
                                     headers=headers, content=path.read_bytes())
        finish = self._post(f"{GRAPH}/{self.page}/video_reels", "reel finish", upload_phase="finish",
                            video_id=video_id, video_state="PUBLISHED", description=req.caption,
                            title=req.title[:255])
        status = self._wait_video(video_id)
        post_id = finish.get("post_id") or ""
        return PublishResult(remote_id=post_id or video_id, url=f"https://www.facebook.com/reel/{video_id}",
                             raw={"video_id": video_id, "post_id": post_id, "status": status, "kind": "reel"})

    def _wait_video(self, video_id: str) -> dict:
        """Best effort: wait for processing; never fail a finished publish on timeout."""
        def check():
            st = (self._get(video_id, "video status", fields="status").get("status") or {})
            phases = {k: (st.get(k) or {}).get("status") for k in ("uploading_phase", "processing_phase", "publishing_phase")}
            if "error" in phases.values():
                err = (st.get("processing_phase") or {}).get("error") or st
                raise PublishError(f"facebook: video {video_id} processing error: {err}", retryable=False)
            return phases.get("publishing_phase") == "complete" or st.get("video_status") == "ready", st
        try:
            return poll(check, platform=self.platform, what="video processing", sleep=self.sleep,
                        first_wait=self.env_float("FB_POLL_FIRST_SECONDS", 5),
                        max_wait=self.env_float("FB_POLL_MAX_SECONDS", 180))
        except PublishError as e:
            if "gave up waiting" in str(e):
                return {"video_status": "processing"}
            raise

    def _video(self, req: PublishRequest) -> PublishResult:
        path = self._video_file(req)
        data = {"title": req.title, "description": req.caption}
        url = public_url(req.public_urls, path)
        if url:
            body = self._post(f"{GRAPH_VIDEO}/{self.page}/videos", "video upload", file_url=url, **data)
        else:
            with path.open("rb") as fh:
                body = self._post(f"{GRAPH_VIDEO}/{self.page}/videos", "video upload",
                                  files={"source": (path.name, fh, "video/mp4")}, **data)
        vid = body["id"]
        return PublishResult(remote_id=vid, url=f"https://www.facebook.com/{self.page}/videos/{vid}",
                             raw={"video_id": vid, "kind": "video"})

    def _photo_upload(self, req: PublishRequest, path: Path, **extra) -> dict:
        url = public_url(req.public_urls, path)
        if url:
            return self._post(f"{GRAPH}/{self.page}/photos", "photo upload", url=url, **extra)
        if not Path(path).exists():
            raise PublishError(f"facebook: image not found: {path}", retryable=False)
        with Path(path).open("rb") as fh:
            mime = "image/png" if Path(path).suffix.lower() == ".png" else "image/jpeg"
            return self._post(f"{GRAPH}/{self.page}/photos", "photo upload",
                              files={"source": (Path(path).name, fh, mime)}, **extra)

    def _photo(self, req: PublishRequest) -> PublishResult:
        if not req.image_paths:
            raise PublishError("facebook: image post has no image", retryable=False)
        body = self._photo_upload(req, req.image_paths[0], caption=req.caption)
        post_id = body.get("post_id") or body["id"]
        return PublishResult(remote_id=post_id, url=self._permalink(post_id), raw={"photo_id": body["id"], "kind": "photo"})

    def _multi_photo(self, req: PublishRequest) -> PublishResult:
        if len(req.image_paths) < 2:
            raise PublishError("facebook: carousel needs at least 2 images", retryable=False)
        ids = [self._photo_upload(req, p, published="false")["id"] for p in req.image_paths]
        attached = {f"attached_media[{i}]": json.dumps({"media_fbid": pid}) for i, pid in enumerate(ids)}
        body = self._post(f"{GRAPH}/{self.page}/feed", "multi-photo post", message=req.caption, **attached)
        return PublishResult(remote_id=body["id"], url=self._permalink(body["id"]),
                             raw={"photo_ids": ids, "kind": "multi_photo"})

    def _permalink(self, object_id: str) -> str:
        try:
            return self._get(object_id, "permalink", fields="permalink_url").get("permalink_url", "")
        except PublishError:
            return f"https://www.facebook.com/{object_id}"

    # ------------------------------------------------------------------ metrics
    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        """Reactions/comments (and shares on posts) via object fields, plus the
        `post_media_view` insight when available. Failures are recorded in raw."""
        self.ensure_credentials()
        raw: dict = {}
        fields = "reactions.summary(total_count).limit(0),comments.summary(total_count).limit(0)"
        try:
            body = self._get(remote_id, "post fields", fields=fields + ",shares")
        except PublishError as e:
            if e.retryable:
                raise
            body = self._get(remote_id, "object fields", fields=fields)  # videos/photos have no `shares`
        snap = MetricsSnapshot(
            likes=int(((body.get("reactions") or {}).get("summary") or {}).get("total_count", 0)),
            comments=int(((body.get("comments") or {}).get("summary") or {}).get("total_count", 0)),
            shares=int((body.get("shares") or {}).get("count", 0)),
        )
        try:
            ins = self._get(f"{remote_id}/insights", "post insights", metric="post_media_view")
            for item in ins.get("data", []):
                if item.get("name") == "post_media_view" and item.get("values"):
                    snap.views = int(item["values"][0].get("value", 0) or 0)
            raw["insights"] = ins.get("data", [])
        except PublishError as e:
            if e.retryable:
                raise
            raw["insights_error"] = str(e)
        snap.raw = {**raw, "fields": body}
        return snap
