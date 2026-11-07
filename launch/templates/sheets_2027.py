"""2027 Budget Sheet: a dated workbook with one tab per month (Jan 2027 ... Dec 2027) and a 2027 year tab.

Same house style and functions as sheets_templates.py (SUMIFS, SUMIF, REPT; nothing that breaks on Google Sheets
import). Setup holds the categories and the default monthly budget; each month tab copies that budget (yellow, so it
can be changed for that month only), has its own spending log, and shows every category against its budget. The
2027 tab lines all twelve months up with group totals and a chart. January and part of February carry fictional
example data.
"""
from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Font
from openpyxl.worksheet.datavalidation import DataValidation

import sheets_templates as T
from sheets_templates import S

YEAR = 2027
N_LOG = 120
SUM0 = 8                      # group summary rows 8-12, left over 13
CATROW = 16                   # category table rows 16 .. 16 + N_CATS - 1
LOG_HEAD = CATROW + T.N_CATS + 2
LOG0 = LOG_HEAD + 1


def tab(m: int, year: int = YEAR) -> str:
    return f"{calendar.month_abbr[m]} {year}"


def q(name: str) -> str:
    return f"'{name}'"


def _month(wb: Workbook, m: int, year: int, examples: list) -> None:
    first, last = date(year, m, 1), date(year, m, calendar.monthrange(year, m)[1])
    ws = S._sheet(wb, tab(m, year), f"{calendar.month_name[m]} {year}",
                  "Budget at the top, spending log underneath. Log every amount as a positive number.",
                  widths={"B": 26, "C": 13, "D": 14, "E": 14, "F": 14, "G": 9, "H": 18})
    S._label(ws, "B5", "Month")
    S._calc(ws["C5"], first, "mmm d, yyyy")
    S._calc(ws["D5"], last, "mmm d, yyyy")
    lg = lambda col: f"${col}${LOG0}:${col}${LOG0 + N_LOG - 1}"  # noqa: E731
    cl = f"$C${CATROW}:$C${CATROW + T.N_CATS - 1}"
    S._header(ws, SUM0 - 1, ["This month", "Planned", "Actual", "Left"])
    for i, g in enumerate(T.GROUPS):
        r = SUM0 + i
        S._label(ws, f"B{r}", {"Debt": "Debt payments", "Income": "Income received"}.get(g, g), bold=False)
        S._calc(ws[f"C{r}"], f'=SUMIF({cl},"{g}",$D${CATROW}:$D${CATROW + T.N_CATS - 1})', S.MONEY0)
        S._calc(ws[f"D{r}"], f'=SUMIF({cl},"{g}",$E${CATROW}:$E${CATROW + T.N_CATS - 1})', S.MONEY0)
        S._calc(ws[f"E{r}"], f"=C{r}-D{r}", S.MONEY0)
    lo = SUM0 + len(T.GROUPS)
    S._label(ws, f"B{lo}", "Left over")
    S._calc(ws[f"C{lo}"], f"=C{SUM0}-SUM(C{SUM0 + 1}:C{lo - 1})", S.MONEY0, bold=True)
    S._calc(ws[f"D{lo}"], f"=D{SUM0}-SUM(D{SUM0 + 1}:D{lo - 1})", S.MONEY0, bold=True)
    S._total_row(ws, lo, 2, 5)
    ws.conditional_formatting.add(f"D{lo}", CellIsRule(operator="lessThan", formula=["0"], fill=T.RED))

    S._header(ws, CATROW - 1, ["Category", "Group", "Budget", "Actual", "Left", "Used", ""])
    for i in range(T.N_CATS):
        r, sr = CATROW + i, T.CAT0 + i
        S._calc(ws.cell(r, 2), f'=IF(Setup!B{sr}="","",Setup!B{sr})')
        S._calc(ws.cell(r, 3), f'=IF(B{r}="","",Setup!C{sr})')
        S._inp(ws.cell(r, 4), f'=IF(B{r}="","",N(Setup!D{sr}))', S.MONEY0)
        S._calc(ws.cell(r, 5), f'=IF(B{r}="","",SUMIF({lg("D")},B{r},{lg("E")}))', S.MONEY)
        S._calc(ws.cell(r, 6), f'=IF(B{r}="","",D{r}-E{r})', S.MONEY)
        S._calc(ws.cell(r, 7), f'=IF(OR(B{r}="",N(D{r})=0),"",E{r}/D{r})', "0%")
        T._bar(ws.cell(r, 8), f"G{r}", 12)
    cl_last = CATROW + T.N_CATS - 1
    ws.conditional_formatting.add(f"F{CATROW}:F{cl_last}",
                                  FormulaRule(formula=[f'AND(C{CATROW}<>"Income",N(F{CATROW})<0)'], fill=T.RED))

    S._header(ws, LOG_HEAD, ["Date", "Description", "Category", "Amount", "Group"])
    for i in range(N_LOG):
        r = LOG0 + i
        row = examples[i] if i < len(examples) else (None,) * 4
        S._inp(ws.cell(r, 2), row[0], "mmm d")
        S._inp(ws.cell(r, 3), row[1])
        S._inp(ws.cell(r, 4), row[2])
        S._inp(ws.cell(r, 5), row[3], S.MONEY)
        S._calc(ws.cell(r, 6), f'=IF(D{r}="","",IFERROR(INDEX($C${CATROW}:$C${cl_last},MATCH(D{r},$B${CATROW}:$B${cl_last},0)),'
                               f'"Not on Setup"))')
    rng = f"B{LOG0}:B{LOG0 + N_LOG - 1}"
    dv = DataValidation(type="date", operator="between", formula1=f"DATE({year},{m},1)",
                        formula2=f"DATE({year},{m},{last.day})", allow_blank=True)
    dv.error, dv.errorTitle = f"This tab is {calendar.month_name[m]} {year}. Log other months on their own tab.", "Wrong month"
    ws.add_data_validation(dv)
    dv.add(rng)
    T._range_validation(ws, f"Setup!$B${T.CAT0}:$B${T.CAT0 + T.N_CATS - 1}", f"D{LOG0}:D{LOG0 + N_LOG - 1}")
    ws.conditional_formatting.add(f"F{LOG0}:F{LOG0 + N_LOG - 1}",
                                  CellIsRule(operator="equal", formula=['"Not on Setup"'], fill=T.RED))
    ws.freeze_panes = "B6"
    S._foot(ws, LOG0 + N_LOG + 1)


