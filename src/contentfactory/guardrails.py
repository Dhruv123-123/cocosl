"""Compliance and quality checks that run before anything reaches the review queue.

These encode the rules from the research report: platforms punish repetitive
mass-produced content, undisclosed realistic AI, fake testimonials, missing
ad/affiliate disclosure and reposted third-party media. Each check returns a
`Check` with a level: `block` stops the post, `warn` shows in review, `ok` passes.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from . import i18n
from .config import BrandProfile
from .db import DB


@dataclass
class Check:
    name: str
    level: str  # ok | warn | block
    message: str

    def as_dict(self) -> dict:
        return asdict(self)


# A testimonial is a first-person claim of having used/benefited from a product.
# For an AI presenter this is a fake review under the FTC rule (16 CFR 465).
TESTIMONIAL_PATTERNS = [
    r"\bI(?:'ve| have)? (?:been )?(?:using|tried|tested|bought|ordered)\b",
    r"\bchanged my life\b",
    r"\bmy (?:skin|hair|results|wife|husband|kids?) (?:loves?|got|is|are)\b",
    r"\bI lost \d+",
    r"\bI (?:love|swear by|can't live without) (?:this|it)\b",
    r"\bas a (?:real|verified) (?:customer|buyer)\b",
    # Spanish
    r"\b(?:yo )?(?:lo |la )?(?:he|llevo|estoy) (?:usado|usando|probado|probando|comprado|pedido)\b",
    r"\b(?:lo|la) (?:us[eé]|prob[eé]|compr[eé])\b",
    r"\bme cambi[oó] la vida\b",
    r"\bbaj[eé] \d+ ?(?:kilos|libras|lbs?)\b",
    r"\b(?:me encanta|no puedo vivir sin) (?:esto|este|esta|él|ella)\b",
    r"\bcomo (?:cliente|comprador)a? (?:real|verificad[oa])\b",
]

HYPE_PATTERNS = [
    r"\bguarantee[sd]?\b", r"\b100% (?:safe|free|guaranteed)\b", r"\bget rich\b",
    r"\bpassive income (?:for life|forever)\b", r"\bcures?\b", r"\brisk[- ]free\b",
    r"\bmake \$\d[\d,]* (?:a|per) (?:day|week)\b", r"\bdoctors hate\b",
    # Spanish
    r"\bgarantizad[oa]s?\b", r"\bte lo garantizo\b", r"\bhazte rico\b", r"\bhacerte rico\b",
    r"\bdinero f[aá]cil\b", r"\bsin riesgo\b", r"\bingresos pasivos de por vida\b",
    r"\bgana \$\d[\d,]* (?:al|por) (?:d[ií]a|semana)\b", r"\bcura (?:la|el|tu)\b",
]

ENGAGEMENT_BAIT = [
    r"\blike (?:and|&) share or\b", r"\bcomment ['\"]?\w+['\"]? (?:and|to) (?:get|receive)\b.*\bDM\b",
    r"\btag \d+ friends\b", r"\bfollow (?:for|4) follow\b",
    # Spanish
    r"\betiqueta a \d+ amig[oa]s\b", r"\bdale like y comparte o\b", r"\bsigo a quien me siga\b",
    r"\bcomenta ['\"]?\w+['\"]? (?:y|para) (?:recibir|que te)\b.*\b(?:DM|mensaje)\b",
]

AFFILIATE_DISCLOSURE = re.compile(
    r"(#ad\b|#affiliate|affiliate link|paid partnership|I may earn|commission"
    r"|#publicidad|#afiliado|enlace de afiliado|enlaces? de afiliados?|colaboraci[oó]n pagada|comisi[oó]n)", re.I)
AI_DISCLOSURE = re.compile(
    r"(AI[- ](?:generated|assisted|made|tools)|made with AI|#aigenerated|#ai\b"
    r"|(?:hech[oa]s?|cread[oa]s?|generad[oa]s?) con (?:ayuda de )?(?:la )?IA|herramientas de IA|#hechoconia|#ia\b)",
    re.I)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:'[^\W_]+)*", text.lower())


def shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    toks = _tokens(text)
    return {tuple(toks[i:i + n]) for i in range(max(0, len(toks) - n + 1))}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def script_text(script: dict) -> str:
    parts = [script.get("title", ""), script.get("hook", "")]
    for seg in script.get("segments", []):
        parts += [seg.get("narration", ""), seg.get("on_screen_text", "")]
    parts.append(script.get("cta", ""))
    return " ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
def check_originality(db: DB, brand: str, text: str, exclude_post_id: int | None = None,
                      warn_at: float = 0.35, block_at: float = 0.6) -> Check:
    """Compare against this brand's last 200 posts. YouTube's 'inauthentic
    content' rule targets videos with only superficial differences."""
    rows = db.query(
        "SELECT id, script FROM posts WHERE brand = ? AND id != ? AND status != 'rejected' ORDER BY id DESC LIMIT 200",
        [brand, exclude_post_id or -1],
    )
    mine = shingles(text)
    worst, worst_id = 0.0, None
    for r in rows:
        other = r["script"] if isinstance(r["script"], dict) else {}
        sim = jaccard(mine, shingles(script_text(other)))
        if sim > worst:
            worst, worst_id = sim, r["id"]
    if worst >= block_at:
        return Check("originality", "block", f"{worst:.0%} overlap with post #{worst_id}; too repetitive to publish")
    if worst >= warn_at:
        return Check("originality", "warn", f"{worst:.0%} overlap with post #{worst_id}; make it more distinct")
    return Check("originality", "ok", f"Max overlap {worst:.0%}")


