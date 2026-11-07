#!/usr/bin/env python3
"""Write the one-page B2B landing pages served under /business/ on the Money Made Simple site.

    cd launch/b2b && python3 site/business_pages.py   # writes <repo>/site/static/business/<slug>/index.html

The website build (PR #4) copies site/static/ verbatim, so each page is served at /business/<slug>/, and
site/static/business/manifest.json feeds its sitemap. Its link checker tests every internal link, so these
pages link only to each other and the site home; the sample-issue and sample-pack buttons point at the
separate B2B landing site (https://YOUR-SITE.netlify.app, a placeholder) and stay hidden until it's set.

Each page is self-contained (inline CSS, no outside assets), works on phones and in dark mode, and is
noindexed until Dhruv fills in the contact details. The contact email comes from site/config.js
(salesEmail, REPLACE_ME until set), and each offer's card payment link is a {{PAYMENT_LINK_...}}
placeholder that hides the button until it's filled in. Nothing is posted or deployed.
"""
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
OUT = SITE.parents[2] / "site" / "static" / "business"
B2B_SITE = "https://YOUR-SITE.netlify.app"  # the launch/b2b/site landing page, once deployed
UPDATED = "2026-11-07"

PAGES = {
    "scam-watch": dict(
        color="#6B3FA0", dark="#b38ae6", who="Libraries, senior centers and Area Agencies on Aging",
        title="Scam Watch: a large-print scam alert for older adults, every month",
        desc="One scam a month for older adults, ready to print, post and talk through in 10 minutes, under your library's or center's name.",
        hero="One scam a month, in large print, under your name.",
        sub="Scam Watch gives your library or senior center a ready-made monthly alert for older adults: a handout in 18-point type, a flyer, a screen slide and a 10-minute talk guide. Every claim is sourced to the FTC, FBI or another official site.",
        gets=["Large-print handout (18 pt) and a bulletin board flyer", "Screen slide for lobby or community room TVs",
              "A 10-minute talk guide any staff member or volunteer can lead", "Newsletter blurb and Facebook post",
              "A sources page linking every claim to an official .gov site"],
        why=["Older adults lose more per scam than any other age group, and they trust their library and senior center.",
             "Writing and fact-checking a monthly alert takes hours your staff don't have.",
             "It carries your name and phone number, not ours. Nothing tracks your patrons."],
        prices=[("One location", "$19 a month"), ("2 to 4 locations", "$49 a month"),
                ("5 to 20 locations", "$12 a location a month"), ("21+ or a whole region", "Quote, from $250"),
                ("Sponsored by a local credit union", "Free to you")],
        price_note="Monthly, cancel any time. Talks in person or online are $150 each.",
        sample=B2B_SITE + "/samples/scam-watch/", download=B2B_SITE + "/downloads/scam-watch-sample-pack.zip",
        cta="Request the Scam Watch sample", subject="Scam Watch sample", pay="PAYMENT_LINK_SCAM_WATCH",
        faq=[("Do we need to collect patron data?", "No. You print, post or read it. We never see who reads it."),
             ("Can a credit union pay for it?", "Yes. A local credit union can sponsor up to 5 sites for its community; the handout then says who brought it."),
             ("Is it in Spanish?", "A Spanish edition is being reviewed by a native speaker. Ask and we'll tell you when it's ready.")]),
    "accounting-firms": dict(
        color="#9A5B13", dark="#e6a65c", who="CPA, tax and bookkeeping firms",
        title="Freelancer Money Notes: a tax-season newsletter for your 1099 clients",
        desc="A monthly newsletter for your self-employed clients, timed to estimated payments and document season, sent under your firm's name.",
        hero="Get your 1099 clients ready before tax season, without writing a word.",
        sub="Freelancer Money Notes is a monthly client newsletter under your firm's name, timed to the dates your self-employed clients miss: estimated payments, receipts, document deadlines. Your clients show up organized; your team answers fewer of the same questions.",
        gets=["Client email (HTML and plain text) with your booking link", "Social post with image and alt text",
              "A printable client handout", "Notes for your team, with every claim linked to IRS.gov",
              "January issue on the Jan 15 estimated payment and getting documents in early"],
        why=["Small firms decide fast, and it costs less than an hour of staff time a month.",
             "It goes out in your name, from your own email platform. We never see your client list.",
             "Delivered 2 weeks early so you can edit anything before it goes out."],
        prices=[("Essentials", "$39 a month"), ("Standard", "$79 a month"), ("Plus", "$129 a month")],
        price_note="Monthly, cancel any time. Order by mid-December to have January's issue in hand before the Jan 15 payment.",
        sample=B2B_SITE + "/samples/accounting-firm/", download=B2B_SITE + "/downloads/accounting-firm-sample-pack.zip",
        cta="Request the accounting firm sample", subject="Freelancer Money Notes sample", pay="PAYMENT_LINK_FREELANCER",
        faq=[("Is this tax advice?", "No. It's general education with a line saying so, and it points clients to you for advice. You review every issue before it goes out."),
             ("Will you contact our clients?", "Never. You send it. We never see client names or emails."),
             ("We're busy from mid-January.", "That's why issues are delivered 2 weeks early and written to need no changes. Most firms just add their logo once.")]),
    "consumer-protection-week": dict(
        color="#1F5C8B", dark="#6aa7d6", who="Credit unions",
        title="Consumer Protection Week package for credit unions, Mar 1–5, 2027",
        desc="Five ready-made member alerts for National Consumer Protection Week, one a day, under your credit union's brand.",
        hero="Show up for Consumer Protection Week with a member alert every day.",
        sub="National Consumer Protection Week runs Feb 28 to Mar 6, 2027: the FTC's week for talking about frauds, scams and consumer rights. Get five ready-made member alerts, one for each weekday, with your logo, colors and phone number, delivered by Feb 15 for compliance review.",
        gets=["Mon: \"recovery\" offers that charge a fee", "Tue: calls from \"the FTC\" that demand money",
              "Wed: free trials that only cost shipping", "Thu: debt collectors who threaten arrest",
              "Fri: credit repair that wants money up front",
              "Each day: member email, social post, lobby slide, branch poster, staff huddle brief and sources",
              "A press note template and a one-line board update"],
        why=["Every claim is sourced to the FTC or CFPB. Links go only to your site or .gov pages.",
             "No member data reaches us. No tracking pixels, ads or affiliate links.",
             "We never tell members they'll be reimbursed, and we don't claim FTC endorsement."],
        prices=[("Week package", "$149 one-time"), ("With up to 3 local libraries or senior centers", "$249 one-time"),
                ("Weekly Scam Alert Standard or Plus", "Included")],
        price_note="Order by January 29, 2027. If you start the Weekly Scam Alert within 60 days, the package price comes off your first month.",
        sample=B2B_SITE + "/samples/consumer-protection-week/", download=B2B_SITE + "/downloads/ncpw-sample-pack.zip",
        cta="Request a free sample day", subject="Consumer Protection Week package", pay="PAYMENT_LINK_NCPW",
        faq=[("When do we get it?", "By February 15, 2027, so compliance has two weeks to review."),
             ("Can we change the wording?", "Yes. Send edits and they're back within 1 business day."),
             ("What does the library add-on include?", "A large-print one-page handout with your name on it and a 20-minute talk outline, for up to 3 local libraries or senior centers.")]),
    "schools": dict(
        color="#1F5F4A", dark="#6cc2a8", who="High schools, districts and community colleges",
        title="Money Made Simple for Schools: a 10-minute money lesson every week",
        desc="Weekly personal finance mini-lessons aligned to the National Standards for Personal Financial Education, with your school's name on them.",
        hero="A 10-minute money lesson every week, ready to teach.",
        sub="Money Made Simple for Schools gives teachers and advisors a short weekly lesson aligned to the National Standards for Personal Financial Education: a class slide, a student handout, an activity and an exit ticket. No logins, and no student data.",
        gets=["A class slide and a student handout", "A lesson page with an activity and an exit ticket",
              "Teacher notes and an answer key", "The standard each lesson maps to",
              "Your school's or district's name on every page"],
        why=["States are adding personal finance requirements, and teachers need short, current material.",
             "Free curricula exist, and we say so. This saves prep time and carries your school's name.",
             "We never collect student data. Nothing to log in to."],
        prices=[("Teacher", "$79 a school year"), ("School", "$299 a school year"),
                ("District, up to 5 high schools", "$899 a school year"), ("College campus", "$399 a school year"),
                ("Sponsored by a local credit union", "Free to you")],
        price_note="Aligned to the national standards published by the Council for Economic Education and the Jump$tart Coalition. Not endorsed by either.",
        sample=B2B_SITE + "/samples/schools/", download=B2B_SITE + "/downloads/schools-sample-pack.zip",
        cta="Request the schools sample", subject="Money Made Simple for Schools sample", pay="PAYMENT_LINK_SCHOOLS",
        faq=[("Does this replace our curriculum?", "No. It's a 10-minute weekly add-on that fits next to what you already teach."),
             ("Do students need accounts?", "No. Teachers print or project it. We never see student names."),
             ("Can a credit union sponsor it?", "Yes, and many already support school financial literacy. Their name appears as the sponsor.")]),
}

