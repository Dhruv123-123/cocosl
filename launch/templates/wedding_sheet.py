"""Wedding Budget Sheet for Google Sheets (also opens in Excel and Numbers).

Scouting's competitor-product-gaps.md (PR #2): wedding budget spreadsheets are a top seller and we had no life-event
budget. Tabs: Start, Setup (total budget, date, who's chipping in), Budget (planned vs actual vs paid by category),
Payments (every vendor payment with its due date, paid or not, and who's paying), Due by month (the payment-due
calendar for the next 12 months), Who's paying, Guests (RSVPs and headcount) and Dashboard. Same house style as the
other sheets: yellow = input, white = calculated, fictional example data, and only functions Google Sheets imports
cleanly (SUMIFS, COUNTIFS, SUMPRODUCT, EDATE, TODAY). Conditional formatting stays on its own tab.

Meant to pair with the apps thread's wedding planner tool: the categories and the Payments columns are listed in
CATEGORIES and PAY_COLUMNS so a CSV from the tool can be pasted into Payments.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font, PatternFill

import sheets_templates as ST
from sheets_templates import OK, RED, S, _start

SOON = PatternFill("solid", fgColor="FFF1C9")
CATEGORIES = ["Venue", "Catering", "Bar and drinks", "Photography", "Videography", "Attire", "Hair and makeup",
              "Flowers and decor", "Music and DJ", "Cake and desserts", "Invitations and stationery", "Rings", "Transportation",
              "Favors", "Officiant and license", "Rentals", "Planner or coordinator", "Gifts", "Honeymoon", "Buffer for extras"]
# Same labels and order as the apps thread's wedding planner (PR #8, apps/budget/lib/wedding.js), so its "Copy rows"
# paste (Category, Budget, Actual, Paid; tab-separated, 20 rows, no header) lines up on the Planner paste tab.
PAYERS = ["Us", "Family 1", "Family 2", "Other"]
PAY_COLUMNS = ["Vendor", "Category", "What for", "Amount", "Due date", "Paid?", "Paid on", "Who's paying", "Notes"]
B0, NB = 7, len(CATEGORIES)          # Budget rows
P0, NP = 7, 80                       # Payments rows
G0, NG = 7, 150                      # Guests rows
PLAN = [9000, 7800, 1500, 3200, 0, 2100, 500, 1700, 1200, 600, 450, 1500, 300, 250, 150, 400, 0, 300, 0, 1050]


def _payments(today: date, wedding: date) -> list[tuple]:
    d = lambda days: today + timedelta(days=days)  # noqa: E731
    return [
        ("Willow Barn (example)", "Venue", "Deposit", 3000, d(-120), "Yes", d(-121), "Us"),
        ("Willow Barn (example)", "Venue", "Second payment", 3000, d(-10), "Yes", d(-12), "Family 1"),
        ("Willow Barn (example)", "Venue", "Final payment", 3200, wedding - timedelta(days=30), "No", None, "Family 1"),
        ("Green Table Catering (example)", "Catering", "Deposit", 2000, d(-60), "Yes", d(-60), "Us"),
        ("Green Table Catering (example)", "Catering", "Balance (final headcount)", 5900, wedding - timedelta(days=14), "No", None, "Family 2"),
        ("Bright Lens Photo (example)", "Photography", "Retainer", 1000, d(-90), "Yes", d(-90), "Us"),
        ("Bright Lens Photo (example)", "Photography", "Balance", 2300, wedding - timedelta(days=21), "No", None, "Us"),
        ("Bridal shop (example)", "Attire", "Dress", 1400, d(-30), "Yes", d(-30), "Us"),
        ("Tailor (example)", "Attire", "Alterations", 350, d(20), "No", None, "Us"),
        ("Bloom Co (example)", "Flowers + decor", "Deposit", 500, d(-5), "No", None, "Us"),
        ("DJ Sam (example)", "Music + DJ", "Booking", 1200, d(12), "No", None, "Family 2"),
        ("Print shop (example)", "Invitations and stationery", "Invitations", 380, d(-15), "Yes", d(-15), "Us"),
        ("Jeweler (example)", "Rings", "Two bands", 1350, d(45), "No", None, "Us"),
    ]


GUESTS = [("Ana + Luis (example)", "Side 1", 2, "Yes", "Chicken"), ("Grandma Ruth (example)", "Side 2", 1, "Yes", "Fish"),
          ("The Parkers (example)", "Side 2", 4, "Invited", ""), ("Jordan (example)", "Side 1", 2, "No", ""),
          ("Priya (example)", "Side 1", 1, "Yes", "Vegetarian"), ("Uncle Mo (example)", "Side 2", 2, "Invited", "")]


def build_wedding(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wedding = today + timedelta(days=150)
    wb = Workbook()
    _start(wb, "Wedding Budget Sheet", "Plan the wedding budget, track every vendor payment and its due date, and see who's paying for what.",
           ["On Setup, type your total budget, the date, and who's chipping in (and how much).",
            "On Budget, type what you plan to spend in each category. Actual and Paid fill in from Payments.",
            "On Payments, add every deposit and balance with its due date. Pick Yes when it's paid. Overdue turns red; due in the next 30 days turns yellow.",
            "Due by month shows what's due in each of the next 12 months. Guests counts your RSVPs for the cost per guest."],
           [("Setup", "Total budget, wedding date, who's paying."),
            ("Budget", "Planned vs actual vs paid, by category."),
            ("Payments", "Every vendor payment: amount, due date, paid?, who's paying."),
            ("Due by month", "The payment calendar for the next 12 months."),
            ("Who's paying", "Each person's promise vs what they've covered."),
            ("Guests", "RSVPs, party size and meals."),
            ("Planner paste", "Optional: paste the rows from our free wedding budget planner."),
            ("Dashboard", "The whole picture on one screen.")])

    st = S._sheet(wb, "Setup", "Setup", "Fill this in once. Change it any time.", widths={"B": 30, "C": 18, "D": 4, "E": 22, "F": 16})
    S._label(st, "B5", "Total wedding budget")
    S._inp(st["C5"], 32000, S.MONEY0)
    S._label(st, "B6", "Wedding date")
    S._inp(st["C6"], wedding, "mmm d, yyyy")
    S._label(st, "B7", "Guests you're planning for")
    S._inp(st["C7"], 90, "0")
    S._label(st, "E5", "Who's chipping in")
    S._header(st, 6, ["Name", "Amount promised"], col=5)
    promised = [14000, 10000, 8000, 0]
    for i, (n, a) in enumerate(zip(PAYERS, promised)):
        S._inp(st.cell(7 + i, 5), n)
        S._inp(st.cell(7 + i, 6), a, S.MONEY0)
    S._label(st, "E11", "Total promised")
    S._calc(st["F11"], "=SUM(F7:F10)", S.MONEY0, bold=True)
    S._calc(st["E12"], '=IF(F11<C5,"Promised is "&TEXT(C5-F11,"$#,##0")&" short of the budget","Promised covers the budget")')
    S._foot(st, 15)

    pay_last = P0 + NP - 1
    R = lambda c: f"Payments!${c}${P0}:${c}${pay_last}"  # noqa: E731

    pp = S._sheet(wb, "Planner paste", "Paste from the wedding planner tool (optional)",
                  "Used our free wedding budget planner? Press its Copy rows button, click B7 here and paste.",
                  widths={"B": 26, "C": 13, "D": 13, "E": 13})
    S._header(pp, 6, ["Category", "Budget", "Actual", "Paid"])
    for i in range(NB):
        for c in range(2, 6):
            S._inp(pp.cell(7 + i, c), None, None if c == 2 else S.MONEY0)
    pp["B28"] = ("Budget fills any blank Planned cell on Budget. Actual and Paid are used for a category until you add its "
                 "payments on Payments. Categories match by name.")
    pp["B28"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    S._foot(pp, 30)
    PP = lambda col, r: (f"IFERROR(INDEX('Planner paste'!${col}$7:${col}${6 + NB},"  # noqa: E731
                         f"MATCH(B{r},'Planner paste'!$B$7:$B${6 + NB},0)),0)")

    bd = S._sheet(wb, "Budget", "Budget by category", "Type the plan. Booked and Paid come from Payments (or the planner paste).",
                  widths={"B": 26, "C": 13, "D": 13, "E": 13, "F": 13, "G": 13, "H": 10, "I": 4})
    S._header(bd, B0 - 1, ["Category", "Planned", "Booked", "Paid", "Still owed", "Planned minus booked", "% of budget"])
    bl = B0 + NB - 1
    for i, cat in enumerate(CATEGORIES):
        r = B0 + i
        S._inp(bd.cell(r, 2), cat)
        S._inp(bd.cell(r, 3), PLAN[i], S.MONEY0)
        has = f'COUNTIF({R("C")},B{r})>0'
        S._calc(bd.cell(r, 4), f'=IF({has},SUMIF({R("C")},B{r},{R("E")}),N({PP("D", r)}))', S.MONEY0)
        S._calc(bd.cell(r, 5), f'=IF({has},SUMIFS({R("E")},{R("C")},B{r},{R("G")},"Yes"),N({PP("E", r)}))', S.MONEY0)
        S._calc(bd.cell(r, 6), f"=D{r}-E{r}", S.MONEY0)
        S._calc(bd.cell(r, 9), f'=IF(ISNUMBER(C{r}),C{r},N({PP("C", r)}))', S.MONEY0)   # plan used (hidden)
        S._calc(bd.cell(r, 7), f"=I{r}-D{r}", S.MONEY0)
        S._calc(bd.cell(r, 8), f"=IF(Setup!$C$5>0,I{r}/Setup!$C$5,0)", "0%")
    t = bl + 1
    S._label(bd, f"B{t}", "Total")
    S._calc(bd[f"C{t}"], f"=SUM(I{B0}:I{bl})", S.MONEY0, bold=True)
    for c in "DEFG":
        S._calc(bd[f"{c}{t}"], f"=SUM({c}{B0}:{c}{bl})", S.MONEY0, bold=True)
    S._calc(bd[f"H{t}"], f"=IF(Setup!$C$5>0,C{t}/Setup!$C$5,0)", "0%", bold=True)
    S._label(bd, f"B{t + 1}", "Budget left to plan", bold=False)
    S._calc(bd[f"C{t + 1}"], f"=Setup!C5-C{t}", S.MONEY0)
    bd.column_dimensions["I"].hidden = True
    bd.conditional_formatting.add(f"G{B0}:G{bl}", FormulaRule(formula=[f"G{B0}<0"], fill=RED))
    bd.freeze_panes = f"C{B0}"
    S._foot(bd, t + 3)

    pm = S._sheet(wb, "Payments", "Payments", "One row per payment: deposits, balances, tips. Red = overdue. Yellow = due in 30 days.",
                  widths={"B": 28, "C": 22, "D": 22, "E": 12, "F": 13, "G": 8, "H": 13, "I": 14, "J": 26})
    S._header(pm, P0 - 1, PAY_COLUMNS)
    rows = _payments(today, wedding)
    for i in range(NP):
        r = P0 + i
        row = rows[i] if i < len(rows) else (None,) * 8
        for c, (v, fmt) in enumerate(zip(row, (None, None, None, S.MONEY0, "mmm d, yyyy", None, "mmm d, yyyy", None)), start=2):
            S._inp(pm.cell(r, c), v, fmt)
        S._inp(pm.cell(r, 10))
    S._list_validation(pm, ["Yes", "No"], f"G{P0}:G{pay_last}")
    ST._range_validation(pm, f"Budget!$B${B0}:$B${bl}", f"C{P0}:C{pay_last}")
    ST._range_validation(pm, "Setup!$E$7:$E$10", f"I{P0}:I{pay_last}")
    pm.conditional_formatting.add(f"B{P0}:J{pay_last}", FormulaRule(
        formula=[f'AND($E{P0}<>"",$G{P0}<>"Yes",ISNUMBER($F{P0}),$F{P0}<TODAY())'], fill=RED))
    pm.conditional_formatting.add(f"B{P0}:J{pay_last}", FormulaRule(
        formula=[f'AND($E{P0}<>"",$G{P0}<>"Yes",ISNUMBER($F{P0}),$F{P0}>=TODAY(),$F{P0}<=TODAY()+30)'], fill=SOON))
    pm.conditional_formatting.add(f"G{P0}:G{pay_last}", FormulaRule(formula=[f'G{P0}="Yes"'], fill=OK))
    pm.freeze_panes = f"C{P0}"
    S._foot(pm, pay_last + 2)

    du = S._sheet(wb, "Due by month", "Payments due by month", "Unpaid payments, by the month they're due. Overdue ones are in the first row.",
                  widths={"B": 16, "C": 12, "D": 14, "E": 16})
    S._header(du, 5, ["Month", "Payments", "Amount due", "Running total"])
    du["B6"] = "Overdue"
    du["B6"].font = Font(name="Inter", bold=True, color="B3261E")
    S._calc(du["C6"], f'=COUNTIFS({R("G")},"<>Yes",{R("F")},"<"&TODAY(),{R("E")},">0")', "0")
    S._calc(du["D6"], f'=SUMIFS({R("E")},{R("G")},"<>Yes",{R("F")},"<"&TODAY())', S.MONEY0)
    S._calc(du["E6"], "=D6", S.MONEY0)
    for k in range(12):
        r = 7 + k
        start = f"DATE(YEAR(TODAY()),MONTH(TODAY())+{k},1)"
        frm = f"MAX(TODAY(),{start})" if k == 0 else start
        S._calc(du.cell(r, 2), f"={start}", "mmm yyyy")
        cond = f'{R("G")},"<>Yes",{R("F")},">="&{frm},{R("F")},"<"&EDATE({start},1)'
        S._calc(du.cell(r, 3), f'=COUNTIFS({cond},{R("E")},">0")', "0")
        S._calc(du.cell(r, 4), f"=SUMIFS({R('E')},{cond})", S.MONEY0)
        S._calc(du.cell(r, 5), f"=E{r - 1}+D{r}", S.MONEY0)
    du.conditional_formatting.add("B6:E6", FormulaRule(formula=["$C$6>0"], fill=RED))
    ch = BarChart()
    ch.title, ch.height, ch.width = "Due each month", 7.5, 16
    ch.add_data(Reference(du, min_col=4, min_row=5, max_row=18), titles_from_data=True)
    ch.set_categories(Reference(du, min_col=2, min_row=6, max_row=18))
    ch.series[0].graphicalProperties.solidFill = S.GREEN
    du.add_chart(ch, "G5")
    S._foot(du, 21)

    wp = S._sheet(wb, "Who's paying", "Who's paying", "Each person's promise from Setup against the payments assigned to them.",
                  widths={"B": 18, "C": 15, "D": 15, "E": 15, "F": 15, "G": 18})
    S._header(wp, 5, ["Name", "Promised", "Assigned", "Paid so far", "Still to pay", "Promise left over"])
    for i in range(4):
        r, sr = 6 + i, 7 + i
        S._calc(wp.cell(r, 2), f'=IF(Setup!E{sr}="","",Setup!E{sr})')
        S._calc(wp.cell(r, 3), f"=N(Setup!F{sr})", S.MONEY0)
        S._calc(wp.cell(r, 4), f'=IF(B{r}="",0,SUMIF({R("I")},B{r},{R("E")}))', S.MONEY0)
        S._calc(wp.cell(r, 5), f'=IF(B{r}="",0,SUMIFS({R("E")},{R("I")},B{r},{R("G")},"Yes"))', S.MONEY0)
        S._calc(wp.cell(r, 6), f"=D{r}-E{r}", S.MONEY0)
        S._calc(wp.cell(r, 7), f"=C{r}-D{r}", S.MONEY0)
    S._label(wp, "B10", "Total")
    for c in "CDEFG":
        S._calc(wp[f"{c}10"], f"=SUM({c}6:{c}9)", S.MONEY0, bold=True)
    S._label(wp, "B11", "Not assigned to anyone", bold=False)
    S._calc(wp["D11"], f'=SUM({R("E")})-D10', S.MONEY0)
    wp.conditional_formatting.add("G6:G9", FormulaRule(formula=["G6<0"], fill=RED))
    S._foot(wp, 14)

    gl = G0 + NG - 1
    gs = S._sheet(wb, "Guests", "Guests", "One row per invitation. Party size counts everyone on it.",
                  widths={"B": 28, "C": 12, "D": 10, "E": 12, "F": 16, "G": 3, "H": 22, "I": 10})
    S._header(gs, G0 - 1, ["Name", "Side", "Party size", "RSVP", "Meal"])
    for i in range(NG):
        r = G0 + i
        row = GUESTS[i] if i < len(GUESTS) else (None,) * 5
        for c, v in enumerate(row, start=2):
            S._inp(gs.cell(r, c), v, "0" if c == 4 else None)
    S._list_validation(gs, ["Invited", "Yes", "No"], f"E{G0}:E{gl}")
    for k, (lab, f) in enumerate([("Invited (people)", f"=SUM(D{G0}:D{gl})"),
                                  ("Coming", f'=SUMIF(E{G0}:E{gl},"Yes",D{G0}:D{gl})'),
                                  ("Not coming", f'=SUMIF(E{G0}:E{gl},"No",D{G0}:D{gl})'),
                                  ("Waiting to hear", f'=SUMIF(E{G0}:E{gl},"Invited",D{G0}:D{gl})')]):
        S._label(gs, f"H{G0 + k}", lab, bold=k == 1)
        S._calc(gs[f"I{G0 + k}"], f, "0", bold=k == 1)
    gs.freeze_panes = f"C{G0}"
    S._foot(gs, gl + 2)

    db = S._sheet(wb, "Dashboard", "Wedding money dashboard", "Everything on one screen. Nothing to type here.",
                  widths={"B": 30, "C": 16})
    items = [("Total budget", "=Setup!C5", S.MONEY0), ("Planned so far", f"=Budget!C{t}", S.MONEY0),
             ("Booked (all payments)", f"=Budget!D{t}", S.MONEY0), ("Paid", f"=Budget!E{t}", S.MONEY0),
             ("Still owed", f"=Budget!F{t}", S.MONEY0), ("Budget left after bookings", f"=Setup!C5-Budget!D{t}", S.MONEY0),
             ("Overdue payments", "='Due by month'!C6", "0"), ("Due in the next 30 days",
                                                                 f'=SUMIFS({R("E")},{R("G")},"<>Yes",{R("F")},">="&TODAY(),{R("F")},"<="&TODAY()+30)', S.MONEY0),
             ("Days to the wedding", "=MAX(0,Setup!C6-TODAY())", "0"),
             ("Guests coming (so far)", "=Guests!I8", "0"),
             ("Cost per guest (planned guests)", "=IF(Setup!C7>0,Budget!D" + str(t) + "/Setup!C7,0)", S.MONEY0)]
    for i, (lab, f, fmt) in enumerate(items):
        r = 5 + i
        S._label(db, f"B{r}", lab, bold=i in (0, 5))
        S._calc(db[f"C{r}"], f, fmt, bold=i in (0, 5))
    db.conditional_formatting.add("C10", FormulaRule(formula=["C10<0"], fill=RED))
    db.conditional_formatting.add("C11", FormulaRule(formula=["C11>0"], fill=RED))
    S._foot(db, 18)
    wb.move_sheet("Dashboard", offset=-(len(wb.sheetnames) - 2))
    wb.save(path)
    return path


ST.SHEETS["wedding-budget-sheet"] = ("Wedding-Budget-Sheet.xlsx", build_wedding)
