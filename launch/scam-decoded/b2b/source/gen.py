"""Build the Spot It, Stop It B2B outreach kit from leads.tsv + openers.py.

Mirrors content-factory/ai-ad-studio-v2/: leads.csv, leads_research.csv, pitches/NNN-slug.md,
ALL_PITCHES.md, TRACKER.csv, FOLLOW_UP_SEQUENCE.md, README.md. Nothing is sent.
"""
import csv, datetime as dt, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from openers import OPENERS

OPENERS["Vocal Credit Union"] = ("Vocal's members trust a call \"from Vocal's fraud department\", which is exactly why "
                                 "scammers fake those calls, and a new CEO starting is a good moment to refresh staff training.")

OUT = Path(sys.argv[1])
PER_DAY = 8
START = dt.date(2026, 11, 10)
SKIP = {dt.date(2026, 11, 26), dt.date(2026, 11, 27), dt.date(2026, 12, 24), dt.date(2026, 12, 25)}

FOOTER = """--
{Your Name} · {Brand Name}
{Street address or PO box / registered mailbox}, {City, Postcode}, {Country}
Not interested? Reply "no thanks" and I won't email again."""

# niche -> (group key)
GROUP = {
    "property management": "pm", "insurance agency": "ins", "accounting and tax": "acct",
    "bookkeeping": "books", "bookkeeping and payroll": "books", "dental": "clinic", "chiropractic": "clinic",
    "veterinary": "vet", "title and escrow": "title", "estate planning law": "law",
    "estate and real estate law": "law", "credit union": "cu",
}

G = {
 "pm": dict(
    team="property team", who="whoever handles owner payouts and vendor invoices",
    scenario="an email that looks like it's from an owner or a regular vendor, asking you to send this month's payment to a new bank account",
    subject="a quick scam check for the {name} office",
    tells=[
        "A vendor or owner \"updating bank details\" by email. Call the number you already have on file, never the one in the email.",
        "A tenant applicant who overpays the deposit and asks for the difference back by wire or app. Wait until the original payment fully clears.",
        "A rental listing of yours copied onto Marketplace or Craigslist at a lower rent. Search your own addresses once a week.",
    ]),
 "ins": dict(
    team="agency team", who="whoever takes premium payments and policy changes",
    scenario="a call or email that sounds like a carrier or a client, asking for a policy change, a refund to a new account, or a code read back over the phone",
    subject="a quick scam check for {name}",
    tells=[
        "A \"carrier\" email asking you to log in through a link to see a new commission statement. Go to the carrier portal from your own bookmark.",
        "A client asking for a refund or payout to a different account than the one that paid. Call them back on the number in your system.",
        "Anyone asking an agent to read back a code that was just texted to them. That code is the key to the account; nobody legitimate asks for it.",
    ]),
 "acct": dict(
    team="firm", who="whoever handles client files and payroll",
    scenario="an email that looks like a client asking you to change where their refund or payroll goes, or a fake \"IRS\" notice with a link",
    subject="a quick scam check before tax season at {name}",
    tells=[
        "A client emailing new direct-deposit or refund bank details. Confirm by phone on the number you already have, every time.",
        "An \"IRS\" or \"state revenue\" email with a link or attachment. The IRS starts with a letter in the mail, not an email.",
        "A new \"client\" who sends a W-2 or return as a link to a shared drive and wants it filed fast. Fake documents are how preparers get phished.",
    ]),
 "books": dict(
    team="bookkeeping team", who="whoever runs payroll and pays client bills",
    scenario="an email from a \"client employee\" asking to switch their direct deposit, or an invoice that looks like it's from a vendor you already pay",
    subject="a quick scam check for {name}",
    tells=[
        "An employee emailing to change their direct deposit. Confirm with them by phone or in person before the next payroll run.",
        "A familiar vendor's invoice with new bank details. Call the vendor on the number from an older invoice, not this one.",
        "A \"QuickBooks\" or \"Intuit\" payment email with a link. Open the app yourself instead of clicking.",
    ]),
 "clinic": dict(
    team="front desk", who="your front desk",
    scenario="a call from someone claiming to be an insurer, a supplier or IT support, asking for a login, a patient's details or a payment to a new account",
    subject="a quick scam check for the front desk at {name}",
    tells=[
        "A caller \"from IT\" or \"from the software company\" who needs remote access or a code. Hang up and call your real support number.",
        "A supplier invoice that suddenly has new bank details. Call the supplier on the number from an older invoice.",
        "Someone asking for a patient's details by phone or email because they \"are the insurer\". Call the insurer back on the number on the card.",
    ]),
 "vet": dict(
    team="front desk", who="your front desk and whoever pays supplier invoices",
    scenario="an invoice that looks like it's from a supplier or pharmacy you already use, but with new bank details",
    subject="a quick scam check for the front desk at {name}",
    tells=[
        "A supplier or pharmacy invoice with new payment details. Call the supplier on the number from an older invoice.",
        "A client who overpays by card and asks for the difference back by gift card or app. Refund only to the original card.",
        "A caller \"from IT\" who needs remote access to the practice software. Hang up and call your real support number.",
    ]),
 "title": dict(
    team="closing team", who="everyone who sends or confirms wiring instructions",
    scenario="an email that looks like it's from a buyer, seller or agent with last-minute new wiring instructions",
    subject="a quick wire-fraud check for {name}",
    tells=[
        "Any change to wiring instructions by email, at any stage. Confirm by phone using a number from the file, not the email.",
        "A real estate agent's email that's one letter off. Look at the address itself, not the display name.",
        "A seller who suddenly wants proceeds to a new bank, often in a hurry or after hours. Slow down and verify in person or by a known number.",
    ]),
 "law": dict(
    team="office", who="whoever sends or confirms trust and estate payments",
    scenario="an email that looks like it's from a client, heir or bank asking for a distribution or payment to go to a new account",
    subject="a quick scam check for {name}",
    tells=[
        "Any email changing where a distribution or settlement goes. Confirm by phone with the person, using the number in your file.",
        "An older client calling, worried about a \"grandchild in trouble\" or a \"government\" call. Your staff can be the calm voice who helps them check.",
        "A new \"client\" who wants you to receive a large check and wire some of it back. That's a classic fake-check scam aimed at law firms.",
    ]),
 "cu": dict(
    team="member service team", who="member service staff",
    scenario="a member calling in shaken after someone \"from your fraud department\" asked them to read back a code or move their money to a \"safe account\"",
    subject="a quick member-scam check for {name}",
    tells=[
        "Members being called by \"your fraud department\" and asked to read back a code. Staff can explain, every time, that you never ask for it.",
        "\"Move your money to a safe account\" is always a scam. A short script helps staff say that calmly to a worried member.",
        "Fake texts with a link to \"unlock your account\". Staff can show members how to check the real app instead.",
    ]),
}

