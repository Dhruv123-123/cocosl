"""Credential bookkeeping: write tokens to .env and keep short-lived ones fresh.

TikTok access tokens last about 2 hours and refresh tokens rotate, so the
pipeline calls `refresh_tiktok_if_needed` before publishing. Long-lived
Instagram-Login and Threads tokens last ~60 days; `refresh_long_lived` renews
them when they're within 10 days of expiry.
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

from ..config import Settings


def write_env(path: Path, values: dict[str, str]) -> None:
    """Set keys in a .env file (create/replace lines) and in os.environ."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text() if path.exists() else ""
    for key, value in values.items():
        value = str(value)
        line = f"{key}={value}"
        if re.search(rf"^{re.escape(key)}=.*$", text, flags=re.M):
            text = re.sub(rf"^{re.escape(key)}=.*$", lambda _m: line, text, flags=re.M)
        else:
            text = text.rstrip("\n") + ("\n" if text else "") + line + "\n"
        os.environ[key] = value
    path.write_text(text)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _expires_soon(key: str, margin: float) -> bool:
    raw = os.environ.get(key, "")
    try:
        return float(raw) - time.time() < margin
    except ValueError:
        return True


def refresh_tiktok_if_needed(settings: Settings, transport=None) -> bool:
    from .oauth import tiktok_refresh
    key, secret, refresh = (settings.env("TIKTOK_CLIENT_KEY"), settings.env("TIKTOK_CLIENT_SECRET"),
                            settings.env("TIKTOK_REFRESH_TOKEN"))
    if not (key and secret and refresh) or not _expires_soon("TIKTOK_TOKEN_EXPIRES_AT", 15 * 60):
        return False
    data = tiktok_refresh(key, secret, refresh, transport=transport)
    write_env(settings.home / ".env", {
        "TIKTOK_ACCESS_TOKEN": data["access_token"],
        "TIKTOK_REFRESH_TOKEN": data.get("refresh_token", refresh),
        "TIKTOK_TOKEN_EXPIRES_AT": str(int(time.time() + int(data.get("expires_in", 7200)))),
    })
    return True


def refresh_long_lived(settings: Settings, transport=None) -> list[str]:
    """Renew Instagram-Login and Threads long-lived tokens close to expiry."""
    from .oauth import instagram_login_refresh_token, threads_refresh_token
    done = []
    ten_days = 10 * 86400
    if settings.env("IG_API_HOST") == "graph.instagram.com" and settings.env("IG_ACCESS_TOKEN") \
            and settings.env("IG_TOKEN_EXPIRES_AT") and _expires_soon("IG_TOKEN_EXPIRES_AT", ten_days):
        d = instagram_login_refresh_token(settings.env("IG_ACCESS_TOKEN"), transport=transport)
        write_env(settings.home / ".env", {"IG_ACCESS_TOKEN": d["access_token"],
                                           "IG_TOKEN_EXPIRES_AT": str(int(time.time() + int(d.get("expires_in", 0))))})
        done.append("instagram")
    if settings.env("THREADS_ACCESS_TOKEN") and settings.env("THREADS_TOKEN_EXPIRES_AT") \
            and _expires_soon("THREADS_TOKEN_EXPIRES_AT", ten_days):
        d = threads_refresh_token(settings.env("THREADS_ACCESS_TOKEN"), transport=transport)
        write_env(settings.home / ".env", {"THREADS_ACCESS_TOKEN": d["access_token"],
                                           "THREADS_TOKEN_EXPIRES_AT": str(int(time.time() + int(d.get("expires_in", 0))))})
        done.append("threads")
    return done