def check_patterns(text: str, patterns: list[str], name: str, level: str, label: str) -> Check:
    hits = sorted({m.group(0) for p in patterns for m in re.finditer(p, text, re.I)})
    if hits:
        return Check(name, level, f"{label}: " + ", ".join(f'"{h}"' for h in hits[:5]))
    return Check(name, "ok", f"No {label.lower()}")


def check_disclosures(brand: BrandProfile, caption: str, disclosure: str, has_affiliate: bool) -> list[Check]:
    out = []
    full = f"{caption}\n{disclosure}"
    if brand.realistic_synthetic_media and not AI_DISCLOSURE.search(full):
        out.append(Check("ai_label", "block",
                         "Realistic synthetic media must carry an AI label (YouTube, TikTok, Meta, EU AI Act Art. 50)"))
    elif not AI_DISCLOSURE.search(full):
        out.append(Check("ai_label", "warn", "No AI disclosure in caption; the platform AI-label toggle will still be set"))
    else:
        out.append(Check("ai_label", "ok", "AI disclosure present"))
    if has_affiliate and not AFFILIATE_DISCLOSURE.search(full):
        out.append(Check("affiliate_disclosure", "block", "Affiliate link without a clear disclosure (FTC Endorsement Guides)"))
    elif has_affiliate:
        out.append(Check("affiliate_disclosure", "ok", "Affiliate disclosure present"))
    return out


def check_banned(brand: BrandProfile, text: str) -> Check:
    low = text.lower()
    hits = [p for p in brand.voice.banned_phrases if p.lower() in low]
    hits += [t for t in brand.avoid_topics if t.lower() in low]
    if hits:
        return Check("brand_rules", "warn", "Uses avoided phrases/topics: " + ", ".join(hits[:5]))
    return Check("brand_rules", "ok", "Follows brand rules")


def check_language_review(brand: BrandProfile, post: dict) -> Check | None:
    """Non-English copy is machine-written in a language the operator may not read:
    a fluent speaker must sign it off (meta.native_review = their name) before it goes out."""
    if i18n.is_english(brand):
        return None
    meta = post.get("meta") or {}
    reviewer = str(meta.get("native_review") or "").strip()
    if reviewer:
        return Check("language_review", "ok", f"{i18n.locale_of(brand)} copy reviewed by {reviewer}")
    return Check("language_review", "warn",
                 f"{i18n.locale_of(brand)} copy needs a native-speaker review before posting "
                 "(record it with `factory review-language <id> --by NAME`)")


def check_assets_licensed(assets: dict) -> Check:
    """Every media file must be generated by us or have a recorded licence."""
    unlicensed = [a.get("path", "?") for a in assets.get("provenance", [])
                  if a.get("source") not in ("generated", "own", "licensed", "rendered")]
    if unlicensed:
        return Check("asset_rights", "block", f"Assets without recorded rights: {', '.join(unlicensed[:3])}")
    return Check("asset_rights", "ok", "All assets generated or licensed")


NO_REPOST_PLATFORMS = ("instagram",)
_ON_PLATFORM = ("queued", "publishing", "published", "needs_check", "manual")


