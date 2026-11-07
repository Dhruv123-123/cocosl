"""The cross-sell map for every product, not just Gumroad: what the buyer is pointed to next, and where.

Gumroad products use CROSS_SELL in build_storefront.py (receipt note, checkout upsell or buyer email). Etsy, print on
demand and Amazon have no buyer email we control, so the recommendation goes where each platform allows it:
- Etsy (digital and posters): a saved reply sent through Etsy Messages after the order, plus the "next step" page
  in the file. It names an Etsy listing in the same shop, never an off-Etsy link (Etsy's rule for listings and
  messages).
- Amazon KDP: the last page of the book. Amazon shares no buyer emails.
Single $3-$4 printables point at the smallest bundle that holds them, with today's prices worked out from the listings,
so the "bought one by one" figure switches by itself when the Jan 1 prices land. Nothing is sent or changed anywhere.
"""
from __future__ import annotations

ETSY_WHERE = "Etsy saved reply after the order + next-step page in the file"
BOOK_WHERE = "Last page of the book (add on the next upload)"

# Etsy-only next steps where the Gumroad one isn't on Etsy, or the product is Etsy-only. (product -> (next, why))
ETSY_NEXT = {
    "Printable Budget Binder (all 10 printables)": ("2027 Budget Planner", "The binder is undated; the 2027 planner runs the year date by date."),
    "Savings Challenge Pack (12 printables)": ("Printable Budget Binder (all 10 printables)", "The budget pages that find the money for the challenges."),
    "Digital Budget Planner (undated, hyperlinked)": ("Savings Challenge Pack (12 printables)", "The 12 challenge pages open in GoodNotes too: add them to the planner."),
    "Debt Payoff Printable Bundle (5 printables)": ("Printable Budget Binder (all 10 printables)", "The budget pages that find the extra payment each month."),
    "First Paycheck Budget Bundle (6 printables)": ("Savings Challenge Pack (12 printables)", "Once each paycheck has a job, make saving a game."),
    "Freelance and Side Income Budget Bundle (7 printables)": ("2027 Budget Planner", "A dated year for planning around the slow months."),
    "Mega Budget Bundle (all 40 printables)": ("2027 Budget Planner", "The 40 pages are undated; the 2027 planner runs the year month by month."),
    "2027 Budget Planner": ("Printable Budget Binder (all 10 printables)", "Adds the 10 core trackers: bills, sinking funds, subscriptions and debt."),
    "The Quarterly Tax Tracker": ("2027 Freelancer Tax-Year Planner (printable)", "A paper year-planner beside the spreadsheet: dates, months and the tax-time checklist."),
    # Etsy side of products sold on both, where the Gumroad next step isn't on Etsy (guides are Gumroad only)
    "2027 Budget Sheet": ("2027 Budget Planner", "The same year on paper, for the fridge or the binder."),
    "2027 Money HQ for Notion": ("2027 Budget Planner", "The same year on paper, for the fridge or the binder."),
    "Money Dashboard Pro": ("2027 Budget Planner", "The dashboard looks back; the planner plans the year ahead on paper."),
    "El Registro de Envíos": ("El Presupuesto Familiar", "El envío es un gasto fijo; el presupuesto familiar le da su lugar."),
    "Registro de Cuentas y Pagos": ("El Presupuesto Familiar", "Las cuentas son la mitad del presupuesto; este agrega el resto."),
    "Retos de Ahorro": ("El Presupuesto Familiar", "El presupuesto encuentra el dinero para los retos."),
    "Registro de Renta y Reparaciones": ("Registro de Cuentas y Pagos", "La renta es una cuenta más: llévalas todas en un lugar."),
    "Scam Decoded Card Set": ("Scam Red Flags: Posters and Wallet Cards", "The cards go by the phone; the posters put the warning signs on the wall."),
    "Scam Red Flags: Posters and Wallet Cards": ("Scam Decoded Card Set", "The posters show the signs; the cards hold the call-back rule and the numbers."),
}
# Posters point at the printable of the same challenge, so the wall chart has a pen-and-paper log.
POSTER_NEXT = {
    "100 Envelope Challenge Poster": "100 Envelope Challenge",
    "52 Week Savings Challenge Poster": "52-Week Savings Challenge",
    "$1,000 Savings Bingo Poster": "Savings Bingo",
    "Debt Free Mountain Poster": "Debt Mountain Coloring Chart",
    "Savings Jar Poster": "Spare Change Jar Tracker",
    "Travel Fund Poster": "Travel Fund Tracker",
    "Emergency Fund Poster": "Emergency Fund Tracker",
    "House Fund Poster": "Home Fund Brick Tracker",
    "30 Day No Spend Challenge Poster": "No-Spend Challenge",
    "Save $1,000 Challenge Poster": "Savings Challenge Pack (12 printables)",
}
BOOK_NEXT = {
    "2027 Budget Planner (paperback)": ("2027 Budget Sheet", "The same year as a spreadsheet that adds itself up."),
    "Debt Payoff Journal (paperback)": ("The Debt-Free Date Planner", "The journal logs payments; the planner works out the debt-free date."),
    "52-Week Savings Log (paperback)": ("52-Week Savings Challenge Sheet", "The log as a Google Sheet that keeps the running total."),
    "Money Made Simple (Kindle ebook)": ("The Money Made Simple Toolkit", "The book's five plans as guides with spreadsheets."),
    "Money Made Simple (paperback)": ("The Money Made Simple Toolkit", "The book's five plans as guides with spreadsheets."),
}


