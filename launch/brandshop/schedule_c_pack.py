"""1099 Money: the Schedule C Setup Pack for TaxHacker users ($12).

TaxHacker (https://github.com/vas3k/TaxHacker, MIT, Copyright (c) 2025 Vasily Zubarev) is a self-hosted receipt app.
This pack ships none of its code: it is a guide, a category and field list to type into TaxHacker's own Settings, and a
spreadsheet that reads TaxHacker's CSV export. It was written against the TaxHacker 0.8.5 source (commit 636b6b9,
Oct 31 2026) and has NOT yet been tried in a live install: see BLOCKER below.

What the source shows (and why the pack is shaped this way):
- Categories have a name, a colour and an "LLM prompt"; the AI is told "<code>: for <prompt>", so prompts are noun lists.
  A category's code is its name slugified, cut to 16 characters, so names must differ in their first 16.
- Custom fields have a name, a type (string, number, boolean) and an optional prompt; an empty prompt means "fill in by
  hand". Extra fields export like the built-in ones.
- CSV export (Transactions > Export) uses the field *names* as headers, in the order the user ticks them; Category
  exports the category name, Total is in currency units, Issued At is yyyy-MM-dd, Type is "income" or "expense".
  So the spreadsheet finds columns by header name, not by position.
- Settings > Backups can restore a zip, but restoring first deletes all existing data. The pack never asks anyone to
  restore a backup: categories and fields are typed in by hand (about 15 minutes), with the JSON as a reference.

Nothing here computes tax. The set-aside is profit x a percentage the user chooses. The "what counts" pages were checked
against the IRS 2025 Instructions for Schedule C on Nov 7 2026 and need a human check each January.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

import ten99 as T
from shop import etsy_description

BRAND = T.BRAND
P = BRAND.page
TH_VERSION = "0.8.5"
TH_URL = "https://github.com/vas3k/TaxHacker"
YEAR = 2026                      # the packet is for the return filed in 2027; the user can change it on Settings
ROWS = 2000                      # pasted CSV rows the Work tab reads
FLAG_AT = 75
BLOCKER = ("BLOCKER before listing: install TaxHacker 0.8.5 with made-up receipts, add these categories and fields, run "
           "30 sample receipts through it, export the CSV and paste it into the packet. Fix any prompt that sorts badly, "
           "and confirm the menu names in the guide. Until then it is untested in a live install.")

LINES = {  # Schedule C (Form 1040) lines used by the pack, per the 2025 instructions
    "Line 1": "Gross receipts or sales",
    "Line 8": "Advertising",
    "Line 9": "Car and truck expenses",
    "Line 10": "Commissions and fees",
    "Line 11": "Contract labor",
    "Line 13": "Depreciation and section 179",
    "Line 15": "Insurance (other than health)",
    "Line 16b": "Interest (other)",
    "Line 17": "Legal and professional services",
    "Line 18": "Office expense",
    "Line 20b": "Rent or lease (other business property)",
    "Line 21": "Repairs and maintenance",
    "Line 22": "Supplies",
    "Line 23": "Taxes and licenses",
    "Line 24a": "Travel",
    "Line 24b": "Deductible meals",
    "Line 25": "Utilities",
    "Line 26": "Wages",
    "Line 27b": "Other expenses (list them in Part V)",
    "Line 30": "Business use of home",
}
OTHER = {"Not Schedule C": "Goes somewhere else on the return, or nowhere (see the note)",
         "Personal": "Not a business cost",
         "Ask": "Ask your preparer which line"}

# (name, line, LLM prompt, colour, note for the preparer)
CATEGORIES = [
    ("Client income", "Line 1", "payments from clients or platforms for your work: invoice payments, payouts from "
     "Stripe, PayPal, Upwork, Fiverr, delivery and rideshare apps", "#3cc6a0", "Record it as income (Type = income)."),
    ("Advertising", "Line 8", "ads, boosted posts, business cards, flyers, promo items with your logo, sponsorships",
     "#ff7a45", ""),
    ("Car and truck", "Line 9", "fuel, car repairs, oil changes, car insurance and registration for a vehicle used for "
     "work", "#c4532a", "Only with the actual-cost method. With the standard mileage rate, use the Mileage tab instead."),
    ("Parking and tolls", "Line 9", "parking fees and road tolls on work trips", "#e08a5e",
     "Deductible with either car method."),
    ("Platform fees", "Line 10", "fees and commissions a marketplace, app or payment processor kept from your "
     "earnings, card processing fees", "#7a5cc4", "If a 1099-K shows the gross amount, report the gross as income and the fees here."),
    ("Contract labor", "Line 11", "payments to freelancers or contractors who did work for your business, not employees",
     "#5b7bd5", "Ask whether you need to send them a Form 1099-NEC."),
    ("Equipment", "Line 13", "computers, phones, cameras, monitors, furniture and tools that last more than a year",
     "#14213d", "Your preparer chooses depreciation, section 179, or the de minimis safe harbor for cheaper items."),
    ("Business insurance", "Line 15", "business liability, professional (errors and omissions) and equipment insurance, "
     "not health insurance", "#2f8f9d", ""),
    ("Loan interest", "Line 16b", "interest on a business loan or a business credit card", "#8a6d3b",
     "Business share only."),
    ("Professional fees", "Line 17", "accountants, tax preparers, lawyers, bookkeepers and consultants for the business",
     "#4a6fa5", ""),
    ("Office expense", "Line 18", "postage, shipping, printer ink, paper, pens and small office items", "#6c8ead", ""),
    ("Coworking and rent", "Line 20b", "coworking memberships, studio or office rent, a storage unit for business things",
     "#9d6b53", "Not your home: home costs go in Home office."),
    ("Repairs", "Line 21", "repairs and maintenance of business equipment", "#a3a847", ""),
    ("Supplies", "Line 22", "materials and supplies used up in your work, props, packaging, small tools under a year of "
     "use", "#d1a300", ""),
    ("Taxes and licenses", "Line 23", "business licenses, permits, state business registration fees", "#b55d5d",
     "Never federal income tax or estimated tax payments."),
    ("Travel", "Line 24a", "flights, hotels, trains, rental cars and rideshares on overnight business trips away from home",
     "#3a86ff", "Overnight trips away from your tax home. Commuting doesn't count."),
    ("Business meals", "Line 24b", "restaurant and cafe bills with clients or while traveling for work", "#fb5607",
     "Usually 50% deductible: the sheet shows the full amount and your preparer applies the limit."),
    ("Phone and internet", "Line 25", "mobile phone bills, home internet, a second phone line", "#00a6a6",
     "Business share only (use Business %). Some preparers put this in Part V instead."),
    ("Software and subs", "Line 27b", "software, apps, subscriptions, web hosting, domain names, cloud storage",
     "#8338ec", "Part V other expense."),
    ("Education", "Line 27b", "courses, workshops, conferences, books and trade publications for your current work",
     "#ff006e", "Must keep or improve skills for the work you already do."),
    ("Bank fees", "Line 27b", "business bank account fees, wire fees, overdraft fees on the business account",
     "#6d6875", "Part V other expense."),
    ("Business gifts", "Line 27b", "gifts to clients or business contacts", "#e76f51",
     "Generally limited to $25 per person per year."),
    ("Home office", "Line 30", "rent, renter's insurance, electricity, heating and water for the home where you have a "
     "home office", "#264653", "Your preparer works out the business share (simplified method or Form 8829)."),
    ("Health insurance", "Not Schedule C", "health, dental and vision insurance premiums for yourself", "#2a9d8f",
     "Self-employed health insurance goes on Schedule 1, not Schedule C."),
    ("Tax and transfers", "Not Schedule C", "estimated tax payments to the IRS or a state, transfers between your own "
     "accounts, retirement contributions", "#5d6372", "Not a business expense. Keep them for your records."),
    ("Personal", "Personal", "groceries, clothing, personal care, entertainment and anything not for the business",
     "#9aa0a6", "Kept out of every total."),
]

# TaxHacker's own default category names (models/defaults-data.ts, 0.8.5), for people who keep them. Our best guess at
# the line; the guide says to check them or switch to the pack's categories.
DEFAULT_NAMES = [("Advertisement", "Line 8"), ("Swag and Goods", "Line 8"), ("Gifts and Donations", "Ask"),
                 ("Equipment and Tools", "Line 13"), ("Events and Conferences", "Line 27b"), ("Food and Drinks", "Line 24b"),
                 ("Insurance", "Ask"), ("Invoice", "Ask"), ("Mobile and Internet", "Line 25"), ("Office Supplies", "Line 18"),
                 ("Online Services", "Line 27b"), ("Rental", "Line 20b"), ("Education", "Line 27b"), ("Salary", "Line 26"),
                 ("Fees", "Line 10"), ("Travel Expenses", "Line 24a"), ("Utility Bills", "Ask"), ("Transport", "Ask"),
                 ("Software", "Line 27b"), ("Other", "Ask")]

# (name, type, LLM prompt or "" for fill-in-by-hand, what it's for)
FIELDS = [
    ("Business %", "number", "", "Type 0 to 100 when a receipt is part personal (a phone bill used half for work is 50). "
     "Leave blank when it's all business."),
    ("Deductible?", "string", "write yes if this is clearly a business purchase, no if it is clearly personal "
     "(groceries, clothing, personal care), otherwise write ask", "A first sort by the AI. You and your preparer decide."),
    ("Preparer note", "string", "", "Who, what for, and why it's business. The sheet lists every receipt over $75 "
     "without a note."),
]

EXPORT_COLUMNS = ["Name", "Merchant", "Issued At", "Category", "Total", "Currency", "Type", "Note", "Business %",
                  "Deductible?", "Preparer note"]
REQUIRED = ["Issued At", "Category", "Type", "Total"]


def code_of(name: str) -> str:
    """TaxHacker's codeFromName: slugify (lowercase, strict, '_' separator), first 16 characters."""
    s = name.lower().replace("%", " percent ").replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:16]


