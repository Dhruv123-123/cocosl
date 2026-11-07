"""Build the 1099 Money B2B outreach kit from leads_source.tsv + openers.py.

    python3 launch/1099-money/b2b/build_b2b.py            # writes into launch/1099-money/b2b/
    python3 launch/1099-money/b2b/build_b2b.py --out DIR  # writes the kit somewhere else

Nothing is sent. Dhruv sends every email by hand from his own inbox.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys

sys.path.insert(0, str(HERE))
from openers import OPENERS  # noqa: E402

START = dt.date(2026, 11, 11)  # Wed 11 Nov 2026
PER_DAY = 8
FU1_GAP, FU2_GAP = 4, 9  # working days after Email 1
HOLIDAYS = {dt.date(2026, 11, 26), dt.date(2026, 11, 27), dt.date(2026, 12, 24), dt.date(2026, 12, 25),
            dt.date(2026, 12, 31), dt.date(2027, 1, 1)}

MEMBER_PRICE = "$39"        # proposed: $49 bundle with a member code (code MEMBERS, $10 off)
GROUP_SMALL = "$199"        # proposed: group license, up to 25 members
GROUP_LARGE = "$499"        # proposed: group license, up to 100 members

FOOTER = """--
{Your Name} · 1099 Money
{Street address or PO box / registered mailbox}, {City, Postcode}, {Country}
Not interested? Reply "no thanks" and I won't email again."""

# Who the members are, and the one tip in Follow-up 2 written for them.
CATEGORIES = {
    "coworking": dict(
        niche="coworking space",
        people="members who freelance or run their own small business",
        short="your freelance and self-employed members",
        tip="If you use a coworking membership for your business, it's generally a deductible business expense on Schedule C. Keep the receipts with the rest of your records.",
    ),
    "translators": dict(
        niche="translators & interpreters association",
        people="independent translators and interpreters",
        short="your freelance members",
        tip="Clients abroad usually don't send a 1099, and agencies sometimes forget. That income still counts, so log every payment the day it lands, in dollars, with the exchange rate you used.",
    ),
    "editors": dict(
        niche="editors & writers association",
        people="freelance editors and writers",
        short="your freelance members",
        tip="1099s don't always cover every client (a client who paid you less than $2,000 in 2026 doesn't have to send one), but all of it is income. Your own log is the record that counts.",
    ),
    "journalists": dict(
        niche="journalists association",
        people="freelance journalists and authors",
        short="your freelance members",
        tip="Royalties, advances, kill fees and speaking fees all count as income. Advances and royalties can be self-employment income when writing is your business, so plan your set-aside for them too.",
    ),
    "creatives": dict(
        niche="creative professionals association",
        people="illustrators, designers and other working creatives",
        short="your freelance members",
        tip="Software subscriptions, a share of your phone and internet, and equipment used for client work are generally deductible business expenses. Expenses lower both income tax and the 15.3% self-employment tax.",
    ),
    "medical": dict(
        niche="medical writers association",
        people="freelance medical writers and editors",
        short="your freelance members",
        tip="Continuing education, membership dues and certification costs that keep up your skills in your current line of work are generally deductible business expenses.",
    ),
    "consultants": dict(
        niche="independent consultants association",
        people="independent consultants",
        short="members in private practice",
        tip="Expenses lower both income tax and the 15.3% self-employment tax, so every deductible professional cost (dues, campus visits for client work, software) saves more than it looks like.",
    ),
    "community": dict(
        niche="freelancer & founder community",
        people="freelancers and early-stage founders",
        short="your freelance members",
        tip="If you're paid through Stripe, PayPal or a marketplace, the 1099-K threshold for 2026 is back to $20,000 and 200 payments, so many people won't get one. The income still counts.",
    ),
}


