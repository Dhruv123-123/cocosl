"""Start a new 'scam of the week' alert.

From a title (blank fields to fill):
    python3 new_alert.py "Fake toll texts are back" [--date 2027-01-14] [--severity urgent]

From a pasted scam message (drafts every field, plus a card to look at):
    python3 new_alert.py --text "USPS: your package is on hold, pay $1.99: usps-help.top" [--date ...]

--text guesses the scam type from the words in the message, circles up to 3 giveaways (links, money, deadlines,
codes, gift cards, secrecy), and borrows the tells, steps and official source from the newest alert of the same
type. The date defaults to the next free weekday after the last alert. The draft gets `status: draft`, so the site
build skips it, and its card goes to launch/scam-decoded/alert-cards/drafts/. Read every line against the source,
rewrite the example so it's clearly made up (no real names, numbers or links), then delete the status line and build.
"""
import argparse
import datetime as dt
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALERTS = HERE / "content" / "alerts"
HOLIDAYS = {"12-24", "12-25", "01-01"}

# explainer slug -> (words that point to it, short name used for the draft's title)
TYPES = {
    "toll-texts": (["toll", "e-zpass", "ezpass", "sunpass", "fastrak"], "Unpaid toll texts"),
    "package-delivery-texts": (["package", "parcel", "delivery", "usps", "fedex", "ups", "customs", "redeliver"],
                               "Package delivery texts"),
    "family-emergency-scams": (["grandma", "grandpa", "mom", "dad", "accident", "bail", "jail", "lawyer"],
                               "Family emergency calls"),
    "verification-code-scams": (["code", "verification", "verify you"], "Requests for a verification code"),
    "gift-card-scams": (["gift card", "gift cards", "itunes", "google play"], "Gift card payment requests"),
    "government-impostor-scams": (["irs", "social security", "ssn", "medicare", "warrant", "arrest"],
                                  "Government impostor messages"),
    "bank-impersonation-calls": (["bank", "fraud alert", "fraud department", "account locked", "unusual activity"],
                                 "Fake bank fraud alerts"),
    "job-and-task-scams": (["hired", "job", "recruiter", "part-time", "per hour", "/hr", "tasks"], "Fake job offers"),
    "tech-support-scams": (["virus", "infected", "microsoft", "apple support", "computer", "remote"],
                           "Tech support scams"),
    "fake-order-and-refund-emails": (["order", "refund", "subscription", "renewal", "invoice"],
                                     "Fake order and refund messages"),
    "investment-and-crypto-scams": (["crypto", "bitcoin", "invest", "trading", "returns", "profit"],
                                    "Investment and crypto pitches"),
    "online-marketplace-scams": (["buyer", "seller", "marketplace", "pending", "zelle", "listing"],
                                 "Marketplace buyer and seller scams"),
    "fake-charity-scams": (["donate", "donation", "charity", "relief"], "Fake charity appeals"),
    "romance-scams": (["baby", "darling", "my love", "sweetheart", "dear"], "Romance scams"),
    "prize-and-lottery-scams": (["won", "winner", "sweepstakes", "prize", "lottery", "congratulations"],
                                "Prize and lottery scams"),
    "breach-follow-ups": (["breach", "dark web", "leaked"], "Data breach follow-ups"),
}
GIVEAWAYS = [
    r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|top|xyz|info|live|site|online|cc|io|co|us|vip|icu|shop)(?:/\S*)?",  # links
    r"\$\s?\d[\d,]*(?:\.\d\d)?(?:\s(?:fee|deposit|duty|charge|penalty|balance))?",  # money
    r"(?i)\b(?:today|tonight|now|immediately|within \d+ (?:hours?|days?|minutes?)|by \d{1,2}(?::\d\d)? ?(?:am|pm)"
    r"(?: today)?|final notice|last chance|expires?\b[^.,!]*)",  # deadlines
    r"(?i)\b(?:gift cards?|crypto(?:currency)?|bitcoin|wire|zelle|cash app|venmo)\b",  # hard-to-reverse payment
    r"(?i)\b(?:code|pin|password|ssn|social security number)\b",  # secrets
    r"(?i)\b(?:don'?t tell[^.,!]*|keep (?:this|it) (?:quiet|secret|between us))",  # secrecy
    r"(?i)\b(?:suspended|locked|blocked|arrest|warrant|penalty|late fee|license suspension)\b",  # threats
]


def front(p: Path) -> dict:
    t = p.read_text()
    if not t.startswith("---"):
        return {}
    return {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in t[3:].split("\n---", 1)[0].strip().splitlines())}