def _kind(platform: str) -> str:
    if "Amazon" in platform:
        return "book"
    if "print on demand" in platform:
        return "poster"
    if "Gumroad" in platform:
        return "gumroad"
    return "etsy"


def rows(catalog: list[dict], listings: list[dict], cross_sell: dict) -> list[dict]:
    """One row per catalog product: brand, product, platform, price, next, next_price, why, where, code."""
    by_slug = {it["slug"]: it for it in listings}
    printables = {it["name"]: it for it in listings if it["kind"] == "printable"}
    bundles = sorted((it for it in listings if it.get("bundle") and it["kind"] == "bundle"), key=lambda b: len(b["bundle"]))
    price = {}
    for r in catalog:
        price.setdefault((r["brand"], r["product"]), r["price"])
    out, seen = [], set()
    for r in catalog:
        key = (r["brand"], r["product"], _kind(r["platform"]))
        if key in seen or r["platform"].startswith("On hold"):
            continue
        seen.add(key)
        kind, name, code = key[2], r["product"], ""
        if kind == "gumroad" and name in cross_sell:
            nxt, why, where, code = cross_sell[name]
            if "Etsy" in r["platform"]:
                en, _ew = ETSY_NEXT.get(name, (nxt, ""))
                where += " (Gumroad); " + (f"on Etsy recommend {en} instead: " if en != nxt else "") + \
                    (ETSY_WHERE + " (Etsy)" if en else "no Etsy recommendation")
        elif kind == "book":
            nxt, why = BOOK_NEXT[name]
            where = BOOK_WHERE
        elif kind == "poster":
            nxt = POSTER_NEXT[name]
            why, where = "The wall chart, plus a printable log to fill in by hand.", ETSY_WHERE
        elif name in ETSY_NEXT:
            nxt, why = ETSY_NEXT[name]
            where = ETSY_WHERE
        elif name in cross_sell:  # Etsy edition of a Gumroad product: same next step, Etsy edition
            nxt, why, _w, _c = cross_sell[name]
            where = ETSY_WHERE
        elif name in printables:
            it = printables[name]
            b = next(b for b in bundles if it["slug"] in b["bundle"])
            total = sum(by_slug[x]["price"] for x in b["bundle"])
            nxt = b["name"]
            why = (f"All {len(b['bundle'])} pages, this one included: ${total:,.0f} bought one by one, "
                   f"${b['price']:,.0f} together (today's prices).")
            where = ETSY_WHERE
        else:
            nxt, why, where = "", "", ""
        etsy_next = ETSY_NEXT[name][0] if name in ETSY_NEXT else nxt
        out.append(dict(brand=r["brand"], product=name, platform=r["platform"], price=r["price"], next=nxt, etsy_next=etsy_next,
                        next_price=price.get((r["brand"], nxt), "?"), why=why, where=where, code=code))
    return out


def problems(catalog: list[dict], listings: list[dict], cross_sell: dict) -> list[str]:
    """Every product has a next step: another product of the same brand, which is on Etsy when the buyer came from Etsy."""
    on_etsy = {(r["brand"], r["product"]) for r in catalog if "Etsy" in r["platform"]}
    bad = []
    for m in rows(catalog, listings, cross_sell):
        k = _kind(m["platform"])
        if not m["next"]:
            bad.append(f"{m['brand']}: no next step for '{m['product']}' ({m['platform']})")
        elif m["next"] == m["product"] or m["next_price"] == "?":
            bad.append(f"{m['brand']}: '{m['product']}' points at '{m['next']}', not another product of the brand")
        elif "Etsy" in m["platform"] and m["etsy_next"] and (m["brand"], m["etsy_next"]) not in on_etsy:
            bad.append(f"{m['brand']}: Etsy buyers of '{m['product']}' are pointed at '{m['etsy_next']}', which isn't on Etsy")
    return bad


def markdown(catalog: list[dict], listings: list[dict], cross_sell: dict) -> str:
    def esc(x: str) -> str:
        return str(x).replace("|", "\\|")
    m = rows(catalog, listings, cross_sell)
    out = [f"""# Cross-sell map: what each buyer is pointed to next

Every product in `PRODUCTS_CATALOG.md` ({len(m)} rows), every brand and platform. Recommendations stay inside the
brand. Gumroad uses the receipt note, the checkout upsell or the buyer email; Etsy has no buyer email we control, so
Etsy buyers get a saved reply through Etsy Messages and a next-step page in the file, naming an Etsy listing in the
same shop (no off-Etsy links); Amazon books use the last page. Codes are the ones the products already print; create
them before the first sale. Built by `launch/storefront/build_storefront.py`; nothing is sent.
"""]
    for brand in dict.fromkeys(r["brand"] for r in m):
        out.append(f"\n## {brand}\n\n| After buying | Platform | Price | Recommend | Why | Where | Code |\n|---|---|---|---|---|---|---|")
        out += [f"| {esc(r['product'])} | {esc(r['platform'])} | {esc(r['price'])} | {esc(r['next'])} ({esc(r['next_price'])}) | "
                f"{esc(r['why'])} | {esc(r['where'])} | {('`' + r['code'] + '`') if r['code'] else '–'} |"
                for r in m if r["brand"] == brand]
    return "\n".join(out) + "\n"
