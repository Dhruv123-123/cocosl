"""Link-in-bio page, lead magnet and the small public pages around signup.

`build_link_page(settings, brand)` writes one self-contained HTML file to
output/<slug>/site/index.html (inline CSS, profile picture as a data URI) so
it can be hosted free on GitHub Pages / Netlify / Cloudflare Pages. The same
page is served live at /l/<brand> by `routes.public_router`.

The signup form posts to FUNNEL_PUBLIC_URL/subscribe/<brand>, so the static
copy works as long as the dashboard's public routes are reachable there.
"""
from __future__ import annotations

import base64
import io
import re
from functools import lru_cache
from pathlib import Path

import jinja2
from PIL import Image
from pydantic import BaseModel, Field

from ..config import BrandProfile, Settings
from ..db import DB, now_iso
from .mailer import public_url

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
AFFILIATE_NOTE = "Affiliate links: I may earn a commission if you buy through them, at no extra cost to you."
SOCIAL_URLS = {
    "instagram": "https://www.instagram.com/{h}/",
    "youtube": "https://www.youtube.com/@{h}",
    "tiktok": "https://www.tiktok.com/@{h}",
    "threads": "https://www.threads.net/@{h}",
    "facebook": "https://www.facebook.com/{h}",
}
SOCIAL_LABELS = {"instagram": "Instagram", "youtube": "YouTube", "tiktok": "TikTok", "threads": "Threads",
                 "facebook": "Facebook"}


@lru_cache(maxsize=1)
def public_env() -> jinja2.Environment:
    """Jinja env for the standalone public pages (no dashboard layout)."""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
                             autoescape=jinja2.select_autoescape(["html", "xml"]),
                             trim_blocks=True, lstrip_blocks=True)
    env.filters["sentence"] = lambda s: (s or "")[:1].upper() + (s or "")[1:]
    return env


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48].rstrip("-") or "link"


# ---------------------------------------------------------------- data
def theme(brand: BrandProfile) -> dict[str, str]:
    from ..brandkit.draw import Palette, contrast, mix, rgb_to_hex
    pal = Palette.from_hex(brand.visual.palette)
    btn_ink = pal.ink_on(pal.accent)
    return {
        "dark": rgb_to_hex(pal.dark), "light": rgb_to_hex(pal.light), "accent": rgb_to_hex(pal.accent),
        "accent2": rgb_to_hex(pal.accent2), "accent_ink": rgb_to_hex(btn_ink),
        "card": rgb_to_hex(mix(pal.dark, pal.light, 0.08)), "line": rgb_to_hex(mix(pal.dark, pal.light, 0.16)),
        "muted": rgb_to_hex(mix(pal.light, pal.dark, 0.35)),
        "accent_text": rgb_to_hex(pal.accent if contrast(pal.accent, pal.dark) >= 4.5 else pal.light),
    }


def avatar_data_uri(settings: Settings, brand: BrandProfile, size: int = 240) -> str:
    """Brand-kit profile picture as a small PNG data URI ('' if no kit yet)."""
    p = settings.output_dir / brand.slug / "brand-kit" / "profile-picture.png"
    if not p.exists():
        return ""
    with Image.open(p) as img:
        img = img.convert("RGB").resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def socials(brand: BrandProfile) -> list[dict]:
    out = []
    for a in brand.accounts:
        if not a.enabled or not a.handle or a.platform not in SOCIAL_URLS:
            continue
        h = a.handle.lstrip("@")
        out.append({"label": SOCIAL_LABELS[a.platform], "url": SOCIAL_URLS[a.platform].format(h=h)})
    return out


def latest_posts(db: DB, brand: str, limit: int = 6) -> list[dict]:
    rows = db.query(
        "SELECT p.title, pub.platform, pub.url, pub.published_at FROM publications pub "
        "JOIN posts p ON p.id = pub.post_id WHERE p.brand = ? AND pub.status = 'published' AND pub.url != '' "
        "ORDER BY COALESCE(pub.published_at, pub.created_at) DESC LIMIT ?", [brand, limit * 3])
    seen, out = set(), []
    for r in rows:  # one entry per post (prefer the most recent platform)
        if r["title"] in seen:
            continue
        seen.add(r["title"])
        out.append({"title": r["title"] or "Latest post", "url": r["url"],
                    "platform": SOCIAL_LABELS.get(r["platform"], r["platform"].title())})
        if len(out) >= limit:
            break
    return out


def _price(value) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value or "")
    if v == 0:
        return "Free"
    return f"${v:,.0f}" if v == int(v) else f"${v:,.2f}"


