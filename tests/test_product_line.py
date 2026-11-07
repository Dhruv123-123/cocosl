"""The product-line spreadsheets build, and the debt planner's payoff engine matches an independent simulation."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parents[1] / "launch" / "products"
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("product_sheets", ROOT / "sheets.py")
sheets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sheets)
CATALOG = json.loads((ROOT / "catalog.json").read_text())


@pytest.mark.parametrize("product", [p for p in CATALOG["products"] if p.get("xlsx")], ids=lambda p: p["slug"])
def test_workbook_builds(tmp_path, product):
    out = getattr(sheets, product["builder"])(tmp_path / product["xlsx"])
    wb = openpyxl.load_workbook(out)
    assert len(wb.sheetnames) >= 3
    names = set(wb.sheetnames)
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    for ref in re.findall(r"([A-Za-z][A-Za-z0-9 ]*)!", re.sub(r'"[^"]*"', "", c.value).replace("'", "")):
                        assert ref.strip() in names, f"{ws.title}!{c.coordinate} refers to missing sheet {ref}"


def test_catalog_is_consistent():
    slugs = {p["slug"] for p in CATALOG["products"]} | {e["slug"] for e in CATALOG["existing"]}
    for p in CATALOG["products"]:
        assert (ROOT / p["slug"] / "guide.html").exists()
        assert (ROOT / p["slug"] / "LISTING.md").exists()
        assert set(p.get("next", [])) <= slugs
        assert set(p.get("bundle", [])) <= slugs
    bundle = next(p for p in CATALOG["products"] if p.get("bundle"))
    prices = {p["slug"]: p["price"] for p in CATALOG["products"] + CATALOG["existing"]}
    assert bundle["price"] < sum(prices[s] for s in bundle["bundle"])


def _simulate(debts, extra, key):
    bal = [d[1] for d in debts]
    order = sorted(range(len(debts)), key=key)
    budget = sum(d[3] for d in debts) + extra
    paid, months = 0.0, 0
    while any(b > 0.005 for b in bal):
        months += 1
        owed = [b * (1 + debts[i][2] / 1200) if b > 0.005 else 0 for i, b in enumerate(bal)]
        mins = [min(o, debts[i][3]) for i, o in enumerate(owed)]
        left, extra_paid = budget - sum(mins), [0.0] * len(debts)
        for i in order:
            extra_paid[i] = max(0.0, min(owed[i] - mins[i], left))
            left -= extra_paid[i]
        for i in range(len(debts)):
            bal[i] = max(0.0, owed[i] - mins[i] - extra_paid[i])
            paid += mins[i] + extra_paid[i]
    return months, paid - sum(d[1] for d in debts)


@pytest.mark.skipif(not shutil.which("soffice"), reason="LibreOffice not installed")
@pytest.mark.parametrize("method", ["Avalanche", "Snowball"])
def test_debt_planner_matches_simulation(tmp_path, method):
    path = sheets.build_debt_planner(tmp_path / "plan.xlsx")
    wb = openpyxl.load_workbook(path)
    wb["Plan"]["C5"] = method
    wb.save(path)
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(tmp_path / "out"),
                    str(path)], capture_output=True, timeout=180, check=True)
    plan = openpyxl.load_workbook(tmp_path / "out" / "plan.xlsx", data_only=True)["Plan"]
    debts = [(plan.cell(r, 2).value, plan.cell(r, 3).value, plan.cell(r, 4).value, plan.cell(r, 5).value)
             for r in range(10, 20) if plan.cell(r, 3).value]
    key = (lambda i: (-debts[i][2], i)) if method == "Avalanche" else (lambda i: (debts[i][1], i))
    months, interest = _simulate(debts, plan["C6"].value, key)
    assert plan["C24"].value == months  # "Months until debt-free"
    assert plan["J20"].value == pytest.approx(interest, abs=0.01)
