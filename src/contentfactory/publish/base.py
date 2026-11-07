"""Publisher interface. Every platform adapter uses only official APIs.

Adapters get everything they need through `PublishRequest` and must not
touch the database; the pipeline records results.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..config import BrandProfile, Settings


class PublishError(RuntimeError):
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class MissingCredentials(PublishError):
    def __init__(self, platform: str, keys: list[str]):
        super().__init__(f"{platform}: missing credentials {', '.join(keys)} (see docs/CREDENTIALS.md)")
        self.keys = keys


@dataclass
class PublishRequest:
    platform: str
    brand: BrandProfile
    settings: Settings
    format: str                    # short | long | carousel | image
    title: str
    caption: str                   # final caption including hashtags and disclosures
    description: str               # long description (YouTube)
    tags: list[str]
    video_path: Path | None = None
    image_paths: list[Path] = field(default_factory=list)
    thumbnail_path: Path | None = None
    captions_path: Path | None = None  # SRT timed to the voice (YouTube caption track)
    public_urls: dict[str, str] = field(default_factory=dict)  # local path str -> https URL (Instagram needs these)
    ai_generated: bool = True      # sets platform AI-content labels where the API supports it
    realistic_synthetic: bool = False
    has_paid_promotion: bool = False
    scheduled_at: str | None = None


@dataclass
class PublishResult:
    remote_id: str
    url: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class MetricsSnapshot:
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    watch_seconds: float = 0.0
    avg_view_pct: float = 0.0
    follows: int = 0
    link_clicks: int = 0
    raw: dict = field(default_factory=dict)


class Publisher:
    platform: str = "base"
    required_env: list[str] = []

    def __init__(self, settings: Settings):
        self.settings = settings

    def missing_credentials(self) -> list[str]:
        return [k for k in self.required_env if not self.settings.env(k)]

    def ensure_credentials(self) -> None:
        missing = self.missing_credentials()
        if missing:
            raise MissingCredentials(self.platform, missing)

    def supports(self, fmt: str) -> bool:
        return True

    def publish(self, req: PublishRequest) -> PublishResult:  # pragma: no cover - interface
        raise NotImplementedError

    def fetch_metrics(self, remote_id: str) -> MetricsSnapshot:  # pragma: no cover - interface
        raise NotImplementedError
