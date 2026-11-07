"""`factory today --15min`: Dhruv's daily routine (GO_LIVE.md R6), filled in with today's real items.

    factory today --15min          # the 15-minute routine: triage, 2 reviews, post by hand, people
    factory today                  # same steps, every item listed (no 15-minute cut)
    factory today --date 2026-11-21 --save   # plan another day; also writes output/today-<date>.md

Steps, in order (stop at 15 minutes and carry the rest over):
1. 3 min · Triage: the red items (`factory triage` "Do now", without post-by-hand, which is step 3).
2. 5 min · Review 2 posts: the oldest posts waiting in Review, with any blocking flag.
3. 2 min · Post by hand: TikTok and Pinterest packages that are due, with the paste-ready caption.
4. 5 min · People: comment drafts and new comments in the inbox (you send every reply).
Plus the day's extras from R6: weekday ad-studio emails, Monday report + launch-check, Saturday
recording session (with `factory batch-record`), and day-N milestones counted from the launch day
(FACTORY_LAUNCH_DATE, else the first post that went out). Nothing is posted or changed.
"""
from __future__ import annotations

import os
from datetime import date, datetime

STEP_MIN = {"triage": 3, "review": 5, "by_hand": 2, "people": 5}
DATED = {  # date -> (minutes, what): one-off items from R6
    "2026-11-14": (10, "The LAUNCH codes end today: check they've expired on Gumroad"),
    "2026-11-21": (15, "Month 1 starts: import calendar.ics and confirm its first week is approved"),
}
DAY_N = {  # days since launch -> (minutes, what)
    7: (30, "If Money Made Simple is steady, start the next brand's accounts (GO_LIVE Stage 9)"),
    10: (30, "About 10 posts are live: apply to the affiliate programs with the kit's answers (Stage 7)"),
    21: (20, "Look at what worked (`factory report`): keep the hooks that held viewers, drop the rest"),
    30: (30, "Swap the financial model's assumptions for real numbers and decide what to do more of"),
}
AD_STUDIO_FROM = date(2026, 11, 10)


def launch_day(factory) -> date | None:
    env = os.environ.get("FACTORY_LAUNCH_DATE", "").strip()
    if env:
        try:
            return date.fromisoformat(env)
        except ValueError:
            pass
    first = factory.db.scalar("SELECT MIN(COALESCE(published_at, updated_at)) FROM publications "
                              "WHERE status = 'published'")
    try:
        return datetime.fromisoformat(str(first)[:19]).date() if first else None
    except ValueError:
        return None


def extras(factory, day: date) -> list[tuple[int, str]]:
    out = []
    if day.weekday() < 5 and day >= AD_STUDIO_FROM:
        out.append((45, "Ad studio: 15 first emails plus due follow-ups (Stage 2), sent by you. The fastest money"))
    if day.weekday() == 0:
        out.append((20, "`factory report` and its Next actions, then `factory launch-check`"))
    if day.weekday() == 5:
        from .batch_record import sessions, tasks
        plan = sessions(tasks(factory, days=14))
        what = (f"{len(plan)} session(s), first: {plan[0]['brand']} {plan[0]['kind']}, ~{plan[0]['minutes']} min"
                if plan else "nothing waiting to record")
        out.append((60, f"Recording session: `factory batch-record` ({what})"))
    if day.isoformat() in DATED:
        out.append(DATED[day.isoformat()])
    start = launch_day(factory)
    if start:
        n = (day - start).days
        if n in DAY_N:
            m, what = DAY_N[n]
            out.append((m, f"Day {n}: {what}"))
    return out


