#!/usr/bin/env python3
"""Fit B2B cold emails into the free slots of the ad studio's outreach calendar. Nothing is sent.

    python3 outreach_dates.py [path/to/ai-ad-studio-v2/OUTREACH_CALENDAR.md]
    python3 outreach_dates.py --own-inbox     # the same plan from a separate B2B inbox with its own cap

The ad studio calendar caps Dhruv's inbox at 10 emails a day, at most 5 of them new first emails. This
script reads how many sends each day already has, then gives each B2B prospect an Email 1 date and two
follow-up dates (about day 4 and day 10) only where a day still has room. It writes OUTREACH_DATES.md
(day by day) and OUTREACH_DATES.csv (one row per prospect). The ad studio files are only read.

Order: accounting firms first (they must hear from us before mid-January or after tax season),
then credit unions 1-30, Scam Watch, schools and colleges, employer partners and employers, then credit unions 31-60.
After the ad studio calendar ends, the full cap of 10 a day (5 new) is free.
"""
import csv
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CAL = Path("/mnt/project-files/content-factory/ai-ad-studio-v2/OUTREACH_CALENDAR.md")
CAP, NEW_CAP = 10, 5
HOLIDAYS = {dt.date(2026, 11, 26), dt.date(2026, 11, 27), dt.date(2026, 12, 24), dt.date(2026, 12, 25),
            dt.date(2026, 12, 31), dt.date(2027, 1, 1), dt.date(2027, 5, 31), dt.date(2027, 7, 5)}
# CPA firms can't read email in the last weeks of tax season
TAX_BLACKOUT = (dt.date(2027, 1, 16), dt.date(2027, 4, 19))
FU_DAYS = (4, 10)
# Agreed split of the shared inbox from 1 Dec 2026: B2B gets 4 of the 10 daily sends (at most 2 new first
# emails), the ad studio keeps 6 (at most 3 new). Before that date B2B only uses leftover room.
SHARE_FROM = dt.date(2026, 12, 1)
B2B_CAP, B2B_NEW = 4, 2


def load_calendar(path: Path):
    used, new, start, end = {}, {}, None, None
    if not path.exists():
        print(f"note: {path} not found, so no ad studio sends are counted", file=sys.stderr)
        return used, new, dt.date(2026, 11, 10), dt.date(2026, 11, 10)
    day = None
    for line in path.read_text().splitlines():
        m = re.match(r"### \w{3} (\d{2} \w{3} \d{4}) · (\d+) sends", line)
        if m:
            day = dt.datetime.strptime(m.group(1), "%d %b %Y").date()
            used[day], new[day] = int(m.group(2)), 0
            start, end = start or day, day
        elif day and re.match(r"\| \d+ \| Email 1 \|", line):
            new[day] += 1
    return used, new, start, end


def prospects():
    def read(p):
        return list(csv.DictReader(open(ROOT / p, newline="")))
    out = []
    for r in read("freelancer-client-letter/PROSPECTS.csv"):
        out.append(("Accounting firm", r["firm"], r["state"], r.get("fit_score", ""), "freelancer-client-letter", True))
    cu = read("credit-union-alert/PROSPECTS.csv")
    for r in cu[:30]:
        out.append(("Credit union", r["credit_union"], r["state"], "", "credit-union-alert", False))
    for r in read("community-scam-watch/PROSPECTS.csv"):
        out.append(("Scam Watch", r["organization"], r["state"], "", "community-scam-watch", False))
    for r in read("schools/PROSPECTS.csv"):
        out.append(("School or college", r["organization"], r["state"], r.get("fit_score", ""), "schools", False))
    for r in read("employer-wellness/PROSPECTS.csv"):
        kind = "Employer partner" if r["type"].startswith("Channel") else "Employer"
        out.append((kind, r["organization"], r["state"], r.get("fit_score", ""), "employer-wellness", False))
    for r in cu[30:]:
        out.append(("Credit union", r["credit_union"], r["state"], "", "credit-union-alert", False))
    return out


