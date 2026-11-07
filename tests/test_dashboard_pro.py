"""Money Dashboard Pro (launch/dashboard-pro): the workbook builds in both languages, its categories match the free
tool's exactly (so the free tool's Transactions tab pastes straight in), and it only uses import-safe functions."""
import importlib.util
import re
import sys
from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "launch" / "dashboard-pro"


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load under unique names so this folder's build.py and text.py never shadow other `build` or `text` modules
# (the MMS site's build.py in tests/test_site.py). build.py does `from text import TEXT`, so `text` is lent to it
# while it loads, then sys.modules and sys.path are put back exactly as they were.
_saved_text, _saved_path = sys.modules.get("text"), list(sys.path)
try:
    _text = _load("dashboard_pro_text", "text.py")
    sys.modules["text"] = _text
    _build = _load("dashboard_pro_build", "build.py")
finally:
    if _saved_text is None:
        sys.modules.pop("text", None)
    else:
        sys.modules["text"] = _saved_text
    sys.path[:] = _saved_path
build = _build.build
TEXT = _text.TEXT

SAFE = {"IF", "IFERROR", "SUMIFS", "SUMIF", "COUNTIF", "COUNTIFS", "INDEX", "MATCH", "EDATE", "DATEDIF", "DATE", "YEAR", "MONTH",
        "TODAY", "MAX", "MIN", "SUM", "ROUND", "REPT", "OR", "AND", "COUNT", "N", "ISNUMBER"}


def free_tool_names(lang):
    js = (ROOT / "apps" / "budget" / "lib" / "dashboard.js").read_text(encoding="utf-8")
    block = js[js.index("export const CATEGORIES"):js.index("export const CAT =")]
    return set(re.findall(rf"{lang}: '([^']+)'", block))


@pytest.mark.parametrize("lang", ["en", "es"])
def test_workbook(tmp_path, lang):
    t = TEXT[lang]
    wb = openpyxl.load_workbook(build(lang, tmp_path))
    assert wb.sheetnames == [t["tabs"][k] for k in ("start", "dash", "tx", "bva", "trend", "funds", "cats")]
    cats = wb[t["tabs"]["cats"]]
    names = {cats[f"A{r}"].value for r in range(5, 5 + len(t["categories"]))}
    assert names == free_tool_names(lang)
    # Transactions columns match the free tool's download.
    tx = wb[t["tabs"]["tx"]]
    assert [tx.cell(row=4, column=c).value for c in range(1, 6)] == t["tx_head"]
    assert len(tx.data_validations.dataValidation) == 1
    # Every formula uses only functions that survive a Google Sheets import, and no TEXT() date formats.
    used = set()
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    used |= set(re.findall(r"([A-Z][A-Z0-9.]*)\(", c.value))
    assert used <= SAFE, used - SAFE
    assert len(wb[t["tabs"]["dash"]]._charts) == 3
    for k in ("bva", "trend", "funds"):
        assert len(wb[t["tabs"][k]]._charts) == 1


def test_example_data_has_one_category_over_budget():
    t = TEXT["en"]
    nov = [a for d, _, c, a in t["example_tx"] if d.month == 11 and c == "Shopping"]
    budget = next(b for n, _, b in t["categories"] if n == "Shopping")
    assert -sum(nov) > budget
