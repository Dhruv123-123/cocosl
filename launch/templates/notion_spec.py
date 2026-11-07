"""Notion templates, described once as data.

The same spec drives three things:
  * notion_build.py  builds the template in your Notion workspace through the Notion API
  * build_templates.py writes BUILD.md (the by-hand steps), example CSVs and preview images
  * tests/test_templates.py checks every formula only names properties that exist

Formulas are Notion formula 2.0 expressions. Each one carries a Python twin (`py`) used only to draw the
preview images with the example data, so the previews show what the template really calculates.

Dates in example rows are relative, so "this month" views have data whenever the template is built:
"this:5" = the 5th of this month, "last:16" = the 16th of last month, "+13m" = 13 months from today.
"""
from __future__ import annotations

import calendar
import math
from datetime import date

# ---- helpers used by the Python twins ---------------------------------------------------------------


def _ym(d):
    return (d.year, d.month) if d else None


def _add_months(d: date, n: int) -> date:
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _months_between(a: date, b: date) -> int:
    """Notion's dateBetween(a, b, "months"): whole months from b to a."""
    n = (a.year - b.year) * 12 + a.month - b.month
    if n > 0 and a.day < b.day:
        n -= 1
    elif n < 0 and a.day > b.day:
        n += 1
    return n


def _bar(frac: float) -> str:
    n = max(0, min(10, round(frac * 10)))
    return "■" * n + "□" * (10 - n) + f" {round(frac * 100)}%"


def bar_expr(num: str, den: str) -> str:
    """Notion formula for a 10-block progress bar + percent. num/den are formula expressions."""
    f = f"({num}) / ({den})"
    return (f'if({den} > 0, repeat("■", min(max(round({f} * 10), 0), 10)) + '
            f'repeat("□", 10 - min(max(round({f} * 10), 0), 10)) + " " + format(round({f} * 100)) + "%", "")')


def P(name: str) -> str:
    return f'prop("{name}")'


def resolve_date(token, today: date):
    if token is None or isinstance(token, date):
        return token
    if token.startswith("this:") or token.startswith("last:"):
        base = date(today.year, today.month, 1)
        if token.startswith("last:"):
            base = _add_months(base, -1)
        day = int(token.split(":")[1])
        return base.replace(day=min(day, calendar.monthrange(base.year, base.month)[1]))
    if token.startswith("+") and token.endswith("m"):
        return _add_months(today, int(token[1:-1])).replace(day=1)
    raise ValueError(token)


GROUP_COLORS = {"Income": "green", "Needs": "blue", "Wants": "purple", "Savings": "yellow", "Debt": "red",
                "Goal": "blue", "Sinking fund": "purple", "Emergency fund": "green"}

# ---- Budget -------------------------------------------------------------------------------------------
_this = f'prop("Transactions").filter(formatDate(current.prop("Date"), "YYYY-MM") == formatDate(now(), "YYYY-MM")).map(current.prop("Amount")).sum()'
_last = ('prop("Transactions").filter(formatDate(current.prop("Date"), "YYYY-MM") == '
         'formatDate(dateSubtract(now(), 1, "months"), "YYYY-MM")).map(current.prop("Amount")).sum()')


def _sum_month(rows, today, back=0):
    target = _ym(_add_months(date(today.year, today.month, 1), -back))
    return round(sum(r["Amount"] for r in rows if _ym(r["Date"]) == target), 2)


