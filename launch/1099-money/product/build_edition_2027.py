"""Make the 2027 tax-year edition of the Quarterly Tax Tracker guide from the 2026 guide.

    python launch/1099-money/product/build_edition_2027.py

Writes edition-2027/the-quarterly-tax-tracker.html and The-Quarterly-Tax-Tracker.pdf. The spreadsheet comes from
`build_tracker.py --year 2027`. 2027 figures: IRS Rev. Proc. 2026-35 (Nov 5, 2026) and the SSA 2027 wage base.
Sam's numbers are the 2027 spreadsheet's own results (recalculated in LibreOffice).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "src"))

SWAPS = [
    ("Guide + Spreadsheet &middot; 2026 tax year", "Guide + Spreadsheet &middot; 2027 tax year"),
    ("Edition 2026.1", "Edition 2027.1"),
    ("FAQ, 2026 figures and your checklist", "FAQ, 2027 figures and your checklist"),
    ("2026 federal figures (update each January)", "2027 federal figures (update each January)"),
    ('<div class="t">Jan 15</div><div class="h">Q4</div><div class="d">Covers Sep 1 &ndash; Dec 31 (paid next year)</div>',
     '<div class="t">Jan 18</div><div class="h">Q4</div><div class="d">Covers Sep 1 &ndash; Dec 31 (Jan 18, 2028: the 15th is a Saturday, the 17th MLK Day)</div>'),
    ("For payments made in 2026, a client generally only has to send you a <strong>1099-NEC</strong> once they've paid you <strong>$2,000</strong> in the year (it was $600 before).",
     "A client generally only has to send you a <strong>1099-NEC</strong> once they've paid you <strong>$2,000</strong> in the year (it was $600 before 2026; from 2027 the $2,000 rises with inflation)."),
    ("using 2026 figures.", "using 2027 figures."),
    ("Minus 2026 standard deduction (single)</td><td class=\"r\">&minus;$16,100.00", "Minus 2027 standard deduction (single)</td><td class=\"r\">&minus;$16,600.00"),
    ("$39,661.14", "$39,161.14"),
    ("&minus;$7,932.23", "&minus;$7,832.23"),
    ("$31,728.91", "$31,328.91"),
    ("10% of first $12,400 + 12% of the rest</td><td class=\"r\">$3,559.47", "10% of first $12,800 + 12% of the rest</td><td class=\"r\">$3,503.47"),
    ("$12,037.20", "$11,981.20"),
    ('<div class="big">$3,559</div>', '<div class="big">$3,503</div>'),
    ('<div class="big">&asymp;$3,009</div>', '<div class="big">&asymp;$2,995</div>'),
    ("the 2026 wage base of <strong>$184,500</strong>", "the 2027 wage base of <strong>$192,300</strong>"),
    ("2026 standard rate in Tax Tables", "standard rate in Tax Tables; update it when the IRS announces 2027's"),
    ("Q4 (Jan 15)*", "Q4 (Jan 18)*"),
    ('<td class="r">$9,716</td><td class="r">$9,435</td><td class="r">$11,434</td><td class="r">$9,747</td>',
     '<td class="r">$9,660</td><td class="r">$9,379</td><td class="r">$11,378</td><td class="r">$9,691</td>'),
    ('<td class="r">$2,186</td><td class="r">$4,246</td><td class="r">$7,718</td><td class="r">$8,772</td>',
     '<td class="r">$2,174</td><td class="r">$4,221</td><td class="r">$7,680</td><td class="r">$8,722</td>'),
    ("2026 federal figures used", "2027 federal figures used"),
    ('<td class="r">$184,500</td>', '<td class="r">$192,300</td>'),
    ("$16,100 / $32,200", "$16,600 / $33,200"),
    ("$12,400 / $24,800", "$12,800 / $25,600"),
    ("$50,400 / $100,800", "$52,025 / $104,050"),
    ("<td>Standard mileage rate</td><td class=\"r\">72.5&cent;/mile</td>", "<td>Standard mileage rate</td><td class=\"r\">72.5&cent;/mile (2026; 2027 due in Dec)</td>"),
    ("1099-NEC threshold (2026 payments)</td><td class=\"r\">$2,000", "1099-NEC threshold</td><td class=\"r\">$2,000, indexed from 2027"),
    ("Sources: IRS Rev. Proc. 2025-32,", "Sources: IRS Rev. Proc. 2026-35 (Nov 5, 2026),"),
]


def build() -> Path:
    html = (HERE / "the-quarterly-tax-tracker.html").read_text()
    for a, b in SWAPS:
        assert html.count(a) >= 1, f"not found: {a[:60]}"
        html = html.replace(a, b)
    out = HERE / "edition-2027"
    out.mkdir(exist_ok=True)
    (out / "the-quarterly-tax-tracker.html").write_text(html)
    from contentfactory.business.pdf import html_to_pdf
    pdf = out / "The-Quarterly-Tax-Tracker.pdf"
    if not html_to_pdf(out / "the-quarterly-tax-tracker.html", pdf):
        raise SystemExit("PDF print failed")
    return pdf


if __name__ == "__main__":
    print(build())
