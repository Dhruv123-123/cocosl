"""Scam Decoded and 1099 Money shop products: listings, pages, tax dates, scam contacts and the tracker workbook."""
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

SHOP = Path(__file__).resolve().parents[1] / "launch" / "brandshop"
sys.path.insert(0, str(SHOP))

import scam_decoded as SD  # noqa: E402
import shop  # noqa: E402
import ten99 as T  # noqa: E402
import ten99_sheet  # noqa: E402
import dinero_simple as DS  # noqa: E402
import remesas_sheet  # noqa: E402


@pytest.mark.parametrize("mod", [SD, T, DS], ids=["scam-decoded", "1099-money", "dinero-simple"])
def test_listings_pass_etsy_and_copy_rules(mod):
    assert shop.validate(mod.LISTINGS, mod.BRAND.lang) == []
    assert len({it["slug"] for it in mod.LISTINGS}) == len(mod.LISTINGS)
    for it in mod.LISTINGS:
        md = shop.listing_md(it, mod.BRAND)
        assert "Nothing here has been listed" in md and "IA" in it["description"] if mod is DS else "AI" in it["description"]


def test_brand_banned_phrases_absent_everywhere():
    scam = ("you've been hacked", "100% safe", "never get scammed again", "guaranteed protection", "hackers hate")
    money = ("write off everything", "tax-free money", "the irs won't know", "guaranteed refund", "this one trick")
    for mod, words in ((SD, scam), (T, money)):
        pages = SD.kit_pages() + SD.fridge_cards() + [SD.caller_id_large(), SD.caller_id_card()] if mod is SD else T.planner_pages()
        text = " ".join(pages + [it["description"] + it["gumroad"] for it in mod.LISTINGS]).lower()
        assert [w for w in words + ("guarantee", "risk-free") if w in text] == []


def test_page_counts():
    assert len(SD.kit_pages()) == 11
    assert len(SD.fridge_cards()) == 6
    assert len(T.planner_pages()) == 25
    assert "25 pages" in " ".join(T.PRINT_GET)


def test_2027_tax_dates():
    q = T.estimated_due(2027)
    assert [r[2] for r in q] == [date(2027, 4, 15), date(2027, 6, 15), date(2027, 9, 15), date(2028, 1, 18)]
    assert date(2027, 2, 1) in [d for d, _ in T.key_dates()]  # Jan 31 2027 is a Sunday
    assert date(2027, 10, 15) in [d for d, _ in T.key_dates()]
    assert all(d.weekday() < 5 for d, _ in T.key_dates())


def test_scam_contacts_are_the_official_ones():
    text = " ".join(SD.kit_pages())
    for s in ("ReportFraud.ftc.gov", "ic3.gov", "IdentityTheft.gov", "1-833-FRAUD-11", "1-833-372-8311", "877-908-3360"):
        assert s in text, s


