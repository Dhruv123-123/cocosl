"""Start a new 'scam of the week' alert from the template.

    python3 new_alert.py "Fake toll texts are back" [--date 2027-01-14] [--severity urgent]

Creates content/alerts/NN-<slug>.md with the date, severity and title filled in. Fill the other fields, then build.
"""
import argparse
import datetime as dt
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALERTS = HERE / "content" / "alerts"


def main() -> Path:
    ap = argparse.ArgumentParser()
    ap.add_argument("scam")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--severity", default="warning", choices=["watch", "warning", "urgent"])
    args = ap.parse_args()
    nums = [int(m.group(1)) for p in ALERTS.glob("*.md") if (m := re.match(r"(\d+)-", p.name))]
    slug = re.sub(r"[^a-z0-9]+", "-", args.scam.lower()).strip("-")[:50]
    dest = ALERTS / f"{max(nums, default=0) + 1:02d}-{slug}.md"
    t = (ALERTS / "_TEMPLATE.md").read_text()
    t = t.replace("alert_date: \n", f"alert_date: {args.date}\n", 1)
    t = re.sub(r"^severity: .*$", f"severity: {args.severity}", t, count=1, flags=re.M)
    t = re.sub(r"^scam: .*$", f"scam: {args.scam}", t, count=1, flags=re.M)
    t = re.sub(r"^subject: .*$", f"subject: Scam alert: {args.scam}", t, count=1, flags=re.M)
    dest.write_text(t)
    print(f"Created {dest}. Fill in every field, then run python3 build.py")
    return dest


if __name__ == "__main__":
    main()