def _year(wb: Workbook, year: int) -> None:
    yr = S._sheet(wb, str(year), f"{year} at a glance", "Every category, month by month. Fills in from the month tabs.",
                  widths={"B": 24, "C": 11, **{chr(68 + i): 10 for i in range(12)}, "P": 12, "Q": 12})
    S._header(yr, 5, ["Category", "Group"] + [calendar.month_abbr[m] for m in range(1, 13)] + ["Total", "Avg / month"])
    for i in range(T.N_CATS):
        r, mr, sr = 6 + i, CATROW + i, T.CAT0 + i
        S._calc(yr.cell(r, 2), f'=IF(Setup!B{sr}="","",Setup!B{sr})')
        S._calc(yr.cell(r, 3), f'=IF(B{r}="","",Setup!C{sr})')
        for m in range(1, 13):
            S._calc(yr.cell(r, 3 + m), f'=IF($B{r}="","",N({q(tab(m, year))}!E{mr}))', S.MONEY0)
        S._calc(yr.cell(r, 16), f'=IF(B{r}="","",SUM(D{r}:O{r}))', S.MONEY0)
        S._calc(yr.cell(r, 17), f'=IF(B{r}="","",P{r}/12)', S.MONEY0)
    yl = 6 + T.N_CATS - 1
    g0 = yl + 2
    labels = T.GROUPS + ["Left over"]
    for i, g in enumerate(labels):
        r = g0 + i
        yr.cell(r, 2, "Totals" if i == 0 else None)
        S._label(yr, f"C{r}", g)
        for col in range(4, 17):
            L = yr.cell(r, col).column_letter
            f = (f'=SUMIF($C$6:$C${yl},"{g}",{L}$6:{L}${yl})' if g in T.GROUPS
                 else f"={L}{g0}-SUM({L}{g0 + 1}:{L}{g0 + 4})")
            S._calc(yr.cell(r, col), f, S.MONEY0, bold=True)
        S._total_row(yr, r, 2, 16)
    lo = g0 + len(T.GROUPS)
    yr.conditional_formatting.add(f"D{lo}:P{lo}", CellIsRule(operator="lessThan", formula=["0"], fill=T.RED))
    ch = BarChart()
    ch.title, ch.height, ch.width = f"{year}: income vs left over", 8, 22
    ch.y_axis.numFmt = '"$"#,##0'
    ch.add_data(Reference(yr, min_col=3, max_col=15, min_row=g0, max_row=g0), from_rows=True, titles_from_data=True)
    ch.add_data(Reference(yr, min_col=3, max_col=15, min_row=lo, max_row=lo), from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(yr, min_col=4, max_col=15, min_row=5))
    ch.series[0].graphicalProperties.solidFill = S.GREEN
    ch.series[1].graphicalProperties.solidFill = S.GOLD
    yr.add_chart(ch, f"B{lo + 3}")
    yr.freeze_panes = "D6"
    S._foot(yr, lo + 21)


