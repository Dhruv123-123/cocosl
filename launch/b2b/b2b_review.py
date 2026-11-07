#!/usr/bin/env python3
"""Monthly B2B review: one page from PIPELINE.csv and the issue calendars. About 15 minutes, once a month.

    cd launch/b2b
    python3 b2b_review.py                       # this month so far, printed
    python3 b2b_review.py --month 2026-12       # a given month
    python3 b2b_review.py --save                # also writes reviews/<month>.md
    python3 b2b_review.py --append-to ../../output/weekly-review/2026-12-27.md

`--append-to` adds the B2B section to the Sunday one-pager that `factory weekly-review --save` wrote, so the
last Sunday of the month is one read, not two. Nothing is sent or changed apart from the files you name.
Checklist: MONTHLY_REVIEW.md.
"""
import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OPEN = {"Emailed", "Replied", "Sample sent", "Call booked", "Proposal sent", "Not now (revisit)"}
DATE_COLS = ("email_1", "follow_up_1", "follow_up_2")


def month_bounds(month: str) -> tuple[dt.date, dt.date]:
    start = dt.date.fromisoformat(month + "-01")
    nxt = (start.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return start, nxt - dt.timedelta(days=1)


def products():
    for p in sorted(ROOT.glob("*/product.json")):
        yield p.parent


def collect(month: str, today: dt.date) -> dict:
    path = ROOT / "PIPELINE.csv"
    if not path.exists():
        sys.exit("PIPELINE.csv not found: run python3 pipeline_tracker.py first")
    rows = list(csv.DictReader(open(path, newline="")))
    start, end = month_bounds(month)
    in_month = lambda v: bool(v) and start <= dt.date.fromisoformat(v) <= end  # noqa: E731
    planned = sum(in_month(r[c]) for r in rows for c in DATE_COLS if r["stage"] not in ("Do not contact", "Lost"))
    logged = sum(in_month(r["last_contact"]) for r in rows)
    stages: dict = {}
    for r in rows:
        stages[r["stage"]] = stages.get(r["stage"], 0) + 1
    overdue = [r for r in rows if r["stage"] in OPEN | {"Not contacted"} and r["next_step_date"]
               and dt.date.fromisoformat(r["next_step_date"]) < today]
    by_offer: dict = {}
    for r in rows:
        o = by_offer.setdefault(r["offer"], {"prospects": 0, "contacted": 0, "replied": 0, "won": 0, "expected": 0.0})
        o["prospects"] += 1
        o["contacted"] += r["stage"] != "Not contacted"
        o["replied"] += r["stage"] in {"Replied", "Sample sent", "Call booked", "Proposal sent", "Won", "Lost",
                                       "Not now (revisit)"}
        o["won"] += r["stage"] == "Won"
        o["expected"] += float(r["expected_value"] or 0)
    # content runway: the last written issue per product, and deliveries due next month
    nstart, nend = month_bounds((end + dt.timedelta(days=1)).strftime("%Y-%m"))
    runway, due = [], []
    for p in products():
        issues = json.loads((p / "issues.json").read_text())["issues"]
        last = max(i["send_date"] for i in issues)
        runway.append((p.name, last, (dt.date.fromisoformat(last) - today).days))
        due += [(i["deliver_by"], p.name, i["topic"]) for i in issues
                if nstart <= dt.date.fromisoformat(i["deliver_by"]) <= nend]
    return dict(month=month, today=today, planned=planned, logged=logged, stages=stages, overdue=overdue,
                by_offer=by_offer, runway=runway, due=sorted(due),
                dnc=stages.get("Do not contact", 0), won=stages.get("Won", 0))


def to_markdown(r: dict) -> str:
    L = [f"## B2B monthly review: {r['month']}", "",
         f"- Sends planned this month: **{r['planned']}**; contacts logged: **{r['logged']}**"
         + ("  ← log every send in PIPELINE.csv" if r["planned"] and not r["logged"] else ""),
         f"- Clients won so far: **{r['won']}** · Do not contact: **{r['dnc']}**", "",
         "| Offer | Prospects | Contacted | Replied | Won | Reply rate | Expected value |", "|---|---|---|---|---|---|---|"]
    for name, o in r["by_offer"].items():
        rate = f"{o['replied'] / o['contacted']:.0%}" if o["contacted"] else "–"
        L.append(f"| {name} | {o['prospects']} | {o['contacted']} | {o['replied']} | {o['won']} | {rate} | "
                 f"${o['expected']:,.0f} |")
    L += ["", f"**Overdue next steps: {len(r['overdue'])}**"]
    for x in r["overdue"][:10]:
        L.append(f"- {x['next_step_date']} · {x['prospect']} ({x['offer']}): {x['next_step']}")
    if len(r["overdue"]) > 10:
        L.append(f"- … and {len(r['overdue']) - 10} more (filter PIPELINE.xlsx by red dates)")
    L += ["", "**Client deliveries due next month** (only matters once someone has signed):"]
    L += [f"- {d} · {p}: {t}" for d, p, t in r["due"]] or ["- none"]
    L += ["", "**Content runway** (last written issue):"]
    for name, last, days in r["runway"]:
        flag = "  ← write more" if days < 60 else ""
        L.append(f"- {name}: {last} ({days} days){flag}")
    L += ["", "Then work through MONTHLY_REVIEW.md (launch/b2b)."]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--month", default=dt.date.today().strftime("%Y-%m"))
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--append-to", type=Path)
    a = ap.parse_args()
    md = to_markdown(collect(a.month, a.today))
    print(md)
    if a.save:
        d = ROOT / "reviews"
        d.mkdir(exist_ok=True)
        (d / f"{a.month}.md").write_text(md)
        print(f"wrote reviews/{a.month}.md")
    if a.append_to:
        if not a.append_to.exists():
            sys.exit(f"{a.append_to} not found: run `factory weekly-review --save` first")
        text = a.append_to.read_text()
        marker = f"## B2B monthly review: {a.month}"
        if marker in text:
            text = text[:text.index(marker)].rstrip() + "\n"
        a.append_to.write_text(text.rstrip() + "\n\n" + md)
        print(f"added the B2B section to {a.append_to}")


if __name__ == "__main__":
    main()
