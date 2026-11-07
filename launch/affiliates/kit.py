"""Affiliate application kit: ready-to-paste answers per brand, per network and per program.

Run:  python3 launch/affiliates/kit.py [--out DIR]
Writes APPLICATIONS.md, applications.csv (tracker) and applications.html (copy buttons).
Nothing is submitted. [BRACKETS] are things only the owner can fill in (real stats, legal name, tax forms).
"""
import argparse
import csv
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHORT, LONG = 250, 1000  # common form limits for "short description" and "describe your site"

BRANDS = {
    "mms": {
        "name": "Money Made Simple", "site": "https://moneymadesimple.netlify.app",
        "handles": "@moneymadesimple on Instagram, TikTok and YouTube",
        "category": "Personal finance / education",
        "short": "Plain-English personal finance for US students and early-career workers: budgeting, savings, "
                 "credit and first-time investing, with the maths shown and no hype.",
        "long": "Money Made Simple is an independent personal-finance education brand for US students and people "
                "early in their careers. We publish short explainer videos (YouTube Shorts, TikTok, Instagram "
                "Reels and carousels), a weekly email newsletter and in-depth articles on our site covering "
                "budgeting, emergency funds, high-yield savings, credit scores, debt payoff and first-time "
                "investing in index funds. Every piece shows the numbers, links its sources and says who a product "
                "is not for. We don't cover crypto, day trading or individual stock picks. Affiliate links are "
                "labelled, AI-assisted production is disclosed, and a human reviews and fact-checks everything "
                "before it is published.",
        "audience": "Mostly US-based, ages roughly 18–34: college students, new graduates and early-career workers "
                    "setting up their first budget, savings account, credit card, 401(k) or IRA. [ADD REAL "
                    "DEMOGRAPHICS FROM PLATFORM ANALYTICS: % US, age split, monthly views, email subscribers]",
        "proof": ["/blog/best-high-yield-savings-accounts/", "/blog/how-to-build-an-emergency-fund/",
                  "/blog/best-budgeting-apps/"],
    },
    "scam": {
        "name": "Scam Decoded", "site": "https://scamdecoded.netlify.app",
        "handles": "@scamdecoded on Instagram, TikTok and YouTube",
        "category": "Consumer protection / online security",
        "short": "Calm, 60-second breakdowns of real scams and how to protect yourself: identity theft, phishing, "
                 "account takeovers and fraud recovery, for US adults and their families.",
        "long": "Scam Decoded is an independent consumer-protection brand. Each short video and carousel decodes one "
                "real, current scam (how it works, the tell, and exactly what to do), with step-by-step guides on "
                "our site for credit freezes, account security, password managers and recovering from identity "
                "theft. The tone is calm and practical with no fear-based hooks, so viewers share it with parents "
                "and grandparents. We cite official sources (FTC, FBI IC3, CFPB) and recommend free protections "
                "first, then paid tools where they add real value. Affiliate links are labelled, AI-assisted "
                "production is disclosed, and a human reviews every post.",
        "audience": "US adults roughly 25–65 and the adult children who look after their parents' online safety. "
                    "[ADD REAL DEMOGRAPHICS: % US, age split, monthly views, email subscribers]",
        "proof": ["/", "/kit/"],
    },
    "1099": {
        "name": "1099 Money", "site": "https://1099money.netlify.app",
        "handles": "@1099money on Instagram, TikTok and YouTube",
        "category": "Small business / freelancer finance",
        "short": "The money side of freelancing for first-year freelancers, creators and gig workers: quarterly "
                 "taxes, deductions, invoicing and business banking, with the maths shown.",
        "long": "1099 Money is an independent education brand for US freelancers, creators and gig workers in their "
                "first years of self-employment. We publish short videos and carousels, a weekly newsletter and a "
                "free quarterly-tax calculator on our site, covering estimated taxes, self-employment tax, "
                "deductions, invoicing, separating business and personal money, and choosing tools like "
                "accounting software and business bank accounts. We show worked examples, cite IRS sources, and "
                "never promote aggressive 'write off everything' tactics. Affiliate links are labelled, AI-assisted "
                "production is disclosed, and a human reviews and fact-checks every post.",
        "audience": "US-based freelancers, creators, contractors and gig workers, mostly in their first three years "
                    "of self-employment, ages roughly 22–45. [ADD REAL DEMOGRAPHICS]",
        "proof": ["/"],
    },
    "dinero": {
        "name": "Dinero Simple", "site": "https://dinerosimple.netlify.app",
        "handles": "@dinerosimple on Instagram, TikTok and YouTube",
        "category": "Personal finance / Spanish-language education",
        "short": "Spanish-language personal finance for young Latinos in the US: budgeting, building credit from "
                 "scratch, saving, and sending money to family, with clear numbers.",
        "long": "Dinero Simple is an independent, Spanish-language personal-finance brand for young Latinos in the "
                "US, many of them first-generation or bilingual. We publish short videos, carousels and a newsletter "
                "in Spanish on budgeting, building a credit history with no credit, emergency savings, bank "
                "accounts, taxes and sending money abroad, always showing the full cost (fees plus exchange rate). "
                "Spanish copy is checked against official IRS, CFPB and FTC Spanish-language sources, and we're adding a native-speaker review before full launch. Affiliate links are labelled "
                "(#publicidad), AI-assisted production is disclosed, and we don't promote crypto or high-risk "
                "products.",
        "audience": "US-based Spanish-first and bilingual adults, roughly 18–40. [ADD REAL DEMOGRAPHICS]",
        "proof": ["/"],
    },
}