README = """# 1099 Money B2B outreach: coworking spaces and freelancer groups

Everything you need to offer the free **2027 Freelancer Tax Calendar** to {n} coworking spaces and
freelancer associations, and then the **$49 Freelancer Money Bundle** as a member perk. **Nothing here
has been sent.** You send every email yourself, by hand, from your own inbox.

## What's in here

| File | What it is |
|---|---|
| `leads.csv` | {n} researched coworking spaces and freelancer groups, in the factory's import format (`name,contact_name,email,website,niche,source,notes`). Sorted in send order. |
| `leads_research.csv` | Same leads with the research: where the email is published, what we noticed, flags, narrow-inbox and free-mail markers, the opener and the subject line. |
| `pitches/NNN-name.md` | One file per lead: Email 1, Follow-up 1, Follow-up 2 and planned send dates. Numbered in send order. |
| `ALL_PITCHES.md` | Every pitch in one file, for scrolling. |
| `TRACKER.csv` | Send schedule (8 new a weekday from Wed 11 Nov) with blank columns for sent dates, replies, calendar sent, blurb shared, offer, bundle sold and outcome. |
| `FOLLOW_UP_SEQUENCE.md` | The sequence (day 0 / 4 / 9), plus what to send for every kind of reply, including the member blurb. |
| `GROUP_LICENSE.md` | Draft member-code and group-license terms and proposed prices. |
| `build_b2b.py`, `openers.py`, `leads_source.tsv` | The source. Edit a lead or an opener, then run `python3 launch/1099-money/b2b/build_b2b.py`. |

## The offer

- **Email 1** gives something useful first: the free 2027 Freelancer Tax Calendar PDF
  (`apps/freelance-tax/downloads/freelancer-tax-calendar-2027.pdf`), to share with members, plus a
  ready-to-paste newsletter blurb. No link in the first email, so it stays out of spam folders.
  The hook is real and timely: the 4th estimated payment for 2026 is due Fri Jan 15, 2027.
- **Follow-up 1** is a short bump.
- **Follow-up 2** gives three tax habits for their kind of member for free (the third is written for
  each group: coworking members, translators, editors, journalists, designers, medical writers,
  consultants), then offers the bundle once: a member code ({member} instead of $49) or a group license
  ({small} for up to 25, {large} for up to 100). **These prices are proposals.** Change them in
  `build_b2b.py` (`MEMBER_PRICE`, `GROUP_SMALL`, `GROUP_LARGE`) and rebuild, or find-and-replace.

## How the leads were found

Public web search and local "best coworking in ..." guides were used to find names. Then each
organization's **own website** was opened to check that it's active, serves freelancers or small
businesses, and publishes an email on its own site (the page is in `leads_research.csv` →
`email_source_url`). No scraping tools, no bought lists, no guessed emails, and no personal addresses
from anywhere else. {ata} translator-association chapters publish their email only in the American
Translators Association's chapter directory (atanet.org), which is the official parent body; those
are marked in `flags`. Chains (WeWork, Regus, Industrious, Spaces, Expansive) were skipped, and so were
spaces that have closed, sites that now redirect to unrelated pages, and contact-form-only sites.

**Mix:** {mix}.

Many coworking spaces publish only a contact form, so they're under-represented. Translator and
interpreter associations (ATA chapters and affiliates) were the easiest to verify and are a strong fit:
most members are independent contractors who pay quarterly estimated tax.

## Before you send anything (one-time setup)

1. **Put the bundle on sale** and paste the real link in place of `{{Bundle link}}` everywhere.
   Listing: `launch/1099-money/products/bundle/LISTING.md`.
2. **Decide the member and group prices** (see `GROUP_LICENSE.md`) and set up the member code.
3. **Fill in** `{{Your Name}}` and the footer postal address (a PO box or virtual mailbox is fine). The
   footer with an address and opt-out line is required by CAN-SPAM.
4. **Have the calendar ready to attach**, and once the site is live, put the free page's URL in place of
   `{{Calendar link}}` in the blurb (`FOLLOW_UP_SEQUENCE.md`, Branch A).
5. Send from a normal inbox on your own domain if you can. If the domain is new, start at 4 a day.

## Daily routine (about 30 minutes)

1. Open `TRACKER.csv` and filter `email1_planned` = today.
2. For each lead, open its pitch file, spend 60 seconds on their site to check the detail is still true,
   tweak the opener if needed, and send Email 1.
3. Send any Follow-up 1s and 2s due today, **only to people who haven't replied**.
4. Write the sent date in the tracker. Anyone who says no or stop: `do_not_contact`, never again.
5. Reply to yeses the same day using `FOLLOW_UP_SEQUENCE.md` (Branch A).

## Things to know about specific leads

- **Role inboxes:** {narrow} leads publish only a `president@`, `board@`, `admin@`, `help@` or
  `support@` address. Their Email 1 already asks them to pass it to whoever runs the newsletter.
  Associations are volunteer-run, so all association emails include that line.
- **Free-mail addresses:** {gmail} groups publish a Gmail address on their own site (or in the ATA
  directory) as their official contact. That's fine to use.
- **Named people:** Switchboard (Emily), Ward4 (Kristen) and FatPipe (Laura) publish a named staff
  address, so the greeting uses the first name. COVE and the VIP Center also show a name, but their
  main address is a shared inbox, so the greeting uses the team.
- **Possibly stale:** {stale} leads have a site with no 2026 activity (footer 2024 or 2025, or
  undated posts). They're at the end of the send order. Check the site first, and skip any that look
  closed.
- **Decoded addresses:** The Hivery and IECA hide their email behind spam protection; the address in
  the list is what their link decodes to.
- **Big national groups** (Freelancers Union, EFA, NWU, ASJA, AMWA, Graphic Artists Guild, SEJ, NAJIT,
  IECA) get far more pitches and may have a formal partner process. If they reply, ask whether they
  have a member-benefits program, and quote a bigger-group price (see `GROUP_LICENSE.md`).

## Rules for every message

- The calendar and bundle are educational. Never say they make anyone compliant, guarantee no penalty,
  or replace an accountant (Branch C).
- Every tax figure in these emails is a 2026 federal rule as of November 2026: the Jan 15, 2027 payment,
  the 100% / 110% safe harbor, the $2,000 1099-NEC threshold, and the $20,000 / 200-payment 1099-K
  threshold. Recheck irs.gov if you send any of these after January.
- No fake urgency, no invented testimonials, and no "other spaces already offer it" until one actually does.
- No affiliate links anywhere in this kit.

## What to expect

Honest numbers for hand-written cold email to small organizations: a 5 to 10% reply rate is a good
result, and a free, timely calendar should get more yeses than a sales pitch would. From {n} leads, a
realistic target is 5 to 10 replies, 4 to 8 groups sharing the calendar (each one puts it in front of
dozens or hundreds of freelancers, some of whom join the email list), and 0 to 2 member codes or group
licenses in the first month. The real value is learning which kind of group says yes, so that the next
75 can all come from it.
"""


