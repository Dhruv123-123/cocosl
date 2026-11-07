"""The template line: what each one is, its price, and its store copy (Gumroad + Notion Marketplace)."""
from __future__ import annotations

SHEETS_HOW = ["Buy, then open the Start Here PDF in your download.",
              "Click the link and press **Make a copy**. The sheet lands in your own Google Drive.",
              "Follow the Start tab: type over the example data (yellow cells). Everything else calculates."]
NOTION_HOW = ["Buy, then open the Start Here PDF in your download.",
              "Click the link and press **Duplicate** (top right). The template lands in your own Notion workspace.",
              "Type over the example rows, or delete them. Works on the free Notion plan."]
LEGAL = ("Educational organising tool, not financial advice. Example data is fictional. For personal use by the buyer; "
         "please don't resell or share the template.")

ITEMS = [
    {
        "slug": "budget-sheet", "kind": "sheets", "name": "Monthly Budget Sheet", "price": 9,
        "xlsx": "Monthly-Budget-Sheet.xlsx", "link": "sheet_budget",
        "title": "Monthly Budget Sheet for Google Sheets: zero-based budget, spending tracker + dashboard",
        "tagline": "Plan every dollar, log what you spend, and see each category against its budget. Google Sheets or Excel.",
        "hook": "Most budget spreadsheets are either a blank grid or a 40-tab monster. This one is four tabs and "
                "about five minutes to set up.",
        "gets": ["**Setup:** up to 30 categories in five groups (Income, Needs, Wants, Savings, Debt) and a 'left to "
                 "assign' check that hits $0 when every dollar has a job.",
                 "**Transactions:** 500 rows with a category dropdown. Money in and out, always positive numbers.",
                 "**Dashboard:** pick any month. Income, needs, wants, savings and debt against plan, your % split, "
                 "and every category with a progress bar. Red means over.",
                 "**Year:** twelve months side by side, group totals and an income vs spending chart.",
                 "A Start tab with the 5-minute setup, filled with example data so you can see it working."],
        "who": "Anyone starting a budget, or anyone whose budget lives in their head and keeps losing.",
        "faq": [("Do I need Excel?", "No. It's made for Google Sheets (free). The .xlsx also works in Excel and Numbers."),
                ("Does it connect to my bank?", "No, and that's on purpose: nothing to hack, no subscription. You type "
                                                "transactions in, which takes about two minutes a day or ten a week."),
                ("Can I change the categories?", "Yes. Rename, add or delete them on Setup; the dashboard follows.")],
        "tags": ["budget template", "google sheets budget", "budget spreadsheet", "zero based budget", "expense tracker",
                 "monthly budget", "personal finance"],
        "next": "money-sheets-bundle", "shots": [("Dashboard", "B1:H32"), ("Transactions", "B1:G26"), ("Year", "B1:P22")],
    },
    {
        "slug": "debt-payoff-sheet", "kind": "sheets", "name": "Debt Payoff Sheet", "price": 12,
        "xlsx": "Debt-Payoff-Sheet.xlsx", "link": "sheet_debt",
        "title": "Debt Payoff Sheet for Google Sheets: snowball or avalanche planner, debt-free date + payment log",
        "tagline": "See your debt-free date by snowball or avalanche, then log payments and watch every balance fall.",
        "hook": "\"Pay off debt\" is a wish. \"Debt-free in March 2030, and here's this month's payment\" is a plan.",
        "gets": ["**Plan:** up to 10 debts. Pick Avalanche (least interest), Snowball (quick wins) or your own order, "
                 "add an extra monthly amount, and get your debt-free date, total interest, and how much sooner and "
                 "cheaper it is than paying minimums.",
                 "**Rollover built in:** when a debt is paid off, its payment moves to the next one automatically.",
                 "**Payments:** log what you pay and the interest on your statement; each debt shows what's left.",
                 "**Progress:** plan vs actual each month, with a chart.",
                 "**Schedule:** the full 30-year month-by-month maths, so you can check every number."],
        "who": "Anyone with two or more debts who wants a date to aim at. Credit cards, store cards, car, student "
               "and personal loans.",
        "faq": [("Avalanche or snowball?", "Avalanche (highest APR first) costs the least. Snowball (smallest balance "
                                         "first) gives faster wins. The sheet shows both; pick the one you'll stick to."),
                ("How exact is the date?", "It works interest out monthly (APR / 12), so it's an estimate. Lenders "
                                           "calculate daily, so real numbers differ slightly."),
                ("Is this the Debt-Free Date Planner?", "It's the same payoff engine, as a template. The $17 Debt-Free "
                 "Date Planner adds a 10-page guide plus balance-transfer and consolidation-loan calculators.")],
        "tags": ["debt payoff", "debt snowball", "debt avalanche", "google sheets", "debt tracker", "debt free",
                 "credit card payoff"],
        "next": "money-sheets-bundle", "shots": [("Plan", "B1:L33"), ("Payments", "B1:N18"), ("Progress", "B1:F26")],
    },
    {
        "slug": "savings-goals-sheet", "kind": "sheets", "name": "Savings Goals Sheet", "price": 7,
        "xlsx": "Savings-Goals-Sheet.xlsx", "link": "sheet_savings",
        "title": "Savings Goals Sheet for Google Sheets: sinking funds, emergency fund + monthly savings plan",
        "tagline": "Every goal, sinking fund and your emergency fund in one sheet, with what to save each month.",
        "hook": "Saving 'whatever's left' leaves nothing. Saving $130 a month for car repairs means the repair "
                "isn't an emergency.",
        "gets": ["**Goals:** up to 15 goals, sinking funds and emergency funds, each with a target, a date, a progress "
                 "bar, months left and how much a month gets you there.",
                 "**Your monthly savings plan:** the total of every goal's monthly amount, in one number.",
                 "**Deposits:** log transfers in and out (withdrawals are negative), linked to a goal.",
                 "**Emergency Fund:** add up essentials, pick how many months, and see how many months you're "
                 "covered today.", "A saved vs target chart."],
        "who": "Anyone saving for more than one thing, or tired of irregular bills (car, gifts, insurance) "
               "becoming credit-card surprises.",
        "faq": [("What's a sinking fund?", "Money you set aside monthly for a cost you know is coming: gifts, car repairs, "
                                          "a yearly insurance bill. When it arrives, it's already paid for."),
                ("Do I need separate bank accounts?", "No. One savings account is fine; the sheet keeps track of what "
                                                      "each dollar is for.")],
        "tags": ["savings tracker", "sinking funds", "savings goals", "google sheets", "emergency fund",
                 "savings plan", "budget template"],
        "next": "money-sheets-bundle", "shots": [("Goals", "B1:M23"), ("Deposits", "B1:E22"), ("Emergency Fund", "B1:D25")],
    },
    {
        "slug": "money-sheets-bundle", "kind": "sheets-bundle", "name": "Money Sheets Bundle", "price": 19,
        "bundle": ["budget-sheet", "debt-payoff-sheet", "savings-goals-sheet"], "link": None,
        "title": "Money Sheets Bundle: budget, debt payoff + savings goals templates for Google Sheets",
        "tagline": "All three Money Made Simple sheets: budget, debt payoff and savings goals. $28 separately, $19 together.",
        "hook": "Budget, pay off debt, save. Three sheets that each do one job well, for less than the price of two.",
        "gets": ["**Monthly Budget Sheet** ($9): zero-based budget, transactions, dashboard and year view.",
                 "**Debt Payoff Sheet** ($12): avalanche or snowball, debt-free date, payment log, progress chart.",
                 "**Savings Goals Sheet** ($7): goals, sinking funds, emergency fund and a monthly savings plan.",
                 "One Start Here PDF with all three copy links, plus the .xlsx files for Excel or Numbers."],
        "who": "Anyone setting up their whole money system in one weekend.",
        "faq": [("Already bought one?", "Reply to your receipt email and we'll send a code for the bundle minus what you paid.")],
        "tags": ["budget bundle", "google sheets", "budget template", "debt payoff", "savings tracker",
                 "personal finance", "spreadsheet bundle"],
        "next": None,
    },
    {
        "slug": "notion-budget", "kind": "notion", "name": "Notion Budget Planner", "price": 9, "link": "notion_budget",
        "title": "Notion Budget Planner: categories, transactions + a monthly dashboard",
        "tagline": "Plan every dollar in Notion. Log transactions and every category updates: this month, last month, left.",
        "hook": "If your life already runs in Notion, your money should too.",
        "gets": ["**Categories** database: group, monthly budget, this month, last month, left, a progress bar and a status "
                 "(🟢 on track, 🔴 over).", "**Transactions** database linked to categories, with a This month view.",
                 "A 10-minute monthly check-in checklist.", "Example data so you can see it working, and a Start Here guide."],
        "who": "Notion users who want a budget they'll actually open.",
        "faq": [("Free Notion plan OK?", "Yes. Everything works on the free plan."),
                ("Bank sync?", "No. You log transactions yourself (the mobile app makes it quick).")],
        "tags": ["notion template", "notion budget", "budget planner", "finance tracker", "expense tracker",
                 "personal finance", "money"],
        "notion_category": "Personal finance", "next": "notion-money-hq",
    },
    {
        "slug": "notion-debt-payoff", "kind": "notion", "name": "Notion Debt Payoff Tracker", "price": 12,
        "link": "notion_debt",
        "title": "Notion Debt Payoff Tracker: avalanche + snowball views, payoff dates, payment log",
        "tagline": "Every debt with its balance, payoff date and progress bar. Avalanche and Snowball views tell you what to pay next.",
        "hook": "One page that answers \"which debt do I pay first?\" and \"when will I be done?\"",
        "gets": ["**Debts** database: starting balance, APR, minimum, extra, balance now, interest this month, months left, "
                 "a debt-free month and a progress bar.", "**Avalanche** and **Snowball** views: the top row is where your "
                 "extra money goes.", "**Payments** log linked to each debt; principal is worked out from the interest "
                 "on your statement.", "A rollover reminder and a monthly check-in."],
        "who": "Notion users with two or more debts.",
        "faq": [("How exact are the dates?", "They're estimates: monthly interest (APR / 12), and each debt at its own "
                                             "payment. Good for planning; your lender's statement is the final word.")],
        "tags": ["notion template", "debt payoff", "debt snowball", "debt tracker", "debt free", "finance tracker",
                 "personal finance"],
        "notion_category": "Personal finance", "next": "notion-money-hq",
    },
    {
        "slug": "notion-savings-goals", "kind": "notion", "name": "Notion Savings Goals Tracker", "price": 7,
        "link": "notion_savings",
        "title": "Notion Savings Goals Tracker: goals, sinking funds + monthly targets",
        "tagline": "Goals and sinking funds with progress bars, deposits, and how much to save each month to hit each date.",
        "hook": "Watch the bars fill. Know exactly what to move to savings on payday.",
        "gets": ["**Savings goals** database: type (goal, sinking fund, emergency fund), target, date, saved, left, "
                 "months left, per month and status.", "**Deposits** log linked to each goal.",
                 "Gallery and Plan views; the Plan total is your monthly savings plan.", "Emergency fund quick maths."],
        "who": "Notion users saving for more than one thing.",
        "faq": [("Withdrawals?", "Log them as a negative deposit and the goal updates.")],
        "tags": ["notion template", "savings tracker", "sinking funds", "savings goals", "finance tracker",
                 "personal finance", "money"],
        "notion_category": "Personal finance", "next": "notion-money-hq",
    },
    {
        "slug": "notion-money-hq", "kind": "notion-bundle", "name": "Notion Money HQ", "price": 19, "link": "notion_hq",
        "bundle": ["notion-budget", "notion-debt-payoff", "notion-savings-goals"],
        "title": "Notion Money HQ: budget, debt payoff + savings goals in one finance dashboard",
        "tagline": "Budget, debt payoff and savings goals in one Notion home, plus a weekly money check-in. $28 separately, $19 together.",
        "hook": "Your whole money system on one Notion page, and a 10-minute weekly habit to keep it honest.",
        "gets": ["**Notion Budget Planner** ($9)", "**Notion Debt Payoff Tracker** ($12)",
                 "**Notion Savings Goals Tracker** ($7)",
                 "**Weekly money check-in** database with a 5-point score, and a home page that ties it together."],
        "who": "Notion users who want one place for everything money.",
        "faq": [("Already bought one?", "Reply to your receipt email and we'll send a code for the HQ minus what you paid.")],
        "tags": ["notion template", "finance dashboard", "notion budget", "debt payoff", "savings tracker",
                 "personal finance", "life os"],
        "notion_category": "Personal finance", "next": None,
    },
    {
        "slug": "budget-sheet-2027", "kind": "sheets", "name": "2027 Budget Sheet", "price": 12,
        "xlsx": "2027-Budget-Sheet.xlsx", "link": "sheet_budget_2027",
        "title": "2027 Budget Spreadsheet for Google Sheets: monthly tabs Jan to Dec 2027 + year dashboard",
        "tagline": "A dated 2027 budget: one tab per month, each with its own budget and spending log, and the whole year on one page.",
        "hook": "A fresh year, already set up: open January 2027, type your numbers, and the year page fills itself in.",
        "gets": ["**Setup:** up to 30 categories in five groups, with a default monthly budget and a 'left to assign' check.",
                 "**Twelve dated month tabs (Jan 2027 to Dec 2027):** that month's budget (change any line for that month only), "
                 "planned vs actual by group, every category with a progress bar, and a 120-row spending log that only "
                 "accepts dates in that month.",
                 "**2027 tab:** every category month by month, group totals, average per month and an income vs left-over chart.",
                 "A Start tab with the 5-minute setup, and example data in January and February to delete."],
        "who": "Anyone starting 2027 with a budget, who likes one tab per month instead of one long list.",
        "faq": [("Do I need Excel?", "No. It's made for Google Sheets (free). The .xlsx also works in Excel and Numbers."),
                ("What about 2028?", "This one is dated 2027. The undated Monthly Budget Sheet works for any year.")],
        "tags": ["2027 budget", "budget spreadsheet", "google sheets budget", "monthly budget", "2027 planner",
                 "budget template", "personal finance"],
        "next": None, "shots": [("Jan 2027", "B1:H32"), ("2027", "B1:Q22"), ("Setup", "B1:E28")],
    },
    {
        "slug": "notion-money-hq-2027", "kind": "notion", "name": "2027 Money HQ for Notion", "price": 24,
        "link": "notion_hq_2027",
        "title": "2027 Notion Money HQ: dated budget by month, debt payoff, savings goals + monthly reviews",
        "tagline": "The Money HQ, dated for 2027: a budget that fills in January to December, a review page for every month, "
                   "debt payoff, savings goals and a weekly check-in.",
        "hook": "Your 2027 money year on one Notion page, with each month's numbers and review in one place.",
        "gets": ["**2027 Budget:** categories with a column for every month of 2027, a 2027 total and a 2027 budget, "
                 "plus this month, last month and left.",
                 "**2027 month by month:** twelve dated pages with a monthly review (budget set, all logged, reviewed), "
                 "a big win and one change for next month.",
                 "**Debt Payoff Tracker** and **Savings Goals Tracker**, the same as in the Money HQ.",
                 "**Weekly money check-in** with a 5-point score. Example data in January 2027."],
        "who": "Notion users who want to run 2027's money in one place and see the year fill in.",
        "faq": [("Free Notion plan OK?", "Yes. Everything works on the free plan."),
                ("Already have the Money HQ?", "Reply to your receipt email and we'll send a code for the difference.")],
        "tags": ["notion template", "2027 planner", "notion budget", "finance dashboard", "debt payoff",
                 "savings tracker", "personal finance"],
        "notion_category": "Personal finance", "next": None,
    },
    {
        "slug": "notion-money-starter", "kind": "free", "name": "Notion Money Starter", "price": 0, "link": "notion_starter",
        "title": "Free Notion Money Starter: simple budget, one savings goal + weekly check-in",
        "tagline": "A free, simple start: one month's budget, one savings goal and a 10-minute weekly check-in.",
        "hook": "Not ready for a whole system? Start with one page.",
        "gets": ["**This month's budget:** categories, budget, spent, left and a progress bar.",
                 "**One savings goal** with a progress bar.", "A three-step weekly check-in."],
        "who": "Anyone who wants to try budgeting in Notion before buying anything.",
        "faq": [("Why do you ask for my email?", "So we can send you the template and the free weekly Money Made Simple "
                                                 "email. Unsubscribe any time with one click.")],
        "tags": ["free notion template", "notion budget", "budget planner", "personal finance", "savings goal",
                 "beginner budget", "money"],
        "notion_category": "Personal finance", "next": "notion-money-hq",
    },
]

