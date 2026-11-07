"""1099 Money: the 2026 Tax Season Organizer, a printable for the return filed in early 2027.

Trackers and checklists only, with labels and no how-to text, so it isn't a "functional guide" under Etsy's
22 Oct 2026 AI rule (launch/catalog/etsy_rules.py). It goes with 1099 Money's January push: the forms arrive by
Feb 1 2027 and the return is due Apr 15 2027. Dates come from ten99.due() (the IRS weekend and holiday rule).
It never says what is deductible or computes any tax.
"""
from __future__ import annotations

from datetime import date

import shop
import ten99 as T

P = T.BRAND.page
TAX_YEAR = 2026
FILE_YEAR = TAX_YEAR + 1
SLUG = "tax-season-organizer-2026"
KICK = "1099 Money"
FINE = (f"An organizer, not tax, legal or financial advice. Dates follow the IRS weekend and holiday rule; the IRS can "
        f"move them, and your state has its own. Check irs.gov and your state tax agency.")


def key_dates() -> list[tuple[date, str]]:
    q = T.estimated_due(TAX_YEAR)
    return [(q[3][2], f"Q4 {TAX_YEAR} estimated tax"),
            (T.due(date(FILE_YEAR, 1, 31)), "W-2s and most 1099s (NEC, INT, DIV, R) sent out"),
            (T.due(date(FILE_YEAR, 2, 15)), "1099-B and brokerage statements sent out"),
            (T.due(date(FILE_YEAR, 4, 15)), f"{TAX_YEAR} return or extension; last day for {TAX_YEAR} IRA and HSA contributions"),
            (T.due(date(FILE_YEAR, 10, 15)), f"Extended {TAX_YEAR} returns")]


def _rows(labels: list[str], blanks: int, extra: int = 0) -> str:
    return "".join(f"<tr><td>{x}</td>" + "<td></td>" * blanks + "</tr>" for x in labels + [""] * extra)


def _box(label: str, h: int = 26) -> str:
    return T._box(label, h)


def glance_page() -> str:
    rows = "".join(f'<tr><td class="wrap"><b>{T.fmt(d)}</b></td><td class="wrap">{t}</td><td class="c"><span class="cb"></span></td></tr>'
                   for d, t in key_dates())
    return P(f"Tax Season <em>Organizer</em>", f"The {TAX_YEAR} return, filed in {FILE_YEAR}", f'''
      <div class="g3">{_box("Filing status")}{_box("Names on the return")}{_box("Dependents")}</div>
      <div class="g3" style="margin-top:8px">{_box("Preparer or software")}{_box("Appointment")}{_box("Last year's refund or amount owed")}</div>
      <h3>Key dates</h3>
      <table><tr><th style="width:26%">Date</th><th>What</th><th class="c" style="width:8%">Done</th></tr>{rows}</table>
      <h3>My progress</h3>
      <table class="t26"><tr><th style="width:6%"></th><th>Step</th><th style="width:22%">Date</th></tr>
      {"".join(f'<tr><td class="c"><span class="cb"></span></td><td>{s}</td><td></td></tr>' for s in
               ["All forms in (page 2)", "Business totals done (page 4)", "Records gathered (page 5)",
                "Questions written (page 8)", "Return filed (page 9)", "Refund received or balance paid"])}</table>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>
      <div class="box fineprint" style="margin-top:8px">{FINE} Made by 1099 Money with the help of AI tools for
      drafting the labels and layout.</div>''', kicker=KICK)


FORMS = ["W-2", "1099-NEC", "1099-K", "1099-MISC", "1099-INT", "1099-DIV", "1099-B", "1099-R", "SSA-1099", "1099-G",
         "1098 (mortgage interest)", "1098-E (student loan interest)", "1098-T (tuition)", "1095-A (marketplace)",
         "5498 / 5498-SA"]


def forms_page() -> str:
    return P("Tax forms <em>received</em>", f"For {TAX_YEAR}", f'''
      <table class="t30"><tr><th style="width:24%">Form</th><th style="width:26%">From</th><th style="width:12%">Expected</th>
      <th class="c" style="width:8%">Got it</th><th style="width:14%">Amount</th><th>Stored</th></tr>{_rows(FORMS, 5, 5)}</table>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>''',
             kicker=KICK)


