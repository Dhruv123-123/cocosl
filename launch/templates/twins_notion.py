"""Notion versions of five Etsy printables: 52-Week Savings Challenge, No-Spend Challenge, Bill Payment Tracker,
Paycheck Budget Planner and Debt Payoff Coloring Tracker.

Same spec format as notion_spec.py (and the same builder, BUILD.md, CSVs and previews). Registers itself in
notion_spec.TEMPLATES when imported; notion_spec imports it at the bottom, so either import order works.
"""
from __future__ import annotations

import math

import notion_spec as N
from notion_spec import P, _bar, bar_expr

FOOT = ("small", "Money Made Simple · Educational organising tool, not financial advice. "
                 "Personal use only; please don't resell or share this template.")
SMALL_COLORS = {"Bill": "red", "Savings": "green", "Extra debt payment": "yellow", "Monthly": "blue",
                "Every 3 months": "purple", "Yearly": "yellow", "Housing": "blue", "Utilities": "purple",
                "Insurance": "green", "Phone + internet": "blue", "Subscriptions": "purple", "Debt": "red", "Other": "default"}
for _k, _v in SMALL_COLORS.items():
    N.GROUP_COLORS.setdefault(_k, _v)


def _sum(rel: str, field: str) -> str:
    return f'prop("{rel}").map(current.prop("{field}")).sum()'


# ---- 52-Week Savings Challenge --------------------------------------------------------------------------
W52_WEEKS = {
    "key": "weeks52", "title": "Weeks", "icon": "📅",
    "props": [
        ("Name", "title", {}),
        ("Week", "number", {"format": "number"}),
        ("Plan", "number", {"format": "dollar"}),
        ("Saved", "number", {"format": "dollar"}),
        ("Challenge", "relation", {"db": "challenge52", "reverse": "Weeks", "single": True}),
        ("Done", "formula", {"expr": f'if({P("Plan")} > 0 and {P("Saved")} >= {P("Plan")}, "✅", if({P("Saved")} > 0, "◐ Part", ""))',
                             "py": lambda r, t: "✅" if r["Plan"] > 0 and r["Saved"] >= r["Plan"] else "◐ Part" if r["Saved"] > 0 else ""}),
    ],
    "rows": [{"Name": f"Week {w}", "Week": w, "Plan": w, "Saved": w if w <= 9 else 0, "Challenge": "My 52-week challenge"}
             for w in range(1, 53)],
    "views": ["Table view **All weeks**: sort *Week* ascending; footer sum on Plan and Saved.",
              "Table view **Still to do**: filter *Done* is not ✅; sort *Week* ascending."],
}
W52_CHALLENGE = {
    "key": "challenge52", "title": "My challenge", "icon": "🎯",
    "props": [
        ("Name", "title", {}),
        ("Goal", "formula", {"expr": _sum("Weeks", "Plan"), "format": "dollar",
                             "py": lambda r, t: sum(x["Plan"] for x in r["Weeks"])}),
        ("Saved so far", "formula", {"expr": _sum("Weeks", "Saved"), "format": "dollar",
                                     "py": lambda r, t: sum(x["Saved"] for x in r["Weeks"])}),
        ("Left", "formula", {"expr": f'max({P("Goal")} - {P("Saved so far")}, 0)', "format": "dollar",
                             "py": lambda r, t: max(r["Goal"] - r["Saved so far"], 0)}),
        ("Weeks done", "formula", {"expr": 'prop("Weeks").filter(current.prop("Plan") > 0 and current.prop("Saved") >= current.prop("Plan")).length()',
                                   "py": lambda r, t: sum(1 for x in r["Weeks"] if x["Plan"] > 0 and x["Saved"] >= x["Plan"])}),
        ("Progress", "formula", {"expr": bar_expr(P("Saved so far"), P("Goal")),
                                 "py": lambda r, t: _bar(r["Saved so far"] / r["Goal"]) if r["Goal"] else ""}),
    ],
    "rows": [{"Name": "My 52-week challenge"}],
    "views": ["Table view **Challenge**: one row; show Goal, Saved so far, Left, Weeks done, Progress."],
}
W52 = {
    "slug": "notion-52-week-savings", "name": "Notion 52-Week Savings Challenge", "icon": "🗓️",
    "dbs": [W52_WEEKS, W52_CHALLENGE],
    "layout": [
        ("callout", "💡", "Save $1 in week 1, $2 in week 2, and so on: $1,378 by week 52. The example has the first 9 weeks done. "
                         "Type over it or clear the Saved column."),
        ("h2", "1. Your challenge"),
        ("p", "Your goal, what you've saved, the weeks you've done and a progress bar. It all fills in from the weeks below."),
        ("db", "challenge52"),
        ("h2", "2. Every week"),
        ("p", "Each week, type what you saved. Saved at least the plan? ✅. Saved part of it? That still counts (◐)."),
        ("db", "weeks52"),
        ("h2", "Other versions"),
        ("p", "Reverse: change each week's Plan to 53 minus the week ($52 first, when motivation is highest). Same every "
              "week: set every Plan to one amount. Your way: type any Plan you like. The goal updates itself."),
        ("todo", "Pick a version and write what you're saving for in the challenge name"),
        ("todo", "Set a weekly reminder on payday"),
        ("todo", "Move the money to savings the same day you tick the week"),
        ("divider",),
        FOOT,
    ],
    "shots": [
        dict(label="page", layout=(0, 3), db="challenge52", cols=["Name", "Goal", "Saved so far", "Left", "Weeks done", "Progress"],
             view="Challenge", after=(4, 6)),
        dict(label="weeks", layout=(4, 6), db="weeks52", cols=["Name", "Plan", "Saved", "Done"], view="All weeks", limit=14,
             sums=("Plan", "Saved"), head=False),
        dict(label="versions", layout=(7, 12), db="challenge52", cols=["Name", "Goal", "Saved so far", "Progress"],
             view="Challenge", head=False, blocks_first=False),
    ],
}