def guess_type(text: str) -> str:
    low = text.lower()
    scores = {slug: sum(low.count(w) for w in words) for slug, (words, _) in TYPES.items()}
    best = max(scores, key=lambda s: scores[s])
    return best if scores[best] else "lookalike-links"


def find_flags(text: str, limit: int = 3) -> list[str]:
    hits = []
    for pat in GIVEAWAYS:
        for m in re.finditer(pat, text):
            s = m.group(0).strip(" .,!;:")
            if s and not any(a <= m.start() < b or m.start() <= a < m.end() for a, b, _ in hits):
                hits.append((m.start(), m.start() + len(s), s))
                break  # one per kind, so the 3 flags show 3 different giveaways
    return [s for _, _, s in sorted(hits[:limit])]  # kinds in priority order, then shown in reading order


def next_free_weekday(after: str | None = None) -> str:
    taken = {front(p).get("alert_date", "") for p in ALERTS.glob("[0-9]*.md")}
    last = max([t for t in taken if t] or [dt.date.today().isoformat()])
    d = dt.date.fromisoformat(after or last)
    while True:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and d.strftime("%m-%d") not in HOLIDAYS and d.isoformat() not in taken:
            return d.isoformat()


def next_path(slug: str) -> Path:
    nums = [int(m.group(1)) for p in ALERTS.glob("*.md") if (m := re.match(r"(\d+)-", p.name))]
    return ALERTS / f"{max(nums, default=0) + 1:02d}-{slug}.md"


def draft_from_text(text: str, date: str, severity: str) -> Path:
    text = " ".join(text.split())
    kind = guess_type(text)
    models = sorted((front(p) for p in ALERTS.glob("[0-9]*.md")), key=lambda f: f.get("alert_date", ""), reverse=True)
    model = next((m for m in models if m.get("explainer") == kind), None) or next(m for m in models if m.get("alert_date"))
    flags = find_flags(text)
    channel = "text" if re.search(GIVEAWAYS[0], text) else model.get("channel", "text")
    name = TYPES.get(kind, ([], "Look-alike links"))[1]
    fields = {
        "status": "draft",
        "alert_date": date, "severity": severity, "scam": f"{name} are going around", "channel": channel,
        "sender": model.get("sender", "a number you don't know"), "subject": f"Scam alert: {name.lower()}"[:60],
        "preheader": model.get("preheader", ""), "example": text, "flags": " | ".join(flags),
        **{k: model.get(k, "") for k in ("tell_1", "tell_2", "tell_3", "do_1", "do_2", "do_3", "if_already",
                                         "source_title", "source_url")},
        "explainer": kind if any((HERE / "content" / "articles").glob(f"*-{kind}.md")) else "",
    }
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] + "-" + date
    dest = next_path(slug)
    note = ("<!-- DRAFT from new_alert.py --text. Tells, steps and source were borrowed from the newest alert of the same "
            "type: check each against the source, make the example clearly fictional, then delete `status: draft`. -->\n")
    dest.write_text("---\n" + "\n".join(f"{k}: {v}" for k, v in fields.items()) + "\n---\n" + note)
    return dest


def main() -> Path:
    ap = argparse.ArgumentParser()
    ap.add_argument("scam", nargs="?")
    ap.add_argument("--text", help="paste the scam message; drafts the whole alert and a card")
    ap.add_argument("--date")
    ap.add_argument("--severity", default="warning", choices=["watch", "warning", "urgent"])
    ap.add_argument("--no-card", action="store_true")
    args = ap.parse_args()
    if args.text:
        dest = draft_from_text(args.text, args.date or next_free_weekday(), args.severity)
        card = None
        if not args.no_card:
            import make_alert_cards
            card = make_alert_cards.draft_card(dest)
        print(f"Drafted {dest}" + (f"\nCard for review: {card}" if card else "") +
              "\nCheck every line against the source, then delete `status: draft` and run python3 build.py")
        return dest
    if not args.scam:
        ap.error("give a title, or --text with the scam message")
    slug = re.sub(r"[^a-z0-9]+", "-", args.scam.lower()).strip("-")[:50]
    dest = next_path(slug)
    t = (ALERTS / "_TEMPLATE.md").read_text()
    t = t.replace("alert_date: \n", f"alert_date: {args.date or dt.date.today().isoformat()}\n", 1)
    t = re.sub(r"^severity: .*$", f"severity: {args.severity}", t, count=1, flags=re.M)
    t = re.sub(r"^scam: .*$", f"scam: {args.scam}", t, count=1, flags=re.M)
    t = re.sub(r"^subject: .*$", f"subject: Scam alert: {args.scam}", t, count=1, flags=re.M)
    dest.write_text(t)
    print(f"Created {dest}. Fill in every field, then run python3 build.py")
    return dest


if __name__ == "__main__":
    main()