BUDGET_CATEGORIES = {
    "key": "categories", "title": "Categories", "icon": "🗂️",
    "props": [
        ("Name", "title", {}),
        ("Group", "select", {"options": ["Income", "Needs", "Wants", "Savings", "Debt"]}),
        ("Monthly budget", "number", {"format": "dollar"}),
        ("This month", "formula", {"expr": _this, "format": "dollar",
                                   "py": lambda r, t: _sum_month(r["Transactions"], t)}),
        ("Left", "formula", {"expr": f'{P("Monthly budget")} - {P("This month")}', "format": "dollar",
                             "py": lambda r, t: round(r["Monthly budget"] - r["This month"], 2)}),
        ("Used", "formula", {"expr": bar_expr(P("This month"), P("Monthly budget")),
                             "py": lambda r, t: _bar(r["This month"] / r["Monthly budget"]) if r["Monthly budget"] else ""}),
        ("Status", "formula", {"expr": (f'if({P("Group")} == "Income", if({P("This month")} >= {P("Monthly budget")}, '
                                        f'"✅ All in", "⏳ Still coming"), if({P("This month")} > {P("Monthly budget")}, '
                                        f'"🔴 Over", "🟢 On track"))'),
                               "py": lambda r, t: (("✅ All in" if r["This month"] >= r["Monthly budget"] else "⏳ Still coming")
                                                   if r["Group"] == "Income" else
                                                   ("🔴 Over" if r["This month"] > r["Monthly budget"] else "🟢 On track"))}),
        ("Last month", "formula", {"expr": _last, "format": "dollar",
                                   "py": lambda r, t: _sum_month(r["Transactions"], t, 1)}),
    ],
    "rows": [
        {"Name": n, "Group": g, "Monthly budget": b} for n, g, b in [
            ("Paycheck", "Income", 3800), ("Side income", "Income", 300), ("Rent", "Needs", 1400),
            ("Utilities", "Needs", 180), ("Groceries", "Needs", 450), ("Transport", "Needs", 220),
            ("Insurance", "Needs", 140), ("Phone + internet", "Needs", 110), ("Eating out", "Wants", 160),
            ("Fun", "Wants", 120), ("Shopping", "Wants", 100), ("Subscriptions", "Wants", 45),
            ("Emergency fund", "Savings", 250), ("Sinking funds", "Savings", 150), ("Extra debt payment", "Debt", 200)]
    ],
    "views": [
        "Table view **This month**: group by *Group*; show Name, Monthly budget, This month, Left, Used, Status; "
        "turn on the footer sum (Calculate > Sum) for Monthly budget, This month and Left.",
        "Board view **By group**: group by *Group*, card preview off, show Used and Status on cards.",
    ],
}


def _tx(spec):
    out = []
    for when in ("last", "this"):
        for day, name, cat, amt in spec:
            if when == "this" and day > 7:
                continue
            out.append({"Name": name, "Date": f"{when}:{day}", "Amount": amt, "Category": cat})
    return out


BUDGET_TRANSACTIONS = {
    "key": "transactions", "title": "Transactions", "icon": "🧾",
    "props": [
        ("Name", "title", {}),
        ("Date", "date", {}),
        ("Amount", "number", {"format": "dollar"}),
        ("Category", "relation", {"db": "categories", "reverse": "Transactions", "single": True}),
        ("Group", "formula", {"expr": 'prop("Category").map(current.prop("Group")).first()',
                              "py": lambda r, t: r["Category"][0]["Group"] if r["Category"] else ""}),
        ("Month", "formula", {"expr": 'formatDate(prop("Date"), "MMM YYYY")',
                              "py": lambda r, t: r["Date"].strftime("%b %Y")}),
    ],
    "rows": _tx([(1, "Paycheck", "Paycheck", 1900), (1, "Rent", "Rent", 1400), (2, "Grocery run", "Groceries", 112.35),
                 (3, "Electric + water", "Utilities", 96.4), (4, "Streaming x2", "Subscriptions", 28.98),
                 (5, "Fuel", "Transport", 48), (6, "Tacos with friends", "Eating out", 38.5),
                 (7, "Car + renters insurance", "Insurance", 140), (9, "Grocery run", "Groceries", 98.1),
                 (10, "Phone + internet", "Phone + internet", 110), (12, "Bus pass", "Transport", 64),
                 (13, "Movie tickets", "Fun", 32), (14, "Pizza night", "Eating out", 31.2),
                 (15, "Paycheck", "Paycheck", 1900), (16, "Grocery run", "Groceries", 121.6),
                 (16, "Transfer to savings", "Emergency fund", 250), (16, "Gifts + car fund", "Sinking funds", 150),
                 (17, "Extra on credit card", "Extra debt payment", 200), (18, "Gas bill", "Utilities", 61.2),
                 (19, "Fuel", "Transport", 51.5), (20, "Concert", "Fun", 68), (21, "Coffee + lunch", "Eating out", 54.9),
                 (22, "Freelance logo job", "Side income", 280), (23, "Market", "Groceries", 44.8),
                 (8, "Shoes", "Shopping", 74.99), (11, "Music app", "Subscriptions", 11.99)]),
    "views": [
        "Table view **This month**: filter *Date* is relative to today > *This month*; sort *Date* descending; "
        "footer sum on Amount.",
        "Table view **All**: sort *Date* descending; group by *Month*.",
    ],
}

