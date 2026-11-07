"""1099 Money: the 2027 Freelancer Tax-Year Planner, as a printable and as a Google Sheets / Excel workbook.

Dates are worked out in code from the IRS rule: a due date on a weekend or a federal holiday moves to the next business
day. For 2027 that gives Q1 Apr 15, Q2 Jun 15, Q3 Sep 15 2027 and Q4 Jan 18 2028 (Jan 15 2028 is a Saturday and
Jan 17 is Martin Luther King Jr. Day). The planner never computes anyone's tax: it tracks income, expenses and a
set-aside percentage the user chooses, and says to confirm amounts with a tax professional and dates on irs.gov.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta

from shop import Brand

BRAND = Brand("1099 Money", "1099money", ink="#14213d", cream="#f7f3ea", accent="#3cc6a0", accent_d="#c4532a",
              warm="#ff7a45", tint="#fdf0e8", muted="#5d6372", line="#cdc8bd")
P = BRAND.page
YEAR = 2027
MONTHS = list(calendar.month_name)[1:]


def _nth(year: int, month: int, weekday: int, n: int) -> date:
    if n > 0:
        d = date(year, month, 1)
        return d + timedelta(days=(weekday - d.weekday()) % 7) + timedelta(weeks=n - 1)
    d = date(year, month, calendar.monthrange(year, month)[1])
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def federal_holidays(year: int) -> set[date]:
    """Observed US federal holidays (Saturday holidays observed Friday, Sunday holidays Monday)."""
    fixed = [date(year, 1, 1), date(year, 6, 19), date(year, 7, 4), date(year, 11, 11), date(year, 12, 25)]
    out = {_nth(year, 1, 0, 3), _nth(year, 2, 0, 3), _nth(year, 5, 0, -1), _nth(year, 9, 0, 1), _nth(year, 10, 0, 2),
           _nth(year, 11, 3, 4)}
    for d in fixed:
        out.add(d - timedelta(days=1) if d.weekday() == 5 else d + timedelta(days=1) if d.weekday() == 6 else d)
    if date(year + 1, 1, 1).weekday() == 5:          # next New Year's Day observed on Dec 31
        out.add(date(year, 12, 31))
    return out


def due(d: date) -> date:
    """IRS rule: a deadline on a weekend or federal holiday moves to the next business day.
    (DC's Emancipation Day, Apr 16, can also move the April date; it only matters when Apr 15 falls on a weekend.)"""
    hol = federal_holidays(d.year)
    if d.month == 4:
        e = date(d.year, 4, 16)
        hol.add(e - timedelta(days=1) if e.weekday() == 5 else e + timedelta(days=1) if e.weekday() == 6 else e)
    while d.weekday() >= 5 or d in hol:
        d += timedelta(days=1)
    return d


def estimated_due(year: int = YEAR) -> list[tuple[str, str, date]]:
    """The four estimated-tax payments for income earned in `year`."""
    return [("Q1", f"Jan 1 to Mar 31, {year}", due(date(year, 4, 15))),
            ("Q2", f"Apr 1 to May 31, {year}", due(date(year, 6, 15))),
            ("Q3", f"Jun 1 to Aug 31, {year}", due(date(year, 9, 15))),
            ("Q4", f"Sep 1 to Dec 31, {year}", due(date(year + 1, 1, 15)))]


def key_dates(year: int = YEAR) -> list[tuple[date, str]]:
    q = estimated_due(year)
    rows = [(due(date(year, 1, 15)), f"Q4 {year - 1} estimated tax due"),
            (due(date(year, 1, 31)), f"1099-NEC forms for {year - 1} due to you from clients (and to the IRS from them)"),
            (q[0][2], f"{year - 1} tax return or extension due; Q1 {year} estimated tax due; last day for {year - 1} IRA and HSA contributions"),
            (q[1][2], f"Q2 {year} estimated tax due"),
            (q[2][2], f"Q3 {year} estimated tax due"),
            (due(date(year, 10, 15)), f"Extended {year - 1} tax returns due"),
            (date(year, 12, 31), "Year ends: last day for most deductible spending to count this year"),
            (q[3][2], f"Q4 {year} estimated tax due")]
    return sorted(rows)


def fmt(d: date) -> str:
    return f"{d.strftime('%a')} {d.strftime('%b')} {d.day}, {d.year}"


# ---------------------------------------------------------------- printable

SCHEDULE_C = ["Advertising", "Car and truck", "Commissions and fees", "Contract labor", "Insurance (not health)",
              "Interest", "Legal and professional services", "Office expense", "Rent or lease", "Repairs and maintenance",
              "Supplies", "Taxes and licenses", "Travel", "Meals (business)", "Utilities", "Software and subscriptions",
              "Phone and internet (business share)", "Education and training", "Bank and payment fees", "Other"]


def _tbl(headers: list[tuple[str, str]], n: int, cls: str = "") -> str:
    head = "".join(f'<th style="width:{w}">{h}</th>' if w else f"<th>{h}</th>" for h, w in headers)
    body = "".join("<tr>" + "<td></td>" * len(headers) + "</tr>" for _ in range(n))
    return f'<table class="{cls}"><tr>{head}</tr>{body}</table>'


def _box(label: str, h: int = 30, extra: str = "") -> str:
    return f'<div class="box"><div class="lbl">{label}</div><div style="height:{h}px">{extra}</div></div>'


def start_page() -> str:
    return P(f"{YEAR} Freelancer <em>Tax-Year Planner</em>", "Start here", f'''
      <p class="big">One place for every dollar in and out of your freelance work in {YEAR}, so quarterly taxes and
      next April take an hour instead of a weekend.</p>
      <h3>How to use it</h3>
      <ol class="steps big">
        <li>Fill in the year page: your income goal and the share of each payment you'll set aside for taxes.</li>
        <li>Each time a client pays, write it in that month's income log and move your set-aside to a separate savings account.</li>
        <li>Log business expenses as they happen and keep the receipt (a phone photo is fine).</li>
        <li>Before each quarterly due date, total the quarter and record what you paid.</li>
        <li>In January, tick off the 1099s you receive and work through the tax-time checklist.</li>
      </ol>
      <h3>Choosing a set-aside percentage</h3>
      <p>Freelancers pay self-employment tax on top of income tax, and no one withholds it for you. Many set aside a
      fixed share of every payment. The right share depends on your income, state and deductions, so pick it with a tax
      professional or the IRS's Form 1040-ES worksheet, and adjust it each quarter.</p>
      <div style="margin-top:auto" class="box fineprint">An organising tool for US freelancers, not tax, legal or
      financial advice. Federal dates are worked out from the IRS weekend and holiday rule; the IRS can move them (for
      example after a disaster), and your state may have its own dates. Check irs.gov and your state tax agency. Made by
      1099 Money with the help of AI tools for drafting and layout.</div>''', kicker="1099 Money")


def dates_page() -> str:
    rows = "".join(f'<tr><td class="wrap"><b>{fmt(d)}</b></td><td class="wrap">{t}</td><td class="c"><span class="cb"></span></td></tr>'
                   for d, t in key_dates())
    q = "".join(f'<tr><td><b>{n}</b></td><td>{p}</td><td><b>{fmt(d)}</b></td><td></td><td></td></tr>'
                for n, p, d in estimated_due())
    return P(f"{YEAR} key <em>tax dates</em>", "Federal, check your state", f'''
      <table><tr><th style="width:26%">Date</th><th>What's due</th><th class="c" style="width:8%">Done</th></tr>{rows}</table>
      <h3>Estimated tax for {YEAR} income</h3>
      <table class="t28"><tr><th style="width:8%">Pay</th><th style="width:28%">Covers income earned</th><th style="width:24%">Due</th>
      <th>Federal paid</th><th>State paid</th></tr>{q}</table>
      <p class="fineprint" style="margin-top:6px">The quarters aren't equal: Q2 covers two months and Q4 four. Due dates
      that fall on a weekend or federal holiday move to the next business day, which is why Q4 is January 18, 2028.
      Pay through IRS Direct Pay, EFTPS or your IRS Online Account, and keep the confirmation number.</p>
      <div class="g2" style="margin-top:auto">{_box("My state's estimated-tax dates", 46)}{_box("Tax professional (name, phone, email)", 46)}</div>''')


def year_page() -> str:
    rows = "".join(f"<tr><td><b>{m}</b></td>" + "<td></td>" * 5 + "</tr>" for m in MONTHS)
    return P(f"{YEAR} at a <em>glance</em>", "Fill in at each month end", f'''
      <div class="g4">{_box("Income goal", 26)}{_box("Set-aside %", 26)}{_box("Tax savings account", 26)}{_box("Business account", 26)}</div>
      <table class="t26" style="margin-top:10px"><tr><th style="width:16%">Month</th><th>Income</th><th>Expenses</th>
      <th>Profit</th><th>Set aside</th><th>Running profit</th></tr>{rows}
      <tr class="tot"><td>Year</td><td></td><td></td><td></td><td></td><td></td></tr></table>
      <div class="g3" style="margin-top:auto">{_box("Best month and why", 40)}{_box("Biggest expense", 40)}{_box("Next year I'll", 40)}</div>''')


def setup_page() -> str:
    items = ["Open a separate checking account for business income and expenses",
             "Open a savings account just for tax money, and move the set-aside there every payday",
             "Decide your set-aside percentage with a tax professional or the Form 1040-ES worksheet",
             "Choose how you'll keep receipts (a folder, an app, or photos in one album)",
             "Send every client a W-9 when they ask; keep a copy of what you sent",
             "Find your state's estimated-tax rules and dates",
             "Look into retirement options for the self-employed (SEP IRA, Solo 401(k)) and their deadlines",
             "Check whether you need a local business licence",
             "Set calendar reminders for each estimated-tax due date",
             "Write your invoice terms (due date, late fee policy) and number invoices in order"]
    rows = "".join(f'<tr><td class="c"><span class="cb"></span></td><td>{x}</td><td></td></tr>' for x in items)
    return P("Business money <em>setup</em>", "Once, at the start of the year", f'''
      <table class="t30"><tr><th style="width:6%"></th><th>Step</th><th style="width:18%">Done on</th></tr>{rows}</table>
      <div class="lines" style="margin-top:10px;max-height:2.2in"></div><div class="note">Notes and account details (no passwords)</div>''')


def clients_page() -> str:
    return P("Clients and <em>1099s</em>", "Who paid you, and did the form arrive", f'''
      {_tbl([("Client", "24%"), ("Contact", "18%"), ("W-9 sent", "9%"), ("Paid in " + str(YEAR), "13%"),
             ("1099-NEC / 1099-K expected", "14%"), ("Received", "9%"), ("Amount on form", "")], 18, "t30")}
      <p class="fineprint" style="margin-top:6px">Clients send a 1099-NEC when what they paid you in the year passes the
      IRS reporting threshold (it rose from $600 to $2,000 for payments made from 2026; check irs.gov for the current
      figure). Payment apps and marketplaces may send a 1099-K instead. Report all your business income either way, with or without a form, and check each form against
      this list.</p>''')


def month_page(i: int) -> str:
    m = MONTHS[i]
    inc = _tbl([("Date paid", "13%"), ("Client", "27%"), ("Invoice #", "13%"), ("1099?", "8%"), ("Amount", "15%"),
                ("Set aside", "")], 9)
    exp = _tbl([("Date", "13%"), ("Paid to", "27%"), ("Category", "24%"), ("Amount", "15%"), ("Receipt", "")], 10)
    return P(f"{m} <em>{YEAR}</em>", f"Month {i + 1} of 12", f'''
      <h3 style="margin-top:0">Money in</h3>{inc}
      <h3>Money out (business expenses)</h3>{exp}
      <div class="g4" style="margin-top:auto">{_box("Income", 24)}{_box("Expenses", 24)}{_box("Profit", 24)}{_box("Moved to tax savings", 24)}</div>''',
             kicker="1099 Money")


def quarter_page(n: int) -> str:
    name, period, d = estimated_due()[n]
    months = MONTHS[[0, 3, 5, 8][n]:[3, 5, 8, 12][n]]
    rows = "".join(f"<tr><td><b>{m}</b></td><td></td><td></td><td></td><td></td></tr>" for m in months)
    return P(f"{name} estimated <em>tax</em>", f"Due {fmt(d)}", f'''
      <p>Covers income earned {period}. Fill it in a week before the due date.</p>
      <table class="t30"><tr><th style="width:18%">Month</th><th>Income</th><th>Expenses</th><th>Profit</th><th>Set aside</th></tr>
      {rows}<tr class="tot"><td>Quarter</td><td></td><td></td><td></td><td></td></tr></table>
      <h3>Payments</h3>
      <table class="t30"><tr><th style="width:18%"></th><th>Amount</th><th>Date paid</th><th>How (Direct Pay, EFTPS...)</th><th>Confirmation #</th></tr>
        <tr><td><b>Federal</b></td><td></td><td></td><td></td><td></td></tr>
        <tr><td><b>State</b></td><td></td><td></td><td></td><td></td></tr></table>
      <div class="g2" style="margin-top:12px">{_box("Tax savings balance after paying", 30)}{_box("Change my set-aside % to", 30)}</div>
      <div class="lines" style="margin-top:12px;max-height:2.2in"></div><div class="note">Notes for my tax professional</div>''',
             kicker="1099 Money")


def mileage_page(part: int) -> str:
    return P(f"Mileage <em>log</em>", f"Page {part} of 2", f'''
      {_tbl([("Date", "12%"), ("Business purpose", "34%"), ("From", "15%"), ("To", "15%"), ("Start / end odometer", "13%"), ("Miles", "")], 22, "t30")}
      <p class="fineprint" style="margin-top:6px">Write each trip on the day you make it: date, where, why, and miles.
      The {YEAR} IRS standard mileage rate is published around December; look it up on irs.gov. Commuting from home to a
      regular workplace usually doesn't count.</p>''')


def categories_page() -> str:
    half = (len(SCHEDULE_C) + 1) // 2
    col = lambda xs: "".join(f'<tr><td>{x}</td><td></td></tr>' for x in xs)  # noqa: E731
    return P("Expense <em>categories</em>", "Totals for tax time", f'''
      <p>These follow the expense lines on IRS Schedule C, plus a few freelancer favourites. Total each one at year end and
      hand the page to whoever prepares your return. Whether a cost is deductible, and how much, depends on your
      situation: ask your tax professional.</p>
      <div class="g2"><table class="t30"><tr><th>Category</th><th style="width:30%">{YEAR} total</th></tr>{col(SCHEDULE_C[:half])}</table>
      <table class="t30"><tr><th>Category</th><th style="width:30%">{YEAR} total</th></tr>{col(SCHEDULE_C[half:])}</table></div>
      <div class="g2" style="margin-top:auto">{_box("Home office: square feet used only for work / total square feet", 34)}
      {_box("Big purchases (equipment, computer): date, cost, what", 34)}</div>''')


def tax_time_page() -> str:
    items = [f"All 12 month pages totalled, and the year page filled in",
             "Every 1099-NEC and 1099-K received and checked against the clients page",
             "Estimated-tax payments listed with dates and confirmation numbers (federal and state)",
             "Expense category totals, plus receipts for the big ones",
             "Mileage log totalled",
             "Home office measurements, and rent or mortgage, utilities and insurance totals if you claim it",
             "Health insurance premiums you paid yourself",
             "Retirement contributions (SEP IRA, Solo 401(k), IRA) and their deadlines",
             "Last year's tax return, for reference",
             "Booked time with your tax professional, or the software ready",
             f"Set up the {YEAR + 1} planner and your Q1 {YEAR + 1} reminder"]
    rows = "".join(f'<tr><td class="c"><span class="cb"></span></td><td>{x}</td></tr>' for x in items)
    return P("Tax-time <em>checklist</em>", f"January to April {YEAR + 1}", f'''
      <table class="t30"><tr><th style="width:6%"></th><th>Gather</th></tr>{rows}</table>
      <div class="g2" style="margin-top:auto">{_box("Refund or amount owed", 30)}{_box("What I'll change next year", 30)}</div>''')


def planner_pages() -> list[str]:
    pages = [start_page(), dates_page(), year_page(), setup_page(), clients_page()]
    for q in range(4):
        pages += [month_page(i) for i in range([0, 3, 5, 8][q], [3, 5, 8, 12][q])] + [quarter_page(q)]
    pages += [mileage_page(1), mileage_page(2), categories_page(), tax_time_page()]
    return pages


# ---------------------------------------------------------------- listings

GOOD = ["This is a DIGITAL DOWNLOAD. Nothing is shipped. Your files are in your Etsy account right after payment.",
        "For US freelancers, creators and side hustlers who get 1099s. Federal dates; check your state's own.",
        "For personal use only. Please don't resell or share the files.",
        "An organising tool, not tax, legal or financial advice. It doesn't calculate your tax; confirm amounts with a tax professional and dates on irs.gov."]
DISCLOSURE = ("How it's made: designed by 1099 Money. AI tools helped draft the text and lay out the pages; the dates are "
              "worked out in code from the IRS weekend and holiday rule and were checked before listing.")
CAT = "Paper & Party Supplies > Paper > Calendars & Planners"


def _gumroad(hook: str, get: list[str], price: float, files: str) -> str:
    g = "\n".join(f"- {x}" for x in get)
    return (f"{hook}\n\nWhat's inside:\n{g}\n\nInstant download: {files}. ${price:g}, one payment, files you keep.\n\n"
            "For US freelancers. An organising tool, not tax, legal or financial advice; it doesn't calculate your tax. "
            "Federal dates follow the IRS weekend and holiday rule; check irs.gov and your state. Made with the help of AI "
            "tools for drafting and layout. A problem with a file? Reply to your receipt email.")


PRINT_GET = ["25 pages, dated for 2027: key tax dates, a year at a glance and a business money setup checklist",
             "A clients and 1099 tracker",
             "12 month pages, each with an income log, an expense log and a set-aside total",
             "4 quarterly estimated-tax pages with the 2027 due dates (Q4 is Jan 18, 2028)",
             "2 mileage logs, Schedule C expense categories and a tax-time checklist"]
SHEET_GET = ["An income log, expense log and mileage log that total themselves by month, quarter and category",
             "Quarterly estimated-tax tab with the 2027 due dates and your set-aside percentage applied to profit",
             "A clients and 1099 tab, and a year summary with a chart",
             "Works in Google Sheets (free), Excel and Apple Numbers; comes with made-up example rows to delete"]

LISTINGS = [
    dict(slug="freelancer-tax-planner-2027", name="2027 Freelancer Tax-Year Planner (printable)", price=12.00, kind="print",
         title="2027 Freelancer Tax Planner Printable, 1099 Income Expense and Quarterly Tax Tracker",
         tags=["freelancer planner", "1099 tax planner", "self employed", "quarterly taxes", "2027 planner",
               "income tracker", "expense tracker", "tax organizer", "small business", "mileage log",
               "side hustle", "estimated taxes", "bookkeeping"],
         attributes={"Paper size": "US Letter, A4", "File type": "PDF", "Dated or undated": "Dated (2027)",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="Every freelance dollar in and out of 2027 in one printable, with the quarterly estimated-tax dates already worked out."),
    dict(slug="freelancer-tax-sheet-2027", name="2027 Freelancer Tax Tracker (Google Sheets)", price=14.00, kind="sheet",
         title="2027 Freelancer Tax Tracker Spreadsheet, Google Sheets 1099 Income and Expense Tracker",
         tags=["freelancer tracker", "1099 spreadsheet", "google sheets", "self employed", "quarterly taxes",
               "income tracker", "expense tracker", "small business", "bookkeeping", "mileage tracker",
               "side hustle", "estimated taxes", "excel template"],
         attributes={"File type": "XLSX, PDF", "Software": "Google Sheets, Microsoft Excel, Apple Numbers",
                     "Dated or undated": "Dated (2027)", "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="A 2027 income, expense and mileage tracker that adds itself up by month, quarter and category, ready for each estimated-tax date."),
    dict(slug="freelancer-tax-bundle-2027", name="2027 Freelancer Tax Bundle (printable + Sheets)", price=19.00, kind="bundle",
         title="2027 Freelancer Tax Bundle, Printable Planner and Google Sheets 1099 Tracker",
         tags=["freelancer planner", "1099 tax planner", "google sheets", "self employed", "quarterly taxes",
               "2027 planner", "income tracker", "expense tracker", "small business", "side hustle",
               "estimated taxes", "bookkeeping", "tax organizer"],
         attributes={"File type": "PDF, XLSX", "Dated or undated": "Dated (2027)", "Primary colour": "Blue",
                     "Secondary colour": "Orange"},
         hook="The printable planner and the spreadsheet together: paper for the desk, a sheet that does the sums ($26 separately)."),
]

_GET = {"print": PRINT_GET, "sheet": SHEET_GET, "bundle": PRINT_GET[:1] + SHEET_GET[:2]}
_HOW = {"print": ["Print the pages (Letter or A4), or write on them in a PDF app.", "Log each payment and expense as it happens.",
                  "Total the quarter before each due date and record what you paid."],
        "sheet": ["Open the .xlsx in Google Sheets (upload to Drive and open), Excel or Numbers.",
                  "Delete the example rows and set your set-aside % on the Setup tab.", "Add income and expenses; the totals fill in."],
        "bundle": ["Unzip the download.", "Use the sheet for the sums and the printable for the desk.", "Check off each quarter as you pay."]}
_FILES = {"print": "PDFs in US Letter and A4", "sheet": "an .xlsx workbook and a one-page Start Here PDF",
          "bundle": "the printable PDFs and the .xlsx workbook"}
for _it in LISTINGS:
    _it["category"] = CAT if _it["kind"] != "sheet" else "Paper & Party Supplies > Paper > Calendars & Planners (digital)"
    _it["description"] = __import__("shop").etsy_description(_it["hook"], _GET[_it["kind"]], _HOW[_it["kind"]], GOOD, DISCLOSURE)
    _it["gumroad"] = _gumroad(_it["hook"], _GET[_it["kind"]], _it["price"], _FILES[_it["kind"]])
