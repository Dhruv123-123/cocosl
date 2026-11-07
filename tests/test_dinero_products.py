"""Spanish product builds (launch/dinero-simple/products) and the month-1 content plan."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "launch" / "dinero-simple"


def _build_module():
    pytest.importorskip("openpyxl")  # optional: only the product builders need it (CI installs core deps only)
    spec = importlib.util.spec_from_file_location("ds_products_build", DS / "products" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("slug,tabs", [
    ("recorte-de-gastos", ["Resumen", "Revisión", "Registro de llamadas"]),
    ("fecha-sin-deudas", ["Plan", "Transferencia", "Consolidación", "Avance", "Calendario"]),
    ("invertir-con-100", ["Orden", "Crecimiento", "Comisiones", "Match 401k", "Roth o Traditional", "Aportaciones"]),
])
def test_spanish_workbooks_are_fully_translated(tmp_path, slug, tabs):
    build = _build_module()
    product = next(p for p in build.PRODUCTS if p["slug"] == slug)
    import openpyxl
    out = build.build_xlsx(product, tmp_path / product["xlsx"])  # raises on any untranslated label
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == tabs
    english = set(build.SHEETS) - set(build.SHEETS.values())
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    assert not any(f"{name}!" in c.value for name in english), (ws.title, c.coordinate, c.value)
    assert "Money Made Simple" not in json.dumps([[c.value for c in r] for ws in wb for r in ws.iter_rows()],
                                                 default=str)


def test_spanish_guides_have_folio_pages_and_no_english_brand():
    build = _build_module()
    for p in build.PRODUCTS:
        html = build.wrap_guide(p)
        assert '<html lang="es-US">' in html
        assert "Money Made Simple" not in html
        assert html.count('class="folio"') == html.count('<section class="page') - 1  # cover has no folio


def test_month1_plan_is_complete():
    items = json.loads((DS / "content-month-1.json").read_text())
    assert len(items) == 32
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 20 and fmts.count("carousel") == 10 and fmts.count("long") == 2
    assert len({i["key"] for i in items}) == 32
    plan = (DS / "POSTING_PLAN_MONTH_1.md").read_text()
    for i in items:
        assert i["key"] in plan or i["script"]["title"] in plan, i["key"]


def test_scam_series_is_complete_and_points_to_real_help():
    items = json.loads((DS / "content-estafas.json").read_text())
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 13 and fmts.count("carousel") == 6
    plan = (DS / "POSTING_PLAN_ESTAFAS.md").read_text()
    for i in items:
        assert i["script"]["title"] in plan, i["key"]
        assert i["script"]["claims_to_verify"], i["key"]
    text = json.dumps(items, ensure_ascii=False)
    # The immigration pieces send people to a licensed attorney or accredited representative, never a notario.
    assert "abogado con licencia" in text and "acreditado" in text


def test_month2_plan_is_complete_and_avoids_scam_series_slots():
    items = json.loads((DS / "content-month-2.json").read_text())
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 14 and fmts.count("carousel") == 8 and fmts.count("long") == 2
    assert len({i["key"] for i in items}) == len(items)
    plan = (DS / "POSTING_PLAN_MONTH_2.md").read_text()
    review = (DS / "REVIEW_CHECKLIST_MONTH_2.md").read_text()
    for i in items:
        assert i["script"]["title"] in plan and i["script"]["title"] in review, i["key"]
        assert i["script"]["claims_to_verify"], i["key"]
    scam_slots = {(r.split("|")[1].strip(), r.split("|")[2].strip())
                  for r in (DS / "POSTING_PLAN_ESTAFAS.md").read_text().splitlines() if r.startswith("| ") and "ene" in r}
    month2_slots = {(r.split("|")[1].strip(), r.split("|")[2].strip()) for r in plan.splitlines() if r.startswith("| ") and "ene" in r}
    assert month2_slots and not (scam_slots & month2_slots)
    taxes = [i for i in items if "impuesto" in json.dumps(i, ensure_ascii=False).lower() and i["key"] != "m2c-fondos-2027"]
    assert all("no es asesoría fiscal" in i["script"]["caption"] for i in taxes if "irs" in i["script"]["hashtags"])


def test_etsy_listings_fit_etsy_and_editions_stay_on_etsy():
    pytest.importorskip("openpyxl")
    sys.path.insert(0, str(DS / "etsy"))
    sys.path.insert(0, str(DS / "products"))
    import build as products
    import build_etsy
    from listings import LISTINGS
    assert {i["slug"] for i in LISTINGS} == {p["slug"] for p in products.PRODUCTS} | set(products.EXISTING)
    for it in LISTINGS:
        assert len(it["title"]) <= 140 and len(it["tags"]) == 13 and all(len(t) <= 20 for t in it["tags"]), it["slug"]
        assert "No se envía nada" in it["description"] and "IA" in it["description"]
        assert "http" not in it["description"] and "código" not in it["description"].lower()
    for p in products.PRODUCTS:
        src = build_etsy.etsy_edition(p)
        assert "<strong>RECORTE5</strong>" not in src and "FECHA5" not in src and "INVERTIR5" not in src
        assert "[el enlace de tu tienda]" not in src and "correo de compra" not in src


def test_month3_plan_is_complete_and_sends_immigration_questions_to_attorneys():
    items = json.loads((DS / "content-month-3.json").read_text())
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 14 and fmts.count("carousel") == 8 and fmts.count("long") == 2
    plan = (DS / "POSTING_PLAN_MONTH_3.md").read_text()
    review = (DS / "REVIEW_CHECKLIST_MONTH_3.md").read_text()
    for i in items:
        assert i["script"]["title"] in plan and i["script"]["title"] in review, i["key"]
        assert i["script"]["claims_to_verify"], i["key"]
    rows = lambda text: {(r.split("|")[1].strip(), r.split("|")[2].strip()) for r in text.splitlines()  # noqa: E731
                         if r.startswith("| ") and "feb" in r}
    assert rows(plan) and not (rows(plan) & rows((DS / "POSTING_PLAN_ESTAFAS.md").read_text()))
    for i in items:
        cap = i["script"]["caption"]
        if "inmigra" in cap.lower():
            assert "abogado de inmigración con licencia" in cap, i["key"]
        assert "notario" not in cap.lower() or "no con un notario" in cap.lower(), i["key"]


def test_workshop_kits_build_with_notes_and_safety_rules(tmp_path):
    pytest.importorskip("pptx")
    sys.path.insert(0, str(DS / "workshops"))
    import build_workshops
    from pptx import Presentation
    build_workshops.main(["--out", str(tmp_path), "--no-pdf"])
    for w in build_workshops.WORKSHOPS:
        prs = Presentation(tmp_path / w.SLUG / f"{w.SLUG}-diapositivas.pptx")
        assert len(prs.slides) == len(w.S) >= 12
        assert all(s.notes_slide.notes_text_frame.text.strip() for s in prs.slides)
        guide = (tmp_path / w.SLUG / f"{w.SLUG}-guia-para-facilitar.html").read_text()
        assert "hablante nativa" in guide and "no asesoría" in guide
        assert sum(int(b.split("–")[1]) - int(b.split("–")[0]) for b, _ in w.AGENDA) == w.MINUTES
        assert (tmp_path / f"{w.SLUG}.zip").exists()
        assert len(w.WORKSHEETS) == 2
    scam = build_workshops.content_estafas
    text = " ".join(str(x) for s in scam.S for x in s)
    assert "abogado con licencia" in text and "nunca se paga a una cuenta personal" in text


def test_answer_bank_has_30_linkless_answers_and_is_current():
    sys.path.insert(0, str(DS / "community"))
    import build_answers
    assert len(build_answers.A) == 30
    assert (DS / "ANSWER_BANK.md").read_text() == build_answers.build()
    for _, q, a, _ in build_answers.A:
        assert "notario" not in a.lower() or "no con un notario" in a.lower() or "un notario público solo certifica" in a.lower(), q


def test_month4_plan_is_complete_and_names_no_bank():
    items = json.loads((DS / "content-month-4.json").read_text())
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 14 and fmts.count("carousel") == 8 and fmts.count("long") == 2
    plan = (DS / "POSTING_PLAN_MONTH_4.md").read_text()
    review = (DS / "REVIEW_CHECKLIST_MONTH_4.md").read_text()
    banned = ("chase", "wells fargo", "bank of america", "citibank", "capital one", "discover", "remitly", "wise", "xoom", "self financial")
    for i in items:
        s = i["script"]
        assert s["title"] in plan and s["title"] in review and s["claims_to_verify"], i["key"]
        text = " ".join([s["caption"], s["description"]] + [g["narration"] + " " + g["on_screen_text"] for g in s["segments"]]).lower()
        assert not any(b in text for b in banned), i["key"]
    rows = [r for r in plan.splitlines() if r.startswith("| ") and " mar |" in r]
    assert len(rows) == 24 and len({(r.split("|")[1], r.split("|")[2]) for r in rows}) == 24


def test_every_dinero_long_video_has_an_original_element():
    """YouTube's inauthentic-content rule: each long video carries a chart of its own numbers (passes the
    factory's original_element check) and names a screen recording to add later."""
    sys.path.insert(0, str(ROOT / "src"))
    from contentfactory.guardrails import check_original_element
    from contentfactory.launchpack import caption_text
    from contentfactory.config import load_brand
    brand = load_brand(ROOT / "brands", "dinero-simple")
    longs = 0
    for f in ("content.json", "content-month-1.json", "content-month-2.json", "content-month-3.json", "content-month-4.json",
              "content-month-5.json", "content-month-6.json"):
        for it in json.loads((DS / f).read_text()):
            if it["format"] != "long":
                continue
            longs += 1
            s = it["script"]
            assert check_original_element({"format": "long", "script": s}).level == "ok", s["title"]
            assert s["original_element"].startswith("Graba la pantalla"), s["title"]
            for seg in s["segments"]:
                if seg.get("chart"):
                    assert any(c.startswith(f"Chart '{seg['chart']['title']}'") for c in s["claims_to_verify"])
            assert "--- ORIGINAL ELEMENT" in caption_text(brand, it)
    assert longs == 14