def income_page() -> str:
    return P("Clients and <em>1099s</em>", "My records next to the forms", f'''
      <table class="t28"><tr><th style="width:26%">Client or platform</th><th>My records</th><th>Form amount</th>
      <th>Difference</th><th style="width:24%">Note</th></tr>{_rows([], 4, 18)}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td><td></td></tr></table>
      <h3>Other income</h3>
      <table class="t28"><tr><th style="width:40%">Source</th><th>Amount</th><th>Form</th></tr>
      {_rows(["Job (W-2)", "Interest and dividends", "Sales of investments", "Rental", "Other"], 2)}</table>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>''', kicker=KICK)


def business_page() -> str:
    cats = ["Gross receipts", "Returns and refunds given"] + T.SCHEDULE_C
    half = (len(cats) + 1) // 2
    col = lambda xs: "".join(f"<tr><td>{x}</td><td></td><td class='c'><span class='cb'></span></td></tr>" for x in xs)  # noqa: E731
    head = f"<tr><th>Line</th><th style='width:28%'>{TAX_YEAR} total</th><th class='c' style='width:16%'>Receipts</th></tr>"
    return P("Business <em>totals</em>", "Schedule C lines", f'''
      <div class="g2"><table class="t28">{head}{col(cats[:half])}</table><table class="t28">{head}{col(cats[half:])}</table></div>
      <div class="g4" style="margin-top:10px">{_box("Business miles")}{_box("Home office sq ft / total sq ft")}
      {_box("Equipment bought (date, cost)")}{_box("Net profit")}</div>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>''', kicker=KICK)


RECORDS = ["Charitable gifts (cash)", "Charitable gifts (items)", "Medical and dental", "Childcare and dependent care",
           "Tuition and education", "Student loan interest", "Mortgage interest", "Property tax", "State and local tax paid",
           "IRA contributions", "HSA contributions", "SEP IRA / Solo 401(k)", "Health insurance premiums paid myself"]


def records_page() -> str:
    return P("Deductions and credits <em>records</em>", "Amounts and proof", f'''
      <table class="t28"><tr><th style="width:34%">Item</th><th style="width:16%">Amount</th><th style="width:22%">Proof</th>
      <th>Stored</th></tr>{_rows(RECORDS, 3, 4)}</table>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>
      <p class="fineprint" style="margin-top:6px">Which of these count depends on your situation. Ask your preparer.</p>''',
             kicker=KICK)


def payments_page() -> str:
    q = "".join(f"<tr><td><b>{n}</b></td><td>{T.fmt(d)}</td><td></td><td></td><td></td><td></td><td></td></tr>"
                for n, _p, d in T.estimated_due(TAX_YEAR))
    return P("Estimated tax <em>paid</em>", f"For {TAX_YEAR} income", f'''
      <table class="t30"><tr><th style="width:7%"></th><th style="width:19%">Due</th><th>Federal</th><th>Date paid</th>
      <th>Confirmation #</th><th>State</th><th>Date paid</th></tr>{q}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>
      <div class="g3" style="margin-top:10px">{_box("Last year's refund applied")}{_box("Withheld (W-2s, 1099-R)")}{_box("Extension payment")}</div>
      <h3>{FILE_YEAR} set-aside</h3>
      <div class="g3">{_box("Set-aside %")}{_box("Q1 " + str(FILE_YEAR) + " due " + T.fmt(T.estimated_due(FILE_YEAR)[0][2]))}{_box("Tax savings account")}</div>
      <div class="lines" style="margin-top:12px"></div><div class="note">Notes</div>''', kicker=KICK)


def household_page() -> str:
    return P("Household and <em>dependents</em>", "No full SSNs here", f'''
      <table class="t30"><tr><th style="width:24%">Name</th><th>Relationship</th><th>Date of birth</th>
      <th>Months lived with me</th><th class="c" style="width:12%">SSN / ITIN card on file</th></tr>{_rows([], 4, 6)}</table>
      <h3>Childcare providers</h3>
      <table class="t30"><tr><th style="width:30%">Provider</th><th>Address</th><th>Tax ID on file</th><th>Paid in {TAX_YEAR}</th></tr>{_rows([], 3, 4)}</table>
      <h3>Changes in {TAX_YEAR}</h3>
      <table class="t26"><tr><th style="width:6%"></th><th>Change</th><th>Date</th></tr>
      {"".join(f'<tr><td class="c"><span class="cb"></span></td><td>{x}</td><td></td></tr>' for x in
               ["Married or divorced", "New baby or dependent", "Moved (state too?)", "New job or business", "Bought or sold a home"])}</table>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>''',
             kicker=KICK)


