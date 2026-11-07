"""Platform bios for a brand, with hard length limits and an AI disclosure.

The LLM writes the copy (`llm.structured`); the offline fallback assembles it
from the brand profile. Either way `enforce_limits` trims each bio to the
platform limit and adds "AI-assisted" wherever it fits.
"""
from __future__ import annotations

import re

from pydantic import BaseModel, Field

from ..config import BrandProfile
from ..llm import LLM

LIMITS = {"instagram": 150, "tiktok": 80, "youtube_about": 1000, "x": 160, "threads": 150}
AI_TAG = "AI-assisted"
AI_RE = re.compile(r"\bAI[- ](assisted|generated|made|tools)\b|made with AI", re.I)


class BioPack(BaseModel):
    instagram: str = Field(description="Instagram bio, max 150 characters, line breaks allowed")
    tiktok: str = Field(description="TikTok bio, max 80 characters")
    youtube_about: str = Field(description="YouTube channel About text, 800-1000 characters, plain text")
    x: str = Field(description="X (Twitter) bio, max 160 characters")
    threads: str = Field(description="Threads bio, max 150 characters")


SYSTEM = (
    "You write social media bios for a small faceless creator brand. Plain, specific, no hype, no emojis "
    "unless they add meaning, no hashtags. Never claim the creator is a licensed professional, never promise "
    "results or income. Each bio must state what the follower gets. Respect the character limits exactly. "
    "Include the words 'AI-assisted' in every bio where it fits; the YouTube About must include a sentence "
    "that explains how AI tools are used and that a human writes/checks the content."
)


def prompt_for(brand: BrandProfile) -> str:
    return (
        f"Brand: {brand.name}\nNiche: {brand.niche}\nAudience: {brand.audience}\nPromise: {brand.promise}\n"
        f"Pillars: {', '.join(brand.pillars)}\nTone: {brand.voice.tone}\nPersona: {brand.voice.persona}\n"
        f"Call to action: {brand.cta}\nAI disclosure policy: {brand.ai_disclosure}\n"
        f"Banned phrases: {', '.join(brand.voice.banned_phrases) or 'none'}\n"
        f"Limits: instagram {LIMITS['instagram']}, tiktok {LIMITS['tiktok']}, x {LIMITS['x']}, "
        f"threads {LIMITS['threads']}, youtube_about about {LIMITS['youtube_about']} characters."
    )


def _sentence(text: str) -> str:
    text = text.strip().rstrip(".")
    return text[:1].upper() + text[1:] if text else ""


def offline_bios(brand: BrandProfile) -> BioPack:
    """Deterministic bios built only from brand fields."""
    promise = _sentence(brand.promise or brand.niche)
    cta = brand.cta.strip()
    pillars = [p.strip() for p in brand.pillars if p.strip()]
    topics = "; ".join(pillars)
    about = (
        f"{brand.name}: {promise.lower() if promise else brand.niche}.\n\n"
        f"Made for {brand.audience}. We cover {topics or brand.niche}.\n\n"
        f"Every upload is specific and free of hype: one idea you can use, explained clearly. "
        f"{cta}\n\n"
        f"How this channel is made: {brand.ai_disclosure} Content is AI-assisted; a human chooses every topic, "
        f"checks the facts and approves each upload. No fake reviews, no AI testimonials.\n\n"
        f"Some links may be affiliate links; if you buy through them we may earn a commission at no extra cost "
        f"to you. Business enquiries via the link in the channel header."
    )
    return BioPack(
        instagram=f"{promise}.\n{cta}\n{AI_TAG} · free guide below",
        tiktok=f"{promise}",
        youtube_about=about,
        x=f"{promise}. {cta} {AI_TAG}.",
        threads=f"{promise}.\n{cta}\n{AI_TAG}",
    )


def _trim(text: str, limit: int) -> str:
    """Trim to `limit` characters at a word boundary, with an ellipsis."""
    text = re.sub(r"[ \t]+", " ", text.strip())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut[limit // 2:]:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,.;:·-\n") + "…"


def _with_tag(text: str, limit: int, sep: str) -> str:
    """Append the AI tag when missing, making room by trimming when the bio is
    long enough to spare the space (tiny bios keep the copy instead)."""
    text = text.strip()
    if AI_RE.search(text):
        return _trim(text, limit)
    suffix = f"{sep}{AI_TAG}"
    if len(text) + len(suffix) <= limit:
        return text + suffix
    room = limit - len(suffix)
    if room >= 40:
        return _trim(text, room) + suffix
    return _trim(text, limit)


def enforce_limits(pack: BioPack) -> BioPack:
    return BioPack(
        instagram=_with_tag(pack.instagram, LIMITS["instagram"], "\n"),
        tiktok=_with_tag(pack.tiktok, LIMITS["tiktok"], " · "),
        youtube_about=_with_tag(pack.youtube_about, LIMITS["youtube_about"], "\n\n"),
        x=_with_tag(pack.x, LIMITS["x"], " · "),
        threads=_with_tag(pack.threads, LIMITS["threads"], "\n"),
    )


def write_bios(llm: LLM, brand: BrandProfile) -> BioPack:
    pack = llm.structured(BioPack, system=SYSTEM, prompt=prompt_for(brand),
                          offline=lambda: offline_bios(brand), purpose="brandkit.bios", max_tokens=4000)
    return enforce_limits(pack)


def render_text(brand: BrandProfile, pack: BioPack) -> str:
    """Human-friendly bio pack with character counts, ready to copy."""
    rows = [("Instagram bio", pack.instagram, LIMITS["instagram"]),
            ("TikTok bio", pack.tiktok, LIMITS["tiktok"]),
            ("X bio", pack.x, LIMITS["x"]),
            ("Threads bio", pack.threads, LIMITS["threads"]),
            ("YouTube About", pack.youtube_about, LIMITS["youtube_about"])]
    out = [f"BIO PACK: {brand.name}", "=" * (10 + len(brand.name)), ""]
    for label, text, limit in rows:
        out += [f"## {label}  ({len(text)}/{limit} chars)", text, ""]
    out += ["## Full AI disclosure (pin or add to descriptions)", brand.ai_disclosure, "",
            "Notes: keep 'AI-assisted' visible in bios; also use each platform's own AI label "
            "when posting realistic synthetic media."]
    return "\n".join(out) + "\n"
