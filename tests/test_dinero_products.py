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
    for f in ("content.json", "content-month-1.json", "content-month-2.json", "content-month-3.json", "content-month-4.json"):
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
    assert longs == 10
