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
        from products_build import build as PB
        recalc_check = PB.recalc_check
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
        from products_build import build as PB
        recalc_check = PB.recalc_check
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
    assert S.es_problems(rows) == [] and len(ES.PRODUCTOS) == len(rows) == 10
    md = ES.markdown(S.BRANDS["Dinero Simple"]["sections"], S.CROSS_SELL)
    low = md.lower()
    assert low.startswith("# dinero simple") and "native review pending" in low
    assert not [w for w in BANNED_ALL if w in low] and "http" not in low
    assert md.count("**Mensaje de agradecimiento") == md.count("**Descripción:**") == 10
    assert md.count("no es asesoría financiera") >= 10 and md.count("herramientas de IA") >= 10
    assert len({p["enlace"] for p in ES.PRODUCTOS}) == 10
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


def test_bfcm_codes_and_january_push():
    sys.path.insert(0, str(SHOP.parents[0] / "catalog"))
    sys.path.insert(0, str(SHOP.parents[0] / "etsy"))
    import build_catalog as CAT
    import listings as L
    import promos
    rows = CAT.all_rows()
    assert promos.problems(rows, L.LISTINGS) == []
    assert (promos.START.isoformat(), promos.END.isoformat()) == ("2026-11-27", "2026-11-30")
    cr = {(r["code"], r["product"], r["platform"]): r["after"] for r in promos.code_rows(rows)}
    assert cr[("BF25", "Mega Budget Bundle (all 40 printables)", "Etsy")] == "$14.25"
    assert cr[("BF10", "The Money Made Simple Toolkit", "Gumroad")] == "$29"
    assert ("YEAREND10", "The Freelancer Money Bundle", "Etsy") not in cr  # guides are off Etsy
    # bundles only: every discounted product is a bundle or toolkit
    assert all(any(w in p for w in ("Bundle", "Binder", "Pack", "Toolkit", "HQ")) for _, p, _ in cr)
    md = promos.markdown(rows, L.LISTINGS).lower()
    assert "was $" not in md.replace('"was $x"', "") and "strikethrough" not in md
    assert not any(w in md for w in shop.BANNED)
    # the catalog no longer promises a percent-off "sale" on the bundles
    assert not any("on sale Nov 27-30" in r["launch"] for r in rows)


def test_january_reset_bundle_and_full_cross_sell_map():
    """Jan 1-31 Gumroad bundle of existing sheets, honest 'separately' figure; every product has an in-brand next step."""
    sys.path[:0] = [str(SHOP.parent / "catalog"), str(SHOP.parent / "storefront")]
    import build_catalog as C
    import listings as L
    import promos as P
    import build_storefront as S
    import cross_sell_map as XS
    rows = C.all_rows()
    assert P.jan_reset_problems(rows) == [] and XS.problems(rows, L.LISTINGS, S.CROSS_SELL) == []
    md = P.jan_reset_md(rows)
    assert "$33 bought separately, $24 together" in md and "February 1" in md
    assert not any(w in md.lower() for w in ("was $", "guarantee", "risk-free", "bestseller", "hurry"))
    assert "not financial advice" in md and "AI tools" in md
    m = XS.rows(rows, L.LISTINGS, S.CROSS_SELL)
    assert len(m) == len({(r["brand"], r["product"], XS._kind(r["platform"])) for r in rows if not r["platform"].startswith("On hold")})
    poster = next(r for r in m if r["product"] == "Savings Jar Poster")
    assert poster["next"] == "Spare Change Jar Tracker" and "Etsy" in poster["where"]
    assert next(r for r in m if r["product"] == "The January Reset Bundle")["next"] == "The 20-Minute Budget"


def test_etsy_ai_guide_rule_keeps_guides_off_etsy():
    """Etsy's 22 Oct 2026 ban on AI-generated functional guides: every guide is Gumroad only (or on hold)."""
    sys.path.insert(0, str(SHOP.parent / "catalog"))
    import build_catalog as C
    import etsy_rules as R
    import listings as L
    rows = C.all_rows()
    assert R.problems(rows) == []
    etsy = {(r["brand"], r["product"]) for r in rows if "Etsy" in r["platform"] and r["platform"] != R.HOLD}
    assert not (etsy & set(R.GUIDES))
    assert not any(it["kind"] == "product" for it in L.LISTINGS) and L.validate() == []
    gum = {(r["brand"], r["product"]) for r in rows if "Gumroad" in r["platform"]}
    assert ("Money Made Simple", "The 20-Minute Budget") in gum and ("Money Made Simple", "The Money Reset: 30-Day Challenge Workbook") in gum
    held = [r for r in rows if r["platform"] == R.HOLD]
    assert held == []  # PR #9 moved the seniors pack to Gumroad
    bad = R.problems(rows + [dict(rows[0], product="The Side Hustle Guide", platform="Etsy")])
    assert len(bad) == 1 and "looks like a guide" in bad[0]
    md = shop.listing_md(next(it for it in DS.LISTINGS if it["slug"] == "construir-credito"), DS.BRAND)
    assert "Gumroad only. Don't list this on Etsy." in md