# ---- No-Spend Challenge -------------------------------------------------------------------------------------
_NS_SPENT = {4: (18.5, "Lunch out with work"), 9: (32, "Birthday gift (allowed: planned)")}
NS_DAYS = {
    "key": "nsdays", "title": "Days", "icon": "📆",
    "props": [
        ("Name", "title", {}),
        ("Day", "number", {"format": "number"}),
        ("No-spend", "checkbox", {}),
        ("Spent on extras", "number", {"format": "dollar"}),
        ("Note", "rich_text", {}),
        ("Challenge", "relation", {"db": "nschallenge", "reverse": "Days", "single": True}),
        ("Mark", "formula", {"expr": f'if({P("No-spend")}, "●", if({P("Spent on extras")} > 0, "○", ""))',
                             "py": lambda r, t: "●" if r["No-spend"] else "○" if r["Spent on extras"] > 0 else ""}),
    ],
    "rows": [{"Name": f"Day {d}", "Day": d, "No-spend": d <= 12 and d not in _NS_SPENT,
              "Spent on extras": _NS_SPENT.get(d, (0, ""))[0], "Note": _NS_SPENT.get(d, (0, ""))[1],
              "Challenge": "My 30-day no-spend"} for d in range(1, 31)],
    "views": ["Table view **30 days**: sort *Day* ascending; show Mark, No-spend, Spent on extras, Note.",
              "Gallery view **Circles**: card preview off, show Mark only, card size small (it looks like the printable)."],
}
NS_CHALLENGE = {
    "key": "nschallenge", "title": "My challenge", "icon": "🎯",
    "props": [
        ("Name", "title", {}),
        ("Usual daily extras", "number", {"format": "dollar"}),
        ("Moved to savings", "number", {"format": "dollar"}),
        ("No-spend days", "formula", {"expr": 'prop("Days").filter(current.prop("No-spend")).length()',
                                      "py": lambda r, t: sum(1 for x in r["Days"] if x["No-spend"])}),
        ("Days logged", "formula", {"expr": 'prop("Days").filter(current.prop("No-spend") or current.prop("Spent on extras") > 0).length()',
                                    "py": lambda r, t: sum(1 for x in r["Days"] if x["No-spend"] or x["Spent on extras"] > 0)}),
        ("Spent on extras", "formula", {"expr": _sum("Days", "Spent on extras"), "format": "dollar",
                                        "py": lambda r, t: round(sum(x["Spent on extras"] for x in r["Days"]), 2)}),
        ("Not spent (estimate)", "formula", {"expr": f'{P("No-spend days")} * {P("Usual daily extras")}', "format": "dollar",
                                             "py": lambda r, t: r["No-spend days"] * r["Usual daily extras"]}),
        ("Progress", "formula", {"expr": bar_expr(P("No-spend days"), 'prop("Days").length()'),
                                 "py": lambda r, t: _bar(r["No-spend days"] / len(r["Days"])) if r["Days"] else ""}),
    ],
    "rows": [{"Name": "My 30-day no-spend", "Usual daily extras": 15, "Moved to savings": 120}],
    "views": ["Table view **Challenge**: one row; show every property."],
}
NS = {
    "slug": "notion-no-spend-challenge", "name": "Notion No-Spend Challenge", "icon": "🛑",
    "dbs": [NS_DAYS, NS_CHALLENGE],
    "layout": [
        ("callout", "💡", "Thirty days of noticing your spending. Essentials are always allowed: it's a challenge, not a punishment. "
                         "The example is 12 days in."),
        ("h2", "1. Your rules"),
        ("todo", "Always allowed: rent, bills, groceries, fuel, medicine, anything already planned"),
        ("todo", "Not allowed: takeout, coffee out, online shopping, impulse buys (edit this list to fit you)"),
        ("todo", "Free things to do instead: library, a walk, a movie night at home, call a friend"),
        ("h2", "2. Your challenge"),
        ("p", "Set what you usually spend on extras in a day. The template estimates what you didn't spend."),
        ("db", "nschallenge"),
        ("h2", "3. Every day"),
        ("p", "Tick No-spend, or type what you spent on extras and a note. Slipped? Write it down and keep going."),
        ("db", "nsdays"),
        ("h2", "At the end"),
        ("todo", "Move what you didn't spend to savings or a debt, and type it in Moved to savings"),
        ("todo", "Which day was hardest, and why? Plan for it next month"),
        ("divider",),
        FOOT,
    ],
    "shots": [
        dict(label="page", layout=(0, 8), db="nschallenge", cols=["Name", "No-spend days", "Days logged", "Not spent (estimate)",
                                                                  "Progress"], view="Challenge"),
        dict(label="days", layout=(9, 11), db="nsdays", cols=["Name", "Mark", "No-spend", "Spent on extras", "Note"],
             view="30 days", limit=14, sums=("Spent on extras",), head=False),
        dict(label="end", layout=(12, 15), db="nschallenge", cols=["Name", "Spent on extras", "Moved to savings", "Progress"],
             view="Challenge", head=False, blocks_first=False),
    ],
}

