"""Write PRODUCTS_CATALOG.md (+ .csv): every product across every brand, with price, platform, files, listing copy and
launch date, so there is one sheet to list from.

    python launch/catalog/build_catalog.py [--out launch/PRODUCTS_CATALOG.md]

Products built on this branch are read from their own modules, so prices and names can't drift. Products built on
other branches (Scam Decoded PR #9, 1099 Money PR #10, Dinero Simple PR #11) are listed from their LISTING files as
of Nov 7 2026 in OTHER_BRANCHES below; update that table if those change. Paths are relative to the project files
folder content-factory/, where the upload-ready files live. Launch dates come from the Nov–Jan launch calendar doc
where it names the product ("calendar"), otherwise they are a proposal ("proposed").
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAUNCH = HERE.parent
for sub in ("etsy", "templates", "pod", "brandshop"):
    sys.path.insert(0, str(LAUNCH / sub))

CALENDAR = "https://claude.ai/artifact/MoXNajcfVEBSaFXESAyPRp"
COLS = ["brand", "product", "platform", "price", "files", "listing", "launch", "date_source", "notes"]


def row(brand, product, platform, price, files, listing, launch, src, notes=""):
    return dict(brand=brand, product=product, platform=platform, price=price, files=files, listing=listing,
                launch=launch, date_source=src, notes=notes)


def money(p) -> str:
    return "free" if not p else f"${p:,.2f}".replace(".00", "")


# ---------------------------------------------------------------- Money Made Simple (this branch, PR #6)

SAVINGS = ("challenge", "bingo", "roll-and-save", "spare-change", "jar")
HOLIDAY = ("gift-budget", "holiday-savings")
TAX = ("side-hustle", "irregular-income", "net-worth")


def etsy_rows() -> list[dict]:
    import listings as L
    out = []
    for it in L.LISTINGS:
        s, k = it["slug"], it["kind"]
        base = f"etsy/{s}/"
        if it.get("dated"):
            date, src, note = "Week of Nov 9 (list first)", "calendar", "Dated: 4 PDFs (Sun/Mon start x Letter/A4). Drop the price after Jan 31."
        elif k == "bundle":
            date, src, note = "Week of Nov 9; on sale Nov 27-30 (25% off)", "calendar", "Black Friday sale is bundles only."
        elif k == "product":
            date, src, note = "Week of Nov 9 (with the shop)", "proposed", "Etsy edition: no Gumroad codes or links."
        elif any(w in s for w in SAVINGS):
            date, src, note = "Week of Nov 9; featured from Dec 7", "calendar", "Savings challenges to the top of the shop in December."
        elif any(w in s for w in HOLIDAY):
            date, src, note = "Week of Nov 9 (pin it)", "calendar", "Peaks before Thanksgiving."
        elif any(w in s for w in TAX):
            date, src, note = "Week of Nov 9; featured from Jan 25", "calendar", "Tax-season item."
        else:
            date, src, note = "Week of Nov 9 (with the shop)", "proposed", ""
        out.append(row("Money Made Simple", it["name"], "Etsy", money(it["price"]), base, base + "LISTING.md", date, src, note))
    return out


def gumroad_rows() -> list[dict]:
    cat = json.loads((LAUNCH / "products" / "catalog.json").read_text())["products"]
    # The 20-Minute Budget predates the product line (launch/product/), so it isn't in catalog.json.
    cat = [{"slug": "20-minute-budget", "name": "The 20-Minute Budget", "price": 12}] + cat
    feature = {"20-minute-budget": "featured Jan 4", "debt-free-date-planner": "featured Jan 4",
               "credit-report-audit-kit": "featured Jan 25", "bill-cut-kit": "featured Jan 25",
               "money-toolkit-bundle": "on sale Nov 27-30"}
    out = []
    for p in cat:
        s = p["slug"]
        f = feature.get(s)
        out.append(row("Money Made Simple", p["name"], "Gumroad", money(p["price"]), f"products/{s}/", f"products/{s}/LISTING.md",
                       "Week of Nov 16" + (f"; {f}" if f else ""), "calendar",
                       "Create the discount codes in launch/products/UPSELL_PATH.md first; replace [your store link] and rebuild."))
    return out


def template_rows() -> list[dict]:
    import catalog as C
    out = []
    for i in C.ITEMS:
        s = i["slug"]
        dated = s.endswith("2027")
        plat = "Gumroad + Etsy" if dated else ("Gumroad (free, email capture)" if i["kind"] == "free" else "Gumroad")
        date = "Week of Nov 9" if dated else ("Week of Nov 16; on sale Nov 27-30" if "bundle" in i["kind"] else "Week of Nov 16")
        note = "Notion: run notion_build.py once and paste the duplicate link into links.json." if "notion" in i["kind"] else \
            "Paste the Sheets copy link into links.json and rebuild."
        src = "calendar"
        if i.get("twin_of"):  # Sheets/Notion versions of a printable: added after the calendar was made
            date, src = "Week of Dec 14, ahead of the January budgeting and savings-challenge peak", "proposed"
            note += f" Digital version of the Etsy printable '{i['twin_of']}'."
        out.append(row("Money Made Simple", i["name"], plat, money(i["price"]), f"templates/{s}/", f"templates/{s}/LISTING.md",
                       date, src, note))
    return out


def poster_rows() -> list[dict]:
    import posters as P
    return [row("Money Made Simple", p["name"], "Etsy (print on demand)", "about $22-$32", f"pod/{p['slug']}/",
                f"pod/{p['slug']}/LISTING.md", "Week of Nov 16; last orders before the print partner's mid-Dec cutoff",
                "calendar", "Connect Printify, check base price and shipping (keep $6+ per size), order one sample.")
            for p in P.POSTERS]


def book_rows() -> list[dict]:
    b = "Money Made Simple"
    return [
        row(b, "2027 Budget Planner (paperback)", "Amazon KDP", "$9.99-$12.99", "kdp/2027-Budget-Planner-KDP-*.pdf",
            "kdp/KDP_NOTES.md", "Submit week of Nov 9, publish after proof (week of Nov 16)", "calendar", "Order the proof first."),
        row(b, "Debt Payoff Journal (paperback)", "Amazon KDP", "$8.99-$10.99", "kdp/Debt-Payoff-Journal-KDP-*.pdf",
            "kdp/KDP_NOTES.md", "Submit week of Nov 23, publish week of Dec 7", "calendar", "Order the proof first."),
        row(b, "52-Week Savings Log (paperback)", "Amazon KDP", "$8.99-$10.99", "kdp/52-Week-Savings-Log-KDP-*.pdf",
            "kdp/KDP_NOTES.md", "Submit week of Nov 23, publish week of Dec 7", "calendar", "Order the proof first."),
        row(b, "Money Made Simple (Kindle ebook)", "Amazon KDP", "$8.99", "ebook/Money-Made-Simple.epub, ebook/Money-Made-Simple-Kindle-Cover.jpg",
            "ebook/KDP_NOTES.md", "Submit week of Nov 30", "calendar", "Decide the author name. Off Gumroad while in KDP Select."),
        row(b, "Money Made Simple (paperback)", "Amazon KDP", "$14.99", "ebook/Money-Made-Simple-Paperback-*.pdf",
            "ebook/KDP_NOTES.md", "Submit week of Nov 30, publish week of Dec 14", "calendar", "Order the proof first."),
    ]


# ---------------------------------------------------------------- brand shops (this branch, PR #6)

def brandshop_rows() -> list[dict]:
    import dinero_simple as DS
    import money_reset as MR
    import scam_decoded as SD
    import ten99 as T
    out = []
    dates = {"scam-decoded": ("Week of Nov 16 (holiday-scam season runs Nov 21-Dec 18)", "proposed"),
             "1099-money": ("Week of Nov 16, with the brand launch (dated 2027: list early)", "proposed"),
             "dinero-simple": ("After native review; target week of Dec 7 (December remittance and aguinaldo season)", "proposed"),
             "money-made-simple": ("Week of Dec 14, for New Year resets (budget searches peak in January)", "proposed")}
    differ = {
        "scam-card-set": "Cards only (no guide), so it sits beside the Scam-Proofing Kit and the seniors guide rather than competing with them. Replaces the fridge cards, caller ID card, my kit and my bundle (see Merged).",
        "freelancer-tax-planner-2027": "Sold as the paper companion to the Quarterly Tax Tracker (the brand's spreadsheet). My sheet and bundle were merged away (see Merged).",
        "presupuesto-familiar": "Different from El Presupuesto de 20 Minutos ($12, a guide plus a spreadsheet): this is a printable household binder for the whole family.",
        "money-reset-30-day": "A guided month of daily tasks, unlike the trackers (No-Spend Challenge) and the guide kits; leads into The 20-Minute Budget. Goes in the existing Money Made Simple Etsy shop.",
        "paquete-familia": "Different from El Paquete Dinero Simple ($29, the four guide kits): this bundles the three printables.",
    }
    for key, mod, plat in (("scam-decoded", SD, "Etsy + Gumroad"), ("1099-money", T, "Etsy + Gumroad"), ("dinero-simple", DS, "Etsy + Gumroad"),
                           ("money-made-simple", MR, "Etsy + Gumroad")):
        d, src = dates[key]
        for it in mod.LISTINGS:
            if it.get("status", "active") != "active":
                continue
            note = differ.get(it["slug"], "")
            if key == "dinero-simple":
                note = ("NATIVE REVIEW PENDING: sign brands/dinero-simple/REVIEW_CHECKLIST_ES.md first. " + note).strip()
            if key in ("scam-decoded", "1099-money") and "Etsy" in plat:
                note = (note + " Needs the brand's own Etsy shop (or a section in an existing one).").strip()
            out.append(row(mod.BRAND.name, it["name"], plat, money(it["price"]), f"brands/{key}/{it['slug']}/",
                           f"brands/{key}/{it['slug']}/LISTING.md", d, src, note))
    return out


# ---------------------------------------------------------------- other branches (listed from their LISTING files, Nov 7 2026)

OTHER_BRANCHES = [
    # Scam Decoded, PR #9 (branch claude/project-thread-wa5csw)
    ("Scam Decoded", "The Family Scam-Proofing Kit", "Gumroad (site funnel)", "$9", "scam-decoded/product-family-scam-proofing-kit/",
     "scam-decoded/product-family-scam-proofing-kit/LISTING.md", "With the brand launch (posting plan Day 1 is Sat Nov 7)", "proposed",
     "PR #9. Funnel emails and the scam checker sell this kit. Code LAUNCH ($5 for 7 days, only while true)."),
    ("Scam Decoded", "Protect Your Parents (guide)", "Gumroad", "$29", "scam-decoded/products/protect-your-parents/",
     "scam-decoded/products/protect-your-parents/LISTING.md", "Week of Nov 16", "proposed", "PR #9. Codes KITPARENTS, GUIDEKIT, LAUNCH."),
    ("Scam Decoded", "Scam Decoded for Seniors (large print)", "Etsy", "$7", "scam-decoded/products/seniors-pack/",
     "scam-decoded/products/seniors-pack/LISTING.md", "Week of Nov 16", "proposed", "PR #9. See the caller ID card overlap."),
    ("Scam Decoded", "Seniors pack group print license", "Gumroad", "$49 (+$19 per extra site)", "scam-decoded/products/seniors-pack/",
     "scam-decoded/products/seniors-pack/GROUP_LICENSE_LISTING.md", "When the first talk is booked", "proposed", "PR #9. For libraries and senior centers."),
    ("Scam Decoded", "Spot It, Stop It team training pack", "Gumroad", "$99", "scam-decoded/products/team-training/",
     "scam-decoded/products/team-training/LISTING.md", "Before the B2B outreach starts (Tue Nov 10)", "proposed", "PR #9. Code TEAMLAUNCH."),
    # 1099 Money, PR #10 (branch claude/project-thread-7o0kyt)
    ("1099 Money", "The Quarterly Tax Tracker", "Gumroad", "$15", "1099-money/product-quarterly-tax-tracker/",
     "1099-money/product-quarterly-tax-tracker/LISTING.md", "Mon Nov 16 (brand launch day 1)", "proposed", "PR #10. Code LAUNCH ($9 for 7 days)."),
    ("1099 Money", "The Rate & Contract Kit", "Gumroad", "$29", "1099-money/products/rate-contract-kit/",
     "1099-money/products/rate-contract-kit/LISTING.md", "Week of Nov 16", "proposed", "PR #10. Codes LAUNCH, TRACKER5, KIT29."),
    ("1099 Money", "The Freelancer Money Bundle", "Gumroad", "$49", "1099-money/products/bundle/",
     "1099-money/products/bundle/LISTING.md", "Week of Nov 16", "proposed", "PR #10. Codes LAUNCH, TRACKER15, KIT29."),
    ("1099 Money", "The Quarterly Tax Tracker", "Etsy", "$15", "etsy/1099-money/quarterly-tax-tracker/files/",
     "etsy/1099-money/quarterly-tax-tracker/LISTING-ETSY.md", "Week of Nov 16", "proposed", "PR #10. Etsy edition."),
    ("1099 Money", "The Rate & Contract Kit", "Etsy", "$29", "etsy/1099-money/rate-and-contract-kit/files/",
     "etsy/1099-money/rate-and-contract-kit/LISTING-ETSY.md", "Week of Nov 16", "proposed", "PR #10. Etsy edition."),
    ("1099 Money", "The Freelancer Money Bundle", "Etsy", "$49", "etsy/1099-money/freelancer-money-bundle/files/",
     "etsy/1099-money/freelancer-money-bundle/LISTING-ETSY.md", "Week of Nov 16", "proposed", "PR #10. Etsy edition."),
]
_DS = [("El Kit para Recortar Gastos", 5, "recorte-de-gastos", "recorte-de-gastos"),
       ("El Presupuesto de 20 Minutos", 12, None, "presupuesto-20-minutos"),
       ("Tu Fecha Sin Deudas", 17, "fecha-sin-deudas", "fecha-sin-deudas"),
       ("Empieza a Invertir con $100 al Mes", 19, "invertir-con-100", "invertir-con-100"),
       ("El Paquete Dinero Simple", 29, "paquete", "paquete")]
for _n, _p, _g, _e in _DS:
    _gp = f"dinero-simple/products/{_g}/" if _g else "dinero-simple/product/"
    OTHER_BRANCHES.append(("Dinero Simple", _n, "Gumroad", f"${_p}", _gp, _gp + "LISTING.md",
                           "After native review (reviewer brief: cheapest path launches El Presupuesto first)", "proposed",
                           "PR #11. NATIVE REVIEW PENDING. Codes RECORTE5, FECHA5, INVERTIR5."))
    OTHER_BRANCHES.append(("Dinero Simple", _n, "Etsy", f"${_p}", f"etsy/dinero-simple/{_e}/", f"etsy/dinero-simple/{_e}/LISTING.md",
                           "After native review", "proposed", "PR #11. NATIVE REVIEW PENDING. Etsy edition."))


def merged_rows() -> list[dict]:
    """Products built but deliberately not listed because they overlapped another product. Reverse in the module."""
    import scam_decoded as SD
    import ten99 as T
    return [dict(brand=mod.BRAND.name, product=it["name"], price=money(it["price"]), why=mod.RETIRED[it["slug"]],
                 undo=f"remove \"{it['slug']}\" from RETIRED in launch/brandshop/{mod.__name__}.py and rebuild")
            for mod in (SD, T) for it in mod.LISTINGS if it["slug"] in mod.RETIRED]


def all_rows() -> list[dict]:
    rows = etsy_rows() + gumroad_rows() + template_rows() + poster_rows() + book_rows() + brandshop_rows()
    rows += [row(*r) for r in OTHER_BRANCHES]
    return rows


def markdown(rows: list[dict]) -> str:
    def esc(x: str) -> str:
        return str(x).replace("|", "\\|")
    brands = list(dict.fromkeys(r["brand"] for r in rows))
    counts = ", ".join(f"{b} {sum(r['brand'] == b for r in rows)}" for b in brands)
    out = [f"""# Products catalog: every product, every brand