BUDGET = {
    "slug": "notion-budget", "name": "Notion Budget Planner", "icon": "💸",
    "dbs": [BUDGET_TRANSACTIONS, BUDGET_CATEGORIES],
    "layout": [
        ("callout", "💡", "Plan every dollar, log what you spend, and see each category's month at a glance. "
                         "Example data is filled in. Delete it or type over it."),
        ("h2", "1. Your categories"),
        ("p", "One row per category. Set the group and what you plan each month. Income is planned the same way."),
        ("db", "categories"),
        ("h2", "2. Log money in and out"),
        ("p", "New row, a few words, the date, the amount (always positive), and pick the category. "
              "Categories update instantly."),
        ("db", "transactions"),
        ("h2", "3. Monthly check-in (10 minutes)"),
        ("todo", "Every transaction for the month is logged"),
        ("todo", "Look at anything 🔴 Over. Move money from a 🟢 category to cover it"),
        ("todo", "Set next month's budgets (copy last month's, then adjust)"),
        ("todo", "Leftover money gets a job: savings or extra debt payment"),
        ("divider",),
        ("small", "Money Made Simple · Educational organising tool, not financial advice. "
                  "Personal use only; please don't resell or share this template."),
    ],
}

# ---- Debt ---------------------------------------------------------------------------------------------
_r = f'{P("APR %")} / 1200'
_months = (f'if({P("Balance now")} <= 0, 0, if({P("Monthly payment")} <= 0, -1, if({P("APR %")} == 0, '
           f'ceil({P("Balance now")} / {P("Monthly payment")}), if({P("Monthly payment")} <= {P("Balance now")} * {_r}, -1, '
           f'ceil(-ln(1 - {P("Balance now")} * {_r} / {P("Monthly payment")}) / ln(1 + {_r}))))))')


def _months_py(r, t):
    b, p, a = r["Balance now"], r["Monthly payment"], r["APR %"] / 1200
    if b <= 0:
        return 0
    if p <= 0:
        return -1
    if a == 0:
        return math.ceil(b / p)
    if p <= b * a:
        return -1
    return math.ceil(-math.log(1 - b * a / p) / math.log(1 + a))


DEBT_PAYMENTS = {
    "key": "payments", "title": "Payments", "icon": "🧾",
    "props": [
        ("Name", "title", {}),
        ("Date", "date", {}),
        ("Paid", "number", {"format": "dollar"}),
        ("Interest", "number", {"format": "dollar"}),
        ("Debt", "relation", {"db": "debts", "reverse": "Payments", "single": True}),
        ("Principal", "formula", {"expr": f'{P("Paid")} - {P("Interest")}', "format": "dollar",
                                  "py": lambda r, t: round(r["Paid"] - r["Interest"], 2)}),
    ],
    "rows": [{"Name": f"{d} payment", "Date": when, "Paid": paid, "Interest": i, "Debt": d}
             for when, rows in (("last:5", [("Store card", 235, 22.49), ("Credit card", 105, 87.15),
                                            ("Personal loan", 75, 16.5), ("Car loan", 210, 42.79),
                                            ("Student loan", 180, 64.17)]),
                                ("this:5", [("Store card", 235, 17.18), ("Credit card", 105, 86.78)]))
             for d, paid, i in rows],
    "views": ["Table view **All payments**: sort *Date* descending; footer sum on Paid, Interest and Principal."],
}

DEBT_DEBTS = {
    "key": "debts", "title": "Debts", "icon": "💳",
    "props": [
        ("Name", "title", {}),
        ("Starting balance", "number", {"format": "dollar"}),
        ("APR %", "number", {"format": "number"}),
        ("Minimum", "number", {"format": "dollar"}),
        ("Extra", "number", {"format": "dollar"}),
        ("Principal paid", "formula", {"expr": 'prop("Payments").map(current.prop("Principal")).sum()', "format": "dollar",
                                       "py": lambda r, t: round(sum(x["Principal"] for x in r["Payments"]), 2)}),
        ("Interest paid", "formula", {"expr": 'prop("Payments").map(current.prop("Interest")).sum()', "format": "dollar",
                                      "py": lambda r, t: round(sum(x["Interest"] for x in r["Payments"]), 2)}),
        ("Balance now", "formula", {"expr": f'max({P("Starting balance")} - {P("Principal paid")}, 0)', "format": "dollar",
                                    "py": lambda r, t: round(max(r["Starting balance"] - r["Principal paid"], 0), 2)}),
        ("Monthly payment", "formula", {"expr": f'{P("Minimum")} + {P("Extra")}', "format": "dollar",
                                        "py": lambda r, t: r["Minimum"] + r["Extra"]}),
        ("Months left", "formula", {"expr": _months, "py": _months_py}),
        ("Debt-free", "formula", {"expr": (f'if({P("Months left")} < 0, "Never at this payment", if({P("Months left")} == 0, '
                                            f'"Paid off 🎉", formatDate(dateAdd(now(), {P("Months left")}, "months"), "MMM YYYY")))'),
                                  "py": lambda r, t: ("Never at this payment" if r["Months left"] < 0 else "Paid off 🎉"
                                                      if r["Months left"] == 0 else
                                                      _add_months(t, r["Months left"]).strftime("%b %Y"))}),
        ("Progress", "formula", {"expr": bar_expr(f'{P("Starting balance")} - {P("Balance now")}', P("Starting balance")),
                                 "py": lambda r, t: _bar((r["Starting balance"] - r["Balance now"]) / r["Starting balance"])
                                 if r["Starting balance"] else ""}),
        ("Interest this month", "formula", {"expr": f'round({P("Balance now")} * {_r} * 100) / 100', "format": "dollar",
                                            "py": lambda r, t: round(r["Balance now"] * r["APR %"] / 1200, 2)}),
    ],
    "rows": [{"Name": n, "Starting balance": b, "APR %": a, "Minimum": m, "Extra": e} for n, b, a, m, e in [
        ("Store card", 900, 29.99, 35, 200), ("Credit card", 4200, 24.9, 105, 0), ("Personal loan", 1800, 11, 75, 0),
        ("Car loan", 6500, 7.9, 210, 0), ("Student loan", 14000, 5.5, 180, 0)]],
    "views": [
        "Table view **Avalanche (least interest)**: filter *Balance now* > 0; sort *APR %* descending. "
        "Show Name, Balance now, APR %, Monthly payment, Debt-free, Progress; footer sum on Balance now and Monthly payment.",
        "Table view **Snowball (quick wins)**: same filter; sort *Balance now* ascending.",
        "Gallery view **Paid off 🎉**: filter *Balance now* = 0.",
    ],
}