# ---- Bill Payment Tracker -----------------------------------------------------------------------------------
_FREQ = f'if({P("How often")} == "Yearly", 12, if({P("How often")} == "Every 3 months", 3, 1))'
_PAID = ('if(prop("Payments").filter(formatDate(current.prop("Date"), "YYYY-MM") == formatDate(now(), "YYYY-MM")).length() > 0, '
         '"✓", "")')


def _paid_py(r, t):
    return "✓" if any((x["Date"].year, x["Date"].month) == (t.year, t.month) for x in r["Payments"]) else ""


def _status_py(r, t):
    if r["How often"] != "Monthly":
        return "📅 Set aside"
    if r["Paid this month"]:
        return "✅ Paid"
    if r["Due day"] < t.day:
        return "🔴 Past due?"
    return "🟠 Due soon" if r["Due day"] - t.day <= 3 else "⏳ Upcoming"


BILL_PAYMENTS = {
    "key": "billpayments", "title": "Payments", "icon": "🧾",
    "props": [
        ("Name", "title", {}),
        ("Date", "date", {}),
        ("Amount", "number", {"format": "dollar"}),
        ("Bill", "relation", {"db": "bills", "reverse": "Payments", "single": True}),
    ],
    "rows": [{"Name": f"{b} {lab}", "Date": f"{when}:{d}", "Amount": a, "Bill": b}
             for when, lab, items in (("last", "(last month)", [("Rent", 1, 1400), ("Car insurance", 5, 140), ("Electric", 12, 88.4),
                                                                ("Water", 18, 41.2), ("Phone + internet", 20, 110),
                                                                ("Streaming", 22, 15.99), ("Credit card minimum", 25, 105)]),
                                      ("this", "", [("Rent", 1, 1400), ("Car insurance", 3, 140)]))
             for b, d, a in items],
    "views": ["Table view **All payments**: sort *Date* descending; footer sum on Amount.",
              "Table view **This month**: filter *Date* is relative to today > *This month*."],
}
BILLS = {
    "key": "bills", "title": "Bills", "icon": "📌",
    "props": [
        ("Name", "title", {}),
        ("Category", "select", {"options": ["Housing", "Utilities", "Insurance", "Phone + internet", "Subscriptions", "Debt", "Other"]}),
        ("Amount", "number", {"format": "dollar"}),
        ("Due day", "number", {"format": "number"}),
        ("How often", "select", {"options": ["Monthly", "Every 3 months", "Yearly"]}),
        ("Autopay", "checkbox", {}),
        ("Set aside / month", "formula", {"expr": f'round({P("Amount")} / {_FREQ} * 100) / 100', "format": "dollar",
                                          "py": lambda r, t: round(r["Amount"] / {"Yearly": 12, "Every 3 months": 3}.get(r["How often"], 1), 2)}),
        ("Paid this month", "formula", {"expr": _PAID, "py": _paid_py}),
        ("Status", "formula", {"expr": (f'if({P("How often")} != "Monthly", "📅 Set aside", if({P("Paid this month")} == "✓", "✅ Paid", '
                                        f'if({P("Due day")} < date(now()), "🔴 Past due?", if({P("Due day")} - date(now()) <= 3, '
                                        f'"🟠 Due soon", "⏳ Upcoming"))))'), "py": _status_py}),
    ],
    "rows": [{"Name": n, "Category": c, "Amount": a, "Due day": d, "How often": f, "Autopay": ap} for n, c, a, d, f, ap in [
        ("Rent", "Housing", 1400, 1, "Monthly", False), ("Car insurance", "Insurance", 140, 3, "Monthly", True),
        ("Electric", "Utilities", 95, 12, "Monthly", False), ("Water", "Utilities", 45, 18, "Monthly", False),
        ("Phone + internet", "Phone + internet", 110, 20, "Monthly", True), ("Streaming", "Subscriptions", 15.99, 22, "Monthly", True),
        ("Credit card minimum", "Debt", 105, 25, "Monthly", False), ("Car registration", "Other", 180, 15, "Yearly", False),
        ("Renters insurance", "Insurance", 180, 9, "Yearly", True), ("Trash pickup", "Utilities", 66, 10, "Every 3 months", False)]],
    "views": ["Table view **This month**: filter *How often* is Monthly; sort *Due day* ascending; footer sum on Amount.",
              "Table view **Yearly + quarterly**: filter *How often* is not Monthly; footer sum on Set aside / month.",
              "Board view **Status**: group by *Status*."],
}
BILL = {
    "slug": "notion-bill-tracker", "name": "Notion Bill Payment Tracker", "icon": "📌",
    "dbs": [BILL_PAYMENTS, BILLS],
    "layout": [
        ("callout", "💡", "Every bill in one list, sorted by due day, with a status that tells you what's paid, what's due soon "
                         "and what to set aside for the yearly ones. Example data is filled in."),
        ("h2", "1. Your bills"),
        ("p", "One row per bill: amount, due day (1 to 31), how often and whether it's on autopay. Yearly and every-3-months "
              "bills show what to set aside each month so they're never a surprise."),
        ("db", "bills"),
        ("h2", "2. Log each payment"),
        ("p", "Paid a bill? New row: date, amount, pick the bill. Its status turns ✅ for this month."),
        ("db", "billpayments"),
        ("h2", "3. Once a month (5 minutes)"),
        ("todo", "Anything 🔴 or 🟠? Pay it or call to move the date"),
        ("todo", "Move the total of Set aside / month to a savings account for the yearly bills"),
        ("todo", "Any bill that went up? Note it, and see if it can be lowered"),
        ("divider",),
        FOOT,
    ],
    "shots": [
        dict(label="page", layout=(0, 3), db="bills", cols=["Name", "Amount", "Due day", "How often", "Autopay", "Status"],
             view="All bills", sort="Due day", limit=10, sums=("Amount",)),
        dict(label="set-aside", layout=(7, 11), db="bills", cols=["Name", "Category", "Amount", "How often", "Set aside / month"],
             view="By category", group="Category", limit=12, sums=("Set aside / month",), head=False, blocks_first=False),
        dict(label="payments", layout=(4, 6), db="billpayments", cols=["Name", "Date", "Amount", "Bill"], view="All payments",
             sort="-Date", limit=10, sums=("Amount",), head=False),
    ],
}