One sheet to list from. **{len(rows)} listings** ({counts}). Nothing in this list has been uploaded, listed or
submitted anywhere.

- **Files** and **Listing copy** paths are inside the project files folder `content-factory/` (the upload-ready copies).
  Each `LISTING.md` has the title, tags, price, description and the files to upload.
- **Launch** dates marked *calendar* come from the [launch calendar]({CALENDAR}); *proposed* ones are suggestions that
  follow the same logic (dated products first, gifts before the holiday cutoffs, everything live by mid-December).
- **No near-duplicates:** where two threads built overlapping products, one was merged into the other or clearly
  differentiated. Each choice is in the notes and in "Merged or retired" at the end, with how to undo it.
- Dinero Simple is blocked on a fluent Spanish speaker's review; nothing in Spanish goes up before that.
- Regenerate after changing a price or name: `python launch/catalog/build_catalog.py`. Also as `PRODUCTS_CATALOG.csv`.
"""]
    for b in brands:
        br = [r for r in rows if r["brand"] == b]
        out.append(f"\n## {b} ({len(br)})\n\n| Product | Platform | Price | Files | Listing copy | Launch | Date | Notes |\n|---|---|---|---|---|---|---|---|")
        for r in br:
            out.append("| " + " | ".join(esc(r[k]) if k not in ("files", "listing") else f"`{esc(r[k])}`"
                                         for k in ("product", "platform", "price", "files", "listing", "launch", "date_source", "notes")) + " |")
    m = merged_rows()
    out.append(f"\n## Merged or retired ({len(m)}), reversible\n\nBuilt, checked and kept in the repo, but not listed, so the "
               "catalog has no near-duplicates. These were default choices; undo any of them as shown.\n\n"
               "| Brand | Product | Price | Why | To undo |\n|---|---|---|---|---|")
    out += [f"| {r['brand']} | {r['product']} | {r['price']} | {esc(r['why'])} | {esc(r['undo'])} |" for r in m]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(LAUNCH / "PRODUCTS_CATALOG.md"))
    a = ap.parse_args()
    rows = all_rows()
    out = Path(a.out)
    out.write_text(markdown(rows))
    with open(out.with_suffix(".csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} listings -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