def collect(factory, day: date | None = None, cap: bool = True) -> dict:
    from .community.store import ensure_schema, inbox
    from .manual import pending
    from .triage import collect as triage
    day = day or date.today()
    items = triage(factory)
    red = [i for i in items if i.urgency == "now" and not i.kind.startswith("post by hand")]
    review = [i for i in items if i.kind.startswith("review")]
    review.sort(key=lambda i: "blocked" not in i.kind)  # blocked ones first: they need a decision
    by_hand = [r for r in pending(factory) if r["due"] or (r.get("scheduled_at") or "")[:10] <= day.isoformat()]
    ensure_schema(factory.db)
    people = inbox(factory.db, limit=50)
    if cap:
        red, review, by_hand, people = red[:5], review[:2], by_hand[:3], people[:8]
    return {"day": day, "red": red, "review": review, "by_hand": by_hand, "people": people,
            "extras": extras(factory, day), "capped": cap,
            "more": {"review": sum(1 for i in items if i.kind.startswith("review")) - len(review)}}


def to_text(r: dict) -> str:
    d = r["day"]
    out = [f"Today, {d:%a %d %b %Y}" + (" · 15 minutes" if r["capped"] else ""), ""]

    out.append(f"1. Triage ({STEP_MIN['triage']} min)")
    out += [f"   - [{i.brand}] {i.kind}: {i.what}" + (f"\n     → {i.how}" if i.how else "") for i in r["red"]] \
        or ["   - Nothing red. Skip ahead."]

    out.append(f"2. Review {len(r['review']) or 2} post(s) ({STEP_MIN['review']} min): watch it, tick every fact, "
               "then Approve & schedule")
    out += [f"   - [{i.brand}] {i.what}" for i in r["review"]] or ["   - Review is empty."]
    if r["more"]["review"] > 0:
        out.append(f"   ({r['more']['review']} more waiting; they'll be here tomorrow)")

    out.append(f"3. Post by hand ({STEP_MIN['by_hand']} min): AI-generated label on, then mark it posted")
    for p in r["by_hand"]:
        out.append(f"   - [{p['brand']}] {p['platform']} pub #{p['id']} · {p['title'][:60]}")
        if p.get("caption"):
            out.append(f"     caption: {p['caption'][:140].replace(chr(10), ' ')}{'…' if len(p['caption']) > 140 else ''}")
        out.append(f"     `factory manual copy {p['id']}` · then `factory manual done {p['id']} --url <link>`")
    if not r["by_hand"]:
        out.append("   - Nothing due by hand.")

    out.append(f"4. People ({STEP_MIN['people']} min): reply yourself; drafts help, you send")
    for c in r["people"]:
        who = c.get("author") or c.get("author_name") or "someone"
        out.append(f"   - [{c.get('brand', '')}] {c.get('platform', '')} · {who}: {(c.get('text') or '')[:90]}"
                   + (" (draft ready)" if c.get("status") == "drafted" else ""))
    out.append("   - Also: any ad-studio reply in your email, the same day.")

    if r["extras"]:
        out += ["", "Plus today"]
        out += [f"   - +{m} min · {what}" for m, what in r["extras"]]
    out += ["", "Skip a day and nothing breaks: posts wait in the queue, and nothing goes out without your approval."]
    return "\n".join(out) + "\n"


def to_markdown(r: dict) -> str:
    lines = to_text(r).splitlines()
    out = [f"# {lines[0]}", ""]
    for ln in lines[1:]:
        if ln[:2] in ("1.", "2.", "3.", "4.") or ln == "Plus today":
            out += ["", f"## {ln}"]
        elif ln.startswith("   - "):
            out.append("- [ ] " + ln[5:])
        else:
            out.append(ln.strip())
    return "\n".join(out) + "\n"


def register(sub, factory_fn) -> None:
    s = sub.add_parser("today", help="your daily routine (GO_LIVE R6) with today's real items")
    s.add_argument("--15min", dest="cap", action="store_true", help="cut each step to what fits in 15 minutes")
    s.add_argument("--date", type=date.fromisoformat, default=None, help="plan another day (YYYY-MM-DD)")
    s.add_argument("--save", action="store_true", help="also write output/today-<date>.md")

    def cmd(a):
        f = factory_fn(a)
        r = collect(f, a.date, a.cap)
        print(to_text(r), end="")
        if a.save:
            path = f.settings.output_dir / f"today-{r['day'].isoformat()}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(to_markdown(r))
            print(path)
    s.set_defaults(func=cmd)
