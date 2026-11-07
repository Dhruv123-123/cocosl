"""The Etsy compliance audit and the start-here page (launch/catalog)."""
import sys
from pathlib import Path

CAT = Path(__file__).resolve().parents[1] / "launch" / "catalog"
sys.path[:0] = [str(CAT), str(CAT.parent / "storefront")]

import etsy_audit as A  # noqa: E402
import start_here as S  # noqa: E402

SAMPLE = """# Thing

## Etsy

### Title
Budget Planner Printable, Monthly Budget Sheet

### Tags
1. budget planner
2. monthly budget

### Description
A digital download: nothing is shipped. Drafted with AI help and fact-checked by a person. Not financial advice.
"""


def _row(tmp_path, md):
    d = tmp_path / "x"
    d.mkdir()
    (d / "LISTING.md").write_text(md)
    return dict(brand="B", product="P", platform="Etsy", listing="x/LISTING.md", files="x/")


def test_audit_passes_clean_listing(tmp_path):
    e = A.etsy_part(SAMPLE)
    assert e["title"].startswith("Budget Planner") and e["tags"] == ["budget planner", "monthly budget"]
    assert A.check_row(_row(tmp_path, SAMPLE), tmp_path) == []


def test_audit_flags_off_etsy_and_banned(tmp_path):
    md = SAMPLE.replace("Not financial advice.", "Not financial advice. Guaranteed results, more on Gumroad with BUDGET5.")
    probs = " ".join(A.check_row(_row(tmp_path, md), tmp_path))
    assert "off-Etsy" in probs and "banned" in probs and "BUDGET5" in probs


def test_audit_flags_missing_disclosures(tmp_path):
    md = SAMPLE.replace("A digital download: nothing is shipped. Drafted with AI help and fact-checked by a person. Not financial advice.", "Nice planner.")
    probs = " ".join(A.check_row(_row(tmp_path, md), tmp_path))
    assert "digital download" in probs and "AI" in probs and "financial advice" in probs


def test_start_here_scan_finds_link_blanks():
    found = S.scan(CAT.parent)
    assert any("links.json" in f for v in found.values() for f in v)
    assert not any("PRODUCTS_START_HERE.md" in f for v in found.values() for f in v)
    assert len(S.TOP5) == 5