NARROW = ("leasing@", "orders@", "rentals@", "request@", "feedback@", "support@", "taxes@", "customerservice@")

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]

def workdays(start, n):
    d = start
    while n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and d not in SKIP:
            n -= 1
    return d

def schedule(count):
    days, d = [], START
    while len(days) * PER_DAY < count:
        if d.weekday() < 5 and d not in SKIP:
            days.append(d)
        d += dt.timedelta(days=1)
    return days

def fmt(d):
    return d.strftime("%a %-d %b")

rows = list(csv.DictReader(open(HERE / "leads.tsv"), delimiter="\t"))
assert len(rows) == 75, len(rows)
for r in rows:
    r["group"] = GROUP[r["niche"]]
    r["opener"] = OPENERS[r["name"]]

# Send order: named contacts first inside each niche, then round-robin across niches so each day is mixed.
buckets = defaultdict(list)
for r in rows:
    buckets[r["group"]].append(r)
for b in buckets.values():
    b.sort(key=lambda r: (r["contact"] == "",))
order_keys = sorted(buckets, key=lambda k: -len(buckets[k]))
ordered = []
while any(buckets.values()):
    for k in order_keys:
        if buckets[k]:
            ordered.append(buckets[k].pop(0))

days = schedule(len(ordered))
for i, r in enumerate(ordered):
    r["rank"] = i + 1
    d0 = days[i // PER_DAY]
    r["d0"], r["d1"], r["d2"] = d0, workdays(d0, 4), workdays(d0, 9)
    r["file"] = f"pitches/{r['rank']:03d}-{slug(r['name'])}.md"
    r["narrow"] = r["email"].lower().startswith(NARROW)
    r["gmail"] = any(x in r["email"].lower() for x in ("@gmail.", "@outlook.", "@mac.com", "@montana.com", "@blackfoot.net", "@yourhealthemail.com"))

def greet(r):
    c = r["contact"].strip()
    return f"Hi {c}," if c else f"Hi {r['name']} team,"

def email1(r):
    g = G[r["group"]]
    narrow = ("\n\nI wasn't sure this is the right inbox for this, so if it isn't, could you pass it along "
              "to whoever runs the office? Thank you.") if r["narrow"] else ""
    return f"""{greet(r)}

{r['opener']}

I put together a free one-page "Verify before you pay" poster for small offices. It's built around the one habit that stops a lot of the scams aimed at a {g['team']}: {g['scenario']}. You check it by calling a number you already have, never the one in the message.

Would you like a copy? It's a printable PDF and there's no catch. Just reply "yes" and I'll send it.{narrow}

Thanks,
{{Your Name}}

{FOOTER}"""

def fu1(r):
    g = G[r["group"]]
    return f"""{greet(r)}

Just bumping this in case it got buried. Happy to send the free "Verify before you pay" poster for {r['name']}. It takes 30 seconds to print and pin up near {g['who']}.

If now isn't a good time, no problem at all.

{{Your Name}}

{FOOTER}"""

def fu2(r):
    g = G[r["group"]]
    t = "\n".join(f"  {i}. {x}" for i, x in enumerate(g["tells"], 1))
    return f"""{greet(r)}

Last note from me. Here are three common scams aimed at offices like yours, free to share with your team whether or not we talk again:

{t}

If you ever want to walk your whole {g['team']} through this, I made a ready-to-run 45-minute session (slides with speaker notes, a quiz, certificates and a one-page verification policy). It's $99 for one office, any number of people: {{Pack link}}

Otherwise I won't email again. Stay safe out there.

{{Your Name}}

{FOOTER}"""

def pitch_md(r):
    notes = []
    if r["narrow"]:
        notes.append("This is a narrow inbox (orders, leasing, support or similar), so Email 1 asks them to pass it along.")
    if r["gmail"]:
        notes.append("They publish a free-mail or ISP address as their business email on their own site. That's fine to use.")
    if "(" in r["detail"]:
        notes.append("See the note in \"What we noticed\" about how the email shows on their site.")
    note_txt = ("\n**Notes:** " + " ".join(notes) + "\n") if notes else ""
    contact = r["contact"] or "Not named on the site (greeting uses the business name)"
    return f"""# {r['rank']}. {r['name']}

| | |
|---|---|
| Contact | {contact} |
| Email | {r['email']} |
| Where the email is published | {r['email_source_url']} |
| Website | {r['website']} |
| Niche | {r['niche']} · {r['city']} |
| What we noticed | {r['detail']} |
| Scam risk to lead with | {r['risk_angle']} |
| Offer | Free "Verify before you pay" poster (PDF), then the $99 Spot It, Stop It pack in the last email |
| Planned send dates | Email 1: {fmt(r['d0'])} · Follow-up 1: {fmt(r['d1'])} · Follow-up 2: {fmt(r['d2'])} |
{note_txt}
**Before you send:** open their site for 60 seconds and check the detail above is still true.
Fill in `{{Your Name}}`, `{{Brand Name}}`, `{{Pack link}}` and the footer address.

## Email 1

**Subject:** {G[r['group']]['subject'].format(name=r['name'])}

```
{email1(r)}
```

## Follow-up 1 (same thread, {fmt(r['d1'])})

```
{fu1(r)}
```

## Follow-up 2, final ({fmt(r['d2'])})

```
{fu2(r)}
```

## If they reply "yes"

Send `Poster-Verify-Before-You-Pay.pdf` (in the training pack's `dist/` folder) with the
"Poster sent" reply in `FOLLOW_UP_SEQUENCE.md`. Mention the $99 pack only if they ask about training.
"""

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "pitches").mkdir(exist_ok=True)
for old in (OUT / "pitches").glob("*.md"):
    old.unlink()

