"""Etsy listing copy for every item: title (<=140 chars), 13 tags (<=20 chars each), price, description.

Etsy rules this follows: no links or prompts to buy off Etsy, digital items say nothing is shipped, and
AI use in the making is disclosed (Etsy's creativity standards ask sellers to say how items are made).
"""
from __future__ import annotations

import re

SHOP = "Money Made Simple"
PRINT_CAT = "Paper & Party Supplies > Paper > Calendars & Planners"
GUIDE_CAT = "Paper & Party Supplies > Paper > Calendars & Planners (or Books > Guides, whichever Etsy suggests)"

GOOD_TO_KNOW_PRINTABLE = """GOOD TO KNOW
- This is a DIGITAL DOWNLOAD. Nothing is shipped. Files are available in your Etsy account right after payment (Purchases and reviews).
- Two PDFs: US Letter (8.5 x 11 in) and A4. Print at home or at a print shop, as many times as you like for personal use.
- Undated, so you can start any month of any year.
- Ink-friendly: mostly white with thin lines. Colours on screen may look slightly different when printed.
- Works with a tablet too: open the PDF in any note app that lets you write on PDFs.
- For personal use only. Please don't resell, share or redistribute the files.
- This is an organising tool, not financial advice.
- How it's made: designed by Money Made Simple. AI tools helped with drafting and layout; every page was checked by a human."""

GOOD_TO_KNOW_PRODUCT = """GOOD TO KNOW
- This is a DIGITAL DOWNLOAD. Nothing is shipped. Files are available in your Etsy account right after payment (Purchases and reviews).
- The guide is a PDF (US Letter, prints fine on A4). The spreadsheet is an .xlsx file that opens in Microsoft Excel, Google Sheets (free: upload it to Google Drive and open it) and Apple Numbers.
- The spreadsheet comes filled in with a made-up example so you can see how it works. Yellow cells are your inputs.
- For personal use only. Please don't resell, share or redistribute the files.
- Educational content, not financial, tax, legal or investment advice. US-focused where laws or accounts are mentioned.
- How it's made: written and fact-checked by a human at Money Made Simple. AI tools helped with drafting and layout."""

MORE = """MORE FROM THE SHOP
Search "{shop}" on Etsy for the matching budget planner, savings trackers and money guides, or get everything in one of the bundles."""


def _good_to_know_dated(year: int, n_pdfs: int) -> str:
    """The printable notes for a dated planner: says how many PDFs ship and that it's dated (not "undated")."""
    return (GOOD_TO_KNOW_PRINTABLE
            .replace("- Two PDFs: US Letter (8.5 x 11 in) and A4.",
                     f"- {n_pdfs} PDFs: Sunday-start and Monday-start, each in US Letter (8.5 x 11 in) and A4.")
            .replace("- Undated, so you can start any month of any year.",
                     f"- Dated for {year}: every calendar page has the real {year} dates, with US holidays marked."))


def opener(it: dict) -> str:
    """First sentence: name the item and its format, as Etsy advises ("keywords in the first few sentences")."""
    n = it["name"].split(" (")[0].removeprefix("The ")
    if it.get("dated"):
        return f"This {n} is a dated {it['year']} printable PDF planner in US Letter and A4."
    if it.get("product") and it.get("bundle"):
        return f"This {n} is a digital download of {len(it['bundle'])} PDF guides, each with a spreadsheet for Excel and Google Sheets."
    if it.get("product"):
        return f"This {n} is a digital download: a PDF guide plus a spreadsheet for Excel and Google Sheets."
    if it["kind"] == "bundle":
        return f"This {n} is a bundle of {len(it['bundle'])} undated printable PDFs in US Letter and A4."
    return f"This {n} is an undated printable PDF in US Letter and A4."


def _desc(hook: str, get: list[str], how: list[str], product: bool = False, good: str | None = None) -> str:
    g = "\n".join(f"- {x}" for x in get)
    h = "\n".join(f"{i}. {x}" for i, x in enumerate(how, start=1))
    good = good or (GOOD_TO_KNOW_PRODUCT if product else GOOD_TO_KNOW_PRINTABLE)
    return f"{hook}\n\nWHAT YOU GET\n{g}\n\nHOW IT WORKS\n{h}\n\n{good}\n\n{MORE.format(shop=SHOP)}"


