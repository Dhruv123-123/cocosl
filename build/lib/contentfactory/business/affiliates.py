"""Affiliate link registry, tracked /go/{slug} redirects and disclosure helper.

Tracked links look like `{FACTORY_LINK_BASE_URL}/go/{slug}?p={post_id}&s={platform}`.
The redirect counts the click, logs post/platform for attribution and appends
UTM parameters (never overriding ones already on the merchant URL).
"""
from __future__ import annotations

import os
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..config import BrandProfile
from ..db import DB
from ..guardrails import AFFILIATE_DISCLOSURE
from ._util import slugify

DEFAULT_DISCLOSURE = ("Disclosure: this post contains an affiliate link. If you buy through it we may earn a "
                      "commission, at no extra cost to you. #ad")
TRACKED_RE = re.compile(r"/go/([a-z0-9][a-z0-9_-]*)", re.I)


def add_link(db: DB, name: str, url: str, slug: str = "", brand: str = "", commission: str = "") -> int:
    """Create or update a link by slug. Returns its id."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("Affiliate URL must start with http:// or https://")
    slug = slugify(slug or name, 40)
    existing = db.one("SELECT * FROM affiliate_links WHERE slug = ?", [slug])
    if existing:
        db.update("affiliate_links", existing["id"], {"name": name, "url": url, "brand": brand or existing["brand"],
                                                      "commission": commission or existing["commission"]})
        return existing["id"]
    return db.insert("affiliate_links", {"name": name, "slug": slug, "url": url, "brand": brand,
                                         "commission": commission})


def sync_from_brands(db: DB, brands: dict[str, BrandProfile]) -> dict:
    """Upsert every `affiliates:` entry from the brand YAMLs. Click counts are kept."""
    added, updated = [], []
    for brand in brands.values():
        for offer in brand.affiliates:
            slug = slugify(offer.slug or offer.name, 40)
            before = db.one("SELECT id FROM affiliate_links WHERE slug = ?", [slug])
            add_link(db, offer.name, offer.url, slug=slug, brand=brand.slug, commission=offer.commission)
            (updated if before else added).append(slug)
    if added or updated:
        db.log("affiliates.synced", "affiliate_links", None, {"added": added, "updated": updated})
    return {"added": added, "updated": updated}


def links(db: DB, brand: str | None = None) -> list[dict]:
    if brand:
        return db.query("SELECT * FROM affiliate_links WHERE brand = ? ORDER BY clicks DESC, slug", [brand])
    return db.query("SELECT * FROM affiliate_links ORDER BY clicks DESC, slug")


def link_base_url() -> str:
    return os.environ.get("FACTORY_LINK_BASE_URL", "").rstrip("/")


def tracked_url(slug: str, post_id: int | None = None, platform: str = "", base: str | None = None) -> str:
    """Public short link for captions/bios, e.g. https://links.example.com/go/hysa?p=12&s=instagram."""
    base = link_base_url() if base is None else base.rstrip("/")
    params = {k: v for k, v in (("p", post_id), ("s", platform)) if v}
    return f"{base}/go/{slug}" + (f"?{urlencode(params)}" if params else "")


def with_utm(url: str, **utm: str) -> str:
    """Append utm_* params that aren't already on the URL."""
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    present = {k for k, _ in query}
    query += [(f"utm_{k}", v) for k, v in utm.items() if v and f"utm_{k}" not in present]
    return urlunsplit(parts._replace(query=urlencode(query)))


def resolve_click(db: DB, slug: str, post_id: int | str | None = None, platform: str = "",
                  utm: dict | None = None) -> str | None:
    """Count a click and return the destination URL with UTM params, or None if unknown."""
    link = db.one("SELECT * FROM affiliate_links WHERE slug = ?", [slug.lower()])
    if not link:
        return None
    db.execute("UPDATE affiliate_links SET clicks = clicks + 1 WHERE id = ?", [link["id"]])
    pid = int(post_id) if str(post_id or "").isdigit() else None
    platform = re.sub(r"[^a-z0-9_-]", "", (platform or "").lower())[:20]
    db.log("affiliate.click", "affiliate_link", link["id"], {"slug": slug, "post_id": pid, "platform": platform})
    clean = lambda v: re.sub(r"[^A-Za-z0-9_.-]", "", str(v or ""))[:60]  # noqa: E731
    utm = {k.removeprefix("utm_"): clean(v) for k, v in (utm or {}).items() if clean(v)}
    params = {"source": platform or link["brand"] or "contentfactory", "medium": "social",
              "campaign": link["slug"], "content": f"post-{pid}" if pid else ""}
    params.update({k: v for k, v in utm.items() if k in params or k == "term"})
    return with_utm(link["url"], **params)


def clicks_by_post(db: DB, slug: str | None = None) -> list[dict]:
    """Click counts per (post, platform) from the click log."""
    rows = db.query("SELECT detail FROM audit_log WHERE action = 'affiliate.click'")
    counts: dict[tuple, int] = {}
    for r in rows:
        d = r["detail"] if isinstance(r["detail"], dict) else {}
        if slug and d.get("slug") != slug:
            continue
        key = (d.get("slug"), d.get("post_id"), d.get("platform") or "")
        counts[key] = counts.get(key, 0) + 1
    return [{"slug": s, "post_id": p, "platform": pl, "clicks": n}
            for (s, p, pl), n in sorted(counts.items(), key=lambda kv: -kv[1])]


def has_affiliate_link(text: str, known_urls: list[str] | None = None) -> bool:
    if TRACKED_RE.search(text or ""):
        return True
    return any(u and u in (text or "") for u in (known_urls or []))


def ensure_disclosure(caption: str, known_urls: list[str] | None = None,
                      disclosure: str = DEFAULT_DISCLOSURE) -> str:
    """Append a clear affiliate disclosure when the caption has a tracked/affiliate
    link and no disclosure yet (FTC Endorsement Guides). Otherwise unchanged."""
    caption = caption or ""
    if not has_affiliate_link(caption, known_urls) or AFFILIATE_DISCLOSURE.search(caption):
        return caption
    return f"{caption.rstrip()}\n\n{disclosure}"
