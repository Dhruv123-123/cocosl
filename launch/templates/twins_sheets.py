"""Google Sheets versions of five Etsy printables (also open in Excel and Numbers):
52-Week Savings Challenge, No-Spend Challenge, Bill Payment Tracker, Paycheck Budget Planner, Debt Payoff Coloring Tracker.

Same house style and helpers as sheets_templates.py (yellow = input, white = calculated, a Start tab, fictional
example data). Only functions that Google Sheets imports cleanly from .xlsx: SUM, SUMPRODUCT, COUNTIF, INDEX/MATCH,
DATE, TODAY, REPT. Conditional formatting only looks at its own tab (Google Sheets can't point a rule at another tab).
Registers itself in sheets_templates.SHEETS when imported; sheets_templates imports it at the bottom.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

import sheets_templates as ST
from sheets_templates import OK, RED, S, _bar, _start

GREEN_FILL = PatternFill("solid", fgColor="2FBF71")
NOTE = Font(name="Inter", size=9, italic=True, color="4B5A51")


def _note(ws, ref: str, text: str):
    ws[ref] = text
    ws[ref].font = NOTE


def _whole(ws, rng: str, lo: int, hi: int, msg: str):
    dv = DataValidation(type="whole", operator="between", formula1=str(lo), formula2=str(hi), allow_blank=True)
    dv.error, dv.errorTitle = msg, "Check the number"
    ws.add_data_validation(dv)
    dv.add(rng)


def _summary(ws, row: int, items: list[tuple[str, str, str]], col: str = "I"):
    """A label/value block: (label, formula, number format)."""
    lab = chr(ord(col))
    val = chr(ord(col) + 1)
    for i, (text, f, fmt) in enumerate(items):
        r = row + i
        S._label(ws, f"{lab}{r}", text, bold=i == 0)
        S._calc(ws[f"{val}{r}"], f, fmt, bold=i == 0)
    return row + len(items)


# --------------------------------------------------------------------------------------------------
# 1. 52-Week Savings Challenge
# --------------------------------------------------------------------------------------------------
W0, NW = 11, 52
VERSIONS = ["Classic ($1 more each week)", "Reverse (biggest first)", "Same every week", "My own amounts"]


def build_52_week(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "52-Week Savings Challenge", "Save a little more each week. The classic version ends with $1,378 after 52 weeks.",
           ["On Challenge, pick a version, your start date and the base amount ($1 for the classic $1,378).",
            "Each week, type what you saved in the yellow Saved column. Saved at least the plan? It gets a tick.",
            "The box on the right shows your goal, what you've saved, and whether you're ahead or behind for today's date.",
            "Prefer your own amounts? Pick 'My own amounts' and type them in the Your amount column."],
           [("Challenge", "All 52 weeks, your plan, what you saved and the running total."),
            ("Versions", "Classic: base x week. Reverse: base x (53 - week). Same every week: the base each week.")])
    ws = S._sheet(wb, "Challenge", "52-week savings challenge", "One row per week. Start any week of the year.",
                  widths={"B": 8, "C": 13, "D": 12, "E": 13, "F": 12, "G": 8, "H": 15, "I": 30, "J": 15})
    S._label(ws, "B5", "Version")
    S._inp(ws["D5"], VERSIONS[0])
    ws.merge_cells("D5:F5")
    S._list_validation(ws, VERSIONS, "D5")
    S._label(ws, "B6", "Start date")
    start = today - timedelta(weeks=8, days=today.weekday())
    S._inp(ws["D6"], start, "mmm d, yyyy")
    S._label(ws, "B7", "Base amount")
    S._inp(ws["D7"], 1, S.MONEY)
    _note(ws, "G7", "Classic with $1 = $1,378. With $2 = $2,756. With $5 = $6,890.")
    S._header(ws, W0 - 1, ["Week", "Week of", "Plan", "Your amount", "Saved", "Done", "Running total"])
    last = W0 + NW - 1
    for i in range(NW):
        r = W0 + i
        ws.cell(r, 2, i + 1)
        S._calc(ws.cell(r, 3), f"=$D$6+7*(B{r}-1)", "mmm d")
        S._calc(ws.cell(r, 4), f'=IF($D$5="{VERSIONS[0]}",$D$7*B{r},IF($D$5="{VERSIONS[1]}",$D$7*(53-B{r}),'
                               f'IF($D$5="{VERSIONS[2]}",$D$7,N(E{r}))))', S.MONEY)
        S._inp(ws.cell(r, 5), None, S.MONEY)
        S._inp(ws.cell(r, 6), (i + 1) if i < 9 else None, S.MONEY)
        S._calc(ws.cell(r, 7), f'=IF(F{r}="","",IF(F{r}>=D{r},"✓","part"))')
        S._calc(ws.cell(r, 8), f'=IF(F{r}="","",SUM($F${W0}:F{r}))', S.MONEY)
        ws.cell(r, 7).alignment = Alignment(horizontal="center")
    ws.conditional_formatting.add(f"G{W0}:G{last}", CellIsRule(operator="equal", formula=['"✓"'], fill=OK))
    rng = lambda c: f"{c}${W0}:{c}${last}"  # noqa: E731
    end = _summary(ws, 5, [("Goal", f"=SUM({rng('$D')})", S.MONEY),
                           ("Saved so far", f"=SUM({rng('$F')})", S.MONEY),
                           ("Left to save", "=MAX(0,J5-J6)", S.MONEY),
                           ("Weeks done", f'=COUNTIF({rng("$G")},"✓")', "0"),
                           ("Plan up to today", f"=SUMPRODUCT(({rng('$C')}<=TODAY())*{rng('$D')})", S.MONEY),
                           ("Ahead (+) or behind (-)", "=J6-J9", S.MONEY),
                           ("Progress", '=IF(J5>0,MIN(1,J6/J5),"")', "0%")])
    _bar(ws[f"I{end}"], f"J{end - 1}", 20)
    ws.conditional_formatting.add("J10", CellIsRule(operator="lessThan", formula=["0"], fill=RED))
    ws.conditional_formatting.add("J10", CellIsRule(operator="greaterThanOrEqual", formula=["0"], fill=OK))
    ws.freeze_panes = f"B{W0}"
    S._foot(ws, last + 2)
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 2. No-Spend Challenge
# --------------------------------------------------------------------------------------------------
D0, ND = 11, 60
SPENT = {4: (18.5, "Lunch out with work"), 9: (32, "Birthday gift (planned, allowed)")}


def build_no_spend(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "No-Spend Challenge", "Thirty days of noticing your spending. Essentials are always allowed.",
           ["On Rules, write what's always allowed (bills, groceries, fuel, medicine) and what you're pausing.",
            "On Challenge, set the start date, the number of days (30 is classic, up to 60) and what you usually spend on extras a day.",
            "Every day, pick Yes (no extras) or No and type what you spent. The circles fill in.",
            "At the end, move what you didn't spend to savings or a debt and type it in."],
           [("Challenge", "Your days, the circles and the totals."),
            ("Rules", "Allowed, not allowed, free things to do and the end-of-challenge questions.")])
    ws = S._sheet(wb, "Challenge", "No-spend challenge", "Yes = no spending on extras that day. Slipped? Write it down and keep going.",
                  widths={"B": 7, "C": 13, "D": 11, "E": 14, "F": 32, "G": 6, "H": 3, "I": 26, "J": 14})
    rows = [("Start date", today - timedelta(days=12), "mmm d, yyyy"), ("Number of days", 30, "0"),
            ("Usual daily spend on extras", 15, S.MONEY), ("Moved to savings at the end", None, S.MONEY)]
    for i, (lab, v, fmt) in enumerate(rows):
        S._label(ws, f"B{5 + i}", lab)
        S._inp(ws[f"E{5 + i}"], v, fmt)
    _whole(ws, "E6", 7, ND, f"Pick 7 to {ND} days.")
    S._header(ws, D0 - 1, ["Day", "Date", "No-spend?", "Spent on extras", "Note", ""])
    last = D0 + ND - 1
    for i in range(ND):
        r, d = D0 + i, i + 1
        S._calc(ws.cell(r, 2), f'=IF({d}<=$E$6,{d},"")', "0")
        S._calc(ws.cell(r, 3), f'=IF(B{r}="","",$E$5+B{r}-1)', "ddd mmm d")
        logged = d <= 12
        S._inp(ws.cell(r, 4), ("No" if d in SPENT else "Yes") if logged else None)
        S._inp(ws.cell(r, 5), SPENT.get(d, (None,))[0], S.MONEY)
        S._inp(ws.cell(r, 6), SPENT.get(d, (None, None))[1])
        S._calc(ws.cell(r, 7), f'=IF(D{r}="Yes","●",IF(D{r}="No","○",""))')
        ws.cell(r, 7).alignment = Alignment(horizontal="center")
    S._list_validation(ws, ["Yes", "No"], f"D{D0}:D{last}")
    ws.conditional_formatting.add(f"G{D0}:G{last}", CellIsRule(operator="equal", formula=['"●"'], font=Font(color="1E8A50", bold=True)))
    end = _summary(ws, 5, [("No-spend days", f'=COUNTIF(D{D0}:D{last},"Yes")', "0"),
                           ("Days logged", f'=COUNTIF(D{D0}:D{last},"Yes")+COUNTIF(D{D0}:D{last},"No")', "0"),
                           ("Spent on extras", f"=SUM(E{D0}:E{last})", S.MONEY),
                           ("Not spent (estimate)", "=J5*E7", S.MONEY),
                           ("Moved to savings", "=N(E8)", S.MONEY),
                           ("Progress", '=IF(E6>0,J5/E6,"")', "0%")])
    _bar(ws[f"I{end}"], f"J{end - 1}", 20)
    # the circles: 10 per row, like the printable
    S._label(ws, "L4", "Your circles (● no-spend day, ○ spent, · not yet)")
    for k in range(ND):
        r, c = 5 + k // 10, 12 + k % 10
        cell = ws.cell(r, c)
        cell.value = f'=IF({k + 1}>$E$6,"",IF(INDEX($G${D0}:$G${last},{k + 1})="●","●",IF(INDEX($G${D0}:$G${last},{k + 1})="○","○","·")))'
        cell.alignment = Alignment(horizontal="center")
        cell.font = Font(name="Inter", size=14, color="1E8A50", bold=True)
    ws.column_dimensions["K"].width = 3
    for c in range(12, 22):
        ws.column_dimensions[chr(64 + c)].width = 4
    ws.freeze_panes = f"B{D0}"
    S._foot(ws, last + 2)

    ru = S._sheet(wb, "Rules", "My rules", "Write them before day 1. It's a challenge, not a punishment.",
                  widths={"B": 34, "C": 34, "D": 34})
    S._header(ru, 5, ["Always allowed", "Not allowed (for now)", "Free things to do instead"])
    allowed = ["Rent and bills", "Groceries (from the list)", "Fuel and transit", "Medicine", "Anything already planned"]
    pause = ["Takeout and delivery", "Coffee out", "Online shopping", "Impulse buys", "New subscriptions"]
    free = ["Library books and films", "A walk or a hike", "Movie night at home", "Cook something new", "Call a friend"]
    for i in range(10):
        for c, src in ((2, allowed), (3, pause), (4, free)):
            S._inp(ru.cell(6 + i, c), src[i] if i < len(src) else None)
    S._label(ru, "B18", "At the end")
    for i, q in enumerate(["Which day was hardest, and why?", "What did I not miss at all?",
                           "What will I keep doing next month?", "Where did the money I didn't spend go?"]):
        ru.cell(19 + i, 2, q).font = Font(name="Inter", bold=True)
        ru.merge_cells(start_row=19 + i, start_column=3, end_row=19 + i, end_column=4)
        S._inp(ru.cell(19 + i, 3))
    S._foot(ru, 25)
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 3. Bill Payment Tracker
# --------------------------------------------------------------------------------------------------
B0, NB = 6, 40
FREQS = ["Monthly", "Every 3 months", "Yearly"]
CATS = ["Housing", "Utilities", "Insurance", "Phone + internet", "Subscriptions", "Debt", "Other"]
BILLS = [("Rent", "Housing", 1400, 1, "Monthly", None, "No"), ("Car insurance", "Insurance", 140, 3, "Monthly", None, "Yes"),
         ("Electric", "Utilities", 95, 12, "Monthly", None, "No"), ("Water", "Utilities", 45, 18, "Monthly", None, "No"),
         ("Phone + internet", "Phone + internet", 110, 20, "Monthly", None, "Yes"),
         ("Streaming", "Subscriptions", 15.99, 22, "Monthly", None, "Yes"), ("Credit card minimum", "Debt", 105, 25, "Monthly", None, "No"),
         ("Trash pickup", "Utilities", 66, 10, "Every 3 months", 1, "No"), ("Car registration", "Other", 180, 15, "Yearly", 4, "No"),
         ("Renters insurance", "Insurance", 180, 9, "Yearly", 8, "Yes")]
MONTHS3 = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_bill_tracker(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "Bill Payment Tracker", "Every bill in one list, a 12-month checklist to tick as you pay, and a bill calendar.",
           ["On Bills, list every bill once: amount, due day, how often, and the first month it's due (for yearly and every-3-months bills).",
            "On Checklist, pick ✓ in this month's column when you pay. Unpaid bills past their due day turn red.",
            "Calendar shows what's due on each day of the month.",
            "The yearly and every-3-months bills show what to set aside each month, so they're never a surprise."],
           [("Bills", "Your bill list, the monthly set-aside and this month's totals."),
            ("Checklist", "Every bill x 12 months. Red = due, past its day and not ticked."),
            ("Calendar", "Days 1 to 31 with the bills due that day.")])
    bs = S._sheet(wb, "Bills", "Bills", "One row per bill. Due day is the day of the month (1 to 31).",
                  widths={"B": 24, "C": 16, "D": 11, "E": 9, "F": 15, "G": 11, "H": 9, "I": 13, "J": 12, "K": 3, "L": 30, "M": 14})
    S._header(bs, B0 - 1, ["Bill", "Category", "Amount", "Due day", "How often", "First due month", "Autopay",
                           "Set aside / month", "Due this month"])
    last = B0 + NB - 1
    for i in range(NB):
        r = B0 + i
        row = BILLS[i] if i < len(BILLS) else (None,) * 7
        for c, (v, fmt) in enumerate(zip(row, (None, None, S.MONEY, "0", None, "0", None)), start=2):
            S._inp(bs.cell(r, c), v, fmt)
        S._calc(bs.cell(r, 9), f'=IF(B{r}="","",D{r}/IF(F{r}="Yearly",12,IF(F{r}="Every 3 months",3,1)))', S.MONEY)
        S._calc(bs.cell(r, 10), f'=IF(B{r}="","",IF(OR(F{r}="Monthly",F{r}=""),"Yes",IF(MOD(MONTH(TODAY())-N(G{r}),'
                                f'IF(F{r}="Yearly",12,3))=0,"Yes","")))')
        S._calc(bs.cell(r, 11), f'=IF(J{r}="Yes",E{r}&"|"&COUNTIFS($E${B0}:E{r},E{r},$J${B0}:J{r},"Yes"),"")')
        bs.cell(r, 11).font = Font(name="Inter", size=8, color="999999")
    S._list_validation(bs, CATS, f"C{B0}:C{last}")
    S._list_validation(bs, FREQS, f"F{B0}:F{last}")
    S._list_validation(bs, ["Yes", "No"], f"H{B0}:H{last}")
    _whole(bs, f"E{B0}:E{last}", 1, 31, "Due day is 1 to 31.")
    _whole(bs, f"G{B0}:G{last}", 1, 12, "First due month is 1 (January) to 12 (December).")
    R = lambda c: f"${c}${B0}:${c}${last}"  # noqa: E731
    _summary(bs, B0, [("Monthly bills", f'=SUMIF({R("F")},"Monthly",{R("D")})', S.MONEY),
                      ("Set aside for the others / month", f'=SUMIFS({R("I")},{R("F")},"<>Monthly",{R("B")},"<>")', S.MONEY),
                      ("Bills due this month", f'=COUNTIF({R("J")},"Yes")', "0"),
                      ("Amount due this month", f'=SUMIF({R("J")},"Yes",{R("D")})', S.MONEY),
                      ("Paid this month (from Checklist)", f"=SUMPRODUCT((INDEX(Checklist!$D${B0}:$O${last},0,MONTH(TODAY()))=\"✓\")*{R('D')})",
                       S.MONEY)], col="L")
    bs.column_dimensions["K"].hidden = True  # helper: "<due day>|<nth bill that day>" for the Calendar tab
    bs.freeze_panes = f"C{B0}"
    S._foot(bs, last + 2)

    ck = S._sheet(wb, "Checklist", "Payment checklist", "Pick ✓ when it's paid. Red = due this month, past its day, not ticked yet.",
                  widths={"B": 24, "C": 11, **{chr(68 + i): 6 for i in range(12)}, "P": 4, "Q": 4})
    S._header(ck, B0 - 1, ["Bill", "Amount"] + MONTHS3 + ["Day", "Due"])
    cur = today.month
    for i in range(NB):
        r = B0 + i
        S._calc(ck.cell(r, 2), f'=IF(Bills!B{r}="","",Bills!B{r})')
        S._calc(ck.cell(r, 3), f'=IF(Bills!B{r}="","",Bills!D{r})', S.MONEY)
        for m in range(12):
            cell = ck.cell(r, 4 + m)
            mo = m + 1
            past = mo < cur or (mo == cur and i < len(BILLS) and BILLS[i][3] < today.day)
            due = i < len(BILLS) and (BILLS[i][4] == "Monthly" or (mo - BILLS[i][5]) % (12 if BILLS[i][4] == "Yearly" else 3) == 0)
            S._inp(cell, "✓" if (i < len(BILLS) and past and due and not (mo == cur and i == 2)) else None)
            cell.alignment = Alignment(horizontal="center")
        # helpers on this tab so the red rule doesn't need another tab: due day, due-this-month flag
        S._calc(ck.cell(r, 16), f'=IF(Bills!B{r}="","",Bills!E{r})', "0")
        S._calc(ck.cell(r, 17), f'=IF(Bills!B{r}="","",Bills!J{r})')
        for c in (16, 17):
            ck.cell(r, c).font = Font(name="Inter", size=8, color="999999")
    S._list_validation(ck, ["✓", "Skipped"], f"D{B0}:O{last}")
    ck.conditional_formatting.add(f"D{B0}:O{last}", FormulaRule(
        formula=[f'AND(D{B0}="",$B{B0}<>"",COLUMN(D{B0})-3=MONTH(TODAY()),$Q{B0}="Yes",$P{B0}<DAY(TODAY()))'], fill=RED))
    ck.conditional_formatting.add(f"D{B0}:O{last}", CellIsRule(operator="equal", formula=['"✓"'], fill=OK))
    ck.freeze_panes = f"D{B0}"
    S._foot(ck, last + 2)

    cal = S._sheet(wb, "Calendar", "Bill calendar", "Every bill by day of the month (yearly and every-3-months bills only in their months).",
                   widths={"B": 7, "C": 28, "D": 10, "E": 13})
    S._header(cal, 5, ["Day", "First bill due", "More", "Total due"])
    for d in range(1, 32):
        r = 5 + d
        cal.cell(r, 2, d)
        S._calc(cal.cell(r, 3), f'=IFERROR(INDEX(Bills!$B${B0}:$B${last},MATCH("{d}|1",Bills!$K${B0}:$K${last},0)),"")')
        S._calc(cal.cell(r, 4), f'=IF(COUNTIFS(Bills!$E${B0}:$E${last},{d},Bills!$J${B0}:$J${last},"Yes")>1,'
                                f'"+"&(COUNTIFS(Bills!$E${B0}:$E${last},{d},Bills!$J${B0}:$J${last},"Yes")-1)&" more","")')
        S._calc(cal.cell(r, 5), f'=IF(C{r}="","",SUMIFS(Bills!$D${B0}:$D${last},Bills!$E${B0}:$E${last},{d},'
                                f'Bills!$J${B0}:$J${last},"Yes"))', S.MONEY)
    S._foot(cal, 39)
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 4. Paycheck Budget Planner
# --------------------------------------------------------------------------------------------------
P0, NP, PB0, NPB = 6, 26, 6, 30
PAYFREQ = ["Every 2 weeks", "Every week", "Twice a month (1st and 15th)"]
PBILLS = [("Rent", 1400, 1), ("Car insurance", 140, 3), ("Electric", 95, 12), ("Water", 45, 18),
          ("Phone + internet", 110, 20), ("Streaming", 16, 22), ("Credit card minimum", 105, 25), ("Gym", 30, 8)]


def pay_date(n: str) -> str:
    """Formula for the n-th payday (n is a formula, 1-based) from Setup's first payday and frequency."""
    f, first = "Setup!$C$6", "Setup!$C$5"
    k = f"(({n})-1+IF(DAY({first})>=15,1,0))"
    return (f'IF({f}="{PAYFREQ[1]}",{first}+7*(({n})-1),IF({f}="{PAYFREQ[0]}",{first}+14*(({n})-1),'
            f'DATE(YEAR({first}),MONTH({first})+INT({k}/2),IF(MOD({k},2)=0,1,15))))')


