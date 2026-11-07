"""Build the brand shop files (Scam Decoded, 1099 Money, Dinero Simple, and Money Made Simple's Money Reset): PDFs, the workbook, mockups, LISTING.md files and bundle zips.

    python launch/brandshop/build_brandshop.py [--brand scam-decoded 1099-money] [--no-mockups] [--check]

Output goes to launch/brandshop/dist/<brand>/<listing>/ (git-ignored). --check recalculates the workbook in LibreOffice
and fails on any formula error. Nothing is listed or uploaded anywhere.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import shop  # noqa: E402  (also puts launch/etsy on the path)
import build_etsy  # noqa: E402
import scam_decoded as SD  # noqa: E402
import ten99 as T  # noqa: E402
import ten99_sheet  # noqa: E402
import dinero_simple as DS  # noqa: E402
import remesas_sheet  # noqa: E402
import money_reset as MR  # noqa: E402
import schedule_c_pack as SC  # noqa: E402

SIZES = shop.SIZES

# Shorter cover lines for the mockups, where the listing name or the hook's first sentence doesn't fit or says too little.
MOCK = {
    "scam-card-set": ("Scam Decoded Card Set", "Seven bold cards, a large-print phone script and wallet cards. Cards only, no reading."),
    "family-scam-safety-kit": ("Family Scam-Safety Kit", "Red flags, a family plan and what to do if it happens, in 11 printable pages."),
    "scam-fridge-cards": ("Scam Fridge Cards", "Six bold cards, one rule each, for the fridge or the desk."),
    "caller-id-script-card": ("Caller ID Script Card", "What to say when a suspicious call comes in, in large print."),
    "scam-safety-bundle": ("Scam-Safety Bundle", "The 11-page kit, six fridge cards and the caller ID script cards."),
    "freelancer-tax-planner-2027": ("2027 Freelancer Tax Planner", "Income, expenses, mileage and the four estimated-tax dates, in 25 printable pages."),
    "freelancer-tax-sheet-2027": ("2027 Freelancer Tax Tracker", "A Google Sheets and Excel tracker that adds itself up by month, quarter and category."),
    "freelancer-tax-bundle-2027": ("2027 Freelancer Tax Bundle", "The 25-page printable planner and the spreadsheet tracker together."),
    "presupuesto-familiar": ("Presupuesto Familiar", "Lo que entra, lo que sale y un número semanal para toda la casa, en 12 páginas."),
    "registro-de-envios": ("El Registro de Envíos", "Compara antes de enviar y guarda cada envío. Para imprimir y en Google Sheets."),
    "construir-credito": ("Construye tu Crédito", "Tus primeros 12 meses paso a paso, también con ITIN, en 8 páginas."),
    "money-reset-30-day": ("The Money Reset", "30 days, one 15-minute task a day: see it, cut it, plan it, pay it down."),
    "schedule-c-setup-pack": ("Schedule C Setup Pack", "Schedule C categories, a year-end packet and a mileage log, for TaxHacker users."),
    "paquete-familia": ("Paquete de la Familia", "El presupuesto, el registro de envíos y la lista de crédito, en una descarga."),
}
CHIPS = {"sheet": ["Instant download", "Google Sheets + Excel"], "bundle": ["Instant download", "Printable + digital"]}
# Spanish mockup wording (Dinero Simple). Needs the same native review as the rest.
ES = {"chips": {"print": ["Descarga inmediata", "Carta + A4", "En español"],
                "print+sheet": ["Descarga inmediata", "PDF + Google Sheets", "En español"],
                "bundle": ["Descarga inmediata", "3 en 1", "En español"]},
      "footer": "Educativo, no es asesoría",
      "text": {"inside_kick": "Lo que incluye", "inside_pages": "{n} de las páginas", "inside_count": "{n} archivos",
               "how_kick": "Cómo funciona", "how_title": "Listo en minutos", "get_kick": "Qué incluye"},
      "steps": [("Descarga", "Tus archivos están listos en cuanto pagas."), ("Imprime", "Carta o A4, en casa, las veces que quieras."),
                ("Llena", "Con pluma, o en una tablet con cualquier app para PDF.")]}


def doc(brand: shop.Brand, sections: list[tuple[str, str]], title: str, w: str, h: str, page_name: str,
        extra_css: str = "") -> str:
    body = "".join(f'<section class="{cls}">{html}</section>\n' for cls, html in sections)
    return (f'<!doctype html><html lang="{brand.lang}"><head><meta charset="utf-8"><title>{title}</title><style>'
            f'@page{{size:{page_name};margin:0}}\n{brand.css(w, h)}{extra_css}</style></head><body>{body}</body></html>')


def as_pages(cards: list[str]) -> list[tuple[str, str]]:
    """Cards rendered one per page, with the card itself as the measured .page (so overflow is caught)."""
    return [("page card" + (" dark" if 'class="card dark"' in c else ""), c.split(">", 1)[1].rsplit("</div>", 1)[0])
            for c in cards]


CARD_EXTRA = SD.CARD_CSS + SD.WALLET_CSS + ".page.sheet{ padding:.4in; }\n.page.card{ margin:0; }\n"


def scam_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = SD.BRAND, [], {}

    def add(slug: str, name: str, html: str) -> Path:
        d = out / slug
        d.mkdir(parents=True, exist_ok=True)
        src = work / f"{slug}-{name}.html"
        src.write_text(html)
        pdf = d / f"{name}.pdf"
        jobs.append({"src": str(src), "pdf": str(pdf)})
        files.setdefault(slug, []).append(pdf)
        return pdf

    for size, (w, h, pn) in SIZES.items():
        add("family-scam-safety-kit", f"Family-Scam-Safety-Kit-{size}",
            doc(B, [("page", p) for p in SD.kit_pages()], "Family Scam-Safety Kit", w, h, pn, CARD_EXTRA))
        add("scam-fridge-cards", f"Scam-Fridge-Cards-{size}",
            doc(B, [("page sheet", s) for s in SD.card_sheets(SD.fridge_cards())], "Scam Fridge Cards", w, h, pn, CARD_EXTRA))
        add("caller-id-script-card", f"Caller-ID-Script-Card-{size}",
            doc(B, [("page", SD.caller_id_large()), ("page sheet", SD.card_sheets([SD.caller_id_card()] * 2)[0]),
                    ("page sheet", SD.wallet_sheet())], "Caller ID Script Card", w, h, pn, CARD_EXTRA))
    for size, (w, h, pn) in SIZES.items():
        add("scam-card-set", f"Scam-Card-Set-{size}",
            doc(B, [("page sheet", x) for x in SD.card_sheets(SD.fridge_cards() + [SD.caller_id_card()])]
                + [("page", SD.caller_id_large()), ("page sheet", SD.wallet_sheet())], "Scam Decoded Card Set", w, h, pn, CARD_EXTRA))
    add("scam-card-set", "Scam-Card-Set-4x6",
        doc(B, as_pages(SD.fridge_cards() + [SD.caller_id_card()]), "Scam Decoded Card Set 4x6", "6in", "4in", "6in 4in", CARD_EXTRA))
    add("scam-fridge-cards", "Scam-Fridge-Cards-4x6",
        doc(B, as_pages(SD.fridge_cards()), "Scam Fridge Cards 4x6", "6in", "4in", "6in 4in", CARD_EXTRA))
    add("caller-id-script-card", "Caller-ID-Script-Card-4x6",
        doc(B, as_pages([SD.caller_id_card()]), "Caller ID Script Card 4x6", "6in", "4in", "6in 4in", CARD_EXTRA))
    # A check-only render: each wallet card as its own measured page (not shipped).
    wsrc = work / "wallet-check.html"
    wsrc.write_text(doc(B, [("page wallet", SD.wallet_card().split(">", 1)[1].rsplit("</div>", 1)[0])], "wallet", "3.5in",
                        "2in", "3.5in 2in", CARD_EXTRA + ".page.wallet{ margin:0; }"))
    jobs.append({"src": str(wsrc), "pdf": str(work / "wallet-check.pdf")})
    return jobs, files


def dinero_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = DS.BRAND, [], {}
    parts = {"presupuesto-familiar": ("El-Presupuesto-Familiar", "El Presupuesto Familiar", DS.presupuesto_pages),
             "registro-de-envios": ("El-Registro-de-Envios", "El Registro de Envíos", DS.remesas_pages),
             "construir-credito": ("Construye-tu-Credito", "La Lista para Construir tu Crédito", DS.credito_pages)}
    for slug, (stem, title, pages) in parts.items():
        d = out / slug
        d.mkdir(parents=True, exist_ok=True)
        for size, (w, h, pn) in SIZES.items():
            src = work / f"{slug}-{size}.html"
            src.write_text(doc(B, [("page", p) for p in pages()], title, w, h, pn))
            pdf = d / f"{stem}-{'Carta' if size == 'Letter' else size}.pdf"
            jobs.append({"src": str(src), "pdf": str(pdf)})
            files.setdefault(slug, []).append(pdf)
    files["registro-de-envios"].append(remesas_sheet.build(out / "registro-de-envios" / "Registro-de-Envios.xlsx"))
    return jobs, files


def mms_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = MR.BRAND, [], {}
    d = out / "money-reset-30-day"
    d.mkdir(parents=True, exist_ok=True)
    for size, (w, h, pn) in SIZES.items():
        src = work / f"money-reset-{size}.html"
        src.write_text(doc(B, [("page", p) for p in MR.pages()], "The Money Reset", w, h, pn, MR.CSS))
        pdf = d / f"The-Money-Reset-30-Day-Challenge-{size}.pdf"
        jobs.append({"src": str(src), "pdf": str(pdf)})
        files.setdefault("money-reset-30-day", []).append(pdf)
    return jobs, files


def schedc_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = SC.BRAND, [], {}
    d = out / "schedule-c-setup-pack"
    d.mkdir(parents=True, exist_ok=True)
    for size, (w, h, pn) in SIZES.items():
        src = work / f"schedc-{size}.html"
        src.write_text(doc(B, [("page", p) for p in SC.pages()], "Schedule C Setup Pack", w, h, pn, SC.CSS))
        pdf = d / f"Schedule-C-Setup-Pack-Guide-{size}.pdf"
        jobs.append({"src": str(src), "pdf": str(pdf)})
        files.setdefault("schedule-c-setup-pack", []).append(pdf)
    xlsx = SC.build_workbook(d / "Year-End-Packet.xlsx")
    files["schedule-c-setup-pack"] = [xlsx, *files["schedule-c-setup-pack"], *SC.write_mapping(d)]
    return jobs, files


def review_checklist(mod, files: dict[str, list[Path]]) -> str:
    rows = "\n".join(f"| {it['name']} | `{it['slug']}/` | {', '.join(f'`{x}`' for x in it['files'])} | | |" for it in mod.LISTINGS
                     if it.get("status", "active") == "active")
    return f"""# Revisión nativa: Dinero Simple, productos para Etsy y Gumroad

