"""Idea generation, trend intake, scoring and de-duplication."""
from __future__ import annotations

import hashlib
import random
import re
import xml.etree.ElementTree as ET

import httpx

from .config import BrandProfile
from .db import DB
from .guardrails import jaccard, shingles
from .llm import LLM
from .schemas import IdeaBatch, IdeaDraft

USER_AGENT = "contentfactory/0.1 (+https://github.com/; research tool)"


# ---------------------------------------------------------------------------
# Trend signals. All read-only public endpoints; failures are non-fatal.
# ---------------------------------------------------------------------------
def google_trends_daily(geo: str = "US", timeout: float = 8.0) -> list[str]:
    try:
        r = httpx.get(f"https://trends.google.com/trending/rss?geo={geo}", timeout=timeout,
                      headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        root = ET.fromstring(r.text)
        return [i.findtext("title") or "" for i in root.iter("item")][:25]
    except Exception:
        return []


def youtube_suggestions(query: str, timeout: float = 6.0) -> list[str]:
    """Autocomplete suggestions reflect what people actually search for."""
    try:
        r = httpx.get("https://suggestqueries.google.com/complete/search",
                      params={"client": "firefox", "ds": "yt", "q": query},
                      timeout=timeout, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        data = r.json()
        return [s for s in data[1]][:10]
    except Exception:
        return []


def reddit_questions(subreddit: str, timeout: float = 8.0) -> list[str]:
    """Top question-style post titles: a list of what the audience is confused
    about. We only use titles as topic signals and never reuse post content."""
    try:
        r = httpx.get(f"https://www.reddit.com/r/{subreddit}/top.json",
                      params={"t": "week", "limit": 50}, timeout=timeout,
                      headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        titles = [c["data"]["title"] for c in r.json()["data"]["children"]]
        return [t for t in titles if "?" in t or re.match(r"(?i)^(how|why|what|is|should|can)\b", t)][:20]
    except Exception:
        return []


def gather_signals(brand: BrandProfile, online: bool = True) -> list[str]:
    if not online:
        return []
    signals: list[str] = []
    for topic in brand.seed_topics[:4]:
        signals += youtube_suggestions(topic)
    for sub in brand.subreddits:
        signals += reddit_questions(sub)
    return list(dict.fromkeys(s for s in signals if s))[:60]


# ---------------------------------------------------------------------------
IDEA_TEMPLATES = [
    ("The {t} mistake almost everyone makes", "Name one specific, common mistake and the fix", "short"),
    ("{t}: what nobody tells beginners", "Three counter-intuitive facts with a concrete example each", "carousel"),
    ("I compared 3 ways to handle {t}", "Side-by-side comparison with a clear winner and when it loses", "short"),
    ("{t} explained in 60 seconds", "One mental model that makes the whole topic click", "short"),
    ("A 5-step checklist for {t}", "Saveable checklist the viewer can act on today", "carousel"),
    ("The history of {t} in 8 minutes", "Story-driven explainer with surprising turning points", "long"),
    ("Is {t} worth it in 2026?", "Honest pros, cons and who it is not for", "short"),
    ("{t} myths, ranked", "Rank five myths from harmless to costly", "carousel"),
]


def _offline_ideas(brand: BrandProfile, n: int, signals: list[str], seed: int) -> IdeaBatch:
    rng = random.Random(seed)
    topics = (brand.seed_topics or [brand.niche]) + signals[:10]
    pillars = brand.pillars or [brand.niche]
    ideas = []
    for i in range(n):
        tpl, angle, fmt = IDEA_TEMPLATES[(seed + i) % len(IDEA_TEMPLATES)]
        if fmt not in brand.formats:
            fmt = brand.formats[i % len(brand.formats)]
        t = topics[rng.randrange(len(topics))]
        ideas.append(IdeaDraft(
            title=tpl.format(t=t)[:70], angle=angle, format=fmt,
            pillar=pillars[i % len(pillars)],
            hook=f"Most people get {t} wrong, and it costs them.",
            why_now=f"{brand.audience} keep asking about {t}.",
            monetization="affiliate" if brand.affiliates else ("product" if brand.products else "audience"),
            search_demand=rng.randint(4, 9), competition=rng.randint(3, 8), effort=rng.randint(2, 6),
        ))
    return IdeaBatch(ideas=ideas)


def score_idea(d: IdeaDraft, brand: BrandProfile) -> float:
    s = d.search_demand * 1.5 - d.competition * 1.0 - d.effort * 0.4
    if d.monetization in ("affiliate", "product") and (brand.affiliates or brand.products):
        s += 2.0
    if d.format in brand.formats:
        s += 0.5
    return round(s, 2)


def generate_ideas(db: DB, llm: LLM, brand: BrandProfile, n: int = 10, online: bool = True,
                   dedupe_threshold: float = 0.5) -> list[int]:
    from .insights import winners_prompt
    signals = gather_signals(brand, online=online)
    learned = winners_prompt(db, brand.slug)
    recent = db.query("SELECT title FROM ideas WHERE brand = ? ORDER BY id DESC LIMIT 300", [brand.slug])
    recent_titles = [r["title"] for r in recent]
    system = (
        "You are the editor of a niche content channel. You pitch specific, useful, original "
        "ideas that a real expert would be proud of. No clickbait that the content can't pay off, "
        "no reposting other creators, no real people's likeness, no medical or financial guarantees."
    )
    prompt = f"""Pitch {n} content ideas for this channel.

Channel: {brand.name}
Niche: {brand.niche}
Audience: {brand.audience}
Promise to viewers: {brand.promise}
Pillars: {', '.join(brand.pillars)}
Formats available: {', '.join(brand.formats)} (short = 30-60s vertical video, long = 6-12 min video, carousel = 6-10 slide image post)
Topics to avoid: {', '.join(brand.avoid_topics) or 'none'}
Monetization: affiliate offers [{', '.join(a.name for a in brand.affiliates) or 'none'}], products [{', '.join(p.get('name', '') for p in brand.products) or 'none'}]

What people are searching for right now (signals, may be noisy):
{chr(10).join('- ' + s for s in signals[:40]) or '- (no live signals)'}

Recent ideas already in the backlog (do NOT repeat or lightly reword these):
{chr(10).join('- ' + t for t in recent_titles[:60]) or '- (none yet)'}

{learned}

Each idea must have a distinct angle, not a template with the noun swapped."""
    seed = int(hashlib.sha1(f"{brand.slug}{len(recent_titles)}".encode()).hexdigest(), 16) % 10_000
    batch = llm.structured(IdeaBatch, system=system, prompt=prompt, purpose="ideas",
                           offline=lambda: _offline_ideas(brand, n, signals, seed))
    ids = []
    existing = [shingles(t, 2) for t in recent_titles]
    for d in batch.ideas:
        sh = shingles(d.title, 2)
        if any(jaccard(sh, e) >= dedupe_threshold for e in existing):
            continue
        existing.append(sh)
        ids.append(db.insert("ideas", {
            "brand": brand.slug, "title": d.title, "angle": d.angle, "format": d.format,
            "pillar": d.pillar, "score": score_idea(d, brand), "source": llm.provider,
            "meta": d.model_dump(),
        }))
    db.log("ideas.generated", "brand", None, {"brand": brand.slug, "count": len(ids)})
    return ids


def top_ideas(db: DB, brand: str, limit: int = 10, status: str = "new") -> list[dict]:
    return db.query("SELECT * FROM ideas WHERE brand = ? AND status = ? ORDER BY score DESC, id LIMIT ?",
                    [brand, status, limit])
