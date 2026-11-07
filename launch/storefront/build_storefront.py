"""Gumroad storefront kit for each brand, plus one cross-sell map across all of them.

    python launch/storefront/build_storefront.py [--out launch/storefront/dist] [--no-images]

Per brand (dist/<brand>/): STOREFRONT.md (profile name, username, bio, about text, profile sections with products in
order, checkout upsells, receipt notes) plus a profile picture (800x800) and a cover/banner (2400x800). Across brands:
CROSS_SELL.md and cross_sell.csv, one row per Gumroad product: what to recommend after it's bought, why, where, and
the code. The product list comes from the catalog (launch/catalog/build_catalog.py), so it matches PRODUCTS_CATALOG.md.
Nothing is uploaded or changed on Gumroad.
"""
from __future__ import annotations

import argparse
import csv
import html
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAUNCH = HERE.parent
sys.path.insert(0, str(LAUNCH / "catalog"))
import build_catalog as CAT  # noqa: E402  (also puts etsy/, templates/, pod/, brandshop/ on the path)

BRANDS = {
    "Money Made Simple": dict(
        key="money-made-simple", username="moneymadesimple", palette=("#1b2a24", "#f6f3ea", "#2f9e6e", "#e9b949"),
        tagline="Plain-English money tools: budget, debt, credit and investing.",
        bio="Simple money tools that take 20 minutes, not a weekend. Budgets, debt plans, credit and first investing. Not financial advice.",
        about=("Money Made Simple makes the tools we wanted when money felt messy: a weekly number instead of a 40-line "
               "budget, a real debt-free date, a credit report you can actually read. Every guide comes with a spreadsheet "
               "that does the sums. Educational, not financial advice. Made with the help of AI tools and checked by a person."),
        sections=[("Start here", ["The Bill Cut Kit", "The 20-Minute Budget"]),
                  ("Get out of debt and fix your credit", ["The Debt-Free Date Planner", "The Credit Report Audit Kit"]),
                  ("Start investing", ["Start Investing With $100 a Month"]),
                  ("2027 planners", ["2027 Budget Sheet", "2027 Money HQ for Notion"]),
                  ("Google Sheets templates", ["Monthly Budget Sheet", "Debt Payoff Sheet", "Savings Goals Sheet", "Money Sheets Bundle"]),
                  ("Notion templates", ["Notion Money Starter", "Notion Budget Planner", "Notion Debt Payoff Tracker",
                                        "Notion Savings Goals Tracker", "Notion Money HQ"]),
                  ("Everything", ["The Money Made Simple Toolkit"])],
        featured="The 20-Minute Budget"),
    "Scam Decoded": dict(
        key="scam-decoded", username="scamdecoded", palette=("#0d1b2a", "#f4f1ea", "#2ec4b6", "#ff9f1c"),
        tagline="Spot the scam before it costs you. Plans, cards and training.",
        bio="Scams decoded in plain English: family plans, large-print cards and team training. General education, not legal or financial advice.",
        about=("Scam Decoded explains how today's scams work and gives families and teams a plan for the moment the phone "
               "rings: a safe word, a call-back rule, and cards by the phone. Contacts checked against the FTC, FBI and DOJ. "
               "General education, not legal or financial advice. Made with the help of AI tools and checked by a person."),
        sections=[("For your family", ["The Family Scam-Proofing Kit", "Scam Decoded Card Set"]),
                  ("For your parents", ["Protect Your Parents (guide)"]),
                  ("For teams and venues", ["Spot It, Stop It team training pack", "Seniors pack group print license"])],
        featured="The Family Scam-Proofing Kit"),
    "1099 Money": dict(
        key="1099-money", username="1099money", mark="1099", palette=("#14213d", "#f7f3ea", "#3cc6a0", "#ff7a45"),
        tagline="Freelance money, without the April panic.",
        bio="Trackers and kits for freelancers: quarterly taxes, rates, contracts and invoices. Educational, not tax advice.",
        about=("1099 Money is for freelancers and gig workers who get paid with no tax taken out. Set aside the right share, "
               "hit the four estimated-tax dates, price your work and get paid. Dates follow the IRS weekend and holiday "
               "rule; check irs.gov and your state. Educational, not tax, legal or financial advice. Made with the help of "
               "AI tools and checked by a person."),
        sections=[("Quarterly taxes", ["The Quarterly Tax Tracker", "2027 Freelancer Tax-Year Planner (printable)"]),
                  ("Get paid", ["The Rate & Contract Kit"]),
                  ("Everything", ["The Freelancer Money Bundle"])],
        featured="The Quarterly Tax Tracker"),
    "Dinero Simple": dict(
        key="dinero-simple", username="dinerosimple", palette=("#14213d", "#fbf5e9", "#2ab7a9", "#ff7a59"),
        tagline="Tu dinero, simple y en español.",
        bio="Herramientas de dinero en español para latinos en EE. UU.: presupuesto, deudas, crédito, envíos e inversión. No es asesoría financiera.",
        about=("Dinero Simple hace guías y plantillas en español para quien vive en Estados Unidos: un número semanal para "
               "gastar, un plan para tus deudas, tu crédito desde cero (también con ITIN) y cuánto llega de verdad cuando "
               "envías dinero. Contenido educativo, no es asesoría financiera, fiscal ni legal. Hecho con ayuda de "
               "herramientas de IA y revisado por una persona."),
        sections=[("Empieza aquí", ["El Kit para Recortar Gastos", "El Presupuesto de 20 Minutos"]),
                  ("Para la familia", ["El Presupuesto Familiar", "El Registro de Envíos", "La Lista para Construir tu Crédito",
                                       "El Paquete de la Familia"]),
                  ("Deudas e inversión", ["Tu Fecha Sin Deudas", "Empieza a Invertir con $100 al Mes"]),
                  ("Todo junto", ["El Paquete Dinero Simple"])],
        featured="El Presupuesto de 20 Minutos",
        review="NATIVE REVIEW PENDING: the Spanish bio, about text, section names and banner need the same review as the products."),
}