def mapping_rows() -> list[dict]:
    rows = [dict(name=n, code=code_of(n), schedule_c_line=l, line_label=LINES.get(l, OTHER.get(l, "")), llm_prompt=p,
                 color=c, note=note, source="pack") for n, l, p, c, note in CATEGORIES]
    ours = {r["name"] for r in rows}
    rows += [dict(name=n, code=code_of(n), schedule_c_line=l, line_label=LINES.get(l, OTHER.get(l, "")), llm_prompt="",
                  color="", note="TaxHacker default category: check it, or move these receipts to a pack category.",
                  source="taxhacker default") for n, l in DEFAULT_NAMES if n not in ours]
    return rows


def write_mapping(d: Path) -> tuple[Path, Path]:
    rows = mapping_rows()
    c = d / "Schedule-C-Category-Map.csv"
    with open(c, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    j = d / "Schedule-C-Category-Map.json"
    j.write_text(json.dumps({
        "about": ("1099 Money Schedule C Setup Pack: categories and fields to type into TaxHacker's Settings by hand. "
                  "This is a reference, not a TaxHacker backup: don't restore it, because restoring a backup deletes "
                  "your existing data. Not affiliated with TaxHacker. An organising aid, not tax advice."),
        "written_for": f"TaxHacker {TH_VERSION}",
        "categories": rows,
        "fields": [dict(name=n, type=t, llm_prompt=p, purpose=why) for n, t, p, why in FIELDS],
        "export_columns": EXPORT_COLUMNS,
    }, indent=2) + "\n")
    return c, j


# ---------------------------------------------------------------- the year-end packet workbook

EXAMPLES = [  # (Name, Merchant, Issued At, Category, Total, Type, Note, Business %, Preparer note)
    ("Logo project (example)", "Northwind Studio", "2026-01-12", "Client income", 1800, "income", "", "", ""),
    ("Design app (example)", "Design software", "2026-01-05", "Software and subs", 15, "expense", "", "", ""),
    ("Laptop (example)", "Computer store", "2026-02-20", "Equipment", 1299, "expense", "", "", ""),
    ("Phone bill (example)", "Phone company", "2026-03-03", "Phone and internet", 80, "expense", "", 50, "Half for work"),
    ("Client lunch (example)", "Cafe", "2026-04-18", "Business meals", 62.4, "expense", "", "", "Lunch with Northwind, Q2 scope"),
    ("Coworking passes (example)", "Coworking space", "2026-05-02", "Coworking and rent", 120, "expense", "", "", ""),
    ("Website build (example)", "Contoso Bakery", "2026-06-30", "Client income", 2400, "income", "", "", ""),
    ("Conference flight (example)", "Airline", "2026-09-10", "Travel", 340, "expense", "Design conference", "", ""),
    ("Groceries (example)", "Supermarket", "2026-09-12", "Personal", 95, "expense", "", "", ""),
    ("Q3 estimated tax (example)", "IRS", "2026-09-15", "Tax and transfers", 1200, "expense", "", "", ""),
    ("Parking (example)", "City garage", "2026-11-05", "Parking and tolls", 18, "expense", "", "", ""),
    ("Old receipt (example)", "Art supply store", "2025-12-28", "Supplies", 30, "expense", "", "", ""),
]
EXAMPLE_MILES = [(date(YEAR, 2, 3), "Client meeting (example)", "Home", "Northwind Studio", 14.2)]


def build_workbook(path: Path) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    ink = T.BRAND.ink.lstrip("#").upper()
    head_fill, head_font = PatternFill("solid", fgColor=ink), Font(bold=True, color="FFFFFF")
    inp = PatternFill("solid", fgColor="FFF4C2")
    grey = PatternFill("solid", fgColor="EEEEEE")
    bold = Font(bold=True)
    money = '"$"#,##0.00'

    def title(ws, text, sub):
        ws["A1"] = text
        ws["A1"].font = Font(bold=True, size=16, color=ink)
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="5D6372")

    def header(ws, row, labels, widths):
        for c, lab in enumerate(labels, 1):
            cell = ws.cell(row, c, lab)
            cell.fill, cell.font = head_fill, head_font
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        for c, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, c).column_letter].width = w

    # Start
    st = wb.active
    st.title = "Start"
    title(st, "Year-End Packet for TaxHacker", "1099 Money · an organising tool, not tax, legal or financial advice")
    lines = [
        "How it works",
        "1. In TaxHacker, export your transactions as CSV for the year (the guide lists which columns to tick).",
        "2. Open the CSV, select everything, copy, and paste it into cell A1 of the 'Paste CSV' tab (replace the examples).",
        "3. Settings: check the tax year, your set-aside %, and that every required column says 'found'.",
        "4. 'By line' totals your receipts by Schedule C line. 'Quarters' shows each quarter's profit and set-aside.",
        "5. 'Missing notes' lists every business receipt at or over the amount on Settings that has no note. Add notes in",
        "   TaxHacker, export again, paste again.",
        "6. 'Mileage' is a standard-mileage log. Type the IRS rate for your year on Settings (irs.gov publishes it).",
        "7. Mapping: if you renamed a category in TaxHacker, rename it here too (yellow cells).",
        "",
        "Yellow cells are yours. White and grey cells are formulas: leave them alone.",
        "Google Sheets: upload this file to Google Drive and open it with Google Sheets (File > Save as Google Sheets).",
        "",
        "This workbook doesn't calculate your tax. Totals use the Business % on each receipt, nothing more: meal limits,",
        "depreciation and home-office shares are your preparer's call. Set-aside = profit x the percentage you choose.",
        f"Made by 1099 Money with the help of AI tools. Not affiliated with TaxHacker ({TH_URL}).",
    ]
    for i, t in enumerate(lines, 4):
        st.cell(i, 1, t).font = bold if t == "How it works" else Font()
    st.column_dimensions["A"].width = 115

    # Paste CSV (comes before Settings in formulas, so create it first)
    pc = wb.create_sheet("Paste CSV")
    for c, h in enumerate(EXPORT_COLUMNS, 1):
        pc.cell(1, c, h).font = bold
        pc.column_dimensions[pc.cell(1, c).column_letter].width = 18
    for r, ex in enumerate(EXAMPLES, 2):
        name, merch, day, cat, tot, typ, note, pct, pnote = ex
        vals = {"Name": name, "Merchant": merch, "Issued At": day, "Category": cat, "Total": tot, "Currency": "USD",
                "Type": typ, "Note": note, "Business %": pct, "Deductible?": "yes" if cat not in ("Personal", "Tax and transfers") else "no",
                "Preparer note": pnote}
        for c, h in enumerate(EXPORT_COLUMNS, 1):
            if vals[h] != "":
                pc.cell(r, c, vals[h])
    pc.freeze_panes = "A2"

    # Settings
    se = wb.create_sheet("Settings", 1)
    title(se, "Settings", "Yellow cells are yours to change")
    se["A4"], se["B4"] = "Tax year", YEAR
    se["A5"], se["B5"] = "Set-aside % of profit (your choice: pick it with a tax professional or the 1040-ES worksheet)", 0.25
    se["A6"], se["B6"] = "List business receipts with no note at or over", FLAG_AT
    se["A7"], se["B7"] = "IRS standard mileage rate for the tax year, $ per mile (look it up on irs.gov)", 0
    for r in (4, 5, 6, 7):
        se.cell(r, 2).fill = inp
    se["B5"].number_format = "0%"
    se["B6"].number_format = money
    se["B7"].number_format = '"$"0.000'
    se["A9"], se["B9"], se["C9"] = "Columns in your pasted CSV", "Column #", "Status"
    for c in (1, 2, 3):
        se.cell(9, c).fill, se.cell(9, c).font = head_fill, head_font
    col = {}
    for i, h in enumerate([h for h in EXPORT_COLUMNS if h != "Currency"], 10):
        col[h] = f"Settings!$B${i}"
        se.cell(i, 1, h)
        se.cell(i, 2, f"=IFERROR(MATCH(A{i},'Paste CSV'!$1:$1,0),0)")
        need = "REQUIRED: tick it in TaxHacker's export" if h in REQUIRED else "missing (optional)"
        se.cell(i, 3, f'=IF(B{i}>0,"found","{need}")')
    se.column_dimensions["A"].width = 80
    se.column_dimensions["B"].width = 12
    se.column_dimensions["C"].width = 40

    # Mapping
    mp = wb.create_sheet("Mapping")
    header(mp, 1, ["TaxHacker category name", "Schedule C line", "What the line is", "Note"], [30, 16, 40, 90])
    rows = mapping_rows()
    for r, m in enumerate(rows, 2):
        mp.cell(r, 1, m["name"]).fill = inp
        mp.cell(r, 2, m["schedule_c_line"]).fill = inp
        mp.cell(r, 3, m["line_label"])
        mp.cell(r, 4, m["note"])
    map_end = len(rows) + 1 + 15
    for r in range(len(rows) + 2, map_end + 1):
        mp.cell(r, 1).fill = mp.cell(r, 2).fill = inp
    mp.freeze_panes = "A2"

    # Work (helper)
    wk = wb.create_sheet("Work")
    heads = ["Raw date", "Date", "Year", "Quarter", "Who", "Category", "Type", "Total", "Business %", "Line",
             "Business amount", "Notes", "On Schedule C", "Missing note", "List #"]
    header(wk, 1, heads, [12, 12, 7, 8, 26, 22, 9, 11, 10, 14, 13, 30, 10, 10, 8])

    def g(h: str, r: int) -> str:
        return f"IF({col[h]}=0,\"\",INDEX('Paste CSV'!$A:$AZ,{r},{col[h]})&\"\")"

    for r in range(2, ROWS + 2):
        f = {
            "A": "=" + g("Issued At", r),
            "B": f'=IF(A{r}="","",IFERROR(DATEVALUE(A{r}),IFERROR(VALUE(A{r}),"")))',
            "C": f'=IF(B{r}="","",YEAR(B{r}))',
            "D": f'=IF(B{r}="","",IF(MONTH(B{r})<=3,"Q1",IF(MONTH(B{r})<=5,"Q2",IF(MONTH(B{r})<=8,"Q3","Q4"))))',
            "E": f'=IF({g("Merchant", r)}<>"",{g("Merchant", r)},{g("Name", r)})',
            "F": "=" + g("Category", r),
            "G": f'=LOWER({g("Type", r)})',
            "H": f'=IFERROR(ABS(VALUE({g("Total", r)})),0)',
            "I": f'=IFERROR(IF(VALUE({g("Business %", r)})>1,VALUE({g("Business %", r)})/100,VALUE({g("Business %", r)})),1)',
            "J": f'=IF(G{r}="income","Line 1",IF(F{r}="",IF(H{r}=0,"","Unmapped"),IFERROR(VLOOKUP(F{r},Mapping!$A$2:$B${map_end},2,FALSE),"Unmapped")))',
            "K": f'=IF(OR(G{r}="income",H{r}=0),0,H{r}*I{r})',
            "L": f'=TRIM({g("Note", r)}&" "&{g("Preparer note", r)})',
            "M": f'=IF(AND(LEFT(J{r},5)="Line ",J{r}<>"Line 1"),1,0)',
            "N": f'=IF(AND(M{r}=1,C{r}=Settings!$B$4,H{r}>=Settings!$B$6,L{r}=""),1,0)',
            "O": f'=IF(N{r}=1,COUNTIF($N$2:N{r},1),"")',
        }
        for k, v in f.items():
            wk[f"{k}{r}"] = v
        wk[f"B{r}"].number_format = "yyyy-mm-dd"
        wk[f"H{r}"].number_format = wk[f"K{r}"].number_format = money
        wk[f"I{r}"].number_format = "0%"
    wk.freeze_panes = "A2"
    W = lambda c: f"Work!${c}$2:${c}${ROWS + 1}"  # noqa: E731

    # By line
    bl = wb.create_sheet("By line", 2)
    title(bl, "Totals by Schedule C line", "For the tax year on Settings, after Business %")
    header(bl, 4, ["Line", "What the line is", "Total", "Receipts"], [14, 46, 16, 11])
    r = 5
    for line, label in list(LINES.items()) + list(OTHER.items()) + [("Unmapped", "Category not on the Mapping tab: add it there")]:
        bl.cell(r, 1, line)
        bl.cell(r, 2, label)
        if line == "Line 1":
            bl.cell(r, 3, f'=SUMIFS({W("H")},{W("G")},"income",{W("C")},Settings!$B$4)')
        else:
            bl.cell(r, 3, f'=SUMIFS({W("K")},{W("J")},A{r},{W("C")},Settings!$B$4)')
        bl.cell(r, 4, f'=COUNTIFS({W("J")},A{r},{W("C")},Settings!$B$4)')
        bl.cell(r, 3).number_format = money
        if line in ("Line 1", "Line 30"):
            last_c = r
        r += 1
    bl.cell(r + 1, 2, "Gross receipts (line 1)").font = bold
    bl.cell(r + 1, 3, "=C5").number_format = money
    bl.cell(r + 2, 2, "Schedule C expenses in this sheet (lines 8 to 30)").font = bold
    bl.cell(r + 2, 3, f"=SUM(C6:C{last_c})").number_format = money
    bl.cell(r + 3, 2, "Rough profit before your preparer's adjustments").font = bold
    bl.cell(r + 3, 3, f"=C{r + 1}-C{r + 2}").number_format = money
    bl.cell(r + 5, 1, "Line 24b shows the full meal amount; line 13 shows full equipment cost; line 30 shows home costs before "
                      "the business share. Your preparer applies those rules. Mileage is on its own tab.")

    # Quarters
    qt = wb.create_sheet("Quarters", 3)
    title(qt, "Quarter by quarter", "IRS estimated-tax periods; set-aside = profit x your % on Settings")
    header(qt, 4, ["Quarter", "Period", "Federal due date", "Income", "Expenses", "Profit", "Set aside"],
           [10, 24, 18, 14, 14, 14, 14])
    due = {y: T.estimated_due(y) for y in range(2025, 2030)}
    qt["J4"], qt["K4"], qt["L4"], qt["M4"] = "Year", "Quarter", "Due date (IRS weekend and holiday rule)", "Key"
    rr = 5
    for y, qs in due.items():
        for q, _, d in qs:
            qt.cell(rr, 10, y)
            qt.cell(rr, 11, q)
            qt.cell(rr, 12, d).number_format = "mmm d, yyyy"
            qt.cell(rr, 13, f"{y}{q}")
            rr += 1
    for i, (q, period) in enumerate([("Q1", "Jan 1 to Mar 31"), ("Q2", "Apr 1 to May 31"), ("Q3", "Jun 1 to Aug 31"),
                                     ("Q4", "Sep 1 to Dec 31")], 5):
        qt.cell(i, 1, q)
        qt.cell(i, 2, period)
        qt.cell(i, 3, f'=IFERROR(INDEX($L$5:$L${rr - 1},MATCH(Settings!$B$4&A{i},$M$5:$M${rr - 1},0)),"check irs.gov")')
        qt.cell(i, 3).number_format = "mmm d, yyyy"
        qt.cell(i, 4, f'=SUMIFS({W("H")},{W("G")},"income",{W("C")},Settings!$B$4,{W("D")},A{i})')
        qt.cell(i, 5, f'=SUMIFS({W("K")},{W("M")},1,{W("C")},Settings!$B$4,{W("D")},A{i})')
        qt.cell(i, 6, f"=D{i}-E{i}")
        qt.cell(i, 7, f"=MAX(0,F{i})*Settings!$B$5")
        for c in (4, 5, 6, 7):
            qt.cell(i, c).number_format = money
    qt["A9"] = "Year"
    qt["A9"].font = bold
    for c, L in zip((4, 5, 6, 7), "DEFG"):
        qt.cell(9, c, f"=SUM({L}5:{L}8)").number_format = money
        qt.cell(9, c).font = bold
    qt["A11"] = ("Q4 is paid in January of the next year. Your state may have its own dates. A set-aside is not a tax "
                 "calculation: 1099 Money's quarterly calculator [LINK: quarterly calculator] walks through one.")
    qt["A12"] = "Mileage isn't in these expenses: add the Mileage tab's value if you use the standard mileage rate."

    # Missing notes
    mn = wb.create_sheet("Missing notes", 4)
    title(mn, "Receipts that need a note", "Business receipts at or over the Settings amount, in the tax year, with no Note or Preparer note")
    mn["F1"] = "Count"
    mn["G1"] = f'=COUNTIF({W("N")},1)'
    header(mn, 4, ["#", "Date", "Who", "Category", "Total"], [6, 13, 30, 24, 13])
    for i in range(1, 301):
        r = i + 4
        mn.cell(r, 1, f'=IF({i}>$G$1,"",{i})')
        for c, L in ((2, "B"), (3, "E"), (4, "F"), (5, "H")):
            mn.cell(r, c, f'=IF($A{r}="","",INDEX({W(L)},MATCH($A{r},{W("O")},0)))')
        mn.cell(r, 2).number_format = "mmm d, yyyy"
        mn.cell(r, 5).number_format = money

    # Mileage
    mi = wb.create_sheet("Mileage", 5)
    title(mi, "Mileage log (standard mileage rate)", "One row per business trip. Commuting from home to a regular workplace doesn't count.")
    mi["F1"], mi["G1"] = "Miles", f"=SUM(E5:E{4 + 400})"
    mi["F2"], mi["G2"] = "Value", "=G1*Settings!$B$7"
    mi["G2"].number_format = money
    header(mi, 4, ["Date", "Purpose", "From", "To", "Miles", "Value"], [13, 34, 22, 22, 10, 12])
    for r in range(5, 405):
        for c in range(1, 6):
            mi.cell(r, c).fill = inp
        mi.cell(r, 1).number_format = "mmm d, yyyy"
        mi.cell(r, 6, f'=IF(E{r}="","",E{r}*Settings!$B$7)').number_format = money
    for r, row in enumerate(EXAMPLE_MILES, 5):
        for c, v in enumerate(row, 1):
            mi.cell(r, c, v)
    mi["H4"] = "Keep the log as you go: the IRS expects a record made at or near the time of each trip."
    for ws in (wk,):
        for c in range(1, 16):
            ws.cell(1, c).fill = grey
            ws.cell(1, c).font = Font(bold=True, color="333333")
    wk.sheet_properties.tabColor = "BBBBBB"
    wb.save(path)
    return path