def category(row: dict) -> str:
    n = row["name"].lower()
    if row["type"] == "coworking":
        return "coworking"
    if row["type"] == "community":
        return "community"
    if "translat" in n or "interpret" in n or "ata" in n.split():
        return "translators"
    if "editor" in n:
        return "editors"
    if "journalist" in n or "authors" in n or "writers union" in n:
        return "journalists"
    if "graphic" in n:
        return "creatives"
    if "medical" in n:
        return "medical"
    if "consultant" in n:
        return "consultants"
    raise ValueError(f"no category for {row['name']}")


def working_days(start: dt.date):
    d = start
    while True:
        if d.weekday() < 5 and d not in HOLIDAYS:
            yield d
        d += dt.timedelta(days=1)


def add_working(d: dt.date, n: int) -> dt.date:
    it = working_days(d + dt.timedelta(days=1))
    for _ in range(n - 1):
        next(it)
    return next(it)


def fmt(d: dt.date) -> str:
    return d.strftime("%a %-d %b")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def short_name(name: str) -> str:
    """Short name for subject lines: 'Upper Midwest Translators and ...' -> 'UMTIA' where the site uses one."""
    return SHORT.get(name, name)


SHORT = {
    "Upper Midwest Translators and Interpreters Association": "UMTIA",
    "Northwest Translators and Interpreters Society": "NOTIS",
    "Austin Area Translators and Interpreters Association": "AATIA",
    "Carolina Association of Translators and Interpreters": "CATI",
    "Midwest Association of Translators and Interpreters": "MATI",
    "California Association of Professional Interpreters and Translators": "CAPIT",
    "Atlanta Association of Interpreters and Translators": "AAIT",
    "Delaware Valley Translators Association": "DVTA",
    "Houston Interpreters and Translators Association": "HITA",
    "Editorial Freelancers Association": "EFA",
    "American Society of Journalists and Authors": "ASJA",
    "National Writers Union": "NWU",
    "Society of Environmental Journalists": "SEJ",
    "American Medical Writers Association": "AMWA",
    "Association of Translators and Interpreters of Florida": "ATIF",
    "Colorado Interpreters and Translators Association": "CITA",
    "Mid-America Chapter of ATA": "MICATA",
    "National Capital Area Translators Association": "NCATA",
    "New York Circle of Translators": "NYCT",
    "Association of Translators and Interpreters in the San Diego Area": "ATISDA",
    "New Mexico Translators and Interpreters Association": "NMTIA",
    "Oregon Society of Translators and Interpreters": "OSTI",
    "Tennessee Association of Professional Interpreters and Translators": "TAPIT",
    "Kentucky Interpreter and Translator Association": "KITA",
    "National Association of Judiciary Interpreters and Translators": "NAJIT",
    "Independent Educational Consultants Association": "IECA",
    "Northwest Editors Guild": "the Guild",
}


def greeting(row: dict) -> str:
    c = row["contact"].strip()
    local = row["email"].split("@")[0].lower()
    if c and c.split()[0].lower() == local:
        return f"Hi {c.split()[0]},"
    sn = short_name(row["name"])
    return f"Hi {row['name'] if sn.startswith('the ') else sn} team,"