LISTINGS: list[dict] = [
    # ------------------------------------------------------------------ printables ($3-$6)
    dict(slug="monthly-budget-planner", kind="printable", name="Monthly Budget Planner", price=6.00,
         file_stem="Monthly-Budget-Planner",
         title="Monthly Budget Planner Printable, Undated Budget Binder, 12 Month Budget Sheets, Bill Tracker, Savings, Letter + A4 PDF",
         tags=["budget planner", "monthly budget", "budget printable", "budget binder", "undated planner",
               "finance planner", "budget template", "money planner", "bill tracker", "savings tracker",
               "budget sheet", "household budget", "printable planner"],
         hook="A simple monthly budget you'll actually keep. One page per month: income, bills, savings, what's left to spend, and a 5-minute weekly check-in.",
         get=["15 pages: how-to page, year at a glance, 12 monthly budget pages (January to December, undated), notes page",
              "Each month: income, bill list with due dates and paid boxes, savings goals, 'left to spend', weekly spending check-in, month-end notes",
              "US Letter and A4 PDFs"],
         how=["Print the year page and this month's page.", "List income, bills and savings. What's left is your spending money; divide by the weeks in the month.",
              "Check in once a week and tick paid bills.", "At month end, write one thing to change next month."],
         hero=[3, 2, 4], grid=[1, 2, 3, 4, 5, 6, 15, 16]),
    dict(slug="paycheck-budget-planner", kind="printable", name="Paycheck Budget Planner", price=4.00,
         file_stem="Paycheck-Budget-Planner",
         title="Paycheck Budget Planner Printable, Biweekly Budget Template, Paycheck to Paycheck Tracker, Bill Planner, Letter + A4 PDF",
         tags=["paycheck budget", "biweekly budget", "budget by paycheck", "paycheck planner", "budget printable",
               "bill planner", "budget template", "money tracker", "budget worksheet", "finance printable",
               "paycheck tracker", "budget planner", "zero based budget"],
         hook="Paid every two weeks? Budget each paycheck instead of each month. Every check gets a job: bills due before the next payday, savings, then spending money.",
         get=["4 pages: how-to page, two 'paycheck plan' pages (2 paychecks per page), 26-paycheck year tracker",
              "Bills from this check, savings and goals, and a 'spending money' box for each paycheck",
              "US Letter and A4 PDFs"],
         how=["Write the pay date and the amount you received.", "List the bills due before your next payday.",
              "Pay savings and goals next.", "What's left is spending money until next payday."],
         hero=[2, 4, 1], grid=[1, 2, 3, 4]),
    dict(slug="savings-challenge-tracker", kind="printable", name="Savings Challenge Tracker", price=3.00,
         file_stem="Savings-Challenge-Tracker",
         title="Savings Challenge Printable, $1000 Savings Tracker, $500 $2500 $5000 Money Challenge, Color In Savings Goal, Letter + A4",
         tags=["savings challenge", "savings tracker", "1000 savings", "money challenge", "saving printable",
               "savings goal", "color in tracker", "5000 savings", "emergency fund", "money saving",
               "savings chart", "budget printable", "save money tracker"],
         hook="Colour a circle every time you save. Four challenges, $500, $1,000, $2,500 and $5,000, and every set of circles adds up to exactly the goal.",
         get=["5 pages: how-to page plus one tracker for each goal: $500 (50 circles), $1,000, $2,500 and $5,000 (100 circles each)",
              "Mixed amounts so you can save big on payday and small on tight weeks",
              "Start, halfway and done boxes. US Letter and A4 PDFs"],
         how=["Pick a goal and write what you're saving for.", "Each time you save, colour a circle with that amount.",
              "Do them in any order.", "All circles coloured = goal reached."],
         hero=[3, 2, 4], grid=[1, 2, 3, 4, 5]),
    dict(slug="52-week-savings-challenge", kind="printable", name="52-Week Savings Challenge", price=3.00,
         file_stem="52-Week-Savings-Challenge",
         title="52 Week Savings Challenge Printable, $1378 Money Challenge Tracker, Reverse and Custom Weekly Savings Chart, Letter + A4",
         tags=["52 week challenge", "savings challenge", "weekly savings", "money challenge", "savings tracker",
               "1378 challenge", "savings printable", "new year savings", "savings chart", "save money",
               "budget printable", "money saving", "savings goal"],
         hook="Save $1 in week one and $52 in week 52, and finish with $1,378. Or flip it, or set your own weekly amount.",
         get=["4 pages: how-to page, classic ($1 to $52), reverse ($52 to $1) and a blank 'my way' version for any amount",
              "Running total and a checkbox for every week", "US Letter and A4 PDFs"],
         how=["Choose a version.", "Save that week's amount and write the running total.", "Tick the box.",
              "Start any week of the year."],
         hero=[2, 3, 4], grid=[1, 2, 3, 4]),
    dict(slug="bill-payment-tracker", kind="printable", name="Bill Payment Tracker", price=4.00,
         file_stem="Bill-Payment-Tracker",
         title="Bill Tracker Printable, Monthly Bill Payment Checklist, Bill Calendar, Yearly Bills Organizer, Due Date Tracker, Letter + A4",
         tags=["bill tracker", "bill payment", "bill organizer", "bill calendar", "bill checklist",
               "monthly bills", "due date tracker", "bill printable", "budget binder", "finance printable",
               "household bills", "bill planner", "budget printable"],
         hook="Never miss a due date again. One list of every bill, a 12-month checklist to tick as you pay, a bill calendar and a page for the once-a-year bills that usually sneak up on you.",
         get=["5 pages: how-to page, bill list, 12-month payment checklist, undated monthly bill calendar, yearly bills planner",
              "The yearly bills page shows how much to set aside each month", "US Letter and A4 PDFs"],
         how=["List every bill once.", "Copy them to the 12-month checklist and tick as you pay.",
              "Write bills on the calendar each month.", "Set aside 1/12 of each yearly bill monthly."],
         hero=[3, 4, 2], grid=[1, 2, 3, 4, 5]),
    dict(slug="sinking-funds-tracker", kind="printable", name="Sinking Funds Tracker", price=4.00,
         file_stem="Sinking-Funds-Tracker",
         title="Sinking Funds Tracker Printable, Savings Thermometer, Sinking Fund Log, Savings Goals Budget Binder Insert, Letter + A4 PDF",
         tags=["sinking funds", "sinking fund tracker", "savings tracker", "savings goals", "budget binder",
               "savings thermometer", "sinking fund", "budget printable", "money tracker", "savings printable",
               "finance planner", "savings log", "cash envelope"],
         hook="Stop being surprised by costs you knew were coming. Set money aside every month for car repairs, gifts, travel and more, and watch each fund fill up.",
         get=["6 pages: how-to page, overview (goal, date, monthly amount for up to 14 funds), 8 fund trackers (2 per page) each with a thermometer and a log",
              "Starter ideas list for common sinking funds", "US Letter and A4 PDFs"],
         how=["List each fund, its goal and the date you need it.", "Goal divided by months left = monthly amount.",
              "Log each deposit and colour the thermometer.", "Spend from it when the bill comes. That's what it's for."],
         hero=[3, 2, 4], grid=[1, 2, 3, 4, 5, 6]),
    dict(slug="debt-payoff-coloring-tracker", kind="printable", name="Debt Payoff Coloring Tracker", price=4.00,
         file_stem="Debt-Payoff-Coloring-Trackers",
         title="Debt Payoff Tracker Printable, Debt Coloring Page, Debt Snowball Avalanche Thermometer, 100 Squares Debt Free Chart, Letter A4",
         tags=["debt payoff tracker", "debt tracker", "debt snowball", "debt free", "debt coloring page",
               "debt thermometer", "debt avalanche", "pay off debt", "debt printable", "credit card debt",
               "debt free chart", "budget printable", "debt payoff"],
         hook="Make paying off debt visible. Colour in a square, a step or a line every time your balance drops, and stick it on the fridge.",
         get=["5 pages: how-to page, debt list, 100-squares tracker, debt thermometer with payment log, 50-step debt-free staircase with milestone rewards",
              "Works for one debt or your total debt", "US Letter and A4 PDFs"],
         how=["List your debts.", "Pick a tracker and divide the balance by the spaces: that's each space's value.",
              "Colour a space each time the balance drops by that much.", "Celebrate the milestones (cheaply)."],
         hero=[3, 4, 5], grid=[1, 2, 3, 4, 5]),
    dict(slug="monthly-expense-tracker", kind="printable", name="Monthly Expense Tracker", price=3.00,
         file_stem="Monthly-Expense-Tracker",
         title="Expense Tracker Printable, Monthly Spending Log, Daily Expense Tracker, Spending Tracker Budget Binder Insert, Letter + A4 PDF",
         tags=["expense tracker", "spending tracker", "expense log", "spending log", "budget printable",
               "monthly expenses", "money tracker", "budget binder", "finance tracker", "daily expenses",
               "budget worksheet", "spending journal", "budget planner"],
         hook="See where your money actually goes. Log spending as you go (or once a day from your banking app), then total it by category at month end.",
         get=["4 pages: how-to page, two expense log pages (60 lines), monthly category summary with planned vs actual",
              "'Biggest surprise' and 'next month I'll' boxes", "US Letter and A4 PDFs"],
         how=["Log each purchase: date, what, category, amount.", "Use a handful of simple categories.",
              "Total each category at month end.", "Pick one category to work on next month."],
         hero=[2, 4, 3], grid=[1, 2, 3, 4]),
    dict(slug="no-spend-challenge", kind="printable", name="No-Spend Challenge", price=3.00,
         file_stem="No-Spend-Challenge",
         title="No Spend Challenge Printable, 30 Day No Spend Tracker, Money Challenge Calendar, Frugal Living Savings Printable, Letter + A4",
         tags=["no spend challenge", "no spend tracker", "30 day challenge", "money challenge", "frugal living",
               "savings challenge", "spending tracker", "budget printable", "no buy challenge", "save money",
               "money saving", "spending freeze", "budget challenge"],
         hook="Thirty days of noticing your spending. Set your own rules, colour a circle for every no-spend day, and send what you didn't spend to savings.",
         get=["4 pages: how-to page, 30-day tracker, 'my rules' page (allowed vs not allowed, free things to do), reflection page",
              "Essentials are always allowed: it's a challenge, not a punishment", "US Letter and A4 PDFs"],
         how=["Write your rules.", "Colour a circle for every no-spend day.", "Slipped? Write it down and keep going.",
              "Move what you didn't spend to savings or debt."],
         hero=[2, 3, 4], grid=[1, 2, 3, 4]),
    dict(slug="subscription-tracker", kind="printable", name="Subscription Tracker", price=3.00,
         file_stem="Subscription-Tracker",
         title="Subscription Tracker Printable, Monthly Subscription Log, Recurring Payments Tracker, Cancel Subscriptions Checklist, Letter A4",
         tags=["subscription tracker", "subscriptions", "recurring payments", "bill tracker", "budget printable",
               "money saving", "cancel subscription", "budget binder", "expense tracker", "finance tracker",
               "frugal living", "save money", "budget planner"],
         hook="Find every subscription you're paying for, see what each one costs per year, and decide which to keep. Then log each cancellation so it stays cancelled.",
         get=["3 pages: how-to page (with where to look for hidden subscriptions), subscription tracker with keep/cancel/downgrade/negotiate column, cancellation log",
              "Yearly cost before and saved per year boxes", "US Letter and A4 PDFs"],
         how=["Check statements, app stores, PayPal and email receipts.", "List each charge and its yearly cost.",
              "Decide keep, cancel, downgrade or negotiate.", "Log cancellations and check next month's statement."],
         hero=[2, 3, 1], grid=[1, 2, 3]),
    # ------------------------------------------------------------------ guides + spreadsheets
    dict(slug="bill-cut-kit", kind="product", name="The Bill Cut Kit", price=5.00, file_stem="The-Bill-Cut-Kit",
         title="Bill Cut Kit, Subscription Audit Checklist, Bill Negotiation Scripts, Savings Tracker Spreadsheet, Excel Google Sheets",
         tags=["save money", "bill negotiation", "subscription audit", "cancel subscription", "budget spreadsheet",
               "google sheets", "excel template", "money saving", "frugal living", "budget template",
               "bill tracker", "personal finance", "savings tracker"],
         hook="Find every recurring charge in about 10 minutes, cut the ones you don't use, and lower the bills you keep with word-for-word call scripts.",
         get=["9-page PDF guide: where subscriptions hide, keep/cut/downgrade/negotiate, cancelling cleanly, 7 call scripts (internet, phone, insurance, card APR, fees, gym), printable worksheet",
              "Spreadsheet (.xlsx): audit with yearly costs, negotiation log with promo-end reminders, savings summary"],
         how=["Check the five places charges hide.", "Make one decision per charge.",
              "Use the scripts on the bills you keep.", "Send what you save to savings or debt."], product=True,
         hero=[1, 7, 5], grid=[2, 3, 4, 5, 6, 7, 8, 9]),
    dict(slug="20-minute-budget", kind="product", name="The 20-Minute Budget", price=12.00, file_stem="The-20-Minute-Budget",
         title="Budget Spreadsheet and Guide, 20 Minute Weekly Budget, Excel Google Sheets Budget Template, Sinking Funds, Debt Payoff Planner",
         tags=["budget spreadsheet", "google sheets", "excel budget", "weekly budget", "budget template",
               "sinking funds", "debt payoff", "budget planner", "zero based budget", "debt snowball",
               "personal finance", "money management", "budget for beginner"],
         hook="A budget you set up once in an evening and run in 20 minutes a week. Bills, savings and goals run on autopilot; everything else is one weekly spending number.",
         get=["14-page PDF guide with a fully worked example, setup steps, the weekly routine, avalanche vs snowball, FAQ and a printable worksheet",
              "Spreadsheet (.xlsx): Setup, Monthly Plan, Weekly Check-in, Sinking Funds, Debt Payoff (avalanche vs snowball, up to 6 debts)"],
         how=["Read the setup chapters (about 15 minutes).", "Fill in the yellow cells.",
              "Automate bills, savings and goals.", "Check your weekly number once a week."], product=True,
         hero=[1, 6, 3], grid=[2, 3, 4, 5, 6, 8, 10, 14]),
    dict(slug="credit-report-audit-kit", kind="product", name="The Credit Report Audit Kit", price=9.00,
         file_stem="The-Credit-Report-Audit-Kit",
         title="Credit Report Audit Kit, Credit Dispute Letter Templates, Credit Freeze Guide, Utilization Calculator Spreadsheet, DIY Credit",
         tags=["credit report", "credit dispute", "dispute letter", "credit freeze", "credit score",
               "credit utilization", "diy credit", "identity theft", "personal finance", "credit tracker",
               "google sheets", "excel template", "credit checklist"],
         hook="Check all three of your credit reports like an auditor, dispute real errors with ready-to-fill letters, and freeze your credit for free. No credit repair company needed.",
         get=["12-page PDF guide: free reports, line-by-line audit checklist, errors vs real negatives, how disputes work, freeze and identity theft steps, utilization, 90-day plan",
              "3 letter templates: credit bureau dispute, lender dispute, goodwill request",
              "Spreadsheet (.xlsx): account audit across the three bureaus, dispute tracker with due dates, utilization calculator, freeze record"],
         how=["Pull your three free reports.", "Run the audit checklist.", "Dispute real errors and log them.",
              "Freeze your credit and plan your utilization."], product=True,
         hero=[1, 7, 4], grid=[2, 3, 4, 5, 6, 7, 8, 9]),
    dict(slug="debt-free-date-planner", kind="product", name="The Debt-Free Date Planner", price=17.00,
         file_stem="The-Debt-Free-Date-Planner",
         title="Debt Payoff Planner Spreadsheet, Debt Snowball Avalanche Calculator, Debt Free Date, Excel Google Sheets Template + Guide",
         tags=["debt payoff", "debt snowball", "debt avalanche", "debt spreadsheet", "debt free",
               "debt calculator", "google sheets", "excel template", "credit card debt", "balance transfer",
               "debt tracker", "personal finance", "pay off debt"],
         hook="Put a real date on the day you owe nothing. Enter up to 10 debts, pick avalanche, snowball or your own order, and see your payoff month for every debt.",
         get=["Spreadsheet (.xlsx): Plan (10 debts, method switch, debt-free date, interest vs minimums only), Balance Transfer check, Consolidation check, Progress tracker with chart, 30-year schedule",
              "10-page PDF guide: worked example, choosing a method, what extra payments are worth, lower-APR script, automation, when to get help, printable payoff tracker"],
         how=["Enter balances, rates and minimums.", "Choose a method and an extra payment.",
              "Read your debt-free date.", "Log your balance monthly and watch it move."], product=True,
         hero=[1, 4, 5], grid=[2, 3, 4, 5, 6, 7, 8, 9]),
    dict(slug="investing-starter-kit", kind="product", name="Start Investing With $100 a Month", price=19.00,
         file_stem="Start-Investing-With-100-a-Month",
         title="Investing for Beginners Guide, Start Investing With $100 a Month, Roth IRA 401k Explained, Compound Interest Calculator Sheets",
         tags=["investing guide", "investing beginner", "roth ira", "401k", "index funds",
               "compound interest", "investment tracker", "google sheets", "excel template", "personal finance",
               "retirement planner", "money guide", "financial literacy"],
         hook="Which account to open first, what to buy, what fees really cost, and how to put it on autopilot. Plain English, no stock picks, no hype.",
         get=["12-page PDF guide: readiness checks, where each dollar goes first, Roth vs Traditional in one question, target-date and index funds, fees, opening and automating an account, market drops, FAQ, one-page plan",
              "Spreadsheet (.xlsx) with 6 calculators: growth with yearly increases, fee drag, 401(k) match, Roth vs Traditional, contributions vs this year's limits, order checklist"],
         how=["Do the three readiness checks.", "Follow the order of accounts.", "Pick a simple fund and check its fee.",
              "Automate a monthly amount."], product=True,
         hero=[1, 7, 9], grid=[2, 3, 4, 5, 6, 7, 9, 11]),
    # ------------------------------------------------------------------ bundles (built last)
    dict(slug="budget-binder-bundle", kind="bundle", name="Printable Budget Binder (all 10 printables)", price=12.00,
         file_stem="Printable-Budget-Binder",
         title="Budget Binder Printable Bundle, 10 Budget Planner Inserts, Bill Tracker, Savings Challenge, Sinking Funds, Debt Tracker, Letter A4",
         tags=["budget binder", "budget bundle", "budget planner", "printable bundle", "finance planner",
               "savings challenge", "bill tracker", "sinking funds", "debt tracker", "expense tracker",
               "no spend challenge", "budget printable", "money planner"],
         hook="The 10 core budget printables in one download: a complete budget binder for less than half the price of buying them one by one.",
         get=["All 10 printables (about 50 pages), each in US Letter and A4: Monthly Budget Planner, Paycheck Budget Planner, Savings Challenge Tracker, 52-Week Savings Challenge, Bill Payment Tracker, Sinking Funds Tracker, Debt Payoff Coloring Trackers, Monthly Expense Tracker, No-Spend Challenge, Subscription Tracker",
              "One zip file, organised in numbered folders",
              "Bought separately: $37. Bundle: $12"],
         how=["Download and unzip.", "Print the pages you need, in the order of the numbered folders.",
              "Put them in a binder.", "Reprint any page any time."],
         bundle=["monthly-budget-planner", "paycheck-budget-planner", "bill-payment-tracker", "sinking-funds-tracker",
                 "monthly-expense-tracker", "subscription-tracker", "savings-challenge-tracker", "52-week-savings-challenge",
                 "debt-payoff-coloring-tracker", "no-spend-challenge"]),
    dict(slug="money-toolkit-bundle", kind="product", name="The Money Made Simple Toolkit", price=39.00,
         file_stem="The-Money-Made-Simple-Toolkit",
         title="Personal Finance Bundle, Budget Spreadsheet, Debt Payoff Planner, Investing Guide, Credit Report Kit, Excel Google Sheets",
         tags=["finance bundle", "budget spreadsheet", "debt payoff", "investing guide", "credit report",
               "google sheets", "excel template", "budget planner", "personal finance", "money management",
               "debt snowball", "financial planner", "budget template"],
         hook="All five Money Made Simple guide-and-spreadsheet kits in one download: stop the leaks, run a 20-minute budget, clean up your credit, set a debt-free date and start investing.",
         get=["The Bill Cut Kit, The 20-Minute Budget, The Credit Report Audit Kit, The Debt-Free Date Planner and Start Investing With $100 a Month: 5 PDF guides (about 60 pages) and 5 spreadsheets",
              "A 'Start Here' map with a 30-day plan that uses all five",
              "Bought separately: $62. Bundle: $39"],
         how=["Open the Start Here map.", "Week 1: Bill Cut Kit. Week 2: the budget.", "Week 3: credit. Week 4: debt or investing.",
              "Keep the spreadsheets running monthly."], product=True,
         bundle=["bill-cut-kit", "20-minute-budget", "credit-report-audit-kit", "debt-free-date-planner", "investing-starter-kit"],
         hero=[1, 2, 3], grid=[1, 2, 3]),
]