allp = ["# Spot It, Stop It outreach: all 75 pitches\n\nNothing here has been sent. Same content as `pitches/`, in send order.\n"]
for r in ordered:
    md = pitch_md(r)
    (OUT / r["file"]).write_text(md)
    allp.append(md)
(OUT / "ALL_PITCHES.md").write_text("\n\n---\n\n".join(allp))

with open(OUT / "leads.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "contact_name", "email", "website", "niche", "source", "notes"])
    for r in ordered:
        w.writerow([r["name"], r["contact"], r["email"], r["website"], r["niche"], "web-search, verified via own site",
                    f"{r['city']} · {r['detail']} · pitch: {r['file']}"])

with open(OUT / "leads_research.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank", "name", "contact_name", "email", "email_source_url", "website", "city", "niche", "source",
                "specific_detail", "risk_angle", "narrow_inbox", "free_mail_address", "opener_line",
                "tell1", "tell2", "tell3", "pitch_file"])
    for r in ordered:
        t = G[r["group"]]["tells"]
        w.writerow([r["rank"], r["name"], r["contact"], r["email"], r["email_source_url"], r["website"], r["city"],
                    r["niche"], "web-search, verified via own site", r["detail"], r["risk_angle"],
                    "yes" if r["narrow"] else "", "yes" if r["gmail"] else "", r["opener"], *t, r["file"]])

with open(OUT / "TRACKER.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank", "name", "email", "email1_planned", "fu1_planned", "fu2_planned", "email1_sent", "fu1_sent",
                "fu2_sent", "replied", "poster_sent", "pack_bought", "outcome", "status"])
    for r in ordered:
        w.writerow([r["rank"], r["name"], r["email"], r["d0"], r["d1"], r["d2"], "", "", "", "", "", "", "", "not sent"])

mix = Counter(r["niche"] for r in ordered)
states = Counter(r["city"].split(", ")[-1] for r in ordered)
summary = dict(
    mix=", ".join(f"{k} {v}" for k, v in mix.most_common()),
    states=", ".join(f"{k} {v}" for k, v in states.most_common()),
    first=fmt(days[0]), last=fmt(days[-1]), last_fu=fmt(max(r["d2"] for r in ordered)), days=len(days),
    narrow=sum(r["narrow"] for r in ordered), gmail=sum(r["gmail"] for r in ordered),
)
(OUT / "_summary.txt").write_text(repr(summary))
print(summary)