CSS = """
:root{--bg:#fff;--soft:#f3f5f8;--text:#16202b;--muted:#4a5664;--line:#dde3ea;--c:%(color)s;--on:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#111821;--soft:#18222e;--text:#e8edf3;--muted:#a8b4c2;--line:#2b3746;--c:%(dark)s;--on:#111821}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
a{color:var(--c)}.wrap{max-width:960px;margin:0 auto;padding:0 16px}
header{border-bottom:1px solid var(--line)}header .wrap{display:flex;justify-content:space-between;align-items:center;padding-top:14px;padding-bottom:14px;gap:12px}
header a{text-decoration:none;color:var(--muted);font-size:15px}header b a{color:var(--text);font-size:17px}
.hero{padding:52px 0 36px}.who{font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--c)}
h1{font-size:clamp(30px,5vw,46px);line-height:1.1;margin:8px 0 14px;letter-spacing:-.02em}
.hero p{font-size:19px;color:var(--muted);max-width:720px;margin:0 0 22px}
.btn[hidden]{display:none}.btn{display:inline-block;background:var(--c);color:var(--on);font-weight:700;text-decoration:none;padding:13px 20px;border-radius:8px;margin:0 8px 8px 0}
.btn.ghost{background:transparent;color:var(--text);border:2px solid var(--line)}
section{border-top:1px solid var(--line);padding:40px 0}h2{font-size:28px;margin:0 0 16px;line-height:1.2}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}ul{padding-left:20px;margin:0}li{margin-bottom:8px}
.check{list-style:none;padding:0}.check li::before{content:"✓ ";color:var(--c);font-weight:800}
table{width:100%%;border-collapse:collapse}td{padding:12px 6px;border-bottom:1px solid var(--line);vertical-align:top}
td:last-child{text-align:right;font-weight:800;color:var(--c);white-space:nowrap}
.note{color:var(--muted);font-size:15px;margin-top:12px}
details{border-bottom:1px solid var(--line);padding:14px 0}summary{font-weight:700;cursor:pointer}details p{color:var(--muted);margin:8px 0 0}
footer{border-top:1px solid var(--line);padding:28px 0 44px;color:var(--muted);font-size:14px}
:focus-visible{outline:3px solid var(--c);outline-offset:2px}
@media (max-width:760px){.grid{grid-template-columns:1fr}header nav{display:none}}
"""


