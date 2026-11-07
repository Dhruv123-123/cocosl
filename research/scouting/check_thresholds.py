"""Check a brand's weekly numbers against launch_thresholds.json (first 30 days after launch).

Usage:
    python3 check_thresholds.py --day 14 --scorecard card.json [--manual manual.json]

`card.json` is the dict from contentfactory.stats.scorecard(factory, brand), saved as JSON, e.g.:
    python3 -c "import json; from contentfactory.config import Settings; from contentfactory.pipeline import Factory; \
        from contentfactory import stats; f = Factory.create(Settings.load(None)); \
        print(json.dumps(stats.scorecard(f, 'money-made-simple'), default=str))" > card.json
(pass your factory home to Settings.load instead of None if you use one). `manual.json` holds the numbers factory stats doesn't import yet,
typed in from each platform's dashboard; see launch-metrics-30-days.md for the template.

Derived values added before checking: platforms.tiktok.views_per_video and site.signup_rate.
Prints one line per rule that fires, most severe first. Exit code 2 if any "stop" rule fires.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = {"stop": 0, "change": 1, "watch": 2}


def get(d: dict, path: str):
    for part in path.split("."):
        if not isinstance(d, dict) or part not in d:
            return None
        d = d[part]
    return d


def derive(card: dict) -> dict:
    card = json.loads(json.dumps(card or {}))
    tt = get(card, "platforms.tiktok")
    if tt and tt.get("videos"):
        tt["views_per_video"] = tt.get("views", 0) / tt["videos"]
    site = card.get("site") or {}
    if site.get("visitors"):
        site["signup_rate"] = site.get("signups", 0) / site["visitors"]
    return card


def evaluate(rules: list[dict], day: int, card: dict, manual: dict) -> list[dict]:
    data = {"scorecard": derive(card), "manual": manual or {}}
    fired = []
    for r in rules:
        if day < r.get("from_day", 0):
            continue
        src = data[r["source"]]
        v = get(src, r["path"])
        if v is None:
            continue
        m = r.get("min")
        if m and (get(src, m["path"]) or 0) < m["value"]:
            continue
        hit = v < r["value"] if r["op"] == "<" else v > r["value"]
        if hit:
            fired.append({**r, "actual": v})
    return sorted(fired, key=lambda r: ORDER.get(r["severity"], 9))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--day", type=int, required=True, help="days since this brand launched")
    ap.add_argument("--scorecard", type=Path)
    ap.add_argument("--manual", type=Path)
    ap.add_argument("--rules", type=Path, default=HERE / "launch_thresholds.json")
    a = ap.parse_args(argv)
    rules = json.loads(a.rules.read_text())["rules"]
    card = json.loads(a.scorecard.read_text()) if a.scorecard else {}
    manual = json.loads(a.manual.read_text()) if a.manual else {}
    fired = evaluate(rules, a.day, card, manual)
    if not fired:
        print(f"Day {a.day}: no thresholds crossed (rules only check numbers you supplied).")
    for r in fired:
        actual = round(r["actual"], 4) if isinstance(r["actual"], float) else r["actual"]
        print(f"[{r['severity'].upper()}] {r['id']}: {r['path']} = {actual} ({r['op']} {r['value']}). {r['action']}")
    return 2 if any(r["severity"] == "stop" for r in fired) else 0


if __name__ == "__main__":
    sys.exit(main())