DEBT = {
    "slug": "notion-debt-payoff", "name": "Notion Debt Payoff Tracker", "icon": "🏔️",
    "dbs": [DEBT_PAYMENTS, DEBT_DEBTS],
    "layout": [
        ("callout", "💡", "List your debts, choose Avalanche (highest APR first, least interest) or Snowball (smallest "
                         "balance first, quick wins), and log each payment. Balances and debt-free dates update."),
        ("h2", "1. Your debts"),
        ("p", "Balance, APR and minimum come from your statement or app. Put all your extra money in Extra on ONE debt: "
              "the top row of your Avalanche or Snowball view."),
        ("db", "debts"),
        ("callout", "🔁", "When a debt says Paid off 🎉, add its whole monthly payment to the next debt's Extra. "
                         "That's the snowball (or avalanche) rolling."),
        ("h2", "2. Log payments"),
        ("p", "One row per payment. Interest is on your statement. Principal (what came off the balance) is worked out."),
        ("db", "payments"),
        ("h2", "Monthly check-in"),
        ("todo", "Every payment this month is logged"),
        ("todo", "Balance now matches your statements (close enough? great)"),
        ("todo", "Extra is on the top debt in your chosen view"),
        ("divider",),
        ("small", "Debt-free dates are estimates: interest is worked out monthly (APR / 12) and each debt is estimated at its own "
                  "payment. Your lender's numbers will differ slightly. Educational organising tool, not financial advice. "
                  "Personal use only. Money Made Simple"),
    ],
}

# ---- Savings ------------------------------------------------------------------------------------------
SAV_DEPOSITS = {
    "key": "deposits", "title": "Deposits", "icon": "🪙",
    "props": [
        ("Name", "title", {}),
        ("Date", "date", {}),
        ("Amount", "number", {"format": "dollar"}),
        ("Goal", "relation", {"db": "goals", "reverse": "Deposits", "single": True}),
    ],
    "rows": [{"Name": "Payday transfer" if amt > 0 else "New tyre (withdrawal)", "Date": when, "Amount": amt, "Goal": g}
             for when in ("last:16", "this:1")
             for g, amt in (("Emergency fund", 250), ("Car repairs", 75), ("Holiday gifts", 60), ("Summer trip", 150),
                            ("New laptop", 100), ("Car insurance (yearly)", 75))] +
            [{"Name": "New tyre (withdrawal)", "Date": "last:22", "Amount": -180, "Goal": "Car repairs"}],
    "views": ["Table view **All deposits**: sort *Date* descending; group by *Goal*; footer sum on Amount."],
}

