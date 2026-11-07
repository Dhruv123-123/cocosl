"""Spanish product builds (launch/dinero-simple/products) and the month-1 content plan."""
import importlib.util
import json
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
