"""Settings and brand profiles.

Settings come from environment variables (see `.env.example`). Brand profiles
are YAML files in `brands/`; each one describes a single niche channel: who it
is for, how it sounds, how it looks, where it posts and how it makes money.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader so we don't need python-dotenv. Existing env wins."""
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass
class Settings:
    home: Path
    db_path: Path
    output_dir: Path
    brands_dir: Path
    llm_provider: str = "auto"  # auto | anthropic | offline
    anthropic_model: str = "claude-opus-5-5"
    anthropic_effort: str = "medium"
    tts_provider: str = "auto"  # auto | piper | espeak | elevenlabs | openai | silent
    image_provider: str = "auto"  # auto | comfyui | openai | replicate | cards
    public_media_base_url: str = ""  # where rendered files are reachable over HTTPS (needed by Instagram)
    dry_run: bool = True  # never call publishing APIs unless explicitly turned off
    dashboard_token: str = ""
    extra: dict = field(default_factory=dict)

    @classmethod
    def load(cls, home: str | Path | None = None) -> "Settings":
        home_path = Path(home or os.environ.get("FACTORY_HOME") or Path.cwd()).resolve()
        _load_dotenv(home_path / ".env")
        env = os.environ
        s = cls(
            home=home_path,
            db_path=Path(env.get("FACTORY_DB", home_path / "data" / "factory.db")),
            output_dir=Path(env.get("FACTORY_OUTPUT", home_path / "output")),
            brands_dir=Path(env.get("FACTORY_BRANDS", home_path / "brands")),
            llm_provider=env.get("FACTORY_LLM", "auto"),
            anthropic_model=env.get("FACTORY_MODEL", "claude-opus-5-5"),
            anthropic_effort=env.get("FACTORY_EFFORT", "medium"),
            tts_provider=env.get("FACTORY_TTS", "auto"),
            image_provider=env.get("FACTORY_IMAGES", "auto"),
            public_media_base_url=env.get("PUBLIC_MEDIA_BASE_URL", "").rstrip("/"),
            dry_run=env.get("FACTORY_DRY_RUN", "1").lower() not in ("0", "false", "no"),
            dashboard_token=env.get("DASHBOARD_TOKEN", ""),
        )
        s.db_path.parent.mkdir(parents=True, exist_ok=True)
        s.output_dir.mkdir(parents=True, exist_ok=True)
        return s

    def env(self, key: str, default: str = "") -> str:
        return os.environ.get(key, default)


# ---------------------------------------------------------------------------
# Brand profile
# ---------------------------------------------------------------------------

Platform = Literal["instagram", "youtube", "tiktok", "facebook", "threads", "postiz"]


class VisualStyle(BaseModel):
    palette: list[str] = Field(default_factory=lambda: ["#0f172a", "#f8fafc", "#22d3ee", "#f59e0b"])
    font: str = "Inter"
    image_style: str = "clean flat editorial illustration, soft lighting, no text"
    mascot: str = ""  # optional recurring character description (original, never a real person)
    watermark: str = ""  # e.g. @handle


class VoiceStyle(BaseModel):
    tone: str = "friendly, direct, no hype"
    persona: str = "a knowledgeable friend"
    tts_voice: str = ""  # provider-specific voice id; must be your own or licensed
    words_per_minute: int = 160
    piper_model: str = ""  # path to a Piper .onnx voice in the brand's language (overrides PIPER_MODEL)
    banned_phrases: list[str] = Field(default_factory=list)


class Cadence(BaseModel):
    """Posting limits. Defaults are deliberately conservative."""
    shorts_per_week: int = 7
    long_per_week: int = 1
    carousels_per_week: int = 3
    max_posts_per_day_per_platform: int = 2
    post_times: list[str] = Field(default_factory=lambda: ["12:30", "18:30"])  # local times
    timezone: str = "America/New_York"


class AffiliateOffer(BaseModel):
    name: str
    url: str
    slug: str = ""
    keywords: list[str] = Field(default_factory=list)
    commission: str = ""


class PlatformAccount(BaseModel):
    platform: Platform
    handle: str = ""
    enabled: bool = True
    formats: list[str] = Field(default_factory=lambda: ["short"])


class BrandProfile(BaseModel):
    slug: str
    name: str
    niche: str
    audience: str
    promise: str = ""  # what the viewer gets from following
    pillars: list[str] = Field(default_factory=list)  # recurring content themes
    formats: list[str] = Field(default_factory=lambda: ["short", "carousel"])
    seed_topics: list[str] = Field(default_factory=list)
    avoid_topics: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=list)  # read-only topic signals
    hashtags: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)  # optional Instagram highlight titles (≤15 chars)
    bios: dict[str, str] = Field(default_factory=dict)  # optional hand-written bios: instagram, tiktok, x, threads, youtube_about
    cta: str = "Follow for more."
    link_in_bio: str = ""
    language: str = "en"  # ISO 639-1; script copy, on-screen labels, bios and TTS follow it (see i18n.py)
    region: str = ""  # optional market, e.g. "US" -> locale es-US; also used for trend signals
    visual: VisualStyle = Field(default_factory=VisualStyle)
    voice: VoiceStyle = Field(default_factory=VoiceStyle)
    cadence: Cadence = Field(default_factory=Cadence)
    accounts: list[PlatformAccount] = Field(default_factory=list)
    affiliates: list[AffiliateOffer] = Field(default_factory=list)
    products: list[dict] = Field(default_factory=list)  # {name, url, price}
    # Compliance switches. The defaults are the safe ones; flipping them is on you.
    ai_disclosure: str = "Made with AI tools; written and fact-checked by a human."
    realistic_synthetic_media: bool = False  # True if visuals/voices could pass as real people/events
    require_human_review: bool = True

    def account(self, platform: str) -> PlatformAccount | None:
        return next((a for a in self.accounts if a.platform == platform and a.enabled), None)


def load_brands(brands_dir: Path) -> dict[str, BrandProfile]:
    brands: dict[str, BrandProfile] = {}
    if not brands_dir.exists():
        return brands
    for path in sorted(brands_dir.glob("*.y*ml")):
        if path.name.startswith("_"):
            continue
        data = yaml.safe_load(path.read_text()) or {}
        data.setdefault("slug", path.stem)
        brand = BrandProfile.model_validate(data)
        brands[brand.slug] = brand
    return brands


def load_brand(brands_dir: Path, slug: str) -> BrandProfile:
    brands = load_brands(brands_dir)
    if slug not in brands:
        known = ", ".join(brands) or "none"
        raise KeyError(f"Unknown brand '{slug}'. Known brands: {known}")
    return brands[slug]