def bills_between(p: str, q: str, what: str) -> str:
    """SUMPRODUCT of Bills!<what> for bills whose due day falls on or after p and before q (windows up to a month)."""
    d = f"Bills!$D${PB0}:$D${PB0 + NPB - 1}"
    c1 = f"DATE(YEAR({p}),MONTH({p}),{d})"
    c2 = f"DATE(YEAR({q}),MONTH({q}),{d})"
    hit = f"((({c1}>={p})*({c1}<{q})+(MONTH({q})<>MONTH({p}))*({c2}>={p})*({c2}<{q}))>0)"
    w = "1" if what == "count" else f"Bills!$C${PB0}:$C${PB0 + NPB - 1}"
    return f"SUMPRODUCT({hit}*({d}>0)*{w})"


def build_paycheck(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "Paycheck Budget Planner", "Budget each paycheck instead of each month: bills due before the next payday, then savings, then spending money.",
           ["On Setup, type your first payday this year (or any recent one) and how often you're paid.",
            "On Bills, list each monthly bill and the day it's due (1 to 28; use 28 for bills due on the 29th to 31st).",
            "On Paychecks, the sheet finds the bills due before each next payday. Type what you received and what you'll save.",
            "Spending money is what's left. Divide by the days until next payday for a daily number."],
           [("Setup", "First payday and how often you're paid."),
            ("Bills", "Monthly bills and their due days."),
            ("Paychecks", "26 paydays: bills due, savings, extra debt, spending money and a daily number.")])
    su = S._sheet(wb, "Setup", "Setup", "Your pay schedule.", widths={"B": 30, "C": 30, "D": 50})
    first = date(today.year, today.month, 1) - timedelta(days=28)
    first = first - timedelta(days=(first.weekday() - 4) % 7)  # a Friday
    S._label(su, "B5", "A recent payday")
    S._inp(su["C5"], first, "mmm d, yyyy")
    S._label(su, "B6", "How often you're paid")
    S._inp(su["C6"], PAYFREQ[0])
    S._list_validation(su, PAYFREQ, "C6")
    S._label(su, "B7", "Usual take-home pay")
    S._inp(su["C7"], 1900, S.MONEY)
    _note(su, "D7", "Fills in Received as a guess; type over it with the real amount each payday.")
    S._foot(su, 10)

    bl = S._sheet(wb, "Bills", "Monthly bills", "Due day 1 to 28. A bill due on the 29th to 31st: use 28 so it's never missed.",
                  widths={"B": 26, "C": 12, "D": 10, "E": 36})
    S._header(bl, PB0 - 1, ["Bill", "Amount", "Due day", "Note"])
    for i in range(NPB):
        r = PB0 + i
        row = PBILLS[i] if i < len(PBILLS) else (None,) * 3
        S._inp(bl.cell(r, 2), row[0])
        S._inp(bl.cell(r, 3), row[1], S.MONEY)
        S._inp(bl.cell(r, 4), row[2], "0")
        S._inp(bl.cell(r, 5))
    _whole(bl, f"D{PB0}:D{PB0 + NPB - 1}", 1, 28, "Use 1 to 28 (28 for bills due on the 29th to 31st).")
    t = PB0 + NPB
    S._label(bl, f"B{t}", "Total a month")
    S._calc(bl[f"C{t}"], f"=SUM(C{PB0}:C{t - 1})", S.MONEY, bold=True)
    S._total_row(bl, t, 2, 4)
    S._foot(bl, t + 2)

    pc = S._sheet(wb, "Paychecks", "Paychecks", "Every check gets a job. Yellow: what you received and what goes to savings and extra debt.",
                  widths={"B": 5, "C": 12, "D": 12, "E": 12, "F": 9, "G": 13, "H": 12, "I": 12, "J": 14, "K": 12, "L": 18})
    S._header(pc, P0 - 1, ["#", "Pay date", "Next payday", "Received", "Bills", "Bills due", "Savings", "Extra debt",
                           "Spending money", "Per day", "Status"])
    last = P0 + NP - 1
    for i in range(NP):
        r, n = P0 + i, i + 1
        pc.cell(r, 2, n)
        S._calc(pc.cell(r, 3), "=" + pay_date(f"B{r}"), "ddd mmm d")
        S._calc(pc.cell(r, 4), "=" + pay_date(f"B{r}+1"), "ddd mmm d")
        S._inp(pc.cell(r, 5), "=Setup!$C$7" if i >= 3 else 1900, S.MONEY)
        S._calc(pc.cell(r, 6), "=" + bills_between(f"C{r}", f"D{r}", "count"), "0")
        S._calc(pc.cell(r, 7), "=" + bills_between(f"C{r}", f"D{r}", "amount"), S.MONEY)
        S._inp(pc.cell(r, 8), [100, 150, 100][i] if i < 3 else None, S.MONEY)
        S._inp(pc.cell(r, 9), [0, 100, 50][i] if i < 3 else None, S.MONEY)
        S._calc(pc.cell(r, 10), f"=N(E{r})-G{r}-N(H{r})-N(I{r})", S.MONEY)
        S._calc(pc.cell(r, 11), f'=IF(D{r}>C{r},J{r}/(D{r}-C{r}),"")', S.MONEY)
        S._calc(pc.cell(r, 12), f'=IF(N(E{r})=0,"",IF(J{r}<0,"Short: move a bill","Every dollar has a job"))')
    pc.conditional_formatting.add(f"J{P0}:J{last}", CellIsRule(operator="lessThan", formula=["0"], fill=RED))
    pc.conditional_formatting.add(f"L{P0}:L{last}", CellIsRule(operator="equal", formula=['"Every dollar has a job"'], fill=OK))
    pc.conditional_formatting.add(f"L{P0}:L{last}", CellIsRule(operator="equal", formula=['"Short: move a bill"'], fill=RED))
    pc.freeze_panes = f"C{P0}"
    _note(pc, f"B{last + 2}", "Weekly pay: these 26 rows cover half a year. Copy the sheet for the second half and change the start payday.")
    S._foot(pc, last + 3)
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 5. Debt Payoff Coloring Tracker
# --------------------------------------------------------------------------------------------------
DD0, NDD = 6, 10
CDEBTS = [("Store card", 900, 0, 29.99), ("Credit card", 4200, 3310, 24.9), ("Personal loan", 1800, 1420, 11),
          ("Car loan", 6500, 5890, 7.9)]


