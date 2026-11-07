"""Google Sheets templates (also open in Excel and Numbers): budget, debt payoff, savings goals.

These are the template-only line: no guide, just a spreadsheet that is quick to start. They share the
house style of launch/products/sheets.py (yellow = input, white = calculated) and stick to functions that
Google Sheets imports cleanly from .xlsx: SUMIFS, SUMIF, INDEX/MATCH, EDATE, REPT, TODAY, NPER.
Every workbook opens on a Start tab and ships filled with fictional example data.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "products"))
import sheets as S  # noqa: E402  (launch/products/sheets.py)

RED = PatternFill("solid", fgColor="F8D7D3")
OK = PatternFill("solid", fgColor="D6F2E1")
BAR = Font(name="Inter", color=S.GREEN, bold=True)
GROUPS = ["Income", "Needs", "Wants", "Savings", "Debt"]


def _range_validation(ws, ref: str, rng: str):
    dv = DataValidation(type="list", formula1=ref, allow_blank=True)
    dv.error, dv.errorTitle = "Pick one from the list (add new ones on the setup tab).", "Not in the list"
    ws.add_data_validation(dv)
    dv.add(rng)


def _bar(cell, pct_ref: str, width: int = 15):
    cell.value = f'=IF({pct_ref}="","",REPT("█",ROUND(MIN({pct_ref},1)*{width},0)))'
    cell.font = BAR


def _start(wb: Workbook, title: str, intro: str, steps: list[str], tabs: list[tuple[str, str]], first=True):
    ws = wb.active if first else wb.create_sheet(index=0)
    ws.title = "Start"
    ws.sheet_properties.tabColor = S.INK
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 80
    ws["B2"] = "MONEY MADE SIMPLE"
    ws["B2"].font = Font(name="Inter", size=9, bold=True, color=S.GREEN)
    ws["B3"] = title
    ws["B3"].font = Font(name="Inter", size=22, bold=True, color=S.INK)
    ws["B4"] = intro
    ws["B4"].font = Font(name="Inter", size=11, color="4B5A51")
    ws["B6"] = "Start here (5 minutes)"
    ws["B6"].font = Font(name="Inter", size=13, bold=True)
    for i, step in enumerate(steps):
        r = 7 + i
        ws[f"B{r}"] = f"Step {i + 1}"
        ws[f"B{r}"].font = Font(name="Inter", bold=True, color=S.GREEN)
        ws[f"C{r}"] = step
        ws[f"C{r}"].alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 32
    r = 8 + len(steps)
    ws[f"B{r}"] = "The tabs"
    ws[f"B{r}"].font = Font(name="Inter", size=13, bold=True)
    for i, (tab, what) in enumerate(tabs):
        ws[f"B{r + 1 + i}"] = tab
        ws[f"B{r + 1 + i}"].font = Font(name="Inter", bold=True)
        ws[f"C{r + 1 + i}"] = what
    r = r + 2 + len(tabs)
    ws[f"B{r}"] = "Colour key"
    ws[f"B{r}"].font = Font(name="Inter", size=13, bold=True)
    S._inp(ws[f"B{r + 1}"], "Yellow")
    ws[f"C{r + 1}"] = "Your inputs. Type over the example data, or clear it (select the yellow cells, press Delete)."
    ws[f"B{r + 2}"] = "White"
    ws[f"C{r + 2}"] = "Calculates for you. Leave these alone and the sheet keeps working."
    ws[f"B{r + 4}"] = "Tips"
    ws[f"B{r + 4}"].font = Font(name="Inter", size=13, bold=True)
    tips = ["Google Sheets: this is your own copy. Nobody else can see it unless you share it.",
            "Excel or Numbers: open the .xlsx file from your download. Everything works the same.",
            "Phone: the Google Sheets app works, but setup is easier on a computer."]
    for i, t in enumerate(tips):
        ws[f"C{r + 5 + i}"] = t
    S._foot(ws, r + 9)
    return ws


# --------------------------------------------------------------------------------------------------
# 1. Monthly Budget Sheet
# --------------------------------------------------------------------------------------------------
BUDGET_CATS = [
    ("Paycheck", "Income", 3800), ("Side income", "Income", 300),
    ("Rent", "Needs", 1400), ("Utilities", "Needs", 180), ("Groceries", "Needs", 450),
    ("Transport", "Needs", 220), ("Insurance", "Needs", 140), ("Phone + internet", "Needs", 110),
    ("Eating out", "Wants", 160), ("Fun", "Wants", 120), ("Shopping", "Wants", 100), ("Subscriptions", "Wants", 45),
    ("Emergency fund", "Savings", 250), ("Sinking funds", "Savings", 150), ("Extra debt payment", "Debt", 200),
]
N_CATS, N_TX = 30, 500
CAT0, TX0 = 6, 6  # first data row on Setup / Transactions


def _budget_examples(month: date) -> list[tuple[date, str, str, float]]:
    """A believable month of fictional transactions."""
    y, m = month.year, month.month
    d = lambda day: date(y, m, day)  # noqa: E731
    return [
        (d(1), "Rent", "Rent", 1400), (d(1), "Paycheck", "Paycheck", 1900), (d(15), "Paycheck", "Paycheck", 1900),
        (d(3), "Electric + water", "Utilities", 96.4), (d(18), "Gas bill", "Utilities", 61.2),
        (d(2), "Grocery run", "Groceries", 112.35), (d(9), "Grocery run", "Groceries", 98.1),
        (d(16), "Grocery run", "Groceries", 121.6), (d(23), "Market", "Groceries", 44.8),
        (d(5), "Fuel", "Transport", 48), (d(19), "Fuel", "Transport", 51.5), (d(12), "Bus pass", "Transport", 64),
        (d(7), "Car + renters insurance", "Insurance", 140), (d(10), "Phone + internet", "Phone + internet", 110),
        (d(6), "Tacos with friends", "Eating out", 38.5), (d(14), "Pizza night", "Eating out", 31.2),
        (d(21), "Coffee + lunch", "Eating out", 54.9), (d(13), "Movie tickets", "Fun", 32),
        (d(20), "Concert", "Fun", 68), (d(8), "Shoes", "Shopping", 74.99), (d(4), "Streaming x2", "Subscriptions", 28.98),
        (d(11), "Music app", "Subscriptions", 11.99), (d(16), "Transfer to savings", "Emergency fund", 250),
        (d(16), "Gifts + car fund", "Sinking funds", 150), (d(17), "Extra on credit card", "Extra debt payment", 200),
        (d(22), "Freelance logo job", "Side income", 280),
    ]


def build_budget_sheet(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    this_month = date(today.year, today.month, 1)
    last_month = date((this_month - timedelta(days=1)).year, (this_month - timedelta(days=1)).month, 1)
    wb = Workbook()
    _start(wb, "Monthly Budget Sheet", "Plan every dollar, log what you spend, and see where the month stands.",
           ["On Setup, change the categories and monthly amounts to yours. Income goes in as Income.",
            "On Transactions, log what comes in and goes out: date, a few words, category, amount.",
            "On Dashboard, type any date to see that month: income, spending, and every category vs its budget.",
            "Once a month, look at Year to see the trend. Adjust next month's budget on Setup."],
           [("Setup", "Your categories, their group (Income / Needs / Wants / Savings / Debt) and monthly budget."),
            ("Transactions", "Everything you earn and spend. Amounts are always positive numbers."),
            ("Dashboard", "One month at a glance. Red = over budget."),
            ("Year", "Twelve months side by side, with a chart.")])

    # Setup
    st = S._sheet(wb, "Setup", "Setup: your categories and budget",
                  "Give every dollar of planned income a job. When 'Left to assign' is $0, the budget is done.",
                  widths={"B": 26, "C": 12, "D": 16, "E": 40})
    S._header(st, 5, ["Category", "Group", "Monthly budget", "Notes"])
    last = CAT0 + N_CATS - 1
    for i in range(N_CATS):
        r = CAT0 + i
        name, grp, amt = BUDGET_CATS[i] if i < len(BUDGET_CATS) else (None, None, None)
        S._inp(st.cell(r, 2), name)
        S._inp(st.cell(r, 3), grp)
        S._inp(st.cell(r, 4), amt, S.MONEY0)
        S._inp(st.cell(r, 5))
    S._list_validation(st, GROUPS, f"C{CAT0}:C{last}")
    t = last + 2
    rows = [("Planned income", f'=SUMIF(C{CAT0}:C{last},"Income",D{CAT0}:D{last})'),
            ("Planned spending, saving + debt", f'=SUM(D{CAT0}:D{last})-D{t}'),
            ("Left to assign", f"=D{t}-D{t + 1}")]
    for i, (lab, f) in enumerate(rows):
        S._label(st, f"B{t + i}", lab, bold=(i == 2))
        S._calc(st[f"D{t + i}"], f, S.MONEY0, bold=(i == 2))
    S._total_row(st, t + 2, 2, 4)
    st.conditional_formatting.add(f"D{t + 2}", CellIsRule(operator="notEqual", formula=["0"], fill=RED))
    st.conditional_formatting.add(f"D{t + 2}", CellIsRule(operator="equal", formula=["0"], fill=OK))
    st[f"B{t + 4}"] = "Over budget? Lower a Wants line first. Money left over? Give it a job: savings or extra debt payment."
    st[f"B{t + 4}"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    st.freeze_panes = f"B{CAT0}"
    S._foot(st, t + 6)
    cats = f"Setup!$B${CAT0}:$B${last}"
    grps = f"Setup!$C${CAT0}:$C${last}"

    # Transactions
    tx = S._sheet(wb, "Transactions", "Transactions", "Log money in and out. Pick the category from the list.",
                  widths={"B": 13, "C": 30, "D": 22, "E": 13, "F": 11, "G": 12})
    S._header(tx, 5, ["Date", "Description", "Category", "Amount", "Group", "Month"])
    tlast = TX0 + N_TX - 1
    ex = sorted(_budget_examples(last_month) + [t for t in _budget_examples(this_month) if t[0].day <= 17])
    for i in range(N_TX):
        r = TX0 + i
        row = ex[i] if i < len(ex) else (None,) * 4
        S._inp(tx.cell(r, 2), row[0], "mmm d, yyyy")
        S._inp(tx.cell(r, 3), row[1])
        S._inp(tx.cell(r, 4), row[2])
        S._inp(tx.cell(r, 5), row[3], S.MONEY)
        S._calc(tx.cell(r, 6), f'=IF(D{r}="","",IFERROR(INDEX({grps},MATCH(D{r},{cats},0)),"Not on Setup"))')
        S._calc(tx.cell(r, 7), f'=IF(ISNUMBER(B{r}),DATE(YEAR(B{r}),MONTH(B{r}),1),"")', "mmm yyyy")
    _range_validation(tx, cats, f"D{TX0}:D{tlast}")
    tx.conditional_formatting.add(f"F{TX0}:F{tlast}", CellIsRule(operator="equal", formula=['"Not on Setup"'], fill=RED))
    tx.freeze_panes = f"B{TX0}"
    S._foot(tx, tlast + 2)
    T = lambda col: f"Transactions!${col}${TX0}:${col}${tlast}"  # noqa: E731

    # Dashboard
    db = S._sheet(wb, "Dashboard", "Dashboard", "Type any date in the month you want to see.",
                  widths={"B": 26, "C": 17, "D": 15, "E": 15, "F": 16, "G": 9, "H": 20})
    S._label(db, "B5", "Month")
    S._inp(db["C5"], this_month, "mmmm yyyy")
    db["E5"], db["E6"] = "From", "Until"
    S._calc(db["F5"], "=DATE(YEAR(C5),MONTH(C5),1)", "mmm d, yyyy")
    S._calc(db["F6"], "=EDATE(F5,1)-1", "mmm d, yyyy")
    inmonth = f'{T("B")},">="&$F$5,{T("B")},"<="&$F$6'
    S._header(db, 8, ["This month", "Actual", "Planned", "% of income"])
    for i, g in enumerate(GROUPS):
        r = 9 + i
        S._label(db, f"B{r}", {"Debt": "Debt payments", "Income": "Income received"}.get(g, g), bold=False)
        S._calc(db[f"C{r}"], f'=SUMIFS({T("E")},{T("F")},"{g}",{inmonth})', S.MONEY0)
        S._calc(db[f"D{r}"], f'=SUMIF(Setup!$C${CAT0}:$C${last},"{g}",Setup!$D${CAT0}:$D${last})', S.MONEY0)
        if g != "Income":
            S._calc(db[f"E{r}"], f'=IF($C$9>0,C{r}/$C$9,"")', "0%")
    S._label(db, "B14", "Left over this month")
    S._calc(db["C14"], "=C9-SUM(C10:C13)", S.MONEY0, bold=True)
    S._calc(db["D14"], "=D9-SUM(D10:D13)", S.MONEY0, bold=True)
    S._total_row(db, 14, 2, 5)
    db.conditional_formatting.add("C14", CellIsRule(operator="lessThan", formula=["0"], fill=RED))
    db["B15"] = "% of income shows your split. A common starting point is about 50% needs, 30% wants, 20% savings + debt."
    db["B15"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    S._header(db, 17, ["Category", "Group", "Budget", "Actual", "Budget - actual", "Used", ""])
    for i in range(N_CATS):
        r, sr = 18 + i, CAT0 + i
        S._calc(db.cell(r, 2), f'=IF(Setup!B{sr}="","",Setup!B{sr})')
        S._calc(db.cell(r, 3), f'=IF(B{r}="","",Setup!C{sr})')
        S._calc(db.cell(r, 4), f'=IF(B{r}="","",N(Setup!D{sr}))', S.MONEY0)
        S._calc(db.cell(r, 5), f'=IF(B{r}="","",SUMIFS({T("E")},{T("D")},B{r},{inmonth}))', S.MONEY)
        S._calc(db.cell(r, 6), f'=IF(B{r}="","",D{r}-E{r})', S.MONEY)
        S._calc(db.cell(r, 7), f'=IF(OR(B{r}="",N(D{r})=0),"",E{r}/D{r})', "0%")
        _bar(db.cell(r, 8), f"G{r}", 12)
    dl = 18 + N_CATS - 1
    db.conditional_formatting.add(f"F18:F{dl}", FormulaRule(formula=['AND(C18<>"Income",N(F18)<0)'], fill=RED))
    db.conditional_formatting.add(f"H18:H{dl}", FormulaRule(formula=['AND(C18<>"Income",N(G18)>1)'],
                                                            font=Font(color="C0392B", bold=True)))
    db.freeze_panes = "B9"
    S._foot(db, dl + 2)

    # Year
    yr = S._sheet(wb, "Year", "The year", "Every category, month by month. The year comes from the Dashboard month.",
                  widths={"B": 24, "C": 11, **{chr(68 + i): 10 for i in range(12)}, "P": 12})
    S._label(yr, "B5", "Year")
    S._calc(yr["C5"], "=YEAR(Dashboard!C5)", "0", bold=True)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    S._header(yr, 7, ["Category", "Group"] + months + ["Total"])
    for i in range(N_CATS):
        r, sr = 8 + i, CAT0 + i
        S._calc(yr.cell(r, 2), f'=IF(Setup!B{sr}="","",Setup!B{sr})')
        S._calc(yr.cell(r, 3), f'=IF(B{r}="","",Setup!C{sr})')
        for m in range(12):
            frm = f"DATE($C$5,{m + 1},1)"
            S._calc(yr.cell(r, 4 + m), f'=IF($B{r}="","",SUMIFS({T("E")},{T("D")},$B{r},{T("B")},">="&{frm},'
                                       f'{T("B")},"<="&(EDATE({frm},1)-1)))', S.MONEY0)
        S._calc(yr.cell(r, 16), f'=IF(B{r}="","",SUM(D{r}:O{r}))', S.MONEY0)
    yl = 8 + N_CATS - 1
    g0 = yl + 2
    labels = GROUPS + ["Spending (needs + wants)", "Left over"]
    for i, g in enumerate(labels):
        r = g0 + i
        yr.cell(r, 2, "Totals" if i == 0 else None)
        S._label(yr, f"C{r}", g)
        for m in range(13):
            col = 4 + m
            L = yr.cell(r, col).column_letter
            if g in GROUPS:
                f = f'=SUMIF($C$8:$C${yl},"{g}",{L}$8:{L}${yl})'
            elif g.startswith("Spending"):
                f = f"={L}{g0 + 1}+{L}{g0 + 2}"
            else:
                f = f"={L}{g0}-SUM({L}{g0 + 1}:{L}{g0 + 4})"
            S._calc(yr.cell(r, col), f, S.MONEY0, bold=True)
        S._total_row(yr, r, 2, 16)
    ch = BarChart()
    ch.title, ch.height, ch.width = "Income vs spending", 8, 22
    ch.y_axis.numFmt = '"$"#,##0'
    ch.add_data(Reference(yr, min_col=3, max_col=15, min_row=g0, max_row=g0), from_rows=True, titles_from_data=True)
    ch.add_data(Reference(yr, min_col=3, max_col=15, min_row=g0 + 5, max_row=g0 + 5), from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(yr, min_col=4, max_col=15, min_row=7))
    ch.series[0].graphicalProperties.solidFill = S.GREEN
    ch.series[1].graphicalProperties.solidFill = S.GOLD
    yr.add_chart(ch, f"B{g0 + 9}")
    yr.freeze_panes = "D8"
    S._foot(yr, g0 + 27)
    wb.move_sheet("Dashboard", offset=-2)  # Start, Dashboard, Setup, Transactions, Year
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 2. Savings Goals Sheet
# --------------------------------------------------------------------------------------------------
N_GOALS, N_DEP = 15, 500
GOAL0, DEP0 = 6, 6


def _savings_examples(today: date):
    y = today.year
    goals = [("Emergency fund", "Emergency fund", 6000, date(y + 1, 12, 1), 1800),
             ("Car repairs", "Sinking fund", 1200, date(y + 1, 6, 1), 300),
             ("Holiday gifts", "Sinking fund", 600, date(y, 12, 15), 250),
             ("Summer trip", "Goal", 2400, date(y + 1, 7, 1), 0),
             ("New laptop", "Goal", 1100, date(y + 1, 3, 1), 200),
             ("Car insurance (yearly)", "Sinking fund", 900, date(y + 1, 9, 1), 150)]
    per = {"Emergency fund": 250, "Car repairs": 75, "Holiday gifts": 60, "Summer trip": 150, "New laptop": 100,
           "Car insurance (yearly)": 75}
    deps = []
    for back in (3, 2, 1, 0):
        m = today.month - back
        yy = y + (m - 1) // 12
        mm = (m - 1) % 12 + 1
        for g, amt in per.items():
            deps.append((date(yy, mm, 16), g, amt, "Payday transfer"))
    lm = date(today.year, today.month, 1) - timedelta(days=1)
    deps.append((lm.replace(day=22), "Car repairs", -180, "New tyre (withdrawal)"))
    return goals, sorted(deps)


def build_savings_sheet(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "Savings Goals Sheet", "Every goal, sinking fund and your emergency fund in one place, with what to save each month.",
           ["On Goals, list what you're saving for: the target, the date you want it by, and what you already have.",
            "Each time you move money to savings, add a line on Deposits (a withdrawal is a negative amount).",
            "Goals shows how much is saved, what's left and how much a month gets you there on time.",
            "On Emergency Fund, list your essential monthly costs to see how many months you're covered."],
           [("Goals", "Up to 15 goals. Type = Goal, Sinking fund (yearly or irregular costs) or Emergency fund."),
            ("Deposits", "Every transfer in or out, linked to a goal."),
            ("Emergency Fund", "How big yours should be, and how many months it covers today.")])
    g = S._sheet(wb, "Goals", "Savings goals", "Saved = already saved + deposits. 'Needed / month' gets you there by the date.",
                 widths={"B": 24, "C": 15, "D": 12, "E": 13, "F": 13, "G": 12, "H": 12, "I": 12, "J": 9, "K": 14,
                         "L": 12, "M": 14})
    S._header(g, 5, ["Goal", "Type", "Target", "Target date", "Already saved", "Deposits", "Saved", "Left",
                     "Progress", "", "Months left", "Needed / month"])
    goals, deps = _savings_examples(today)
    gl = GOAL0 + N_GOALS - 1
    D = lambda col: f"Deposits!${col}${DEP0}:${col}${DEP0 + N_DEP - 1}"  # noqa: E731
    for i in range(N_GOALS):
        r = GOAL0 + i
        row = goals[i] if i < len(goals) else (None,) * 5
        S._inp(g.cell(r, 2), row[0])
        S._inp(g.cell(r, 3), row[1])
        S._inp(g.cell(r, 4), row[2], S.MONEY0)
        S._inp(g.cell(r, 5), row[3], "mmm yyyy")
        S._inp(g.cell(r, 6), row[4], S.MONEY0)
        S._calc(g.cell(r, 7), f'=IF(B{r}="","",SUMIF({D("C")},B{r},{D("D")}))', S.MONEY0)
        S._calc(g.cell(r, 8), f'=IF(B{r}="","",N(F{r})+G{r})', S.MONEY0)
        S._calc(g.cell(r, 9), f'=IF(B{r}="","",MAX(0,N(D{r})-H{r}))', S.MONEY0)
        S._calc(g.cell(r, 10), f'=IF(OR(B{r}="",N(D{r})=0),"",MIN(1,H{r}/D{r}))', "0%")
        _bar(g.cell(r, 11), f"J{r}", 10)
        S._calc(g.cell(r, 12), f'=IF(OR(B{r}="",NOT(ISNUMBER(E{r}))),"",IF(I{r}=0,"Done",IF(E{r}<=TODAY(),"Date passed",'
                               f'MAX(1,(YEAR(E{r})-YEAR(TODAY()))*12+MONTH(E{r})-MONTH(TODAY())))))', "0")
        S._calc(g.cell(r, 13), f'=IF(ISNUMBER(L{r}),I{r}/L{r},IF(L{r}="Done",0,""))', S.MONEY0)
    S._list_validation(g, ["Goal", "Sinking fund", "Emergency fund"], f"C{GOAL0}:C{gl}")
    t = gl + 1
    S._label(g, f"B{t}", "Total")
    for col in "DFGHIM":
        S._calc(g[f"{col}{t}"], f"=SUM({col}{GOAL0}:{col}{gl})", S.MONEY0, bold=True)
    S._calc(g[f"J{t}"], f'=IF(D{t}>0,H{t}/D{t},"")', "0%", bold=True)
    S._total_row(g, t, 2, 13)
    g.conditional_formatting.add(f"L{GOAL0}:L{gl}", CellIsRule(operator="equal", formula=['"Date passed"'], fill=RED))
    g.conditional_formatting.add(f"L{GOAL0}:L{gl}", CellIsRule(operator="equal", formula=['"Done"'], fill=OK))
    g[f"B{t + 2}"] = (f"Your monthly savings plan: the total of 'Needed / month'. Too high? Push a date back or lower a "
                      f"target. A 'Date passed' goal needs a new date.")
    g[f"B{t + 2}"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    ch = BarChart()
    ch.type, ch.title, ch.height, ch.width = "bar", "Saved vs target", 8, 16
    ch.add_data(Reference(g, min_col=8, min_row=5, max_row=GOAL0 + len(goals) - 1), titles_from_data=True)
    ch.add_data(Reference(g, min_col=4, min_row=5, max_row=GOAL0 + len(goals) - 1), titles_from_data=True)
    ch.set_categories(Reference(g, min_col=2, min_row=GOAL0, max_row=GOAL0 + len(goals) - 1))
    ch.series[0].graphicalProperties.solidFill = S.GREEN
    ch.series[1].graphicalProperties.solidFill = "D9D3C3"
    g.add_chart(ch, f"B{t + 4}")
    g.freeze_panes = f"C{GOAL0}"
    S._foot(g, t + 22)

    dp = S._sheet(wb, "Deposits", "Deposits", "Every move into (or out of) savings. Withdrawals are negative.",
                  widths={"B": 13, "C": 26, "D": 13, "E": 32})
    S._header(dp, 5, ["Date", "Goal", "Amount", "Note"])
    for i in range(N_DEP):
        r = DEP0 + i
        row = deps[i] if i < len(deps) else (None,) * 4
        S._inp(dp.cell(r, 2), row[0], "mmm d, yyyy")
        S._inp(dp.cell(r, 3), row[1])
        S._inp(dp.cell(r, 4), row[2], S.MONEY)
        S._inp(dp.cell(r, 5), row[3])
    _range_validation(dp, f"Goals!$B${GOAL0}:$B${gl}", f"C{DEP0}:C{DEP0 + N_DEP - 1}")
    dp.conditional_formatting.add(f"D{DEP0}:D{DEP0 + N_DEP - 1}", CellIsRule(operator="lessThan", formula=["0"],
                                                                             font=Font(color="C0392B")))
    dp.freeze_panes = f"B{DEP0}"
    S._foot(dp, DEP0 + N_DEP + 1)

    ef = S._sheet(wb, "Emergency Fund", "Emergency fund", "Essentials only: what you'd still have to pay if your income stopped.",
                  widths={"B": 40, "C": 14, "D": 50})
    S._header(ef, 5, ["Essential monthly cost", "Amount"])
    ess = [("Rent or mortgage", 1400), ("Utilities", 180), ("Groceries", 400), ("Insurance", 140),
           ("Transport", 180), ("Phone + internet", 80), ("Minimum debt payments", 300), ("Other must-pays", 50)]
    for i in range(10):
        r = 6 + i
        row = ess[i] if i < len(ess) else (None, None)
        S._inp(ef.cell(r, 2), row[0])
        S._inp(ef.cell(r, 3), row[1], S.MONEY0)
    S._label(ef, "B16", "Essentials per month")
    S._calc(ef["C16"], "=SUM(C6:C15)", S.MONEY0, bold=True)
    S._total_row(ef, 16, 2, 3)
    S._label(ef, "B18", "Months you want covered", bold=False)
    S._inp(ef["C18"], 3, "0")
    ef["D18"] = "Many people start with 1 month, then build to 3 to 6. Pick what helps you sleep."
    ef["D18"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    out = [("Your emergency fund target", "=C16*C18", S.MONEY0),
           ("Saved now (Emergency fund goals)", f'=SUMIF(Goals!$C${GOAL0}:$C${gl},"Emergency fund",Goals!$H${GOAL0}:$H${gl})', S.MONEY0),
           ("Months covered today", '=IF(C16>0,C20/C16,"")', "0.0"),
           ("Still to save", "=MAX(0,C19-C20)", S.MONEY0)]
    for i, (lab, f, fmt) in enumerate(out):
        r = 19 + i
        S._label(ef, f"B{r}", lab, bold=(i in (0, 2)))
        S._calc(ef[f"C{r}"], f, fmt, bold=(i in (0, 2)))
    S._total_row(ef, 21, 2, 3)
    ef["D19"] = "Tip: set the Emergency fund goal's target on Goals to this number."
    ef["D19"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    S._foot(ef, 25)
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 3. Debt Payoff Sheet (the Debt-Free Date Planner engine, template-only, plus a payment log)
# --------------------------------------------------------------------------------------------------
N_PAY = 300


def build_debt_sheet(path: Path, today: date | None = None) -> Path:
    def hook(wb: Workbook, plan_total: int):
        _start(wb, "Debt Payoff Sheet", "Snowball or avalanche: see your debt-free date, then log payments and watch balances fall.",
               ["On Plan, list each debt: balance, APR and minimum payment (from your statements or app).",
                "Pick a method and how much extra you can pay each month. Your debt-free date updates instantly.",
                "Every time you pay, add a line on Payments: the amount, and the interest shown on your statement.",
                "Once a month, type your total balance on Progress to see if you're ahead of the plan."],
               [("Plan", "Your debts, the method (Avalanche / Snowball / Custom), extra payment and debt-free date."),
                ("Payments", "Your payment log, with the balance each debt has left."),
                ("Progress", "Plan vs actual each month, with a chart."),
                ("Schedule", "The month-by-month maths. No inputs here.")], first=False)
        p = wb.create_sheet("Payments", index=2)
        p.sheet_properties.tabColor = S.GREEN
        p.sheet_view.showGridLines = False
        for col, w in {"A": 2, "B": 13, "C": 20, "D": 12, "E": 12, "F": 12, "G": 16, "H": 3, "I": 20, "J": 13,
                       "K": 13, "L": 13, "M": 13, "N": 15}.items():
            p.column_dimensions[col].width = w
        p["B1"] = "Payments"
        p["B1"].font = Font(name="Inter", size=18, bold=True, color=S.INK)
        p["B2"] = "Log every payment. Interest comes from your statement; principal = what actually came off the balance."
        p["B2"].font = Font(name="Inter", size=10, color="4B5A51")
        p["B3"] = "Yellow cells = your inputs. White cells calculate automatically. Example data shown; type over it."
        p["B3"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
        S._header(p, 5, ["Date", "Debt", "Paid", "Interest", "Principal", "Note"])
        first_m = date(2026, 12, 1)
        ex = [("Store card", 35 + 200, 22.49), ("Credit card", 105, 87.15), ("Personal loan", 75, 16.5),
              ("Car loan", 210, 42.79), ("Student loan", 180, 64.17)]
        pl = 6 + N_PAY - 1
        for i in range(N_PAY):
            r = 6 + i
            row = ex[i] if i < len(ex) else (None, None, None)
            S._inp(p.cell(r, 2), first_m.replace(day=5 + 3 * i) if i < len(ex) else None, "mmm d, yyyy")
            S._inp(p.cell(r, 3), row[0])
            S._inp(p.cell(r, 4), row[1], S.MONEY)
            S._inp(p.cell(r, 5), row[2], S.MONEY)
            S._calc(p.cell(r, 6), f'=IF(N(D{r})=0,"",D{r}-N(E{r}))', S.MONEY)
            S._inp(p.cell(r, 7))
        _range_validation(p, "Plan!$B$10:$B$19", f"C6:C{pl}")
        S._header(p, 5, ["Debt", "Starting balance", "Paid so far", "Interest paid", "Principal paid", "Balance now (est.)"], col=9)
        for k in range(10):
            r, pr = 6 + k, 10 + k
            S._calc(p.cell(r, 9), f'=IF(Plan!B{pr}="","",Plan!B{pr})')
            S._calc(p.cell(r, 10), f'=IF(I{r}="","",N(Plan!C{pr}))', S.MONEY0)
            for col, src in ((11, "D"), (12, "E"), (13, "F")):
                S._calc(p.cell(r, col), f'=IF(I{r}="","",SUMIF($C$6:$C${pl},I{r},${src}$6:${src}${pl}))', S.MONEY)
            S._calc(p.cell(r, 14), f'=IF(I{r}="","",MAX(0,J{r}-M{r}))', S.MONEY, bold=True)
        S._label(p, "I16", "Total")
        for col in "JKLMN":
            S._calc(p[f"{col}16"], f"=SUM({col}6:{col}15)", S.MONEY0, bold=True)
        S._total_row(p, 16, 9, 14)
        p["I18"] = "Balance now = starting balance minus principal paid. Check it against your statement now and then."
        p["I18"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
        p.freeze_panes = "B6"
        S._foot(p, pl + 2)

    return S.build_debt_planner(path, extras=False, hook=hook)


SHEETS = {
    "budget-sheet": ("Monthly-Budget-Sheet.xlsx", build_budget_sheet),
    "debt-payoff-sheet": ("Debt-Payoff-Sheet.xlsx", build_debt_sheet),
    "savings-goals-sheet": ("Savings-Goals-Sheet.xlsx", build_savings_sheet),
}


def _budget_2027(path: Path, today: date | None = None) -> Path:
    import sheets_2027
    return sheets_2027.build_budget_2027(path, today)


SHEETS["budget-sheet-2027"] = ("2027-Budget-Sheet.xlsx", _budget_2027)
import twins_sheets  # noqa: E402,F401  (registers the five printable twins in SHEETS)
import wedding_sheet  # noqa: E402,F401  (registers the Wedding Budget Sheet in SHEETS)
