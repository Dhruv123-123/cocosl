"""The Google Sheets + Notion template line: workbooks build cleanly, Notion formulas only name real properties,
the Notion API builder makes its calls in a working order, and the store catalog is consistent."""
import math
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "launch" / "templates"
sys.path.insert(0, str(TPL))

import catalog as C  # noqa: E402
import notion_build as NB  # noqa: E402
import notion_spec as N  # noqa: E402
import sheets_templates as ST  # noqa: E402

TODAY = date(2026, 11, 7)


@pytest.mark.parametrize("slug", list(ST.SHEETS))
def test_sheet_builds_with_valid_cross_sheet_refs(tmp_path, slug):
    fn, builder = ST.SHEETS[slug]
    wb = openpyxl.load_workbook(builder(tmp_path / fn, TODAY))
    assert wb.sheetnames[0] == "Start"
    names = set(wb.sheetnames)
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    for ref in re.findall(r"([A-Za-z][A-Za-z0-9 ]*)!", re.sub(r'"[^"]*"', "", c.value).replace("'", "")):
                        assert ref.strip() in names, f"{ws.title}!{c.coordinate} -> {ref}"
    for ws in wb:
        for dv in ws.data_validations.dataValidation:
            m = re.match(r"([A-Za-z ]+)!", dv.formula1 or "")
            assert not m or m.group(1) in names


@pytest.mark.skipif(not shutil.which("soffice"), reason="LibreOffice not installed")
def test_budget_dashboard_matches_example_data(tmp_path):
    p = ST.build_budget_sheet(tmp_path / "b.xlsx", TODAY)
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(tmp_path / "rc"), str(p)],
                   capture_output=True, timeout=180, check=True)
    wb = openpyxl.load_workbook(tmp_path / "rc" / "b.xlsx", data_only=True)
    month = [t for t in ST._budget_examples(date(2026, 11, 1)) if t[0].day <= 17]
    groups = {n: g for n, g, _ in ST.BUDGET_CATS}
    want = {g: round(sum(a for _, _, c, a in month if groups[c] == g), 2) for g in ST.GROUPS}
    got = {g: round(wb["Dashboard"].cell(9 + i, 3).value, 2) for i, g in enumerate(ST.GROUPS)}
    assert got == want
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                assert not (isinstance(c.value, str) and c.value.startswith("#")), f"{ws.title}!{c.coordinate}={c.value}"


def test_notion_formulas_only_name_real_properties():
    import build_templates as B
    for slug, t in N.TEMPLATES.items():
        assert B.check_notion(t) == [], slug


def test_notion_twins_work_out_example_data():
    for t in N.TEMPLATES.values():
        rows = N.evaluate(t, TODAY)
        assert all(rows.values())
    debts = {r["Name"]: r for r in N.evaluate(N.DEBT, TODAY)["debts"]}
    # minimum-only payoff time for the example credit card matches the spreadsheet's NPER (87 months from $4,200)
    r = {"Balance now": 4200, "Monthly payment": 105, "APR %": 24.9}
    assert N._months_py(r, TODAY) == 87 == math.ceil(-math.log(1 - 4200 * 24.9 / 1200 / 105) / math.log(1 + 24.9 / 1200))
    assert debts["Store card"]["Balance now"] == round(900 - sum(p["Principal"] for p in debts["Store card"]["Payments"]), 2)
    goals = {r["Name"]: r for r in N.evaluate(N.SAVINGS, TODAY)["goals"]}
    assert goals["Car repairs"]["Saved"] == 450 + 75 + 75 - 180


@pytest.mark.parametrize("slug", list(N.TEMPLATES))
def test_notion_builder_call_order(slug):
    api = NB.DryRun()
    NB.build(api, N.TEMPLATES[slug], "0" * 32, {}, TODAY, log=lambda *_: None)
    created, relation_done, ids_seen = {}, set(), set()
    for i, (method, path, body) in enumerate(api.calls):
        if method == "POST" and path == "/databases":
            created[body["title"][0]["text"]["content"]] = i
        if method == "PATCH" and path.startswith("/databases/"):
            for name, cfg in body["properties"].items():
                if "relation" in cfg:
                    relation_done.add(path)
                if "formula" in cfg:
                    assert "prop(" in cfg["formula"]["expression"]
        if method == "POST" and path == "/pages" and "database_id" in body["parent"]:
            for v in body["properties"].values():
                for rel in v.get("relation", []):
                    assert rel["id"] in ids_seen, "row links to a row that doesn't exist yet"
        ids_seen.add(f"{i + 1:032x}")
    dbs = N.all_dbs(N.TEMPLATES[slug])
    assert set(created) == {d["title"] for d in dbs}
    rows = sum(1 for m, p, b in api.calls if m == "POST" and p == "/pages" and "database_id" in b["parent"])
    assert rows == sum(len(d["rows"]) for d in dbs)


def test_page_id_from_link():
    assert NB.page_id("https://www.notion.so/me/Templates-0123456789abcdef0123456789abcdef?pvs=4") == "0123456789abcdef0123456789abcdef"


def test_catalog():
    paid = [i for i in C.ITEMS if i["price"]]
    assert all(7 <= i["price"] <= 19 for i in paid)
    assert [i["slug"] for i in C.ITEMS if i["price"] == 0] == ["notion-money-starter"]
    for i in C.ITEMS:
        if i["kind"] in ("notion", "notion-bundle", "free"):
            assert i["slug"] in N.TEMPLATES
        if i["kind"] == "sheets":
            assert i["slug"] in ST.SHEETS
        if i.get("bundle"):
            assert i["price"] < sum(C.BY_SLUG[s]["price"] for s in i["bundle"])
        if i.get("next"):
            assert i["next"] in C.BY_SLUG
        text = " ".join([i["title"], i["tagline"], i["hook"], *i["gets"]]).lower()
        for banned in ("guarantee", "bestseller", "get rich", "limited time"):
            assert banned not in text
    assert {i["link"] for i in C.ITEMS if i.get("link")} <= set(__import__("json").loads((TPL / "links.json").read_text()))