PROMOTION = {
    "methods": "Content and SEO articles on our own site; organic short-form video (YouTube Shorts, TikTok, "
               "Instagram Reels) with links in the description or link-in-bio page; Instagram carousels; "
               "Pinterest pins linking to our articles; and our own opt-in email newsletter.",
    "not": "We don't bid on your brand terms or trademarks in paid search, don't use coupon or cashback sites, "
           "incentivised traffic, pop-ups, toolbars, spam or bought email lists, and don't put your trademark in "
           "any domain or social handle.",
    "compliance": "Every post or article with an affiliate link carries a clear disclosure next to the link and "
                  "in the caption (#ad / affiliate link), and links are marked rel=\"sponsored\". Our site has a "
                  "public disclosures page. We disclose AI-assisted production, never publish fake testimonials or "
                  "made-up results, make no income or return promises, and date any rate or price we mention and "
                  "link to your official page for current terms. We're happy to follow your brand guidelines and "
                  "send content for pre-approval where you require it.",
    "traffic": "[MONTHLY SITE VISITORS from analytics] site visitors/month; [AVG VIEWS] average views per short "
               "video; [FOLLOWERS] followers across platforms; [EMAIL SUBSCRIBERS] newsletter subscribers. "
               "Audience is [% US]% US.",
}

NETWORKS = [
    {"name": "Impact (impact.com)", "url": "https://impact.com/partners/", "unlocks": "SoFi, Empower, Rocket Money, Aura, Acorns, Betterment, M1, FreshBooks, QuickBooks, Lively, CapCut",
     "fields": {"Property type": "Website + social media (add each brand's site and its social profiles as separate properties)",
                "Promotional methods to tick": "Content/Reviews, Blog/Website, Social Media, Email/Newsletter, Video. Leave unticked: Coupon/Deal, Cashback/Loyalty, Paid Search, Toolbar, Sub-affiliate network.",
                "Vertical": "Finance & Insurance (Money Made Simple, Dinero Simple); Business Services (1099 Money); Software & Security (Scam Decoded)"}},
    {"name": "CJ Affiliate", "url": "https://www.cj.com/publisher", "unlocks": "CIT Bank, Ally Invest, TaxAct",
     "fields": {"Website category": "Financial Services > Banking/Personal Finance",
                "Promotional model": "Content/Niche; Social Media; Email (opt-in newsletter)",
                "Tip": "CJ reviews the site itself: apply with the site that has the most articles live (Money Made Simple)."}},
    {"name": "FlexOffers", "url": "https://www.flexoffers.com/affiliates/", "unlocks": "Monarch, Chime, Betterment, Stash, Credit Karma, Experian, Self, Kikoff, Dashlane, Incogni, 1Password",
     "fields": {"Primary promotional method": "Content site / blog, plus social media",
                "Tip": "FlexOffers asks for a short call or email verification: answer from the same text below."}},
    {"name": "PartnerStack", "url": "https://partnerstack.com/", "unlocks": "Gusto, Novo, Optery, ElevenLabs, Descript, Notion",
     "fields": {"Partner type": "Affiliate / content creator",
                "Tip": "PartnerStack approvals are per brand (per marketplace listing), not network-wide."}},
]