def test_month5_plan_is_complete_and_flags_itin_pieces_for_an_attorney():
    items = json.loads((DS / "content-month-5.json").read_text())
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 14 and fmts.count("carousel") == 8 and fmts.count("long") == 2
    plan = (DS / "POSTING_PLAN_MONTH_5.md").read_text()
    review = (DS / "REVIEW_CHECKLIST_MONTH_5.md").read_text()
    itin = 0
    for i in items:
        s = i["script"]
        assert s["title"] in plan and s["title"] in review and s["claims_to_verify"], i["key"]
        text = " ".join([s["caption"]] + [g["narration"] + " " + g["on_screen_text"] for g in s["segments"]]).lower()
        if "itin" in text:
            itin += 1
            assert s["claims_to_verify"][0].startswith("ATTORNEY REVIEW"), i["key"]
        if "inmigra" in s["caption"].lower():
            assert "abogado de inmigración con licencia" in s["caption"], i["key"]
        assert not any(b in text for b in ("remitly", "western union", "xoom", "wise ")), i["key"]
    assert itin >= 4
    rows = [r for r in plan.splitlines() if r.startswith("| ") and " abr |" in r]
    assert len(rows) == 24 and len({(r.split("|")[1], r.split("|")[2]) for r in rows}) == 24


def test_newsletter_has_six_linkless_issues_and_is_current():
    sys.path.insert(0, str(DS / "newsletter"))
    import build_newsletter
    assert len(build_newsletter.ISSUES) == 7
    assert (DS / "NEWSLETTER.md").read_text() == build_newsletter.build()
    for i in build_newsletter.ISSUES:
        build_newsletter.check(i)  # raises on a link outside a placeholder
        assert (DS / "newsletter" / "issues" / f"{i['n']:02d}-{i['slug']}.md").read_text() == build_newsletter.paste(i)
    assert "[ENLACE: darse de baja]" in build_newsletter.FOOTER and "[DIRECCIÓN POSTAL" in build_newsletter.FOOTER
    with pytest.raises(SystemExit):
        build_newsletter.check({**build_newsletter.ISSUES[0], "body": "Visita irs.gov hoy"})