def test_goal_bundles_and_launch_kit(tmp_path):
    """Goal bundles match the site's /shop/ goals; the launch kit orders every listing and shows gaps."""
    sys.path[:0] = [str(SHOP.parent / "catalog"), str(SHOP.parent / "storefront")]
    import build_catalog as C
    import launch_kit as K
    import listings as L
    goals = {it["goal"]: it for it in L.LISTINGS if it.get("goal")}
    assert set(goals) == {"debt", "first-job", "freelance"} and L.validate() == []
    for it in goals.values():
        parts = sum(L.BY_SLUG[s]["price"] for s in it["bundle"])
        assert it["price"] < parts and all(L.BY_SLUG[s]["kind"] == "printable" for s in it["bundle"])
    rows = C.all_rows()
    (tmp_path / "products/bill-cut-kit").mkdir(parents=True)
    (tmp_path / "products/bill-cut-kit/LISTING.md").write_text("# Bill Cut\n\n## Title\nThe Bill Cut Kit\n\n## Tags\n1. bills\n2. cut costs\n")
    for n in ("mockup-02-hero.png", "cover.png", "mockup-01-clean.png", "The-Bill-Cut-Kit.zip"):
        (tmp_path / "products/bill-cut-kit" / n).write_bytes(b"x")
    docs, csv_rows = K.build(tmp_path, rows)
    g = [r for r in csv_rows if r["sitting"] == "Gumroad"]
    e = [r for r in csv_rows if r["sitting"] == "Etsy"]
    names = [r["product"] for r in g]
    assert names.index("The 20-Minute Budget") < names.index("The Bill Cut Kit")  # cross-sell target goes up first
    assert len(names) == len(set(names)) and not any(r["brand"] == "Dinero Simple" for r in csv_rows)
    assert "Schedule C Setup Pack for TaxHacker" not in names and "The January Reset Bundle" not in names
    assert e[0]["product"] == "2027 Budget Planner" and e[-1]["product"] != "Monthly Budget Planner"
    first_bundle = next(i for i, r in enumerate(e) if "Bundle" in r["product"] or "Binder" in r["product"])
    assert all("Bundle" not in r["product"] for r in e[:first_bundle])
    bc = next(r for r in g if r["product"] == "The Bill Cut Kit")
    assert bc["images"] == "mockup-01-clean.png; mockup-02-hero.png; cover.png" and bc["title"] == "The Bill Cut Kit"
    assert "MISSING" in docs["LAUNCH_KIT.md"] and "BLOCKER before listing" in docs["LAUNCH_KIT.md"]


def test_tax_organizer_dates_and_listing():
    import shop
    import tax_organizer as TO
    import ten99 as T
    from datetime import date
    assert TO.LISTING in T.LISTINGS and shop.validate([TO.LISTING]) == []
    d = dict((t, d) for d, t in TO.key_dates())
    assert d["Q4 2026 estimated tax"] == date(2027, 1, 15)
    assert date(2027, 2, 1) in [x for x, _ in TO.key_dates()]          # Jan 31 2027 is a Sunday
    assert date(2027, 2, 16) in [x for x, _ in TO.key_dates()]         # Feb 15 2027 is Presidents' Day
    assert date(2027, 4, 15) in [x for x, _ in TO.key_dates()]
    assert len(TO.pages()) == 9 and "guide" not in TO.LISTING["name"].lower()
    assert "AI tools" in TO.LISTING["description"] and "not tax" in TO.LISTING["description"]


def test_launch_kit_waves():
    sys.path[:0] = [str(SHOP.parent / "catalog"), str(SHOP.parent / "storefront")]
    import build_catalog as C
    import launch_kit as K
    import tempfile
    from pathlib import Path
    docs, csv_rows = K.build(Path(tempfile.mkdtemp()), C.all_rows())
    assert {r["brand"]: r["wave"] for r in csv_rows}["1099 Money"] == 2
    w1 = docs["WAVE1_LISTINGS.md"]
    assert "1099 Money" not in w1.split("## Wave 1, but not yet")[0].split("wave 2")[1]
    assert w1.index("Week 0") < w1.index("Week 2") < w1.index("Week 4")
    g = [r["brand"] for r in csv_rows if r["sitting"] == "Gumroad"]
    assert g.index("Scam Decoded") < g.index("1099 Money")
