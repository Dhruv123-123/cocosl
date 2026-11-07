"""Spreadsheet templates for the Money Made Simple product line (openpyxl).

House style matches 20-Minute-Budget-Template.xlsx: yellow cells are inputs, white cells calculate,
ink header rows, every workbook ships filled with a fictional example. Formulas stick to functions that
work the same in Excel, Google Sheets and Numbers (SUM, SUMPRODUCT, IF, MIN/MAX, NPER, PMT, FV, ...).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

INK, CREAM, GREEN, GOLD, TINT, INPUT, GREY = "0B1D13", "F4F1E8", "2FBF71", "F2B134", "EAF6EF", "FFF4CC", "999999"
F_INPUT = PatternFill("solid", fgColor=INPUT)
F_HEAD = PatternFill("solid", fgColor=INK)
F_TOTAL = PatternFill("solid", fgColor=TINT)
F_CREAM = PatternFill("solid", fgColor=CREAM)
THIN = Side(style="thin", color="D9D3C3")
BOX = Border(bottom=THIN)
MONEY = '"$"#,##0.00'
MONEY0 = '"$"#,##0'
PCT = '0.0"%"'          # values typed as 24.9 meaning 24.9 %
FOOT = ("Educational tool only, not financial, tax, legal or investment advice. Example data is fictional. "
        "For personal use by the purchaser; please don't resell or redistribute. (c) Money Made Simple")


def _sheet(wb: Workbook, title: str, heading: str, sub: str, tab: str = GREEN, widths=None, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.sheet_properties.tabColor = tab
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    for col, w in (widths or {}).items():
        ws.column_dimensions[col].width = w
    ws["B1"] = heading
    ws["B1"].font = Font(name="Inter", size=18, bold=True, color=INK)
    ws["B2"] = sub
    ws["B2"].font = Font(name="Inter", size=10, color="4B5A51")
    ws["B3"] = "Yellow cells = your inputs. White cells calculate automatically. Example data shown; type over it."
    ws["B3"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    return ws


def _header(ws, row: int, labels: list[str], col: int = 2):
    for i, label in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=label)
        c.font = Font(name="Inter", bold=True, color="FFFFFF")
        c.fill = F_HEAD
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[row].height = 30


def _inp(c, value=None, fmt=None):
    if value is not None:
        c.value = value
    c.fill = F_INPUT
    c.border = BOX
    if fmt:
        c.number_format = fmt
    return c


def _calc(c, formula, fmt=None, bold=False):
    c.value = formula
    c.border = BOX
    if fmt:
        c.number_format = fmt
    if bold:
        c.font = Font(name="Inter", bold=True)
    return c


def _label(ws, ref, text, bold=True, fill=None):
    ws[ref] = text
    ws[ref].font = Font(name="Inter", bold=bold)
    if fill:
        ws[ref].fill = fill


def _total_row(ws, row, cols_from, cols_to):
    for col in range(cols_from, cols_to + 1):
        c = ws.cell(row=row, column=col)
        c.fill = F_TOTAL
        c.font = Font(name="Inter", bold=True)


def _foot(ws, row):
    ws.cell(row=row, column=2, value=FOOT).font = Font(name="Inter", size=8, italic=True, color=GREY)


def _list_validation(ws, options: list[str], rng: str):
    dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(rng)


# --------------------------------------------------------------------------------------------------
# 1. The Bill Cut Kit
# --------------------------------------------------------------------------------------------------
def build_bill_cut(path: Path) -> Path:
    wb = Workbook()
    ws = _sheet(wb, "Audit", "Subscription & Bill Audit",
                "Every recurring charge, converted to a yearly cost, with one decision each.",
                widths={"B": 30, "C": 13, "D": 13, "E": 13, "F": 13, "G": 14, "H": 13, "I": 13, "J": 16, "K": 26},
                first=True)
    _header(ws, 5, ["Charge", "Amount", "How often", "Yearly cost", "Decision", "New amount (if D/N)",
                    "New yearly", "Saves / yr", "Renewal / cancel date", "Notes"])
    example = [
        ("Video streaming #1", 17.99, "Monthly", "Keep", None, None, "Used weekly"),
        ("Video streaming #2", 15.49, "Monthly", "Cut", None, date(2026, 11, 8), "Not opened since summer"),
        ("Music app", 11.99, "Monthly", "Keep", None, None, ""),
        ("Cloud storage 2 TB", 9.99, "Monthly", "Downgrade", 2.99, None, "Using 120 GB"),
        ("Phone plan", 75.00, "Monthly", "Negotiate", 55.00, None, "See Negotiation Log"),
        ("Internet", 80.00, "Monthly", "Negotiate", 65.00, None, "See Negotiation Log"),
        ("Gym", 40.00, "Monthly", "Downgrade", 25.00, None, "Off-peak plan"),
        ("Food delivery membership", 9.99, "Monthly", "Cut", None, date(2026, 11, 8), "Ordered twice since June"),
        ("Language app", 89.99, "Yearly", "Cut", None, date(2027, 2, 14), "Renews Feb; cancel before"),
        ("Device protection", 9.00, "Monthly", "Cut", None, date(2026, 11, 8), "Phone is paid off"),
        ("Car insurance", 720.00, "Twice a year", "Negotiate", 640.00, None, "Quote shopping in Jan"),
    ]
    first, last = 6, 35
    freq_opts = ["Weekly", "Every 2 weeks", "Monthly", "Quarterly", "Twice a year", "Yearly"]
    dec_opts = ["Keep", "Cut", "Downgrade", "Negotiate"]
    for i, r in enumerate(range(first, last + 1)):
        row = example[i] if i < len(example) else (None,) * 7
        _inp(ws.cell(r, 2), row[0])
        _inp(ws.cell(r, 3), row[1], MONEY)
        _inp(ws.cell(r, 4), row[2])
        mult = (f'IF(D{r}="Weekly",52,IF(D{r}="Every 2 weeks",26,IF(D{r}="Monthly",12,IF(D{r}="Quarterly",4,'
                f'IF(D{r}="Twice a year",2,IF(D{r}="Yearly",1,0))))))')
        _calc(ws.cell(r, 5), f"=N(C{r})*{mult}", MONEY)
        _inp(ws.cell(r, 6), row[3])
        _inp(ws.cell(r, 7), row[4], MONEY)
        _calc(ws.cell(r, 8), f'=IF(F{r}="Cut",0,IF(OR(F{r}="Downgrade",F{r}="Negotiate"),'
                             f'IF(ISNUMBER(G{r}),G{r}*{mult},E{r}),E{r}))', MONEY)
        _calc(ws.cell(r, 9), f"=MAX(0,E{r}-H{r})", MONEY)
        _inp(ws.cell(r, 10), row[5], "yyyy-mm-dd")
        _inp(ws.cell(r, 11), row[6])
    _list_validation(ws, freq_opts, f"D{first}:D{last}")
    _list_validation(ws, dec_opts, f"F{first}:F{last}")
    t = last + 1
    _label(ws, f"B{t}", "Total")
    _calc(ws[f"E{t}"], f"=SUM(E{first}:E{last})", MONEY)
    _calc(ws[f"H{t}"], f"=SUM(H{first}:H{last})", MONEY)
    _calc(ws[f"I{t}"], f"=SUM(I{first}:I{last})", MONEY)
    _total_row(ws, t, 2, 11)
    ws.conditional_formatting.add(f"F{first}:F{last}", CellIsRule(operator="equal", formula=['"Cut"'],
                                  fill=PatternFill("solid", fgColor="F8D7D3")))
    ws.conditional_formatting.add(f"I{first}:I{last}", CellIsRule(operator="greaterThan", formula=["0"],
                                  font=Font(color="1E8A50", bold=True)))
    ws.freeze_panes = "C6"
    _foot(ws, t + 2)

    lg = _sheet(wb, "Negotiation Log", "Negotiation Log",
                "Every call: what you paid, what you pay now, and when the deal ends.", tab=GOLD,
                widths={"B": 13, "C": 22, "D": 16, "E": 13, "F": 13, "G": 13, "H": 14, "I": 16, "J": 30})
    _header(lg, 5, ["Date", "Company", "Spoke to", "Old / month", "New / month", "Saves / yr",
                    "Deal ends", "Remind me on", "What they offered"])
    calls = [(date(2026, 11, 9), "Phone carrier", "Sam (retention)", 75, 55, date(2027, 11, 9), "Moved to 15 GB plan, no contract"),
             (date(2026, 11, 9), "Internet provider", "Chat agent", 80, 65, date(2027, 5, 9), "12-month loyalty rate")]
    for i, r in enumerate(range(6, 26)):
        row = calls[i] if i < len(calls) else (None,) * 7
        _inp(lg.cell(r, 2), row[0], "yyyy-mm-dd")
        _inp(lg.cell(r, 3), row[1])
        _inp(lg.cell(r, 4), row[2])
        _inp(lg.cell(r, 5), row[3], MONEY)
        _inp(lg.cell(r, 6), row[4], MONEY)
        _calc(lg.cell(r, 7), f'=IF(AND(ISNUMBER(E{r}),ISNUMBER(F{r})),MAX(0,(E{r}-F{r})*12),"")', MONEY)
        _inp(lg.cell(r, 8), row[5], "yyyy-mm-dd")
        _calc(lg.cell(r, 9), f'=IF(ISNUMBER(H{r}),H{r}-14,"")', "yyyy-mm-dd")
        _inp(lg.cell(r, 10), row[6])
    _label(lg, "B26", "Total")
    _calc(lg["G26"], "=SUM(G6:G25)", MONEY)
    _total_row(lg, 26, 2, 10)
    lg["B28"] = "'Remind me on' is two weeks before the deal ends: call again then."
    lg["B28"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _foot(lg, 30)

    sm = _sheet(wb, "Summary", "Your savings", "Adds up the Audit tab. Give this money a job (guide, page 9).",
                tab=INK, widths={"B": 34, "C": 16, "D": 40})
    rows = [
        ("Recurring charges found", f'=COUNTA(Audit!B{first}:B{last})', "0"),
        ("Yearly cost before", f"=Audit!E{t}", MONEY),
        ("Yearly cost after", f"=Audit!H{t}", MONEY),
        ("Saved per year", f"=Audit!I{t}", MONEY),
        ("Saved per month", "=C9/12", MONEY),
        ("Saved per week", "=C9/52", MONEY),
        ("Cuts", f'=COUNTIF(Audit!F{first}:F{last},"Cut")', "0"),
        ("Downgrades", f'=COUNTIF(Audit!F{first}:F{last},"Downgrade")', "0"),
        ("Negotiations", f'=COUNTIF(Audit!F{first}:F{last},"Negotiate")', "0"),
    ]
    for i, (lab, f, fmt) in enumerate(rows):
        r = 6 + i
        _label(ws=sm, ref=f"B{r}", text=lab, bold=(r == 9))
        _calc(sm[f"C{r}"], f, fmt, bold=(r == 9))
        sm[f"B{r}"].border = BOX
    _total_row(sm, 9, 2, 3)
    sm["B17"] = "Where it goes (pick one and automate it this week)"
    sm["B17"].font = Font(name="Inter", bold=True)
    _inp(sm["C17"], "Emergency fund")
    _list_validation(sm, ["Emergency fund", "Extra debt payment", "Investing", "Sinking fund"], "C17")
    sm["B18"] = "Automatic transfer per month"
    _calc(sm["C18"], "=ROUNDDOWN(C10,0)", MONEY0, bold=True)
    sm["B19"] = "Next audit (6 months from today)"
    _calc(sm["C19"], "=EDATE(TODAY(),6)", "yyyy-mm-dd")
    _foot(sm, 22)
    wb.move_sheet("Summary", offset=-2)
    wb.active = 0
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 2. The Credit Report Audit Kit
# --------------------------------------------------------------------------------------------------
def build_credit_audit(path: Path) -> Path:
    wb = Workbook()
    ac = _sheet(wb, "Accounts", "Account audit",
                "One row per account or item. Note what each bureau shows and whether it's right.",
                widths={"B": 26, "C": 14, "D": 10, "E": 10, "F": 10, "G": 16, "H": 34, "I": 14, "J": 12},
                first=True)
    _header(ac, 5, ["Account / item", "Type", "On Equifax", "On Experian", "On TransUnion", "Looks right?",
                    "What's wrong", "Priority", "Disputed?"])
    rows = [
        ("Visa ending 4821", "Credit card", "Yes", "Yes", "Yes", "No", "30-day late Mar 2026; I paid on Mar 3", "1 - High", "Yes"),
        ("Store card ending 1102", "Credit card", "Yes", "No", "Yes", "Yes", "", "", "No"),
        ("Car loan ending 7730", "Auto loan", "Yes", "Yes", "Yes", "Yes", "", "", "No"),
        ("Medical collection $210", "Collection", "No", "Yes", "No", "No", "Paid in 2024; should not report", "1 - High", "Yes"),
        ("Student loan ending 0045", "Student loan", "Yes", "Yes", "Yes", "No", "Balance shows $15,900; actual $14,000", "2 - Medium", "No"),
        ("Address: 12 Elm St", "Personal info", "No", "No", "Yes", "No", "Never lived here", "3 - Low", "No"),
    ]
    yn = ["Yes", "No"]
    for i, r in enumerate(range(6, 31)):
        row = rows[i] if i < len(rows) else (None,) * 9
        for j, v in enumerate(row):
            _inp(ac.cell(r, 2 + j), v)
    _list_validation(ac, yn, "D6:G30")
    _list_validation(ac, yn, "J6:J30")
    _list_validation(ac, ["1 - High", "2 - Medium", "3 - Low"], "I6:I30")
    _list_validation(ac, ["Credit card", "Auto loan", "Student loan", "Mortgage", "Personal loan", "Collection",
                          "Inquiry", "Public record", "Personal info", "Other"], "C6:C30")
    ac.conditional_formatting.add("G6:G30", CellIsRule(operator="equal", formula=['"No"'],
                                  fill=PatternFill("solid", fgColor="F8D7D3")))
    _label(ac, "B32", "Items that look wrong")
    _calc(ac["D32"], '=COUNTIF(G6:G30,"No")', "0", bold=True)
    _label(ac, "B33", "Of those, not disputed yet")
    _calc(ac["D33"], '=COUNTIFS(G6:G30,"No",J6:J30,"<>Yes")', "0", bold=True)
    ac.freeze_panes = "C6"
    _foot(ac, 35)

    ds = _sheet(wb, "Disputes", "Dispute tracker",
                "Answer due = sent date + 30 days (+5 if mailed). Overdue rows turn red.", tab=GOLD,
                widths={"B": 26, "C": 14, "D": 12, "E": 12, "F": 14, "G": 14, "H": 12, "I": 36})
    _header(ds, 5, ["Item disputed", "Sent to", "Method", "Date sent", "Answer due by", "Status", "Days left", "Outcome / next step"])
    disputes = [
        ("Visa 4821 late payment", "Experian", "Online", date(2026, 11, 10), "Waiting", ""),
        ("Visa 4821 late payment", "Equifax", "Mail", date(2026, 11, 10), "Waiting", ""),
        ("Medical collection $210", "Experian", "Online", date(2026, 11, 10), "Waiting", ""),
    ]
    for i, r in enumerate(range(6, 26)):
        row = disputes[i] if i < len(disputes) else (None,) * 6
        _inp(ds.cell(r, 2), row[0])
        _inp(ds.cell(r, 3), row[1])
        _inp(ds.cell(r, 4), row[2])
        _inp(ds.cell(r, 5), row[3], "yyyy-mm-dd")
        _calc(ds.cell(r, 6), f'=IF(ISNUMBER(E{r}),E{r}+30+IF(D{r}="Mail",5,0),"")', "yyyy-mm-dd")
        _inp(ds.cell(r, 7), row[4])
        _calc(ds.cell(r, 8), f'=IF(AND(ISNUMBER(F{r}),G{r}="Waiting"),F{r}-TODAY(),"")', "0")
        _inp(ds.cell(r, 9), row[5])
    _list_validation(ds, ["Equifax", "Experian", "TransUnion", "Lender / furnisher", "Collector"], "C6:C25")
    _list_validation(ds, ["Online", "Mail", "Phone"], "D6:D25")
    _list_validation(ds, ["Waiting", "Corrected", "Deleted", "Verified (no change)", "Re-disputed"], "G6:G25")
    ds.conditional_formatting.add("H6:H25", FormulaRule(formula=['AND(ISNUMBER(H6),H6<0)'],
                                  fill=PatternFill("solid", fgColor="F8D7D3")))
    ds["B27"] = ("Bureaus generally have 30 days to investigate (up to 45 in some cases). 'Due by' is a "
                 "planning date, not a legal deadline calculation.")
    ds["B27"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _foot(ds, 29)

    ut = _sheet(wb, "Utilization", "Utilization calculator",
                "How much of your card limits you're using, and what to pay to hit your target.", tab=GREEN,
                widths={"B": 24, "C": 13, "D": 13, "E": 12, "F": 18, "G": 18})
    _label(ut, "B5", "Target utilization %")
    _inp(ut["C5"], 10, PCT)
    _header(ut, 7, ["Card", "Credit limit", "Balance", "Used %", "Pay down to hit target", "Statement closes (day of month)"])
    cards = [("Visa ending 4821", 4000, 1900, 14), ("Store card ending 1102", 1500, 640, 22), ("Mastercard ending 3390", 2500, 150, 5)]
    for i, r in enumerate(range(8, 18)):
        row = cards[i] if i < len(cards) else (None,) * 4
        _inp(ut.cell(r, 2), row[0])
        _inp(ut.cell(r, 3), row[1], MONEY0)
        _inp(ut.cell(r, 4), row[2], MONEY0)
        _calc(ut.cell(r, 5), f'=IF(N(C{r})>0,D{r}/C{r}*100,"")', PCT)
        _calc(ut.cell(r, 6), f'=IF(N(C{r})>0,MAX(0,D{r}-C{r}*$C$5/100),"")', MONEY0)
        _inp(ut.cell(r, 7), row[3], "0")
    _label(ut, "B18", "Total")
    _calc(ut["C18"], "=SUM(C8:C17)", MONEY0)
    _calc(ut["D18"], "=SUM(D8:D17)", MONEY0)
    _calc(ut["E18"], '=IF(C18>0,D18/C18*100,"")', PCT)
    _calc(ut["F18"], "=MAX(0,D18-C18*C5/100)", MONEY0)
    _total_row(ut, 18, 2, 7)
    ut.conditional_formatting.add("E8:E18", CellIsRule(operator="greaterThan", formula=["30"],
                                  fill=PatternFill("solid", fgColor="F8D7D3")))
    ut["B20"] = ("Pay before the statement closes to lower the balance that gets reported. Rows over 30% turn red. "
                 "Utilization is one factor among several; this isn't a score prediction.")
    ut["B20"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _foot(ut, 22)

    fz = _sheet(wb, "Freeze Record", "Freeze record",
                "Where and when you froze. Never type passwords or PINs here: use a password manager.", tab=INK,
                widths={"B": 16, "C": 14, "D": 34, "E": 14, "F": 14, "G": 30})
    _header(fz, 5, ["Bureau", "Frozen on", "Login / PIN stored in (not the PIN!)", "Lifted on", "Re-frozen on", "Why lifted"])
    for i, (b, d) in enumerate([("Equifax", date(2026, 11, 9)), ("Experian", date(2026, 11, 9)), ("TransUnion", date(2026, 11, 9))]):
        r = 6 + i
        _calc(fz.cell(r, 2), b, bold=True)
        _inp(fz.cell(r, 3), d, "yyyy-mm-dd")
        _inp(fz.cell(r, 4), "Password manager, 'Credit' folder")
        _inp(fz.cell(r, 5), None, "yyyy-mm-dd")
        _inp(fz.cell(r, 6), None, "yyyy-mm-dd")
        _inp(fz.cell(r, 7), None)
    _label(fz, "B10", "Next full audit")
    _calc(fz["C10"], "=EDATE(TODAY(),6)", "yyyy-mm-dd", bold=True)
    _foot(fz, 12)
    wb.save(path)
    return path


# --------------------------------------------------------------------------------------------------
# 3. The Debt-Free Date Planner
# --------------------------------------------------------------------------------------------------
N_DEBTS, N_MONTHS = 10, 360


def build_debt_planner(path: Path) -> Path:
    from openpyxl.chart import LineChart, Reference

    wb = Workbook()
    d = _sheet(wb, "Plan", "Your debt-free date",
               "List your debts, pick a method, set your extra payment. Everything else is worked out for you.",
               widths={"B": 22, "C": 13, "D": 10, "E": 13, "F": 12, "G": 10, "H": 13, "I": 14, "J": 14,
                       "K": 14, "L": 15, "M": 4},
               first=True)
    _label(d, "B5", "Method")
    _inp(d["C5"], "Avalanche")
    _list_validation(d, ["Avalanche", "Snowball", "Custom"], "C5")
    d["D5"] = "Avalanche = highest APR first (least interest). Snowball = smallest balance first. Custom = your order (column F)."
    d["D5"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _label(d, "B6", "Extra per month")
    _inp(d["C6"], 200, MONEY0)
    d["D6"] = "On top of all the minimums. When a debt is paid off, its minimum rolls into the next one automatically."
    d["D6"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _label(d, "B7", "First payment month")
    _inp(d["C7"], date(2026, 12, 1), "mmm yyyy")

    _header(d, 9, ["Debt", "Balance", "APR %", "Minimum / mo", "Custom order", "Order used",
                   "Paid off in month #", "Paid off", "Interest you'll pay", "Minimums only: months",
                   "Minimums only: interest"])
    first, last = 10, 10 + N_DEBTS - 1
    example = [("Store card", 900, 29.99, 35, 1), ("Credit card", 4200, 24.9, 105, 3),
               ("Personal loan", 1800, 11, 75, 2), ("Car loan", 6500, 7.9, 210, 4),
               ("Student loan", 14000, 5.5, 180, 5)]
    rng = lambda col: f"${col}${first}:${col}${last}"  # noqa: E731
    for i, r in enumerate(range(first, last + 1)):
        row = example[i] if i < len(example) else (None,) * 5
        _inp(d.cell(r, 2), row[0])
        _inp(d.cell(r, 3), row[1], MONEY)
        _inp(d.cell(r, 4), row[2], PCT)
        _inp(d.cell(r, 5), row[3], MONEY)
        _inp(d.cell(r, 6), row[4], "0")
        # hidden helper (col N): custom key, blanks go last in row order
        d.cell(r, 14, f"=IF(ISNUMBER(F{r}),F{r},100+ROW())")
        tie = f"(ROW({rng('C')})<ROW(C{r}))"
        active = f"({rng('C')}>0)"
        av = f"1+SUMPRODUCT({active}*(({rng('D')}>D{r})+({rng('D')}=D{r})*{tie}))"
        sb = f"1+SUMPRODUCT({active}*(({rng('C')}<C{r})+({rng('C')}=C{r})*{tie}))"
        cu = f"1+SUMPRODUCT({active}*(({rng('N')}<N{r})+({rng('N')}=N{r})*{tie}))"
        _calc(d.cell(r, 7), f'=IF(N(C{r})>0,IF($C$5="Snowball",{sb},IF($C$5="Custom",{cu},{av})),"")', "0")
        k = i  # schedule column offset for this debt
        end_col = get_column_letter(_SCH_END + k)
        min_col = get_column_letter(_SCH_MIN + k)
        ext_col = get_column_letter(_SCH_EXT + k)
        ends = f"Schedule!{end_col}$8:{end_col}${7 + N_MONTHS}"
        _calc(d.cell(r, 8), f'=IF(N(C{r})>0,IF(COUNTIF({ends},">0.005")>={N_MONTHS},"30+ years",'
                            f'COUNTIF({ends},">0.005")+1),"")', "0")
        _calc(d.cell(r, 9), f'=IF(ISNUMBER(H{r}),EDATE($C$7,H{r}-1),H{r})', "mmm yyyy")
        _calc(d.cell(r, 10), f'=IF(N(C{r})>0,SUM(Schedule!{min_col}$8:{min_col}${7 + N_MONTHS})'
                             f'+SUM(Schedule!{ext_col}$8:{ext_col}${7 + N_MONTHS})-C{r},"")', MONEY)
        _calc(d.cell(r, 11), f'=IF(N(C{r})>0,IF(N(E{r})<=C{r}*D{r}/1200,"Never",'
                             f'ROUNDUP(NPER(D{r}/1200,-E{r},C{r}),0)),"")', "0")
        _calc(d.cell(r, 12), f'=IF(ISNUMBER(K{r}),E{r}*NPER(D{r}/1200,-E{r},C{r})-C{r},"")', MONEY)
    d.column_dimensions["N"].hidden = True
    t = last + 1
    _label(d, f"B{t}", "Total")
    _calc(d[f"C{t}"], f"=SUM(C{first}:C{last})", MONEY)
    _calc(d[f"E{t}"], f'=SUMIF(C{first}:C{last},">0",E{first}:E{last})', MONEY)
    _calc(d[f"J{t}"], f"=SUM(J{first}:J{last})", MONEY)
    _calc(d[f"L{t}"], f"=SUM(L{first}:L{last})", MONEY)
    _total_row(d, t, 2, 12)
    ws_warn = f"N{first}:N{last}"  # noqa: F841  (helper column, hidden)
    d.conditional_formatting.add(f"E{first}:E{last}", FormulaRule(
        formula=[f"AND(N(C{first})>0,N(E{first})<=C{first}*D{first}/1200)"], fill=PatternFill("solid", fgColor="F8D7D3")))

    s = t + 2
    _label(d, f"B{s}", "Your plan", fill=F_CREAM)
    summary = [
        ("Total paid toward debt each month", f"=E{t}+N(C6)", MONEY),
        ("Months until debt-free", f'=IF(COUNTIF(H{first}:H{last},"30+ years")>0,"30+ years",MAX(H{first}:H{last}))', "0"),
        ("Debt-free date", f'=IF(ISNUMBER(C{s + 2}),EDATE(C7,C{s + 2}-1),"Increase payments")', "mmmm yyyy"),
        ("Total interest on this plan", f"=J{t}", MONEY),
        ("Minimums only: months until debt-free", f'=IF(COUNTIF(K{first}:K{last},"Never")>0,"Never",MAX(K{first}:K{last}))', "0"),
        ("Minimums only: total interest", f'=IF(COUNTIF(K{first}:K{last},"Never")>0,"Never",L{t})', MONEY),
        ("Interest you save with this plan", f'=IF(ISNUMBER(C{s + 6}),C{s + 6}-C{s + 4},"")', MONEY),
        ("Months sooner", f'=IF(AND(ISNUMBER(C{s + 5}),ISNUMBER(C{s + 2})),C{s + 5}-C{s + 2},"")', "0"),
    ]
    for i, (lab, f, fmt) in enumerate(summary):
        r = s + 1 + i
        _label(d, f"B{r}", lab, bold=False)
        _calc(d[f"C{r}"], f, fmt, bold=True)
    for r in (s + 3, s + 7):
        _total_row(d, r, 2, 3)
    d.merge_cells(f"B{s + 1}:B{s + 1}")
    note = s + 10
    d[f"B{note}"] = ("Red minimum = the minimum doesn't cover the monthly interest, so that balance never shrinks on "
                     "minimums alone. Interest is estimated monthly (APR / 12); your lender's daily calculation will "
                     "differ slightly. Change the method or the extra payment and watch the date move.")
    d[f"B{note}"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    d.freeze_panes = "C10"
    _foot(d, note + 2)

    _build_schedule(wb, first, last)

    # Balance transfer check
    b = _sheet(wb, "Balance Transfer", "Is a balance transfer worth it?",
               "Compares paying a card as it is vs moving it to a promo-rate card with a transfer fee.", tab=GOLD,
               widths={"B": 40, "C": 16, "D": 50})
    inputs = [("Balance to move", 3000, MONEY0), ("Current APR %", 24.9, PCT), ("What you can pay each month", 200, MONEY0),
              ("Transfer fee %", 3, PCT), ("Promo APR %", 0, PCT), ("Promo length (months)", 15, "0"),
              ("APR after the promo ends %", 27.99, PCT)]
    for i, (lab, v, fmt) in enumerate(inputs):
        _label(b, f"B{5 + i}", lab, bold=False)
        _inp(b[f"C{5 + i}"], v, fmt)
    rows = [
        ("Stay put: months to pay off", '=IF(C7<=C5*C6/1200,"Never",NPER(C6/1200,-C7,C5))', "0.0"),
        ("Stay put: interest", '=IF(ISNUMBER(C13),C7*C13-C5,"Never")', MONEY),
        ("Transfer: fee", "=C5*C8/100", MONEY),
        ("Transfer: balance left when the promo ends", "=MAX(0,-FV(C9/1200,C10,-C7,C5+C15))", MONEY),
        ("Transfer: months to pay off", '=IF(C16<=0,NPER(C9/1200,-C7,C5+C15),IF(C7<=C16*C11/1200,"Never",C10+NPER(C11/1200,-C7,C16)))', "0.0"),
        ("Transfer: total cost (fee + interest)", '=IF(ISNUMBER(C17),C7*C17-C5,"Never")', MONEY),
        ("You save by transferring", '=IF(AND(ISNUMBER(C14),ISNUMBER(C18)),C14-C18,"")', MONEY),
        ("Monthly payment to clear it inside the promo", "=IF(C9=0,(C5+C15)/C10,PMT(C9/1200,C10,-(C5+C15)))", MONEY),
    ]
    for i, (lab, f, fmt) in enumerate(rows):
        r = 13 + i
        _label(b, f"B{r}", lab, bold=(r in (19, 20)))
        _calc(b[f"C{r}"], f, fmt, bold=(r in (19, 20)))
    _total_row(b, 19, 2, 3)
    b["D19"] = '=IF(N(C19)>0,"Worth it, IF you stop adding new spending to either card.","Not worth it at this payment.")'
    b["B22"] = ("Check before you apply: the exact fee, how long the promo lasts, whether the promo needs a minimum "
                "payment every month, and the rate on new purchases. Applying is a hard credit inquiry.")
    b["B22"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _foot(b, 24)

    # Consolidation loan check
    c = _sheet(wb, "Consolidation", "Would a consolidation loan help?",
               "Compares one fixed-rate loan with your current plan (from the Plan tab).", tab=GOLD,
               widths={"B": 42, "C": 16, "D": 46})
    cin = [("Amount of debt to consolidate", f"=Plan!C{t}", MONEY0), ("Loan APR %", 12.5, PCT),
           ("Loan term (months)", 48, "0"), ("Origination fee %", 4, PCT)]
    for i, (lab, v, fmt) in enumerate(cin):
        _label(c, f"B{5 + i}", lab, bold=False)
        _inp(c[f"C{5 + i}"], v, fmt)
    c["D5"] = "Linked to your Plan total. Type a number to override."
    crow = [
        ("Loan size so the fee is covered", "=C5/(1-C8/100)", MONEY),
        ("Monthly loan payment", "=PMT(C6/1200,C7,-C10)", MONEY),
        ("Loan: total interest + fee", "=C11*C7-C5", MONEY),
        ("Loan: months to debt-free", "=C7", "0"),
        ("Current plan: total interest", f"=Plan!J{t}", MONEY),
        ("Current plan: months to debt-free", f"=Plan!C{s + 2}", "0"),
        ("Current plan: monthly payment", f"=Plan!C{s + 1}", MONEY),
        ("Loan saves you (interest)", "=IF(ISNUMBER(C14),C14-C12,\"\")", MONEY),
    ]
    for i, (lab, f, fmt) in enumerate(crow):
        r = 10 + i
        _label(c, f"B{r}", lab, bold=(r == 17))
        _calc(c[f"C{r}"], f, fmt, bold=(r == 17))
    _total_row(c, 17, 2, 3)
    c["D17"] = '=IF(N(C17)>0,"Cheaper than your current plan.","Your current plan is cheaper. Keep going.")'
    c["B19"] = ("A loan only helps if the cards stay paid off. Watch for prepayment penalties, and compare the "
                "APR (which includes fees) across a few lenders. Pre-qualification usually uses a soft inquiry.")
    c["B19"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    _foot(c, 21)

    # Progress tracker + chart
    p = _sheet(wb, "Progress", "Progress tracker",
               "Once a month, type your actual total balance. See if you're ahead of the plan.", tab=INK,
               widths={"B": 12, "C": 16, "D": 16, "E": 14, "F": 14})
    _header(p, 5, ["Month", "Plan says", "Actual balance", "Ahead by", "% paid off"])
    for i in range(36):
        r = 6 + i
        _calc(p.cell(r, 2), f"=EDATE(Plan!$C$7,{i})", "mmm yyyy")
        _calc(p.cell(r, 3), f"=Schedule!{get_column_letter(_SCH_TOT)}{8 + i}", MONEY0)
        _inp(p.cell(r, 4), None, MONEY0)
        _calc(p.cell(r, 5), f'=IF(ISNUMBER(D{r}),C{r}-D{r},"")', MONEY0)
        _calc(p.cell(r, 6), f'=IF(ISNUMBER(D{r}),1-D{r}/Plan!$C${t},"")', "0%")
    chart = LineChart()
    chart.title = "Total debt: plan"
    chart.height, chart.width = 8, 16
    chart.y_axis.title = "Balance"
    chart.y_axis.numFmt = '"$"#,##0'
    data = Reference(wb["Schedule"], min_col=_SCH_TOT, min_row=7, max_row=7 + 120)
    chart.add_data(data, titles_from_data=True)
    chart.series[0].graphicalProperties.line.solidFill = GREEN
    chart.series[0].smooth = False
    p.add_chart(chart, "H5")
    _foot(p, 44)

    wb.move_sheet("Schedule", offset=len(wb.sheetnames) - 1 - wb.sheetnames.index("Schedule"))
    wb.save(path)
    return path


# Schedule layout: col B month #, then blocks of N_DEBTS columns
_SCH_OWED = 3
_SCH_MIN = _SCH_OWED + N_DEBTS
_SCH_EXT = _SCH_MIN + N_DEBTS
_SCH_END = _SCH_EXT + N_DEBTS
_SCH_LEFT = _SCH_END + N_DEBTS      # leftover after minimums
_SCH_TOT = _SCH_LEFT + 1            # total balance at month end
_SCH_DATE = _SCH_TOT + 1


def _build_schedule(wb, first: int, last: int):
    s = wb.create_sheet("Schedule")
    s.sheet_properties.tabColor = GREY
    s["B1"] = "Payoff schedule (calculated; no inputs here)"
    s["B1"].font = Font(name="Inter", size=14, bold=True)
    s["B2"] = ("Each month: interest is added, every debt gets its minimum, then the rest of your monthly debt budget "
               "goes to debts in the order shown in row 4.")
    L = get_column_letter
    owed = (L(_SCH_OWED), L(_SCH_OWED + N_DEBTS - 1))
    mins = (L(_SCH_MIN), L(_SCH_MIN + N_DEBTS - 1))
    for k in range(N_DEBTS):
        pr = first + k
        for block, title in ((_SCH_OWED, "Owed"), (_SCH_MIN, "Min paid"), (_SCH_EXT, "Extra paid"), (_SCH_END, "Balance")):
            col = block + k
            s.cell(3, col, f'=IF(Plan!$B${pr}="","Debt {k + 1}",Plan!$B${pr})')
            s.cell(7, col, title).font = Font(bold=True)
        s.cell(4, _SCH_OWED + k, f'=IF(ISNUMBER(Plan!$G${pr}),Plan!$G${pr},99)')
        s.cell(5, _SCH_OWED + k, f"=N(Plan!$D${pr})/1200")
        s.cell(6, _SCH_OWED + k, f"=N(Plan!$E${pr})")
    s["B4"], s["B5"], s["B6"] = "Order", "Monthly rate", "Minimum"
    s.cell(4, _SCH_LEFT, "Budget / mo")
    s.cell(5, _SCH_LEFT, f'=SUMIF(Plan!$C${first}:$C${last},">0",Plan!$E${first}:$E${last})+N(Plan!$C$6)')
    s["B7"] = "Month"
    s.cell(7, _SCH_LEFT, "Left after minimums").font = Font(bold=True)
    s.cell(7, _SCH_TOT, "Total balance").font = Font(bold=True)
    s.cell(7, _SCH_DATE, "Date").font = Font(bold=True)
    budget = f"${L(_SCH_LEFT)}$5"
    rank_row = f"${owed[0]}$4:${owed[1]}$4"
    for m in range(N_MONTHS):
        r = 8 + m
        s.cell(r, 2, m + 1)
        for k in range(N_DEBTS):
            oc, mc, ec, bc = (L(_SCH_OWED + k), L(_SCH_MIN + k), L(_SCH_EXT + k), L(_SCH_END + k))
            prev = f"N(Plan!$C${first + k})" if m == 0 else f"{bc}{r - 1}"
            s[f"{oc}{r}"] = f"=IF({prev}>0.005,{prev}*(1+{oc}$5),0)"
            s[f"{mc}{r}"] = f"=MIN({oc}{r},{oc}$6)"
            s[f"{ec}{r}"] = (f"=MAX(0,MIN({oc}{r}-{mc}{r},${L(_SCH_LEFT)}{r}-SUMPRODUCT(({rank_row}<{oc}$4)*"
                             f"(${owed[0]}{r}:${owed[1]}{r}-${mins[0]}{r}:${mins[1]}{r}))))")
            s[f"{bc}{r}"] = f"=MAX(0,{oc}{r}-{mc}{r}-{ec}{r})"
        s.cell(r, _SCH_LEFT, f"=MAX(0,{budget}-SUM(${mins[0]}{r}:${mins[1]}{r}))")
        s.cell(r, _SCH_TOT, f"=SUM({L(_SCH_END)}{r}:{L(_SCH_END + N_DEBTS - 1)}{r})").number_format = MONEY0
        s.cell(r, _SCH_DATE, f"=EDATE(Plan!$C$7,{m})").number_format = "mmm yyyy"
    s.freeze_panes = "C8"


# --------------------------------------------------------------------------------------------------
# 4. Start Investing With $100 a Month
# --------------------------------------------------------------------------------------------------
def build_investing(path: Path) -> Path:
    from openpyxl.chart import BarChart, Reference

    wb = Workbook()
    note = lambda ws, ref, text: (ws.__setitem__(ref, text),  # noqa: E731
                                  setattr(ws[ref], "font", Font(name="Inter", size=9, italic=True, color="4B5A51")))

    oc = _sheet(wb, "Order Checklist", "Where each dollar goes first",
                "Work down the list. Mark each step as you get to it. (Guide, chapter 2.)",
                widths={"B": 6, "C": 58, "D": 16, "E": 40}, first=True)
    _header(oc, 5, ["#", "Step", "Status", "Notes"])
    steps = [("401(k) / 403(b) up to the full employer match", "Done", "Contributing 4% = full match"),
             ("Pay off high-interest debt (above ~8-10%)", "In progress", "Store card gone; credit card next"),
             ("Starter emergency fund ($500-$1,000)", "Done", "HYSA"),
             ("Full emergency fund: 3-6 months of essentials", "Not started", ""),
             ("IRA: Roth or Traditional", "In progress", "$100/month to Roth IRA"),
             ("More in the 401(k), beyond the match", "Not started", ""),
             ("HSA, if you have a high-deductible health plan", "Not applicable", ""),
             ("Taxable brokerage account", "Not started", "")]
    for i, (st, status, n) in enumerate(steps):
        r = 6 + i
        _calc(oc.cell(r, 2), i + 1, "0", bold=True)
        oc.cell(r, 3, st).border = BOX
        _inp(oc.cell(r, 4), status)
        _inp(oc.cell(r, 5), n)
    _list_validation(oc, ["Not started", "In progress", "Done", "Not applicable"], "D6:D13")
    oc.conditional_formatting.add("D6:D13", CellIsRule(operator="equal", formula=['"Done"'],
                                  fill=PatternFill("solid", fgColor="CDEFD9")))
    _label(oc, "C15", "Steps done")
    _calc(oc["D15"], '=COUNTIF(D6:D13,"Done")&" of "&(8-COUNTIF(D6:D13,"Not applicable"))', bold=True)
    _foot(oc, 17)

    g = _sheet(wb, "Growth", "What regular investing might grow to",
               "An illustration using an assumed average return. Real returns vary and can be negative.", tab=GREEN,
               widths={"B": 34, "C": 14, "D": 16, "E": 16, "F": 16, "G": 4})
    gi = [("Starting amount", 0, MONEY0), ("Monthly investment", 100, MONEY0),
          ("Increase the monthly amount each year by %", 3, PCT), ("Assumed average yearly return %", 6, PCT),
          ("Years", 30, "0")]
    for i, (lab, v, fmt) in enumerate(gi):
        _label(g, f"B{5 + i}", lab, bold=False)
        _inp(g[f"C{5 + i}"], v, fmt)
    _header(g, 11, ["Year", "Monthly amount", "Put in (total)", "Value (end of year)", "Growth so far"])
    for y in range(1, 51):
        r = 11 + y
        _calc(g.cell(r, 2), f'=IF({y}<=$C$9,{y},"")', "0")
        _calc(g.cell(r, 3), f'=IF(ISNUMBER(B{r}),$C$6*(1+$C$7/100)^({y}-1),"")', MONEY)
        prev_in = "$C$5" if y == 1 else f"D{r - 1}"
        prev_val = "$C$5" if y == 1 else f"E{r - 1}"
        _calc(g.cell(r, 4), f'=IF(ISNUMBER(B{r}),{prev_in}+C{r}*12,"")', MONEY0)
        _calc(g.cell(r, 5), f'=IF(ISNUMBER(B{r}),IF($C$8=0,{prev_val}+C{r}*12,'
                            f'FV($C$8/1200,12,-C{r},-{prev_val})),"")', MONEY0)
        _calc(g.cell(r, 6), f'=IF(ISNUMBER(B{r}),E{r}-D{r},"")', MONEY0)
    _label(g, "B63", "After your chosen years")
    _calc(g["E63"], "=INDEX(E12:E61,MIN(C9,50))", MONEY0, bold=True)
    _calc(g["D63"], "=INDEX(D12:D61,MIN(C9,50))", MONEY0, bold=True)
    _total_row(g, 63, 2, 6)
    note(g, "B65", "Monthly compounding. No fees, taxes or inflation. Max 50 years. Not a prediction or a promise.")
    ch = BarChart()
    ch.type = "col"
    ch.grouping = "stacked"
    ch.overlap = 100
    ch.title = "Put in vs growth"
    ch.height, ch.width = 9, 17
    ch.add_data(Reference(g, min_col=4, min_row=11, max_row=11 + 30), titles_from_data=True)
    ch.add_data(Reference(g, min_col=6, min_row=11, max_row=11 + 30), titles_from_data=True)
    ch.set_categories(Reference(g, min_col=2, min_row=12, max_row=11 + 30))
    ch.series[0].graphicalProperties.solidFill = INK
    ch.series[1].graphicalProperties.solidFill = GREEN
    ch.y_axis.numFmt = '"$"#,##0'
    g.add_chart(ch, "H5")
    _foot(g, 67)

    f = _sheet(wb, "Fee Drag", "What a fund's fee costs you",
               "Same deposits, same market, two different yearly fees.", tab=GOLD,
               widths={"B": 38, "C": 16, "D": 16})
    fi = [("Starting amount", 0, MONEY0), ("Monthly investment", 200, MONEY0), ("Years", 30, "0"),
          ("Assumed yearly return before fees %", 7, PCT)]
    for i, (lab, v, fmt) in enumerate(fi):
        _label(f, f"B{5 + i}", lab, bold=False)
        _inp(f[f"C{5 + i}"], v, fmt)
    _header(f, 10, ["", "Fund A", "Fund B"])
    _label(f, "B11", "Yearly fee (expense ratio) %", bold=False)
    _inp(f["C11"], 0.04, '0.00"%"')
    _inp(f["D11"], 1.0, '0.00"%"')
    for col in ("C", "D"):
        _calc(f[f"{col}12"], f"=FV(($C$8-{col}11)/1200,$C$7*12,-$C$6,-$C$5)", MONEY0, bold=True)
    _label(f, "B12", "Ending value", bold=False)
    _label(f, "B13", "You put in", bold=False)
    _calc(f["C13"], "=C5+C6*12*C7", MONEY0)
    _calc(f["D13"], "=C5+C6*12*C7", MONEY0)
    _label(f, "B15", "Lost to the higher fee")
    _calc(f["C15"], "=ABS(C12-D12)", MONEY0, bold=True)
    _total_row(f, 15, 2, 4)
    note(f, "B17", "Simplified: the fee is subtracted from the yearly return. Illustration only.")
    _foot(f, 19)

    m = _sheet(wb, "401k Match", "Your employer match",
               "How much free money your employer adds, and whether you're leaving any behind.", tab=GOLD,
               widths={"B": 46, "C": 16, "D": 44})
    mi = [("Your yearly salary", 52000, MONEY0), ("You contribute (% of salary)", 4, PCT),
          ("Employer matches (% of what you put in)", 100, PCT),
          ("...on contributions up to (% of salary)", 4, PCT)]
    for i, (lab, v, fmt) in enumerate(mi):
        _label(m, f"B{5 + i}", lab, bold=False)
        _inp(m[f"C{5 + i}"], v, fmt)
    note(m, "D7", "e.g. '100% up to 4%', or '50% up to 6%'. Check your plan documents.")
    rows = [("You put in per year", "=C5*C6/100", MONEY0),
            ("Employer adds per year", "=C5*MIN(C6,C8)/100*C7/100", MONEY0),
            ("Maximum match available", "=C5*C8/100*C7/100", MONEY0),
            ("Match you're leaving on the table", "=C12-C11", MONEY0),
            ("Contribute at least this % to get it all", "=C8", PCT),
            ("Per paycheck to reach that (26 paychecks)", "=C5*C8/100/26", MONEY)]
    for i, (lab, fm, fmt) in enumerate(rows):
        r = 10 + i
        _label(m, f"B{r}", lab, bold=(r == 13))
        _calc(m[f"C{r}"], fm, fmt, bold=(r == 13))
    _total_row(m, 13, 2, 3)
    m["D13"] = '=IF(C13>0,"Raise your contribution: this is part of your pay.","You get the full match.")'
    note(m, "B17", "Some matches 'vest' over a few years: if you leave before then, you may keep only part. Check your plan.")
    _foot(m, 19)

    rt = _sheet(wb, "Roth vs Traditional", "Roth or Traditional?",
                "Same pre-tax money, two tax treatments. The one that wins depends on tax rates now vs later.",
                tab=GREEN, widths={"B": 44, "C": 16, "D": 16})
    ri = [("Pre-tax money you can set aside per year", 4000, MONEY0), ("Your tax rate now %", 12, PCT),
          ("Expected tax rate in retirement %", 22, PCT), ("Years until retirement", 35, "0"),
          ("Assumed yearly return %", 6, PCT)]
    for i, (lab, v, fmt) in enumerate(ri):
        _label(rt, f"B{5 + i}", lab, bold=False)
        _inp(rt[f"C{5 + i}"], v, fmt)
    _header(rt, 11, ["", "Roth", "Traditional"])
    rr = [("Goes into the account each year", "=C5*(1-C6/100)", "=C5"),
          ("Value at retirement (before tax)", "=FV(C9/100,C8,-C12)", "=FV(C9/100,C8,-D12)"),
          ("Tax when you withdraw", "=0", "=D13*C7/100"),
          ("What you keep", "=C13-C14", "=D13-D14")]
    for i, (lab, a, b_) in enumerate(rr):
        r = 12 + i
        _label(rt, f"B{r}", lab, bold=(r == 15))
        _calc(rt[f"C{r}"], a, MONEY0, bold=(r == 15))
        _calc(rt[f"D{r}"], b_, MONEY0, bold=(r == 15))
    _total_row(rt, 15, 2, 4)
    _label(rt, "B17", "Better choice with these numbers")
    _calc(rt["C17"], '=IF(ABS(C15-D15)<1,"Same",IF(C15>D15,"Roth","Traditional"))', bold=True)
    note(rt, "B19", "Simplified: assumes the Traditional tax saving is invested too, yearly compounding, flat tax "
                    "rates. Ignores income limits, state tax and employer matches. Illustration only.")
    _foot(rt, 21)

    c = _sheet(wb, "Contributions", "This year's contributions",
               "Log each deposit. Totals are checked against the yearly limits (2026 figures; update each year).",
               tab=INK, widths={"B": 14, "C": 22, "D": 14, "E": 30, "F": 4, "G": 26, "H": 14, "I": 14, "J": 14})
    _header(c, 5, ["Date", "Account", "Amount", "Note"])
    log = [(date(2026, 1, 2), "Roth IRA", 100), (date(2026, 2, 2), "Roth IRA", 100), (date(2026, 3, 2), "Roth IRA", 100)]
    for i, r in enumerate(range(6, 66)):
        row = log[i] if i < len(log) else (None,) * 3
        _inp(c.cell(r, 2), row[0], "yyyy-mm-dd")
        _inp(c.cell(r, 3), row[1])
        _inp(c.cell(r, 4), row[2], MONEY)
        _inp(c.cell(r, 5), None)
    accts = ["401(k) / 403(b)", "Roth IRA", "Traditional IRA", "HSA", "Taxable brokerage"]
    _list_validation(c, accts, "C6:C65")
    _header(c, 5, ["Account", "Yearly limit", "So far", "Room left"], col=7)
    limits = [24500, 7500, 7500, 4400, None]
    for i, (a, lim) in enumerate(zip(accts, limits)):
        r = 6 + i
        c.cell(r, 7, a).border = BOX
        _inp(c.cell(r, 8), lim, MONEY0)
        _calc(c.cell(r, 9), f'=SUMIF($C$6:$C$65,G{r},$D$6:$D$65)', MONEY0)
        _calc(c.cell(r, 10), f'=IF(ISNUMBER(H{r}),H{r}-I{r},"No limit")', MONEY0)
    note(c, "G12", "IRA limit is shared: Roth + Traditional together. HSA figure is self-only coverage.")
    note(c, "G13", "Check IRS.gov for the current year and catch-up amounts if you're 50+.")
    _calc(c["G15"], '=IF(I7+I8>H7,"Over the combined IRA limit!","IRA total within the limit")', bold=True)
    _foot(c, 68)
    wb.save(path)
    return path
