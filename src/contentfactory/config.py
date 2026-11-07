"""Settings and brand profiles.

Settings come from environment variables (see `.env.example`). Brand profiles
are YAML files in `brands/`; each one describes a single niche channel: who it
is for, how it sounds, how it looks, where it posts and how it makes money.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator


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
    tts_provider: str = "auto"  # auto | kokoro | piper | espeak | elevenlabs | openai | silent
    image_provider: str = "auto"  # auto | comfyui | openai | replicate | cards
    public_media_base_url: str = ""  # where rendered files are reachable over HTTPS (needed by Instagram)
    dry_run: bool = True  # never call publishing APIs unless explicitly turned off
    dashboard_token: str = ""
    extra: dict = field(default_factory=dict)
    brand_scope: str = ""  # set by for_brand(): env() prefers <BRAND>__KEY over KEY

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
        """A setting from the environment. Inside a brand scope, `MONEY_MADE_SIMPLE__IG_ACCESS_TOKEN`
        wins over `IG_ACCESS_TOKEN`, so each brand can post to its own accounts while app-level
        values (client ids, secrets) stay shared."""
        if self.brand_scope:
            scoped = os.environ.get(scoped_key(self.brand_scope, key))
            if scoped:
                return scoped
        return os.environ.get(key, default)

    def env_key(self, key: str, write_scoped: bool | None = None) -> str:
        """The variable name to write a refreshed/new value to: the brand-scoped name if this brand
        already uses one (or write_scoped=True), else the shared name."""
        if self.brand_scope:
            name = scoped_key(self.brand_scope, key)
            if write_scoped or (write_scoped is None and os.environ.get(name)):
                return name
        return key

    def for_brand(self, slug: str | None) -> "Settings":
        from dataclasses import replace
        return replace(self, brand_scope=slug or "")


def scoped_key(brand_slug: str, key: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", brand_slug.upper()).strip("_") + "__" + key


# ---------------------------------------------------------------------------
# Brand profile
# ---------------------------------------------------------------------------

Platform = Literal["instagram", "youtube", "tiktok", "facebook", "threads", "postiz", "pinterest"]


class SignatureVisual(BaseModel):
    """One recurring graphic device (see media/signature.py). auto = picked from the slug."""
    device: Literal["auto", "corner_block", "stripe", "ring", "bracket", "dot_grid", "none"] = "auto"
    color: str = "accent"  # accent | accent2 | light | dark | #hex
    corner: Literal["top-left", "top-right", "bottom-left", "bottom-right"] = "top-right"
    size: float = Field(0.14, ge=0.04, le=0.4)
    label: str = Field("", max_length=6)
    where: list[Literal["thumbnail", "intro", "cover"]] = Field(default_factory=lambda: ["thumbnail", "intro", "cover"])


class VisualStyle(BaseModel):
    palette: list[str] = Field(default_factory=lambda: ["#0f172a", "#f8fafc", "#22d3ee", "#f59e0b"])
    font: str = "Inter"
    image_style: str = "clean flat editorial illustration, soft lighting, no text"
    mascot: str = ""  # optional recurring character description (original, never a real person)
    watermark: str = ""  # e.g. @handle
    signature: SignatureVisual = Field(default_factory=SignatureVisual)


class VoiceStyle(BaseModel):
    tone: str = "friendly, direct, no hype"
    persona: str = "a knowledgeable friend"
    tts_voice: str = ""  # provider-specific voice id; must be your own or licensed
    words_per_minute: int = 160
    piper_model: str = ""  # path to a Piper .onnx voice in the brand's language (overrides PIPER_MODEL)
    banned_phrases: list[str] = Field(default_factory=list)


DEFAULT_PLATFORM_TIMES = {"tiktok": ["18:00"], "pinterest": ["11:00"], "youtube:short": ["12:30"]}
DEFAULT_WEEKLY_CAPS: dict[str, int] = {}  # scouting dropped the 3 Reels/week idea: 6-9 posts a week grows faster


class Cadence(BaseModel):
    """Posting limits. Defaults are deliberately conservative."""
    shorts_per_week: int = 7
    long_per_week: int = 1
    carousels_per_week: int = 3
    max_posts_per_day_per_platform: int = 2
    post_times: list[str] = Field(default_factory=lambda: ["12:30", "18:30"])  # local times
    # Local posting times per platform, or per "platform:format" (that wins). Defaults from scouting's
    # posting-times memo (PR #2): TikTok 6pm, Pinterest 11am, YouTube Shorts 12:30. Anything not listed
    # uses post_times. A brand file's platform_times entries are merged over these defaults.
    platform_times: dict[str, list[str]] = Field(default_factory=lambda: dict(DEFAULT_PLATFORM_TIMES))
    # Optional: at most N posts in any 7 days per "platform:format" (or "platform"), e.g.
    # {"instagram:short": 3}. Past the cap the scheduler leaves that platform out (the post still goes to
    # the others); asked for explicitly, it refuses. None by default.
    platform_weekly_caps: dict[str, int] = Field(default_factory=lambda: dict(DEFAULT_WEEKLY_CAPS))
    timezone: str = "America/New_York"
    # Worker settings for this brand (multi-brand runner)
    daily_at: str = ""            # local HH:MM for the daily ideas+drafts run; "" = DAILY_AT env (07:00)
    daily_ideas: int = 8
    daily_drafts: int = 2         # posts drafted into the review queue per day
    paused: bool = False          # true = the worker skips this brand's daily run (publishing still runs)

    @field_validator("platform_times", mode="after")
    @classmethod
    def _merge_times(cls, v: dict) -> dict:
        return {**DEFAULT_PLATFORM_TIMES, **(v or {})}

    @field_validator("platform_weekly_caps", mode="after")
    @classmethod
    def _merge_caps(cls, v: dict) -> dict:
        return {**DEFAULT_WEEKLY_CAPS, **(v or {})}

    def times_for(self, platform: str, fmt: str | None = None) -> list[str]:
        return (self.platform_times.get(f"{platform}:{fmt}") if fmt else None) or self.platform_times.get(platform) \
            or self.post_times

    def weekly_cap(self, platform: str, fmt: str | None = None) -> int | None:
        v = (self.platform_weekly_caps.get(f"{platform}:{fmt}") if fmt else None)
        if v is None:
            v = self.platform_weekly_caps.get(platform)
        if v is None and fmt == "mid":
            v = self.platform_weekly_caps.get(f"{platform}:short")
        return v


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
    board: str = ""  # Pinterest board the pin goes on


class PlaylistPlan(BaseModel):
    title: str  # lead with the search phrase, e.g. "Budgeting for beginners: start here"
    description: str = ""
    pillars: list[str] = Field(default_factory=list)  # posts in these pillars go here
    keywords: list[str] = Field(default_factory=list)  # ...or whose title contains one of these


class YouTubePlan(BaseModel):
    """Set by hand in Studio (the Data API has no end-screen or related-video endpoint)."""
    playlists: list[PlaylistPlan] = Field(default_factory=list)  # empty = one per pillar
    start_here: str = "Start here"  # a playlist of the 3-5 best videos, featured on the channel page
    end_screen: list[str] = Field(default_factory=lambda: [
        "Left: the next video in this series (specific video)", "Right: Best for viewer", "Subscribe button"])


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
    youtube: YouTubePlan = Field(default_factory=YouTubePlan)
    affiliates: list[AffiliateOffer] = Field(default_factory=list)
    products: list[dict] = Field(default_factory=list)  # {name, url, price}
    # Compliance switches. The defaults are the safe ones; flipping them is on you.
    ai_disclosure: str = "Visuals and voice made with AI tools. Script drafted with AI help and fact-checked by a person."
    # Who writes the scripts. "ai_assisted" (the default: writer.py drafts them, you fact-check) or
    # "person" (you write them yourself). launch-check turns red if ai_disclosure claims a person wrote
    # scripts while this says ai_assisted: understating AI use is what platforms and the FTC call deceptive.
    scripts_by: Literal["ai_assisted", "person"] = "ai_assisted"
    # Who sends the welcome sequence: the factory's own mailer, or an email platform you built it in
    # (`factory sequence-export --for sender`). Anything but "factory" makes the worker skip this brand's welcomes.
    welcome_via: Literal["factory", "sender", "kit"] = "factory"
    realistic_synthetic_media: bool = False  # True if visuals/voices could pass as real people/events
    require_human_review: bool = True
    # Extra reviews every post of this brand needs before you can approve it: native_review (a fluent
    # speaker) and/or legal_review (an attorney or tax pro). See `factory review-gate`.
    review_stages: list[Literal["native_review", "legal_review"]] = Field(default_factory=list)
    own_voice: bool = False  # videos wait for the owner's recorded narration (`factory voice`) before scheduling

    def account(self, platform: str) -> PlatformAccount | None:
        return next((a for a in self.accounts if a.platform == platform and a.enabled), None)


_BRAND_CACHE: dict[Path, tuple[str, BrandProfile]] = {}
_YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _load_brand_file(path: Path) -> BrandProfile:
    """Parse and validate one brand file, cached until its text changes.

    Pages and checks ask for the brands once per post; parsing the YAML every time made the
    dashboard take seconds with a few hundred posts. Callers get their own copy, so changing
    one in memory never leaks into the next call."""
    text = path.read_text()
    key = hashlib.sha1(text.encode()).hexdigest()
    hit = _BRAND_CACHE.get(path)
    if hit is None or hit[0] != key:
        data = yaml.load(text, Loader=_YAML_LOADER) or {}
        data.setdefault("slug", path.stem)
        hit = (key, BrandProfile.model_validate(data))
        _BRAND_CACHE[path] = hit
    return hit[1].model_copy(deep=True)


def load_brands(brands_dir: Path) -> dict[str, BrandProfile]:
    brands: dict[str, BrandProfile] = {}
    if not brands_dir.exists():
        return brands
    for path in sorted(brands_dir.glob("*.y*ml")):
        if path.name.startswith("_"):
            continue
        brand = _load_brand_file(path.resolve())
        brands[brand.slug] = brand
    return brands


def load_brand(brands_dir: Path, slug: str) -> BrandProfile:
    brands = load_brands(brands_dir)
    if slug not in brands:
        known = ", ".join(brands) or "none"
        raise KeyError(f"Unknown brand '{slug}'. Known brands: {known}")
    return brands[slug]
