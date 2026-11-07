"""Subscriber storage, double opt-in and abuse protection.

Tables are created on demand with CREATE TABLE IF NOT EXISTS on the shared
factory DB, so nothing in db.py needs to change.

Flow: subscribe() -> status 'pending' + token -> confirmation email with
/confirm/<token> -> confirm() -> 'confirmed'. Every email carries
/unsubscribe/<token>; unsubscribing is one click and permanent until the
person signs up again (which restarts double opt-in).
"""
from __future__ import annotations

import re
import secrets
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from ..db import DB, now_iso

SCHEMA = """
CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY,
  brand TEXT NOT NULL,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',   -- pending | confirmed | unsubscribed
  token TEXT NOT NULL UNIQUE,
  source TEXT DEFAULT '',
  ip TEXT DEFAULT '',
  created_at TEXT NOT NULL,
  confirmed_at TEXT,
  unsubscribed_at TEXT,
  UNIQUE(brand, email)
);
CREATE INDEX IF NOT EXISTS subscribers_brand_status ON subscribers(brand, status);

CREATE TABLE IF NOT EXISTS emails_sent (
  id INTEGER PRIMARY KEY,
  brand TEXT NOT NULL,
  subscriber_id INTEGER,
  email TEXT NOT NULL,
  kind TEXT NOT NULL,                       -- confirm | digest
  draft_id INTEGER,
  status TEXT NOT NULL,                     -- sent | dry_run | failed
  path TEXT DEFAULT '',
  error TEXT DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS emails_sent_draft ON emails_sent(draft_id, subscriber_id);

CREATE TABLE IF NOT EXISTS newsletter_drafts (
  id INTEGER PRIMARY KEY,
  brand TEXT NOT NULL,
  subject TEXT NOT NULL,
  preheader TEXT DEFAULT '',
  html TEXT NOT NULL,
  text TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',     -- draft | sent
  period_start TEXT,
  period_end TEXT,
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL,
  sent_at TEXT
);
"""

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
                      r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
HONEYPOT_FIELD = "website"  # hidden input; humans leave it empty


class SubscribeError(ValueError):
    """Bad input from the signup form (shown to the visitor)."""


def ensure_schema(db: DB) -> None:
    with db.lock:
        db.conn.executescript(SCHEMA)
        db.conn.commit()
    db.__dict__.get("_colcache", {}).pop("subscribers", None)


def normalize_email(raw: str) -> str:
    """Trim + lowercase the domain; raise SubscribeError if it isn't a plausible address."""
    email = (raw or "").strip()
    if len(email) > 254 or "@" not in email:
        raise SubscribeError("Please enter a valid email address.")
    local, _, domain = email.rpartition("@")
    email = f"{local}@{domain.lower()}"
    if not local or len(local) > 64 or ".." in email or not EMAIL_RE.match(email):
        raise SubscribeError("Please enter a valid email address.")
    tld = domain.rsplit(".", 1)[-1]
    if len(tld) < 2 or tld.isdigit():
        raise SubscribeError("Please enter a valid email address.")
    return email


# ---------------------------------------------------------------- rate limit
class RateLimiter:
    """In-memory sliding window: at most `limit` hits per key per `window` s."""

    def __init__(self, limit: int = 5, window: float = 600):
        self.limit, self.window = limit, window
        self.hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self.hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            if len(self.hits) > 10000:  # keep memory bounded under abuse
                for k in [k for k, v in self.hits.items() if not v][:5000]:
                    del self.hits[k]
            return True


# ---------------------------------------------------------------- operations
@dataclass
class SubscribeResult:
    subscriber: dict | None
    needs_confirmation: bool  # True when a confirmation email should go out
    bot: bool = False


