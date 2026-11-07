"""Delegate posting/scheduling to a (self-hosted) Postiz instance via its public API.

Postiz itself talks to the platforms through their official APIs; this adapter
only uploads our media to Postiz and creates the post there.

Docs used:
- Public API intro (base URLs, `Authorization: <api key>`, create-post rate limit):
  https://docs.postiz.com/public-api/introduction.md
- Upload: https://docs.postiz.com/public-api/uploads/upload-file.md
- Create post: https://docs.postiz.com/public-api/posts/create.md
- Integrations: https://docs.postiz.com/public-api/integrations/list.md
- Provider settings: https://docs.postiz.com/public-api/providers/{youtube,tiktok,instagram,facebook,threads}.md

Setup:
- Run Postiz (or use Postiz cloud), connect each channel in its UI (Postiz
  needs its own platform app credentials/review), then create an API key in
  Settings -> Public API.
- POSTIZ_URL: e.g. https://postiz.example.com (we append /api/public/v1) or a
  full base ending in /public/v1 (cloud: https://api.postiz.com/public/v1).
- POSTIZ_INTEGRATION_IDS: either a JSON map {"instagram": "id", ...} or a comma
  list of integration ids (their platform is looked up via /integrations).
- Limits: create-post is limited to ~90/h self-hosted (API_LIMIT), 100/h cloud.

Compliance notes: Postiz's YouTube settings have no containsSyntheticMedia
field, so realistic synthetic videos are refused for YouTube here (publish
those with the direct YouTube adapter). TikTok uses DIRECT_POST with
video_made_with_ai and the brand-content toggles.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ._text import disclosures, fit_caption
from ._http import HttpPublisher
from .base import MetricsSnapshot, PublishError, PublishRequest, PublishResult

ALIASES = {"instagram-standalone": "instagram", "youtube": "youtube", "tiktok": "tiktok",
           "facebook": "facebook", "threads": "threads", "instagram": "instagram"}


class PostizPublisher(HttpPublisher):
    platform = "postiz"
    required_env = ["POSTIZ_URL", "POSTIZ_API_KEY", "POSTIZ_INTEGRATION_IDS"]

    @property
    def base(self) -> str:
        url = self.settings.env("POSTIZ_URL").rstrip("/")
        return url if url.endswith("/public/v1") else f"{url}/api/public/v1"

    def _headers(self) -> dict:
        return {"Authorization": self.settings.env("POSTIZ_API_KEY")}

    # ------------------------------------------------------------------ targets
    def integrations(self) -> list[dict]:
        body = self.http.request("GET", f"{self.base}/integrations", what="list integrations",
                                 headers=self._headers()).json()
        return body if isinstance(body, list) else body.get("integrations", [])

    def targets(self, platform: str) -> list[tuple[str, str]]:
        """[(identifier, integration_id)] for this request. A request for a
        specific platform only goes to that platform's integration."""
        raw = self.settings.env("POSTIZ_INTEGRATION_IDS").strip()
        pairs: list[tuple[str, str]]
        if raw.startswith("{"):
            try:
                pairs = [(k, str(v)) for k, v in json.loads(raw).items()]
            except ValueError:
                raise PublishError("postiz: POSTIZ_INTEGRATION_IDS is not valid JSON", retryable=False) from None
        else:
            ids = [x.strip() for x in raw.split(",") if x.strip()]
            known = {i.get("id"): i.get("identifier", "") for i in self.integrations()}
            missing = [i for i in ids if i not in known]
            if missing:
                raise PublishError(f"postiz: unknown integration ids {missing}", retryable=False)
            pairs = [(known[i], i) for i in ids]
        if platform != "postiz":
            pairs = [(k, v) for k, v in pairs if ALIASES.get(k, k) == platform]
            if not pairs:
                raise PublishError(f"postiz: no integration configured for {platform}", retryable=False)
        return pairs

    # ------------------------------------------------------------------ media
    def upload(self, path: Path) -> dict:
        path = Path(path)
        if not path.exists():
            raise PublishError(f"postiz: file not found: {path}", retryable=False)
        with path.open("rb") as fh:
            body = self.upload_http.request("POST", f"{self.base}/upload", what="upload",
                                            headers=self._headers(), files={"file": (path.name, fh)}).json()
        if not body.get("id") or not body.get("path"):
            raise PublishError("postiz: upload returned no id/path", retryable=True)
        return {"id": body["id"], "path": body["path"]}

    def media_for(self, req: PublishRequest) -> list[Path]:
        if req.format in ("short", "long"):
            if not req.video_path:
                raise PublishError("postiz: video post has no video file", retryable=False)
            return [Path(req.video_path)]
        if not req.image_paths:
            raise PublishError("postiz: image post has no images", retryable=False)
        return [Path(p) for p in (req.image_paths[:1] if req.format == "image" else req.image_paths)]

    # ------------------------------------------------------------------ settings
    def settings_for(self, identifier: str, req: PublishRequest, thumb: dict | None) -> dict:
        kind = ALIASES.get(identifier, identifier)
        if kind == "youtube":
            if req.realistic_synthetic:
                raise PublishError("postiz: can't set YouTube's containsSyntheticMedia via Postiz; "
                                   "publish realistic synthetic videos with the direct YouTube adapter", retryable=False)
            privacy = (self.settings.env("YT_PRIVACY", "private") or "private").lower()
            return {"__type": "youtube", "title": (req.title or "Untitled")[:100].ljust(2, "."),
                    "type": privacy, "selfDeclaredMadeForKids": "no", "thumbnail": thumb,
                    "tags": [{"value": t.lstrip("#"), "label": t.lstrip("#")} for t in req.tags]}
        if kind == "tiktok":
            privacy = (self.settings.env("TIKTOK_PRIVACY") or "SELF_ONLY").upper()
            return {"__type": "tiktok", "title": req.title[:90], "privacy_level": privacy,
                    "duet": False, "stitch": False, "comment": True, "autoAddMusic": "no",
                    "brand_content_toggle": bool(req.has_paid_promotion), "brand_organic_toggle": False,
                    "video_made_with_ai": bool(req.ai_generated), "content_posting_method": "DIRECT_POST"}
        if kind == "instagram":
            return {"__type": identifier, "post_type": "post"}
        if kind == "facebook":
            return {"__type": "facebook", "post_type": "post",
                    **({"title": req.title} if req.format in ("short", "long") else {})}
        return {"__type": identifier}

    # ------------------------------------------------------------------ publish
    def publish(self, req: PublishRequest) -> PublishResult:
        self.ensure_credentials()
        targets = self.targets(req.platform)
        media = [self.upload(p) for p in self.media_for(req)]
        thumb = self.upload(Path(req.thumbnail_path)) if (req.thumbnail_path and req.format == "long"
                                                           and Path(req.thumbnail_path).exists()) else None
        caption = fit_caption(req.caption, 2200, 30, protected=disclosures(req.caption, req.brand.ai_disclosure))
        posts = [{"integration": {"id": iid},
                  "value": [{"content": caption, "image": media}],
                  "settings": self.settings_for(ident, req, thumb)} for ident, iid in targets]
        when = req.scheduled_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload = {"type": "schedule" if req.scheduled_at else "now", "date": when,
                   "shortLink": False, "tags": [], "posts": posts}
        resp = self.http.request("POST", f"{self.base}/posts", what="create post",
                                 headers={**self._headers(), "Content-Type": "application/json"},
                                 content=json.dumps(payload).encode())
        created = resp.json()
        created = created if isinstance(created, list) else [created]
        ids = [str(c.get("postId", "")) for c in created if c.get("postId")]
        if not ids:
            raise PublishError("postiz: create post returned no postId", retryable=False)
        return PublishResult(remote_id=ids[0], url="", raw={
            "postiz_posts": created, "targets": [t[0] for t in targets], "type": payload["type"],
            "date": when, "media": media})

    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        return MetricsSnapshot(raw={"note": "Postiz public API exposes no per-post analytics; "
                                            "collect metrics with the direct platform adapters"})