def test_holiday_pack_rotates_formats_and_never_takes_a_month1_slot():
    items = json.loads((DS / "content-holiday-2026.json").read_text())
    fmts = [i["format"] for i in items]
    assert len(items) == 10 and {"short", "mid", "carousel", "image"} <= set(fmts)
    assert all(a != b for a, b in zip(fmts, fmts[1:])), "no two pieces in a row share a format"
    plan = (DS / "POSTING_PLAN_HOLIDAY_2026.md").read_text()
    slots = lambda text: {(r.split("|")[1].strip(), r.split("|")[2].strip()) for r in text.splitlines()  # noqa: E731
                          if r.startswith("| ") and (" nov |" in r or " dic |" in r)}
    assert len(slots(plan)) == 10 and not slots(plan) & slots((DS / "POSTING_PLAN_MONTH_1.md").read_text())
    for i in items:
        if i["format"] == "mid":
            words = sum(len(s["narration"].split()) for s in i["script"]["segments"])
            assert 190 <= words <= 250 and 8 <= len(i["script"]["segments"]) <= 11, i["key"]


def test_remittance_calculator_page_builds_and_is_linked(tmp_path):
    import shutil
    import subprocess
    site = tmp_path / "site"
    shutil.copytree(ROOT / "sites" / "dinero-simple", site, ignore=shutil.ignore_patterns("public"))
    subprocess.run([sys.executable, str(ROOT / "site" / "build.py")], check=True, capture_output=True,
                   env={**__import__("os").environ, "SITE_ROOT": str(site)})
    page = (site / "public" / "calculadora-de-envios" / "index.html").read_text()
    for needle in ('id="rc-amount"', 'id="rc-market"', "rc-prov-t", "A * (M - R) / M", "A * 0.01"):
        assert needle in page, needle
    assert "fetch(" not in page and "XMLHttpRequest" not in page  # no scraping, nothing leaves the browser
    assert "/calculadora-de-envios/" in (site / "public" / "links" / "index.html").read_text()


