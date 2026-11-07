"""Moving Budget Sheet for Google Sheets (also opens in Excel and Numbers).

Scouting's product-ideas-round2.md (PR #2): "moving checklist" gets 14,800 searches a month and is rising, with few
listings. This sheet pairs with the apps thread's moving cost calculator (PR #8): CATEGORIES are its labels in its
order, and its "Copy rows" output (tab-separated Category, Estimate, Actual, Paid, no header) pastes into the
Planner paste tab at B7, the same shape as the Wedding Budget Sheet. Budget's yellow Estimate, Actual and Paid cells
use the paste (matched by category name) wherever you leave them blank; a typed number always wins.
Tabs: Start, Setup, Budget, Quotes (compare three movers), Utilities (stop, start, transfer), Planner paste.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font

import sheets_templates as ST
from sheets_templates import RED, S, _start

CATEGORIES = ["Movers or truck rental", "Fuel and mileage", "Packing supplies", "Storage", "Travel and lodging",
              "Deposits (new place)", "Overlap rent", "Utility setup", "Cleaning", "Time off work", "Buffer"]
EXAMPLE = [(1800, 1650, 500), (250, 0, 0), (180, 142, 142), (0, 0, 0), (300, 0, 0), (2400, 2400, 2400), (1100, 0, 0),
           (150, 75, 75), (200, 0, 0), (400, 0, 0), (420, 0, 0)]
UTILITIES = ["Electric", "Gas", "Water and sewer", "Trash and recycling", "Internet", "Phone", "Renter's or home insurance",
             "Streaming and subscriptions", "Mail forwarding (USPS)", "Other"]
NB = len(CATEGORIES)
B0 = 7


def build_moving(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "Moving Budget Sheet", "Plan the cost of the move, compare movers, and track every utility you need to stop or start.",
           ["On Setup, type the moving date and your total budget.",
            "On Budget, type an estimate for each cost, then the actual and what's paid as bills come in.",
            "On Quotes, compare up to three movers or truck rentals side by side.",
            "On Utilities, list what to stop at the old place and start at the new one, with dates and confirmation numbers."],
           [("Setup", "Moving date, from and to, total budget."),
            ("Budget", "Estimate vs actual vs paid for 11 moving costs, with a chart."),
            ("Quotes", "Three movers or truck rentals side by side."),
            ("Utilities", "Stop, start or transfer each service, with dates."),
            ("Planner paste", "Optional: paste the rows from our free moving cost calculator.")])

    st = S._sheet(wb, "Setup", "Setup", "Fill this in once. Change it any time.", widths={"B": 30, "C": 22})
    for r, (lab, val, fmt) in enumerate([("Moving date", today + timedelta(days=60), "mmm d, yyyy"),
                                         ("Moving from", "Apartment 4B (example)", None), ("Moving to", "12 Oak St (example)", None),
                                         ("Total moving budget", 7500, S.MONEY0)], start=5):
        S._label(st, f"B{r}", lab)
        S._inp(st[f"C{r}"], val, fmt)
    S._label(st, "B10", "Days to go")
    S._calc(st["C10"], "=MAX(0,C5-TODAY())", "0", bold=True)
    S._foot(st, 13)

    pp = S._sheet(wb, "Planner paste", "Paste from the moving cost calculator (optional)",
                  "Used our free moving cost calculator? Press its Copy rows button, click B7 here and paste.",
                  widths={"B": 26, "C": 13, "D": 13, "E": 13})
    S._header(pp, 6, ["Category", "Estimate", "Actual", "Paid"])
    for i in range(NB):
        for c in range(2, 6):
            S._inp(pp.cell(7 + i, c), None, None if c == 2 else S.MONEY0)
    pp[f"B{8 + NB}"] = ("Budget's Estimate, Actual and Paid cells read these rows by category name until you type over them.")
    pp[f"B{8 + NB}"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    S._foot(pp, 10 + NB)

    def paste(col: str, r: int) -> str:
        return (f"=IFERROR(N(INDEX('Planner paste'!${col}$7:${col}${6 + NB},"
                f"MATCH(B{r},'Planner paste'!$B$7:$B${6 + NB},0))),0)")

    bd = S._sheet(wb, "Budget", "Moving budget", "Type your numbers, or leave a cell blank to use the planner paste.",
                  widths={"B": 26, "C": 13, "D": 13, "E": 13, "F": 13, "G": 15, "H": 16})
    S._header(bd, B0 - 1, ["Category", "Estimate", "Actual", "Paid", "Still to pay", "Estimate minus actual", "Source"])
    last = B0 + NB - 1
    for i, cat in enumerate(CATEGORIES):
        r = B0 + i
        S._inp(bd.cell(r, 2), cat)
        for j, col in enumerate("CDE"):
            S._inp(bd[f"{col}{r}"], EXAMPLE[i][j], S.MONEY0)
            hc = "IJK"[j]   # hidden: the number used (typed, or the planner paste when the cell is blank)
            S._calc(bd[f"{hc}{r}"], f'=IF(ISNUMBER({col}{r}),{col}{r},{paste("CDE"[j], r)[1:]})', S.MONEY0)
        S._calc(bd[f"F{r}"], f"=MAX(0,J{r}-K{r})", S.MONEY0)
        S._calc(bd[f"G{r}"], f'=IF(J{r}=0,"",I{r}-J{r})', S.MONEY0)
        S._calc(bd[f"H{r}"], f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r}),ISNUMBER(E{r})),"Typed",IF(I{r}+J{r}+K{r}>0,"Planner paste","Typed"))')
    t = last + 1
    S._label(bd, f"B{t}", "Total")
    for c, h in zip("CDEFG", "IJKFG"):
        S._calc(bd[f"{c}{t}"], f"=SUM({h}{B0}:{h}{last})", S.MONEY0, bold=True)
    S._label(bd, f"B{t + 1}", "Budget left after estimates", bold=False)
    S._calc(bd[f"C{t + 1}"], f"=Setup!C8-C{t}", S.MONEY0)
    bd.conditional_formatting.add(f"G{B0}:G{last}", FormulaRule(formula=[f'AND(G{B0}<>"",G{B0}<0)'], fill=RED))
    bd.conditional_formatting.add(f"C{t + 1}", FormulaRule(formula=[f"C{t + 1}<0"], fill=RED))
    for col in "IJK":
        bd.column_dimensions[col].hidden = True
    S._foot(bd, t + 5)
    ch = BarChart()
    ch.type, ch.title, ch.height, ch.width = "bar", "Estimate vs actual", 8, 15
    ch.add_data(Reference(bd, min_col=3, max_col=4, min_row=B0 - 1, max_row=last), titles_from_data=True)
    ch.set_categories(Reference(bd, min_col=2, min_row=B0, max_row=last))
    ch.x_axis.scaling.orientation = "maxMin"
    ch.y_axis.number_format = '"$"#,##0'
    ch.series[0].graphicalProperties.solidFill = "DDD6C4"
    ch.series[1].graphicalProperties.solidFill = S.GREEN
    bd.add_chart(ch, "M5")

    q = S._sheet(wb, "Quotes", "Compare movers", "Up to three quotes side by side.", widths={"B": 28, "C": 18, "D": 18, "E": 18})
    S._header(q, 5, ["", "Quote 1", "Quote 2", "Quote 3"])
    lines = [("Company", ["Swift Movers (example)", "U-Move truck (example)", ""], None),
             ("Type (full service, labor only, truck)", ["Full service", "Truck only", ""], None),
             ("Date available", [today + timedelta(days=60), today + timedelta(days=60), None], "mmm d, yyyy"),
             ("Base price", [1650, 420, None], S.MONEY0), ("Packing and materials", [180, 0, None], S.MONEY0),
             ("Mileage or fuel", [0, 250, None], S.MONEY0), ("Stairs, long carry, heavy items", [120, 0, None], S.MONEY0),
             ("Insurance or valuation", [90, 35, None], S.MONEY0), ("Deposit required", [300, 0, None], S.MONEY0),
             ("USDOT number (interstate)", ["", "", ""], None), ("Reviews checked?", ["Yes", "Yes", ""], None)]
    for i, (lab, vals, fmt) in enumerate(lines):
        r = 6 + i
        S._label(q, f"B{r}", lab, bold=False)
        for j, v in enumerate(vals):
            S._inp(q.cell(r, 3 + j), v, fmt)
    r = 6 + len(lines)
    S._label(q, f"B{r}", "Total (base + extras)")
    for j, col in enumerate("CDE"):
        S._calc(q[f"{col}{r}"], f"=SUM({col}9:{col}13)", S.MONEY0, bold=True)
    S._label(q, f"B{r + 1}", "Cheapest", bold=False)
    S._calc(q[f"C{r + 1}"], f'=IF(COUNTIF(C{r}:E{r},">0")=0,"",INDEX(C6:E6,MATCH(SMALL(C{r}:E{r},COUNTIF(C{r}:E{r},0)+1),C{r}:E{r},0)))')
    S._foot(q, r + 4)

    u = S._sheet(wb, "Utilities", "Utilities and services", "Stop, start or transfer each one. Write the confirmation number.",
                 widths={"B": 26, "C": 18, "D": 13, "E": 18, "F": 13, "G": 12, "H": 18, "I": 6})
    S._header(u, 5, ["Service", "Old provider", "Stop on", "New provider", "Start on", "Deposit", "Confirmation #", "Done"])
    for i, svc in enumerate(UTILITIES + [""] * 4):
        r = 6 + i
        S._inp(u.cell(r, 2), svc or None)
        for c in range(3, 10):
            fmt = "mmm d, yyyy" if c in (4, 6) else S.MONEY0 if c == 7 else None
            S._inp(u.cell(r, c), None, fmt)
    S._list_validation(u, ["Yes", "No"], f"I6:I{5 + len(UTILITIES) + 4}")
    S._label(u, f"B{7 + len(UTILITIES) + 4}", "Deposits total")
    S._calc(u[f"G{7 + len(UTILITIES) + 4}"], f"=SUM(G6:G{5 + len(UTILITIES) + 4})", S.MONEY0, bold=True)
    S._foot(u, 10 + len(UTILITIES) + 4)

    wb.move_sheet("Planner paste", offset=len(wb.sheetnames))
    wb.save(path)
    return path


ST.SHEETS["moving-budget-sheet"] = ("Moving-Budget-Sheet.xlsx", build_moving)
