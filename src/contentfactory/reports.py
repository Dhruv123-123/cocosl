"""Weekly business report: one page that says what happened and what to do next.

`weekly_report(factory)` returns a dict and a Markdown rendering; `save_report`
writes it to output/reports/. The worker can run it every Monday and the
dashboard/n8n can email it to you.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from .pipeline import Factory


def _money(cents: int | None) -> str:
    return f"${(cents or 0) / 100:,.2f}"


def _sum(db, sql: str, params: list) -> int:
    return int(db.scalar(sql, params) or 0)


def weekly_report(factory: Factory, end: date | None = None) -> dict:
    db = factory.db
    end = end or datetime.now(timezone.utc).date()
    start = end - timedelta(days=7)
    prev = start - timedelta(days=7)
    s, e, p = start.isoformat(), (end + timedelta(days=1)).isoformat(), prev.isoformat()

    content = {
        "produced": _sum(db, "SELECT COUNT(*) FROM posts WHERE created_at >= ? AND created_at < ?", [s, e]),
        "approved": _sum(db, "SELECT COUNT(*) FROM audit_log WHERE action='post.approved' AND ts >= ? AND ts < ?", [s, e]),
        "published": db.query("""SELECT platform, COUNT(*) n FROM publications WHERE status='published'
                                 AND published_at >= ? AND published_at < ? GROUP BY platform""", [s, e]),
        "in_review": _sum(db, "SELECT COUNT(*) FROM posts WHERE status IN ('in_review','blocked')", []),
        "scheduled_next_7d": _sum(db, "SELECT COUNT(*) FROM publications WHERE status='queued' AND scheduled_at < ?",
                                  [(end + timedelta(days=8)).isoformat()]),
        "ideas_backlog": _sum(db, "SELECT COUNT(*) FROM ideas WHERE status IN ('new','approved')", []),
    }

    from .insights import report as perf_report
    perf = perf_report(db, days=7)
    # What actually went out this week, per brand and platform, with each post's latest numbers.
    posted = db.query("""
        SELECT s.brand, p.platform, s.title, s.format, p.url, p.published_at, p.status,
               (SELECT m.views FROM metrics m WHERE m.publication_id = p.id ORDER BY m.captured_at DESC LIMIT 1) views,
               (SELECT m.likes FROM metrics m WHERE m.publication_id = p.id ORDER BY m.captured_at DESC LIMIT 1) likes,
               (SELECT m.link_clicks FROM metrics m WHERE m.publication_id = p.id ORDER BY m.captured_at DESC LIMIT 1) clicks
        FROM publications p JOIN posts s ON s.id = p.post_id
        WHERE p.status IN ('published', 'dry_run') AND p.published_at >= ? AND p.published_at < ?
        ORDER BY s.brand, p.platform, p.published_at""", [s, e])
    platforms: dict = {}
    for row in posted:
        k = (row["brand"], row["platform"])
        agg = platforms.setdefault(k, {"brand": row["brand"], "platform": row["platform"], "posts": 0, "dry_run": 0,
                                       "views": 0, "likes": 0, "clicks": 0, "measured": 0})
        agg["posts"] += 1
        agg["dry_run"] += row["status"] == "dry_run"
        if row["views"] is not None:
            agg["measured"] += 1
            agg["views"] += row["views"] or 0
            agg["likes"] += row["likes"] or 0
            agg["clicks"] += row["clicks"] or 0

    money: dict = {
        "revenue_week": _sum(db, "SELECT SUM(amount_cents) FROM revenue WHERE date >= ? AND date < ?", [s, e]),
        "revenue_prev_week": _sum(db, "SELECT SUM(amount_cents) FROM revenue WHERE date >= ? AND date < ?", [p, s]),
        "expenses_week": _sum(db, "SELECT SUM(amount_cents) FROM expenses WHERE date >= ? AND date < ?", [s, e]),
        "llm_cost_week_usd": round(float(db.scalar(
            "SELECT SUM(cost_usd) FROM llm_usage WHERE ts >= ? AND ts < ?", [s, e]) or 0), 2),
        "by_source": db.query("""SELECT source, SUM(amount_cents) cents FROM revenue WHERE date >= ? AND date < ?
                                 GROUP BY source ORDER BY cents DESC""", [s, e]),
    }
    try:
        from .business.revenue import goal_progress
        money["goal"] = goal_progress(db, on=end)
    except Exception:  # business module optional
        pass

    try:
        from .funnel.analytics import revenue_by_campaign
        money["by_campaign"] = revenue_by_campaign(db, since=s)[:10]
    except Exception:
        money["by_campaign"] = []

    sales: dict = {}
    try:
        from .business import invoices, ugc
        pipe = ugc.pipeline(db)
        sales = {
            "pipeline": {k: len(v) for k, v in pipe.items()},
            "follow_ups_due": len(ugc.due_follow_ups(db, end.isoformat())),
            "overdue_invoices": [{"number": i["number"], "total": _money(i["total_cents"])} for i in invoices.overdue(db, end)],
            "new_leads_week": _sum(db, "SELECT COUNT(*) FROM clients WHERE created_at >= ? AND created_at < ?", [s, e]),
        }
    except Exception:
        pass

    audience: list = []
    try:
        from .funnel.analytics import funnel_stats
        audience = funnel_stats(db, since=s)
    except Exception:
        pass

    actions = []
    if content["in_review"]:
        actions.append(f"Review {content['in_review']} post(s) waiting in the queue.")
    if content["scheduled_next_7d"] < 5:
        actions.append("Fewer than 5 posts scheduled for next week: approve and schedule more.")
    if sales.get("follow_ups_due"):
        actions.append(f"Send {sales['follow_ups_due']} follow-up email(s) to leads.")
    if sales.get("overdue_invoices"):
        actions.append(f"Chase {len(sales['overdue_invoices'])} overdue invoice(s).")
    if sales and sales.get("new_leads_week", 0) < 10:
        actions.append("Add at least 10 new leads to the ad-studio pipeline (launch/ugc-service/LEAD_CRITERIA.md).")
    if perf["by_format"]:
        best = perf["by_format"][0]
        actions.append(f"Best format this week: {best['format']} ({best['avg_views']:.0f} avg views). Make more of it.")
    goal = money.get("goal")
    if goal and not goal.get("on_track"):
        actions.append(f"Behind the monthly goal: need {_money(goal['needed_per_day_cents'])}/day for the rest of the month.")

    if posted and not any(a["measured"] for a in platforms.values()) and not factory.settings.dry_run:
        actions.append("No view numbers yet: check the platform connections (`factory doctor`).")
    return {"start": s, "end": end.isoformat(), "content": content, "performance": perf, "money": money,
            "posted": posted, "platforms": list(platforms.values()),
            "sales": sales, "audience": audience, "actions": actions}


def to_markdown(r: dict) -> str:
    c, m, perf = r["content"], r["money"], r["performance"]
    pub = ", ".join(f"{x['platform']} {x['n']}" for x in c["published"]) or "none"
    lines = [
        f"# Weekly report: {r['start']} to {r['end']}", "",
        "## Next actions", *[f"- {a}" for a in r["actions"] or ["Nothing urgent. Keep the cadence."]], "",
        "## Money",
        f"- Revenue: **{_money(m['revenue_week'])}** (previous week {_money(m['revenue_prev_week'])})",
        f"- Expenses: {_money(m['expenses_week'])}; Claude usage ≈ ${m['llm_cost_week_usd']:.2f}",
    ]
    for row in m["by_source"]:
        lines.append(f"  - {row['source']}: {_money(row['cents'])}")
    if m.get("goal"):
        g = m["goal"]
        lines.append(f"- Month to date: {_money(g['revenue_cents'])} of {_money(g['goal_cents'])} "
                     f"({g['pct']}%), projected {_money(g['projected_cents'])}")
    lines += ["", "## Content",
              f"- Produced {c['produced']}, approved {c['approved']}, published: {pub}",
              f"- Waiting for review: {c['in_review']}; scheduled next 7 days: {c['scheduled_next_7d']}; "
              f"ideas in backlog: {c['ideas_backlog']}",
              f"- Views this week: {perf['total_views']:,} across {perf['posts_measured']} measured posts"]
    for t in perf["top_posts"][:3]:
        lines.append(f"  - {t['title']} ({t['platform']}): {t['views']:,} views")
    if r.get("platforms"):
        lines += ["", "## Posted this week"]
        for a in r["platforms"]:
            nums = (f"{a['views']:,} views, {a['likes']:,} likes, {a['clicks']:,} link clicks"
                    if a["measured"] else "no numbers yet")
            dry = f" ({a['dry_run']} dry run)" if a["dry_run"] else ""
            lines.append(f"- {a['brand']} · {a['platform']}: {a['posts']} post(s){dry}; {nums}")
        for row in r["posted"][:15]:
            v = f" · {row['views']:,} views" if row["views"] is not None else ""
            link = f" ({row['url']})" if row["url"] else ""
            lines.append(f"  - {row['title']} [{row['platform']}]{v}{link}")
    if m.get("by_campaign"):
        lines += ["", "## Sales by campaign (UTM)"]
        for c in m["by_campaign"]:
            lines.append(f"- {c['brand']} · {c['campaign']}: {c['sales']} sale(s), {_money(c['revenue_cents'])}"
                         + (f" (from {c['source']})" if c.get("source") else ""))
    if r["audience"]:
        lines += ["", "## Funnel"]
        for a in r["audience"]:
            lines.append(f"- {a['brand']}: {a['views']:,} views → {a['link_clicks']} clicks → "
                         f"{a['subscribers']} subscribers → {a['sales']} sales ({_money(a['revenue_cents'])})")
    if r["sales"]:
        sp = r["sales"]
        lines += ["", "## Ad studio pipeline",
                  "- " + ", ".join(f"{k} {v}" for k, v in sp["pipeline"].items() if v) if any(sp["pipeline"].values())
                  else "- No leads yet",
                  f"- New leads this week: {sp['new_leads_week']}; follow-ups due: {sp['follow_ups_due']}"]
        for inv in sp["overdue_invoices"]:
            lines.append(f"- Overdue: {inv['number']} {inv['total']}")
    return "\n".join(lines) + "\n"


def save_report(factory: Factory, end: date | None = None) -> str:
    r = weekly_report(factory, end)
    out = factory.settings.output_dir / "reports"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"week-{r['end']}.md"
    path.write_text(to_markdown(r))
    factory.db.log("report.weekly", "", None, {"path": str(path)})
    return str(path)
