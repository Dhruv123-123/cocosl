"""Etsy SEO pass (November 2026): titles, 13 tags and attributes for every listing.

Rules (from Etsy's Seller Handbook, "The Anatomy of a Well-Crafted Etsy Listing"):
- Titles name the item first and stay under 15 words; shoppers only see the first few words in search.
- 13 tags, multi-word phrases a shopper would type. Tags cover what the title doesn't (synonyms, long-tail, who it's for).
- Attributes act like tags, so a phrase set as an attribute doesn't need its own tag.

Keyword choices lean on public search estimates (rankhero.com keyword pages, checked Nov 2026; see SEO_NOTES.md):
"budget planner" ~60k searches/month, "savings challenge" ~10k (27k in January), "debt snowball" ~27k with under
10k competing listings, "bill tracker" ~5k, "debt tracker" ~3k, "2027 planner" rising from August.
listings.py applies these over the base data; tests check every listing is covered and within Etsy's limits.
"""
from __future__ import annotations

# Attributes. Etsy's attribute list changes by category: pick the closest option it offers.
BASE_ATTR = {"Primary color": "White", "Secondary color": "Green", "Can be personalized": "No"}
FILE_ATTR = {"Digital file type": "PDF", "Paper size": "US Letter + A4"}
SHEET_ATTR = {"Digital file type": "PDF + XLSX", "Software": "Excel, Google Sheets, Numbers"}

S = {}  # slug -> (title, tags, extra attributes)


def add(slug, title, tags, **attrs):
    S[slug] = (title, tags, attrs)


# ------------------------------------------------------------------ core printables
add("monthly-budget-planner", "Monthly Budget Planner Printable, Undated Budget Binder Pages, Bill and Savings Tracker",
    ["budget planner", "monthly budget", "budget binder", "budget printable", "finance planner", "budget worksheet",
     "household budget", "budget template", "money planner", "budget for beginner", "bill tracker", "savings tracker",
     "budget sheets"], planner_type="Monthly", dated="Undated")
add("paycheck-budget-planner", "Paycheck Budget Planner Printable, Biweekly Budget by Paycheck, Bill Planner",
    ["paycheck budget", "biweekly budget", "paycheck planner", "paycheck to paycheck", "budget by paycheck",
     "budget planner", "bill planner", "budget printable", "weekly paycheck", "budget binder", "low income budget",
     "money planner", "pay period budget"], planner_type="Budget", dated="Undated")
add("savings-challenge-tracker", "Savings Challenge Printable, $1000 Savings Tracker, Color In Money Challenge",
    ["savings challenge", "savings tracker", "money challenge", "1000 savings", "color in tracker", "savings goal",
     "savings printable", "money saving", "savings challenges", "cash stuffing", "saving tracker",
     "budget binder", "5000 challenge"], planner_type="Tracker", dated="Undated")
add("52-week-savings-challenge", "52 Week Savings Challenge Printable, $1378 Money Challenge Tracker, Reverse Chart",
    ["52 week challenge", "52 week savings", "savings challenge", "money challenge", "1378 challenge", "weekly savings",
     "savings tracker", "new year savings", "savings printable", "money saving", "savings challenges",
     "cash stuffing", "budget binder"], planner_type="Tracker", dated="Undated", holiday="New Year's")
add("bill-payment-tracker", "Bill Tracker Printable, Monthly Bill Payment Checklist and Yearly Bill Organizer",
    ["bill tracker", "bill payment tracker", "monthly bills", "bill organizer", "bill planner", "bill calendar",
     "monthly bill tracker", "payment tracker", "due date tracker", "budget binder", "budget printable",
     "household bills", "finance tracker"], planner_type="Tracker", dated="Undated")
add("sinking-funds-tracker", "Sinking Funds Tracker Printable, Savings Thermometer Pages for Your Budget Binder",
    ["sinking funds", "sinking fund tracker", "savings tracker", "savings goal", "budget binder", "cash stuffing",
     "savings thermometer", "sinking fund", "savings printable", "money tracker", "cash envelopes",
     "budget printable", "savings binder"], planner_type="Tracker", dated="Undated")
add("debt-payoff-coloring-tracker", "Debt Payoff Tracker Printable, Debt Snowball Coloring Pages, Debt Free Chart",
    ["debt payoff tracker", "debt snowball", "debt tracker", "debt free", "debt coloring page", "debt payoff",
     "debt avalanche", "pay off debt", "credit card payoff", "debt free chart", "loan tracker", "debt printable",
     "debt free journey"], planner_type="Tracker", dated="Undated")
