"""The one thing a template can't make, for every Scam Decoded long video.

The factory blocks a long video unless a beat carries a chart drawn from the video's own numbers or the
owner's own footage (guardrails.check_original_element). This file says which beat gets which:

* "How the scam actually worked" (8 parts): a chart of the case's own figures, from the court or agency
  release already in the video's sources.
* Every other long video: a screen recording (or camera clip) Dhruv makes. The beat's `footage` path is where
  the file goes; until it exists the render stops with "footage not found" and `factory recordings` lists it.

    python3 long_originals.py   # applies to every pack JSON in launch/scam-decoded/ (safe to rerun)

Generators call apply() too, so a regenerated pack keeps these.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FOOTAGE_DIR = "footage/scam-decoded"
RULES = "Record at 1080p or better, no personal data on screen (blur account numbers, codes and names), 10-30 s."


def chart(title, labels, values, prefix="", suffix="", note=""):
    return {"kind": "bars", "title": title, "labels": labels, "values": values,
            "unit_prefix": prefix, "unit_suffix": suffix, "note": note}


# title prefix -> (beat heading, chart spec)
CHARTS = {
    "How the scam actually worked: the 'bail money' calls": (
        "Cold open", chart("The Montreal bail-call case", ["People charged", "Other states hit"], [25, 40],
                           note="DOJ, D. Vt., Mar 2025; 'more than 40' states shown as 40")),
    "The $26 million pop-up": (
        "What happened next", chart("Restoro and Reimage: the money", ["Settlement", "Refunded"],
                                    [26, 25.5], "$", "M", "FTC, Mar 2024 settlement; refunds announced Mar 2025")),
    "How the scam actually worked: the fake invoices": (
        "How it ended", chart("Fake invoices: taken vs ordered back", ["Taken, 2013-15", "Forfeit", "Restitution"],
                              [120, 49.7, 26.5], "$", "M", "SDNY; 'more than $120M' shown as 120")),
    "'Google will remove your business'": (
        "How it ended", chart("Pointbreak refund checks, Aug 2020", ["Businesses refunded"], [4467],
                              note="FTC, Aug 2020: $700K+ in all, about $158 each")),
    "How the scam actually worked: inside the IRS impersonation": (
        "How it ended", chart("India call-center case, by Jul 2018", ["Sentenced", "Owe restitution"],
                              [24, 22], note="DOJ, S.D. Tex.; restitution nearly $9M")),
    "Inside a pig butchering compound": (
        "The scale", chart("Crypto fraud: one seizure vs a year", ["Bitcoin seized", "US losses, 2024"],
                           [15, 5.8], "$", "B", "Seizure value at the time, DOJ EDNY Oct 2025; US crypto investment fraud losses, FBI 2024")),
    "How the scam actually worked: the money transfer company": (
        "The refunds", chart("Western Union: ordered vs repaid", ["FTC judgment", "DOJ forfeiture",
                                                                  "Repaid, Mar 2020"],
                             [586, 586, 153], "$", "M", "FTC and DOJ, Jan 2017; DOJ remission round Mar 2020")),
    "The 'chairmen' behind": (
        "How it's ending", chart("The romance ring's losses", ["Ring (alleged)", "Chairman 1", "Chairman 2"],
                                 [100, 12.5, 28.5], "$", "M", "SDNY; 'more than $100M' shown as 100")),
}

# title prefix -> (beat heading, what Dhruv records)
FOOTAGE = {
    "Sextortion: what every parent": ("Take It Down", "Screen-record the Take It Down start page (takeitdown.ncmec.org, typed in) and scroll its how-it-works steps. Don't upload anything."),
    "Valentine's Day: the 4 ways": ("If money's gone", "Screen-record reportfraud.ftc.gov (typed in): pick the romance option and stop before any personal details."),
    "IRS scams 2027": ("Check and pay", "Screen-record typing irs.gov and finding the Individual Online Account sign-in and the Payments page. Stop at sign-in."),
    "Owe the IRS?": ("Free help", "Screen-record the Taxpayer Advocate Service site and the Low Income Taxpayer Clinic list on irs.gov (find your state)."),
    "Government imposter scams": ("Social Security", "Screen-record ssa.gov/scam (typed in) and its 'report a scam' button. Stop before the form."),
    "Spring break scams": ("Fake booking sites", "Screen-record a search for a big hotel chain: point at the 'Sponsored' result, then type the chain's real address yourself and compare the domains. Book nothing."),
    "Job scams 2027": ("Fake recruiters", "Screen-record checking a recruiter email domain against a real, public company's careers page."),
    "Filing last minute?": ("Free extensions", "Screen-record irs.gov (typed in): the Free File page and the extension page for Form 4868."),
    "Your consumer rights in 2027": ("Right 3: free credit reports", "Screen-record typing annualcreditreport.com, then the 'request your free credit reports' page. Stop before any personal details."),
    "After the storm": ("Hiring safely", "Screen-record your state's contractor license lookup: search a common business name and show the license status field."),
    "After Tax Day": ("Refund trackers", "Screen-record typing irs.gov and opening Where's My Refund. Stop before entering anything."),
    "How 1 hacked email": ("Two-step", "Screen-record turning on 2-step verification in your own email account settings (blur codes and the address)."),
    "Moving this spring?": ("Check a mover", "Screen-record the FMCSA mover search: search a moving company by name and show its USDOT number and complaint history link."),
    "Older Americans Month": ("How families help", "Screen-record your own phone's settings: silence unknown callers and the carrier's spam filter."),
    "Medicare fraud": ("Read the statement", "Medicare's own sample Medicare Summary Notice on screen: circle where fake tests and equipment would show up (face cam intro and outro)."),
    "Graduates' guide": ("The chat interview", "Screen-record checking a real, public company's careers page and a recruiter's email domain, then a reverse image search of a listing photo."),
    "Veterans' benefit scams": ("Free help", "Screen-record VA's accreditation search (search a common surname, no personal data) and a charity watchdog lookup."),
    "The summer travel scam guide": ("Skimmers", "Film a real gas pump check: wiggle the card reader, look at the seal. Then screen-record finding an airline's help number inside its own app."),
    "9 holiday scams": ("1. Fake stores", "Screen-record checking an unfamiliar store: search its name plus 'scam' and 'reviews', then open its contact and returns pages."),
    "How to protect your parents": ("Phone settings", "Screen-record your own phone: silence unknown callers, the carrier spam filter, and adding a contact as a favorite."),
    "Identity theft recovery": ("3. Report", "Screen-record IdentityTheft.gov (typed in): start a report, pick a category, stop before personal details."),
    "Credit freeze vs fraud alert": ("Freeze", "Screen-record typing one credit bureau's freeze page address and finding the freeze button. Stop at sign-in."),
    "Teens and summer money": ("Settings", "Screen-record the security settings in a payment app and a game account on your own phone (2-step verification, private payments, parent PIN)."),
    "Before Father's Day": ("Blocking calls", "Screen-record your own call log of warranty robocalls (numbers blurred), then blocking and reporting one."),
    "Official-looking scams": ("The pattern", "Film from above: three fictional mock-ups on your desk (a call script, a deed letter, a storage email), marking the tells with a pen. Then your phone's real storage screen."),
    "4th of July weekend scams": ("Settings", "Screen-record two settings on your own phone: making a payment app private, and the 'report ad' menu in a social app."),
    "7 scams that hit after the holidays": ("6. Balance checks", "Screen-record typing the balance-check address printed on the back of your own gift card (blur the card number)."),
    "Find and cancel every subscription": ("Place 2: app stores", "Screen-record your own phone's subscriptions screen in the app store settings (blur prices if you like)."),
    "Tax season scams 2027": ("The IP PIN", "Screen-record irs.gov (typed in): the Get an IP PIN page. Stop at sign-in."),
    "How to file your taxes safely": ("Step 3: choose", "Screen-record the IRS Directory of Federal Tax Return Preparers: search your ZIP code and show the credentials column."),
    "How a wrong-number text": ("Stage 3: the tip", "Screen-record FINRA BrokerCheck and the SEC's investor.gov search: look up a made-up 'platform' name and show that nothing comes back."),
    "Romance scams before Valentine's": ("Video and AI", "Screen-record a reverse image search of a stock photo of a person, showing where else the photo appears."),
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48].strip("-")


def _find(table: dict, title: str):
    hits = [v for k, v in table.items() if title.startswith(k)]
    return hits[0] if hits else None


def apply(items: list[dict]) -> list[dict]:
    """Add the chart or footage beat to each long video in a pack (in place; returns items)."""
    from long_examples import apply_examples, examples
    table = examples()
    for it in items:
        if it.get("format") != "long":
            continue
        apply_examples(it, table)
        script = it["script"]
        title = script["title"]
        heads = [s["heading"] for s in script["segments"]]
        if (c := _find(CHARTS, title)):
            seg = script["segments"][heads.index(c[0])]
            seg["chart"] = c[1]
            script["original_element"] = f"A chart of the case's own figures on the '{c[0]}' beat ({c[1]['note']})."
        elif (f := _find(FOOTAGE, title)):
            k = heads.index(f[0])
            seg = script["segments"][k]
            seg["footage"] = f"{FOOTAGE_DIR}/{slug(title)[:40].strip('-')}--{slug(f[0])}.mp4"
            script["original_element"] = f"{f[1]} {RULES} Save it as {seg['footage']}."
        else:
            raise SystemExit(f"long video without a chart or footage plan: {title}")
    return items


def plan_dates(pack: Path) -> dict[int, str]:
    """Older packs carry no post_on: read each long video's Sunday from its posting plan ('#n' = index)."""
    import datetime as dt
    plan = HERE / f"POSTING_PLAN_{pack.stem.upper().replace('WEEKS-', 'WEEKS_')}.md"
    out = {}
    if plan.exists():
        for line in plan.read_text().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            m = re.match(r"\w{3} (\w{3}) (\d+)$", cells[0]) if len(cells) > 4 else None
            n = re.match(r"#(\d+)", cells[-1]) if m else None
            if m and n:
                mon = dt.datetime.strptime(m.group(1), "%b").month
                out[int(n.group(1))] = dt.date(2026 if mon >= 11 else 2027, mon, int(m.group(2))).isoformat()
    return out


