"""Black Friday-Cyber Monday 2026 codes and the January budget-planner push: one source for PRODUCTS_CATALOG.md and the
Gumroad storefront kit.

From scouting's research/scouting/bfcm-plan-2026.md (PR #2), with two decisions from the project chat:
- No crossed-out "was" prices anywhere. Most listings go live Nov 9-16, too new for a former price to be honest
  (Etsy: the original price must be in place "for a substantial amount of time"; FTC 16 CFR 233.1). So no Etsy
  "Sale" (it shows a strikethrough) and no "was $X" text: discount codes only, bundles only, Nov 27-30.
- January is the peak for "budget planner" on Etsy (about 74K searches in Jan 2026 vs 60.5K a month Oct-Dec,
  RankHero, Oct 28 2026), so the bigger push is Dec 26-Jan 15: tags, featured listings, the shop announcement and
  email, with no discount.
Nothing here is created or sent: Dhruv makes the codes and edits the listings.
"""
from __future__ import annotations

from datetime import date

START, END = date(2026, 11, 27), date(2026, 11, 30)
JAN_START, JAN_END = date(2026, 12, 26), date(2027, 1, 15)
WINDOW = "Fri Nov 27 12:00 am to Mon Nov 30 11:59 pm Pacific"

# code, where it's created, discount ("25%" or "$10"), products as (brand, product, platform in the catalog), who gets it
CODES = [
    ("BF25", "Etsy (Money Made Simple shop): Marketing > Sales and discounts > Promo code", "25%",
     [("Money Made Simple", "Mega Budget Bundle (all 40 printables)", "Etsy"),
      ("Money Made Simple", "Printable Budget Binder (all 10 printables)", "Etsy"),
      ("Money Made Simple", "Savings Challenge Pack (12 printables)", "Etsy"),
      ("Money Made Simple", "The Money Made Simple Toolkit", "Etsy")],
     "Email list, Etsy shop announcement and social bios. Limit it to these listings (check the promo-code screen "
     "offers a listing choice; if not, use it shop-wide only on bundles by saying so in the announcement) and set a "
     "total-use limit of 300 so a leak to coupon sites stays small."),
    ("BF10", "Gumroad (Money Made Simple): Checkout > Discounts", "$10",
     [("Money Made Simple", "The Money Made Simple Toolkit", "Gumroad")],
     "Restrict to the Toolkit. A fixed $10 lands on a round $29 (25% would be $29.25)."),
    ("BF5", "Gumroad (Money Made Simple): Checkout > Discounts", "$5",
     [("Money Made Simple", "Money Sheets Bundle", "Gumroad"), ("Money Made Simple", "Notion Money HQ", "Gumroad")],
     "Restrict to these two bundles."),
    ("YEAREND10", "Gumroad and Etsy (1099 Money)", "$10",
     [("1099 Money", "The Freelancer Money Bundle", "Gumroad"), ("1099 Money", "The Freelancer Money Bundle", "Etsy")],
     "Restrict to the bundle. Pitch: set up 2027 before Jan 1. (Scouting suggested running it to Dec 6; kept to the "
     "same Nov 27-30 window as the other bundle codes.)"),
]

NOT_DISCOUNTED = [
    ("Dated 2027 products (2027 Budget Planner, 2027 Budget Sheet, 2027 Money HQ, 2027 Freelancer Tax-Year Planner)",
     "They sell through January at full price; the 2027 Budget Planner drops its price after Jan 31 as planned."),
    ("Entry products (The Bill Cut Kit $5, The 20-Minute Budget $12, single printables $3-6)",
     "Already cheap, and their ladder codes (BILLCUT5, BUDGET5...) would stack confusingly with a sale."),
    ("Scam Decoded (Family Scam-Proofing Kit, Card Set, guide)",
     "No code. Pitched as a gift: \"send it to your parents before the holidays\" (see the listing tweaks)."),
    ("Dinero Simple", "Not live until native review (target week of Dec 7); December remittance and aguinaldo push instead."),
    ("Products launching in December (printable twins, The Money Reset, Schedule C Setup Pack)",
     "Not live yet on Nov 27; they launch into the January push instead."),
    ("Posters and paperbacks", "Print partner and KDP prices leave too little margin for a code."),
]

RULES = [
    "Codes only. No Etsy \"Sale\" (it shows a crossed-out price) and no \"was $X\" anywhere: listings are too new for a "
    "former price to be honest.",
    "Bundles only, Nov 27-30. Every code has a start and end date set in Etsy or Gumroad, so \"ends Monday\" is true.",
    "No timers, no \"only 3 left\", no extensions. On Tue Dec 1 the codes are off and prices are what they always were.",
    "Bundle-vs-separately lines compare today's real prices of the parts. That's a comparison, not a former price.",
    "Etsy listings stay free of off-Etsy links; codes go in the shop announcement and emails, not in titles or tags.",
]