# ---- Paycheck Budget Planner --------------------------------------------------------------------------------
_LINES = [  # (paycheck, line, amount, type, due day)
    ("Paycheck 1", "Rent", 1400, "Bill", 1), ("Paycheck 1", "Car insurance", 140, "Bill", 3),
    ("Paycheck 1", "Emergency fund", 50, "Savings", None),
    ("Paycheck 2", "Electric", 95, "Bill", 18), ("Paycheck 2", "Phone + internet", 110, "Bill", 20),
    ("Paycheck 2", "Credit card minimum", 105, "Bill", 25), ("Paycheck 2", "Emergency fund", 150, "Savings", None),
    ("Paycheck 2", "Extra on credit card", 100, "Extra debt payment", None),
    ("Paycheck 3", "Rent", 1400, "Bill", 1), ("Paycheck 3", "Car insurance", 140, "Bill", 3),
    ("Paycheck 3", "Emergency fund", 50, "Savings", None),
    ("Paycheck 4", "Electric", 95, "Bill", 18), ("Paycheck 4", "Phone + internet", 110, "Bill", 20),
    ("Paycheck 4", "Credit card minimum", 105, "Bill", 25), ("Paycheck 4", "Holiday fund", 100, "Savings", None)]
PAY_LINES = {
    "key": "paylines", "title": "Plan lines", "icon": "🧩",
    "props": [
        ("Name", "title", {}),
        ("Amount", "number", {"format": "dollar"}),
        ("Type", "select", {"options": ["Bill", "Savings", "Extra debt payment"]}),
        ("Due day", "number", {"format": "number"}),
        ("Paycheck", "relation", {"db": "paychecks", "reverse": "Lines", "single": True}),
    ],
    "rows": [{"Name": f"{n} ({p[-1]})", "Amount": a, "Type": ty, "Due day": d or 0, "Paycheck": p} for p, n, a, ty, d in _LINES],
    "views": ["Table view **By paycheck**: group by *Paycheck*; sort *Due day* ascending; footer sum on Amount."],
}


