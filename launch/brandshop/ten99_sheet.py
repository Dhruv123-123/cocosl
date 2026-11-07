"""The 2027 Freelancer Tax Tracker workbook (Google Sheets / Excel / Numbers).

Tabs: Start, Setup, Income, Expenses, Mileage, Months, Quarters, Categories, Clients. Yellow cells are inputs; every
other number is a formula, so it recalculates in Google Sheets after import. It comes with a few made-up example rows.
Nothing here computes tax: the set-aside is profit x a percentage the user chooses.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from ten99 import BRAND, MONTHS, SCHEDULE_C, YEAR, estimated_due, fmt

ROWS = 400            # log rows per tab
INK, ACC, CREAM = BRAND.ink[1:], BRAND.warm[1:], BRAND.cream[1:]
YELLOW = "FFF4C2"

EXAMPLE_INCOME = [(date(YEAR, 1, 8), "Northwind Studio (example)", "INV-001", "Logo refresh", 1200, "Yes"),
                  (date(YEAR, 1, 22), "Example Client B", "INV-002", "Blog posts x4", 640, "Yes"),
                  (date(YEAR, 2, 12), "Marketplace payout (example)", "", "Template sales", 310, "No"),
                  (date(YEAR, 4, 3), "Northwind Studio (example)", "INV-003", "Brand guide", 1800, "Yes")]
EXAMPLE_EXPENSES = [(date(YEAR, 1, 5), "Design software (example)", "Software and subscriptions", 54.99, "Yes"),
                    (date(YEAR, 1, 19), "Office supplies (example)", "Supplies", 37.40, "Yes"),
                    (date(YEAR, 3, 2), "Online course (example)", "Education and training", 129, "Yes")]
EXAMPLE_MILES = [(date(YEAR, 1, 22), "Client meeting (example)", "Home office", "Client office", 18.4)]


def build(path: Path) -> Path:
    from openpyxl import Workbook
    from openpyxl.chart import BarChart, Reference
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    head_fill, head_font = PatternFill("solid", fgColor=INK), Font(bold=True, color="FFFFFF")
    inp = PatternFill("solid", fgColor=YELLOW)
    tot_fill = PatternFill("solid", fgColor="FDF0E8")
    thin = Border(bottom=Side(style="thin", color="D6D1C6"))
    bold = Font(bold=True)
    money = '"$"#,##0.00'

    def header(ws, row, labels, widths=None):
        for c, lab in enumerate(labels, 1):
            cell = ws.cell(row, c, lab)
            cell.fill, cell.font = head_fill, head_font
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[row].height = 30
        for c, w in enumerate(widths or [], 1):
            ws.column_dimensions[chr(64 + c)].width = w
        ws.freeze_panes = ws.cell(row + 1, 1)

    def title(ws, text, sub):
        ws["A1"] = text
        ws["A1"].font = Font(bold=True, size=16, color=INK)
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="5D6372")

    # Start
    st = wb.active
    st.title = "Start"
    title(st, f"{YEAR} Freelancer Tax Tracker", "1099 Money · an organising tool, not tax, legal or financial advice")
    lines = [
        "How it works",
        "1. Setup: type your set-aside % (yellow). Pick it with a tax professional or the IRS Form 1040-ES worksheet.",
        "2. Income: one row per payment you receive. Expenses: one row per business cost, with a category from the list.",
        "3. Mileage: one row per business trip. Type the IRS standard mileage rate for the year on Setup when it's published.",
        "4. Months, Quarters and Categories fill themselves in. Before each due date, look at Quarters and record what you paid.",
        "5. Clients: list each client once; the tab totals what they paid and you tick off each 1099 as it arrives.",
        "",
        "Yellow cells are inputs. White cells are formulas: leave them alone.",
        "The rows marked (example) are made up. Delete them before you start.",
        "Google Sheets: upload this file to Google Drive and open it with Google Sheets (File > Save as Google Sheets).",
        "",
        "Federal due dates follow the IRS weekend and holiday rule. Your state has its own rules. Check irs.gov.",
        "This workbook does not calculate your tax. The set-aside is simply profit x the percentage you choose.",
    ]
    for i, t in enumerate(lines, 4):
        st.cell(i, 1, t).font = bold if t in ("How it works",) else Font()
    st.column_dimensions["A"].width = 110

    # Setup
    su = wb.create_sheet("Setup")
    title(su, "Setup", "Yellow cells are yours to change")
    su["A4"], su["B4"] = "Tax year", YEAR
    su["A5"], su["B5"] = "Set-aside % of profit (your choice)", 0.25
    su["A6"], su["B6"] = "IRS standard mileage rate for the year ($ per mile; look it up on irs.gov)", 0
    su["A7"], su["B7"] = "Income goal for the year", 40000
    for r in (5, 6, 7):
        su.cell(r, 2).fill = inp
    su["B5"].number_format = "0%"
    su["B6"].number_format = '"$"0.000'
    su["B7"].number_format = money
    su["A9"] = "Expense categories (edit the yellow list; the Expenses tab's dropdown reads it)"
    su["A9"].font = bold
    for i, c in enumerate(SCHEDULE_C, 10):
        su.cell(i, 2, c).fill = inp
    su.column_dimensions["A"].width = 70
    su.column_dimensions["B"].width = 34
    cat_end = 10 + len(SCHEDULE_C) - 1 + 5          # five spare rows
    for r in range(10 + len(SCHEDULE_C), cat_end + 1):
        su.cell(r, 2).fill = inp
    cats = f"Setup!$B$10:$B${cat_end}"

    date_dv = lambda: DataValidation(type="date", operator="between", formula1=f"DATE({YEAR},1,1)",  # noqa: E731
                                     formula2=f"DATE({YEAR},12,31)", showErrorMessage=True,
                                     errorTitle="Date", error=f"Use a date in {YEAR}.")

    # Income
    inc = wb.create_sheet("Income")
    header(inc, 1, ["Date paid", "Client", "Invoice #", "What for", "Amount", "1099 expected?", "Month", "Quarter",
                    "Set aside"], [13, 30, 12, 26, 13, 14, 9, 9, 13])
    yn = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    dv = date_dv()
    inc.add_data_validation(yn)
    inc.add_data_validation(dv)
    for r in range(2, ROWS + 2):
        for c in range(1, 7):
            inc.cell(r, c).fill = inp
        inc.cell(r, 1).number_format = "mmm d, yyyy"
        inc.cell(r, 5).number_format = money
        inc.cell(r, 7, f'=IF(A{r}="","",MONTH(A{r}))')
        inc.cell(r, 8, f'=IF(A{r}="","",IF(MONTH(A{r})<=3,1,IF(MONTH(A{r})<=5,2,IF(MONTH(A{r})<=8,3,4))))')
        inc.cell(r, 9, f'=IF(E{r}="","",E{r}*Setup!$B$5)').number_format = money
    dv.add(f"A2:A{ROWS + 1}")
    yn.add(f"F2:F{ROWS + 1}")
    for i, row in enumerate(EXAMPLE_INCOME, 2):
        for c, v in enumerate(row, 1):
            inc.cell(i, c, v)

    # Expenses
    ex = wb.create_sheet("Expenses")
    header(ex, 1, ["Date", "Paid to", "Category", "Amount", "Receipt saved?", "Month", "Quarter"], [13, 30, 30, 13, 14, 9, 9])
    cdv = DataValidation(type="list", formula1=f"={cats}", allow_blank=True)
    yn2 = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    dv2 = date_dv()
    for v in (cdv, yn2, dv2):
        ex.add_data_validation(v)
    for r in range(2, ROWS + 2):
        for c in range(1, 6):
            ex.cell(r, c).fill = inp
        ex.cell(r, 1).number_format = "mmm d, yyyy"
        ex.cell(r, 4).number_format = money
        ex.cell(r, 6, f'=IF(A{r}="","",MONTH(A{r}))')
        ex.cell(r, 7, f'=IF(A{r}="","",IF(MONTH(A{r})<=3,1,IF(MONTH(A{r})<=5,2,IF(MONTH(A{r})<=8,3,4))))')
    cdv.add(f"C2:C{ROWS + 1}")
    yn2.add(f"E2:E{ROWS + 1}")
    dv2.add(f"A2:A{ROWS + 1}")
    for i, row in enumerate(EXAMPLE_EXPENSES, 2):
        for c, v in enumerate(row, 1):
            ex.cell(i, c, v)

    # Mileage
    mi = wb.create_sheet("Mileage")
    header(mi, 1, ["Date", "Business purpose", "From", "To", "Miles", "Value at IRS rate", "Month", "Quarter"],
           [13, 32, 20, 20, 10, 16, 9, 9])
    dv3 = date_dv()
    mi.add_data_validation(dv3)
    for r in range(2, ROWS + 2):
        for c in range(1, 6):
            mi.cell(r, c).fill = inp
        mi.cell(r, 1).number_format = "mmm d, yyyy"
        mi.cell(r, 6, f'=IF(E{r}="","",E{r}*Setup!$B$6)').number_format = money
        mi.cell(r, 7, f'=IF(A{r}="","",MONTH(A{r}))')
        mi.cell(r, 8, f'=IF(A{r}="","",IF(MONTH(A{r})<=3,1,IF(MONTH(A{r})<=5,2,IF(MONTH(A{r})<=8,3,4))))')
    dv3.add(f"A2:A{ROWS + 1}")
    for i, row in enumerate(EXAMPLE_MILES, 2):
        for c, v in enumerate(row, 1):
            mi.cell(i, c, v)

    rng = lambda ws, col: f"{ws}!${col}$2:${col}${ROWS + 1}"  # noqa: E731

    # Months
    mo = wb.create_sheet("Months")
    title(mo, f"{YEAR} month by month", "Fills itself in from Income, Expenses and Mileage")
    header(mo, 4, ["Month", "Income", "Expenses", "Mileage value", "Profit", "Set aside", "Running profit"],
           [14, 14, 14, 15, 14, 14, 16])
    mo.freeze_panes = "A5"
    for i, m in enumerate(MONTHS, 1):
        r = 4 + i
        mo.cell(r, 1, m)
        mo.cell(r, 2, f"=SUMIFS({rng('Income', 'E')},{rng('Income', 'G')},{i})")
        mo.cell(r, 3, f"=SUMIFS({rng('Expenses', 'D')},{rng('Expenses', 'F')},{i})")
        mo.cell(r, 4, f"=SUMIFS({rng('Mileage', 'F')},{rng('Mileage', 'G')},{i})")
        mo.cell(r, 5, f"=B{r}-C{r}-D{r}")
        mo.cell(r, 6, f"=MAX(0,E{r})*Setup!$B$5")
        mo.cell(r, 7, f"=E{r}" if i == 1 else f"=G{r - 1}+E{r}")
        for c in range(2, 8):
            mo.cell(r, c).number_format = money
            mo.cell(r, c).border = thin
    tr = 17
    mo.cell(tr, 1, "Year").font = bold
    for c, col in zip(range(2, 7), "BCDEF"):
        cell = mo.cell(tr, c, f"=SUM({col}5:{col}16)")
        cell.number_format, cell.font, cell.fill = money, bold, tot_fill
    mo.cell(tr, 1).fill = tot_fill
    mo.cell(19, 1, "Income goal")
    mo.cell(19, 2, "=Setup!B7").number_format = money
    mo.cell(20, 1, "Share of goal reached")
    mo.cell(20, 2, "=IF(Setup!B7=0,0,B17/Setup!B7)").number_format = "0%"
    chart = BarChart()
    chart.type, chart.style, chart.title = "col", 10, f"{YEAR} income and expenses by month"
    chart.add_data(Reference(mo, min_col=2, min_row=4, max_col=3, max_row=16), titles_from_data=True)
    chart.set_categories(Reference(mo, min_col=1, min_row=5, max_row=16))
    chart.height, chart.width = 8, 18
    mo.add_chart(chart, "I4")

    # Quarters
    qu = wb.create_sheet("Quarters")
    title(qu, f"Estimated tax for {YEAR} income", "Federal due dates (weekend and holiday rule applied). Check irs.gov and your state.")
    header(qu, 4, ["Payment", "Covers", "Due", "Income", "Expenses + mileage", "Profit", "Set aside",
                   "Federal paid", "State paid", "Date paid", "Confirmation #"], [10, 24, 20, 13, 17, 13, 13, 13, 13, 13, 18])
    qu.freeze_panes = "A5"
    for i, (name, period, d) in enumerate(estimated_due(), 1):
        r = 4 + i
        qu.cell(r, 1, name).font = bold
        qu.cell(r, 2, period)
        qu.cell(r, 3, fmt(d))
        qu.cell(r, 4, f"=SUMIFS({rng('Income', 'E')},{rng('Income', 'H')},{i})")
        qu.cell(r, 5, f"=SUMIFS({rng('Expenses', 'D')},{rng('Expenses', 'G')},{i})+SUMIFS({rng('Mileage', 'F')},{rng('Mileage', 'H')},{i})")
        qu.cell(r, 6, f"=D{r}-E{r}")
        qu.cell(r, 7, f"=MAX(0,F{r})*Setup!$B$5")
        for c in range(8, 12):
            qu.cell(r, c).fill = inp
        for c in (4, 5, 6, 7, 8, 9):
            qu.cell(r, c).number_format = money
        qu.cell(r, 10).number_format = "mmm d, yyyy"
    qu.cell(9, 1, "Year").font = bold
    for c, col in zip(range(4, 10), "DEFGHI"):
        cell = qu.cell(9, c, f"=SUM({col}5:{col}8)")
        cell.number_format, cell.font, cell.fill = money, bold, tot_fill
    qu.cell(11, 1, "Set aside minus federal and state paid so far")
    qu.cell(11, 7, "=G9-H9-I9").number_format = money
    qu.cell(12, 1, "Q2 covers two months and Q4 four. Record each payment's confirmation number.").font = Font(italic=True, color="5D6372")

    # Categories
    ca = wb.create_sheet("Categories")
    title(ca, f"{YEAR} expenses by category", "For whoever prepares your return. Deductibility depends on your situation.")
    header(ca, 4, ["Category", "Total", "Share of expenses"], [36, 14, 18])
    ca.freeze_panes = "A5"
    n = cat_end - 10 + 1
    for i in range(n):
        r = 5 + i
        ca.cell(r, 1, f'=IF(Setup!B{10 + i}="","",Setup!B{10 + i})')
        ca.cell(r, 2, f'=IF(A{r}="","",SUMIFS({rng("Expenses", "D")},{rng("Expenses", "C")},A{r}))').number_format = money
        ca.cell(r, 3, f'=IF(OR(A{r}="",SUM(Expenses!$D$2:$D${ROWS + 1})=0),"",B{r}/SUM(Expenses!$D$2:$D${ROWS + 1}))').number_format = "0%"
    end = 5 + n
    ca.cell(end, 1, "Mileage (value at the IRS rate)")
    ca.cell(end, 2, f"=SUM({rng('Mileage', 'F')})").number_format = money
    ca.cell(end + 1, 1, "Total").font = bold
    c = ca.cell(end + 1, 2, f"=SUM(B5:B{end})")
    c.number_format, c.font, c.fill = money, bold, tot_fill
    ca.cell(end + 3, 1, "Uncategorised expenses (fix these)")
    ca.cell(end + 3, 2, f'=SUMIFS({rng("Expenses", "D")},{rng("Expenses", "C")},"")').number_format = money

    # Clients
    cl = wb.create_sheet("Clients")
    header(cl, 1, ["Client (type it exactly as on the Income tab)", "W-9 sent?", f"Paid in {YEAR}", "1099 expected?",
                   "1099 received?", "Amount on the form", "Difference"], [40, 11, 15, 15, 15, 18, 14])
    yn3 = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    cl.add_data_validation(yn3)
    for r in range(2, 62):
        for col in (1, 2, 4, 5, 6):
            cl.cell(r, col).fill = inp
        cl.cell(r, 3, f'=IF(A{r}="","",SUMIFS({rng("Income", "E")},{rng("Income", "B")},A{r}))').number_format = money
        cl.cell(r, 6).number_format = money
        cl.cell(r, 7, f'=IF(OR(A{r}="",F{r}=""),"",F{r}-C{r})').number_format = money
    yn3.add("B2:B61")
    yn3.add("D2:E61")
    for i, name in enumerate(dict.fromkeys(x[1] for x in EXAMPLE_INCOME), 2):
        cl.cell(i, 1, name)

    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = ACC if ws.title in ("Income", "Expenses", "Mileage") else INK
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path
