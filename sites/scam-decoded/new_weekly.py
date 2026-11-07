"""Start this week's 'scam of the week' email from the alerts.

    python3 new_weekly.py [--date 2027-01-18] [--lead unpaid-toll-texts]

Creates content/weekly/NN-week-of-<date>.md. It leads with the newest alert no weekly email has used yet (or --lead),
lists up to 3 other recent alerts under "Also going around", and picks an unused quiz question. Write the intro, then build.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTENT = HERE / "content"
WEEKLY = CONTENT / "weekly"


def front(p: Path) -> dict:
    t = p.read_text()
    if not t.startswith("---"):
        return {}
    return {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in t[3:].split("\n---", 1)[0].strip().splitlines())}


def main() -> Path:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--lead", help="alert slug; default: newest alert not yet used as a lead")
    args = ap.parse_args()
    alerts = sorted(((front(p).get("alert_date", ""), re.sub(r"^\d+-", "", p.stem), front(p))
                     for p in (CONTENT / "alerts").glob("[0-9]*.md")), reverse=True)
    alerts = [a for a in alerts if a[0] and a[0] <= args.date]
    if not alerts:
        raise SystemExit("No alerts dated on or before that day. Make one first: python3 new_alert.py \"...\"")
    done = [front(p) for p in WEEKLY.glob("[0-9]*.md")]
    used = {d.get("lead") for d in done}
    lead = args.lead or next((s for _, s, _ in alerts if s not in used), alerts[0][1])
    by_slug = {s: f for _, s, f in alerts}
    if lead not in by_slug:
        raise SystemExit(f"No alert called {lead}. Alerts: {', '.join(by_slug)}")
    also = [s for _, s, _ in alerts if s != lead][:3]
    a = by_slug[lead]
    questions = json.loads((CONTENT / "quiz.json").read_text())["questions"]
    used_q = {int(d["quiz"]) for d in done if d.get("quiz", "").isdigit()}
    topic = {w for w in lead.split("-") if len(w) > 4 and w not in ("texts", "calls", "after")}
    same = lambda q: any(w.rstrip("s") in (q["message"] + q["sender"]).lower() for w in topic)  # don't give away the lead
    quiz = next((str(n) for n, q in enumerate(questions, 1) if n not in used_q and not same(q)), "")
    nums = [int(m.group(1)) for p in WEEKLY.glob("*.md") if (m := re.match(r"(\d+)-", p.name))]
    dest = WEEKLY / f"{max(nums, default=0) + 1:02d}-week-of-{args.date}.md"
    t = (WEEKLY / "_TEMPLATE.md").read_text()
    subject = f"Scam of the week: {a.get('scam', lead)}"
    for k, v in (("send_date", args.date), ("subject", subject), ("preheader", a.get("preheader", "")),
                 ("lead", lead), ("also", ", ".join(also)), ("quiz", quiz)):
        t = re.sub(rf"^{k}:.*$", lambda m: f"{k}: {v}", t, count=1, flags=re.M)
    if not also:
        t = re.sub(r"^also: *\n", "", t, flags=re.M)
    dest.write_text(t)
    print(f"Created {dest}. Write the intro line, then run python3 build.py")
    return dest


if __name__ == "__main__":
    main()
