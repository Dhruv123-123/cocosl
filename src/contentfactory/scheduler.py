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
           WHERE s.brand = ? AND p.platform = ? AND p.status IN ('queued','publishing','published','dry_run','needs_check','manual')
           AND p.scheduled_at IS NOT NULL""",
        [brand, platform],
    )
    return {r["scheduled_at"] for r in rows}


WEEKLY_CAP = {"short": "shorts_per_week", "mid": "shorts_per_week", "long": "long_per_week", "carousel": "carousels_per_week"}


def format_days(db: DB, brand: str, platform: str, fmt: str, tz) -> dict:
    """Local date -> number of `fmt` posts on that platform."""
    rows = db.query(
        """SELECT p.scheduled_at FROM publications p JOIN posts s ON s.id = p.post_id
           WHERE s.brand = ? AND p.platform = ? AND s.format = ?
           AND p.status IN ('queued','publishing','published','dry_run','needs_check','manual') AND p.scheduled_at IS NOT NULL""",
        [brand, platform, fmt])
    out: dict = {}
    for r in rows:
        d = datetime.fromisoformat(r["scheduled_at"]).astimezone(tz).date()
        out[d] = out.get(d, 0) + 1
    return out


def next_slot(db: DB, brand: BrandProfile, platform: str, after: datetime | None = None,
              horizon_days: int = 60, fmt: str | None = None) -> datetime:
    """First free configured posting time after `after` that keeps the
    platform under its daily cap and, when `fmt` is given, the format under
    its weekly cadence (any 7 consecutive days). Returns an aware UTC datetime."""
    tz = ZoneInfo(brand.cadence.timezone)
    after = (after or datetime.now(timezone.utc)).astimezone(tz)
    taken = taken_slots(db, brand.slug, platform)
    per_day: dict[str, int] = {}
    for t in taken:
        d = datetime.fromisoformat(t).astimezone(tz).date().isoformat()
        per_day[d] = per_day.get(d, 0) + 1
    weekly = getattr(brand.cadence, WEEKLY_CAP.get(fmt or "", ""), None) if fmt else None
    fdays = format_days(db, brand.slug, platform, fmt, tz) if weekly else {}

    def week_full(date) -> bool:
        # every 7-day window containing `date` must stay at or under the weekly number
        for start in range(-6, 1):
            first = date + timedelta(days=start)
            if sum(fdays.get(first + timedelta(days=i), 0) for i in range(7)) >= weekly:
                return True
        return False
    wanted = brand.cadence.times_for(platform, fmt)
    times = sorted(_parse_hhmm(t) for t in wanted) or [time(12, 0)]
    cap = brand.cadence.max_posts_per_day_per_platform
    for day in range(horizon_days):
        date = (after + timedelta(days=day)).date()
        if per_day.get(date.isoformat(), 0) >= cap:
            continue
        if weekly and week_full(date):
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


def platform_cap_reached(db: DB, brand: BrandProfile, platform: str, fmt: str, slot: datetime) -> int | None:
    """The cap when `platform` already has its `platform_weekly_caps` number of `fmt` posts in a 7-day window
    around `slot` (short and mid count together); None when there is room or no cap."""
    cap = brand.cadence.weekly_cap(platform, fmt)
    if cap is None:
        return None
    tz = ZoneInfo(brand.cadence.timezone)
    fmts = ("short", "mid") if fmt in ("short", "mid") else (fmt,)
    days: dict = {}
    for f in fmts:
        for d, n in format_days(db, brand.slug, platform, f, tz).items():
            days[d] = days.get(d, 0) + n
    day = slot.astimezone(tz).date()
    for start in range(-6, 1):
        first = day + timedelta(days=start)
        if sum(days.get(first + timedelta(days=i), 0) for i in range(7)) >= cap:
            return cap
    return None


def collisions(db: DB, brand: str | None = None) -> list[dict]:
    """Two live publications of one brand on one platform at the same minute."""
    sql = """SELECT s.brand, p.platform, substr(p.scheduled_at, 1, 16) AS at, COUNT(*) AS n,
                    GROUP_CONCAT(p.id) AS ids FROM publications p JOIN posts s ON s.id = p.post_id
             WHERE p.status IN ('queued','manual') AND p.scheduled_at IS NOT NULL""" + (" AND s.brand = ?" if brand else "") + \
          " GROUP BY s.brand, p.platform, substr(p.scheduled_at, 1, 16) HAVING COUNT(*) > 1"
    return db.query(sql, [brand] if brand else [])


def reslot(factory, brand: str | None = None, after: datetime | None = None, apply: bool = False) -> dict:
    """Move every queued publication (not yet handed off or posted) onto the brand's current slots:
    per-platform times, daily caps, weekly cadence and platform weekly caps. Order is kept (earliest
    first). Publications over a platform cap are cancelled (the post keeps its other platforms).
    Without apply, nothing changes and the plan is returned."""
    after = after or datetime.now(timezone.utc)
    brands = factory.brands()
    moves, dropped = [], []
    from .launchmode import active_brands
    act = active_brands(factory)
    slugs = [brand] if brand else [b for b in brands if act is None or b in act]
    db = factory.db
    for slug in slugs:
        b = brands[slug]
        rows = db.query("""SELECT p.id, p.platform, p.scheduled_at, p.post_id, s.format FROM publications p
                           JOIN posts s ON s.id = p.post_id WHERE s.brand = ? AND p.status = 'queued'
                           AND p.scheduled_at > ? ORDER BY p.scheduled_at, p.id""", [slug, after.isoformat()])
        if not rows:
            continue
        ids = [r["id"] for r in rows]
        posts_before = {r["post_id"]: db.scalar("SELECT scheduled_at FROM posts WHERE id = ?", [r["post_id"]]) for r in rows}

        def restore():
            for r in rows:
                db.execute("UPDATE publications SET status = 'queued', scheduled_at = ?, error = '' WHERE id = ?",
                           [r["scheduled_at"], r["id"]])
            for pid, at in posts_before.items():
                db.execute("UPDATE posts SET scheduled_at = ? WHERE id = ?", [at, pid])
        # take them off the calendar, place them again in order; a dry run (or an error) puts everything back
        try:
            db.execute(f"UPDATE publications SET status = 'reslotting' WHERE id IN ({','.join('?' * len(ids))})", ids)
            for r in rows:
                slot = next_slot(db, b, r["platform"], after=after, fmt=r["format"])
                cap = platform_cap_reached(db, b, r["platform"], r["format"], slot)
                if cap is not None:
                    dropped.append({"pub": r["id"], "post": r["post_id"], "platform": r["platform"], "was": r["scheduled_at"],
                                    "why": f"{r['platform']} {r['format']} cap {cap} a week"})
                    db.execute("UPDATE publications SET status = 'cancelled', error = ? WHERE id = ?",
                               [f"reslot: over the {cap}-a-week {r['platform']} cap", r["id"]])
                    continue
                new = slot.isoformat()
                if new != r["scheduled_at"]:
                    moves.append({"pub": r["id"], "post": r["post_id"], "platform": r["platform"],
                                  "from": r["scheduled_at"], "to": new})
                db.execute("UPDATE publications SET status = 'queued', scheduled_at = ? WHERE id = ?", [new, r["id"]])
            for pid in posts_before:
                first = db.scalar("SELECT MIN(scheduled_at) FROM publications WHERE post_id = ? AND status = 'queued'", [pid])
                if first:
                    db.execute("UPDATE posts SET scheduled_at = ? WHERE id = ?", [first, pid])
            found = collisions(db, slug)
            if not apply:
                restore()
            elif found:
                restore()
                raise RuntimeError(f"reslot would leave {len(found)} collision(s); nothing changed")
        except Exception:
            restore()
            raise
    if apply and (moves or dropped):
        db.log("schedule.reslot", "", None, {"moved": len(moves), "dropped": len(dropped)})
    return {"moved": moves, "dropped": dropped, "collisions": collisions(db, brand), "applied": apply}


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


def register(sub, factory_fn) -> None:
    s = sub.add_parser("reslot", help="move queued posts onto the current posting slots (per-platform times, caps); "
                                      "lists the plan unless --yes")
    s.add_argument("--brand", default=None)
    s.add_argument("--yes", action="store_true", help="apply the moves")

    def cmd(a):
        res = reslot(factory_fn(a), a.brand, apply=a.yes)
        for m in res["moved"]:
            print(f"pub #{m['pub']} (post #{m['post']}) {m['platform']}: {m['from'][:16]} -> {m['to'][:16]}")
        for d in res["dropped"]:
            print(f"pub #{d['pub']} (post #{d['post']}) {d['platform']}: dropped ({d['why']})")
        print(f"{len(res['moved'])} move(s), {len(res['dropped'])} dropped, {len(res['collisions'])} collision(s)"
              + ("" if a.yes else ". Nothing changed: run again with --yes."))
        if res["collisions"]:
            for c in res["collisions"]:
                print(f"  collision: {c['brand']} {c['platform']} {c['at']} pubs {c['ids']}")
            raise SystemExit(2)
    s.set_defaults(func=cmd)
