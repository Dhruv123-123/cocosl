"""Shared dashboard dependencies: the Factory accessor, the Jinja environment
and its filters. The business module imports `get_factory` and `templates`
from here so its pages share the same layout (base.html) and helpers.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

import jinja2
from fastapi import Request
from fastapi.templating import Jinja2Templates

from ..pipeline import Factory

WEB_DIR = Path(__file__).resolve().parent
TEMPLATE_DIRS = [WEB_DIR / "templates", WEB_DIR.parent / "business" / "templates"]
STATIC_DIR = WEB_DIR / "static"

NAV = [
    ("Overview", "/"),
    ("Ideas", "/ideas"),
    ("Review", "/review"),
    ("Calendar", "/calendar"),
    ("Published", "/published"),
    ("Revenue", "/business/revenue"),
    ("Clients", "/business/clients"),
    ("Products", "/business/products"),
    ("Settings", "/settings"),
]

CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "CAD": "CA$", "AUD": "A$", "JPY": "¥"}


def get_factory(request: Request) -> Factory:
    """FastAPI dependency: the Factory stored on app.state by create_app()."""
    return request.app.state.factory


# --------------------------------------------------------------------------- filters
def money(cents: Any, currency: str = "USD") -> str:
    """Integer cents -> '$1,234.56'. None/'' render as '$0.00'."""
    try:
        value = int(cents or 0) / 100
    except (TypeError, ValueError):
        return str(cents)
    code = (currency or "USD").upper()
    sign = "-" if value < 0 else ""
    if code == "JPY":
        body = f"{abs(value):,.0f}"
    else:
        body = f"{abs(value):,.2f}"
    symbol = CURRENCY_SYMBOLS.get(code)
    return f"{sign}{symbol}{body}" if symbol else f"{sign}{body} {code}"


def parse_dt(value: Any) -> datetime | None:
    """ISO string or datetime -> aware UTC datetime (naive values are assumed UTC)."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def humanize(value: Any, now: datetime | None = None) -> str:
    """'3 min ago', 'in 2 h', 'in 5 days'."""
    dt = parse_dt(value)
    if dt is None:
        return "—" if value in (None, "") else str(value)
    delta = (dt - (now or datetime.now(timezone.utc))).total_seconds()
    future, secs = delta > 0, abs(delta)
    if secs < 45:
        return "just now"
    for limit, div, unit in ((3600, 60, "min"), (86400, 3600, "h"), (86400 * 30, 86400, "day"),
                             (86400 * 365, 86400 * 30, "month")):
        if secs < limit:
            n = round(secs / div)
            label = f"{n} {unit}" + ("s" if unit in ("day", "month") and n != 1 else "")
            return f"in {label}" if future else f"{label} ago"
    n = round(secs / (86400 * 365))
    label = f"{n} year" + ("s" if n != 1 else "")
    return f"in {label}" if future else f"{label} ago"


def localtime(value: Any, tz: str | None = None, fmt: str = "%a %d %b %H:%M") -> str:
    """Format an ISO timestamp in the given IANA timezone (default UTC)."""
    dt = parse_dt(value)
    if dt is None:
        return "—"
    try:
        zone = ZoneInfo(tz) if tz else timezone.utc
    except Exception:
        zone = timezone.utc
    return dt.astimezone(zone).strftime(fmt)


def pretty_json(value: Any) -> str:
    """Indented JSON for <pre> blocks."""
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str, sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


def media_url(rel: Any) -> str:
    """Relative output path -> URL under the /media mount."""
    if not rel:
        return ""
    return "/media/" + quote(str(rel).lstrip("/"))


def compact(n: Any) -> str:
    """12345 -> '12.3k'."""
    try:
        x = float(n or 0)
    except (TypeError, ValueError):
        return str(n)
    for div, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(x) >= div:
            return f"{x / div:.1f}".rstrip("0").rstrip(".") + suffix
    return f"{x:.0f}"


def sparkline(values: list[float] | None, width: int = 120, height: int = 28) -> str:
    """SVG polyline points for a small sparkline (empty string if <2 values)."""
    vals = [float(v or 0) for v in (values or [])]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    step = width / (len(vals) - 1)
    pts = [f"{i * step:.1f},{height - 2 - (v - lo) / span * (height - 4):.1f}" for i, v in enumerate(vals)]
    return " ".join(pts)


FILTERS = {
    "money": money,
    "humanize": humanize,
    "localtime": localtime,
    "pretty_json": pretty_json,
    "tojson_pretty": pretty_json,
    "media_url": media_url,
    "compact": compact,
    "sparkline": sparkline,
}


# --------------------------------------------------------------------------- context
def _common_context(request: Request) -> dict:
    """Variables every page (including business pages) can use in base.html."""
    factory: Factory | None = getattr(request.app.state, "factory", None)
    settings = factory.settings if factory else None
    path = request.url.path
    authed = bool(getattr(request.state, "authed", False))
    active = next((href for _, href in sorted(NAV, key=lambda x: -len(x[1]))
                   if href != "/" and (path == href or path.startswith(href + "/"))), "/" if path == "/" else "")
    return {
        "authed": authed,
        "nav": NAV if authed else [],
        "active_nav": active,
        "dry_run": bool(settings and settings.dry_run),
        "auth_open": bool(settings and not settings.dashboard_token),
        "authed_with_token": bool(authed and settings and settings.dashboard_token),
        "flash_msg": request.query_params.get("msg", ""),
        "flash_err": request.query_params.get("err", ""),
        "running_jobs": request.app.state.jobs.running() if authed and hasattr(request.app.state, "jobs") else [],
        "review_count": _review_count(factory) if authed else 0,
    }


def _review_count(factory: Factory | None) -> int:
    if not factory:
        return 0
    try:
        return int(factory.db.scalar("SELECT COUNT(*) FROM posts WHERE status IN ('in_review', 'blocked')") or 0)
    except Exception:
        return 0


def _build_env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([str(d) for d in TEMPLATE_DIRS]),
        autoescape=jinja2.select_autoescape(["html", "xml"], default_for_string=True),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(FILTERS)
    return env


templates = Jinja2Templates(env=_build_env(), context_processors=[_common_context])