def build_budget_2027(path: Path, today: date | None = None, year: int = YEAR) -> Path:
    wb = Workbook()
    T._start(wb, f"{year} Budget Sheet", f"A dated budget for {year}: one tab per month, and the whole year on one page.",
             ["On Setup, change the categories and default monthly amounts to yours. Income goes in as Income.",
              f"Open this month's tab (Jan {year} to Dec {year}). Its budget copies Setup; type over any yellow amount "
              "to change it for that month only.",
              "Log what comes in and goes out underneath: date, a few words, category, amount.",
              f"The {year} tab lines up all twelve months. January and February have example data: delete it first."],
             [("Setup", "Your categories, their group and the default monthly budget."),
              (f"Jan {year} ... Dec {year}", "One tab per month: budget, actual, left, and that month's spending log."),
              (str(year), "Twelve months side by side, group totals, average per month and a chart.")])
    st = S._sheet(wb, "Setup", "Setup: your categories and default budget",
                  "These amounts copy into every month. When 'Left to assign' is $0, the budget is done.",
                  widths={"B": 26, "C": 12, "D": 16, "E": 40})
    S._header(st, 5, ["Category", "Group", "Monthly budget", "Notes"])
    last = T.CAT0 + T.N_CATS - 1
    for i in range(T.N_CATS):
        r = T.CAT0 + i
        name, grp, amt = T.BUDGET_CATS[i] if i < len(T.BUDGET_CATS) else (None, None, None)
        S._inp(st.cell(r, 2), name)
        S._inp(st.cell(r, 3), grp)
        S._inp(st.cell(r, 4), amt, S.MONEY0)
        S._inp(st.cell(r, 5))
    S._list_validation(st, T.GROUPS, f"C{T.CAT0}:C{last}")
    t = last + 2
    for i, (lab, f) in enumerate([("Planned income", f'=SUMIF(C{T.CAT0}:C{last},"Income",D{T.CAT0}:D{last})'),
                                  ("Planned spending, saving + debt", f"=SUM(D{T.CAT0}:D{last})-D{t}"),
                                  ("Left to assign", f"=D{t}-D{t + 1}")]):
        S._label(st, f"B{t + i}", lab, bold=(i == 2))
        S._calc(st[f"D{t + i}"], f, S.MONEY0, bold=(i == 2))
    S._total_row(st, t + 2, 2, 4)
    st.conditional_formatting.add(f"D{t + 2}", CellIsRule(operator="notEqual", formula=["0"], fill=T.RED))
    st.conditional_formatting.add(f"D{t + 2}", CellIsRule(operator="equal", formula=["0"], fill=T.OK))
    st.freeze_panes = f"B{T.CAT0}"
    S._foot(st, t + 5)
    for m in range(1, 13):
        ex = []
        if m == 1:
            ex = sorted(T._budget_examples(date(year, 1, 1)))
        elif m == 2:
            ex = sorted(x for x in T._budget_examples(date(year, 2, 1)) if x[0].day <= 17)
        _month(wb, m, year, ex)
    _year(wb, year)
    wb.move_sheet(str(year), offset=-13)       # Start, 2027, Setup, Jan ... Dec
    for ws in wb.worksheets:
        ws.sheet_view.tabSelected = ws.title == "Start"
    wb.active = 0
    wb.save(path)
    return path


if __name__ == "__main__":
    import sys
    print(build_budget_2027(Path(sys.argv[1] if len(sys.argv) > 1 else "2027-Budget-Sheet.xlsx")))