SAV_GOALS = {
    "key": "goals", "title": "Savings goals", "icon": "🎯",
    "props": [
        ("Name", "title", {}),
        ("Type", "select", {"options": ["Goal", "Sinking fund", "Emergency fund"]}),
        ("Target", "number", {"format": "dollar"}),
        ("Target date", "date", {}),
        ("Starting amount", "number", {"format": "dollar"}),
        ("Saved", "formula", {"expr": f'{P("Starting amount")} + prop("Deposits").map(current.prop("Amount")).sum()',
                              "format": "dollar",
                              "py": lambda r, t: round(r["Starting amount"] + sum(x["Amount"] for x in r["Deposits"]), 2)}),
        ("Left", "formula", {"expr": f'max({P("Target")} - {P("Saved")}, 0)', "format": "dollar",
                             "py": lambda r, t: round(max(r["Target"] - r["Saved"], 0), 2)}),
        ("Progress", "formula", {"expr": bar_expr(P("Saved"), P("Target")),
                                 "py": lambda r, t: _bar(r["Saved"] / r["Target"]) if r["Target"] else ""}),
        ("Months left", "formula", {"expr": f'if(empty({P("Target date")}), 0, max(dateBetween({P("Target date")}, now(), "months"), 1))',
                                    "py": lambda r, t: 0 if not r["Target date"] else max(_months_between(r["Target date"], t), 1)}),
        ("Per month", "formula", {"expr": f'if({P("Months left")} > 0, ceil({P("Left")} / {P("Months left")}), 0)', "format": "dollar",
                                  "py": lambda r, t: math.ceil(r["Left"] / r["Months left"]) if r["Months left"] > 0 else 0}),
        ("Status", "formula", {"expr": (f'if({P("Saved")} >= {P("Target")}, "🎉 Reached", if(empty({P("Target date")}), "Add a date", '
                                        f'if(dateBetween({P("Target date")}, now(), "days") < 0, "📅 Date passed", "🟢 On the way")))'),
                               "py": lambda r, t: ("🎉 Reached" if r["Saved"] >= r["Target"] else "Add a date" if not r["Target date"]
                                                   else "📅 Date passed" if r["Target date"] < t else "🟢 On the way")}),
    ],
    "rows": [{"Name": n, "Type": ty, "Target": tg, "Target date": d, "Starting amount": s} for n, ty, tg, d, s in [
        ("Emergency fund", "Emergency fund", 6000, "+13m", 2300), ("Car repairs", "Sinking fund", 1200, "+7m", 450),
        ("Holiday gifts", "Sinking fund", 600, "+2m", 370), ("Summer trip", "Goal", 2400, "+8m", 300),
        ("New laptop", "Goal", 1100, "+4m", 400), ("Car insurance (yearly)", "Sinking fund", 900, "+10m", 300)]],
    "views": [
        "Gallery view **Goals**: card preview none; show Progress, Saved, Per month, Status.",
        "Table view **Plan**: group by *Type*; footer sum on Target, Saved, Left and Per month "
        "(the Per month total is your monthly savings plan).",
    ],
}

SAVINGS = {
    "slug": "notion-savings-goals", "name": "Notion Savings Goals Tracker", "icon": "🎯",
    "dbs": [SAV_DEPOSITS, SAV_GOALS],
    "layout": [
        ("callout", "💡", "Every goal, sinking fund and your emergency fund in one place, with how much to save each "
                         "month to hit each date."),
        ("h2", "1. What you're saving for"),
        ("p", "Type: Goal (one-off), Sinking fund (a yearly or irregular cost you save for monthly) or Emergency fund."),
        ("db", "goals"),
        ("h2", "2. Log deposits"),
        ("p", "Each transfer to savings is a row. Taking money out? Use a negative amount."),
        ("db", "deposits"),
        ("h2", "Emergency fund, quick maths"),
        ("bullet", "Add up only the essentials: housing, utilities, food, insurance, transport, minimum debt payments."),
        ("bullet", "Many people start with one month of that, then build towards three to six. Set the Target to your number."),
        ("divider",),
        ("small", "Educational organising tool, not financial advice. Personal use only. Money Made Simple"),
    ],
}

# ---- Money HQ (bundle) ---------------------------------------------------------------------------------
_checks = ["Logged spending", "Paid bills due", "Moved money to savings", "Extra debt payment made", "Checked balances"]
CHECKIN = {
    "key": "checkins", "title": "Weekly money check-in", "icon": "✅",
    "props": [("Name", "title", {}), ("Date", "date", {})] + [(c, "checkbox", {}) for c in _checks] + [
        ("Notes", "rich_text", {}),
        ("Score", "formula", {"expr": " + ".join(f'if({P(c)}, 1, 0)' for c in _checks).join(["format(", ")"]) + ' + "/5"',
                              "py": lambda r, t: f"{sum(1 for c in _checks if r[c])}/5"}),
    ],
    "rows": [{"Name": "Week 1", "Date": "last:3", **{c: True for c in _checks}, "Notes": "Fast one. All good."},
             {"Name": "Week 2", "Date": "last:10", **{c: c != "Extra debt payment made" for c in _checks}, "Notes": ""},
             {"Name": "Week 3", "Date": "last:17", **{c: True for c in _checks}, "Notes": "Car repair came from the sinking fund."},
             {"Name": "Week 4", "Date": "last:24", **{c: c in _checks[:3] for c in _checks}, "Notes": ""},
             {"Name": "This week", "Date": "this:1", **{c: c == "Logged spending" for c in _checks}, "Notes": ""}],
    "views": ["Table view **Check-ins**: sort *Date* descending."],
}