def _more_listings() -> list[dict]:
    """The 30 extra printables (listings_more.py) and the two new bundles, in the same shape as above."""
    import listings_more as M
    import printables_more

    def tags(own, pool):
        seen = {t.lower() for t in own}
        return (list(own) + [t for t in M.POOL[pool] if t.lower() not in seen])[:13]

    out = []
    for d in M.ITEMS:
        n = len(printables_more.MORE[d["slug"]]())
        out.append(dict(slug=d["slug"], kind="printable", name=d["name"], price=d["price"],
                        file_stem=re.sub(r"[^A-Za-z0-9]+", "-", d["name"]).strip("-"), title=d["title"],
                        tags=tags(d["tags"], d["pool"]), hook=d["hook"], get=d["get"] + ["US Letter and A4 PDFs"],
                        how=d["how"], hero=[4, 3, 2] if n >= 4 else [3, 2] if n == 3 else [1, 2], grid=list(range(1, n + 1))))
    printable_slugs = [x["slug"] for x in LISTINGS if x["kind"] == "printable"] + [x["slug"] for x in out]
    import planner_2027
    for d in M.DATED:
        n = len(planner_2027.build(d["year"]))
        out.append(dict(slug=d["slug"], kind="printable", dated=True, name=d["name"], price=d["price"], file_stem=d["file_stem"],
                        title=d["title"], tags=tags(d["tags"], d["pool"]), hook=d["hook"], get=d["get"], how=d["how"],
                        year=d["year"], variants=d["variants"], hero=[11, 10, 1], grid=[1, 3, 4, 5, 6, 8, 10, 11, 12, 46]))
    prices = {x["slug"]: x["price"] for x in LISTINGS + out}
    names = {x["slug"]: x["name"] for x in LISTINGS + out}
    for d in M.BUNDLES:
        subs = d["bundle"] or printable_slugs
        worth = sum(prices[s] for s in subs)
        out.append(dict(slug=d["slug"], kind="bundle", name=d["name"], price=d["price"], file_stem=d["file_stem"],
                        title=d["title"], tags=tags(d["tags"], d["pool"]), hook=d["hook"],
                        get=[f"All {len(subs)} printables, each in US Letter and A4: " + ", ".join(names[s] for s in subs),
                             "One zip file, organised in numbered folders",
                             f"Bought separately: ${worth:.0f}. Bundle: ${d['price']:.0f}"],
                        how=["Download and unzip.", "Print the pages you need.", "Put them in a binder.", "Reprint any page any time."],
                        bundle=subs))
    return out