add("monthly-expense-tracker", "Expense Tracker Printable, Monthly Spending Log and Category Summary",
    ["expense tracker", "spending tracker", "spending log", "monthly expenses", "expense log", "daily expenses",
     "budget tracker", "money tracker", "budget binder", "expense sheet", "finance tracker", "track spending",
     "budget printable"], planner_type="Tracker", dated="Undated")
add("no-spend-challenge", "No Spend Challenge Printable, 30 Day No Spend Tracker and Money Calendar",
    ["no spend challenge", "no spend tracker", "no buy challenge", "frugal living", "money challenge",
     "spending challenge", "savings challenge", "no spend month", "save money", "low buy year", "budget challenge",
     "money saving", "no spend calendar"], planner_type="Tracker", dated="Undated", holiday="New Year's")
add("subscription-tracker", "Subscription Tracker Printable, Recurring Payments Log and Cancel Checklist",
    ["subscription tracker", "subscriptions", "recurring payments", "subscription list", "bill tracker",
     "monthly bills", "payment tracker", "cancel subscription", "budget binder", "streaming tracker",
     "money tracker", "autopay tracker", "budget printable"], planner_type="Tracker", dated="Undated")

# ------------------------------------------------------------------ guides + spreadsheets
add("bill-cut-kit", "Bill Cut Kit: Subscription Audit, Bill Negotiation Scripts and Savings Spreadsheet",
    ["bill negotiation", "lower your bills", "subscription audit", "save money", "cut expenses", "money saving tips",
     "budget spreadsheet", "google sheets", "excel template", "frugal living", "bill tracker", "personal finance",
     "money guide"], **SHEET_ATTR)
add("20-minute-budget", "Budget Spreadsheet and Guide, Weekly 20 Minute Budget, Excel and Google Sheets Template",
    ["budget spreadsheet", "google sheets budget", "excel budget", "budget template", "monthly budget",
     "sinking funds", "budget for beginner", "weekly budget", "personal finance", "budget planner", "money guide",
     "finance spreadsheet", "budget tracker"], **SHEET_ATTR)
add("credit-report-audit-kit", "Credit Report Audit Kit, Dispute Letter Templates, Credit Freeze Guide and Spreadsheet",
    ["credit report", "credit repair", "dispute letter", "credit dispute", "credit freeze", "credit score",
     "credit utilization", "diy credit repair", "credit tracker", "personal finance", "google sheets",
     "excel template", "fix my credit"], **SHEET_ATTR)
add("debt-free-date-planner", "Debt Snowball Spreadsheet, Debt Payoff Planner and Guide, Excel Google Sheets",
    ["debt snowball", "debt payoff", "debt avalanche", "debt spreadsheet", "debt calculator", "debt free",
     "debt payoff planner", "credit card payoff", "snowball calculator", "debt tracker", "google sheets",
     "excel template", "balance transfer"], **SHEET_ATTR)
add("investing-starter-kit", "Investing for Beginners Guide, Start Investing With $100 a Month, Calculator Spreadsheet",
    ["investing guide", "investing beginner", "roth ira", "401k", "index funds", "compound interest",
     "investment tracker", "retirement planner", "financial literacy", "personal finance", "google sheets",
     "excel template", "money guide"], **SHEET_ATTR)

# ------------------------------------------------------------------ bundles
add("budget-binder-bundle", "Budget Binder Printable Bundle, 10 Budget Planner Inserts for Bills, Savings and Debt",
    ["budget binder", "budget bundle", "budget planner", "printable bundle", "finance planner", "binder inserts",
     "savings challenge", "bill tracker", "sinking funds", "debt tracker", "expense tracker", "cash stuffing",
     "budget printable"], planner_type="Budget", dated="Undated")
add("money-toolkit-bundle", "Personal Finance Bundle: Budget, Debt Payoff, Credit and Investing Spreadsheets and Guides",
    ["finance bundle", "budget spreadsheet", "debt snowball", "investing guide", "credit report", "google sheets",
     "excel template", "budget planner", "personal finance", "money management", "financial planner",
     "budget template", "debt payoff"], **SHEET_ATTR)
add("savings-challenge-pack", "Savings Challenge Bundle Printable, 12 Money Challenges: 100 Envelope, 52 Week, Bingo",
    ["savings challenge", "savings challenges", "money challenge", "100 envelope", "52 week challenge",
     "savings bingo", "cash stuffing", "savings tracker", "challenge bundle", "money saving", "new year savings",
     "savings printable", "budget binder"], planner_type="Tracker", dated="Undated", holiday="New Year's")