def shot_list(rows: list[tuple[str, dict]]) -> str:
    out = ["# Scam Decoded: recordings for the long videos", "",
           "Every long video needs one thing a template can't make, or the factory blocks it. The 8 \"How the scam "
           "actually worked\" parts carry a chart of the case's figures. Every other long video waits on one "
           "recording from Dhruv, listed here soonest first. Save each file at the path shown (relative to the "
           f"factory home), then render. {RULES}", "", "| When | Video | Beat | Record | Save as |",
           "|---|---|---|---|---|"]
    for when, it in sorted(rows, key=lambda r: r[0] or "9999"):
        when = when or "see posting plan"
        segs = it["script"]["segments"]
        k = next(i for i, s in enumerate(segs) if s.get("footage"))
        what = _find(FOOTAGE, it["script"]["title"])[1]
        out.append(f"| {when or 'see plan'} | {it['script']['title']} | {k + 1}. {segs[k]['heading']} | {what} | "
                   f"`{segs[k]['footage']}` |")
    return "\n".join(out) + "\n"


def main():
    rows = []
    for p in sorted(HERE.glob("*.json")):
        try:
            data = json.loads(p.read_text())
        except ValueError:
            continue
        if not isinstance(data, list) or not any(isinstance(i, dict) and i.get("format") == "long" for i in data):
            continue
        apply(data)
        raw = p.read_text()
        indent = len(raw.split("\n", 1)[1]) - len(raw.split("\n", 1)[1].lstrip(" ")) if "\n" in raw else 1
        ascii_only = "\\u" in raw
        p.write_text(json.dumps(data, indent=indent or 1, ensure_ascii=ascii_only) + "\n")
        print("updated", p.name)
        dates = plan_dates(p)
        rows += [((i.get("post_on") or dates.get(n, ""))[:10], i) for n, i in enumerate(data)
                 if i.get("format") == "long" and any(s.get("footage") for s in i["script"]["segments"])]
    (HERE / "LONG_VIDEO_RECORDINGS.md").write_text(shot_list(rows))
    print(f"{len(rows)} recordings listed in LONG_VIDEO_RECORDINGS.md")


if __name__ == "__main__":
    sys.exit(main())