# (after buying, recommend, why, where, code). "Where" uses Gumroad's own tools: a checkout upsell on the product,
# the receipt/thank-you note, or the post-purchase email. Codes marked (new) don't exist yet in any plan.
CROSS_SELL = {
    # Money Made Simple (launch/products/UPSELL_PATH.md)
    "The Bill Cut Kit": ("The 20-Minute Budget", "The money the kit frees up needs a plan.", "Receipt note + email 2", "BILLCUT5"),
    "The 20-Minute Budget": ("The Debt-Free Date Planner", "Once the weekly number works, the extra goes to debt.", "Receipt note + email", "BUDGET5"),
    "The Credit Report Audit Kit": ("The Debt-Free Date Planner", "Most people who audit their credit have debt to plan.", "Receipt note", "AUDIT5"),
    "The Debt-Free Date Planner": ("Start Investing With $100 a Month", "What to do with the payment once the debt is gone.", "Receipt note", "DEBTFREE5"),
    "Start Investing With $100 a Month": ("The 20-Minute Budget", "Finding the $100 a month starts with a budget.", "Receipt note", "INVEST5"),
    "The Money Made Simple Toolkit": ("2027 Budget Sheet", "The toolkit is undated; the 2027 sheet runs the year month by month.", "Email", ""),
    "Monthly Budget Sheet": ("Money Sheets Bundle", "Adds the debt and savings sheets for the difference.", "Checkout upsell", ""),
    "Debt Payoff Sheet": ("Money Sheets Bundle", "Adds the budget and savings sheets for the difference.", "Checkout upsell", ""),
    "Savings Goals Sheet": ("Money Sheets Bundle", "Adds the budget and debt sheets for the difference.", "Checkout upsell", ""),
    "Money Sheets Bundle": ("The Money Made Simple Toolkit", "The guides behind the sheets, for people who want the why.", "Email", ""),
    "2027 Budget Sheet": ("The Debt-Free Date Planner", "A dated budget shows the debt; the planner gives it an end date.", "Receipt note", ""),
    "2027 Money HQ for Notion": ("The Money Made Simple Toolkit", "The guides and spreadsheets behind the Notion setup.", "Email", ""),
    "Notion Money Starter": ("Notion Budget Planner", "The free starter's next step.", "Delivery email", "STARTER20"),
    "Notion Budget Planner": ("Notion Money HQ", "Adds the debt and savings trackers for the difference.", "Checkout upsell", ""),
    "Notion Debt Payoff Tracker": ("Notion Money HQ", "Adds the budget and savings trackers for the difference.", "Checkout upsell", ""),
    "Notion Savings Goals Tracker": ("Notion Money HQ", "Adds the budget and debt trackers for the difference.", "Checkout upsell", ""),
    "Notion Money HQ": ("2027 Money HQ for Notion", "The same HQ, dated month by month for 2027.", "Email", ""),
    # Scam Decoded (scam-decoded/products/LADDER.md)
    "The Family Scam-Proofing Kit": ("Protect Your Parents (guide)", "Families who make the plan usually want to help their parents next.", "Receipt note + email 7", "KITPARENTS"),
    "Protect Your Parents (guide)": ("Scam Decoded Card Set", "The guide's plan, as cards by the phone and in the wallet. (The kit itself comes free with GUIDEKIT.)", "Receipt note", ""),
    "Scam Decoded Card Set": ("The Family Scam-Proofing Kit", "The cards are the reminders; the kit is the plan behind them.", "Receipt note", ""),
    "Spot It, Stop It team training pack": ("Seniors pack group print license", "Teams that serve older clients can hand out the large-print pack.", "Email", ""),
    "Seniors pack group print license": ("Spot It, Stop It team training pack", "Staff training to go with the handouts.", "Email", "TEAMLAUNCH (first 14 days)"),
    # 1099 Money (1099-money/products/UPSELL_PATH.md)
    "The Quarterly Tax Tracker": ("The Freelancer Money Bundle", "Adds the rate, contract and invoice kit and the email scripts.", "Checkout upsell ($34 more)", "TRACKER15"),
    "The Rate & Contract Kit": ("The Freelancer Money Bundle", "Adds the tax tracker and the email scripts.", "Checkout upsell ($20 more)", "KIT29"),
    "The Freelancer Money Bundle": ("2027 Freelancer Tax-Year Planner (printable)", "A paper year-planner beside the spreadsheet: dates, months and the tax-time checklist.", "Email", ""),
    "2027 Freelancer Tax-Year Planner (printable)": ("The Quarterly Tax Tracker", "The planner is for the desk; the tracker does the sums.", "Receipt note", ""),
    # Dinero Simple (dinero-simple product pages and LISTING files)
    "El Kit para Recortar Gastos": ("El Presupuesto de 20 Minutos", "Lo que recortas necesita un plan.", "Receipt note", "RECORTE5"),
    "El Presupuesto de 20 Minutos": ("Tu Fecha Sin Deudas", "Con el número semanal, lo que sobra va a las deudas.", "Receipt note", ""),
    "Tu Fecha Sin Deudas": ("Empieza a Invertir con $100 al Mes", "Qué hacer con el pago cuando terminas la deuda.", "Receipt note", "FECHA5"),
    "Empieza a Invertir con $100 al Mes": ("El Presupuesto de 20 Minutos", "De dónde sacar los $100.", "Receipt note", "INVERTIR5"),
    "El Paquete Dinero Simple": ("El Paquete de la Familia", "Los cuatro kits son para ti; este paquete es para toda la casa.", "Email", ""),
    "El Presupuesto Familiar": ("El Registro de Envíos", "Si el envío a la familia es un gasto fijo, vale la pena compararlo.", "Receipt note", ""),
    "El Registro de Envíos": ("La Lista para Construir tu Crédito", "El siguiente paso para la familia: crédito propio.", "Receipt note", ""),
    "La Lista para Construir tu Crédito": ("Tu Fecha Sin Deudas", "Construir crédito y salir de deudas van juntos.", "Receipt note", ""),
    "El Paquete de la Familia": ("El Presupuesto de 20 Minutos", "La guía y la hoja de cálculo detrás del número semanal.", "Email", ""),
}