# ---------------------------------------------------------------- the guide (PDF)

CSS = """
table.cats td{ font-size:8.2pt; height:auto; padding:3px 5px; vertical-align:top; line-height:1.25; }
table.cats th{ font-size:8.4pt; }
.code{ font-family:ui-monospace,Menlo,monospace; font-size:8pt; }
.tight li{ padding-bottom:5px; }
"""

CHEAT = [  # (expense, usually goes on, watch out for)
    ("Phone and internet", "Line 25 (some preparers use Part V)", "Business share only. The base rate of the first landline in your home never counts."),
    ("Home office", "Line 30", "Used regularly and only for work. Simplified method: $5 per square foot, up to 300 sq ft. Otherwise Form 8829."),
    ("Car", "Line 9", "Standard mileage rate or actual costs. Parking and tolls count with either. Commuting doesn't count."),
    ("Meals", "Line 24b", "Usually 50%. Note who you met and the business reason."),
    ("Travel", "Line 24a", "Overnight trips away from your tax home: flights, hotels, local transport there."),
    ("Computer, camera, furniture", "Line 13, or line 22 under the de minimis safe harbor", "Your preparer picks the method; keep the invoice."),
    ("Software and subscriptions", "Part V (line 27b)", "Business share only if you use it personally too."),
    ("Platform and card fees", "Line 10", "A 1099-K shows the gross: report the gross as income and the fees here."),
    ("Contractors you pay", "Line 11", "Ask whether you need to send a 1099-NEC."),
    ("Courses and conferences", "Part V (line 27b)", "Must keep or improve skills for the work you already do."),
    ("Gifts to clients", "Part V (line 27b)", "Generally $25 per person per year."),
    ("Health insurance", "Not Schedule C", "Self-employed health insurance goes on Schedule 1."),
    ("Retirement contributions", "Not Schedule C", "Your own SEP or solo 401(k) contributions go on Schedule 1."),
    ("Estimated tax payments", "Not an expense", "Record them so you can enter them on your return."),
    ("Everyday clothes, fines", "Not deductible", "Costumes and safety gear you can't wear day to day are different: ask."),
]