def test_workbook_formulas(tmp_path):
    import openpyxl
    path = ten99_sheet.build(tmp_path / "t.xlsx")
    wb = openpyxl.load_workbook(path)
    assert {"Start", "Setup", "Income", "Expenses", "Mileage", "Months", "Quarters", "Categories", "Clients"} <= set(wb.sheetnames)
    formulas = [c.value for ws in wb for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
    assert any("SUMIFS" in f for f in formulas)
    if shutil.which("soffice"):
        sys.path.insert(0, str(SHOP.parents[0] / "products"))
        from build import recalc_check
        assert recalc_check(path) == []


def test_dinero_simple_is_spanish_and_flagged_for_review():
    pages = DS.presupuesto_pages() + DS.remesas_pages() + DS.credito_pages()
    assert [len(DS.presupuesto_pages()), len(DS.remesas_pages()), len(DS.credito_pages())] == [12, 7, 8]
    text = " ".join(pages).lower()
    banned = ("garantizad", "sin riesgo", "dinero fácil", "este truco", "rendimientos garantizados", "libertad financiera de la noche")
    assert [w for w in banned if w in text] == []
    for it in DS.LISTINGS:
        assert it["review"] == "pending native review"
        md = shop.listing_md(it, DS.BRAND)
        assert "NATIVE REVIEW PENDING" in md and "QUÉ INCLUYE" in it["description"]
    assert DS.BRAND.lang == "es" and 'lang="es"' in DS.BRAND.html(["x"], "t", "8.5in", "11in", "Letter")
    # the facts the pages rely on
    for s in ("30 minutos", "180 días", "consumerfinance.gov", "AnnualCreditReport.com", "1%"):
        assert s.lower() in text, s


def test_remittance_workbook(tmp_path):
    import openpyxl
    path = remesas_sheet.build(tmp_path / "r.xlsx")
    wb = openpyxl.load_workbook(path)
    assert {"Empieza", "Comparar", "Envíos", "Meses", "Servicios"} == set(wb.sheetnames)
    assert wb["Envíos"]["G5"].value.startswith("=") and "'Envíos'!" in wb["Meses"]["C5"].value
    if shutil.which("soffice"):
        sys.path.insert(0, str(SHOP.parents[0] / "products"))
        from build import recalc_check
        assert recalc_check(path) == []


def test_products_catalog_covers_every_brand():
    sys.path.insert(0, str(SHOP.parents[0] / "catalog"))
    import build_catalog as C
    rows = C.all_rows()
    brands = {r["brand"] for r in rows}
    assert {"Money Made Simple", "Scam Decoded", "1099 Money", "Dinero Simple"} <= brands
    assert all(r[k] for r in rows for k in ("product", "platform", "price", "files", "listing", "launch", "date_source"))
    assert {r["date_source"] for r in rows} <= {"calendar", "proposed"}
    assert all("NATIVE REVIEW" in r["notes"] for r in rows if r["brand"] == "Dinero Simple")
    names = {r["product"] for r in rows}
    for mod in (SD, T, DS):
        active = {it["name"] for it in mod.LISTINGS if it["status"] == "active"} if hasattr(mod, "RETIRED") else \
            {it["name"] for it in mod.LISTINGS}
        assert active <= names
    # no near-duplicates: every retired product says where it went, and none of them is listed
    merged = C.merged_rows()
    assert {m["product"] for m in merged} == {it["name"] for mod in (SD, T) for it in mod.LISTINGS if it["slug"] in mod.RETIRED}
    assert all(m["why"] and "RETIRED" in m["undo"] for m in merged)
    assert not ({m["product"] for m in merged} & names)
    assert "The 20-Minute Budget" in names


def test_scam_card_set_replaces_the_overlaps():
    cs = next(it for it in SD.LISTINGS if it["slug"] == "scam-card-set")
    assert cs["status"] == "active" and cs["price"] == 6
    assert set(SD.RETIRED) == {"family-scam-safety-kit", "scam-fridge-cards", "caller-id-script-card", "scam-safety-bundle"}
    assert set(T.RETIRED) == {"freelancer-tax-sheet-2027", "freelancer-tax-bundle-2027"}


def test_gumroad_storefront_kit():
    sys.path.insert(0, str(SHOP.parents[0] / "storefront"))
    import build_storefront as S
    assert S.problems() == []
    prods = S.gumroad_products()
    assert set(prods) == set(S.BRANDS)
    for brand, rows in prods.items():
        b = S.BRANDS[brand]
        assert len(b["bio"]) <= 160 and ("not" in b["bio"].lower() or "no es" in b["bio"].lower())
        md = S.storefront_md(brand, rows)
        assert "Nothing here has been set up" in md
        assert ("NATIVE REVIEW PENDING" in md) == (brand == "Dinero Simple")
    assert "CROSS_SELL" not in S.cross_sell_md(prods) and all(r["product"] in S.cross_sell_md(prods) for rs in prods.values() for r in rs)


BANNED_ALL = ["guarantee", "risk-free", "i've used", "bestseller", "best seller", "libertad financiera de la noche a la mañana",
              "este truco", "rendimientos garantizados", "dinero fácil", "garantizad", "sin riesgo", "100% seguro", "hazte rico"]


def test_spanish_gumroad_storefront():
    sys.path.insert(0, str(SHOP.parents[0] / "storefront"))
    import build_storefront as S
    import gumroad_es as ES
    rows = S.gumroad_products()["Dinero Simple"]
    assert S.es_problems(rows) == [] and len(ES.PRODUCTOS) == len(rows) == 9
    md = ES.markdown(S.BRANDS["Dinero Simple"]["sections"], S.CROSS_SELL)
    low = md.lower()
    assert low.startswith("# dinero simple") and "native review pending" in low
    assert not [w for w in BANNED_ALL if w in low] and "http" not in low
    assert md.count("**Mensaje de agradecimiento") == md.count("**Descripción:**") == 9
    assert md.count("no es asesoría financiera") >= 10 and md.count("herramientas de IA") >= 10
    assert len({p["enlace"] for p in ES.PRODUCTOS}) == 9
    for p in ES.PRODUCTOS:
        assert len(p["resumen"]) <= 230 and 5 <= len(p["etiquetas"]) <= 10
    # bundle maths in the copy add up
    assert 5 + 12 + 17 + 19 == 53 and "$53" in md and 9 + 7 + 6 == 22 and "$22" in md


def test_post_purchase_emails(tmp_path):
    sys.path.insert(0, str(SHOP.parents[0] / "storefront"))
    import build_storefront as S
    import post_purchase as PP
    assert S.email_problems() == []
    assert set(PP.SEQUENCES) | set(PP.ELSEWHERE) == set(S.BRANDS)
    for brand, seq in PP.SEQUENCES.items():
        for i, e in enumerate(seq["emails"], 1):
            md = PP.email_md(brand, i, e)
            low = md.lower()
            assert md.startswith("---\norder:") and not [w for w in BANNED_ALL if w in low]
            assert "not financial advice" in low or "not legal or financial advice" in low or "no es asesoría" in low
            assert ("NATIVE REVIEW PENDING" in md) == (brand == "Dinero Simple")
            assert "\n> NATIVE" not in md or "revise. No se envían antes de eso.\n\nHola" in md
        assert "{{download_url}}" in seq["emails"][0]["body"]
        assert seq["code"] not in seq["emails"][0]["body"] + seq["emails"][1]["body"]  # days 0 and 3: no pitch
    idx = PP.index_md()
    assert "SEMANA5" in idx and "TRACKER15" in idx and "Nothing is sent" in idx


def test_money_reset_workbook():
    import money_reset as MR
    assert shop.validate(MR.LISTINGS) == []
    assert [d[0] for d in MR.DAYS] == list(range(1, 31))
    assert len(MR.pages()) == 21 and "21 printable pages" in MR.GET[0]
    it = MR.LISTINGS[0]
    assert it["price"] == 9 and "[LINK:" in it["gumroad"] and "http" not in it["gumroad"]
    worksheets = {d[4] for d in MR.DAYS if d[4]}
    titles = " ".join(MR.pages()).replace("<em>", "").replace("</em>", "")
    assert all(w.split()[0] in titles for w in worksheets)


def test_schedule_c_pack_matches_taxhacker_and_irs_lines(tmp_path):
    import schedule_c_pack as SC
    assert shop.validate(SC.LISTINGS) == []
    it = SC.LISTINGS[0]
    assert it["price"] == 12 and it["review"].startswith("BLOCKER") and "[LINK:" in it["gumroad"]
    assert "isn't affiliated" in it["gumroad"] and "Vasily Zubarev" in it["gumroad"]
    # TaxHacker builds a category's code from its first 16 slug characters: they must not collide
    codes = [SC.code_of(n) for n, *_ in SC.CATEGORIES]
    assert len(set(codes)) == len(codes) and all(len(c) <= 16 for c in codes)
    assert SC.code_of("Business %") == "business_percent" and SC.code_of("Software and subscriptions") == "software_and_sub"
    assert all(line in SC.LINES or line in SC.OTHER for _, line, *_ in SC.CATEGORIES)
    assert f"{len(SC.CATEGORIES)} Schedule C categories" in SC.GET[0] and f"{len(SC.pages())}-page" in SC.GET[0]
    assert set(SC.REQUIRED) <= set(SC.EXPORT_COLUMNS)
    csv_path, json_path = SC.write_mapping(tmp_path)
    text = json_path.read_text()
    assert "don't restore" in text and "TaxHacker 0.8.5" in text
    # the pack ships our own files only: no TaxHacker source
    assert not any(p.suffix in (".ts", ".tsx", ".prisma") for p in tmp_path.iterdir())


@pytest.mark.skipif(not shutil.which("soffice"), reason="LibreOffice not installed")
def test_year_end_packet_reads_taxhacker_csv(tmp_path):
    import subprocess
    from openpyxl import load_workbook
    import schedule_c_pack as SC
    src = SC.build_workbook(tmp_path / "p.xlsx")
    out = tmp_path / "out"
    subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", str(out), str(src)],
                   capture_output=True, timeout=300, check=True)
    wb = load_workbook(out / "p.xlsx", data_only=True)
    by = {r[0]: r[2] for r in wb["By line"].iter_rows(min_row=5, max_row=30, values_only=True) if r[0]}
    # 2026 examples only (the Dec 2025 receipt is left out); the phone bill counts at its 50% business share
    assert by["Line 1"] == 4200 and by["Line 13"] == 1299 and by["Line 25"] == 40 and by["Line 24b"] == pytest.approx(62.4)
    assert by["Not Schedule C"] == 1200 and by["Personal"] == 95 and by["Unmapped"] == 0 and by["Line 22"] == 0
    q = [r for r in wb["Quarters"].iter_rows(min_row=5, max_row=8, max_col=7, values_only=True)]
    assert [r[4] for r in q] == [1354, pytest.approx(182.4), 0, 358]
    assert q[0][2].date() == date(2026, 4, 15) and q[3][2].date() == date(2027, 1, 15)
    assert q[0][6] == pytest.approx(446 * 0.25) and q[1][6] == 0
    mn = wb["Missing notes"]
    assert mn["G1"].value == 2 and mn["C5"].value == "Computer store" and mn["C6"].value == "Coworking space"
    assert all(r[2] == "found" for r in wb["Settings"].iter_rows(min_row=10, max_row=19, max_col=3, values_only=True))