def gumroad_products() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    seen = set()
    for r in CAT.all_rows():
        if "Gumroad" in r["platform"] and (r["brand"], r["product"]) not in seen:
            seen.add((r["brand"], r["product"]))
            out.setdefault(r["brand"], []).append(r)
    return out


def problems() -> list[str]:
    """Every Gumroad product is in exactly one section and has a cross-sell to another product of its brand."""
    bad, prods = [], gumroad_products()
    for brand, rows in prods.items():
        names = [r["product"] for r in rows]
        placed = [p for _, ps in BRANDS[brand]["sections"] for p in ps]
        bad += [f"{brand}: '{n}' is in no section" for n in names if n not in placed]
        bad += [f"{brand}: section lists unknown '{p}'" for p in placed if p not in names]
        bad += [f"{brand}: '{p}' is in more than one section" for p in set(placed) if placed.count(p) > 1]
        for n in names:
            if n not in CROSS_SELL:
                bad.append(f"{brand}: no cross-sell for '{n}'")
            elif CROSS_SELL[n][0] not in names or CROSS_SELL[n][0] == n:
                bad.append(f"{brand}: cross-sell for '{n}' points at '{CROSS_SELL[n][0]}', not another product of the brand")
        if BRANDS[brand]["featured"] not in names:
            bad.append(f"{brand}: featured product isn't a Gumroad product")
    return bad


