"""UTM tagging and revenue attribution.

Outbound links from the link page, sales pages and emails get
utm_source / utm_medium / utm_campaign (never overriding values already on
the URL). Stripe Payment Links don't copy query params into the checkout
session, so for buy.stripe.com links the same three values also go into
`client_reference_id` (allowed: letters, digits, `-`, `_`; max 200 chars),
which Stripe does put on `checkout.session.completed`.

Webhooks store whatever UTM they find (Stripe metadata / client_reference_id,
Gumroad url_params) at the end of revenue.note as
`| utm_source=.. utm_medium=.. utm_campaign=..`, and `revenue_by_campaign`
reads it back. No new tables or columns.
"""
from __future__ import annotations

import json
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..db import DB

UTM_KEYS = ("source", "medium", "campaign", "content")
_CLEAN = re.compile(r"[^A-Za-z0-9_.-]+")
REF_SEP = "__"
NOTE_RE = re.compile(r"utm_(source|medium|campaign|content)=(\S+)")


def clean(value: str, limit: int = 60) -> str:
    return _CLEAN.sub("-", str(value or "").strip()).strip("-")[:limit]


def with_utm(url: str, source: str = "", medium: str = "", campaign: str = "", content: str = "") -> str:
    """Append utm_* params that aren't already on the URL. Non-http URLs are returned unchanged."""
    if not url or not url.startswith(("http://", "https://")):
        return url
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    present = {k for k, _ in query}
    values = {"source": source, "medium": medium, "campaign": campaign, "content": content}
    query += [(f"utm_{k}", clean(v)) for k, v in values.items() if v and f"utm_{k}" not in present]
    return urlunsplit(parts._replace(query=urlencode(query)))


def is_stripe_link(url: str) -> bool:
    host = urlsplit(url or "").netloc.lower()
    return host == "buy.stripe.com" or host.endswith(".buy.stripe.com")


def is_gumroad_link(url: str) -> bool:
    host = urlsplit(url or "").netloc.lower()
    return host == "gumroad.com" or host.endswith(".gumroad.com") or host == "gum.co"


def client_reference(source: str = "", medium: str = "", campaign: str = "") -> str:
    """`email__sequence__welcome-d6`: Stripe-safe encoding of the three UTM values."""
    parts = [re.sub(r"[^A-Za-z0-9-]+", "-", clean(v, 60)).strip("-") or "na" for v in (source, medium, campaign)]
    return REF_SEP.join(parts)[:200]


def parse_client_reference(ref: str) -> dict:
    parts = str(ref or "").split(REF_SEP)
    if len(parts) != 3:
        return {}
    return {f"utm_{k}": v for k, v in zip(("source", "medium", "campaign"), parts) if v and v != "na"}


def tag_link(url: str, source: str = "", medium: str = "", campaign: str = "", content: str = "") -> str:
    """with_utm, plus client_reference_id on Stripe Payment Links (if not set already)."""
    out = with_utm(url, source, medium, campaign, content)
    if is_stripe_link(out) and "client_reference_id=" not in out and (source or medium or campaign):
        sep = "&" if urlsplit(out).query else "?"
        out += sep + urlencode({"client_reference_id": client_reference(source, medium, campaign)})
    return out


def utm_from_query(query: dict) -> dict:
    """utm_* values from request query params (cleaned, only known keys)."""
    return {f"utm_{k}": clean(query.get(f"utm_{k}", "")) for k in UTM_KEYS if clean(query.get(f"utm_{k}", ""))}


def utm_from_mapping(data) -> dict:
    """Find utm_* values in a dict that may be flat (`utm_source`), nested
    (`url_params: {utm_source}`), a JSON string, or form-style
    (`url_params[utm_source]`)."""
    found: dict[str, str] = {}

    def visit(obj, depth=0):
        if depth > 3 or obj is None:
            return
        if isinstance(obj, str):
            s = obj.strip()
            if s.startswith("{"):
                try:
                    visit(json.loads(s), depth + 1)
                except ValueError:
                    pass
            elif "utm_" in s and "=" in s:
                visit(dict(parse_qsl(s.lstrip("?"))), depth + 1)
            return
        if not isinstance(obj, dict):
            return
        for k, v in obj.items():
            key = str(k)
            m = re.search(r"utm_(source|medium|campaign|content)\]?$", key)
            if m and isinstance(v, (str, int)) and clean(str(v)):
                found.setdefault(f"utm_{m.group(1)}", clean(str(v)))
            elif isinstance(v, (dict, str)) and key not in ("utm_source", "utm_medium", "utm_campaign"):
                visit(v, depth + 1)

    visit(data)
    return found


def note_suffix(utm: dict) -> str:
    """' | utm_source=a utm_medium=b utm_campaign=c' (empty when no UTM)."""
    bits = [f"utm_{k}={clean(utm[f'utm_{k}'])}" for k in UTM_KEYS if utm.get(f"utm_{k}")]
    return (" | " + " ".join(bits)) if bits else ""


def parse_note(note: str) -> dict:
    return {f"utm_{k}": v for k, v in NOTE_RE.findall(note or "")}


def revenue_by_campaign(db: DB, brand: str | None = None, since: str | None = None) -> list[dict]:
    """[{brand, campaign, source, medium, sales, revenue_cents}] for product and
    affiliate revenue, grouped by (brand, utm_campaign), biggest first. source /
    medium list the distinct values seen. Untagged sales are campaign '(none)'."""
    sql = "SELECT brand, note, amount_cents FROM revenue WHERE source IN ('product', 'affiliate')"
    args: list = []
    if brand:
        sql += " AND brand = ?"
        args.append(brand)
    if since:
        sql += " AND date >= ?"
        args.append(since)
    groups: dict[tuple, dict] = {}
    for r in db.query(sql, args):
        utm = parse_note(r["note"])
        key = (r["brand"] or "", utm.get("utm_campaign", "(none)"))
        g = groups.setdefault(key, {"brand": key[0], "campaign": key[1], "sources": set(), "mediums": set(),
                                    "sales": 0, "revenue_cents": 0})
        g["sources"].add(utm.get("utm_source", ""))
        g["mediums"].add(utm.get("utm_medium", ""))
        g["sales"] += 1
        g["revenue_cents"] += int(r["amount_cents"] or 0)
    out = []
    for g in groups.values():
        g["source"] = ", ".join(sorted(x for x in g.pop("sources") if x))
        g["medium"] = ", ".join(sorted(x for x in g.pop("mediums") if x))
        out.append(g)
    return sorted(out, key=lambda g: (-g["revenue_cents"], g["campaign"]))