add("mega-budget-bundle", "Mega Budget Planner Bundle, 40 Printable Finance Pages: Budget, Savings, Debt Trackers",
    ["budget bundle", "budget binder", "budget planner", "finance planner", "printable bundle", "savings challenge",
     "debt tracker", "bill tracker", "sinking funds", "cash stuffing", "expense tracker", "money planner",
     "budget binder kit"], planner_type="Budget", dated="Undated")

# ------------------------------------------------------------------ 30 newer printables
add("100-envelope-challenge", "100 Envelope Challenge Printable, $5050 Savings Tracker and 50 Envelope Chart",
    ["100 envelope", "envelope challenge", "savings challenge", "5050 challenge", "cash stuffing", "cash envelopes",
     "money challenge", "savings tracker", "envelope savings", "50 envelope", "savings challenges",
     "new year savings", "budget binder"], planner_type="Tracker", dated="Undated", holiday="New Year's")
add("paycheck-savings-challenge", "Biweekly Savings Challenge Printable, 26 Paycheck Savings Tracker",
    ["biweekly savings", "paycheck savings", "savings challenge", "26 week challenge", "paycheck tracker",
     "money challenge", "payday savings", "biweekly budget", "savings tracker", "paycheck budget", "save 1000",
     "savings goal", "money saving"], planner_type="Tracker", dated="Undated")
add("30-day-savings-challenge", "30 Day Savings Challenge Printable, Save $100 $250 or $500 in a Month",
    ["30 day challenge", "savings challenge", "money challenge", "monthly challenge", "save 500", "daily savings",
     "savings tracker", "save money", "money saving", "savings challenges", "cash stuffing", "quick savings",
     "budget printable"], planner_type="Tracker", dated="Undated")
add("roll-and-save-challenge", "Dice Savings Challenge Printable, Roll and Save Money Game Tracker",
    ["dice challenge", "roll and save", "savings game", "savings challenge", "money game", "money challenge",
     "fun savings", "family savings", "savings tracker", "cash stuffing", "money saving", "savings challenges",
     "kids savings"], planner_type="Tracker", dated="Undated")
add("spare-change-jar-tracker", "Savings Jar Tracker Printable, Spare Change Coloring Chart and Money Jar Goal",
    ["savings jar", "money jar", "spare change", "coin savings", "jar tracker", "color in tracker",
     "savings tracker", "savings goal", "kids savings", "savings challenge", "money tracker", "piggy bank",
     "savings printable"], planner_type="Tracker", dated="Undated")
add("savings-bingo", "Savings Bingo Printable, $1000 and $2000 Money Challenge Bingo Cards",
    ["savings bingo", "money bingo", "bingo challenge", "savings challenge", "money challenge", "savings game",
     "1000 savings", "cash stuffing", "fun savings", "savings tracker", "savings challenges", "money game",
     "new year savings"], planner_type="Tracker", dated="Undated", holiday="New Year's")
add("travel-fund-tracker", "Vacation Savings Tracker Printable, Travel Fund Coloring Chart and Trip Budget",
    ["vacation savings", "travel fund", "trip budget", "travel savings", "vacation fund", "travel planner",
     "savings tracker", "savings goal", "holiday fund", "disney savings", "savings challenge", "trip planner",
     "color in tracker"], planner_type="Tracker", dated="Undated")
add("emergency-fund-tracker", "Emergency Fund Tracker Printable, Rainy Day Savings Goal Coloring Chart",
    ["emergency fund", "rainy day fund", "savings goal", "savings tracker", "6 month savings", "color in tracker",
     "savings challenge", "money tracker", "emergency savings", "financial safety", "savings printable",
     "cash stuffing", "budget binder"], planner_type="Tracker", dated="Undated")
add("home-fund-tracker", "House Down Payment Savings Tracker Printable, Home Fund Coloring Chart",
    ["down payment", "house fund", "home savings", "first home", "house savings", "home buying",
     "savings tracker", "savings goal", "new home fund", "savings challenge", "color in tracker",
     "first time buyer", "money tracker"], planner_type="Tracker", dated="Undated")
add("holiday-savings-planner", "Christmas Budget Planner Printable, Holiday Savings and Spending Tracker",
    ["christmas budget", "holiday budget", "holiday savings", "christmas savings", "gift budget",
     "christmas planner", "holiday planner", "christmas fund", "holiday spending", "sinking funds",
     "savings tracker", "budget printable", "gift list"], planner_type="Budget", dated="Undated", holiday="Christmas")