def main():
    own = "--own-inbox" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--own-inbox"]
    cal = Path(args[0]) if args else DEFAULT_CAL
    used, new, start, cal_end = load_calendar(cal)
    start = max(start, dt.date(2026, 11, 10))
    if own:
        used, new, cal_end = {}, {}, start - dt.timedelta(1)
    suffix = "_OWN_INBOX" if own else ""

    def workday(d):
        return d.weekday() < 5 and d not in HOLIDAYS

    shared = not own
    b_used, b_new = {}, {}

    def room(d, first):
        if not workday(d):
            return False
        if shared and d >= SHARE_FROM:
            return b_used.get(d, 0) < B2B_CAP and (not first or b_new.get(d, 0) < B2B_NEW)
        u, n = used.get(d, 0), new.get(d, 0)
        return u < CAP and (not first or n < NEW_CAP)

    def take(d, first):
        used[d] = used.get(d, 0) + 1
        b_used[d] = b_used.get(d, 0) + 1
        if first:
            new[d] = new.get(d, 0) + 1
            b_new[d] = b_new.get(d, 0) + 1

    if shared:
        over = [d for d in used if d >= SHARE_FROM and used[d] > CAP - B2B_CAP]
        if over:
            print(f"note: the ad studio calendar still has {len(over)} days after {SHARE_FROM} with more than "
                  f"{CAP - B2B_CAP} sends. Regenerate it with the 6-a-day cap so the total stays at {CAP}.",
                  file=sys.stderr)

    def slot_from(d, first, limit=4):
        for k in range(limit):
            if room(d + dt.timedelta(k), first):
                return d + dt.timedelta(k)
        return None

    rows, day = [], start
    for kind, name, state, fit, product, tax in prospects():
        d = day
        while True:
            if tax and TAX_BLACKOUT[0] <= d <= TAX_BLACKOUT[1]:
                d = TAX_BLACKOUT[1] + dt.timedelta(1)
            if room(d, True):
                fus = [slot_from(d + dt.timedelta(x), False) for x in FU_DAYS]
                if all(fus) and not (tax and any(TAX_BLACKOUT[0] <= f <= TAX_BLACKOUT[1] for f in fus)):
                    break
            d += dt.timedelta(1)
        take(d, True)
        for f in fus:
            take(f, False)
        rows.append(dict(type=kind, prospect=name, state=state, fit_score=fit, product=product,
                         email_1=d.isoformat(), follow_up_1=fus[0].isoformat(), follow_up_2=fus[1].isoformat(),
                         inside_ad_studio_calendar="yes" if fus[1] <= cal_end else "no (after it ends)"))
        if not tax:
            day = max(day, d)  # keep the non-tax queue moving forward in order

    with open(ROOT / f"OUTREACH_DATES{suffix}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    by_day = {}
    for r in rows:
        for step, key in (("Email 1", "email_1"), ("Follow-up 1", "follow_up_1"), ("Follow-up 2", "follow_up_2")):
            by_day.setdefault(r[key], []).append((step, r))
    inside = sum(r["inside_ad_studio_calendar"] == "yes" for r in rows)
    last = max(r["follow_up_2"] for r in rows)
    kinds = {}
    for r in rows:
        k = kinds.setdefault(r["type"], [0, None, None])
        k[0] += 1
        k[1] = min(k[1] or r["email_1"], r["email_1"])
        k[2] = max(k[2] or r["email_1"], r["email_1"])
    if own:
        L = ["# B2B outreach dates from a separate B2B inbox", "",
             "Made by `outreach_dates.py --own-inbox`. **Nothing has been sent, and this plan needs a second inbox "
             "that costs money, so it's only for comparison until Dhruv decides.** Same caps (10 a day, 5 new), "
             "counted separately from the ad studio.", ""]
        L += ["| Group | Prospects | First Email 1 | Last Email 1 |", "|---|---|---|---|"]
        for k, (n, a, b) in kinds.items():
            L.append(f"| {k} | {n} | {a} | {b} |")
        L += ["", f"Last email: {dt.date.fromisoformat(last):%a %d %b %Y}. A new inbox needs 2 to 4 weeks of warm-up "
              "at low volume first, so add that before the first date.", ""]
    else:
        L = ["# B2B outreach dates (sharing the ad studio's inbox)", "",
             f"Made by `outreach_dates.py` from `{cal.name}`. **Nothing has been sent.** Dhruv sends every email by hand.", "",
             f"**The split:** one inbox, at most {CAP} emails a day and {NEW_CAP} new first emails. From "
             f"{SHARE_FROM:%a %d %b %Y}, B2B gets {B2B_CAP} sends a day (at most {B2B_NEW} new) and the ad studio keeps "
             f"{CAP - B2B_CAP} (at most {NEW_CAP - B2B_NEW} new); the ad studio's `OUTREACH_CALENDAR.md` uses the same split. "
             "Before then the ad studio has the whole cap. Follow-ups land about 4 and 10 days after Email 1, on the "
             "next day with B2B room.", "",
             "**Order:** accounting firms first, highest fit score first, so they hear from us before tax season. "
             "Any firm whose 3 emails can't finish by Jan 15 moves to after Apr 19. Then credit unions 1–30, Scam Watch, schools and colleges, "
             "employer partners and employers (by fit score), then credit unions 31–60.", "",
             f"**{len(rows)} prospects, {3 * len(rows)} emails.** Last email: {dt.date.fromisoformat(last):%a %d %b %Y}. "
             f"{sum(r['type'] == 'Accounting firm' and r['follow_up_2'] < TAX_BLACKOUT[0].isoformat() for r in rows)} of the "
             "accounting firms finish before tax season; the rest (the lower fit scores) start after Apr 19.", "",
             "| Group | Prospects | First Email 1 | Last Email 1 |", "|---|---|---|---|"]
        for k, (n, a, b) in kinds.items():
            L.append(f"| {k} | {n} | {a} | {b} |")
        L += ["", "Templates: each product's `COLD_EMAILS.md` (freelancer emails are in its `README.md`). "
              "Stop a prospect's later rows the moment they reply or say no. "
              "`OUTREACH_DATES_OWN_INBOX.md` shows the alternative with a second inbox (costs money; not the plan).", ""]
    for d in sorted(by_day):
        items = by_day[d]
        date = dt.date.fromisoformat(d)
        L.append(f"### {date:%a %d %b %Y} · {len(items)} B2B")
        L.append("")
        for step, r in sorted(items, key=lambda x: x[0] != "Email 1"):
            fit = f" · fit {r['fit_score']}" if r["fit_score"] else ""
            L.append(f"- {step}: {r['prospect']} ({r['type']}, {r['state']}{fit})")
        L.append("")
    (ROOT / f"OUTREACH_DATES{suffix}.md").write_text("\n".join(L))
    print(f"{len(rows)} prospects; {inside} inside the ad studio calendar; last email {last}")
    for k, v in kinds.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
