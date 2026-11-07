"""Build Quarterly-Tax-Tracker.xlsx for the 1099 Money brand.

    python launch/1099-money/product/build_tracker.py [out.xlsx]

Every number on the Quarterly tab is a live formula, so the file works in Excel, Google Sheets and
Numbers. The method is a simplified version of the IRS annualized installment method (Form 2210
Schedule AI): year-to-date profit is annualized at the end of each IRS period (3, 5, 8 and 12 months),
tax is estimated on that, and the required payment so far is the lesser of 22.5/45/67.5/90% of that
tax and the prior-year safe harbor. Tax tables come from YEARS (2026 default; `--year 2027` builds the 2027 edition
into edition-2027/).
Example rows are a fictional freelancer ("Sam") and match the brand's long video.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

NAVY, CREAM, CORAL, MINT = "14213D", "F7F3EA", "FF7A45", "3CC6A0"
INPUT = PatternFill("solid", fgColor="FFF2B3")
HEAD = PatternFill("solid", fgColor=NAVY)
TINT = PatternFill("solid", fgColor="EAF7F2")
CORAL_T = PatternFill("solid", fgColor="FFE6DA")
THIN = Side(style="thin", color="D9D3C3")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
H1 = Font(name="Inter", size=18, bold=True, color=NAVY)
H2 = Font(name="Inter", size=12, bold=True, color=NAVY)
WHITE_B = Font(name="Inter", bold=True, color="FFFFFF")
BODY = Font(name="Inter", size=10)
MUTED = Font(name="Inter", size=9, italic=True, color="5B6475")
BOLD = Font(name="Inter", size=10, bold=True)
USD = '"$"#,##0.00'
USD0 = '"$"#,##0'
PCT = "0.0%"
DATE = "mmm d, yyyy"
ROWS = 300  # log capacity

# Federal figures by tax year. Re-check each January; build an edition with `--year`.
YEARS = {
    2026: {  # IRS Rev. Proc. 2025-32 / OBBBA; SSA 2026 wage base
        "brackets": {
            "Single": [(0, .10), (12400, .12), (50400, .22), (105700, .24), (201775, .32), (256225, .35), (640600, .37)],
            "Married filing jointly": [(0, .10), (24800, .12), (100800, .22), (211400, .24), (403550, .32),
                                       (512450, .35), (768700, .37)],
        },
        "std": {"Single": 16100, "Married filing jointly": 32200},
        "ss_base": 184500, "mileage": 0.725, "mileage_note": "",
        "sources": "Sources: IRS Rev. Proc. 2025-32 (2026 inflation adjustments), SSA 2026 contribution and benefit base, IRS standard mileage rates.",
        "deadlines": None,  # formula dates from the Setup year
    },
    2027: {  # IRS Rev. Proc. 2026-35 (IR-2026-133, Nov 5 2026); SSA 2027 wage base $192,300
        "brackets": {
            "Single": [(0, .10), (12800, .12), (52025, .22), (109125, .24), (208325, .32), (264550, .35), (661375, .37)],
            "Married filing jointly": [(0, .10), (25600, .12), (104050, .22), (218250, .24), (416650, .32),
                                       (529100, .35), (793650, .37)],
        },
        "std": {"Single": 16600, "Married filing jointly": 33200},
        "ss_base": 192300, "mileage": 0.725,
        "mileage_note": "2026 rate: the IRS announces the 2027 rate in December. Update this cell when it does.",
        "sources": "Sources: IRS Rev. Proc. 2026-35 (2027 inflation adjustments, Nov 5 2026), SSA 2027 contribution and benefit base ($192,300), IRS standard mileage rates.",
        # Jan 31 2027 is a Sunday; Jan 15 2028 is a Saturday and Jan 17 2028 is MLK Day.
        "deadlines": [date(2027, 1, 15), date(2027, 2, 1), date(2027, 4, 15), date(2027, 6, 15), date(2027, 9, 15),
                      date(2027, 10, 15), date(2028, 1, 18)],
    },
}
YEAR = 2026
BRACKETS = YEARS[YEAR]["brackets"]
STD = YEARS[YEAR]["std"]
SS_BASE = YEARS[YEAR]["ss_base"]
MILEAGE = YEARS[YEAR]["mileage"]

CATEGORIES = ["Software & subscriptions", "Equipment", "Office supplies", "Phone & internet (business %)",
              "Advertising & marketing", "Contractors", "Professional fees", "Education (current work)",
              "Travel", "Meals (50%)", "Payment & bank fees", "Insurance (business)", "Home office (simplified)",
              "Other"]


def title(ws, text, sub):
    ws["B2"] = text
    ws["B2"].font = H1
    ws["B3"] = sub
    ws["B3"].font = MUTED
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2


def header(ws, row, cols, start=2):
    for i, c in enumerate(cols):
        cell = ws.cell(row=row, column=start + i, value=c)
        cell.fill, cell.font, cell.border = HEAD, WHITE_B, BOX
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def put(ws, ref, value, fmt=None, fill=None, font=BODY, bold=False):
    c = ws[ref]
    c.value = value
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    c.font = BOLD if bold else font
    c.border = BOX
    return c


QUARTER = 'IF({d}="","",IF(MONTH({d})<=3,1,IF(MONTH({d})<=5,2,IF(MONTH({d})<=8,3,4))))'


def build(out: Path, year: int = 2026) -> Path:
    global YEAR, BRACKETS, STD, SS_BASE, MILEAGE
    Y = YEARS[year]
    YEAR, BRACKETS, STD, SS_BASE, MILEAGE = year, Y["brackets"], Y["std"], Y["ss_base"], Y["mileage"]
    wb = Workbook()

    # ------------------------------------------------------------ Start Here
    ws = wb.active
    ws.title = "Start Here"
    title(ws, "The Quarterly Tax Tracker", f"1099 Money · for US freelancers · {YEAR} tax year edition")
    ws.column_dimensions["B"].width = 100
    lines = [
        ("How it works", H2),
        ("1. Setup tab: pick your filing status and type last year's total tax and AGI (from last year's Form 1040).", BODY),
        ("2. Log every client payment on Income, every business cost on Expenses and every business drive on Mileage.", BODY),
        ("3. Before each deadline (Apr 15, Jun 15, Sep 15, Jan 15) open Quarterly. Row 'Suggested payment' is what to pay.", BODY),
        ("4. Pay at irs.gov/payments (Direct Pay or your IRS online account), choose 'estimated tax' and the right year,", BODY),
        ("   then type what you paid in the yellow 'Actually paid' row so the next quarter accounts for it.", BODY),
        ("", BODY),
        ("Colour key", H2),
        ("Yellow cells are inputs. Everything else calculates. The example rows are a fictional freelancer (Sam): delete them.", BODY),
        ("", BODY),
        ("What the numbers are", H2),
        ("Suggested payment = the lesser of two IRS penalty-avoidance amounts, minus what you've already paid and withheld:", BODY),
        ("  (a) the annualized current-year method: 22.5% / 45% / 67.5% / 90% of tax on your year-to-date profit, annualized;", BODY),
        ("  (b) the prior-year safe harbor: 25% per quarter of 100% of last year's total tax (110% if last year's AGI > $150K).", BODY),
        ("Paying the suggested amount on time generally avoids the underpayment penalty. It is not your final bill: any balance", BODY),
        ("is due when you file in April. The Set-aside check row shows whether your tax savings will cover it.", BODY),
        ("", BODY),
        ("What it assumes (read this)", H2),
        ("Sole proprietor (Schedule C), standard deduction, no credits, taxable income below the QBI phase-in threshold.", BODY),
        ("Filing statuses: Single or Married filing jointly. Federal tax only; the state line is a flat-rate estimate you choose.", BODY),
        ("If you itemise, have big credits, capital gains, an S corp, or high income, use Form 1040-ES or a tax professional.", BODY),
        (f"Tax tables are {YEAR} figures (Tax Tables tab). Check irs.gov each January and update them.", BODY),
        ("", BODY),
        ("Educational tool only. Not tax, legal or financial advice. © 1099 Money. For personal use; please don't resell.", MUTED),
    ]
    for i, (t, f) in enumerate(lines, start=5):
        ws.cell(row=i, column=2, value=t).font = f

    # ------------------------------------------------------------ Tax Tables
    tt = wb.create_sheet("Tax Tables")
    title(tt, f"Tax Tables ({YEAR} federal)", "Update every January from irs.gov. Used by the Quarterly tab.")
    for col, w in zip("BCDEFG", (26, 16, 12, 4, 16, 12)):
        tt.column_dimensions[col].width = w
    header(tt, 5, ["Single: over", "Marginal rate", "Rate step"], 2)
    header(tt, 5, ["MFJ: over", "Marginal rate", "Rate step"], 6)
    for i, ((s_t, s_r), (m_t, m_r)) in enumerate(zip(BRACKETS["Single"], BRACKETS["Married filing jointly"])):
        r = 6 + i
        put(tt, f"B{r}", s_t, USD0, INPUT)
        put(tt, f"C{r}", s_r, "0%", INPUT)
        put(tt, f"D{r}", f"=C{r}" if i == 0 else f"=C{r}-C{r - 1}", "0%")
        put(tt, f"F{r}", m_t, USD0, INPUT)
        put(tt, f"G{r}", m_r, "0%", INPUT)
        put(tt, f"H{r}", f"=G{r}" if i == 0 else f"=G{r}-G{r - 1}", "0%")
    tt.column_dimensions["H"].width = 12
    consts = [
        ("Standard deduction: Single", STD["Single"], USD0),
        ("Standard deduction: MFJ", STD["Married filing jointly"], USD0),
        ("Social Security wage base", SS_BASE, USD0),
        ("Social Security rate (both halves)", 0.124, PCT),
        ("Medicare rate (both halves)", 0.029, PCT),
        ("Net earnings factor", 0.9235, "0.00%"),
        ("QBI deduction rate", 0.20, "0%"),
        ("Standard mileage rate ($/mile)", MILEAGE, '"$"0.000'),
        ("Safe harbor high-income AGI line", 150000, USD0),
        ("Annualization factor Q1 (3 months)", 4, "0.00"),
        ("Annualization factor Q2 (5 months)", 2.4, "0.00"),
        ("Annualization factor Q3 (8 months)", 1.5, "0.00"),
        ("Annualization factor Q4 (12 months)", 1, "0.00"),
    ]
    for i, (label, val, fmt) in enumerate(consts):
        r = 15 + i
        put(tt, f"B{r}", label)
        put(tt, f"C{r}", val, fmt, INPUT)
    # named-ish anchors used below
    T = {"std_s": "'Tax Tables'!$C$15", "std_m": "'Tax Tables'!$C$16", "ssbase": "'Tax Tables'!$C$17",
         "ss": "'Tax Tables'!$C$18", "med": "'Tax Tables'!$C$19", "nef": "'Tax Tables'!$C$20",
         "qbi": "'Tax Tables'!$C$21", "mile": "'Tax Tables'!$C$22", "hi": "'Tax Tables'!$C$23"}
    tt["B29"] = Y["sources"]
    if Y["mileage_note"]:
        put(tt, "D22", Y["mileage_note"], font=MUTED)
    tt["B29"].font = MUTED

    # ------------------------------------------------------------ Setup
    su = wb.create_sheet("Setup", 1)
    title(su, "Setup", "Five inputs. Do this once a year.")
    su.column_dimensions["B"].width = 52
    su.column_dimensions["C"].width = 26
    su.column_dimensions["D"].width = 60
    rows = [
        ("Tax year", YEAR, "0", "Must match the Tax Tables tab."),
        ("Filing status", "Single", None, "Single or Married filing jointly."),
        ("Last year's total tax (Form 1040, 'total tax' line)", 6500, USD, "For the safe harbor. Enter 0 if you didn't file / owed nothing (see guide)."),
        ("Last year's AGI (Form 1040, adjusted gross income)", 52000, USD, "Over $150,000 ($75,000 if married filing separately) → 110% safe harbor."),
        ("Expected W-2 wages this year (other job), if any", 0, USD, "Leave 0 if you only freelance."),
        ("Expected federal withholding from that job this year", 0, USD, "Counts as paid evenly through the year."),
        ("State income tax: flat estimate of your rate", 0.05, PCT, "Rough planning only. 0% if your state has no income tax."),
        ("Set-aside % you move to tax savings per payment", 0.30, PCT, "30% is a common start. The Quarterly tab tells you if it's enough."),
        ("Current balance of your tax savings account", 9000, USD, "Update before each deadline."),
    ]
    header(su, 5, ["Input", "Value", "Notes"])
    for i, (label, val, fmt, note) in enumerate(rows):
        r = 6 + i
        put(su, f"B{r}", label)
        put(su, f"C{r}", val, fmt, INPUT)
        put(su, f"D{r}", note, font=MUTED)
    dv = DataValidation(type="list", formula1='"Single,Married filing jointly"', allow_blank=False)
    su.add_data_validation(dv)
    dv.add("C7")
    put(su, "B16", "Safe harbor rate that applies to you", bold=True)
    put(su, "C16", f"=IF(C9>{T['hi']},110%,100%)", "0%")
    put(su, "B17", "Prior-year safe harbor (full year)", bold=True)
    put(su, "C17", "=C8*C16", USD)
    put(su, "B18", "Tables check", bold=True)
    put(su, "C18", f"=IF(C6={YEAR},\"OK: {YEAR} tables\",\"Update the Tax Tables tab for \"&C6)")
    S = {"status": "Setup!$C$7", "prior": "Setup!$C$17", "w2": "Setup!$C$10", "wh": "Setup!$C$11",
         "state": "Setup!$C$12", "aside": "Setup!$C$13", "bal": "Setup!$C$14"}

    # ------------------------------------------------------------ Income
    inc = wb.create_sheet("Income")
    title(inc, "Income log", "Every client or platform payment, form or no form. Quarter = IRS estimated-tax period.")
    cols = ["Date received", "Client / platform", "What for", "Invoice #", "Amount", "IRS period", "Set aside"]
    for col, w in zip("BCDEFGH", (14, 24, 30, 11, 13, 10, 13)):
        inc.column_dimensions[col].width = w
    header(inc, 5, cols)
    sam_income = [
        (date(YEAR, 1, 9), "Northwind Studio", "Brand refresh, deposit", "1001", 3250),
        (date(YEAR, 1, 30), "Northwind Studio", "Brand refresh, balance", "1002", 3250),
        (date(YEAR, 2, 13), "Juniper Bakery", "Menu + signage", "1003", 2450),
        (date(YEAR, 3, 6), "Platform payout", "Template sales", "", 550),
        (date(YEAR, 3, 27), "Atlas Outdoors", "Social templates", "1004", 4300),
        (date(YEAR, 4, 17), "Juniper Bakery", "Website graphics", "1005", 2050),
        (date(YEAR, 5, 8), "Brightline Co-op", "Annual report layout", "1006", 6200),
        (date(YEAR, 5, 29), "Platform payout", "Template sales", "", 500),
        (date(YEAR, 6, 19), "Atlas Outdoors", "Summer campaign", "1007", 7000),
        (date(YEAR, 7, 10), "Northwind Studio", "Pitch deck", "1008", 3900),
        (date(YEAR, 7, 31), "Harbor Dental", "Logo + cards", "1009", 2950),
        (date(YEAR, 8, 21), "Brightline Co-op", "Event posters", "1010", 4600),
        (date(YEAR, 9, 11), "Atlas Outdoors", "Retainer (Sep)", "1011", 4050),
        (date(YEAR, 10, 2), "Platform payout", "Template sales", "", 800),
        (date(YEAR, 10, 9), "Atlas Outdoors", "Retainer (Oct)", "1012", 4050),
        (date(YEAR, 10, 23), "Harbor Dental", "Website graphics", "1013", 3650),
    ]
    for i in range(ROWS):
        r = 6 + i
        row = sam_income[i] if i < len(sam_income) else (None,) * 5
        for col, v, fmt in zip("BCDEF", row, (DATE, None, None, None, USD)):
            put(inc, f"{col}{r}", v, fmt, INPUT)
        put(inc, f"G{r}", "=" + QUARTER.format(d=f"B{r}"), "0")
        put(inc, f"H{r}", f'=IF(F{r}="","",F{r}*{S["aside"]})', USD)
    inc.freeze_panes = "B6"
    last = 6 + ROWS - 1
    INC_AMT, INC_Q = f"Income!$F$6:$F${last}", f"Income!$G$6:$G${last}"

    # ------------------------------------------------------------ Expenses
    ex = wb.create_sheet("Expenses")
    title(ex, "Business expenses", "Business costs only. Mixed-use items: enter your business-use %. Keep every receipt.")
    for col, w in zip("BCDEFGHI", (14, 22, 28, 30, 12, 11, 13, 10)):
        ex.column_dimensions[col].width = w
    header(ex, 5, ["Date", "Vendor", "Category", "What for", "Amount", "Business %", "Deductible", "IRS period"])
    cat_dv = DataValidation(type="list", formula1="=Lists!$B$2:$B$%d" % (1 + len(CATEGORIES)), allow_blank=True)
    ex.add_data_validation(cat_dv)
    sam_exp = [
        (date(YEAR, 1, 5), "Design software", "Software & subscriptions", "Annual plan", 660, 1),
        (date(YEAR, 1, 20), "Electronics store", "Equipment", "Drawing tablet", 380, 1),
        (date(YEAR, 2, 3), "Phone carrier", "Phone & internet (business %)", "Phone, Jan-Mar", 240, 0.6),
        (date(YEAR, 3, 15), "Font foundry", "Software & subscriptions", "Font licence", 120, 1),
        (date(YEAR, 4, 2), "Accountant", "Professional fees", "Last year's return", 450, 1),
        (date(YEAR, 5, 4), "Phone carrier", "Phone & internet (business %)", "Phone, Apr-Jun", 240, 0.6),
        (date(YEAR, 5, 20), "Payment processor", "Payment & bank fees", "Card fees, Jan-May", 310, 1),
        (date(YEAR, 6, 12), "Online course", "Education (current work)", "Motion design course", 199, 1),
        (date(YEAR, 7, 8), "Print shop", "Office supplies", "Portfolio prints", 85, 1),
        (date(YEAR, 8, 3), "Phone carrier", "Phone & internet (business %)", "Phone, Jul-Sep", 240, 0.6),
        (date(YEAR, 9, 1), "Insurance co.", "Insurance (business)", "Professional liability", 420, 1),
        (date(YEAR, 10, 15), "Payment processor", "Payment & bank fees", "Card fees, Jun-Oct", 290, 1),
    ]
    for i in range(ROWS):
        r = 6 + i
        row = sam_exp[i] if i < len(sam_exp) else (None,) * 6
        for col, v, fmt in zip("BCDEFG", row, (DATE, None, None, None, USD, "0%")):
            put(ex, f"{col}{r}", v, fmt, INPUT)
        cat_dv.add(f"D{r}")
        put(ex, f"H{r}", f'=IF(F{r}="","",F{r}*IF(G{r}="",1,G{r})*IF(D{r}="Meals (50%)",0.5,1))', USD)
        put(ex, f"I{r}", "=" + QUARTER.format(d=f"B{r}"), "0")
    ex.freeze_panes = "B6"
    EX_AMT, EX_Q = f"Expenses!$H$6:$H${last}", f"Expenses!$I$6:$I${last}"

    # ------------------------------------------------------------ Mileage
    mi = wb.create_sheet("Mileage")
    title(mi, "Mileage log", "Business drives only (not your commute). Log the same day: date, where, why, miles.")
    for col, w in zip("BCDEFG", (14, 30, 30, 10, 13, 10)):
        mi.column_dimensions[col].width = w
    header(mi, 5, ["Date", "From → to", "Business purpose", "Miles", "Deduction", "IRS period"])
    sam_miles = [
        (date(YEAR, 2, 13), "Home → Juniper Bakery → home", "Menu photo shoot", 18),
        (date(YEAR, 4, 17), "Home → Juniper Bakery → home", "Website handover", 18),
        (date(YEAR, 5, 8), "Home → Brightline Co-op → home", "Kickoff meeting", 26),
        (date(YEAR, 6, 19), "Home → Atlas Outdoors → home", "Campaign shoot", 42),
        (date(YEAR, 7, 31), "Home → Harbor Dental → home", "Logo presentation", 14),
        (date(YEAR, 8, 21), "Home → print shop → Brightline → home", "Poster proofs + delivery", 31),
        (date(YEAR, 10, 9), "Home → Atlas Outdoors → home", "Retainer review", 42),
    ]
    for i in range(ROWS):
        r = 6 + i
        row = sam_miles[i] if i < len(sam_miles) else (None,) * 4
        for col, v, fmt in zip("BCDE", row, (DATE, None, None, "0.0")):
            put(mi, f"{col}{r}", v, fmt, INPUT)
        put(mi, f"F{r}", f'=IF(E{r}="","",E{r}*{T["mile"]})', USD)
        put(mi, f"G{r}", "=" + QUARTER.format(d=f"B{r}"), "0")
    mi.freeze_panes = "B6"
    MI_AMT, MI_Q = f"Mileage!$F$6:$F${last}", f"Mileage!$G$6:$G${last}"

    # ------------------------------------------------------------ Quarterly
    q = wb.create_sheet("Quarterly", 2)
    title(q, "Quarterly estimate", "Open before each deadline. Pay the 'Suggested payment' row, then type what you paid in yellow.")
    q.column_dimensions["B"].width = 50
    for col in "CDEF":
        q.column_dimensions[col].width = 17
    q.column_dimensions["G"].width = 54
    header(q, 5, ["", "Q1", "Q2", "Q3", "Q4", "What it is"])
    periods = [("Jan 1 – Mar 31", "=DATE(Setup!$C$6,4,15)", 1, 0.225),
               ("Apr 1 – May 31", "=DATE(Setup!$C$6,6,15)", 2, 0.45),
               ("Jun 1 – Aug 31", "=DATE(Setup!$C$6,9,15)", 3, 0.675),
               ("Sep 1 – Dec 31", "=DATE(Setup!$C$6+1,1,15)", 4, 0.90)]
    if Y["deadlines"]:  # exact due dates (weekends and holidays moved)
        periods = [(c, d, k, f) for (c, _, k, f), d in zip(periods, [Y["deadlines"][i] for i in (2, 3, 4, 6)])]
    labels = {}
    spec = [
        ("period", "Income covered (cumulative from Jan 1)", None, "IRS splits the year unevenly: 3, 2, 3 and 4 months."),
        ("due", "Payment due", DATE, "Weekend or holiday → next business day."),
        ("inc", "Income so far this year", USD, "From the Income tab."),
        ("exp", "Deductible expenses so far", USD, "From Expenses (business % applied)."),
        ("mil", "Mileage deduction so far", USD, "Miles × standard rate."),
        ("prof", "Profit so far", USD, "Income − expenses − mileage."),
        ("fac", "Annualization factor", "0.00", "12 ÷ months covered."),
        ("ann", "Profit, annualized (full-year pace)", USD, "Profit so far × factor."),
        ("seb", "Net earnings from self-employment", USD, "Annualized profit × 92.35%."),
        ("se", "Self-employment tax (annualized)", USD, "12.4% up to the wage base (less W-2 wages) + 2.9%."),
        ("agi", "Adjusted gross income (annualized)", USD, "Profit − half of SE tax + W-2 wages."),
        ("std", "Standard deduction", USD, "From Tax Tables, by filing status."),
        ("pre", "Taxable income before QBI", USD, ""),
        ("qbi", "QBI deduction", USD, "Lesser of 20% of (profit − half SE tax) and 20% of taxable income."),
        ("ti", "Taxable income", USD, ""),
        ("it", "Income tax", USD, f"{YEAR} brackets for your filing status."),
        ("tot", "Total federal tax for the year (at this pace)", USD, "SE tax + income tax. Your rough full-year bill."),
        ("rate", "Effective rate on profit", PCT, ""),
        ("cy", "Required so far: current-year method", USD, "22.5% / 45% / 67.5% / 90% of the line above."),
        ("sh", "Required so far: prior-year safe harbor", USD, "25% / 50% / 75% / 100% of the Setup safe harbor."),
        ("req", "Required so far (the lesser)", USD, "Paying this much on time generally avoids the penalty."),
        ("wh", "W-2 withholding credited so far", USD, "Withholding counts as paid evenly."),
        ("paid", "Estimated payments made before this one", USD, "Sum of earlier 'Actually paid' cells."),
        ("sug", "SUGGESTED PAYMENT", USD, "What to pay by the due date."),
        ("act", "Actually paid (type it in)", USD, "Yellow. Save the IRS confirmation number."),
        ("state", "State estimate for this period (rough)", USD, "Profit this period × your Setup rate. Check your state's rules."),
    ]
    for i, (key, label, fmt, note) in enumerate(spec):
        r = 6 + i
        labels[key] = r
        put(q, f"B{r}", label, bold=key in ("sug", "tot", "gap"))
        put(q, f"G{r}", note, font=MUTED)
    L = labels
    for j, (pl, due, k, cy_share) in enumerate(periods):
        c = "CDEF"[j]
        cell = lambda key: f"{c}{L[key]}"  # noqa: E731
        put(q, cell("period"), pl)
        put(q, cell("due"), due, DATE)
        put(q, cell("inc"), f'=SUMIFS({INC_AMT},{INC_Q},"<="&{k})', USD)
        put(q, cell("exp"), f'=SUMIFS({EX_AMT},{EX_Q},"<="&{k})', USD)
        put(q, cell("mil"), f'=SUMIFS({MI_AMT},{MI_Q},"<="&{k})', USD)
        put(q, cell("prof"), f"=MAX(0,{cell('inc')}-{cell('exp')}-{cell('mil')})", USD)
        put(q, cell("fac"), f"='Tax Tables'!$C${24 + j}", "0.00")
        put(q, cell("ann"), f"={cell('prof')}*{cell('fac')}", USD)
        put(q, cell("seb"), f"=IF({cell('ann')}*{T['nef']}<400,0,{cell('ann')}*{T['nef']})", USD)
        put(q, cell("se"), f"=MIN({cell('seb')},MAX(0,{T['ssbase']}-{S['w2']}))*{T['ss']}+{cell('seb')}*{T['med']}", USD)
        put(q, cell("agi"), f"={cell('ann')}-{cell('se')}/2+{S['w2']}", USD)
        put(q, cell("std"), f'=IF({S["status"]}="Single",{T["std_s"]},{T["std_m"]})', USD)
        put(q, cell("pre"), f"=MAX(0,{cell('agi')}-{cell('std')})", USD)
        put(q, cell("qbi"), f"=MIN({T['qbi']}*MAX(0,{cell('ann')}-{cell('se')}/2),{T['qbi']}*{cell('pre')})", USD)
        put(q, cell("ti"), f"=MAX(0,{cell('pre')}-{cell('qbi')})", USD)
        ti = cell("ti")
        single = f"SUMPRODUCT(({ti}>'Tax Tables'!$B$6:$B$12)*({ti}-'Tax Tables'!$B$6:$B$12)*'Tax Tables'!$D$6:$D$12)"
        mfj = f"SUMPRODUCT(({ti}>'Tax Tables'!$F$6:$F$12)*({ti}-'Tax Tables'!$F$6:$F$12)*'Tax Tables'!$H$6:$H$12)"
        put(q, cell("it"), f'=IF({S["status"]}="Single",{single},{mfj})', USD)
        put(q, cell("tot"), f"={cell('se')}+{cell('it')}", USD, CORAL_T, bold=True)
        put(q, cell("rate"), f"=IF({cell('ann')}=0,0,{cell('tot')}/{cell('ann')})", PCT)
        put(q, cell("cy"), f"={cell('tot')}*{cy_share}", USD)
        put(q, cell("sh"), f"={S['prior']}*{k}/4", USD)
        put(q, cell("req"), f"=IF({S['prior']}>0,MIN({cell('cy')},{cell('sh')}),{cell('cy')})", USD)
        put(q, cell("wh"), f"={S['wh']}*{k}/4", USD)
        prev = "0" if j == 0 else f"SUM($C${L['act']}:{'CDEF'[j - 1]}${L['act']})"
        put(q, cell("paid"), f"={prev}", USD)
        put(q, cell("sug"), f"=MAX(0,{cell('req')}-{cell('wh')}-{cell('paid')})", USD, TINT, bold=True)
        put(q, cell("act"), [1625, 1625, 1625, None][j], USD, INPUT)
        prev_prof = "0" if j == 0 else f"{'CDEF'[j - 1]}{L['prof']}"
        put(q, cell("state"), f"=MAX(0,{cell('prof')}-{prev_prof})*{S['state']}", USD)
    # Set-aside check, using the column for today's IRS period.
    top = 6 + len(spec) + 1
    act = f"$C${L['act']}:$F${L['act']}"
    pick = lambda key: f"INDEX($C${L[key]}:$F${L[key]},$C${top})"  # noqa: E731
    summary = [
        ("Current IRS period (from today's date)",
         "=IF(YEAR(TODAY())>Setup!$C$6,4,IF(YEAR(TODAY())<Setup!$C$6,1," + QUARTER.format(d="TODAY()") + "))", "0",
         "1-4. Uses the column for the period you're in now."),
        ("Full-year federal bill at your current pace", "=" + pick("tot"), USD, ""),
        ("Federal already paid (estimates + withholding so far)", f"=SUM({act})+{pick('wh')}", USD, ""),
        ("State bill at your current pace (rough)", f"={pick('ann')}*{S['state']}", USD, "Before any state estimates you've paid."),
        ("Still to pay this year (federal + state)", f"=MAX(0,C{top + 1}-C{top + 2})+C{top + 3}", USD, ""),
        ("Your tax savings balance (Setup)", f"={S['bal']}", USD, ""),
        ("SET-ASIDE CHECK", f"=C{top + 5}-C{top + 4}", USD,
         "Positive: your savings cover the rest of the year. Negative: raise your set-aside %."),
    ]
    for i, (label, formula, fmt, note) in enumerate(summary):
        r = top + i
        put(q, f"B{r}", label, bold=i == len(summary) - 1)
        put(q, f"C{r}", formula, fmt, TINT if i == len(summary) - 1 else None, bold=i == len(summary) - 1)
        put(q, f"G{r}", note, font=MUTED)
    gap = f"C{top + len(summary) - 1}"
    q.conditional_formatting.add(gap, FormulaRule(formula=[f"{gap}<0"], fill=CORAL_T,
                                                  font=Font(color="9A2B00", bold=True)))
    q.freeze_panes = "C6"
    note_r = top + len(summary) + 1
    q[f"B{note_r}"] = ("Simplified annualized installment method (Form 2210 Schedule AI). Assumes Schedule C, standard deduction, "
                       "no credits, income below the QBI threshold. Educational only, not tax advice.")
    q[f"B{note_r}"].font = MUTED

    # ------------------------------------------------------------ Deadlines
    dl = wb.create_sheet("Deadlines")
    title(dl, "Deadlines", "Add each one to your calendar with a reminder a week early.")
    dl.column_dimensions["B"].width = 18
    dl.column_dimensions["C"].width = 70
    header(dl, 5, ["Date", "What's due"])
    items = [
        ("=DATE(Setup!$C$6,1,15)", "Q4 estimated payment for LAST year's income"),
        ("=DATE(Setup!$C$6,1,31)", "Clients and platforms send your 1099-NEC / 1099-K. Match them to the Income tab."),
        ("=DATE(Setup!$C$6,4,15)", "File last year's return + pay any balance. Q1 estimate for this year."),
        ("=DATE(Setup!$C$6,6,15)", "Q2 estimated payment"),
        ("=DATE(Setup!$C$6,9,15)", "Q3 estimated payment"),
        ("=DATE(Setup!$C$6,10,15)", "Extended filing deadline (if you filed an extension; it extends filing, not paying)"),
        ("=DATE(Setup!$C$6+1,1,15)", "Q4 estimated payment for THIS year"),
    ]
    if Y["deadlines"]:  # exact dates, moved for weekends and holidays
        items = [(d, what) for d, (_, what) in zip(Y["deadlines"], items)]
    for i, (d, what) in enumerate(items):
        put(dl, f"B{6 + i}", d, DATE)
        put(dl, f"C{6 + i}", what)

    # ------------------------------------------------------------ Lists (hidden helper)
    li = wb.create_sheet("Lists")
    li["B1"] = "Expense categories"
    for i, cat in enumerate(CATEGORIES, start=2):
        li[f"B{i}"] = cat
    li.sheet_state = "hidden"

    wb.move_sheet("Tax Tables", offset=10)
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = {"Start Here": CORAL, "Setup": CORAL, "Quarterly": MINT}.get(ws.title, NAVY)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    year = 2026
    if "--year" in args:
        k = args.index("--year")
        year = int(args[k + 1])
        del args[k:k + 2]
    here = Path(__file__).parent
    default = here / "Quarterly-Tax-Tracker.xlsx" if year == 2026 else here / f"edition-{year}" / "Quarterly-Tax-Tracker.xlsx"
    dest = Path(args[0]) if args else default
    print(build(dest, year))