def products(db: DB, brand: BrandProfile, *, settings: Settings | None = None, base_url: str | None = None,
             utm: dict | None = None) -> list[dict]:
    """Brand YAML products plus listed products from the business `products` table.

    Each entry: {name, url (checkout), price, slug, page_url, raw}. page_url is
    the sales page (/p/<brand>/<slug>) with UTM params from `utm`
    ({source, medium, campaign}; campaign defaults to the product slug)."""
    from .attribution import with_utm
    from .brandfunnel import launch_state
    from .salespage import _overrides, product_slug
    base = (base_url or public_url(settings)).rstrip("/")
    utm = utm or {}
    raw: list[dict] = []
    urls: set[str] = set()
    for p in brand.products:
        if p.get("url") and p["url"] not in urls:
            urls.add(p["url"])
            raw.append(dict(p))
    try:
        rows = db.query("SELECT name, url, price_cents FROM products WHERE brand = ? AND status = 'listed' "
                        "AND url != '' ORDER BY id DESC", [brand.slug])
    except Exception:
        rows = []
    for r in rows:
        if r["url"] not in urls:
            urls.add(r["url"])
            raw.append({"name": r["name"], "url": r["url"], "price": (r["price_cents"] or 0) / 100})
    out = []
    for p in raw:
        slug = product_slug(settings, brand, p)
        page = with_utm(f"{base}/p/{brand.slug}/{slug}", utm.get("source", ""), utm.get("medium", ""),
                        utm.get("campaign", "") or (slug if utm else ""))
        o = _overrides(settings, brand, p)
        price = str(o.get("price") or _price(p.get("price")))
        launch = launch_state({**o, "price": price})
        out.append({"name": o.get("name") or p.get("name", "Product"), "url": p["url"],
                    "price": launch["launch_price"] if launch["active"] else price,
                    "regular_price": price if launch["active"] else "",
                    "slug": slug, "page_url": page, "raw": p})
    return out


def sync_affiliate_links(db: DB, brand: BrandProfile) -> list[dict]:
    """Make sure each brand affiliate has a tracked /go/<slug> row (idempotent)."""
    out = []
    for a in brand.affiliates:
        slug = a.slug or slugify(a.name)
        db.execute("INSERT OR IGNORE INTO affiliate_links (brand, name, slug, url, commission, created_at) "
                   "VALUES (?, ?, ?, ?, ?, ?)", [brand.slug, a.name, slug, a.url, a.commission, now_iso()])
        out.append({"name": a.name, "slug": slug})
    return out


def lead_magnet(brand: BrandProfile, settings: Settings | None = None) -> dict:
    """The freebie offered at signup: the `lead_magnet` in the brand's funnel
    file (brands/sequences/<brand>.yaml) if there is one, else a free product
    the brand lists, else a starter checklist generated from the pillars."""
    from .brandfunnel import load_funnel
    cfg = load_funnel(settings, brand.slug)
    lm = cfg.get("lead_magnet") or {}
    welcome = " Then a short welcome series and one useful email a week." if cfg.get("steps") else ""
    if lm.get("title"):
        return {"kind": "checklist" if not lm.get("url") else "product", "title": lm["title"],
                "url": lm.get("url", ""), "pitch": lm.get("pitch") or f"Get {lm['title']} free when you join.",
                "after": welcome or " One useful email a week."}
    free = next((p for p in brand.products if _price(p.get("price")) == "Free" and p.get("url")), None)
    if free:
        return {"kind": "product", "title": free.get("name", "Free download"), "url": free["url"],
                "pitch": f"Get {free.get('name', 'the free download')} when you join.",
                "after": welcome or " One useful email a week."}
    title = f"The {brand.name} Starter Checklist"
    return {"kind": "checklist", "title": title, "url": "",
            "pitch": "A free one-page checklist to get you started, sent when you join the weekly email.",
            "after": welcome or " One useful email a week."}


class ChecklistSection(BaseModel):
    heading: str = Field(description="Section title, under 50 characters")
    items: list[str] = Field(description="3-4 concrete, checkable actions, each under 110 characters")


class Checklist(BaseModel):
    sections: list[ChecklistSection]


def offline_checklist(brand: BrandProfile) -> Checklist:
    """One section per pillar with three concrete starter actions."""
    sections = []
    topics = list(brand.seed_topics)
    for i, pillar in enumerate(brand.pillars or [brand.niche]):
        topic = topics[i % len(topics)] if topics else pillar
        short = pillar.split("(")[0].strip()
        sections.append(ChecklistSection(heading=short[:1].upper() + short[1:], items=[
            f"Find one beginner explainer on \u201c{topic}\u201d and write down the single takeaway.",
            f"Pick the one part of {short.lower()} that would help you most this month.",
            "Turn it into one 15-minute action and put it in your calendar this week.",
            "Check it off, then reply to the weekly email and tell us how it went.",
        ]))
    return Checklist(sections=sections)