def sales_email() -> str:
    m = re.search(r'salesEmail:\s*"([^"]+)"', (SITE / "config.js").read_text())
    return m.group(1) if m else "REPLACE_ME@example.com"


def page(slug: str, p: dict, email: str) -> str:
    e = html.escape
    mail = f"mailto:{email}?subject={e(p['subject'].replace(' ', '%20'))}"
    pay = f"{{{{{p['pay']}}}}}"
    rows = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in p["prices"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Made by launch/b2b/site/business_pages.py; edit there, not here. Remove the noindex line once the contact
     email in site/config.js and the payment link below are real. -->
<meta name="robots" content="noindex">
<title>{e(p['title'])}</title><meta name="description" content="{e(p['desc'])}">
<style>{CSS % p}</style></head><body>
<header><div class="wrap"><b><a href="../">For organizations</a></b>
<nav><a href="#gets">What you get</a> · <a href="#price">Price</a> · <a href="#faq">Questions</a></nav></div></header>
<main>
<div class="hero"><div class="wrap"><div class="who">{e(p['who'])}</div><h1>{e(p['hero'])}</h1><p>{e(p['sub'])}</p>
<a class="btn" href="{mail}">{e(p['cta'])}</a><a class="btn ghost" hidden data-ph="{p['sample']}">See a sample issue</a></div></div>
<section id="gets"><div class="wrap grid"><div><h2>What you get</h2><ul class="check">{''.join(f'<li>{e(g)}</li>' for g in p['gets'])}</ul></div>
<div><h2>Why it works</h2><ul>{''.join(f'<li>{e(w)}</li>' for w in p['why'])}</ul></div></div></section>
<section id="price"><div class="wrap"><h2>Price</h2><table>{rows}</table><p class="note">{e(p['price_note'])} Invoiced; ACH or card.</p>
<a class="btn" href="{mail}">{e(p['cta'])}</a><a class="btn ghost" hidden data-ph="{pay}">Pay by card</a>
<a class="btn ghost" hidden data-ph="{p['download']}">Download the sample pack</a></div></section>
<section id="faq"><div class="wrap"><h2>Questions</h2>{faq}</div></section>
</main>
<footer><div class="wrap"><a href="/">Money Made Simple</a> · <a href="../">For organizations</a><br>Questions? Write to <a href="mailto:{email}">{e(email)}</a>. {{{{YOUR_BUSINESS_NAME}}}} · {{{{YOUR_ADDRESS}}}}.
Sample issues are made for fictional organizations; the sources are real.</div></footer>
<script>/* show a button only once its link is real (placeholders live in data-ph, never in href, so the site's link checker never sees them) */document.querySelectorAll('[data-ph]').forEach(function(a){{var u=a.getAttribute('data-ph');if(!/\\{{\\{{|YOUR-SITE/.test(u)){{a.href=u;a.hidden=false}}}});</script>
</body></html>
"""


def index(email: str) -> str:
    cards = "".join(f'<li><a href="{s}/"><b>{html.escape(p["who"])}</b></a>: {html.escape(p["desc"])}</li>'
                    for s, p in PAGES.items())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>For organizations</title>
<meta name="description" content="Ready-made, white-label newsletters for libraries, accounting firms, credit unions and schools.">
<style>{CSS % dict(color="#1F5C8B", dark="#6aa7d6")}</style></head><body>
<main class="wrap"><div class="hero"><div class="who">For organizations</div><h1>Ready-made newsletters, under your name</h1>
<p>Scam alerts and money lessons your members, patrons, clients and students can use. Every claim sourced; nothing tracks your readers.</p></div>
<ul class="check">{cards}</ul></main>
<footer><div class="wrap"><a href="/">Money Made Simple</a><br>Questions? Write to <a href="mailto:{email}">{html.escape(email)}</a>.</div></footer></body></html>
"""


def main() -> None:
    email = sales_email()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(index(email))
    manifest = []
    for slug, p in PAGES.items():
        d = OUT / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(slug, p, email))
        manifest.append(dict(slug=slug, title=p["title"], description=p["desc"], updated=UPDATED))
    # format agreed with the website thread: a list of {slug, title, description, updated} for sitemap.xml
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(PAGES)} pages + index to {OUT.relative_to(SITE.parents[2])}/ (contact: {email})")


if __name__ == "__main__":
    main()