BRING = ["Photo ID", f"Last year's ({TAX_YEAR - 1}) return", "Every form from page 2", "Business totals (page 4)",
         "Records and receipts (page 5)", "Estimated payments (page 6)", "Bank account for the refund", "IRS letters, if any"]


def preparer_page() -> str:
    rows = "".join(f'<tr><td class="c"><span class="cb"></span></td><td>{x}</td></tr>' for x in BRING)
    return P("For my <em>preparer</em>", "Bring and ask", f'''
      <div class="g2"><table class="t26"><tr><th style="width:12%"></th><th>Bring</th></tr>{rows}</table>
      <div>{_box("Preparer (name, phone, email)", 40)}<div style="height:8px"></div>{_box("Appointment and fee", 40)}</div></div>
      <h3>Questions</h3><div class="lines"></div>''', kicker=KICK)


def filing_page() -> str:
    head = "<tr><th style='width:14%'></th><th>Filed on</th><th>How</th><th>Confirmation</th><th>Accepted</th><th>Refund / owed</th><th>Received / paid</th></tr>"
    return P("Filing <em>tracker</em>", f"{TAX_YEAR} return", f'''
      <table class="t34">{head}<tr><td><b>Federal</b></td>{"<td></td>" * 6}</tr><tr><td><b>State</b></td>{"<td></td>" * 6}</tr>
      <tr><td><b>Extension</b></td>{"<td></td>" * 6}</tr></table>
      <h3>Records kept</h3>
      <table class="t28"><tr><th style="width:34%">Document</th><th>Where stored</th><th style="width:20%">Keep until</th></tr>
      {_rows([f"{TAX_YEAR} federal return", f"{TAX_YEAR} state return", "Forms (W-2, 1099s, 1098s)", "Receipts",
              "Mileage log", "Estimated payment confirmations"], 2, 3)}</table>
      <div class="lines" style="margin-top:10px"></div><div class="note">Notes</div>
      <div class="g2" style="margin-top:10px">{_box("Next year I'll", 40)}{_box("Reminder set for Q1 " + str(FILE_YEAR), 40)}</div>''',
             kicker=KICK)


def pages() -> list[str]:
    return [glance_page(), forms_page(), income_page(), business_page(), records_page(), payments_page(),
            household_page(), preparer_page(), filing_page()]


GET = [f"9 pages for the {TAX_YEAR} return: key dates and a checklist of tax forms (W-2, 1099s, 1098s and more)",
       "A clients page to match your records against each 1099",
       "Business totals by Schedule C line, and records for deductions and credits",
       f"Estimated payments for {TAX_YEAR}, household and dependents, questions for your preparer and a filing tracker"]
HOW = ["Print the pages (Letter or A4), or write on them in a PDF app.", "Tick off each form as it arrives.",
       "Bring the pages to your preparer, or open them beside your tax software."]
DISCLOSURE = ("How it's made: designed by 1099 Money. Trackers and checklists only, with labels and no how-to text. "
              "AI tools helped draft the labels and lay out the pages, and a person checked them; the dates are worked out "
              "in code from the IRS weekend and holiday rule.")

LISTING = dict(
    slug=SLUG, name=f"{TAX_YEAR} Tax Season Organizer (printable)", price=8.00, kind="print",
    title=f"{TAX_YEAR} Tax Season Organizer Printable, 1099 and W-2 Form Checklist, Deductions Estimated Payments Tracker",
    tags=["tax organizer", "tax season planner", "tax checklist", "1099 tracker", "tax prep printable", "tax document list",
          "self employed tax", "freelancer taxes", "deduction tracker", "tax return prep", "estimated taxes",
          "small business tax", "2026 tax year"],
    attributes={"Paper size": "US Letter, A4", "File type": "PDF", "Dated or undated": f"Dated ({TAX_YEAR} tax year)",
                "Primary colour": "Blue", "Secondary colour": "Orange"},
    hook=(f"Every form, total and payment for your {TAX_YEAR} return on nine printable pages, ready for your preparer "
          "or your tax software."),
    status="active", category=T.CAT)
LISTING["description"] = shop.etsy_description(shop.opener(LISTING) + " " + LISTING["hook"], GET, HOW, T.GOOD, DISCLOSURE)
LISTING["gumroad"] = T._gumroad(LISTING["hook"], GET, LISTING["price"], "PDFs in US Letter and A4")
if all(it["slug"] != SLUG for it in T.LISTINGS):
    T.LISTINGS.append(LISTING)