LISTINGS += _more_listings()

import seo  # noqa: E402  (titles, tags and attributes from the Nov 2026 SEO pass)
seo.apply(LISTINGS)

# Scheduled price changes from Jan 1 2027 (scouting's template-pricing-jan-2027.md, PR #2): $3 singles to $4 (the Etsy
# median for "savings challenge"), the 12-challenge pack $8 to $10. Today's price stays until then; nothing shows a
# "was" price. Change them in Etsy on Jan 1 (and Gumroad, where the same product is sold).
from datetime import date as _date  # noqa: E402
JAN1_DATE = _date(2027, 1, 1)
JAN1 = {"savings-challenge-pack": 10.0}
for it in LISTINGS:
    if it["price"] == 3:
        JAN1[it["slug"]] = 4.0
    if it["slug"] in JAN1:
        it["jan1_price"] = JAN1[it["slug"]]
        if _date.today() >= JAN1_DATE:  # rebuilt on or after Jan 1: the new price is the price
            it["price"] = it.pop("jan1_price")

for it in LISTINGS:
    it.setdefault("category", GUIDE_CAT if it["kind"] == "product" else PRINT_CAT)
    good = _good_to_know_dated(it["year"], 2 * len(it["variants"])) if it.get("dated") else None
    it["description"] = _desc(opener(it) + " " + it["hook"], it["get"], it["how"], product=it.get("product", False), good=good)
