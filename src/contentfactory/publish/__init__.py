"""Platform publishers (official APIs only) and the dry-run stand-in."""
from __future__ import annotations

import hashlib
import importlib

from ..config import Settings
from .base import (MetricsSnapshot, MissingCredentials, PublishError, Publisher,  # noqa: F401
                   PublishRequest, PublishResult)

REGISTRY = {
    "instagram": ("contentfactory.publish.instagram", "InstagramPublisher"),
    "facebook": ("contentfactory.publish.facebook", "FacebookPublisher"),
    "threads": ("contentfactory.publish.threads", "ThreadsPublisher"),
    "youtube": ("contentfactory.publish.youtube", "YouTubePublisher"),
    "tiktok": ("contentfactory.publish.tiktok", "TikTokPublisher"),
    "postiz": ("contentfactory.publish.postiz", "PostizPublisher"),
    "pinterest": ("contentfactory.publish.pinterest", "PinterestPublisher"),  # post-by-hand packages only
}


class DryRunPublisher(Publisher):
    """Records what would be posted without calling any API."""
    platform = "dry_run"

    def __init__(self, settings: Settings, target: str):
        super().__init__(settings)
        self.target = target

    def publish(self, req: PublishRequest) -> PublishResult:
        digest = hashlib.sha1(f"{req.platform}{req.title}{req.caption}".encode()).hexdigest()[:12]
        return PublishResult(remote_id=f"dry-{digest}", url="",
                             raw={"dry_run": True, "platform": req.platform, "format": req.format,
                                  "caption_chars": len(req.caption)})

    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:
        return MetricsSnapshot()


def get_publisher(platform: str, settings: Settings, dry_run: bool | None = None) -> Publisher:
    if dry_run if dry_run is not None else settings.dry_run:
        return DryRunPublisher(settings, platform)
    if platform not in REGISTRY:
        raise PublishError(f"No publisher for platform '{platform}'")
    module, cls = REGISTRY[platform]
    return getattr(importlib.import_module(module), cls)(settings)


def credential_status(settings: Settings) -> dict[str, list[str]]:
    """Platform -> list of missing env vars (empty list = ready)."""
    out = {}
    for platform, (module, cls) in REGISTRY.items():
        try:
            pub = getattr(importlib.import_module(module), cls)(settings)
            out[platform] = pub.missing_credentials()
        except Exception as e:  # module not importable
            out[platform] = [f"error: {e}"]
    return out