**Nothing here can be listed until this is signed.** A fluent Spanish speaker reads every listed item: the Etsy title,
the 13 tags, the Etsy description, the Gumroad copy (all in each `LISTING.md`), every page of each PDF, the spreadsheet
tabs and the mockup images.

Check for: natural, neutral US-Latino Spanish in the tú form; no anglicisms that read as errors; the money and legal
facts (remittance rights, the 1% cash remittance tax from 2026, AnnualCreditReport.com, CROA, CPN warning) still
current; nothing that reads as a promise or as financial, tax or legal advice.

| Producto | Carpeta | Archivos | Revisado por | Fecha |
|---|---|---|---|---|
{rows}

Cambios pedidos:

-

Firmado (nombre y fecha): ______________________
"""


def ten99_jobs(out: Path, work: Path) -> tuple[list[dict], dict[str, list[Path]]]:
    B, jobs, files = T.BRAND, [], {}
    for size, (w, h, pn) in SIZES.items():
        d = out / "freelancer-tax-planner-2027"
        d.mkdir(parents=True, exist_ok=True)
        src = work / f"planner-{size}.html"
        src.write_text(doc(B, [("page", p) for p in T.planner_pages()], "2027 Freelancer Tax-Year Planner", w, h, pn))
        pdf = d / f"2027-Freelancer-Tax-Planner-{size}.pdf"
        jobs.append({"src": str(src), "pdf": str(pdf)})
        files.setdefault("freelancer-tax-planner-2027", []).append(pdf)
    d = out / "freelancer-tax-sheet-2027"
    d.mkdir(parents=True, exist_ok=True)
    src = work / "sheet-start.html"
    src.write_text(doc(B, [("page", sheet_start_page())], "Start here", "8.5in", "11in", "Letter"))
    pdf = d / "2027-Freelancer-Tax-Tracker-Start-Here.pdf"
    jobs.append({"src": str(src), "pdf": str(pdf)})
    xlsx = ten99_sheet.build(d / "2027-Freelancer-Tax-Tracker.xlsx")
    files["freelancer-tax-sheet-2027"] = [xlsx, pdf]
    return jobs, files


def sheet_start_page() -> str:
    tabs = [("Setup", "Your set-aside %, the IRS mileage rate once published, your income goal and the expense categories."),
            ("Income", "One row per payment: date, client, invoice, amount, and whether a 1099 is expected."),
            ("Expenses", "One row per business cost, with a category from the dropdown."),
            ("Mileage", "One row per business trip; the value uses the rate on Setup."),
            ("Months", "Income, expenses, profit and set-aside for each month, with a chart."),
            ("Quarters", "The four 2027 estimated-tax due dates, each quarter's profit and set-aside, and what you paid."),
            ("Categories", "Expense totals by category, ready for tax time."),
            ("Clients", "What each client paid you, and a tick when their 1099 arrives.")]
    rows = "".join(f"<tr><td class='wrap'><b>{a}</b></td><td class='wrap'>{b}</td></tr>" for a, b in tabs)
    return T.BRAND.page("Your tracker: <em>start here</em>", "2027 Freelancer Tax Tracker", f'''
      <h3 style="margin-top:0">Open it</h3>
      <ol class="steps big">
        <li><b>Google Sheets (free):</b> upload the .xlsx to Google Drive, open it, then File &gt; Save as Google Sheets.</li>
        <li><b>Excel or Apple Numbers:</b> just open the .xlsx.</li>
        <li>Delete the rows marked "(example)" on Income, Expenses, Mileage and Clients.</li>
        <li>Yellow cells are yours. Everything else is a formula; leave it alone.</li>
      </ol>
      <h3>The tabs</h3><table><tr><th style="width:20%">Tab</th><th>What it does</th></tr>{rows}</table>
      <div class="box fineprint" style="margin-top:auto">The tracker doesn't calculate your tax. The set-aside is your
      profit times a percentage you choose (pick it with a tax professional or the IRS Form 1040-ES worksheet). Federal due
      dates follow the IRS weekend and holiday rule; check irs.gov and your state. An organising tool, not tax, legal or
      financial advice. Made by 1099 Money with the help of AI tools.</div>''', kicker="1099 Money")


def sheet_preview_pages(xlsx: Path, work: Path) -> list[Path]:
    """Real pages of the workbook, printed by LibreOffice, for the mockups: Months, Quarters, Income."""
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(xlsx)],
                   capture_output=True, timeout=240, check=True)
    pdf = work / (xlsx.stem + ".pdf")
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout.split("\f")
    want = [f"{T.YEAR} month by month", "Estimated tax for", "Date paid"]
    picks = []
    for w in want:
        for i, t in enumerate(text):
            if w in t and i + 1 not in picks:
                picks.append(i + 1)
                break
    imgs = []
    for n in picks:
        imgs += build_etsy.page_images(pdf, work / "sheetprev", f"p{n}", n, n, 130)
    return imgs


def zip_bundle(name: Path, paths: list[Path]) -> Path:
    with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, p.name)
    return name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", nargs="*", default=["scam-decoded", "1099-money", "dinero-simple", "money-made-simple", "1099-money-taxhacker"])
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--no-mockups", action="store_true")
    ap.add_argument("--check", action="store_true", help="recalculate the workbook in LibreOffice")
    a = ap.parse_args()
    root = Path(a.out)
    work = Path(tempfile.mkdtemp(prefix="brandshop-"))
    failures: list[str] = []
    brands = {"scam-decoded": (SD, scam_jobs), "1099-money": (T, ten99_jobs), "dinero-simple": (DS, dinero_jobs),
              "money-made-simple": (MR, mms_jobs), "1099-money-taxhacker": (SC, schedc_jobs)}
    if a.check:
        sys.path.insert(0, str(shop.ROOT / "launch" / "products"))
        from products_build import build as _PB
        recalc_check = _PB.recalc_check
    for key in a.brand:
        mod, make = brands[key]
        out = root / key
        failures += [f"{key}: {x}" for x in shop.validate(mod.LISTINGS, mod.BRAND.lang)]
        jobs, files = make(out, work)
        for r in build_etsy.run_jobs(jobs):
            if r["overflow"]:
                failures.append(f'{Path(r["out"]).name}: overflow on pages {r["overflow"]}')
        active = [it for it in mod.LISTINGS if it.get("status", "active") == "active"]
        if key == "scam-decoded" and any(it["slug"] == "scam-safety-bundle" for it in active):
            b = out / "scam-safety-bundle"
            b.mkdir(parents=True, exist_ok=True)
            files["scam-safety-bundle"] = [zip_bundle(b / "Family-Scam-Safety-Bundle.zip",
                                                      [p for s in ("family-scam-safety-kit", "scam-fridge-cards", "caller-id-script-card") for p in files[s]])]
        elif key == "dinero-simple":
            b = out / "paquete-familia"
            b.mkdir(parents=True, exist_ok=True)
            files["paquete-familia"] = [zip_bundle(b / "El-Paquete-de-la-Familia.zip",
                                                   [p for s in ("presupuesto-familiar", "registro-de-envios", "construir-credito") for p in files[s]])]
            if a.check:
                failures += recalc_check(files["registro-de-envios"][-1])
        elif key == "1099-money":
            if any(it["slug"] == "freelancer-tax-bundle-2027" for it in active):
                b = out / "freelancer-tax-bundle-2027"
                b.mkdir(parents=True, exist_ok=True)
                files["freelancer-tax-bundle-2027"] = [zip_bundle(b / "2027-Freelancer-Tax-Bundle.zip",
                                                                  files["freelancer-tax-planner-2027"] + files["freelancer-tax-sheet-2027"])]
            if a.check:
                failures += recalc_check(files["freelancer-tax-sheet-2027"][0])
        elif key == "1099-money-taxhacker" and a.check:
            failures += recalc_check(files["schedule-c-setup-pack"][0])
        for it in mod.LISTINGS:  # a retired listing leaves no upload folder behind (its pages still render and are checked)
            if it not in active and (out / it["slug"]).exists():
                shutil.rmtree(out / it["slug"])
        for it in active:
            it["files"] = [p.name for p in files[it["slug"]]]
            if not (1 <= len(it["files"]) <= 5) or any(p.stat().st_size > 20 * 1024 * 1024 for p in files[it["slug"]]):
                failures.append(f"{it['slug']}: Etsy allows 1-5 files of 20 MB each")
        if not a.no_mockups:
            with mod.BRAND.mockup_theme() as mg:
                for it in active:
                    d = out / it["slug"]
                    pdfs = [p for p in files.get(it["slug"], []) if p.suffix == ".pdf" and "A4" not in p.name]
                    if it["kind"] == "bundle":
                        parts = [s for s in files if s != it["slug"]]
                        pdfs = [p for s in parts for p in files[s] if p.suffix == ".pdf" and "A4" not in p.name and "4x6" not in p.name]
                    n_pages = 9 if it["kind"] in ("kit", "print") else 3
                    if it["kind"] == "sheet":
                        pages = sheet_preview_pages(files[it["slug"]][0], work)
                    else:
                        pages = []
                        for p in pdfs:
                            pages += build_etsy.page_images(p, work / "pg" / it["slug"], p.stem, 1, n_pages, 150)
                    hero = pages[:3] if it["kind"] not in ("bundle",) else [pages[0], pages[len(pages) // 2], pages[-1]]
                    mt, ms = MOCK[it["slug"]]
                    o = {"title": mt, "label": mod.BRAND.name, "price": it["price"], "brand": mod.BRAND.name.upper(),
                         "subtitle": ms, "chips": CHIPS.get(it["kind"], ["Instant download", "US Letter + A4"]),
                         "footer": "Educational, not advice"}
                    if mod.BRAND.lang == "es":
                        o.update(chips=ES["chips"][it["kind"]], footer=ES["footer"], text=ES["text"], steps=ES["steps"])
                    mg.generate(o, hero, d, sizes=("etsy", "gumroad", "square", "pin"), run=build_etsy.run_jobs,
                                inside_pages=pages[:10])
        for it in active:
            (out / it["slug"] / "LISTING.md").write_text(shop.listing_md(it, mod.BRAND))
        with open(out / "listings.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["slug", "title", "price", "tags", "files", "review"])
            for it in active:
                w.writerow([it["slug"], it["title"], f"{it['price']:.2f}", ", ".join(it["tags"]), " | ".join(it["files"]),
                            it.get("review", "")])
        if mod.BRAND.review:
            (out / "REVIEW_CHECKLIST_ES.md").write_text(review_checklist(mod, files))
    shutil.rmtree(work, ignore_errors=True)
    for f in failures:
        print("FAIL", f)
    print(f"built {', '.join(a.brand)} into {root}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
