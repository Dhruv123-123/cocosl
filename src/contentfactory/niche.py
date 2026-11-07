"""Pick a niche and spin up a brand profile for it.

`score_niche` is a quick, honest scorecard (ad value, product fit, demand,
saturation, compliance risk). `generate_brand` drafts a full brand YAML with
the LLM (offline: a sensible template) for you to edit.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .ideas import youtube_suggestions
from .llm import LLM

# Long-form ad value tiers (USD RPM, rough ranges from public creator reports, 2025-26).
# Shorts pay ~$0.03-0.10 per 1k views regardless of niche.
RPM_TIERS = {
    "finance": (8, 15), "investing": (8, 15), "business": (6, 12), "software": (6, 12), "ai tools": (5, 10),
    "real estate": (6, 12), "careers": (4, 8), "education": (4, 8), "tech": (4, 8), "health": (3, 7),
    "history": (3, 6), "science": (3, 6), "travel": (2, 5), "food": (2, 4), "diy": (2, 5),
    "fitness": (2, 5), "productivity": (4, 8), "parenting": (3, 6), "pets": (2, 4),
    "gaming": (1, 3), "entertainment": (1, 3), "memes": (0.5, 2), "music": (0.5, 2),
}
HIGH_RISK = ["medical", "supplement", "crypto", "forex", "gambling", "betting", "weight loss", "diet pills",
             "celebrity", "news", "politics", "adult"]
SATURATED = ["reddit stories", "motivational quotes", "stoic", "facts", "quiz", "ai art", "true crime", "luxury lifestyle"]


class NicheScore(BaseModel):
    niche: str
    rpm_range: tuple[float, float]
    demand_signals: int
    risk_flags: list[str]
    saturation_flags: list[str]
    score: float
    verdict: str


def score_niche(niche: str, online: bool = True) -> NicheScore:
    low = niche.lower()
    rpm = next((v for k, v in RPM_TIERS.items() if k in low), (2, 5))
    risks = [r for r in HIGH_RISK if r in low]
    sat = [s for s in SATURATED if s in low]
    demand = len(youtube_suggestions(niche)) if online else 5
    score = (rpm[0] + rpm[1]) / 2 + min(demand, 10) * 0.5 - 4 * len(risks) - 3 * len(sat)
    if risks:
        verdict = "Risky: platforms and advertisers restrict this; expect limited ads and stricter review."
    elif sat:
        verdict = "Saturated format: only worth it with a genuinely different angle or style."
    elif score >= 10:
        verdict = "Strong: good ad value and product/affiliate fit. Go deep on one sub-niche."
    elif score >= 6:
        verdict = "Decent: viable with a clear format and a product or affiliate offer."
    else:
        verdict = "Weak on ads: only pursue if you have a product, service or real expertise to sell."
    return NicheScore(niche=niche, rpm_range=rpm, demand_signals=demand, risk_flags=risks,
                      saturation_flags=sat, score=round(score, 1), verdict=verdict)


class BrandDraft(BaseModel):
    name: str
    slug: str = Field(description="lowercase-hyphenated")
    niche: str
    audience: str
    promise: str
    pillars: list[str]
    seed_topics: list[str]
    avoid_topics: list[str]
    subreddits: list[str]
    hashtags: list[str]
    cta: str
    tone: str
    persona: str
    image_style: str
    mascot: str
    palette: list[str] = Field(description="4 hex colours: dark, light, accent, highlight")
    product_ideas: list[str]
    affiliate_categories: list[str]


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "brand"


def _offline_brand(niche: str, audience: str) -> BrandDraft:
    words = [w for w in re.findall(r"[A-Za-z]+", niche) if len(w) > 3][:2] or ["Simple"]
    name = " ".join(w.capitalize() for w in words) + " Explained"
    return BrandDraft(
        name=name, slug=_slugify(name), niche=niche, audience=audience or f"beginners curious about {niche}",
        promise=f"one useful thing about {niche} in under a minute",
        pillars=[f"{niche} basics", f"common {niche} mistakes", f"tools for {niche}", f"{niche} myths"],
        seed_topics=[niche, f"{niche} for beginners", f"best {niche} tools", f"{niche} mistakes"],
        avoid_topics=["get rich quick", "guarantees"], subreddits=[],
        hashtags=[_slugify(niche).replace("-", ""), "learnontiktok", "howto", "tips"],
        cta="Follow for more.", tone="clear, friendly, no hype", persona="a patient expert friend",
        image_style="clean flat vector illustration, soft colours, simple shapes, no text, no logos",
        mascot="", palette=["#111827", "#f9fafb", "#6366f1", "#f59e0b"],
        product_ideas=[f"{niche} starter checklist (PDF)"], affiliate_categories=["tools", "books"],
    )


def generate_brand(llm: LLM, niche: str, audience: str = "", platforms: list[str] | None = None) -> dict:
    prompt = f"""Design a faceless educational content brand for this niche.
Niche: {niche}
Audience: {audience or 'choose the most valuable specific audience'}

Requirements: a specific promise, 3-5 pillars that won't run dry, original visual identity (no real
people, no copyrighted characters), a mascot only if it helps, topics to avoid for compliance and brand
safety, product ideas a small creator could make, and affiliate categories (not specific companies)."""
    d = llm.structured(BrandDraft, system="You are a content strategist who builds durable niche brands.",
                       prompt=prompt, purpose="brand", offline=lambda: _offline_brand(niche, audience))
    platforms = platforms or ["instagram", "youtube", "tiktok"]
    handle = "@" + d.slug.replace("-", "")
    fmt_for = {"instagram": ["short", "carousel", "image"], "youtube": ["short", "long"], "tiktok": ["short"],
               "facebook": ["short", "image"], "threads": ["image", "carousel"]}
    return {
        "name": d.name, "niche": d.niche, "audience": d.audience, "promise": d.promise,
        "pillars": d.pillars, "formats": ["short", "carousel", "long"], "seed_topics": d.seed_topics,
        "avoid_topics": d.avoid_topics, "subreddits": d.subreddits, "hashtags": d.hashtags, "cta": d.cta,
        "voice": {"tone": d.tone, "persona": d.persona, "tts_voice": "", "banned_phrases": []},
        "visual": {"palette": d.palette[:4], "font": "Inter", "image_style": d.image_style,
                   "mascot": d.mascot, "watermark": handle},
        "accounts": [{"platform": p, "handle": handle, "formats": fmt_for.get(p, ["short"])} for p in platforms],
        "affiliates": [], "products": [{"name": p, "url": "", "price": 9} for p in d.product_ideas[:2]],
        "ai_disclosure": "Visuals and voice made with AI tools. Script drafted with AI help and fact-checked by a person.",
        "realistic_synthetic_media": False, "require_human_review": True,
        "_notes": {"affiliate_categories": d.affiliate_categories},
    }, d.slug


def write_brand(brands_dir: Path, data: dict, slug: str, overwrite: bool = False) -> Path:
    path = brands_dir / f"{slug}.yaml"
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} exists")
    notes = data.pop("_notes", {})
    header = "# Generated brand profile. Review every field, then add real affiliate links and products.\n"
    if notes.get("affiliate_categories"):
        header += f"# Affiliate categories to look for: {', '.join(notes['affiliate_categories'])}\n"
    brands_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    return path