TIER_NOTE = {
    1: "Apply now (once about 10 posts and the site are live).",
    2: "Apply once the brand's site and about 10 posts are live.",
    3: "Apply after 30 days of real stats; these review traffic closely.",
}

PROGRAMS = json.loads((HERE / "programs.json").read_text())


def check(label, text, limit):
    assert len(text) <= limit, f"{label}: {len(text)} chars > {limit}"
    assert not re.search(r"\bguarantee|risk[- ]free|get rich\b", text, re.I), label
    return text


def program_answers(p):
    """Per-program fields, built from the brand blocks plus the program's own lines."""
    b = BRANDS[p["brands"][0]]
    why = check(f"{p['name']} why", p["why"], 600)
    return {
        "Website URL": b["site"],
        "Site / channel name": b["name"],
        "Short description": check(f"{b['name']} short", b["short"], SHORT),
        "Describe your site and audience": check(f"{b['name']} long", b["long"], LONG),
        "Audience": b["audience"],
        f"Why {p['name']}?": why,
        "How will you promote us?": check(f"{p['name']} promo", p["promo"] + " " + PROMOTION["methods"], LONG),
        "Methods we don't use": PROMOTION["not"],
        "Compliance and disclosure": check("compliance", PROMOTION["compliance"] + (" " + p["compliance"] if p.get("compliance") else ""), LONG),
        "Traffic": PROMOTION["traffic"],
        "Example content": ", ".join(b["site"] + x for x in b["proof"]),
    }


def build_md():
    out = ["# Affiliate application kit", "",
           "Nothing has been submitted. Fill the [BRACKETS] with real numbers from your analytics (never estimates), "
           "then paste the answers into each form. Apply to the networks first: one approval at Impact or CJ "
           "makes the program applications there much faster.", "",
           "## Before you apply (all programs)", "",
           "- [ ] The brand's site is live with its disclosures, privacy and about pages, and at least ~10 posts or articles.",
           "- [ ] Social profiles link to the site, and the bio says what the account is about.",
           "- [ ] You have a business email on the brand (not a personal Gmail) for the application.",
           "- [ ] Payment and tax details ready (W-9 for US). Fill these in yourself; they're not in this kit.",
           "- [ ] Real stats from the last 30 days: site visitors, average views, followers, email subscribers, % US.",
           "- [ ] Investing programs (Betterment, M1, Acorns, Robinhood, Ally Invest, Empower, Wealthfront): read the "
           "FINRA/SEC notes. Expect script pre-approval and a written agreement.", "",
           "## Reusable answers by brand", ""]
    for key, b in BRANDS.items():
        out += [f"### {b['name']}", "", f"**Website:** {b['site']}  ", f"**Social:** {b['handles']}  ",
                f"**Category:** {b['category']}", "",
                f"**Short description ({len(b['short'])} chars):**", "", f"> {b['short']}", "",
                f"**Long description ({len(b['long'])} chars):**", "", f"> {b['long']}", "",
                f"**Audience:** {b['audience']}", ""]
    out += ["### Shared answers (every brand)", "",
            f"**Promotion methods:** {PROMOTION['methods']}", "",
            f"**Methods we don't use:** {PROMOTION['not']}", "",
            f"**Compliance statement:** {PROMOTION['compliance']}", "",
            f"**Traffic:** {PROMOTION['traffic']}", "",
            "## Networks (apply here first)", ""]
    for n in NETWORKS:
        out += [f"### {n['name']}", "", f"Sign up: {n['url']}  ", f"Unlocks: {n['unlocks']}", ""]
        out += [f"- **{k}:** {v}" for k, v in n["fields"].items()] + [""]
    out += ["## Programs", "",
            "| Program | Brands | Apply via | When | Payout (confirm in dashboard) |", "|---|---|---|---|---|"]
    for p in PROGRAMS:
        out.append(f"| {p['name']} | {', '.join(BRANDS[x]['name'] for x in p['brands'])} | {p['network']} | "
                   f"Tier {p['tier']} | {p['payout']} |")
    out.append("")
    for p in PROGRAMS:
        a = program_answers(p)
        out += [f"### {p['name']}", "",
                f"**Apply:** {p['apply']}  ", f"**Network:** {p['network']}  ",
                f"**Brands:** {', '.join(BRANDS[x]['name'] for x in p['brands'])} (answers below use "
                f"{BRANDS[p['brands'][0]]['name']}; swap in another brand's block from above if applying for it)  ",
                f"**When:** {TIER_NOTE[p['tier']]}  ", f"**Payout:** {p['payout']}", ""]
        out += [f"- **Why {p['name']}?** {p['why']}",
                f"- **How we'll promote it:** {p['promo']}"]
        if p.get("compliance"):
            out.append(f"- **Compliance:** {p['compliance']}")
        if p.get("tips"):
            out.append(f"- **Tips:** {p['tips']}")
        out.append("")
    return "\n".join(out)