HQ = {
    "slug": "notion-money-hq", "name": "Notion Money HQ", "icon": "🏡",
    "dbs": [CHECKIN],
    "children": [BUDGET, DEBT, SAVINGS],
    "layout": [
        ("callout", "🏡", "Your whole money system in one place: budget, debt payoff and savings goals, plus a 10-minute "
                         "weekly check-in. Open each page below to get started."),
        ("h2", "Your money pages"),
        ("children",),
        ("h2", "Weekly check-in (10 minutes, same time every week)"),
        ("p", "New row each week. Tick what you did. Five out of five isn't the point; showing up is."),
        ("db", "checkins"),
        ("h2", "The order that works"),
        ("bullet", "Budget first: know what comes in and goes out."),
        ("bullet", "A small emergency fund next, so a surprise doesn't land on a credit card."),
        ("bullet", "Then your extra money goes to debt (Avalanche or Snowball) and to your goals."),
        ("divider",),
        ("small", "Educational organising tool, not financial advice. Personal use only. Money Made Simple"),
    ],
}

# ---- Free starter (email capture) -------------------------------------------------------------------
STARTER_BUDGET = {
    "key": "starter_budget", "title": "This month's budget", "icon": "💸",
    "props": [
        ("Name", "title", {}),
        ("Group", "select", {"options": ["Income", "Needs", "Wants", "Savings", "Debt"]}),
        ("Budget", "number", {"format": "dollar"}),
        ("Spent", "number", {"format": "dollar"}),
        ("Left", "formula", {"expr": f'{P("Budget")} - {P("Spent")}', "format": "dollar",
                             "py": lambda r, t: round(r["Budget"] - r["Spent"], 2)}),
        ("Used", "formula", {"expr": bar_expr(P("Spent"), P("Budget")),
                             "py": lambda r, t: _bar(r["Spent"] / r["Budget"]) if r["Budget"] else ""}),
    ],
    "rows": [{"Name": n, "Group": g, "Budget": b, "Spent": s} for n, g, b, s in [
        ("Paycheck", "Income", 3800, 1900), ("Rent", "Needs", 1400, 1400), ("Groceries", "Needs", 450, 210.45),
        ("Transport", "Needs", 220, 48), ("Bills", "Needs", 430, 236.4), ("Fun + eating out", "Wants", 280, 70.5),
        ("Savings", "Savings", 250, 0), ("Extra debt payment", "Debt", 200, 0)]],
    "views": ["Table view **Budget**: group by *Group*; footer sum on Budget, Spent and Left. "
              "Each new month: duplicate the page or clear the Spent column."],
}

STARTER_GOAL = {
    "key": "starter_goal", "title": "Savings goal", "icon": "🎯",
    "props": [
        ("Name", "title", {}),
        ("Target", "number", {"format": "dollar"}),
        ("Saved", "number", {"format": "dollar"}),
        ("Progress", "formula", {"expr": bar_expr(P("Saved"), P("Target")),
                                 "py": lambda r, t: _bar(r["Saved"] / r["Target"]) if r["Target"] else ""}),
    ],
    "rows": [{"Name": "Starter emergency fund", "Target": 1000, "Saved": 320}],
    "views": ["Gallery or table, your choice. Update Saved each time you move money."],
}