def _media_fingerprint(assets: dict, output_dir) -> str:
    """sha1 of the post's main media file (video, else first slide), '' if there's none on disk."""
    import hashlib
    from pathlib import Path
    rel = assets.get("video") or next(iter(assets.get("slides") or []), None)
    if not rel or output_dir is None:
        return ""
    path = Path(output_dir) / rel
    if not path.is_file():
        return ""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_no_repost(db: DB, post: dict, platform: str, exclude_pub_id: int | None = None,
                    output_dir=None, block_at: float = 0.6) -> Check:
    """Instagram stops recommending accounts that repost (Apr 2026, now photos and carousels too).
    Blocks a second Instagram publication of the same post, the same media file posted by any of our
    accounts, or a script that's a near-copy of one already on Instagram (any brand)."""
    if platform not in NO_REPOST_PLATFORMS:
        return Check("no_repost", "ok", f"{platform}: no repost rule")
    marks = ",".join("?" * len(_ON_PLATFORM))
    same = db.query(f"SELECT id, status FROM publications WHERE post_id = ? AND platform = ? AND id != ? "
                    f"AND status IN ({marks})", [post["id"], platform, exclude_pub_id or -1, *_ON_PLATFORM])
    if same:
        return Check("no_repost", "block", f"post #{post['id']} is already on {platform} "
                     f"(publication #{same[0]['id']}, {same[0]['status']}); Instagram penalises reposts")
    others = db.query(f"""SELECT DISTINCT s.id, s.brand, s.script, s.assets FROM posts s JOIN publications p ON p.post_id = s.id
                          WHERE p.platform = ? AND s.id != ? AND p.status IN ({marks})
                          ORDER BY s.id DESC LIMIT 500""", [platform, post["id"], *_ON_PLATFORM])
    fp = _media_fingerprint(post.get("assets") or {}, output_dir)
    mine = shingles(script_text(post.get("script") or {}))
    for o in others:
        if fp and _media_fingerprint(o["assets"] or {}, output_dir) == fp:
            return Check("no_repost", "block", f"same media file as post #{o['id']} ({o['brand']}), already on "
                         f"{platform}; make a new cut instead of reposting")
        if mine and jaccard(mine, shingles(script_text(o["script"] if isinstance(o["script"], dict) else {}))) >= block_at:
            return Check("no_repost", "block", f"near-copy of post #{o['id']} ({o['brand']}), already on {platform}; "
                         "Instagram treats that as a repost")
    return Check("no_repost", "ok", "original on Instagram")