def _cat_rows(rows) -> str:
    return "".join(f"<tr><td><b>{n}</b></td><td>{l}</td><td>{p}</td></tr>" for n, l, p, *_ in rows)


def pages() -> list[str]:
    half = 13
    head = '<table class="cats"><tr><th style="width:22%">Category name</th><th style="width:13%">Line</th><th>LLM prompt (paste as is)</th></tr>'
    out = [
        P("Schedule C <em>Setup Pack</em>", "For TaxHacker users", f'''
          <p class="big">TaxHacker reads your receipts with AI. This pack sorts them the way a US freelancer's tax return
          does, so at year end you hand your preparer totals by Schedule C line instead of a shoebox.</p>
          <h3>What's in it</h3>
          <ol class="steps big tight">
            <li>26 categories, each with an AI prompt and its Schedule C line (pages 2 to 3).</li>
            <li>Three custom fields: Business %, Deductible? and Preparer note (page 4).</li>
            <li>The year-end packet: paste TaxHacker's CSV export, get totals by line, quarterly set-asides and a list of
            receipts that need a note (page 5).</li>
            <li>A mileage log, and a "what counts" cheat sheet (pages 5 to 6).</li>
            <li>The category list as CSV and JSON, for reference.</li>
          </ol>
          <h3>Before you start</h3>
          <p>Written for TaxHacker {TH_VERSION}. Menu names can move in later versions. Set Settings &gt; Default currency
          to USD. You'll type the categories in by hand (about 15 minutes). Don't restore the JSON as a backup:
          restoring a TaxHacker backup deletes your existing data.</p>
          <div class="box fineprint" style="margin-top:auto">TaxHacker is free, open-source software by Vasily Zubarev
          (MIT licence), at github.com/vas3k/TaxHacker. 1099 Money isn't affiliated with it, and this pack contains none
          of its code. An organising tool, not tax, legal or financial advice: confirm how anything is treated with a tax
          professional and irs.gov. Made by 1099 Money with the help of AI tools; a person checked every page.</div>''',
          kicker="1099 Money"),
        P("Step 1: <em>categories</em>", "Settings &gt; Categories", f'''
          <p>For each row: click add, type the name exactly, paste the prompt, pick any colour. Delete or keep TaxHacker's
          default categories; the packet's Mapping tab already has a best guess for each default name.</p>
          {head}{_cat_rows(CATEGORIES[:half])}</table>'''),
        P("Step 1, <em>continued</em>", "Settings &gt; Categories", f'''
          {head}{_cat_rows(CATEGORIES[half:])}</table>
          <p class="fineprint" style="margin-top:10px">Names differ in their first 16 characters on purpose: TaxHacker
          builds each category's code from the first 16. Rename a category later? Rename it on the packet's Mapping tab
          too. Prompts are a starting point: check how the AI sorts your first 20 receipts and adjust.</p>'''),
        P("Step 2: <em>fields</em> and export", "Settings &gt; Fields, then Transactions", '''
          <h3 style="margin-top:0">Add three fields</h3>
          <table class="cats"><tr><th style="width:18%">Name</th><th style="width:10%">Type</th><th style="width:36%">LLM prompt</th><th>What it's for</th></tr>'''
          + "".join(f"<tr><td><b>{n}</b></td><td>{t}</td><td>{p or '<i>leave empty: you fill it in</i>'}</td><td>{w}</td></tr>"
                    for n, t, p, w in FIELDS) + '''</table>
          <p>Tick "Show in transactions table" for all three so you can fill them in as you go.</p>
          <h3>Export for the packet</h3>
          <ol class="steps tight">
            <li>Transactions: filter to the tax year (January 1 to December 31).</li>
            <li>Export, CSV. Tick at least: Issued At, Category, Total, Type. Also tick Name, Merchant, Note, Business %
            and Preparer note.</li>
            <li>Keep "include attachments" on if you want a zip of the receipts for your preparer.</li>
          </ol>
          <p>Column order doesn't matter: the packet finds each column by its name.</p>'''),
        P("Step 3: the <em>year-end packet</em>", "Year-End-Packet.xlsx", '''
          <ol class="steps tight">
            <li>Open the workbook in Google Sheets (upload, then File &gt; Save as Google Sheets), Excel or Numbers.</li>
            <li>Open your CSV, copy everything, paste into cell A1 of <b>Paste CSV</b> over the examples.</li>
            <li><b>Settings</b>: set the tax year and your set-aside %. Every required column should say "found".</li>
          </ol>
          <table><tr><th style="width:22%">Tab</th><th>What it shows</th></tr>
          <tr><td class="wrap"><b>By line</b></td><td class="wrap">Totals by Schedule C line after Business %, gross receipts and a rough profit.</td></tr>
          <tr><td class="wrap"><b>Quarters</b></td><td class="wrap">Each IRS estimated-tax period: income, expenses, profit, set-aside and the federal due date.</td></tr>
          <tr><td class="wrap"><b>Missing notes</b></td><td class="wrap">Business receipts at or over $75 (you can change it) with no note. Add notes in TaxHacker and export again.</td></tr>
          <tr><td class="wrap"><b>Mileage</b></td><td class="wrap">A standard-mileage log: date, purpose, from, to, miles. Type the IRS rate for your year on Settings.</td></tr>
          <tr><td class="wrap"><b>Mapping</b></td><td class="wrap">Which category goes to which line. Yellow cells are yours to change.</td></tr></table>
          <h3>Hand it over</h3>
          <p>Give your preparer the By line and Quarters tabs (print to PDF), the mileage log, your 1099s, and the receipts
          zip from TaxHacker's export.</p>
          <div class="box fineprint" style="margin-top:auto">The packet doesn't calculate tax. It totals what you recorded.
          Meal limits, depreciation and the home-office share are your preparer's call.</div>'''),
        P("What <em>counts</em>", "Common 1099 expenses", '''
          <table class="cats"><tr><th style="width:24%">Expense</th><th style="width:26%">Usually goes on</th><th>Watch out for</th></tr>'''
          + "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in CHEAT) + '''</table>
          <p class="fineprint" style="margin-top:10px">Checked against the IRS 2025 Instructions for Schedule C (Form 1040)
          on November 7, 2026. Rules change: check irs.gov/instructions/i1040sc for your year. General information, not tax
          advice. Your situation decides what you can deduct.</p>'''),
    ]
    return out


# ---------------------------------------------------------------- listing

GET = ["A 6-page setup guide (US Letter and A4): 26 Schedule C categories with AI prompts, three custom fields, export steps",
       "The Year-End Packet (.xlsx for Google Sheets, Excel or Numbers): paste the CSV export, get totals by Schedule C line, "
       "quarterly set-asides and a list of receipts that need a note",
       "A standard-mileage log tab and a one-page \"what counts\" cheat sheet",
       "The category list as CSV and JSON"]
HOW = ["Type the categories and fields into TaxHacker's Settings (about 15 minutes).",
       "Snap receipts as usual; the AI sorts them into Schedule C categories.",
       "At year end, export the CSV, paste it into the packet and hand the totals to your preparer."]
GOOD = ["This is a DIGITAL DOWNLOAD. Nothing is shipped. Your files are in your Etsy account right after payment.",
        "For people who already use TaxHacker, the free open-source receipt app. You need your own TaxHacker install or account.",
        "Not affiliated with TaxHacker, and none of its code is included. Written for version 0.8.5.",
        "An organising tool, not tax, legal or financial advice. Confirm deductions with a tax professional."]
DISCLOSURE = "How it's made: written and built by 1099 Money. AI tools helped draft the text; a person checked every page and formula."
HOOK = ("Turn TaxHacker's receipt inbox into Schedule C totals: categories that match the tax form, three fields for "
        "business use and notes, and a year-end sheet that adds it all up for your preparer.")


def _gumroad() -> str:
    g = "\n".join(f"- {x}" for x in GET)
    return (f"{HOOK}\n\nWhat's inside:\n{g}\n\nInstant download: two PDFs, an .xlsx workbook, a CSV and a JSON file. "
            "$12, one payment, files you keep.\n\n"
            "Who it's for: US freelancers and side-hustlers who self-host TaxHacker or use its hosted version and file "
            "Schedule C. Who it's not for: if you don't use TaxHacker, 1099 Money's Quarterly Tax Tracker "
            "[LINK: Quarterly Tax Tracker product page] does the same sums without it.\n\n"
            f"TaxHacker is free, open-source software by Vasily Zubarev ({TH_URL}). 1099 Money isn't affiliated with it, "
            "and this pack contains none of its code.\n\n"
            "Educational content, not tax or financial advice. Made with the help of AI tools for drafting, and checked by "
            "a person. A problem with a file? Reply to your receipt email.")


LISTINGS = [
    dict(slug="schedule-c-setup-pack", name="Schedule C Setup Pack for TaxHacker", price=12.00, kind="kit",
         title="Schedule C Expense Categories and Year End Tax Packet Spreadsheet for Freelancers, Mileage Log",
         tags=["schedule c", "1099 tax", "freelancer taxes", "self employed", "tax spreadsheet", "expense categories",
               "mileage log", "receipt tracker", "year end taxes", "tax organizer", "small business", "bookkeeping",
               "google sheets"],
         attributes={"File type": "PDF, XLSX, CSV, JSON", "Software": "TaxHacker, Google Sheets, Microsoft Excel",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         category="Paper & Party Supplies > Paper > Calendars & Planners (digital)", status="active", review=BLOCKER,
         hook=HOOK)
]
for _it in LISTINGS:
    _it["description"] = etsy_description(HOOK, GET, HOW, GOOD, DISCLOSURE)
    _it["gumroad"] = _gumroad()