TIMELINE = [
    ("By Mon Nov 16", "Bundles live at full price. Create BF25, BF10, BF5 and YEAREND10 with the dates above (inactive until Nov 27)."),
    ("Tue Nov 24", "Email 1 (scouting's draft): the Black Friday traps, and \"bundles 25% off with a code from Friday\". No code yet."),
    ("Thu Nov 26, evening", "Email 2 with the codes. Etsy shop announcement and Gumroad profile text go up (below)."),
    ("Fri Nov 27 to Mon Nov 30", "Codes live. One post a day per brand points at the bundle, in place of a normal slot."),
    ("Mon Nov 30", "Email 3: \"the code stops working at midnight Pacific tonight\" (true: the codes expire)."),
    ("Tue Dec 1", "Take the announcement and profile text down. Nothing is extended."),
    ("Dec 26 to Jan 15", "The January budget-planner push (below). Keep the tags and featured listings to Jan 31."),
]

ANNOUNCEMENT = {  # (brand, platform): the shop announcement (Etsy) or a profile text section (Gumroad), Nov 26 to Dec 1
    ("Money Made Simple", "Etsy"): ("Black Friday to Cyber Monday (Nov 27-30): code BF25 takes 25% off our bundles: the Mega "
                                    "Budget Bundle, the Budget Binder, the Savings Challenge Pack and the Toolkit. Ends Monday "
                                    "at 11:59 pm Pacific. Single printables stay at their usual price."),
    ("Money Made Simple", "Gumroad"): ("Black Friday to Cyber Monday (Nov 27-30): code BF10 takes $10 off The Money Made Simple "
                                       "Toolkit, and BF5 takes $5 off the Money Sheets Bundle and Notion Money HQ. Ends Monday at "
                                       "11:59 pm Pacific."),
    ("1099 Money", "Etsy"): ("Nov 27-30: code YEAREND10 takes $10 off The Freelancer Money Bundle. Set up 2027 before Jan 1. "
                             "Ends Monday at 11:59 pm Pacific."),
    ("1099 Money", "Gumroad"): ("Nov 27-30: code YEAREND10 takes $10 off The Freelancer Money Bundle. Set up 2027 before Jan 1. "
                                "Ends Monday at 11:59 pm Pacific."),
}

# Etsy listing copy tweaks for the BFCM window (brand, product, the line to add at the top of the description, when).
BFCM_TWEAKS = [
    ("Scam Decoded", "The Family Scam-Proofing Kit",
     "Buying it as a gift? Send the download link to a parent or grandparent, or print it and bring it home for the holidays.",
     "Nov 20 to Dec 18 (holiday-scam season)"),
    ("1099 Money", "The Freelancer Money Bundle",
     "Set up 2027 before January 1: the tracker, the rate and contract kit and the email scripts in one download.",
     "Nov 20 to Jan 15"),
]

# January: tag swaps on the Money Made Simple Etsy shop (slug, tag out, tag in). Each listing keeps 13 tags.
JAN_TAGS = [
    ("monthly-budget-planner", "budget sheets", "new year budget"),
    ("mega-budget-bundle", "budget binder kit", "new year budget"),
    ("budget-binder-bundle", "cash stuffing", "new year budget"),
    ("weekly-budget-planner", "daily expenses", "new year budget"),
    ("paycheck-budget-planner", "pay period budget", "new year budget"),
    ("zero-based-budget-worksheet", "zero budget", "new year budget"),
    ("50-30-20-budget-worksheet", "budget rule", "new year budget"),
    ("financial-goals-planner", None, "2027 goals"),
]
JAN_FEATURED = ["2027 Budget Planner", "Monthly Budget Planner", "Mega Budget Bundle (all 40 printables)",
                "The Money Reset: 30-Day Challenge Workbook"]
JAN_STEPS = [
    "Etsy, Dec 26: swap the tags below (Shop Manager > Listings > edit > Tags), then set the four featured listings "
    "(Shop Manager > Listings > star). Holiday listings come off the featured row.",
    "Etsy shop announcement, Dec 26 to Jan 31: \"New year, new budget: the 2027 Budget Planner, the Monthly Budget "
    "Planner and the 30-day Money Reset are at the top of the shop. Undated pages work any month you start.\"",
    "Gumroad (Money Made Simple): keep The 20-Minute Budget featured; move \"2027 planners\" to the top section from "
    "Dec 26 to Jan 31.",
    "Pinterest: start the budget-planner pins from Dec 1 (pins take weeks to pick up), pointing at the Etsy listings.",
    "Email, Fri Jan 2: \"Your 2027 budget in 20 minutes\" to the Money Made Simple list, linking The 20-Minute Budget "
    "and the 2027 Budget Sheet. No code: January buyers come anyway, and a discount right after Black Friday trains "
    "people to wait.",
    "Jan 15 is also the Q4 estimated-tax date: 1099 Money's posts point at the Quarterly Tax Tracker and, once tested, "
    "the Schedule C Setup Pack.",
]