STARTER = {
    "slug": "notion-money-starter", "name": "Notion Money Starter (free)", "icon": "🌱",
    "dbs": [STARTER_BUDGET, STARTER_GOAL],
    "layout": [
        ("callout", "🌱", "A simple start: one month's budget, one savings goal, and a 10-minute weekly check-in. Free."),
        ("h2", "This month's budget"),
        ("p", "Type what you plan for each category, then update Spent as you go (or once a week)."),
        ("db", "starter_budget"),
        ("h2", "One savings goal"),
        ("p", "Most people start with a small emergency fund. $500 or $1,000 is a great first target."),
        ("db", "starter_goal"),
        ("h2", "Weekly check-in"),
        ("todo", "Update Spent for each category"),
        ("todo", "Pay anything due this week"),
        ("todo", "Move something, even $10, to your savings goal"),
        ("h2", "Want it to do the maths for you?"),
        ("p", "The full templates log every transaction, roll up categories automatically, plan your debt payoff by "
              "Avalanche or Snowball, and track every savings goal with a monthly target."),
        ("link", "See the Money Made Simple templates (code STARTER20 = 20% off)", "store"),
        ("link", "Get the free weekly Money Made Simple email", "newsletter"),
        ("divider",),
        ("small", "Educational organising tool, not financial advice. Free for personal use; please share the link, "
                  "not a copy. Money Made Simple"),
    ],
}


# ---- 2027 editions (dated) --------------------------------------------------------------------------
Y27 = 2027
_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _month_expr(m: int, year: int = Y27) -> str:
    return (f'prop("Transactions").filter(formatDate(current.prop("Date"), "YYYY-MM") == "{year}-{m:02d}")'
            f'.map(current.prop("Amount")).sum()')


def _month_py(m: int, year: int = Y27):
    return lambda r, t: round(sum(x["Amount"] for x in r["Transactions"] if (x["Date"].year, x["Date"].month) == (year, m)), 2)


BUDGET27_CATEGORIES = {
    **BUDGET_CATEGORIES,
    "props": BUDGET_CATEGORIES["props"] + [
        (f"{_MON[m - 1]} {Y27}", "formula", {"expr": _month_expr(m), "format": "dollar", "py": _month_py(m)})
        for m in range(1, 13)] + [
        (f"{Y27} total", "formula", {"expr": " + ".join(P(f"{x} {Y27}") for x in _MON), "format": "dollar",
                                     "py": lambda r, t: round(sum(r[f"{x} {Y27}"] for x in _MON), 2)}),
        (f"{Y27} budget", "formula", {"expr": f'{P("Monthly budget")} * 12', "format": "dollar",
                                      "py": lambda r, t: r["Monthly budget"] * 12}),
    ],
    "views": BUDGET_CATEGORIES["views"] + [
        f"Table view **{Y27} by month**: group by *Group*; show Name, Jan {Y27} ... Dec {Y27}, {Y27} total, {Y27} budget; "
        "footer sum on every month and the totals."],
}

_ex27 = [(1, "Paycheck", "Paycheck", 1900), (1, "Rent", "Rent", 1400), (2, "Grocery run", "Groceries", 112.35),
         (3, "Electric + water", "Utilities", 96.4), (4, "Streaming x2", "Subscriptions", 28.98), (5, "Fuel", "Transport", 48),
         (6, "Tacos with friends", "Eating out", 38.5), (7, "Car + renters insurance", "Insurance", 140),
         (9, "Grocery run", "Groceries", 98.1), (10, "Phone + internet", "Phone + internet", 110),
         (12, "Bus pass", "Transport", 64), (13, "Movie tickets", "Fun", 32), (15, "Paycheck", "Paycheck", 1900),
         (16, "Grocery run", "Groceries", 121.6), (16, "Transfer to savings", "Emergency fund", 250),
         (16, "Gifts + car fund", "Sinking funds", 150), (17, "Extra on credit card", "Extra debt payment", 200),
         (18, "Gas bill", "Utilities", 61.2), (20, "Concert", "Fun", 68), (22, "Freelance logo job", "Side income", 280),
         (23, "Market", "Groceries", 44.8), (8, "Shoes", "Shopping", 74.99)]

BUDGET27_TRANSACTIONS = {
    **BUDGET_TRANSACTIONS,
    "rows": [{"Name": n, "Date": date(Y27, m, d), "Amount": a, "Category": c}
             for m in (1, 2) for d, n, c, a in _ex27 if m == 1 or d <= 17],
}

BUDGET_2027 = {
    **BUDGET,
    "slug": "notion-budget-2027", "name": f"{Y27} Budget", "icon": "📅",
    "dbs": [BUDGET27_TRANSACTIONS, BUDGET27_CATEGORIES],
    "layout": [
        ("callout", "📅", f"Your {Y27} budget. Plan each category, log every transaction, and the {Y27} by month view "
                         f"fills in January to December on its own. Example data covers January and early February {Y27}."),
        *BUDGET["layout"][1:],
    ],
}