def is_narrow(row: dict) -> bool:
    return row["email"].split("@")[0].lower() in {"support", "help", "webmaster", "president", "board", "admin"}


def load() -> list[dict]:
    with open(HERE / "leads_source.tsv", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        r["cat"] = category(r)
        r["opener"] = OPENERS[r["name"]]
    missing = set(OPENERS) - {r["name"] for r in rows}
    assert not missing, f"openers with no lead: {missing}"
    emails = [r["email"].lower() for r in rows]
    assert len(emails) == len(set(emails)), "duplicate email"
    return rows


def order(rows: list[dict]) -> list[dict]:
    """Clean leads first, flagged ones last; alternate coworking spaces and associations so each day is mixed."""
    clean = [r for r in rows if not r["flags"]]
    flagged = [r for r in rows if r["flags"]]
    out = []
    for group in (clean, flagged):
        cw = [r for r in group if r["cat"] == "coworking"]
        other = [r for r in group if r["cat"] != "coworking"]
        while cw or other:
            for src in (cw, other):
                if src:
                    out.append(src.pop(0))
    return out


def emails_for(r: dict, dates: dict) -> dict:
    c = CATEGORIES[r["cat"]]
    sn = short_name(r["name"])
    hi = greeting(r)
    pass_on = ("\n\nIf someone else looks after member perks or the newsletter, I'd be grateful if you could pass this along."
               if is_narrow(r) or r["cat"] != "coworking" else "")
    e1_subject = f"a free 2027 tax calendar for {'Guild' if sn == 'the Guild' else sn} members"
    e1 = f"""{hi}

{r['opener']}

Mid-January is when a lot of self-employed people get caught out. The 4th estimated tax payment for 2026 is due Fri Jan 15, 2027, about two weeks before most 1099s even arrive.

I made a free, printable 2027 Freelancer Tax Calendar: every federal date a US freelancer needs next year, what to do on each one, and a 15-minute routine to run before each payment. It's educational, not tax advice.

Would it be useful for {c['short']}? Reply "yes" and I'll send the PDF, plus a short blurb you can paste into a newsletter or member Slack. You're welcome to share it with members as-is.{pass_on}

Thanks,
{{Your Name}}

{FOOTER}"""
    fu1 = f"""{hi}

Just bumping this in case it got buried. Happy to send the free 2027 Freelancer Tax Calendar for {sn}, with a ready-to-paste blurb for members. The January 15 payment is easy to miss over the holidays, so it's a good one to share before then.

If now isn't a good time, no problem at all.

{{Your Name}}

{FOOTER}"""
    fu2 = f"""{hi}

Last note from me. Here are three tax habits that help {c['people']}, free to share whether or not we talk again:

  1. Set aside a fixed share of every client payment the day it arrives, in a separate account. The calendar has a table to pick the right percentage.
  2. Paying 100% of last year's total tax (110% if last year's AGI was over $150,000) in four on-time payments generally avoids the underpayment penalty, even if this year's bill is bigger.
  3. {c['tip']}

If you'd ever like to offer members something more, I make the Freelancer Money Bundle ($49): a quarterly tax tracker, a tax-aware rate calculator, a proposal, contract and invoice set, and 14 client email scripts. I could set it up for {sn} in one of two ways:

  - a member code, so your members get it for {MEMBER_PRICE}, or
  - a group license you give members as a perk: {GROUP_SMALL} for up to 25 people, {GROUP_LARGE} for up to 100.

Here's the bundle: {{Bundle link}}

Otherwise I won't email again. Good luck with the new year.

{{Your Name}}

{FOOTER}"""
    return dict(e1_subject=e1_subject, e1=e1, fu1=fu1, fu2=fu2)


def pitch_md(i: int, r: dict, d: dict, m: dict) -> str:
    c = CATEGORIES[r["cat"]]
    contact = r["contact"] or "(none named; greeting uses the team)"
    return f"""# {i}. {r['name']}

| | |
|---|---|
| Contact | {contact} |
| Email | {r['email']} |
| Where the email is published | {r['email_source_url']} |
| Website | {r['website']} |
| Type | {c['niche']} · {r['city']} |
| What we noticed | {r['detail']} |
| Flags | {r['flags'] or 'none'} |
| Offer | Free 2027 Freelancer Tax Calendar (PDF) + member blurb, then the $49 bundle as a member code or group license in the last email |
| Planned send dates | Email 1: {fmt(d['e1'])} · Follow-up 1: {fmt(d['fu1'])} · Follow-up 2: {fmt(d['fu2'])} |

**Before you send:** open their site for 60 seconds and check the detail above is still true.
Fill in `{{Your Name}}`, `{{Bundle link}}` and the footer address.

## Email 1

**Subject:** {m['e1_subject']}

```
{m['e1']}
```

## Follow-up 1 (same thread, {fmt(d['fu1'])})

```
{m['fu1']}
```

## Follow-up 2, final (same thread, {fmt(d['fu2'])})

```
{m['fu2']}
```

## If they reply "yes"

Send `freelancer-tax-calendar-2027.pdf` (in `apps/freelance-tax/downloads/`) with Branch A in
`FOLLOW_UP_SEQUENCE.md`, which includes the member blurb. Mention the bundle only if they ask.
"""


def build(out: Path) -> list[dict]:
    rows = order(load())
    out.mkdir(parents=True, exist_ok=True)
    pdir = out / "pitches"
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir()
    days = working_days(START)
    day = None
    all_md = ["# All pitches: 1099 Money B2B outreach\n",
              "Every pitch in send order. Nothing here has been sent. See `README.md` first.\n"]
    leads, research, tracker = [], [], []
    for i, r in enumerate(rows, 1):
        if (i - 1) % PER_DAY == 0:
            day = next(days)
        d = dict(e1=day, fu1=add_working(day, FU1_GAP), fu2=add_working(day, FU2_GAP))
        m = emails_for(r, d)
        fname = f"{i:03d}-{slug(r['name'])[:48].strip('-')}.md"
        md = pitch_md(i, r, d, m)
        (pdir / fname).write_text(md)
        all_md.append(md)
        all_md.append("\n---\n")
        c = CATEGORIES[r["cat"]]
        greet_name = greeting(r)[3:-1]
        leads.append({
            "name": r["name"], "contact_name": greet_name if not greet_name.endswith(" team") else "",
            "email": r["email"], "website": r["website"], "niche": c["niche"],
            "source": "web-search, verified via own site" if "ATA chapter directory" not in r["flags"]
            else "ATA chapter directory (atanet.org)",
            "notes": f"{r['city']} · {r['detail']} · pitch: pitches/{fname}",
        })
        research.append({
            "rank": i, "name": r["name"], "type": r["type"], "category": r["cat"], "city": r["city"],
            "email": r["email"], "email_source_url": r["email_source_url"], "website": r["website"],
            "contact": r["contact"], "what_we_noticed": r["detail"], "flags": r["flags"],
            "narrow_inbox": "yes" if is_narrow(r) else "",
            "free_mail": "yes" if r["email"].lower().endswith("@gmail.com") else "",
            "opener": r["opener"], "email1_subject": m["e1_subject"], "pitch_file": f"pitches/{fname}",
        })
        tracker.append({
            "rank": i, "name": r["name"], "email": r["email"],
            "email1_planned": d["e1"].isoformat(), "fu1_planned": d["fu1"].isoformat(),
            "fu2_planned": d["fu2"].isoformat(), "email1_sent": "", "fu1_sent": "", "fu2_sent": "",
            "replied": "", "calendar_sent": "", "blurb_shared": "", "offer": "", "bundle_sold": "",
            "outcome": "", "status": "not sent",
        })
    for name, data in (("leads.csv", leads), ("leads_research.csv", research), ("TRACKER.csv", tracker)):
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    (out / "ALL_PITCHES.md").write_text("\n".join(all_md))
    from collections import Counter
    labels = {"coworking": "coworking spaces", "translators": "translator and interpreter associations",
              "editors": "editors' groups", "journalists": "writers' and journalists' groups",
              "creatives": "creative guild", "medical": "medical writers' association",
              "consultants": "independent consultants' association", "community": "freelancer and founder communities"}
    cnt = Counter(r["category"] for r in research)
    mix = ", ".join(f"{labels[k]} {v}" for k, v in cnt.most_common())
    stale = sum(1 for r in research if re.search(r"20(24|25)|stale|old", r["flags"]))
    (out / "README.md").write_text(README.format(
        n=len(research), mix=mix, member=MEMBER_PRICE, small=GROUP_SMALL, large=GROUP_LARGE,
        narrow=sum(1 for r in research if r["narrow_inbox"]),
        gmail=sum(1 for r in research if r["free_mail"]), stale=stale,
        ata=sum(1 for r in research if "ATA chapter directory" in r["flags"])))
    return tracker


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE)
    a = ap.parse_args()
    t = build(a.out)
    print(f"{len(t)} leads · first {t[0]['email1_planned']} · last Email 1 {t[-1]['email1_planned']} · "
          f"last follow-up {max(x['fu2_planned'] for x in t)}")