def _img_doc(brand: str, w: int, h: int, avatar: bool) -> str:
    b = BRANDS[brand]
    ink, cream, acc, warm = b["palette"]
    E = html.escape
    words = brand.split()
    if avatar:
        initials = b.get("mark") or "".join(x[0] for x in words if x[0].isalnum())[:3]
        body = (f'<div style="width:{w}px;height:{h}px;background:{ink};display:flex;align-items:center;justify-content:center">'
                f'<div style="width:{w * .78:.0f}px;height:{h * .78:.0f}px;border-radius:50%;background:{acc};display:flex;'
                f'align-items:center;justify-content:center;font-size:{w * (.34 if len(initials) < 3 else .26 if len(initials) == 3 else .2):.0f}px;font-weight:900;'
                f'color:{ink};letter-spacing:-.03em">{E(initials)}</div></div>')
    else:
        n = len(gumroad_products().get(brand, []))
        body = (f'<div style="width:{w}px;height:{h}px;background:{cream};position:relative;overflow:hidden">'
                f'<div style="position:absolute;right:-{h * .6:.0f}px;top:-{h * .25:.0f}px;width:{h * 1.1:.0f}px;height:{h * 1.1:.0f}px;border-radius:50%;background:{acc}"></div>'
                f'<div style="position:absolute;left:-{h * .2:.0f}px;bottom:-{h * .35:.0f}px;width:{h * .7:.0f}px;height:{h * .7:.0f}px;border-radius:50%;background:{warm}"></div>'
                f'<div style="position:absolute;left:{w * .2:.0f}px;right:{w * .2:.0f}px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center">'
                f'<div style="font-size:{h * .16:.0f}px;font-weight:900;letter-spacing:-.02em;color:{ink}">{E(brand)}</div>'
                f'<div style="font-size:{h * .065:.0f}px;color:{ink};opacity:.8;margin-top:{h * .03:.0f}px">{E(b["tagline"])}</div>'
                f'<div style="margin-top:{h * .05:.0f}px;font-size:{h * .045:.0f}px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:{ink}">{n} digital products &middot; instant download</div>'
                f'</div></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'html,body{{margin:0}} body{{font-family:Inter,Arial,sans-serif}}</style></head><body>{body}</body></html>')


def storefront_md(brand: str, rows: list[dict]) -> str:
    b = BRANDS[brand]
    by = {r["product"]: r for r in rows}
    sec = []
    for title, names in b["sections"]:
        lines = "\n".join(f"   {i}. {n} ({by[n]['price']}) · files `{by[n]['files']}` · copy `{by[n]['listing']}`"
                          for i, n in enumerate(names, 1))
        sec.append(f"1. **{title}**\n{lines}")
    upsells = [f"| {n} | {t} | {why} | {where} | {('`' + c + '`') if c else '–'} |"
               for n, (t, why, where, c) in CROSS_SELL.items() if n in by]
    review = f"\n> **{b['review']}**\n" if b.get("review") else ""
    return f"""# Gumroad storefront: {brand}
{review}
Nothing here has been set up. Do it in Gumroad (Settings > Profile, then the profile page editor) after the products
from `PRODUCTS_CATALOG.md` exist. Gumroad gives one profile per account, so each brand gets its own account (its own
email), the same way each brand gets its own Etsy shop.

## Profile

- **Name:** {brand}
- **Username:** `{b['username']}` (so the store is {b['username']}.gumroad.com; pick the closest free one)
- **Profile picture:** `avatar.png` (800 x 800)
- **Cover / banner:** `cover.png` (2400 x 800, text kept in the middle third so mobile crops don't cut it). If the
  profile layout you pick has no banner, use it as the first image of the featured product instead.
- **Bio** ({len(b['bio'])} characters): {b['bio']}

**About** (a text section at the bottom of the profile):

> {b['about']}

## Sections, in this order

Add one product section per heading, with the products in this order. Put **{b['featured']}** in a "Featured product"
section above them.

{chr(10).join(sec)}

## After each purchase

One recommendation per product, set where the table says: a checkout upsell (Checkout > Upsells, never pre-ticked),
the product's receipt/thank-you note, or the post-purchase email. Codes are the ones already printed in the products;
create them before the first sale. Full map across brands: `CROSS_SELL.md`.

| After buying | Recommend | Why | Where | Code |
|---|---|---|---|---|
{chr(10).join(upsells)}

## Rules

Same as every listing: no fake urgency or countdowns, no income promises, no testimonials until real buyers give them,
"not financial advice" on every page, AI help disclosed. Launch codes only while they're true.
"""


def cross_sell_md(prods: dict[str, list[dict]]) -> str:
    out = ["# Cross-sell map: what to recommend after each purchase\n",
           "One row per Gumroad product, every brand. Recommendations stay inside the brand. Codes are the ones the "
           "products already print; create them in each Gumroad account before the first sale. Built by "
           "`launch/storefront/build_storefront.py` from the same product list as `PRODUCTS_CATALOG.md`.\n"]
    for brand, rows in prods.items():
        out.append(f"\n## {brand}\n\n| After buying | Price | Recommend | Why | Where | Code |\n|---|---|---|---|---|---|")
        price = {r["product"]: r["price"] for r in rows}
        for r in rows:
            t, why, where, code = CROSS_SELL[r["product"]]
            out.append(f"| {r['product']} | {r['price']} | {t} ({price.get(t, '?')}) | {why} | {where} | {('`' + code + '`') if code else '–'} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    bad = problems()
    for p in bad:
        print("FAIL", p)
    if bad:
        return 1
    out, prods = Path(a.out), gumroad_products()
    jobs = []
    work = Path(tempfile.mkdtemp(prefix="storefront-"))
    for brand, rows in prods.items():
        d = out / BRANDS[brand]["key"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "STOREFRONT.md").write_text(storefront_md(brand, rows))
        for name, w, h, av in (("cover", 2400, 800, False), ("avatar", 800, 800, True)):
            src = work / f"{BRANDS[brand]['key']}-{name}.html"
            src.write_text(_img_doc(brand, w, h, av))
            jobs.append({"src": str(src), "png": str(d / f"{name}.png"), "w": w, "h": h, "scale": 1})
    (out / "CROSS_SELL.md").write_text(cross_sell_md(prods))
    with open(out / "cross_sell.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["brand", "after_buying", "recommend", "why", "where", "code"])
        for brand, rows in prods.items():
            for r in rows:
                wr.writerow([brand, r["product"], *CROSS_SELL[r["product"]]])
    if not a.no_images:
        import build_etsy
        build_etsy.run_jobs(jobs)
    print(f"storefront kits for {len(prods)} brands -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
