"""Posting calendar: turn approved posts into time slots that respect cadence."""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from .config import BrandProfile
from .db import DB


def _parse_hhmm(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def taken_slots(db: DB, brand: str, platform: str) -> set[str]:
    rows = db.query(
        """SELECT p.scheduled_at FROM publications p JOIN posts s ON s.id = p.post_id
           WHERE s.brand = ? AND p.platform = ? AND p.status IN ('queued','publishing','published','dry_run','needs_check')
           AND p.scheduled_at IS NOT NULL""",
        [brand, platform],
    )
    return {r["scheduled_at"] for r in rows}


def next_slot(db: DB, brand: BrandProfile, platform: str, after: datetime | None = None,
              horizon_days: int = 60) -> datetime:
    """First free configured posting time after `after` that keeps the
    platform under its daily cap. Returns an aware UTC datetime."""
    tz = ZoneInfo(brand.cadence.timezone)
    after = (after or datetime.now(timezone.utc)).astimezone(tz)
    taken = taken_slots(db, brand.slug, platform)
    per_day: dict[str, int] = {}
    for t in taken:
        d = datetime.fromisoformat(t).astimezone(tz).date().isoformat()
        per_day[d] = per_day.get(d, 0) + 1
    times = sorted(_parse_hhmm(t) for t in brand.cadence.post_times) or [time(12, 0)]
    cap = brand.cadence.max_posts_per_day_per_platform
    for day in range(horizon_days):
        date = (after + timedelta(days=day)).date()
        if per_day.get(date.isoformat(), 0) >= cap:
            continue
        for t in times:
            slot = datetime.combine(date, t, tzinfo=tz)
            if slot <= after:
                continue
            iso = slot.astimezone(timezone.utc).isoformat()
            if iso in taken:
                continue
            return slot.astimezone(timezone.utc)
    raise RuntimeError(f"No free slot in the next {horizon_days} days for {brand.slug}/{platform}")


def calendar(db: DB, days: int = 14, brand: str | None = None) -> list[dict]:
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    sql = """SELECT p.*, s.title, s.brand, s.format FROM publications p JOIN posts s ON s.id = p.post_id
             WHERE p.scheduled_at >= ? AND p.scheduled_at < ?"""
    params: list = [(now - timedelta(days=1)).isoformat(), end.isoformat()]
    if brand:
        sql += " AND s.brand = ?"
        params.append(brand)
    return db.query(sql + " ORDER BY p.scheduled_at", params)