# Scouting's template-pricing-jan-2027.md (PR #2): proposed prices from Jan 1 2027, after the codes end. Waiting on
# Dhruv's decision; current prices stay until then. Etsy and Gumroad stay equal. (brand, product, from, to, why)
JAN1_PRICES_STATUS = "proposed, waiting on Dhruv"
JAN1_PRICES = [
    ("Money Made Simple", "Every $3 Etsy printable (35 listings)", "$3", "$4",
     "Etsy median for \"savings challenge\" is $4; adds about $0.90 net per sale."),
    ("Money Made Simple", "Savings Challenge Pack (12 printables)", "$8", "$10", "Still well under 12 singles at $4."),
    ("Money Made Simple", "The Debt-Free Date Planner", "$17", "$17 (keep)",
     "Above the debt-tracker median, so the first line says \"a PDF guide plus a spreadsheet\" (done)."),
    ("1099 Money", "The Quarterly Tax Tracker (2027 edition)", "$15", "$17", "PR #10's product: its thread decides."),
    ("1099 Money", "The Freelancer Money Bundle", "$49", "$39, or keep $49 with a \"worth $59 separately\" line",
     "PR #10's product: its thread decides."),
]


def _price(s: str) -> float:
    return float(s.replace("$", "").replace(",", "").split()[0])


def after(price: str, off: str) -> str:
    p = _price(price)
    v = p * (1 - float(off[:-1]) / 100) if off.endswith("%") else p - float(off[1:])
    return f"${v:,.2f}".replace(".00", "")


def code_rows(rows: list[dict]) -> list[dict]:
    """One line per (code, product, platform) with the catalog price and the price with the code."""
    by = {(r["brand"], r["product"], r["platform"]): r for r in rows}
    out = []
    for code, where, off, prods, note in CODES:
        for key in prods:
            r = by[key]
            out.append(dict(code=code, brand=key[0], product=key[1], platform=key[2], price=r["price"], off=off,
                            after=after(r["price"], off), where=where, note=note))
    return out


def separately(listings: list[dict]) -> dict[str, tuple[int, float]]:
    """Etsy bundle slug -> (parts, today's price of the parts bought one by one)."""
    by = {it["slug"]: it for it in listings}
    return {it["slug"]: (len(it["bundle"]), sum(by[s]["price"] for s in it["bundle"]))
            for it in listings if it.get("bundle")}


def jan_tag_rows(listings: list[dict]) -> list[dict]:
    by = {it["slug"]: it for it in listings}
    out = []
    for slug, old, new in JAN_TAGS:
        tags = by[slug]["tags"]
        if old is None:  # replace the listing's last tag
            old = tags[-1]
        out.append(dict(slug=slug, product=by[slug]["name"], old=old, new=new, ok=old in tags and new not in tags))
    return out


def problems(rows: list[dict], listings: list[dict]) -> list[str]:
    bad = []
    keys = {(r["brand"], r["product"], r["platform"]) for r in rows}
    for code, _w, off, prods, _n in CODES:
        bad += [f"{code}: {p} isn't in the catalog" for p in prods if p not in keys]
        if not (off.endswith("%") or off.startswith("$")):
            bad.append(f"{code}: discount must be a percent or a dollar amount")
    names = {r["product"] for r in rows}
    bad += [f"January featured '{n}' isn't in the catalog" for n in JAN_FEATURED if n not in names]
    for t in jan_tag_rows(listings):
        if not t["ok"]:
            bad.append(f"January tags: {t['slug']} can't swap '{t['old']}' for '{t['new']}'")
        if len(t["new"]) > 20 or t["new"] != t["new"].lower():
            bad.append(f"January tags: '{t['new']}' must be lowercase and 20 characters or less")
    return bad


