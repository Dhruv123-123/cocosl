"""Weekly B2B issues from the week's alert-of-the-day cards, in PR #13's issue format.

    python3 build.py                     # every week that has alerts -> issues.json + WEEKS.md
    python3 build.py --week 2027-01-11   # print one week's issue

Each week's Monday-Friday alerts (sites/scam-decoded/content/alerts/, the same ones behind the cards) become one
issue in the schema the white-label newsletters use (launch/b2b/*/issues.json on PR #13: subject, preheader,
headline, example, explain, tell, steps, quick_hits, job, lobby, social, brief, sources as {name, url}). The most
serious alert of the week leads; the others become quick hits. send_date is that Monday; deliver_by is a week
earlier, so a credit union or library has time to approve it. Member-facing text has no Scam Decoded links or
product mentions (PR #13's rule): steps that point at our site are dropped. Drafts (status: draft) are skipped.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent.parent / "sites" / "scam-decoded"
RANK = {"urgent": 0, "warning": 1, "watch": 2}
OURS = re.compile(r"scamdecoded|scam decoded|our free|our checker|link in bio", re.I)
FALLBACK_STEP = "**Report it** at [ReportFraud.ftc.gov](https://reportfraud.ftc.gov)."


def alerts() -> list[dict]:
    # load the site's build.py under its own name, and leave sys.path alone, so it can't shadow another `build`
    name = "scam_decoded_site_build"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, SITE / "build.py")
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    B = sys.modules[name]
    if not B.CFG:
        B.CFG = B.load_config()
    return B.alert_items()


def clean(text: str) -> str:
    """Drop any sentence that points at our own site or products."""
    keep = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s and not OURS.search(s)]
    return " ".join(keep)


def first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s+", text.strip())[0]


def issue(week: list[dict], monday: dt.date, n: int) -> dict:
    lead = sorted(week, key=lambda a: (RANK[a["severity"]], str(a["alert_date"])))[0]
    rest = [a for a in week if a is not lead]
    steps = [clean(lead[f"do_{i}"]) for i in (1, 2)]
    steps = [s for s in steps if s] or [FALLBACK_STEP]
    q, _, rest_ = clean(lead["if_already"]).partition("? ")
    steps.append(f"**{q}?** {rest_}" if rest_ else f"**Already paid or shared something?** {q}")
    if len(steps) < 3:
        steps.insert(-1, FALLBACK_STEP)
    channel = lead["channel"]
    out = {
        "id": f"{monday.isocalendar()[0]}-w{monday.isocalendar()[1]:02d}", "n": n,
        "send_date": monday.isoformat(), "deliver_by": (monday - dt.timedelta(days=7)).isoformat(),
        "source": "Scam Decoded alert cards, week of " + monday.strftime("%b %-d, %Y") + ": " +
                  ", ".join(a["slug"] for a in week),
        "topic": lead["scam"],
        "subject": "Scam alert: " + lead["scam"][0].lower() + lead["scam"][1:] if not lead["scam"].startswith('"')
                   else "Scam alert: " + lead["scam"],
        "preheader": clean(lead["preheader"]) or first_sentence(lead["tell_1"]),
        "headline": lead["scam"],
        "example_label": "What it looks like (made-up example)",
        "example": f"\"{lead['example']}\"",
        "explain": [f"It arrives by {channel}, usually from {lead['sender']}. {lead['tell_1']}",
                    f"{lead['tell_2']} {lead['tell_3']}"],
        "tell": clean(lead["preheader"]) or lead["tell_1"],
        "promise": lead.get("explainer") == "bank-impersonation-calls",
        "steps": steps,
        "quick_hits": [f"**{a['scam']}:** {a['tell_1']} {clean(a['do_1'])}".strip() for a in rest[:4]],
        "job": f"Tell one person who'd get a {channel.split(' or ')[0].split(',')[0]} like this about it. The rule to pass on: "
               f"{clean(lead['do_1']) or lead['tell_1']}",
        "lobby": {"kicker": "Scam alert", "headline": lead["scam"],
                  "bullets": [first_sentence(lead[f"tell_{i}"]) for i in (1, 2)] + [first_sentence(steps[0]).replace("**", "")]},
        "social": {"caption": f"Scam alert: {lead['scam']}. {lead['tell_1']} {clean(lead['do_1'])} "
                              f"Report scams at ReportFraud.ftc.gov.",
                   "alt": f"Scam alert: {lead['scam']}. {first_sentence(clean(lead['do_1']) or lead['tell_1'])}"},
        "brief": {"People may ask": f"\"I got a {channel} like this. Is it real?\"",
                  "What to say": clean(lead["do_1"]) or lead["tell_1"],
                  "Escalate": clean(lead["if_already"])},
        "sources": [{"name": a["source_title"], "url": a["source_url"]} for a in [lead, *rest]],
    }
    return out


def weeks(items: list[dict]) -> dict[dt.date, list[dict]]:
    out: dict[dt.date, list[dict]] = {}
    for a in items:
        d = dt.date.fromisoformat(str(a["alert_date"]))
        if d.weekday() < 5:
            out.setdefault(d - dt.timedelta(days=d.weekday()), []).append(a)
    return dict(sorted(out.items()))


def build() -> list[dict]:
    issues = [issue(w, monday, n) for n, (monday, w) in enumerate(weeks(alerts()).items(), 1)]
    for i in issues:
        member = json.dumps({k: v for k, v in i.items() if k not in ("source", "sources", "id")})
        assert not OURS.search(member), (i["id"], OURS.search(member).group(0))
        assert len(i["steps"]) == 3 and len(i["lobby"]["bullets"]) == 3
    return issues


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", help="any date in the week to print")
    args = ap.parse_args()
    issues = build()
    if args.week:
        d = dt.date.fromisoformat(args.week)
        monday = (d - dt.timedelta(days=d.weekday())).isoformat()
        print(json.dumps(next(i for i in issues if i["send_date"] == monday), indent=1, ensure_ascii=False))
        return
    data = {"_about": "Weekly Scam Watch issues built from the Scam Decoded alert-of-the-day cards by "
                      "launch/scam-decoded/scam-watch/build.py, in the issue schema of launch/b2b/*/issues.json (PR #13). "
                      "The week's most serious alert leads; the rest are quick hits. Member-facing text has no Scam Decoded "
                      "links or products. Examples are made up. Rebuild after adding alerts.",
            "reviewed": dt.date.today().isoformat(), "issues": issues}
    (HERE / "issues.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    rows = ["# Scam Watch weekly issues (from the alert cards)", "",
            "Built by `python3 build.py` from `sites/scam-decoded/content/alerts/`. Hand `issues.json` to the B2B "
            "newsletters (PR #13): the credit union weekly can take each week as is; the monthly library Scam Watch can "
            "pick one week a month. Each client approves before sending.", "",
            "| Week (send) | Deliver by | Lead | Quick hits |", "|---|---|---|---|"]
    rows += [f"| {i['send_date']} | {i['deliver_by']} | {i['headline']} | {len(i['quick_hits'])} |" for i in issues]
    (HERE / "WEEKS.md").write_text("\n".join(rows) + "\n")
    print(f"wrote {len(issues)} weekly issues")


if __name__ == "__main__":
    main()