def subscribe(db: DB, brand: str, email: str, *, source: str = "", ip: str = "",
              honeypot: str = "") -> SubscribeResult:
    """Create or refresh a pending subscription. Honeypot hits are silently
    dropped (the caller still shows the normal 'check your inbox' page)."""
    ensure_schema(db)
    if honeypot.strip():
        db.log("funnel.honeypot", "subscriber", None, {"brand": brand, "ip": ip})
        return SubscribeResult(None, False, bot=True)
    email = normalize_email(email)
    row = db.one("SELECT * FROM subscribers WHERE brand = ? AND email = ? COLLATE NOCASE", [brand, email])
    if row and row["status"] == "confirmed":
        return SubscribeResult(row, False)
    token = secrets.token_urlsafe(24)
    if row:
        db.execute("UPDATE subscribers SET status='pending', token=?, source=?, ip=?, unsubscribed_at=NULL "
                   "WHERE id=?", [token, source or row["source"], ip, row["id"]])
        sid = row["id"]
    else:
        sid = db.insert("subscribers", {"brand": brand, "email": email, "status": "pending", "token": token,
                                        "source": source[:200], "ip": ip})
    db.log("funnel.subscribe", "subscriber", sid, {"brand": brand, "source": source})
    return SubscribeResult(db.get("subscribers", sid), True)


def by_token(db: DB, token: str) -> dict | None:
    ensure_schema(db)
    if not token or len(token) > 100:
        return None
    return db.one("SELECT * FROM subscribers WHERE token = ?", [token])


def confirm(db: DB, token: str) -> dict | None:
    """Confirm a pending subscriber. Returns the row (already-confirmed is fine), None if unknown."""
    row = by_token(db, token)
    if not row or row["status"] == "unsubscribed":
        return None
    if row["status"] == "pending":
        db.execute("UPDATE subscribers SET status='confirmed', confirmed_at=? WHERE id=?", [now_iso(), row["id"]])
        db.log("funnel.confirm", "subscriber", row["id"], {"brand": row["brand"]})
        row = db.get("subscribers", row["id"])
    return row


def unsubscribe(db: DB, token: str) -> dict | None:
    row = by_token(db, token)
    if not row:
        return None
    if row["status"] != "unsubscribed":
        db.execute("UPDATE subscribers SET status='unsubscribed', unsubscribed_at=? WHERE id=?",
                   [now_iso(), row["id"]])
        db.log("funnel.unsubscribe", "subscriber", row["id"], {"brand": row["brand"]})
        row = db.get("subscribers", row["id"])
    return row


def list_subscribers(db: DB, brand: str, status: str | None = None, limit: int = 500) -> list[dict]:
    ensure_schema(db)
    sql, args = "SELECT * FROM subscribers WHERE brand = ?", [brand]
    if status:
        sql += " AND status = ?"
        args.append(status)
    return db.query(sql + " ORDER BY id DESC LIMIT ?", [*args, limit])


def counts(db: DB, brand: str | None = None) -> dict[str, dict[str, int]]:
    """{brand: {pending, confirmed, unsubscribed, total, new_7d, new_30d}}."""
    ensure_schema(db)
    out: dict[str, dict[str, int]] = {}
    where, args = ("WHERE brand = ?", [brand]) if brand else ("", [])
    for r in db.query(f"SELECT brand, status, COUNT(*) n FROM subscribers {where} GROUP BY brand, status", args):
        b = out.setdefault(r["brand"], {"pending": 0, "confirmed": 0, "unsubscribed": 0})
        b[r["status"]] = r["n"]
    for b, d in out.items():
        d["total"] = d["pending"] + d["confirmed"]
        for days in (7, 30):
            d[f"new_{days}d"] = int(db.scalar(
                "SELECT COUNT(*) FROM subscribers WHERE brand = ? AND status = 'confirmed' "
                "AND confirmed_at >= datetime('now', ?)", [b, f"-{days} days"]) or 0)
    return out


def growth(db: DB, brand: str, days: int = 30) -> list[dict]:
    """Daily confirmed signups for the last `days` days: [{day, n}]."""
    ensure_schema(db)
    rows = db.query("SELECT substr(confirmed_at, 1, 10) day, COUNT(*) n FROM subscribers "
                    "WHERE brand = ? AND confirmed_at >= date('now', ?) GROUP BY day ORDER BY day",
                    [brand, f"-{days} days"])
    return rows


def log_email(db: DB, *, brand: str, email: str, kind: str, status: str, subscriber_id: int | None = None,
              draft_id: int | None = None, path: str = "", error: str = "") -> int:
    ensure_schema(db)
    return db.insert("emails_sent", {"brand": brand, "subscriber_id": subscriber_id, "email": email, "kind": kind,
                                     "draft_id": draft_id, "status": status, "path": path, "error": error[:1000]})
