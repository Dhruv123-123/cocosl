"""Build Debt-Payoff-Planner.xlsx with openpyxl.

Run:  python3 build_planner_xlsx.py [out.xlsx]
All math lives in formulas; nothing is pre-computed in Python.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import AreaChart, LineChart, Reference
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

from debtsim import EXAMPLE, EXAMPLE_EXTRA

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parents[1] / "debt-payoff-planner" / "Debt-Payoff-Planner.xlsx")

ND = 8            # debt rows
MONTHS = 360      # 30 years
FIRST = 13        # first debt row on My Debts
LAST = FIRST + ND - 1
TOTAL_ROW = LAST + 1

INK, CREAM, GREEN, GOLD = "0B1D13", "F4F1E8", "2FBF71", "F2B134"
MUTED, LINE = "4B5A51", "D9D3C3"
INPUT, TINT, OUTFILL, GREY = "FFF4CC", "EAF6EF", "D5F2E1", "F2F2F2"

F = "Arial"
thin = Side(style="thin", color="C9C2B0")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
MONEY = '"$"#,##0.00'
MONEY0 = '"$"#,##0'
PCT = '0.00'
MONTHFMT = 'mmm yyyy'


def font(size=10, bold=False, color=None, italic=False):
    return Font(name=F, size=size, bold=bold, color=color, italic=italic)


def fill(rgb):
    return PatternFill("solid", fgColor=rgb)


def title(ws, text, sub=None, note=None, col="B"):
    ws[f"{col}1"] = text
    ws[f"{col}1"].font = font(18, True, INK)
    if sub:
        ws[f"{col}2"] = sub
        ws[f"{col}2"].font = font(10, False, MUTED)
    if note:
        ws[f"{col}3"] = note
        ws[f"{col}3"].font = font(9, False, MUTED)
    ws.sheet_view.showGridLines = False


def header(ws, row, col, text, width_cols=1):
    c = ws.cell(row=row, column=col, value=text)
    c.font = font(10, True, CREAM)
    c.fill = fill(INK)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    c.border = BOX
    if width_cols > 1:
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + width_cols - 1)
    return c


def cell(ws, ref, value=None, fmt=None, bold=False, bg=None, color=None, align=None, size=10, border=True,
         italic=False, wrap=False):
    c = ws[ref]
    if value is not None:
        c.value = value
    c.font = font(size, bold, color, italic)
    if fmt:
        c.number_format = fmt
    if bg:
        c.fill = fill(bg)
    if border:
        c.border = BOX
    if align or wrap:
        c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    return c


def note(ws, ref, text, size=9):
    ws[ref] = text
    ws[ref].font = font(size, False, MUTED)


wb = Workbook()

# ====================================================================== Start Here
ws0 = wb.active
ws0.title = "Start Here"
ws0.sheet_properties.tabColor = INK
title(ws0, "Debt Payoff Planner", "Money Made Simple · see exactly when you'll be debt-free, three ways.",
      "Educational tool, not financial advice. Example data is fictional: replace it with your own.")
ws0.column_dimensions["A"].width = 2
ws0.column_dimensions["B"].width = 4
ws0.column_dimensions["C"].width = 100
steps = [
    ("1", "Go to the My Debts tab. Replace the yellow example rows with your debts: name, balance, APR and "
          "minimum payment. Up to 8 debts. Leave unused rows blank."),
    ("2", "Enter the extra amount you can pay each month on top of all your minimums (C7). Even $25 counts. "
          "Optional: a one-time extra payment (a tax refund, a bonus) and the month it arrives."),
    ("3", "Pick a plan in C6: Avalanche (highest APR first), Snowball (smallest balance first) or Custom "
          "(your own order, typed in the Custom order column)."),
    ("4", "Read your results: payoff month for each debt, your debt-free date and total interest. The Compare "
          "tab shows all three plans side by side, plus what happens if you only pay minimums."),
    ("5", "Payoff Plan is your month-by-month schedule: what to pay on each debt, every month. Print it or "
          "check off one row each payday."),
    ("6", "Loan Amortization is a separate calculator for one fixed-payment loan (car, student, personal): "
          "see the interest in each payment and what an extra payment saves."),
]
r = 5
header(ws0, r, 2, "#")
header(ws0, r, 3, "How to use it (about 15 minutes)")
for n, text in steps:
    r += 1
    cell(ws0, f"B{r}", n, bold=True, align="center")
    cell(ws0, f"C{r}", text, wrap=True)
    ws0.row_dimensions[r].height = 30
r += 2
header(ws0, r, 2, "")
header(ws0, r, 3, "Color key")
r += 1
cell(ws0, f"B{r}", "", bg=INPUT)
cell(ws0, f"C{r}", "Yellow = your inputs. Type over these.")
r += 1
cell(ws0, f"B{r}", "", bg="FFFFFF")
cell(ws0, f"C{r}", "White = calculated. Leave these alone (they are formulas).")
r += 1
cell(ws0, f"B{r}", "", bg=OUTFILL)
cell(ws0, f"C{r}", "Green = key results.")
r += 1
cell(ws0, f"B{r}", "", bg=GREY)
cell(ws0, f"C{r}", "Grey tabs (Calc ·, Chart Data) = the engine. No inputs there; don't edit.")
r += 2
header(ws0, r, 2, "")
header(ws0, r, 3, "Good to know")
notes = [
    "Where to find your numbers: your latest statement or the lender's app shows the balance, APR (not the "
    "'monthly rate') and the minimum payment due.",
    "The model: each month, interest = balance × APR ÷ 12; every debt gets its minimum; everything left over "
    "goes to your target debt. When a debt is paid off, its minimum rolls into the next one.",
    "It's an estimate. Lenders usually charge interest daily, minimums on cards shrink as balances fall, and "
    "rates can change. Expect your real payoff to land within a month or two of what you see here.",
    "If a minimum is smaller than the monthly interest, the balance grows. The planner flags this in red.",
    "Works in Excel, Google Sheets (File > Import > Upload) and Apple Numbers. If a number looks stuck, "
    "make sure calculation is set to automatic.",
    "Struggling to make minimums at all? A non-profit credit counselor (in the US, an NFCC member agency) "
    "is a sensible, low-cost next step before any debt-relief company.",
]
for t in notes:
    r += 1
    cell(ws0, f"B{r}", "•", align="center")
    cell(ws0, f"C{r}", t, wrap=True)
    ws0.row_dimensions[r].height = 30
r += 2
note(ws0, f"C{r}", "Personal use only. Please don't resell or share the file. Educational content, not financial "
                    "advice. © Money Made Simple.")

# ====================================================================== My Debts
ws = wb.create_sheet("My Debts")
ws.sheet_properties.tabColor = GREEN
title(ws, "My Debts", "Enter your debts in the yellow cells. Everything else calculates.",
      "Example data is fictional. Delete it (select the yellow cells, press Delete) and type your own.")
widths = {"A": 2, "B": 33, "C": 15, "D": 10, "E": 14, "F": 11, "G": 14, "H": 11, "I": 11, "J": 11, "K": 11,
          "L": 13, "M": 13, "N": 15, "O": 34, "P": 3, "Q": 12, "R": 12}
for k, v in widths.items():
    ws.column_dimensions[k].width = v

header(ws, 5, 2, "Settings", 1)
header(ws, 5, 3, "")
cell(ws, "B6", "Plan to use", bold=True)
cell(ws, "C6", "Avalanche", bg=INPUT, bold=True, align="center")
dv = DataValidation(type="list", formula1='"Avalanche,Snowball,Custom"', allow_blank=False,
                    showErrorMessage=True, errorTitle="Pick a plan", error="Choose Avalanche, Snowball or Custom.")
ws.add_data_validation(dv)
dv.add("C6")
note(ws, "D6", "Avalanche = highest APR first · Snowball = smallest balance first · Custom = your order (column F)")
cell(ws, "B7", "Extra payment per month", bold=True)
cell(ws, "C7", EXAMPLE_EXTRA, MONEY, bg=INPUT)
note(ws, "D7", "On top of all minimums. This is the money that speeds everything up.")
cell(ws, "B8", "First payment month", bold=True)
cell(ws, "C8", date(2026, 12, 1), MONTHFMT, bg=INPUT)
note(ws, "D8", "Any date in the month you'll make the first payment.")
cell(ws, "B9", "One-time extra payment", bold=True)
cell(ws, "C9", 0, MONEY, bg=INPUT)
note(ws, "D9", "Optional: a tax refund or bonus you'll put toward debt.")
cell(ws, "B10", "…in month #", bold=True)
cell(ws, "C10", 4, "0", bg=INPUT)
note(ws, "D10", "1 = the first payment month. Leave the amount at 0 to ignore.")
dv2 = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", showErrorMessage=True,
                     error="Use 0 or a positive amount.")
ws.add_data_validation(dv2)
dv2.add("C7")
dv2.add("C9")
dv3 = DataValidation(type="whole", operator="between", formula1="1", formula2=str(MONTHS), showErrorMessage=True,
                     error=f"Enter a month number from 1 to {MONTHS}.")
ws.add_data_validation(dv3)
dv3.add("C10")

# helper: plan index
cell(ws, "Q5", "helper", size=8, color=MUTED, border=False)
cell(ws, "Q6", '=IFERROR(MATCH(C6,{"Avalanche","Snowball","Custom"},0),1)', "0", size=8, color=MUTED, border=False)

heads = ["Debt", "Balance", "APR %", "Minimum / mo", "Custom order", "Interest / mo now",
         "Avalanche #", "Snowball #", "Custom #", "Your plan #", "Paid off (month #)", "Paid off (date)",
         "Interest you'll pay", "Check"]
for j, h in enumerate(heads):
    header(ws, 12, 2 + j, h)
ws.row_dimensions[12].height = 30

rng = lambda c: f"{c}${FIRST}:{c}${LAST}"  # noqa: E731
for k in range(ND):
    r = FIRST + k
    d = EXAMPLE[k] if k < len(EXAMPLE) else None
    cell(ws, f"B{r}", d.name if d else None, bg=INPUT)
    cell(ws, f"C{r}", d.balance if d else None, MONEY, bg=INPUT)
    cell(ws, f"D{r}", d.apr if d else None, PCT, bg=INPUT)
    cell(ws, f"E{r}", d.minimum if d else None, MONEY, bg=INPUT)
    cell(ws, f"F{r}", d.custom if d else None, "0", bg=INPUT, align="center")
    cell(ws, f"G{r}", f'=IF(N(C{r})>0,C{r}*N(D{r})/1200,"")', MONEY)
    # Avalanche: APR high->low, ties smaller balance, then row
    cell(ws, f"H{r}", (
        f'=IF(N(C{r})>0,1+SUMPRODUCT(({rng("C")}>0)*(({rng("D")}>N(D{r}))'
        f'+({rng("D")}=N(D{r}))*({rng("C")}<C{r})'
        f'+({rng("D")}=N(D{r}))*({rng("C")}=C{r})*(ROW({rng("C")})<ROW(C{r})))),"")'), "0", align="center")
    # Snowball: balance low->high, ties higher APR, then row
    cell(ws, f"I{r}", (
        f'=IF(N(C{r})>0,1+SUMPRODUCT(({rng("C")}>0)*(({rng("C")}<C{r})'
        f'+({rng("C")}=C{r})*({rng("D")}>N(D{r}))'
        f'+({rng("C")}=C{r})*({rng("D")}=N(D{r}))*(ROW({rng("C")})<ROW(C{r})))),"")'), "0", align="center")
    # Custom: helper key in R (blank order -> 999), unique by row
    cell(ws, f"R{r}", f'=IF(N(F{r})>0,F{r},999)+ROW()/1000', "0.000", size=8, color=MUTED, border=False)
    cell(ws, f"J{r}", f'=IF(N(C{r})>0,1+SUMPRODUCT(({rng("C")}>0)*({rng("R")}<R{r})),"")', "0", align="center")
    cell(ws, f"K{r}", f'=IF(N(C{r})>0,CHOOSE($Q$6,H{r},I{r},J{r}),"")', "0", align="center", bold=True)
    cell(ws, f"L{r}", f"=IF(N(C{r})>0,INDEX('Calc · Your Plan'!$B$8:$AG$8,4*(K{r}-1)+1),\"\")", "0",
         align="center", bg=OUTFILL, bold=True)
    cell(ws, f"M{r}", f'=IF(ISNUMBER(L{r}),EDATE($C$8,L{r}-1),IF(N(C{r})>0,"30+ years",""))', MONTHFMT,
         align="center", bg=OUTFILL, bold=True)
    cell(ws, f"N{r}", f"=IF(N(C{r})>0,IF(ISNUMBER(L{r}),INDEX('Calc · Your Plan'!$B$9:$AG$9,4*(K{r}-1)+1),\"n/a\"),\"\")", MONEY, align="right")
    cell(ws, f"O{r}", (
        f'=IF(N(C{r})<=0,IF(OR(N(E{r})>0,N(D{r})>0),"Add a balance",""),'
        f'IF(N(E{r})<=0,"Add the minimum payment",'
        f'IF(N(E{r})<=C{r}*N(D{r})/1200,"Minimum doesn\'t cover interest","OK")))'), size=9)
cell(ws, "R12", "custom key", size=8, color=MUTED, border=False)
ws.column_dimensions["R"].hidden = False

tr = TOTAL_ROW
cell(ws, f"B{tr}", "Total", bold=True, bg=TINT)
cell(ws, f"C{tr}", f"=SUM(C{FIRST}:C{LAST})", MONEY, bold=True, bg=TINT)
cell(ws, f"D{tr}", f'=IF(C{tr}>0,SUMPRODUCT(C{FIRST}:C{LAST},D{FIRST}:D{LAST})/C{tr},"")', PCT, bold=True, bg=TINT)
cell(ws, f"E{tr}", f"=SUM(E{FIRST}:E{LAST})", MONEY, bold=True, bg=TINT)
for col in "FGHIJKLM":
    cell(ws, f"{col}{tr}", None, bg=TINT)
cell(ws, f"G{tr}", f"=SUM(G{FIRST}:G{LAST})", MONEY, bold=True, bg=TINT)
cell(ws, f"N{tr}", f"=SUM(N{FIRST}:N{LAST})", MONEY, bold=True, bg=TINT)
cell(ws, f"O{tr}", None, bg=TINT)
note(ws, f"D{tr+1}", "Total row APR = balance-weighted average.", 8)

# conditional formatting on Check column
ws.conditional_formatting.add(f"O{FIRST}:O{LAST}", FormulaRule(
    formula=[f'AND(O{FIRST}<>"",O{FIRST}<>"OK")'], font=Font(name=F, color="B42318", bold=True),
    fill=fill("FDE7E4")))
ws.conditional_formatting.add(f"O{FIRST}:O{LAST}", CellIsRule(operator="equal", formula=['"OK"'],
                                                             font=Font(name=F, color="1E8A50")))

# Summary
sr = tr + 3
header(ws, sr, 2, "Your plan at a glance")
header(ws, sr, 3, "")
ws.merge_cells(start_row=sr, start_column=2, end_row=sr, end_column=3)
summary = [
    ("Plan", "=C6", None),
    ("Total monthly debt payment", f"=E{tr}+C7", MONEY),
    ("Months to debt-free", "='Calc · Your Plan'!AI4", "0"),
    ("Debt-free month", "=IF(ISNUMBER(C{0}),IF(C{0}=0,\"\",EDATE(C8,C{0}-1)),\"30+ years\")", MONTHFMT),
    ("Total interest", "=IF(ISNUMBER(C{0}),'Calc · Your Plan'!AI5,\"n/a: not paid off in 30 yrs\")", MONEY),
    ("Total you'll pay", "=IF(ISNUMBER(C{0}),'Calc · Your Plan'!AI6,\"n/a\")", MONEY),
    ("Interest saved vs minimums only", "=IF(NOT(ISNUMBER(C{1})),\"n/a\",IF(ISNUMBER('Calc · Minimums Only'!AI4),'Calc · Minimums Only'!AI5-C{1},\"Minimums alone never pay it off\"))", MONEY),
    ("Months sooner vs minimums only", "=IF(NOT(ISNUMBER(C{2})),\"n/a\",IF(ISNUMBER('Calc · Minimums Only'!AI4),'Calc · Minimums Only'!AI4-C{2},\"Minimums alone: 30+ yrs\"))", "0"),
]
rows_at = {}
for i, (lbl, f_, fmt) in enumerate(summary):
    rr = sr + 1 + i
    rows_at[lbl] = rr
for i, (lbl, f_, fmt) in enumerate(summary):
    rr = sr + 1 + i
    f2 = f_
    if "{0}" in f2 or "{1}" in f2 or "{2}" in f2:
        f2 = f2.replace("{0}", str(rows_at["Months to debt-free"])).replace(
            "{1}", str(rows_at["Total interest"])).replace("{2}", str(rows_at["Months to debt-free"]))
    cell(ws, f"B{rr}", lbl, bold=True)
    cell(ws, f"C{rr}", f2, fmt, bg=OUTFILL, bold=True, align="right")
note(ws, f"B{sr + len(summary) + 1}",
     "Estimate only: lenders charge interest daily and card minimums usually fall as balances fall. "
     "Treat dates as ± a month or two.")
note(ws, f"B{sr + len(summary) + 2}",
     "If 'Months to debt-free' says 30+ years, a minimum is too small to cover its interest or the extra payment is 0.")
SUMMARY_ROW = sr
ws.freeze_panes = "A5"

# ====================================================================== Calc sheets
BLOCK0 = 2  # column B


def bcol(k, j):
    """Column index for priority block k (1-based), field j (0 bal+int, 1 min, 2 extra, 3 end)."""
    return BLOCK0 + 4 * (k - 1) + j


TAIL = BLOCK0 + 4 * ND      # first tail column (AH)
C_BUDGET, C_POOL, C_TOT, C_INT, C_PAID = (L(TAIL + i) for i in range(5))
R0 = 12                      # month 0 row
RLAST = R0 + MONTHS


def make_calc(name, rank_col, pool_on=True, tab="BFBFBF"):
    c = wb.create_sheet(name)
    c.sheet_properties.tabColor = tab
    c.sheet_view.showGridLines = False
    c["A1"] = f"{name.split('· ')[1]}: month-by-month engine (no inputs here)"
    c["A1"].font = font(13, True, INK)
    c["A2"] = ("Each month: balance × (1 + APR/12), then every minimum, then the extra pool to debts in priority "
               "order. Freed-up minimums roll forward." if pool_on else
               "Baseline: every debt pays only its own minimum. No extra, no rollover.")
    c["A2"].font = font(9, False, MUTED)
    c.column_dimensions["A"].width = 20
    labels = {4: "Debt (priority →)", 5: "APR %", 6: "Minimum", 7: "Starting balance", 8: "Paid off (month #)",
              9: "Interest on this debt"}
    for rr, t in labels.items():
        c.cell(row=rr, column=1, value=t).font = font(9, True, MUTED)
    rc = f"'My Debts'!${rank_col}${FIRST}:${rank_col}${LAST}"
    for k in range(1, ND + 1):
        c0 = L(bcol(k, 0))
        end = L(bcol(k, 3))
        m = f"MATCH({k},{rc},0)"
        c[f"{c0}4"] = f"=IFERROR(INDEX('My Debts'!$B${FIRST}:$B${LAST},{m})&\"\",\"\")"
        c[f"{c0}5"] = f"=IFERROR(N(INDEX('My Debts'!$D${FIRST}:$D${LAST},{m})),0)"
        c[f"{c0}6"] = f"=IFERROR(N(INDEX('My Debts'!$E${FIRST}:$E${LAST},{m})),0)"
        c[f"{c0}7"] = f"=IFERROR(N(INDEX('My Debts'!$C${FIRST}:$C${LAST},{m})),0)"
        c[f"{c0}8"] = (f'=IF({c0}7>0,IF({end}{RLAST}>0,"30+ yrs",COUNTIF({end}{R0+1}:{end}{RLAST},">0")+1),"")')
        c[f"{c0}9"] = f"=SUM({c0}{R0+1}:{c0}{RLAST})-SUM({end}{R0}:{end}{RLAST-1})"
        for rr in range(4, 10):
            c[f"{c0}{rr}"].font = font(9, rr == 4)
        c[f"{c0}5"].number_format = PCT
        for rr in (6, 7, 9):
            c[f"{c0}{rr}"].number_format = MONEY
        c.merge_cells(start_row=10, start_column=bcol(k, 0), end_row=10, end_column=bcol(k, 3))
        c[f"{c0}10"] = f'="#{k} "&{c0}4'
        c[f"{c0}10"].font = font(9, True, CREAM)
        c[f"{c0}10"].fill = fill(INK)
        for j, h in enumerate(["bal + interest", "minimum", "extra", "end balance"]):
            hc = c.cell(row=11, column=bcol(k, j), value=h)
            hc.font = font(8, True, INK)
            hc.fill = fill(CREAM)
            c.column_dimensions[L(bcol(k, j))].width = 11
    for i, h in enumerate(["budget", "extra pool", "total balance", "interest", "paid"]):
        hc = c.cell(row=11, column=TAIL + i, value=h)
        hc.font = font(8, True, INK)
        hc.fill = fill(CREAM)
        c.column_dimensions[L(TAIL + i)].width = 12
    c.cell(row=11, column=1, value="Month").font = font(8, True, INK)
    # strategy summary (AH4:AI7)
    for rr, (lbl, f_, fmt) in enumerate([
        ("Months to debt-free", f'=IF({C_TOT}{R0}<=0,0,IF({C_TOT}{RLAST}>0,"30+ yrs",COUNTIF({C_TOT}{R0+1}:{C_TOT}{RLAST},">0")+1))', "0"),
        ("Total interest", f"=SUM({C_INT}{R0+1}:{C_INT}{RLAST})", MONEY),
        ("Total paid", f"=SUM({C_PAID}{R0+1}:{C_PAID}{RLAST})", MONEY),
        ("First debt paid off (month #)", f"=IF(COUNT({L(BLOCK0)}8:{L(bcol(ND, 0))}8)=0,\"\",MIN({','.join(L(bcol(k, 0)) + '8' for k in range(1, ND + 1))}))", "0"),
    ], start=4):
        c[f"{C_BUDGET}{rr}"] = lbl
        c[f"{C_BUDGET}{rr}"].font = font(9, True, MUTED)
        c[f"{C_POOL}{rr}"] = f_
        c[f"{C_POOL}{rr}"].number_format = fmt
        c[f"{C_POOL}{rr}"].font = font(9, True)
    # month 0
    c[f"A{R0}"] = 0
    for k in range(1, ND + 1):
        c[f"{L(bcol(k, 3))}{R0}"] = f"={L(bcol(k, 0))}$7"
    c[f"{C_TOT}{R0}"] = "=" + "+".join(f"{L(bcol(k, 3))}{R0}" for k in range(1, ND + 1))
    for m in range(1, MONTHS + 1):
        r = R0 + m
        p = r - 1
        c[f"A{r}"] = m
        for k in range(1, ND + 1):
            b, mi, ex, en = (L(bcol(k, j)) for j in range(4))
            p0 = L(bcol(k, 0))
            c[f"{b}{r}"] = f"={en}{p}*(1+{p0}$5/1200)"
            c[f"{mi}{r}"] = f"=MIN({p0}$6,{b}{r})"
            prev_extras = "+".join(f"{L(bcol(q, 2))}{r}" for q in range(1, k)) or "0"
            c[f"{ex}{r}"] = f"=MAX(0,MIN({C_POOL}{r}-({prev_extras}),{b}{r}-{mi}{r}))"
            c[f"{en}{r}"] = f"=IF({b}{r}-{mi}{r}-{ex}{r}<0.005,0,{b}{r}-{mi}{r}-{ex}{r})"
        mins = "+".join(f"{L(bcol(k, 1))}{r}" for k in range(1, ND + 1))
        c[f"{C_BUDGET}{r}"] = f"='My Debts'!$E${TOTAL_ROW}+N('My Debts'!$C$7)+IF(A{r}='My Debts'!$C$10,N('My Debts'!$C$9),0)"
        c[f"{C_POOL}{r}"] = f"=MAX(0,{C_BUDGET}{r}-({mins}))" if pool_on else "=0"
        c[f"{C_TOT}{r}"] = "=" + "+".join(f"{L(bcol(k, 3))}{r}" for k in range(1, ND + 1))
        c[f"{C_INT}{r}"] = "=" + "+".join(f"({L(bcol(k, 0))}{r}-{L(bcol(k, 3))}{p})" for k in range(1, ND + 1))
        c[f"{C_PAID}{r}"] = "=" + "+".join(f"{L(bcol(k, 1))}{r}+{L(bcol(k, 2))}{r}" for k in range(1, ND + 1))
    for row in c.iter_rows(min_row=R0, max_row=RLAST, min_col=2, max_col=TAIL + 4):
        for x in row:
            x.number_format = '#,##0.00'
            x.font = font(8)
    for row in c.iter_rows(min_row=R0, max_row=RLAST, min_col=1, max_col=1):
        row[0].font = font(8, True)
    c.freeze_panes = f"B{R0}"
    return c


# Create the user-facing sheets first so tab order is friendly; calc sheets after.
cmp_ws = wb.create_sheet("Compare")
plan_ws = wb.create_sheet("Payoff Plan")
amort = wb.create_sheet("Loan Amortization")
cd = wb.create_sheet("Chart Data")
make_calc("Calc · Your Plan", "K", tab="8FA399")
make_calc("Calc · Avalanche", "H")
make_calc("Calc · Snowball", "I")
make_calc("Calc · Custom", "J")
make_calc("Calc · Minimums Only", "H", pool_on=False)

# ====================================================================== Compare
c = cmp_ws
c.sheet_properties.tabColor = GREEN
title(c, "Compare plans", "Same debts, same monthly budget, three different orders. Plus the 'minimums only' baseline.",
      "Difference = vs. minimums only. Snowball usually costs a bit more interest; it can win on motivation.")
for k, v in {"A": 2, "B": 38, "C": 16, "D": 16, "E": 16, "F": 18}.items():
    c.column_dimensions[k].width = v
cols = [("Avalanche", "Calc · Avalanche"), ("Snowball", "Calc · Snowball"), ("Custom", "Calc · Custom"),
        ("Minimums only", "Calc · Minimums Only")]
header(c, 5, 2, "")
for j, (lbl, _) in enumerate(cols):
    header(c, 5, 3 + j, lbl)
metrics = [
    ("Months to debt-free", "AI4", "0"),
    ("Debt-free month", None, MONTHFMT),
    ("Total interest", "AI5", MONEY),
    ("Total paid", "AI6", MONEY),
    ("First debt paid off (month #)", "AI7", "0"),
    ("Interest saved vs minimums only", None, MONEY),
    ("Monthly payment (while all debts open)", None, MONEY),
]
for i, (lbl, ref, fmt) in enumerate(metrics):
    r = 6 + i
    cell(c, f"B{r}", lbl, bold=True)
    for j, (_, sh) in enumerate(cols):
        col = L(3 + j)
        if lbl == "Debt-free month":
            f_ = f'=IF(ISNUMBER({col}6),IF({col}6=0,"",EDATE(\'My Debts\'!$C$8,{col}6-1)),"30+ years")'
        elif lbl == "Interest saved vs minimums only":
            f_ = (f"=IF(AND(ISNUMBER({col}8),ISNUMBER($F$8)),$F$8-{col}8,"
                  f"IF(AND(ISNUMBER({col}8),{j}<3),\"minimums never pay off\",\"\"))")
        elif lbl.startswith("Monthly payment"):
            f_ = "='My Debts'!$E$%d" % TOTAL_ROW if sh.endswith("Only") else "='My Debts'!$E$%d+'My Debts'!$C$7" % TOTAL_ROW
        elif lbl in ("Total interest", "Total paid"):
            f_ = f"=IF(ISNUMBER({col}6),'{sh}'!{ref},\"never paid off\")"
        else:
            f_ = f"='{sh}'!{ref}"
        cell(c, f"{col}{r}", f_, fmt, align="right", bg=OUTFILL if lbl in ("Total interest", "Months to debt-free") else None,
             bold=lbl in ("Total interest", "Months to debt-free"))
# best marker
r_best = 6 + len(metrics)
cell(c, f"B{r_best}", "Lowest interest of the three", bold=True)
for j in range(3):
    col = L(3 + j)
    cell(c, f"{col}{r_best}", f'=IF(AND(ISNUMBER({col}8),N({col}6)>0),IF({col}8=MIN($C$8:$E$8),"✓ lowest",""),"")', align="center", color="1E8A50", bold=True)
cell(c, f"F{r_best}", "")
note(c, f"B{r_best+1}", "Totals cover up to 30 years. If a column says 30+ years, at least one debt never gets paid off at that pace.")

# per-debt payoff months
pr = r_best + 3
header(c, pr, 2, "Paid off in month #")
for j, (lbl, _) in enumerate(cols):
    header(c, pr, 3 + j, lbl)
for k in range(ND):
    r = pr + 1 + k
    src = FIRST + k
    cell(c, f"B{r}", f"=IF(N('My Debts'!C{src})>0,'My Debts'!B{src}&\"\",\"\")")
    for j, (lbl, sh) in enumerate(cols):
        rank = {"Avalanche": "H", "Snowball": "I", "Custom": "J", "Minimums only": "H"}[lbl]
        cell(c, f"{L(3+j)}{r}",
             f"=IF(N('My Debts'!C{src})>0,INDEX('{sh}'!$B$8:$AG$8,4*('My Debts'!{rank}{src}-1)+1),\"\")",
             "0", align="center")
CMP_CHART_ROW = pr + ND + 3

# ====================================================================== Chart Data
cd.sheet_properties.tabColor = "BFBFBF"
title(cd, "Chart Data", "Feeds the charts. No inputs here.", None)
cd.column_dimensions["A"].width = 2
cd["B4"] = "Compare chart step (months)"
cd["C4"] = ("=MAX(1,CEILING(MAX(IF(ISNUMBER('Calc · Avalanche'!AI4),'Calc · Avalanche'!AI4,360),"
            "IF(ISNUMBER('Calc · Snowball'!AI4),'Calc · Snowball'!AI4,360),"
            "IF(ISNUMBER('Calc · Custom'!AI4),'Calc · Custom'!AI4,360),"
            "IF(ISNUMBER('Calc · Minimums Only'!AI4),'Calc · Minimums Only'!AI4,360),1)/60,1))")
cd["B5"] = "Your-plan chart step (months)"
cd["C5"] = "=MAX(1,CEILING(IF(ISNUMBER('Calc · Your Plan'!AI4),'Calc · Your Plan'!AI4,360)/40,1))"
for rr in (4, 5):
    cd[f"B{rr}"].font = font(9, True)
for j, h in enumerate(["Month", "Avalanche", "Snowball", "Custom", "Minimums only"]):
    header(cd, 7, 2 + j, h)
for p in range(61):
    r = 8 + p
    cd[f"B{r}"] = f"={p}*$C$4"
    for j, sh in enumerate(["Calc · Avalanche", "Calc · Snowball", "Calc · Custom", "Calc · Minimums Only"]):
        cd[f"{L(3+j)}{r}"] = f"=IF(B{r}>{MONTHS},0,INDEX('{sh}'!${C_TOT}${R0}:${C_TOT}${RLAST},B{r}+1))"
        cd[f"{L(3+j)}{r}"].number_format = MONEY0
# your plan by debt (input order)
base = 8 + 61 + 2
header(cd, base, 2, "Month")
for k in range(ND):
    src = FIRST + k
    cd.cell(row=base, column=3 + k, value=f"=IF(N('My Debts'!C{src})>0,'My Debts'!B{src}&\"\",\" \")")
    cd.cell(row=base, column=3 + k).font = font(10, True, CREAM)
    cd.cell(row=base, column=3 + k).fill = fill(INK)
for p in range(41):
    r = base + 1 + p
    cd[f"B{r}"] = f"={p}*$C$5"
    for k in range(ND):
        src = FIRST + k
        col = L(3 + k)
        cd[f"{col}{r}"] = (f"=IF(OR(N('My Debts'!C{src})<=0,B{r}>{MONTHS}),0,"
                           f"INDEX('Calc · Your Plan'!$B${R0}:$AG${RLAST},B{r}+1,4*('My Debts'!K{src}-1)+4))")
        cd[f"{col}{r}"].number_format = MONEY0
for k in range(ND + 1):
    cd.column_dimensions[L(2 + k)].width = 14

# charts
ch = LineChart()
ch.title = "Total balance over time"
ch.y_axis.title = "Total owed ($)"
ch.x_axis.title = "Month"
ch.height, ch.width = 9, 22
ch.y_axis.numFmt = '"$"#,##0'
ch.y_axis.majorGridlines = None
data = Reference(cd, min_col=3, max_col=6, min_row=7, max_row=68)
ch.add_data(data, titles_from_data=True)
ch.set_categories(Reference(cd, min_col=2, min_row=8, max_row=68))
for s, colr, dash in zip(ch.series, [GREEN, GOLD, "5B7FA6", "9AA59F"], [None, None, None, "dash"]):
    s.graphicalProperties.line.solidFill = colr
    s.graphicalProperties.line.width = 28000
    if dash:
        s.graphicalProperties.line.dashStyle = dash
    s.smooth = False
    s.marker.symbol = "none"
ch.x_axis.tickLblSkip = 10
ch.x_axis.delete = False
ch.y_axis.delete = False
ch.legend.position = "b"
cmp_ws.add_chart(ch, f"B{CMP_CHART_ROW}")

ach = AreaChart()
ach.grouping = "stacked"
ach.title = "Your plan: what you owe, by debt"
ach.y_axis.title = "Balance ($)"
ach.x_axis.title = "Month"
ach.height, ach.width = 9, 22
ach.y_axis.numFmt = '"$"#,##0'
ach.add_data(Reference(cd, min_col=3, max_col=2 + ND, min_row=base, max_row=base + 41), titles_from_data=True)
ach.set_categories(Reference(cd, min_col=2, min_row=base + 1, max_row=base + 41))
palette = [GREEN, GOLD, "5B7FA6", "C8553D", "8E6BB0", "1E8A50", "D9A441", "6C7A73"]
for s, colr in zip(ach.series, palette):
    s.graphicalProperties.solidFill = colr
    s.graphicalProperties.line.solidFill = colr
ach.x_axis.tickLblSkip = 5
ach.x_axis.delete = False
ach.y_axis.delete = False
ach.legend.position = "b"
ws.add_chart(ach, f"E{SUMMARY_ROW}")

# ====================================================================== Payoff Plan
pp = plan_ws
pp.sheet_properties.tabColor = GREEN
title(pp, "Payoff Plan", "Your month-by-month schedule for the plan chosen on My Debts. One row per payment month.",
      "Payment = minimum + any extra. Rows go blank after your debt-free month.")
pp.column_dimensions["A"].width = 2
pp.column_dimensions["B"].width = 8
pp.column_dimensions["C"].width = 11
pp["B4"] = "Plan:"
pp["B4"].font = font(10, True)
pp["C4"] = "='My Debts'!C6"
pp["C4"].font = font(10, True, "1E8A50")
pp["E4"] = "Rows shown:"
pp["E4"].font = font(9, False, MUTED)
pp["F4"] = f"=IF(ISNUMBER('Calc · Your Plan'!AI4),'Calc · Your Plan'!AI4,{MONTHS})"
pp["F4"].font = font(9, False, MUTED)
header(pp, 6, 2, "Month #")
header(pp, 6, 3, "Date")
pp.row_dimensions[6].height = 30
pp.row_dimensions[7].height = 28
for k in range(ND):
    src = FIRST + k
    pc, bc = 4 + 2 * k, 5 + 2 * k
    header(pp, 6, pc, f"=IF(N('My Debts'!C{src})>0,'My Debts'!B{src}&\"\",\"(debt {k+1})\")", 2)
    for col, h in ((pc, "pay"), (bc, "balance")):
        hc = pp.cell(row=7, column=col, value=h)
        hc.font = font(8, True, INK)
        hc.fill = fill(CREAM)
        hc.alignment = Alignment(horizontal="center")
        pp.column_dimensions[L(col)].width = 11
    # helper: offset into the plan calc row (hidden row 5)
    pp.cell(row=5, column=pc, value=f"=IF(N('My Debts'!C{src})>0,4*('My Debts'!K{src}-1),\"\")")
tc = 4 + 2 * ND
for i, h in enumerate(["Total paid", "Interest", "Still owed"]):
    header(pp, 6, tc + i, h)
    pp.cell(row=7, column=tc + i).fill = fill(CREAM)
    pp.column_dimensions[L(tc + i)].width = 12
header(pp, 7, 2, "")
header(pp, 7, 3, "")
pp.row_dimensions[5].hidden = True
for m in range(1, MONTHS + 1):
    r = 7 + m
    cr = R0 + m
    show = f"$B{r}<=$F$4"
    pp[f"B{r}"] = f'=IF({m}<=$F$4,{m},"")'
    pp[f"C{r}"] = f'=IF(ISNUMBER(B{r}),EDATE(\'My Debts\'!$C$8,B{r}-1),"")'
    pp[f"C{r}"].number_format = MONTHFMT
    for k in range(ND):
        pc, bc = 4 + 2 * k, 5 + 2 * k
        off = f"{L(pc)}$5"
        row = f"'Calc · Your Plan'!$B${cr}:$AG${cr}"
        pp.cell(row=r, column=pc, value=(f'=IF(OR(NOT(ISNUMBER($B{r})),{off}=""),"",'
                                         f"INDEX({row},{off}+2)+INDEX({row},{off}+3))"))
        pp.cell(row=r, column=bc, value=(f'=IF(OR(NOT(ISNUMBER($B{r})),{off}=""),"",'
                                         f'IF(AND(N({L(pc)}{r})=0,INDEX({row},{off}+4)=0),"",INDEX({row},{off}+4)))'))
    pp.cell(row=r, column=tc, value=f"=IF(ISNUMBER($B{r}),'Calc · Your Plan'!{C_PAID}{cr},\"\")")
    pp.cell(row=r, column=tc + 1, value=f"=IF(ISNUMBER($B{r}),'Calc · Your Plan'!{C_INT}{cr},\"\")")
    pp.cell(row=r, column=tc + 2, value=f"=IF(ISNUMBER($B{r}),'Calc · Your Plan'!{C_TOT}{cr},\"\")")
    for col in range(2, tc + 3):
        x = pp.cell(row=r, column=col)
        x.font = font(9, col in (2, tc + 2))
        if col >= 4:
            x.number_format = MONEY0 if ((col - 4) % 2 == 1 and col < tc) else (
                '"$"#,##0.00;-"$"#,##0.00;""' if col < tc else '"$"#,##0.00')
        x.border = Border(bottom=Side(style="hair", color=LINE))
        if m % 2 == 0:
            x.fill = fill("FAF8F2")
    pp.cell(row=r, column=2).alignment = Alignment(horizontal="center")
# highlight payoff (balance hits 0 while payment > 0)
for k in range(ND):
    pc, bc = 4 + 2 * k, 5 + 2 * k
    rng_ = f"{L(bc)}8:{L(bc)}{7+MONTHS}"
    pp.conditional_formatting.add(rng_, FormulaRule(
        formula=[f'AND(ISNUMBER({L(bc)}8),{L(bc)}8=0,N({L(pc)}8)>0)'],
        fill=fill(OUTFILL), font=Font(name=F, bold=True, color="1E8A50")))
pp.freeze_panes = "D8"
pp.print_title_rows = "6:7"
pp.page_setup.orientation = "landscape"
pp.page_setup.fitToWidth = 1
pp.page_setup.fitToHeight = 0
pp.sheet_properties.pageSetUpPr.fitToPage = True

# ====================================================================== Loan Amortization
a = amort
a.sheet_properties.tabColor = GOLD
title(a, "Loan Amortization", "One fixed-payment loan: where each payment goes, and what paying extra saves.",
      "Yellow = inputs. Example is fictional. Separate from My Debts: nothing here changes your plan.")
for k, v in {"A": 2, "B": 30, "C": 16, "D": 4, "E": 9, "F": 11, "G": 13, "H": 13, "I": 13, "J": 13, "K": 15}.items():
    a.column_dimensions[k].width = v
header(a, 5, 2, "Loan")
header(a, 5, 3, "")
inputs = [("Loan amount", 18500, MONEY), ("APR %", 5.8, PCT), ("Term (months)", 120, "0"),
          ("First payment month", date(2026, 12, 1), MONTHFMT), ("Extra payment per month", 50, MONEY)]
for i, (lbl, v, fmt) in enumerate(inputs):
    cell(a, f"B{6+i}", lbl, bold=True)
    cell(a, f"C{6+i}", v, fmt, bg=INPUT)
header(a, 12, 2, "Results")
header(a, 12, 3, "")
res = [
    ("Regular monthly payment", '=IF(OR(N(C6)<=0,N(C8)<=0),0,IF(N(C7)=0,C6/C8,PMT(C7/1200,C8,-C6)))', MONEY),
    ("Total interest (no extra)", "=IF(C13>0,C13*C8-C6,0)", MONEY),
    ("Payoff with extra (months)", f'=IF(N(C6)<=0,0,IF(K{20+600-1}>0,"50+ yrs",COUNTIF(K20:K{20+600-1},">0")+1))', "0"),
    ("Payoff month with extra", '=IF(ISNUMBER(C15),IF(C15=0,"",EDATE(C9,C15-1)),"")', MONTHFMT),
    ("Total interest with extra", "=SUM(H20:H619)", MONEY),
    ("Interest saved by paying extra", "=C14-C17", MONEY),
    ("Months saved", '=IF(ISNUMBER(C15),C8-C15,"")', "0"),
]
for i, (lbl, f_, fmt) in enumerate(res):
    cell(a, f"B{13+i}", lbl, bold=True)
    cell(a, f"C{13+i}", f_, fmt, bg=OUTFILL, bold=True, align="right")
for i, t in enumerate([
        "Real loans may charge interest daily and round each payment; small differences are normal.",
        "Before paying extra, check the lender applies it to principal and has no prepayment penalty.",
        "Student loans: income-driven plans and forgiveness can change the math. Check studentaid.gov first."]):
    rr = 21 + i
    note(a, f"B{rr}", t)
    a[f"B{rr}"].alignment = Alignment(wrap_text=True, vertical="top")
    a.merge_cells(f"B{rr}:C{rr}")
    a.row_dimensions[rr].height = 26
for j, h in enumerate(["#", "Date", "Payment", "Interest", "Principal", "of which extra", "Balance"]):
    header(a, 18, 5 + j, h)
a["E19"] = 0
a["K19"] = "=N(C6)"
a["K19"].number_format = MONEY
a["F19"] = "start"
for x in ("E19", "F19", "K19"):
    a[x].font = font(9, True)
for m in range(1, 601):
    r = 19 + m
    p = r - 1
    a[f"E{r}"] = f'=IF(K{p}>0,{m},"")'
    a[f"F{r}"] = f'=IF(ISNUMBER(E{r}),EDATE($C$9,E{r}-1),"")'
    a[f"H{r}"] = f'=IF(ISNUMBER(E{r}),K{p}*N($C$7)/1200,"")'
    a[f"G{r}"] = f'=IF(ISNUMBER(E{r}),MIN(K{p}+H{r},$C$13+N($C$10)),"")'
    a[f"I{r}"] = f'=IF(ISNUMBER(E{r}),G{r}-H{r},"")'
    a[f"J{r}"] = f'=IF(ISNUMBER(E{r}),MAX(0,G{r}-MIN(K{p}+H{r},$C$13)),"")'
    a[f"K{r}"] = f'=IF(ISNUMBER(E{r}),IF(K{p}+H{r}-G{r}<0.005,0,K{p}+H{r}-G{r}),0)'
    for col in "EFGHIJK":
        x = a[f"{col}{r}"]
        x.font = font(9)
        x.number_format = {"E": "0", "F": MONTHFMT}.get(col, MONEY)
        x.border = Border(bottom=Side(style="hair", color=LINE))
a.freeze_panes = "A20"
a.conditional_formatting.add("E20:K619", FormulaRule(formula=['NOT(ISNUMBER($E20))'], font=Font(color="FFFFFF")))

# ====================================================================== print setup & save
for s in wb.worksheets:
    s.page_setup.orientation = s.page_setup.orientation or "landscape"
    if s.title in ("Start Here", "My Debts", "Compare", "Loan Amortization"):
        s.page_setup.orientation = "landscape" if s.title != "Start Here" else "portrait"
        s.page_setup.fitToWidth = 1
        s.page_setup.fitToHeight = 0
        s.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_area = f"A1:O{SUMMARY_ROW+32}"
cmp_ws.print_area = f"A1:F{CMP_CHART_ROW+20}"
wb.calculation.fullCalcOnLoad = True
wb.active = 1
OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print("wrote", OUT)