def test_newyear_pack_rotates_formats_and_never_takes_a_january_slot():
    items = json.loads((DS / "content-newyear-2027.json").read_text())
    fmts = [i["format"] for i in items]
    assert len(items) == 8 and all(a != b for a, b in zip(fmts, fmts[1:]))
    rows = lambda text: [(r.split("|")[1].strip(), r.split("|")[2].strip(), r.split("|")[3]) for r in text.splitlines()  # noqa: E731
                         if r.startswith("| ") and " ene |" in r]
    taken = rows((DS / "POSTING_PLAN_MONTH_2.md").read_text()) + rows((DS / "POSTING_PLAN_ESTAFAS.md").read_text())
    mine = rows((DS / "POSTING_PLAN_NEWYEAR_2027.md").read_text())
    assert len(mine) == 8 and not {(d, t) for d, t, _ in mine} & {(d, t) for d, t, _ in taken}
    for day in {d for d, _, _ in mine}:  # at most two posts a day on any platform
        on = [p for d, _, p in taken + mine if d == day]
        for platform in ("TikTok", "Instagram", "YouTube"):
            assert sum(platform in p for p in on) <= 2, (day, platform)
    for i in items:
        if i["format"] == "mid":
            assert 190 <= sum(len(s["narration"].split()) for s in i["script"]["segments"]) <= 250, i["key"]


def test_paycheck_calculator_uses_the_cited_2026_tables():
    import re
    page = (ROOT / "sites" / "dinero-simple" / "content" / "pages" / "calculadora-de-sueldo.md").read_text()
    js = page[page.index("// Federal tables"):page.index("var $ =")]
    # IRS Rev. Proc. 2025-32 and the SSA 2026 fact sheet
    for frag in ("single: [[12400, .10], [50400, .12], [105700, .22], [201775, .24], [256225, .32], [640600, .35]",
                 "mfj: [[24800, .10], [100800, .12], [211400, .22], [403550, .24], [512450, .32], [768700, .35]",
                 "hoh: [[17700, .10], [67450, .12], [105700, .22], [201750, .24], [256200, .32], [640600, .35]",
                 "standard: { single: 16100, mfj: 32200, hoh: 24150, mfs: 16100 }", "childCredit: 2200",
                 "ssRate: .062, ssWageBase: 184500, medicareRate: .0145, addlMedicareRate: .009, addlMedicareOver: 200000"):
        assert frag in js, frag
    assert "Rev. Proc. 2025-32" in js and "SSA" in js
    assert not re.search(r"fetch\(|XMLHttpRequest|https?://", page.split("<script>")[1].split("</script>")[0])
    # the printed table on the page matches the script
    assert "| Soltero | $16,100 | $12,400 | $50,400 | $105,700 | $201,775 | $256,225 | $640,600 |" in page


def test_month6_plan_is_complete():
    items = json.loads((DS / "content-month-6.json").read_text())
    fmts = [i["format"] for i in items]
    assert fmts.count("short") == 14 and fmts.count("carousel") == 8 and fmts.count("long") == 2
    plan = (DS / "POSTING_PLAN_MONTH_6.md").read_text()
    review = (DS / "REVIEW_CHECKLIST_MONTH_6.md").read_text()
    for i in items:
        s = i["script"]
        assert s["title"] in plan and s["title"] in review and s["claims_to_verify"], i["key"]
    rows = [r for r in plan.splitlines() if r.startswith("| ") and " may |" in r]
    assert len(rows) == 24 and len({(r.split("|")[1], r.split("|")[2]) for r in rows}) == 24


def test_whatsapp_kit_has_30_linkless_messages_and_is_current():
    sys.path.insert(0, str(DS / "whatsapp"))
    import build_whatsapp
    assert (DS / "WHATSAPP_CHANNEL.md").read_text() == build_whatsapp.build()
    assert len(build_whatsapp.M) == 30 and len(build_whatsapp.DESCRIPTION) < 500
    with pytest.raises(SystemExit):
        build_whatsapp.check(1, "consejo", "Visita irs.gov", None)
    polls = [m[3] for m in build_whatsapp.M if m[3]]
    assert polls and all(2 <= len(p[1]) <= 12 for p in polls)