def build_csv(path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["program", "brand", "network", "apply_url", "tier", "payout_note", "status", "applied_on",
                    "decision_on", "tracking_link", "site_program", "notes"])
        for p in PROGRAMS:
            for b in p["brands"]:
                w.writerow([p["name"], BRANDS[b]["name"], p["network"], p["apply"], p["tier"], p["payout"],
                            "not applied", "", "", "", p.get("go", "").replace("-", "_"), ""])


def build_html():
    def block(label, text):
        t = html.escape(text)
        return (f'<div class="f"><div class="l">{html.escape(label)} <span>{len(text)} chars</span>'
                f'<button onclick="cp(this)">Copy</button></div><div class="t">{t}</div></div>')
    cards = []
    for p in PROGRAMS:
        a = program_answers(p)
        body = "".join(block(k, v) for k, v in a.items())
        others = [BRANDS[x]["name"] for x in p["brands"][1:]]
        note = f'<p class="n">Also fits: {", ".join(others)}. Swap in that brand\'s description from the brand section.</p>' if others else ""
        cards.append(f'<details><summary><b>{html.escape(p["name"])}</b> <em>{html.escape(p["network"])} · Tier {p["tier"]}</em></summary>'
                     f'<p class="n"><a href="{html.escape(p["apply"])}" rel="noopener">Application page</a> · {html.escape(TIER_NOTE[p["tier"]])} · {html.escape(p["payout"])}</p>'
                     f'{note}{body}</details>')
    brands = "".join(f'<details><summary><b>{html.escape(b["name"])}</b> <em>brand answers</em></summary>'
                     + block("Website", b["site"]) + block("Short description", b["short"])
                     + block("Long description", b["long"]) + block("Audience", b["audience"]) + "</details>"
                     for b in BRANDS.values())
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Affiliate application kit</title><style>
:root{{--bg:#fafaf7;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#e4e2db;--acc:#1f6f5c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe6;--mut:#a3a29c;--card:#1f1f1d;--line:#34332f;--acc:#6fc2a9}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:860px;margin:auto}}h1{{margin:0 0 4px}}p.lead{{color:var(--mut);margin:0 0 20px}}
details{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0;padding:10px 14px}}
summary{{cursor:pointer}}summary em{{color:var(--mut);font-style:normal;font-size:13px;margin-left:6px}}
.f{{border-top:1px solid var(--line);padding:8px 0}}.l{{font-weight:600;font-size:13px;display:flex;gap:8px;align-items:center}}
.l span{{color:var(--mut);font-weight:400}}.l button{{margin-left:auto;border:1px solid var(--acc);color:var(--acc);background:none;border-radius:6px;padding:2px 10px;cursor:pointer}}
.t{{white-space:pre-wrap;word-break:break-word}}.n{{color:var(--mut);font-size:13px}}a{{color:var(--acc)}}h2{{margin-top:28px}}
</style></head><body><main><h1>Affiliate application kit</h1>
<p class="lead">Ready-to-paste answers. Nothing has been submitted. Replace every [BRACKET] with real numbers before pasting.</p>
<h2>Brands</h2>{brands}<h2>Programs ({len(PROGRAMS)})</h2>{''.join(cards)}</main>
<script>function cp(b){{const t=b.closest('.f').querySelector('.t').innerText;navigator.clipboard.writeText(t).then(()=>{{b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1200)}})}}</script>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    for p in PROGRAMS:
        program_answers(p)  # length and wording checks
        assert p["tier"] in TIER_NOTE and all(b in BRANDS for b in p["brands"]), p["name"]
    (out / "APPLICATIONS.md").write_text(build_md())
    build_csv(out / "applications.csv")
    (out / "applications.html").write_text(build_html())
    print(f"{len(PROGRAMS)} programs, {sum(len(p['brands']) for p in PROGRAMS)} tracker rows -> {out}")


if __name__ == "__main__":
    main()