BY_SLUG = {it["slug"]: it for it in LISTINGS}

STOP = set("and or for the a an to of with your in on by".split())


def _jan1_line(it: dict) -> str:
    if "jan1_price" not in it:
        return ""
    j = fees(it["jan1_price"])
    return (f"\n**From Jan 1 2027: ${it['jan1_price']:.2f}** (scheduled, from scouting's January pricing check). On Jan 1, edit "
            f"the price in Etsy; no sale, no crossed-out price. You'd then keep about ${j['net']:.2f} a sale.\n")



def _title_problems(slug: str, title: str, tags: list[str]) -> list[str]:
    """Etsy's handbook: don't repeat words in a title; use multi-word tag phrases (same rule as brandshop/shop.py)."""
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9$']+", title) if w.lower() not in STOP]
    bad = [f"{slug}: title repeats '{w}'" for w in sorted({w for w in words if words.count(w) > 1})]
    return bad + [f"{slug}: single-word tag '{t}'" for t in tags if len(t.split()) == 1]


TAG_OK = re.compile(r"^[A-Za-z0-9 '\-]+$")


def validate() -> list[str]:
    errs = []
    seen_titles = set()
    for it in LISTINGS:
        s = it["slug"]
        if len(it["title"]) > 140:
            errs.append(f"{s}: title is {len(it['title'])} chars (max 140)")
        if it["title"] in seen_titles:
            errs.append(f"{s}: duplicate title")
        seen_titles.add(it["title"])
        errs += _title_problems(s, it["title"], it["tags"])
        if len(it["title"].split()) > 15:
            errs.append(f"{s}: title is {len(it['title'].split())} words (Etsy suggests under 15)")
        if len(it["tags"]) != 13:
            errs.append(f"{s}: {len(it['tags'])} tags (use all 13)")
        if len(set(t.lower() for t in it["tags"])) != len(it["tags"]):
            errs.append(f"{s}: duplicate tags")
        for t in it["tags"]:
            if len(t) > 20 or not TAG_OK.match(t):
                errs.append(f"{s}: bad tag '{t}' (max 20 chars, letters/numbers/spaces)")
        if not 0.20 <= it["price"] <= 50000:
            errs.append(f"{s}: price out of Etsy range")
        if re.search(r"https?://|gumroad|\.com\b|discount code|BILLCUT5|BUDGET5", it["description"], re.I):
            errs.append(f"{s}: description points off Etsy")
        if len(it["description"]) > 9000:
            errs.append(f"{s}: description too long")
        for b in it.get("bundle", []):
            if b not in BY_SLUG:
                errs.append(f"{s}: bundle item {b} has no listing")
    return errs