from twins_catalog import ITEMS as _TWINS  # noqa: E402  (Sheets + Notion versions of five printables)

ITEMS += _TWINS
# Life-event budgets (scouting's competitor-product-gaps.md, Nov 2026). Pairs with the apps thread's wedding planner tool.
ITEMS.append({
    "slug": "wedding-budget-sheet", "kind": "sheets", "name": "Wedding Budget Sheet", "price": 12,
    "xlsx": "Wedding-Budget-Sheet.xlsx", "link": "sheet_wedding",
    "title": "Wedding Budget Spreadsheet for Google Sheets: budget vs actual, payment due dates + who's paying",
    "tagline": "Plan every category, log each vendor payment with its due date, and see who's covering what, with RSVPs and cost per guest.",
    "hook": "Keep the wedding money in one place: what you planned, what you've booked, what's paid, and what's due next.",
    "gets": ["**Budget:** 20 wedding categories with planned, booked, paid, still owed and planned minus booked.",
             "**Payments:** every deposit and balance with its due date, paid or not, and who's paying. Overdue turns red; "
             "due in the next 30 days turns yellow.",
             "**Due by month:** the payment calendar for the next 12 months, with a chart.",
             "**Who's paying:** each person's promise against the payments assigned to them.",
             "**Guests:** RSVPs and party sizes, and the cost per guest on the Dashboard."],
    "who": "Couples (and the families helping) who want one shared sheet instead of five vendor emails.",
    "faq": [("Do I need Excel?", "No. It's made for Google Sheets (free) so you can share it with your partner and family. "
                                 "The .xlsx also opens in Excel and Numbers."),
            ("Does it tell me what to spend?", "No. You type your own plan for each category; the sheet keeps the totals."),
            ("Can I rename the categories?", "Yes. Type over them on Budget; the Payments list follows.")],
    "tags": ["wedding budget", "wedding planner", "google sheets", "wedding spreadsheet", "budget tracker",
             "wedding checklist", "personal finance"],
    "next": "budget-sheet", "shots": [("Dashboard", "B1:C16"), ("Payments", "B1:J20"), ("Budget", "B1:H28")],
})
# Scouting's product-ideas-round2.md (PR #2): sinking funds (27,100 searches, January peak) and moving (14,800, May-Aug peak).
ITEMS.append({
    "slug": "sinking-funds-sheet", "kind": "sheets", "name": "Sinking Funds Sheet", "price": 7,
    "xlsx": "Sinking-Funds-Sheet.xlsx", "link": "sheet_sinking",
    "title": "Sinking Funds Spreadsheet for Google Sheets: monthly and per-paycheck savings for the bills you know are coming",
    "tagline": "List the bills you know are coming, and the sheet works out how much to set aside each month and each payday.",
    "hook": "Car insurance, the holidays, the vet: list them once and see exactly what to move to savings each payday.",
    "gets": ["**Funds:** each fund's target and date, with saved, still to save, months left, save each month and a progress bar. "
             "Late funds turn red; full ones turn green.",
             "**Deposits:** log each deposit and pick the fund from a list.",
             "**Dashboard:** the total to move each month and each paycheck, the next fund due, and a saved-vs-target chart.",
             "**Year ahead:** what comes due in each of the next 12 months.",
             "**Pairs with our free sinking-funds planner:** its Copy buttons paste straight into the Funds tab."],
    "who": "Anyone tired of the same 'surprise' bills every year: insurance, holidays, car repairs, school.",
    "faq": [("Do I need Excel?", "No. It's made for Google Sheets (free). The .xlsx also opens in Excel and Numbers."),
            ("How does it work out the monthly amount?", "Still to save divided by the months left, counting the month it's due."),
            ("Can I add my own funds?", "Yes, up to 20. Type over the examples.")],
    "tags": ["sinking funds", "savings tracker", "google sheets", "budget spreadsheet", "cash stuffing",
             "savings goals", "personal finance"],
    "next": "budget-sheet", "shots": [("Funds", "A1:I14"), ("Dashboard", "B1:C17"), ("Year ahead", "B1:D18")],
})
ITEMS.append({
    "slug": "moving-budget-sheet", "kind": "sheets", "name": "Moving Budget Sheet", "price": 9,
    "xlsx": "Moving-Budget-Sheet.xlsx", "link": "sheet_moving",
    "title": "Moving Budget Spreadsheet for Google Sheets: moving costs, mover quotes and a utilities tracker",
    "tagline": "Estimate every moving cost, compare movers side by side, and track each utility you stop and start.",
    "hook": "The move in one sheet: what it will cost, what you've paid, which mover is cheapest, and which utilities are sorted.",
    "gets": ["**Budget:** 11 moving costs with estimate, actual, paid, still to pay and estimate minus actual, plus a chart.",
             "**Quotes:** three movers or truck rentals side by side, with the cheapest picked out.",
             "**Utilities:** stop, start or transfer each service, with dates, deposits and confirmation numbers.",
             "**Setup:** moving date, days to go and your total budget.",
             "**Pairs with our free moving cost calculator:** its Copy rows paste into the Planner paste tab."],
    "who": "Renters and homeowners planning a move who want the costs and the to-dos in one place.",
    "faq": [("Do I need Excel?", "No. It's made for Google Sheets (free). The .xlsx also opens in Excel and Numbers."),
            ("Does it tell me what a move should cost?", "No. You type your own estimates and quotes; the sheet keeps the totals."),
            ("Is there a printable version?", "Yes: the Moving Planner printable has the same categories, a checklist and a utilities page.")],
    "tags": ["moving budget", "moving checklist", "google sheets", "moving planner", "budget tracker",
             "new home", "personal finance"],
    "next": "budget-sheet", "shots": [("Budget", "B1:H20"), ("Quotes", "B1:E19"), ("Utilities", "B1:I20")],
})
BY_SLUG = {i["slug"]: i for i in ITEMS}