def _type_sum(r, bill: bool) -> float:
    return round(sum(x["Amount"] for x in r["Lines"] if (x["Type"] == "Bill") == bill), 2)


PAYCHECKS = {
    "key": "paychecks", "title": "Paychecks", "icon": "💵",
    "props": [
        ("Name", "title", {}),
        ("Pay date", "date", {}),
        ("Received", "number", {"format": "dollar"}),
        ("Bills", "formula", {"expr": 'prop("Lines").filter(current.prop("Type") == "Bill").map(current.prop("Amount")).sum()',
                              "format": "dollar", "py": lambda r, t: _type_sum(r, True)}),
        ("Savings + debt", "formula", {"expr": 'prop("Lines").filter(current.prop("Type") != "Bill").map(current.prop("Amount")).sum()',
                                       "format": "dollar", "py": lambda r, t: _type_sum(r, False)}),
        ("Spending money", "formula", {"expr": f'{P("Received")} - {P("Bills")} - {P("Savings + debt")}', "format": "dollar",
                                       "py": lambda r, t: round(r["Received"] - r["Bills"] - r["Savings + debt"], 2)}),
        ("Status", "formula", {"expr": f'if({P("Received")} == 0, "⏳ Not paid yet", if({P("Spending money")} < 0, "🔴 Short", "🟢 Every dollar has a job"))',
                               "py": lambda r, t: "⏳ Not paid yet" if r["Received"] == 0 else "🔴 Short" if r["Spending money"] < 0
                               else "🟢 Every dollar has a job"}),
    ],
    "rows": [{"Name": n, "Pay date": d, "Received": a} for n, d, a in [
        ("Paycheck 1", "last:1", 1900), ("Paycheck 2", "last:15", 1900), ("Paycheck 3", "this:1", 1900), ("Paycheck 4", "this:15", 0)]],
    "views": ["Table view **Paychecks**: sort *Pay date* ascending; footer sum on Received, Bills and Spending money."],
}
PAY = {
    "slug": "notion-paycheck-budget", "name": "Notion Paycheck Budget Planner", "icon": "💵",
    "dbs": [PAY_LINES, PAYCHECKS],
    "layout": [
        ("callout", "💡", "Budget each paycheck instead of each month. Every check gets a job: the bills due before the next "
                         "payday, then savings, then spending money. Example: paid on the 1st and the 15th."),
        ("h2", "1. Your paychecks"),
        ("p", "One row per payday. Type what you actually received. Spending money is what's left after the plan."),
        ("db", "paychecks"),
        ("h2", "2. Give each paycheck its jobs"),
        ("p", "Add a line for each bill due before the next payday, then savings and any extra debt payment, and pick the "
              "paycheck. Tip: duplicate last month's lines and change the paycheck."),
        ("db", "paylines"),
        ("h2", "3. Every payday (5 minutes)"),
        ("todo", "Type what you received"),
        ("todo", "Pay the bills on this paycheck's list"),
        ("todo", "Move the savings lines on payday, before spending"),
        ("todo", "Spending money ÷ days until next payday = your daily number"),
        ("divider",),
        FOOT,
    ],
    "shots": [
        dict(label="page", layout=(0, 3), db="paychecks", cols=["Name", "Pay date", "Received", "Bills", "Savings + debt",
                                                                "Spending money", "Status"], view="Paychecks",
             sort="Pay date", sums=("Received", "Bills", "Spending money")),
        dict(label="lines", layout=(4, 6), db="paylines", cols=["Name", "Amount", "Type", "Due day", "Paycheck"],
             view="By paycheck", limit=12, sums=("Amount",), head=False),
        dict(label="payday", layout=(7, 13), db="paychecks", cols=["Name", "Received", "Spending money", "Status"],
             view="Paychecks", sort="Pay date", head=False, blocks_first=False),
    ],
}