def markdown(rows: list[dict], listings: list[dict]) -> str:
    cr = code_rows(rows)
    sep = separately(listings)
    names = {it["slug"]: it for it in listings}
    out = [f"""## Black Friday to Cyber Monday 2026 (Nov 27-30): codes, bundles only

From scouting's `research/scouting/bfcm-plan-2026.md` (PR #2). **Nothing here is created yet**: make each code in Etsy or
Gumroad with its dates set ({WINDOW}), so it switches itself on and off.

""" + "\n".join(f"- {x}" for x in RULES) + """

| Code | Product | Platform | Price | Off | With the code | Where to create it | Notes |
|---|---|---|---|---|---|---|---|"""]
    out += [f"| `{r['code']}` | {r['product']} | {r['platform']} | {r['price']} | {r['off']} | {r['after']} | {r['where']} | {r['note']} |"
            for r in cr]
    out.append("\n**Not discounted, and why**\n\n| What | Why |\n|---|---|")
    out += [f"| {a} | {b} |" for a, b in NOT_DISCOUNTED]
    out.append("\n**Listing tweaks for the window**\n\n| Brand | Listing | Change | When |\n|---|---|---|---|")
    for slug, (n, total) in sep.items():
        it = names[slug]
        short = it["name"].split(" (")[0].removeprefix("The ")
        what = "printables" if it["kind"] == "bundle" else "guide-and-spreadsheet kits"
        out.append(f"| Money Made Simple | {it['name']} (Etsy) | Open the description with: \"This {short} is {n} {what} in "
                   f"one download: ${total:,.0f} bought one by one, ${it['price']:,.0f} together.\" (The listing already says "
                   "\"Bought separately\" lower down; this moves it up and names the item first, as Etsy advises.) Today's "
                   "prices, not a former price, so it stays after the sale. | From Nov 20 |")
    out += [f"| {b} | {p} | First line of the description: \"{line}\" | {when} |" for b, p, line, when in BFCM_TWEAKS]
    out += [f"| {b} | {'Etsy shop announcement' if pl == 'Etsy' else 'Gumroad profile text section'} | \"{t}\" | Nov 26 evening to Dec 1 |"
            for (b, pl), t in ANNOUNCEMENT.items()]
    out.append("\n**Timeline**\n\n| When | What |\n|---|---|")
    out += [f"| {a} | {b} |" for a, b in TIMELINE]
    out.append(f"""
## January budget-planner push (Dec 26-Jan 15, kept to Jan 31)

Etsy searches for "budget planner" peak in January, so this is the bigger push, at full price.
""")
    out += [f"{i}. {s}" for i, s in enumerate(JAN_STEPS, 1)]
    out.append("\nFeatured on Etsy (in order): " + ", ".join(JAN_FEATURED) + ".\n\n| Listing | Tag out | Tag in |\n|---|---|---|")
    out += [f"| {t['product']} | {t['old']} | {t['new']} |" for t in jan_tag_rows(listings)]
    out.append("\nAfter Jan 31, swap the tags back if their views fell, and keep them if not.")
    out.append(f"\n**Prices from Jan 1 ({JAN1_PRICES_STATUS})**, from scouting's `template-pricing-jan-2027.md`. No January "
               "discounts on tax products.\n\n| Brand | Product | Now | From Jan 1 | Why |\n|---|---|---|---|---|")
    out += [f"| {b} | {p} | {a} | {n} | {w} |" for b, p, a, n, w in JAN1_PRICES]
    return "\n".join(out) + "\n"


def storefront_section(brand: str, rows: list[dict]) -> str:
    """The BFCM and January part of one brand's Gumroad STOREFRONT.md (Gumroad codes only)."""
    cr = [r for r in code_rows(rows) if r["brand"] == brand and "Gumroad" in r["platform"]]
    tweaks = [(p, line, when) for b, p, line, when in BFCM_TWEAKS if b == brand]
    if not cr and not tweaks and brand != "Money Made Simple":
        return ""
    out = ["## Black Friday to Cyber Monday (Nov 27-30) and January\n",
           "Codes only, no crossed-out prices, bundles only. Create each in Checkout > Discounts with the dates set "
           f"({WINDOW}). Full plan: `PRODUCTS_CATALOG.md`, section \"Black Friday to Cyber Monday 2026\".\n"]
    if cr:
        out.append("| Code | Product | Price | Off | With the code | Notes |\n|---|---|---|---|---|---|")
        out += [f"| `{r['code']}` | {r['product']} | {r['price']} | {r['off']} | {r['after']} | {r['note']} |" for r in cr]
    else:
        out.append("No code for this brand.")
    if (brand, "Gumroad") in ANNOUNCEMENT:
        out.append(f"\nProfile text, Nov 26 evening to Dec 1 (a text section above the products): \"{ANNOUNCEMENT[(brand, 'Gumroad')]}\"")
    out += [f"\n{p}: add at the top of the description, {when}: \"{line}\"" for p, line, when in tweaks]
    if brand == "Money Made Simple":
        out.append("\nJanuary (Dec 26 to Jan 31): " + JAN_STEPS[2])
    return "\n".join(out) + "\n"
