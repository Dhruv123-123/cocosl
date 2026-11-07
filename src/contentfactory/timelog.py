"""`factory time`: how much of Dhruv's time the business takes, against the one-hour-a-day limit.

    factory time log 20                      # 20 minutes, today, category "routine"
    factory time log 45 --what ad-studio     # categories: routine, review, recording, replies, ad-studio, setup, other
    factory time log 30 --brand scam-decoded --date 2026-11-21 --note "recording session"
    factory time                             # this week and the last 4: minutes per day, per category, vs the limit
    factory time --weeks 8

The limit (risk memo, two-brand plan): the brands together take under an hour a day. "Brand time" is
everything except ad-studio and setup (those are tracked, shown, but don't count against the brands'
hour), so the brand-3 gate in `factory scorecard --gate` reads the same number. The Today page has a
one-line form for logging too. TIME_LIMIT_MIN_PER_DAY (default 60) changes the limit.
"""
from __future__ import annotations

import os
from datetime import date, timedelta

CATEGORIES = ("routine", "review", "recording", "replies", "ad-studio", "setup", "other")
NOT_BRAND = ("ad-studio", "setup")
SCHEMA = """CREATE TABLE IF NOT EXISTS time_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, minutes INTEGER NOT NULL,
  category TEXT NOT NULL DEFAULT 'routine', brand TEXT DEFAULT '', note TEXT DEFAULT '', created_at TEXT NOT NULL)"""


def limit_per_day() -> int:
    try:
        return int(os.environ.get("TIME_LIMIT_MIN_PER_DAY", "60"))
    except ValueError:
        return 60


def ensure(db) -> None:
    db.execute(SCHEMA)


def log(factory, minutes: int, category: str = "routine", brand: str = "", note: str = "", day: date | None = None) -> int:
    from .db import now_iso
    if minutes <= 0 or minutes > 16 * 60:
        raise ValueError("minutes must be between 1 and 960")
    category = category.strip().lower()
    if category not in CATEGORIES:
        raise ValueError(f"category: one of {', '.join(CATEGORIES)}")
    ensure(factory.db)
    return factory.db.insert("time_log", {"day": (day or date.today()).isoformat(), "minutes": int(minutes),
                                          "category": category, "brand": brand, "note": note, "created_at": now_iso()})


def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def weeks(factory, n: int = 5, today: date | None = None) -> list[dict]:
    """Newest first: {monday, total, brand_min, by_category, by_day, days_logged, over_days, limit_week, ok}."""
    ensure(factory.db)
    today = today or date.today()
    out = []
    lim = limit_per_day()
    for k in range(n):
        mon = week_start(today) - timedelta(weeks=k)
        rows = factory.db.query("SELECT day, minutes, category FROM time_log WHERE day >= ? AND day < ?",
                                [mon.isoformat(), (mon + timedelta(days=7)).isoformat()])
        by_cat: dict = {}
        by_day: dict = {}
        for r in rows:
            by_cat[r["category"]] = by_cat.get(r["category"], 0) + r["minutes"]
            if r["category"] not in NOT_BRAND:
                by_day[r["day"]] = by_day.get(r["day"], 0) + r["minutes"]
        brand_min = sum(by_day.values())
        days = 7 if mon + timedelta(days=6) <= today else (today - mon).days + 1
        out.append({"monday": mon, "total": sum(by_cat.values()), "brand_min": brand_min, "by_category": by_cat,
                    "by_day": by_day, "days_logged": len({r["day"] for r in rows}),
                    "over_days": sorted(d for d, m in by_day.items() if m > lim),
                    "limit_week": lim * days, "ok": bool(rows) and brand_min <= lim * days})
    return out


def streak_ok(factory, n: int = 4, today: date | None = None) -> tuple[bool, str]:
    """Brand time under the limit for the last n complete weeks (each logged)."""
    ws = weeks(factory, n + 1, today)[1:]  # complete weeks only
    bad = [w for w in ws if not w["ok"]]
    if not bad:
        return True, f"under {limit_per_day()} min a day for {n} straight weeks"
    w = bad[0]
    why = "nothing logged" if not w["total"] else f"{w['brand_min']} min (limit {w['limit_week']})"
    return False, f"week of {w['monday']}: {why}"


def _h(m: int) -> str:
    return f"{m // 60}h{m % 60:02d}" if m >= 60 else f"{m} min"


def to_text(ws: list[dict]) -> str:
    lim = limit_per_day()
    out = [f"Time used (limit: brands {lim} min a day; ad studio and setup shown, not counted)", ""]
    for w in ws:
        flag = "OK " if w["ok"] else ("--" if not w["total"] else "OVER")
        cats = ", ".join(f"{c} {_h(m)}" for c, m in sorted(w["by_category"].items(), key=lambda x: -x[1])) or "nothing logged"
        out.append(f"{flag:4s} week of {w['monday']}: brands {_h(w['brand_min'])} of {_h(w['limit_week'])} · total {_h(w['total'])} · {cats}")
        if w["over_days"]:
            out.append(f"     over the hour on: {', '.join(w['over_days'])}")
    return "\n".join(out) + "\n"


def register(sub, factory_fn) -> None:
    s = sub.add_parser("time", help="log your minutes and see the week against the one-hour-a-day limit")
    s.add_argument("action", nargs="?", choices=["show", "log"], default="show")
    s.add_argument("minutes", nargs="?", type=int)
    s.add_argument("--what", default="routine", help=f"category: {', '.join(CATEGORIES)}")
    s.add_argument("--brand", default="")
    s.add_argument("--note", default="")
    s.add_argument("--date", type=date.fromisoformat, default=None)
    s.add_argument("--weeks", type=int, default=5)

    def cmd(a):
        f = factory_fn(a)
        if a.action == "log":
            if not a.minutes:
                raise SystemExit("usage: factory time log <minutes> [--what routine]")
            log(f, a.minutes, a.what, a.brand, a.note, a.date)
            w = weeks(f, 1)[0]
            print(f"Logged {a.minutes} min ({a.what}). This week: brands {_h(w['brand_min'])} of {_h(w['limit_week'])} so far.")
            return
        print(to_text(weeks(f, a.weeks)), end="")
    s.set_defaults(func=cmd)