def check_cadence(db: DB, brand: BrandProfile, platform: str, when: datetime) -> Check:
    """Keep posting volume human-scale. Floods of near-identical uploads are
    exactly what spam classifiers look for. Days are the brand's local days,
    the same days the scheduler fills."""
    from zoneinfo import ZoneInfo
    try:
        tz = ZoneInfo(brand.cadence.timezone)
    except Exception:
        tz = timezone.utc
    local = when.astimezone(tz)
    day_start = local.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = (day_start + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    n = db.scalar(
        """SELECT COUNT(*) FROM publications p JOIN posts s ON s.id = p.post_id
           WHERE s.brand = ? AND p.platform = ?
           AND p.status IN ('queued','publishing','published','dry_run','needs_check','manual')
           AND p.scheduled_at >= ? AND p.scheduled_at < ?""",
        [brand.slug, platform, day_start.astimezone(timezone.utc).isoformat(),
         day_end.astimezone(timezone.utc).isoformat()],
    ) or 0
    cap = brand.cadence.max_posts_per_day_per_platform
    if n >= cap:
        return Check("cadence", "block", f"Already {n} posts on {platform} that day (cap {cap})")
    return Check("cadence", "ok", f"{n}/{cap} posts on {platform} that day")


def _shape(text: str, words: int = 3) -> str:
    """'7 Ways to Save $500' -> '# ways to': the template, not the topic."""
    toks = re.sub(r"\d[\d,.$%]*", "#", (text or "").lower()).split()
    return " ".join(toks[:words])


def structure(post: dict) -> dict:
    script = post.get("script") or {}
    segs = script.get("segments") or []
    look = (post.get("assets") or {}).get("look") or {}
    meta = post.get("meta") or {}
    return {"format": post.get("format", ""), "beats": min(len(segs), 12) // 2,
            "title": _shape(script.get("title") or post.get("title", "")), "hook": _shape(script.get("hook", ""), 4),
            "hook_template": str(meta.get("hook_template") or meta.get("hook_id") or ""),
            "look": "|".join(str(look.get(k, "")) for k in sorted(look))}


def check_sameness(db: DB, brand: str, post: dict, window: int = 20, min_history: int = 6) -> Check:
    """Channel-level sameness: does this post share its *structure* (format, beat count, title and hook
    pattern, hook template, visual look) with more than half of the brand's recent posts? The text
    originality check can't see this: two scripts with no shared sentences can still be the same video."""
    rows = db.query("SELECT id, format, title, script, assets, meta FROM posts WHERE brand = ? AND id != ? "
                    "AND status != 'rejected' AND format = ? ORDER BY id DESC LIMIT ?",
                    [brand, post.get("id") or -1, post.get("format", ""), window])
    if len(rows) < min_history:
        return Check("sameness", "ok", f"only {len(rows)} earlier {post.get('format')} post(s) to compare")
    mine = structure(post)
    keys = [k for k in mine if k != "format" and mine[k] not in ("", "|")]
    alike = 0
    for r in rows:
        other = structure(r)
        if sum(mine[k] == other[k] for k in keys) >= max(2, len(keys) - 2):
            alike += 1
    if alike * 2 > len(rows):
        same = [k for k in keys if sum(mine[k] == structure(r)[k] for r in rows) * 2 > len(rows)]
        return Check("sameness", "warn", f"Built like {alike} of the last {len(rows)} {post.get('format')} posts "
                     f"(same {', '.join(same) or 'structure'}). YouTube reviews whole channels for repetitive "
                     "videos: change the opening, the title pattern or the number of beats")
    return Check("sameness", "ok", f"structure differs from most recent posts ({alike}/{len(rows)} alike)")


def check_original_element(post: dict) -> Check | None:
    """Long videos need one thing a template can't make (YouTube judges whole channels for
    'inauthentic content': slideshows with the same narration). A chart drawn from the video's own
    numbers or the person's own footage counts; a planned element only counts once it's in the video."""
    if post.get("format") != "long":
        return None
    script = post.get("script") or {}
    segs = script.get("segments") or []
    footage = [s for s in segs if (s.get("footage") or "").strip()]
    charts = [s for s in segs if s.get("chart")]
    if footage:
        return Check("original_element", "ok", f"{len(footage)} beat(s) with your own footage")
    if charts:
        return Check("original_element", "ok", f"{len(charts)} chart(s) drawn from this video's numbers")
    from .originality import element_text
    planned = element_text(script.get("original_element"))
    if planned:
        return Check("original_element", "block", f"Planned original element not in the video yet: {planned[:160]}. "
                     "Add the footage to a beat (or a chart), then re-render")
    return Check("original_element", "block", "Long video with nothing a template can't make: add a chart with "
                 "this video's own numbers or a beat with your own screen recording")


def run_content_checks(db: DB, brand: BrandProfile, post: dict) -> list[Check]:
    script = post.get("script") or {}
    text = script_text(script)
    caption = post.get("caption", "")
    everything = f"{text}\n{caption}"
    has_affiliate = bool(post.get("meta", {}).get("affiliate_slugs")) or any(
        a.url in caption for a in brand.affiliates)
    checks = [
        check_originality(db, brand.slug, text, exclude_post_id=post.get("id")),
        check_patterns(everything, TESTIMONIAL_PATTERNS, "fake_testimonial",
                       "block" if post.get("meta", {}).get("ai_presenter") else "warn",
                       "First-person product claims"),
        check_patterns(everything, HYPE_PATTERNS, "claims", "warn", "Risky claims"),
        check_patterns(everything, ENGAGEMENT_BAIT, "engagement_bait", "warn", "Engagement bait"),
        check_banned(brand, everything),
        *check_disclosures(brand, caption, post.get("disclosure", ""), has_affiliate),
    ]
    lang_check = check_language_review(brand, post)
    if lang_check:
        checks.append(lang_check)
    if post.get("assets"):
        checks.append(check_assets_licensed(post["assets"]))
    checks.append(check_sameness(db, brand.slug, post))
    if (orig := check_original_element(post)) is not None:
        checks.append(orig)
    from .numbercheck import as_check, check_script
    if (nums := as_check(check_script(script, caption))) is not None:
        checks.append(nums)
    unverified = script.get("claims_to_verify") or []
    if unverified:
        checks.append(Check("fact_check", "warn", f"{len(unverified)} claim(s) need a human fact-check"))
    return checks


def summarize(checks: list[Check]) -> dict:
    levels = [c.level for c in checks]
    status = "block" if "block" in levels else "warn" if "warn" in levels else "ok"
    return {"status": status, "checks": [c.as_dict() for c in checks]}