_month_checks = ["Budget set", "All logged", "Reviewed"]
MONTHS_2027 = {
    "key": "months27", "title": f"{Y27} month by month", "icon": "🗓️",
    "props": [("Name", "title", {}), ("Month", "date", {})] + [(c, "checkbox", {}) for c in _month_checks] + [
        ("Big win", "rich_text", {}), ("Next month I'll", "rich_text", {}),
        ("Status", "formula", {"expr": (f'if({" and ".join(P(c) for c in _month_checks)}, "✅ Done", '
                                        f'if({P("Budget set")}, "⏳ In progress", "○ Not started"))'),
                               "py": lambda r, t: ("✅ Done" if all(r[c] for c in _month_checks) else
                                                   "⏳ In progress" if r["Budget set"] else "○ Not started")}),
    ],
    "rows": [{"Name": f"{calendar.month_name[m]} {Y27}", "Month": date(Y27, m, 1),
              **{c: (m == 1) or (m == 2 and c == "Budget set") for c in _month_checks},
              "Big win": "Paid the card $200 extra" if m == 1 else "", "Next month I'll": "Cook at home twice more" if m == 1 else ""}
             for m in range(1, 13)],
    "views": [f"Board view **{Y27}**: group by *Status*; or a Calendar view by *Month*. Open a month's page for your "
              "own notes; the checkboxes are the monthly review."],
}

CHECKIN_2027 = {
    **CHECKIN,
    "rows": [{"Name": f"Week {i + 1}", "Date": date(Y27, 1, 1 + 7 * i), **{c: v for c, v in zip(_checks, flags)}, "Notes": note}
             for i, (flags, note) in enumerate([((1, 1, 0, 0, 1), "First week of the year. Set up the budget."),
                                                ((1, 1, 1, 1, 1), ""), ((1, 1, 1, 0, 1), ""),
                                                ((1, 1, 1, 1, 1), "January done: under on groceries.")])],
}

HQ_2027 = {
    "slug": "notion-money-hq-2027", "name": f"{Y27} Money HQ", "icon": "🗓️",
    "dbs": [MONTHS_2027, CHECKIN_2027],
    "children": [BUDGET_2027, DEBT, SAVINGS],
    "layout": [
        ("callout", "🗓️", f"Your {Y27} money year: a dated budget that fills in month by month, debt payoff, savings goals, "
                          "a monthly review for each month and a 10-minute weekly check-in."),
        ("h2", "Your money pages"),
        ("children",),
        ("h2", f"{Y27} month by month"),
        ("p", "At the end of each month: tick the review boxes, write one win and one change. Takes ten minutes."),
        ("db", "months27"),
        ("h2", "Weekly check-in (10 minutes, same time every week)"),
        ("p", "New row each week. Tick what you did. Showing up is the point."),
        ("db", "checkins"),
        ("divider",),
        ("small", "Educational organising tool, not financial advice. Personal use only. Money Made Simple"),
    ],
}

TEMPLATES = {t["slug"]: t for t in (BUDGET, DEBT, SAVINGS, HQ, STARTER, HQ_2027)}


def all_dbs(t: dict) -> list[dict]:
    out = list(t["dbs"])
    for c in t.get("children", []):
        out += all_dbs(c)
    return out


def prop_names(db: dict, template: dict) -> set[str]:
    names = {p[0] for p in db["props"]}
    for other in all_dbs(template):
        for name, kind, cfg in other["props"]:
            if kind == "relation" and cfg["db"] == db["key"]:
                names.add(cfg["reverse"])
    return names


def evaluate(template: dict, today: date) -> dict[str, list[dict]]:
    """Example rows with every formula worked out (Python twins), keyed by database key. For previews/tests."""
    dbs = {d["key"]: d for d in all_dbs(template)}
    rows = {k: [dict(r) for r in d["rows"]] for k, d in dbs.items()}
    for k, d in dbs.items():
        for r in rows[k]:
            for name, kind, cfg in d["props"]:
                if kind == "date":
                    r[name] = resolve_date(r.get(name), today)
                elif kind == "number":
                    r.setdefault(name, 0)
                elif kind == "checkbox":
                    r.setdefault(name, False)
    for k, d in dbs.items():                       # relations, both directions
        for name, kind, cfg in d["props"]:
            if kind != "relation":
                continue
            by_name = {r["Name"]: r for r in rows[cfg["db"]]}
            for r in rows[cfg["db"]]:
                r[cfg["reverse"]] = []
            for r in rows[k]:
                target = by_name[r[name]] if r.get(name) else None
                r[name] = [target] if target else []
                if target:
                    target[cfg["reverse"]].append(r)
    order = [d["key"] for d in dbs.values()]
    for k in order:                                # children first, as listed
        for name, kind, cfg in dbs[k]["props"]:
            if kind == "formula":
                for r in rows[k]:
                    r[name] = cfg["py"](r, today)
    return rows