add("weekly-budget-planner", "Weekly Budget Planner Printable, Undated Weekly Spending Tracker",
    ["weekly budget", "weekly planner", "spending tracker", "budget planner", "weekly spending", "expense tracker",
     "budget printable", "weekly paycheck", "budget binder", "money planner", "budget worksheet",
     "daily expenses", "budget for beginner"], planner_type="Weekly", dated="Undated")
add("zero-based-budget-worksheet", "Zero Based Budget Worksheet Printable, Give Every Dollar a Job Template",
    ["zero based budget", "budget worksheet", "every dollar budget", "budget template", "monthly budget",
     "budget planner", "zero budget", "budget printable", "budget binder", "household budget",
     "budget for beginner", "money planner", "finance planner"], planner_type="Budget", dated="Undated")
add("50-30-20-budget-worksheet", "50 30 20 Budget Worksheet Printable, Needs Wants Savings Budget Template",
    ["50 30 20 budget", "budget worksheet", "budget template", "simple budget", "needs and wants", "budget rule",
     "monthly budget", "budget planner", "budget printable", "budget for beginner", "household budget",
     "money planner", "finance planner"], planner_type="Budget", dated="Undated")
add("cash-envelope-trackers", "Cash Envelope Tracker Printable, Cash Stuffing Budget Sheets",
    ["cash stuffing", "cash envelopes", "cash envelope", "envelope system", "cash budget", "envelope tracker",
     "cash budgeting", "budget binder", "sinking funds", "cash binder", "a6 binder", "expense tracker",
     "budget printable"], planner_type="Tracker", dated="Undated")
add("daily-spending-log", "Daily Spending Tracker Printable, Need vs Want Spending Journal",
    ["spending tracker", "daily expenses", "spending journal", "expense tracker", "expense log", "need vs want",
     "no spend day", "spending log", "track spending", "money tracker", "budget tracker", "money journal",
     "budget printable"], planner_type="Daily", dated="Undated")
add("grocery-budget-tracker", "Grocery Budget Tracker Printable, Meal Planner and Shopping List",
    ["grocery budget", "meal planner", "grocery list", "shopping list", "food budget", "meal plan",
     "grocery tracker", "weekly meal plan", "budget meals", "family meal plan", "kitchen printable",
     "budget printable", "money saving"], planner_type="Weekly", dated="Undated")
add("irregular-income-budget", "Irregular Income Budget Printable, Freelancer and Self Employed Budget Planner",
    ["irregular income", "freelancer budget", "variable income", "self employed", "gig worker budget",
     "commission budget", "budget planner", "small business", "income tracker", "budget worksheet",
     "budget printable", "money planner", "finance planner"], planner_type="Budget", dated="Undated")
add("utility-bill-tracker", "Utility Bill Tracker Printable, Yearly Electric Gas and Water Bill Log",
    ["utility tracker", "utility bills", "electric bill", "bill tracker", "household bills", "monthly bills",
     "bill organizer", "home expenses", "energy tracker", "bill log", "budget binder", "home binder",
     "budget printable"], planner_type="Tracker", dated="Undated")
add("car-expense-tracker", "Car Expense Tracker Printable, Fuel Log, Mileage and Maintenance Log",
    ["car maintenance", "mileage log", "fuel log", "vehicle log", "car expenses", "gas tracker", "car budget",
     "maintenance log", "mileage tracker", "auto log", "car care", "expense tracker", "budget printable"],
    planner_type="Tracker", dated="Undated")
add("financial-goals-planner", "Financial Goals Planner Printable, Money Goals Worksheet and Vision Page",
    ["financial goals", "money goals", "goal planner", "goal setting", "new year goals", "finance vision",
     "savings goal", "money mindset", "finance planner", "vision board", "yearly goals", "budget printable",
     "financial planner"], planner_type="Yearly", dated="Undated", holiday="New Year's")
add("net-worth-tracker", "Net Worth Tracker Printable, Assets and Liabilities Log with Chart",
    ["net worth tracker", "net worth", "assets liabilities", "finance tracker", "wealth tracker", "money tracker",
     "financial planner", "fire movement", "debt tracker", "investment tracker", "finance planner",
     "personal finance", "budget printable"], planner_type="Tracker", dated="Undated")