def fees(price: float) -> dict:
    """US seller fees per sale (Nov 2026 Etsy pricing; check etsy.com/legal/fees): listing, transaction, processing."""
    listing, transaction, processing = 0.20, round(price * 0.065, 2), round(price * 0.03 + 0.25, 2)
    total = round(listing + transaction + processing, 2)
    return {"listing": listing, "transaction": transaction, "processing": processing, "total": total,
            "net": round(price - total, 2)}


def listing_md(it: dict) -> str:
    f = fees(it["price"])
    tags = "\n".join(f"{i}. {t}" for i, t in enumerate(it["tags"], start=1))
    attrs = "\n".join(f"- **{k}:** {v}" for k, v in it.get("attributes", {}).items())
    return f"""# Etsy listing: {it['name']}

Copy each field into Etsy (Shop Manager > Listings > Add a listing). Upload the mockups in order (01 is the
thumbnail) and the files listed under "Digital files".

## Title ({len(it['title'])}/140)
{it['title']}

## Price
${it['price']:.2f}. Etsy fees per sale about ${f['total']:.2f} (listing $0.20, transaction ${f['transaction']:.2f}, processing ${f['processing']:.2f}), so you keep about **${f['net']:.2f}**.
{_jan1_line(it)}
## Listing details
- **Type:** Digital files
- **Who made it:** I did. **What is it:** A finished product. **When was it made:** the most recent range
- **Category:** {it['category']}
- **Renewal:** Automatic. **Quantity:** 999

## Attributes (fill every one Etsy shows; pick the closest option it offers)
{attrs}

## Tags (13, each 20 characters or less; paste one at a time)
{tags}

## Description
```
{it['description']}
```

## Digital files to upload
See the PDF/XLSX/ZIP files in this folder. Etsy allows up to 5 files, 20 MB each.

## Images
Upload the `mockup-*.png` files in number order (2700x2025). 01 is the thumbnail: pages only, no text, as Etsy
advises for search. 02 has the title and formats, 03 the pages inside, 04 how it works, 05-07 page close-ups. Optionally add a short
video later (Etsy shows it in search). Don't use photos of real people or brand logos you don't own.
"""
