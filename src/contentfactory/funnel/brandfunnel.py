"""Per-brand funnel file: brands/sequences/<brand>.yaml.

One YAML per brand holds the email welcome sequence, the lead magnet copy
and the sales page copy for its products, so the whole funnel for a brand is
reviewed in one place. Every section is optional; without the file the
funnel falls back to generic defaults.

    lead_magnet: {title, pitch, sections: [{heading, items: [...]}]}
    vars:        {product_name, price, launch_price, launch_code, launch_ends, ...}
    links:       {key: "freebie" | "link_page" | "product:<slug>" | "affiliate:<slug>" | "https://..."}
    name:        welcome
    min_gap_hours / max_late_days / footer_note
    steps:       [{day_offset, subject, body_markdown, cta_url_key, cta_label}]
    products:    [{slug, match, headline, ...sales page copy}]  (see salespage.py)
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import yaml

_CACHE: dict[Path, tuple[float, dict]] = {}


def funnel_path(settings, brand_slug: str) -> Path:
    return Path(settings.brands_dir) / "sequences" / f"{brand_slug}.yaml"


def load_funnel(settings, brand_slug: str) -> dict:
    """Parsed funnel file ({} when missing). Cached by mtime."""
    if settings is None:
        return {}
    path = funnel_path(settings, brand_slug)
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return {}
    hit = _CACHE.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at the top level")
    _CACHE[path] = (mtime, data)
    return data


def parse_day(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10]) if value else None
    except ValueError:
        return None


def launch_state(info: dict, now: datetime | None = None) -> dict:
    """{active, price, launch_price, code, ends, ends_human} from a dict with
    price / launch_price / launch_code / launch_ends. A launch is active only
    while launch_price and launch_ends are set and today <= launch_ends (UTC),
    so emails and pages never advertise a launch price that has ended."""
    now = now or datetime.now(timezone.utc)
    ends = parse_day(info.get("launch_ends"))
    lp = str(info.get("launch_price") or "").strip()
    active = bool(lp and ends and now.date() <= ends)
    human = f"{ends.strftime('%A, %B')} {ends.day}" if ends else ""
    return {"active": active, "price": str(info.get("price") or "").strip(), "launch_price": lp,
            "code": str(info.get("launch_code") or "").strip(), "ends": ends.isoformat() if ends else "",
            "ends_human": human}