# ---- Debt Payoff Coloring Tracker ---------------------------------------------------------------------------
_PCT = f'({P("Paid off")} / {P("Started with")})'


def _squares_expr(paid: str, start: str, n: int = 20) -> str:
    k = f"min(max(floor(({paid}) / ({start}) * {n}), 0), {n})"
    return f'if({start} > 0, repeat("🟩", {k}) + repeat("⬜", {n} - {k}), "")'


def _squares_py(paid: float, start: float, n: int = 20) -> str:
    if start <= 0:
        return ""
    k = min(max(math.floor(paid / start * n), 0), n)
    return "🟩" * k + "⬜" * (n - k)


def _next_py(r, t):
    if r["Started with"] <= 0:
        return ""
    pct = r["Paid off"] / r["Started with"]
    if pct >= 1:
        return "🎉 Debt-free!"
    nxt = 25 if pct < .25 else 50 if pct < .5 else 75 if pct < .75 else 100
    return f"Next: {nxt}% (${math.ceil(r['Started with'] * nxt / 100 - r['Paid off'])} to go)"


DC_DEBTS = {
    "key": "cdebts", "title": "Debts", "icon": "💳",
    "props": [
        ("Name", "title", {}),
        ("Starting balance", "number", {"format": "dollar"}),
        ("Balance now", "number", {"format": "dollar"}),
        ("APR %", "number", {"format": "number"}),
        ("My debt", "relation", {"db": "mydebt", "reverse": "Debts", "single": True}),
        ("Paid off", "formula", {"expr": f'max({P("Starting balance")} - {P("Balance now")}, 0)', "format": "dollar",
                                 "py": lambda r, t: round(max(r["Starting balance"] - r["Balance now"], 0), 2)}),
        ("Progress", "formula", {"expr": bar_expr(P("Paid off"), P("Starting balance")),
                                 "py": lambda r, t: _bar(r["Paid off"] / r["Starting balance"]) if r["Starting balance"] else ""}),
        ("Colored in", "formula", {"expr": _squares_expr(P("Paid off"), P("Starting balance")),
                                   "py": lambda r, t: _squares_py(r["Paid off"], r["Starting balance"])}),
    ],
    "rows": [{"Name": n, "Starting balance": s, "Balance now": b, "APR %": a, "My debt": "All my debt"} for n, s, b, a in [
        ("Store card", 900, 0, 29.99), ("Credit card", 4200, 3310, 24.9), ("Personal loan", 1800, 1420, 11),
        ("Car loan", 6500, 5890, 7.9)]],
    "views": ["Table view **Debts**: sort *Balance now* ascending (snowball) or *APR %* descending (avalanche).",
              "Gallery view **Color in**: show Colored in and Progress on the cards."],
}
DC_TOTAL = {
    "key": "mydebt", "title": "All my debt", "icon": "🏔️",
    "props": [
        ("Name", "title", {}),
        ("25% reward", "rich_text", {}),
        ("50% reward", "rich_text", {}),
        ("75% reward", "rich_text", {}),
        ("Debt-free reward", "rich_text", {}),
        ("Started with", "formula", {"expr": _sum("Debts", "Starting balance"), "format": "dollar",
                                     "py": lambda r, t: sum(x["Starting balance"] for x in r["Debts"])}),
        ("Owe now", "formula", {"expr": _sum("Debts", "Balance now"), "format": "dollar",
                                "py": lambda r, t: sum(x["Balance now"] for x in r["Debts"])}),
        ("Paid off", "formula", {"expr": f'max({P("Started with")} - {P("Owe now")}, 0)', "format": "dollar",
                                 "py": lambda r, t: max(r["Started with"] - r["Owe now"], 0)}),
        ("Colored in", "formula", {"expr": _squares_expr(P("Paid off"), P("Started with")),
                                   "py": lambda r, t: _squares_py(r["Paid off"], r["Started with"])}),
        ("Progress", "formula", {"expr": bar_expr(P("Paid off"), P("Started with")),
                                 "py": lambda r, t: _bar(r["Paid off"] / r["Started with"]) if r["Started with"] else ""}),
        ("Next milestone", "formula", {"expr": (f'if({P("Started with")} <= 0, "", if({_PCT} >= 1, "🎉 Debt-free!", "Next: " + '
                                                f'format(if({_PCT} < 0.25, 25, if({_PCT} < 0.5, 50, if({_PCT} < 0.75, 75, 100)))) + "% ($" + '
                                                f'format(ceil({P("Started with")} * if({_PCT} < 0.25, 25, if({_PCT} < 0.5, 50, if({_PCT} < 0.75, 75, 100))) / 100 - '
                                                f'{P("Paid off")})) + " to go)"))'),
                                       "py": _next_py}),
    ],
    "rows": [{"Name": "All my debt", "25% reward": "Pizza night at home", "50% reward": "A day trip",
              "75% reward": "New running shoes", "Debt-free reward": "A weekend away (paid in cash)"}],
    "views": ["Table view **Total**: one row; show Colored in, Progress, Next milestone and the rewards."],
}
DC = {
    "slug": "notion-debt-coloring", "name": "Notion Debt Payoff Coloring Tracker", "icon": "🟩",
    "dbs": [DC_DEBTS, DC_TOTAL],
    "layout": [
        ("callout", "💡", "Make paying off debt visible. Each 🟩 is 5% of the balance paid off. Update Balance now once a month "
                         "from your statements and watch the squares fill in."),
        ("h2", "1. All my debt"),
        ("p", "Your total, the squares colored in, and the next milestone with its reward. Pick rewards that don't cost much."),
        ("db", "mydebt"),
        ("h2", "2. Each debt"),
        ("p", "Starting balance once; Balance now every month. The squares and the progress bar update themselves."),
        ("db", "cdebts"),
        ("h2", "3. Once a month (5 minutes)"),
        ("todo", "Copy each balance from the statement into Balance now"),
        ("todo", "Hit a milestone? Take the reward. You earned it"),
        ("todo", "Snowball (smallest first) or avalanche (highest APR first)? Sort the Debts table to see your next target"),
        ("divider",),
        FOOT,
    ],
    "shots": [
        dict(label="page", layout=(0, 3), db="mydebt", cols=["Name", "Started with", "Owe now", "Progress", "Next milestone"],
             view="Total"),
        dict(label="debts", layout=(4, 6), db="cdebts", cols=["Name", "Balance now", "APR %", "Colored in", "Progress"],
             view="Debts", sort="Balance now", sums=("Balance now",), head=False),
        dict(label="rewards", layout=(7, 11), db="mydebt", cols=["Name", "Colored in", "25% reward", "50% reward", "Debt-free reward"],
             view="Total", head=False, blocks_first=False),
    ],
}

TWINS = [W52, NS, BILL, PAY, DC]
N.TEMPLATES.update({t["slug"]: t for t in TWINS})