add("monthly-money-review", "Monthly Money Review Printable, Budget Check In and Finance Reflection",
    ["money review", "budget check in", "finance journal", "money journal", "monthly review", "money mindset",
     "budget reflection", "finance planner", "budget planner", "money planner", "monthly reset",
     "budget printable", "financial wellness"], planner_type="Monthly", dated="Undated")
add("credit-card-payoff-tracker", "Credit Card Payoff Tracker Printable, Debt Coloring Chart and Payment Log",
    ["credit card payoff", "credit card debt", "debt payoff tracker", "debt snowball", "debt tracker",
     "debt free", "payment tracker", "debt coloring page", "pay off debt", "debt payoff", "card payoff",
     "debt free journey", "debt printable"], planner_type="Tracker", dated="Undated")
add("debt-snowball-worksheet", "Debt Snowball Worksheet Printable, Debt Avalanche Payoff Plan",
    ["debt snowball", "snowball method", "debt avalanche", "debt payoff", "debt payoff planner",
     "debt free planner", "debt worksheet", "debt tracker", "pay off debt", "debt free", "debt planner",
     "credit card payoff", "debt printable"], planner_type="Tracker", dated="Undated")
add("debt-mountain-coloring-chart", "Debt Coloring Chart Printable, Debt Mountain Payoff Tracker",
    ["debt coloring page", "debt tracker", "debt payoff tracker", "debt snowball", "debt free chart",
     "debt free", "color in tracker", "pay off debt", "debt payoff", "debt free journey", "fridge tracker",
     "debt printable", "debt mountain"], planner_type="Tracker", dated="Undated")
add("loan-payoff-tracker", "Loan Payoff Tracker Printable, Car Loan and Student Loan Payment Chart",
    ["loan payoff tracker", "loan tracker", "student loan", "car loan", "debt payoff tracker", "debt snowball",
     "payment tracker", "mortgage payoff", "debt tracker", "debt free", "pay off debt", "loan payment",
     "debt printable"], planner_type="Tracker", dated="Undated")
add("savings-account-register", "Savings Account Register Printable, Deposit and Withdrawal Ledger",
    ["savings register", "savings ledger", "account register", "deposit log", "savings tracker", "bank ledger",
     "sinking fund", "money tracker", "transaction log", "finance tracker", "savings log", "cash stuffing",
     "budget printable"], planner_type="Tracker", dated="Undated")
add("checking-account-register", "Checking Account Register Printable, Check Register and Transaction Log",
    ["check register", "checkbook register", "account register", "transaction log", "bank ledger",
     "checkbook ledger", "bank balance", "money tracker", "finance tracker", "expense log", "check ledger",
     "budget binder", "budget printable"], planner_type="Tracker", dated="Undated")
add("gift-budget-planner", "Gift Budget Planner Printable, Christmas and Birthday Gift Tracker",
    ["gift tracker", "gift budget", "christmas gift list", "gift list", "birthday tracker", "christmas budget",
     "gift planner", "holiday budget", "gift organizer", "christmas planner", "present list", "holiday planner",
     "budget printable"], planner_type="Budget", dated="Undated", holiday="Christmas")
add("side-hustle-income-tracker", "Side Hustle Income Tracker Printable, Small Business Income and Expense Log",
    ["side hustle", "income tracker", "small business", "income and expense", "freelance tracker",
     "business expenses", "profit tracker", "tax tracker", "self employed", "bookkeeping", "sales tracker",
     "expense log", "business planner"], planner_type="Tracker", dated="Undated")

# ------------------------------------------------------------------ dated
add("2027-budget-planner", "2027 Budget Planner Printable, Dated Monthly Budget Calendar and Finance Planner",
    ["2027 budget planner", "2027 planner", "2027 calendar", "budget planner", "monthly budget", "finance planner",
     "budget calendar", "yearly planner", "new year planner", "2027 monthly", "budget binder", "bill tracker",
     "money planner"], planner_type="Yearly", dated="Dated: 2027", holiday="New Year's")

ATTR_NAMES = {"planner_type": "Calendar / planner type", "dated": "Dated or undated", "holiday": "Holiday"}


def attributes(slug: str, kind: str) -> dict:
    extra = S[slug][2]
    out = dict(BASE_ATTR)
    out.update(FILE_ATTR if kind != "product" else {})
    for k, v in extra.items():
        out[ATTR_NAMES.get(k, k)] = v
    return out


def apply(listings: list[dict]) -> None:
    for it in listings:
        title, tags, _ = S[it["slug"]]
        it["title"], it["tags"] = title, list(tags)
        it["attributes"] = attributes(it["slug"], it["kind"])