def lead_magnet_path(settings: Settings, brand: BrandProfile) -> Path:
    return settings.output_dir / brand.slug / "site" / "lead-magnet.json"


def ensure_lead_magnet(settings: Settings, brand: BrandProfile, llm=None, *, refresh: bool = False) -> Checklist:
    """Write the checklist lead magnet once (LLM when available, offline
    fallback otherwise) and cache it next to the link page."""
    from .brandfunnel import load_funnel
    sections = (load_funnel(settings, brand.slug).get("lead_magnet") or {}).get("sections")
    if sections:  # hand-written checklist in the funnel file wins (no LLM, no cache)
        return Checklist.model_validate({"sections": sections})
    path = lead_magnet_path(settings, brand)
    if path.exists() and not refresh:
        try:
            return Checklist.model_validate_json(path.read_text())
        except ValueError:
            pass
    if llm is None:
        checklist = offline_checklist(brand)
    else:
        checklist = llm.structured(
            Checklist, purpose="funnel.lead_magnet", max_tokens=3000,
            system=("You write a one-page starter checklist that a small creator brand gives away for an email "
                    "signup. Practical, specific, safe general information; no promises of results, no "
                    "personalised professional advice."),
            prompt=(f"Brand: {brand.name}. Niche: {brand.niche}. Audience: {brand.audience}. "
                    f"Promise: {brand.promise}. Pillars: {'; '.join(brand.pillars)}. Tone: {brand.voice.tone}. "
                    "One section per pillar, 3-4 checkable actions each."),
            offline=lambda: offline_checklist(brand))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(checklist.model_dump_json(indent=2))
    return checklist


# ---------------------------------------------------------------- render
def link_page_context(settings: Settings, db: DB, brand: BrandProfile, base_url: str | None = None) -> dict:
    base = (base_url or public_url(settings)).rstrip("/")
    from .attribution import with_utm
    affiliates = sync_affiliate_links(db, brand)
    utm = {"source": "linkpage", "medium": "bio"}
    return {
        "brand": brand, "t": theme(brand), "avatar": avatar_data_uri(settings, brand),
        "initials": _initials(brand.name), "socials": socials(brand), "posts": latest_posts(db, brand.slug),
        "products": products(db, brand, settings=settings, base_url=base, utm=utm),
        "affiliates": [{"name": a["name"], "url": with_utm(f"{base}/go/{a['slug']}?s=linkpage", campaign=a["slug"],
                                                           **utm)} for a in affiliates],
        "affiliate_note": AFFILIATE_NOTE, "magnet": lead_magnet(brand, settings),
        "subscribe_url": f"{base}/subscribe/{brand.slug}", "base": base, "year": now_iso()[:4],
    }


def _initials(name: str) -> str:
    from ..brandkit.draw import initials
    return initials(name)


def render_link_page(settings: Settings, db: DB, brand: BrandProfile, base_url: str | None = None) -> str:
    return public_env().get_template("link_page.html").render(**link_page_context(settings, db, brand, base_url))


def build_link_page(settings: Settings, brand: BrandProfile, db: DB | None = None,
                    base_url: str | None = None, llm=None) -> Path:
    """Write output/<slug>/site/index.html (and the cached lead magnet
    checklist) and return the page path."""
    if lead_magnet(brand, settings)["kind"] == "checklist":
        ensure_lead_magnet(settings, brand, llm)
    own = db is None
    db = db or DB(settings.db_path)
    try:
        page = render_link_page(settings, db, brand, base_url)
    finally:
        if own:
            db.conn.close()
    out = settings.output_dir / brand.slug / "site" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return out


def render_message(brand: BrandProfile | None, title: str, body: str, *, button: tuple[str, str] | None = None,
                   status: str = "ok", extra_html: str = "") -> str:
    """A small standalone page (check your inbox / confirmed / unsubscribed)."""
    t = theme(brand) if brand else None
    return public_env().get_template("message.html").render(
        brand=brand, t=t, title=title, body=body, button=button, status=status, extra_html=extra_html)


def render_checklist(settings: Settings, brand: BrandProfile, llm=None) -> str:
    checklist = ensure_lead_magnet(settings, brand, llm)
    return public_env().get_template("freebie.html").render(
        brand=brand, t=theme(brand), magnet=lead_magnet(brand, settings), sections=[s.model_dump() for s in checklist.sections])