def build_debt_coloring(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "Debt Payoff Coloring Tracker", "Make paying off debt visible: 100 squares that color themselves in as your balances drop.",
           ["On Debts, list each debt and its starting balance once.",
            "Once a month, copy each balance from your statement into Balance now.",
            "Color In shows 100 squares for your total debt. Each square is 1% of what you started with.",
            "Write a small reward for each milestone. Log your total once a month to see the line go down."],
           [("Debts", "Up to 10 debts: starting balance, balance now, paid off and a progress bar."),
            ("Color In", "The 100-square chart, milestones and rewards."),
            ("Log", "Your total owed each month, with a chart.")])
    ds = S._sheet(wb, "Debts", "Debts", "Starting balance once. Balance now every month.",
                  widths={"B": 22, "C": 15, "D": 14, "E": 9, "F": 13, "G": 9, "H": 18})
    S._header(ds, DD0 - 1, ["Debt", "Starting balance", "Balance now", "APR %", "Paid off", "Progress", ""])
    last = DD0 + NDD - 1
    for i in range(NDD):
        r = DD0 + i
        row = CDEBTS[i] if i < len(CDEBTS) else (None,) * 4
        S._inp(ds.cell(r, 2), row[0])
        S._inp(ds.cell(r, 3), row[1], S.MONEY0)
        S._inp(ds.cell(r, 4), row[2], S.MONEY0)
        S._inp(ds.cell(r, 5), row[3], "0.00")
        S._calc(ds.cell(r, 6), f'=IF(B{r}="","",MAX(0,N(C{r})-N(D{r})))', S.MONEY0)
        S._calc(ds.cell(r, 7), f'=IF(OR(B{r}="",N(C{r})=0),"",MIN(1,F{r}/C{r}))', "0%")
        _bar(ds.cell(r, 8), f"G{r}", 12)
    t = last + 1
    S._label(ds, f"B{t}", "Total")
    for col in "CDF":
        S._calc(ds[f"{col}{t}"], f"=SUM({col}{DD0}:{col}{last})", S.MONEY0, bold=True)
    S._calc(ds[f"G{t}"], f'=IF(C{t}>0,MIN(1,F{t}/C{t}),"")', "0%", bold=True)
    _bar(ds[f"H{t}"], f"G{t}", 12)
    S._total_row(ds, t, 2, 8)
    _note(ds, f"B{t + 2}", "Snowball: pay extra on the smallest balance first. Avalanche: the highest APR first. Either way, keep every minimum paid.")
    S._foot(ds, t + 4)

    ci = S._sheet(wb, "Color In", "Color in your debt", "Each square is 1% of the total you started with. They fill in by themselves.",
                  widths={"B": 3, **{chr(67 + i): 5 for i in range(10)}, "M": 3, "N": 24, "O": 14, "P": 30})
    S._label(ci, "N5", "Squares colored")
    S._calc(ci["O5"], f"=IF(Debts!C{t}>0,ROUNDDOWN(MIN(1,Debts!F{t}/Debts!C{t})*100,0),0)", "0", bold=True)
    S._label(ci, "N6", "Each square is worth", bold=False)
    S._calc(ci["O6"], f"=Debts!C{t}/100", S.MONEY0)
    S._label(ci, "N7", "Paid off so far", bold=False)
    S._calc(ci["O7"], f"=Debts!F{t}", S.MONEY0)
    S._label(ci, "N8", "Still owe", bold=False)
    S._calc(ci["O8"], f"=Debts!D{t}", S.MONEY0)
    for k in range(100):
        r, c = 5 + k // 10, 3 + k % 10
        cell = ci.cell(r, c, k + 1)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(name="Inter", size=8, color="999999")
        ci.row_dimensions[r].height = 26
    ci.conditional_formatting.add("C5:L14", FormulaRule(formula=["C5<=$O$5"], fill=GREEN_FILL, font=Font(color="FFFFFF", bold=True)))
    S._header(ci, 11, ["Milestone", "Reached", "My reward"], col=14)
    rewards = ["Pizza night at home", "A day trip", "New running shoes", "A weekend away (paid in cash)"]
    for i, pct in enumerate((25, 50, 75, 100)):
        r = 12 + i
        ci.cell(r, 14, "Debt-free" if pct == 100 else f"{pct}% paid off").font = Font(name="Inter", bold=True)
        S._calc(ci.cell(r, 15), f'=IF($O$5>={pct},"✓ Reached","$"&TEXT(MAX(0,Debts!$C${t}*{pct}/100-Debts!$F${t}),"#,##0")&" to go")')
        S._inp(ci.cell(r, 16), rewards[i])
    ci.conditional_formatting.add("O12:O15", CellIsRule(operator="equal", formula=['"✓ Reached"'], fill=OK))
    S._foot(ci, 17)

    lg = S._sheet(wb, "Log", "Monthly log", "Once a month: the date and your total owed (from Debts, or add it up from statements).",
                  widths={"B": 14, "C": 16, "D": 30})
    S._header(lg, 5, ["Date", "Total owed", "Note"])
    start_total = sum(d[1] for d in CDEBTS)
    now_total = sum(d[2] for d in CDEBTS)
    hist = [start_total - round((start_total - now_total) * k / 5) for k in range(6)]
    for i in range(36):
        r = 6 + i
        when = None
        if i < 6:
            m = today.month - 5 + i
            when = date(today.year + (m - 1) // 12, (m - 1) % 12 + 1, 1)
        S._inp(lg.cell(r, 2), when, "mmm yyyy")
        S._inp(lg.cell(r, 3), hist[i] if i < 6 else None, S.MONEY0)
        S._inp(lg.cell(r, 4), "Store card paid off!" if i == 4 else None)
    ch = LineChart()
    ch.title, ch.height, ch.width = "Total owed", 7.5, 15
    ch.add_data(Reference(lg, min_col=3, min_row=5, max_row=11), titles_from_data=True)
    ch.set_categories(Reference(lg, min_col=2, min_row=6, max_row=11))
    ch.series[0].graphicalProperties.line.solidFill = S.GREEN
    lg.add_chart(ch, "F5")
    S._foot(lg, 44)
    wb.save(path)
    return path


TWINS = {
    "52-week-savings-sheet": ("52-Week-Savings-Challenge-Sheet.xlsx", build_52_week),
    "no-spend-challenge-sheet": ("No-Spend-Challenge-Sheet.xlsx", build_no_spend),
    "bill-tracker-sheet": ("Bill-Payment-Tracker-Sheet.xlsx", build_bill_tracker),
    "paycheck-budget-sheet": ("Paycheck-Budget-Sheet.xlsx", build_paycheck),
    "debt-coloring-sheet": ("Debt-Payoff-Coloring-Sheet.xlsx", build_debt_coloring),
}
ST.SHEETS.update(TWINS)
