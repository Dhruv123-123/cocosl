"""The Money Reset: a 30-Day Challenge workbook for Money Made Simple ($9, printable, Letter + A4).

One task a day, about 15 minutes, in four themed weeks plus two wrap-up days: see where the money goes, cut and
lower, plan it, then debt and the future. 21 pages: start, starting snapshot, a progress tracker, nine day pages (three or four
days each), six worksheets, weekly reviews, and an ending snapshot with your money rules.

Different from the free 7-Day Money Reset lead magnet (launch/archive/, retired) and the No-Spend Challenge printable:
this is a guided month of tasks, not a tracker. Built and checked by build_brandshop.py like the other brand products.
"""
from __future__ import annotations

from shop import Brand, etsy_description

BRAND = Brand("Money Made Simple", "moneymadesimple", ink="#0b1d13", cream="#f4f1e8", accent="#2fbf71", accent_d="#1e8a50",
              warm="#f2b134", tint="#eef8f2", muted="#5b6a61", line="#c9c3b3")
P = BRAND.page
KICK = "The Money Reset"

# (day, title, do this, why, worksheet page or "")
WEEKS = [
    ("Week 1", "See where it goes", [
        (1, "Find every account", "Log in to each bank, card, loan and savings account. Write each balance on the Accounts worksheet.",
         "You can't plan money you can't see. Most people find at least one account they'd forgotten.", "Accounts"),
        (2, "List every bill", "Write each bill, its amount and due day on the Bills worksheet. Use last month's statements.",
         "Late fees come from bills you didn't know were due, not from bills you can't pay.", "Bills and subscriptions"),
        (3, "Hunt the repeat charges", "Go through two months of statements, plus app stores and PayPal. List every charge that repeats.",
         "Small repeat charges are the easiest money in this whole month.", "Bills and subscriptions"),
        (4, "Add up last month", "Total last month's spending by category on the Spending worksheet. Rough is fine.",
         "You're looking for the two or three categories that are bigger than you thought.", "Spending"),
        (5, "Name three leaks", "Pick three small, frequent spends (coffee, delivery fees, impulse buys). Write what each costs a month.",
         "Leaks are rarely one big thing. Three small ones can add up to a car payment.", "Spending"),
        (6, "Check your credit reports", "Get your free reports at AnnualCreditReport.com (free every week from all three bureaus). Note anything wrong.",
         "Errors happen, and disputing one is free. You don't need to pay anyone to do it.", ""),
        (7, "Week 1 review", "Fill in the Week 1 review. Total what you found.", "Seeing it all is the hard part. It's done.", "Reviews"),
    ]),
    ("Week 2", "Cut and lower", [
        (8, "Cancel what you don't use", "Cancel at least one repeat charge from Day 3. Write it in the Calls and savings log.",
         "Every cancellation is a raise you give yourself every month.", "Calls and savings"),
        (9, "Ask for a lower bill", "Call your phone or internet company. Say: \"I'm reviewing my bills. What's the lowest price you can offer to keep me?\"",
         "Companies often have offers they don't advertise. The worst answer is no.", "Calls and savings"),
        (10, "Get one insurance quote", "Get a quote for car or renters insurance with the same coverage. Compare it with what you pay.",
         "Prices drift up at renewal. One quote tells you if yours has.", "Calls and savings"),
        (11, "Plan a week of meals", "Plan five dinners and write one grocery list from them. Shop once.",
         "Groceries and eating out are usually the biggest flexible spend.", ""),
        (12, "Set a 48-hour rule", "For anything you want that isn't essential, wait 48 hours. Unsubscribe from three store emails today.",
         "Most impulse buys don't survive two days.", ""),
        (13, "Sell or return one thing", "Return something unused or list one thing you don't need for sale.", "Money back in, clutter out.", ""),
        (14, "Week 2 review", "Fill in the Week 2 review. Add up the monthly savings you found.", "That number is your first raise this month.", "Reviews"),
    ]),
    ("Week 3", "Plan it", [
        (15, "Know your take-home pay", "Write what actually lands in your account each month (not your salary).", "Plans built on gross pay fail.", "Budget"),
        (16, "Build a one-page budget", "On the Budget worksheet: bills, savings, debt payments. What's left is spending money.",
         "One page you'll use beats a perfect budget you won't.", "Budget"),
        (17, "Find your weekly number", "Divide spending money by the weeks in the month. That's your weekly number.",
         "One number to watch is easier than twelve categories.", "Budget"),
        (18, "Plan the irregular costs", "List costs that don't come every month (car repairs, gifts, renewals). Divide each by 12.",
         "These are the costs that wreck budgets. Now they're planned.", "Budget"),
        (19, "Start an emergency fund", "Pick a first goal ($500, or one month of essentials). Open or rename a savings account for it.",
         "A small cushion turns an emergency into an inconvenience.", ""),
        (20, "Put it on autopilot", "Schedule a transfer to savings for each payday, even a small one.", "What happens automatically happens.", ""),
        (21, "Week 3 review", "Fill in the Week 3 review.", "You have a plan now. Next week makes it go further.", "Reviews"),
    ]),
    ("Week 4", "Debt and the future", [
        (22, "List your debts", "On the Debts worksheet: balance, interest rate (APR) and minimum for each.", "Debt is less scary on paper than in your head.", "Debts"),
        (23, "Pick a method", "Avalanche: extra money to the highest APR first (least interest). Snowball: smallest balance first (quick wins). Pick one.",
         "Both work. The best one is the one you'll stick to.", "Debts"),
        (24, "Schedule the extra payment", "Choose an extra amount for your target debt and schedule it. Keep every other minimum paid.",
         "The extra payment is what moves your debt-free date.", "Debts"),
        (25, "Check for free money", "If your employer has a retirement plan, find out whether it matches and what you'd need to put in to get all of it.",
         "A match is part of your pay. Ask HR or check the plan's website.", ""),
        (26, "Set one 12-month goal", "Write one money goal for the next year, with a number and a date.", "A goal with a date gets a plan.", ""),
        (27, "Make a money calendar", "Pick your weekly check-in day and your monthly reset date. Put both in your phone.",
         "The habit keeps the plan alive after this month.", ""),
        (28, "Week 4 review", "Fill in the Week 4 review.", "Four weeks done.", "Reviews"),
    ]),
    ("Days 29 and 30", "Lock it in", [
        (29, "Your ending snapshot", "Fill in the ending snapshot and compare it with Day 1.", "Look at what changed in a month.", "Ending"),
        (30, "Write your money rules", "Write five rules you'll keep, and the first three things you'll do next month.", "Rules make the next month easy.", "Ending"),
    ]),
]
DAYS = [d for _, _, ds in WEEKS for d in ds]


def _box(label: str, h: int = 26, tint: bool = False) -> str:
    bg = "background:var(--tint);" if tint else ""
    return f'<div class="box" style="{bg}"><div class="lbl">{label}</div><div style="height:{h}px"></div></div>'


def _tbl(headers: list[tuple[str, str]], n: int, total: str | None = None) -> str:
    head = "".join(f'<th style="width:{w}">{h}</th>' if w else f"<th>{h}</th>" for h, w in headers)
    body = "".join("<tr>" + "<td></td>" * len(headers) + "</tr>" for _ in range(n))
    tot = (f'<tr class="tot"><td>{total}</td>' + "<td></td>" * (len(headers) - 1) + "</tr>") if total else ""
    return f'<table><tr>{head}</tr>{body}{tot}</table>'


CSS = """
.day{ border:1.5px solid var(--ink); border-radius:12px; padding:9px 12px; margin-bottom:10px; display:flex; flex-direction:column; flex:1; }
.day .hd{ display:flex; align-items:center; gap:10px; }
.day .n{ background:var(--ink); color:var(--cream); font-weight:900; border-radius:8px; padding:3px 9px; font-size:11pt; }
.day .t{ font-weight:900; font-size:13pt; flex:1; }
.day .ck{ width:20px; height:20px; border:2px solid var(--ink); border-radius:5px; }
.day .do{ font-size:10.5pt; margin:6px 0 2px; }
.day .why{ font-size:9pt; color:var(--muted); font-style:italic; }
.day .ws{ font-size:8pt; font-weight:800; color:var(--green-d); text-transform:uppercase; letter-spacing:.08em; }
.track{ display:grid; grid-template-columns:repeat(6,1fr); gap:10px; }
.track div{ aspect-ratio:1; border:2px solid var(--ink); border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:13pt; }
"""


def start_page() -> str:
    weeks = "".join(f"<li><strong>{w}: {t}.</strong> Days {ds[0][0]} to {ds[-1][0]}.</li>" for w, t, ds in WEEKS[:-1])
    weeks += "<li><strong>Days 29 and 30: lock it in.</strong> Your ending snapshot and your money rules.</li>"
    return P("The Money <em>Reset</em>", "30-Day Challenge", f'''
      <p class="big">One small task a day for 30 days, about 15 minutes each. By the end you'll know where your money
      goes, you'll have cut what you don't need, and you'll have a simple plan for spending, saving and debt.</p>
      <h3>How it works</h3>
      <ol class="steps big">
        <li>Fill in the starting snapshot today. It's your "before".</li>
        <li>Do one day's task each day, in order. Tick the box and color in the day on the tracker.</li>
        <li>The worksheets are where the numbers go. Each day says which one it uses.</li>
        <li>Missed a day? Do it tomorrow. It's 30 tasks, not 30 days in a row.</li>
      </ol>
      <h3>The four weeks</h3><ul style="font-size:10.5pt;padding-left:20px">{weeks}</ul>
      <h3>Printing</h3>
      <p style="font-size:10pt">Letter in the US and Canada, A4 elsewhere, at 100% / actual size. Or write on it in any
      PDF app on a tablet.</p>
      <div style="margin-top:auto" class="box fineprint">An educational workbook, not financial, tax, legal or investment
      advice. Nobody can promise results: what you save depends on your bills and choices. US-focused where accounts
      or services are mentioned. Made by Money Made Simple with the help of AI tools for drafting and layout, and
      checked by a person.</div>''', kicker="Money Made Simple")


def snapshot_page(title: str, kick: str, end: bool = False) -> str:
    extra = ('<div class="g2" style="margin-top:8px">' + _box("What changed most?", 60) + _box("What I'm proudest of", 60) + "</div>"
             if end else '<div class="g2" style="margin-top:8px">' + _box("Why I'm doing this", 60) + _box("What I want to be different in 30 days", 60) + "</div>")
    return P(title, kick, f'''
      <div class="g4" style="margin-bottom:10px">{_box("Date")}{_box("Cash + savings")}{_box("Total debt")}{_box("Monthly take-home")}</div>
      <div class="g4" style="margin-bottom:10px">{_box("Monthly bills")}{_box("Saved each month")}{_box("Emergency fund")}{_box("Money stress, 1 to 10", tint=True)}</div>
      <h3>Accounts at a glance</h3>{_tbl([("Account", "40%"), ("Type", ""), ("Balance", "")], 8)}
      {extra}
      <h3>Notes</h3><div class="lines"></div>''', kicker=KICK)


def tracker_page() -> str:
    cells = "".join(f"<div>{d}</div>" for d in range(1, 31))
    return P("30-day <em>tracker</em>", "Color in each day you finish", f'''
      <p class="big">Color a circle when you finish that day's task. Missed one? Leave it, do it tomorrow, then color it.</p>
      <div class="track" style="margin:10px 0 16px">{cells}</div>
      <div class="g3">{_box("Monthly savings found (Week 2)", 30)}{_box("Emergency fund goal (Day 19)", 30)}{_box("Debt-free target (Day 23)", 30)}</div>
      <h3>Notes</h3><div class="lines"></div>''', kicker=KICK)


def day_card(d: tuple) -> str:
    n, title, do, why, ws = d
    tag = f'<div class="ws">Worksheet: {ws}</div>' if ws else ""
    return (f'<div class="day"><div class="hd"><span class="n">Day {n}</span><span class="t">{title}</span><span class="ck"></span></div>'
            f'<div class="do">{do}</div><div class="why">{why}</div>{tag}<h3 style="margin:6px 0 2px">Notes</h3>'
            f'<div class="lines"></div></div>')


def day_pages() -> list[str]:
    out = []
    for w, theme, ds in WEEKS:
        for chunk in ([ds[:4], ds[4:]] if len(ds) > 4 else [ds]):
            out.append(P(f"{w}: <em>{theme}</em>", f"Days {chunk[0][0]} to {chunk[-1][0]}" if len(chunk) > 1 else f"Day {chunk[0][0]}",
                         "".join(day_card(d) for d in chunk), kicker=KICK))
    return out


def worksheets() -> list[str]:
    return [
        P("Accounts", "Day 1", f'''{_tbl([("Account", "30%"), ("Bank or lender", ""), ("Type", ""), ("Balance", ""), ("Login checked", "13%")], 16, "Total")}
          <div class="g2" style="margin-top:10px">{_box("Accounts I'd forgotten", 50)}{_box("Accounts to close or combine", 50)}</div>''', kicker=KICK),
        P("Bills and <em>subscriptions</em>", "Days 2 and 3", f'''
          <h3>Bills</h3>{_tbl([("Bill", "36%"), ("Amount", ""), ("Due day", ""), ("Autopay?", ""), ("Monthly", "")], 11, "Total")}
          <h3>Repeat charges</h3>{_tbl([("Charge", "36%"), ("Amount", ""), ("How often", ""), ("Per year", ""), ("Keep / cancel / lower", "")], 10, "Total")}''',
          kicker=KICK),
        P("Spending", "Days 4 and 5", f'''{_tbl([("Category", "34%"), ("Last month", ""), ("Surprised?", ""), ("Next month's limit", "")], 14, "Total")}
          <h3>Three leaks</h3>{_tbl([("Leak", "40%"), ("Each time", ""), ("Times a month", ""), ("A month", "")], 3)}''', kicker=KICK),
        P("Calls and <em>savings</em>", "Days 8 to 10", f'''{_tbl([("Company", "24%"), ("Date", ""), ("Who I spoke to", ""), ("Was", ""), ("Now", ""), ("Saved a month", "")], 10, "Total")}
          <div class="box" style="margin-top:10px"><div class="lbl">Script</div><p style="margin:4px 0 0;font-size:10pt">"Hi, I'm reviewing my bills.
          I've been a customer for [time]. What's the lowest price you can offer to keep me?" If they say no: "Could you
          check again, or transfer me to the department that handles cancellations?" Be polite, write down the name and
          the new price, and ask when it starts.</p></div>
          <h3>Notes</h3><div class="lines"></div>''', kicker=KICK),
        P("Budget", "Days 15 to 18", f'''
          <div class="g3" style="margin-bottom:8px">{_box("Take-home a month")}{_box("Spending money a month")}{_box("Weekly number", tint=True)}</div>
          <div class="g2"><div><h3>Bills and debt</h3>{_tbl([("Item", "58%"), ("A month", "")], 10, "Total")}</div>
          <div><h3>Savings and goals</h3>{_tbl([("Goal", "58%"), ("A month", "")], 4, "Total")}
          <h3>Irregular costs</h3>{_tbl([("Cost", "46%"), ("A year", ""), ("÷ 12", "")], 4, "Total")}</div></div>
          <p class="fineprint" style="margin-top:8px">Take-home - bills and debt - savings - irregular costs = spending money. Divide by the weeks in the month for your weekly number.</p>''',
          kicker=KICK),
        P("Debts", "Days 22 to 24", f'''{_tbl([("Debt", "26%"), ("Balance", ""), ("APR %", ""), ("Minimum", ""), ("Order", ""), ("Extra", "")], 10, "Total")}
          <div class="g2" style="margin-top:10px">{_box("My method: avalanche or snowball", 30)}{_box("Target debt and extra a month", 30)}</div>
          <p class="fineprint" style="margin-top:8px">Keep every minimum paid. If you can't cover the minimums, a nonprofit credit
          counselor (look for an NFCC member agency) can help for free or a low fee.</p>
          <h3>Notes</h3><div class="lines"></div>''', kicker=KICK),
    ]


def reviews_page() -> str:
    def rev(w):
        return (f'<div class="box" style="flex:1;display:flex;flex-direction:column"><div class="lbl">{w} review</div>'
                '<div style="font-size:9pt;margin:3px 0">Done: ___ of 7 days &nbsp; Found or saved: $______ a month</div>'
                '<div style="font-size:9pt">What worked? What will I do differently next week?</div><div class="lines"></div></div>')
    return P("Weekly <em>reviews</em>", "Days 7, 14, 21, 28",
             '<div style="display:flex;flex-direction:column;gap:10px;flex:1">' + "".join(rev(f"Week {i}") for i in range(1, 5)) + "</div>",
             kicker=KICK)


def ending_page() -> str:
    rules = "".join(f'<tr><td style="height:30px">{i}.</td><td></td></tr>' for i in range(1, 6))
    nxt = "".join(f'<tr><td style="height:30px">{i}.</td><td></td></tr>' for i in range(1, 4))
    return P("My money <em>rules</em>", "Day 30", f'''
      <h3>Five rules I'll keep</h3><table><tr><th style="width:6%"></th><th>Rule</th></tr>{rules}</table>
      <h3>Next month, I'll</h3><table><tr><th style="width:6%"></th><th>Action</th></tr>{nxt}</table>
      <div class="g2" style="margin-top:10px">{_box("Weekly check-in day", 26)}{_box("Monthly reset date", 26)}</div>
      <h3>Notes</h3><div class="lines"></div>''', kicker=KICK)


def pages() -> list[str]:
    return ([start_page(), snapshot_page("Starting <em>snapshot</em>", "Day 0: before you begin"), tracker_page()]
            + day_pages() + worksheets() + [reviews_page(), snapshot_page("Ending <em>snapshot</em>", "Day 29", end=True), ending_page()])


GET = ["21 printable pages, US Letter and A4: a start page, starting and ending snapshots, a 30-day tracker",
       "30 daily tasks of about 15 minutes in four weeks: see where it goes, cut and lower, plan it, debt and the future",
       "6 worksheets: accounts, bills and subscriptions, spending, calls and savings (with a phone script), budget, debts",
       "Weekly reviews and a page for your own money rules"]
GOOD = ["This is a DIGITAL DOWNLOAD. Nothing is shipped. Your files are in your Etsy account right after payment.",
        "Two PDFs: US Letter and A4. Print at home, or write on it in a PDF app on a tablet.",
        "Undated: start any day of any month.",
        "For personal use only. Please don't resell or share the files.",
        "An educational workbook, not financial, tax, legal or investment advice. What you save depends on your bills and choices."]
DISCLOSURE = "How it's made: written and designed by Money Made Simple. AI tools helped draft the text and lay out the pages; a person checked every page."
HOW = ["Print it (Letter or A4) and fill in the starting snapshot.", "Do one 15-minute task a day and color in the tracker.",
       "Finish with the ending snapshot and your money rules."]
HOOK = ("A 30-day money reset, one 15-minute task at a time: find every account and bill, cut what you don't use, build "
        "a one-page budget and a plan for your debt.")


def _gumroad() -> str:
    g = "\n".join(f"- {x}" for x in GET)
    return (f"{HOOK}\n\nWhat's inside:\n{g}\n\nInstant download: PDFs in US Letter and A4. $9, one payment, files you keep.\n\n"
            "Who it's for: anyone who feels behind with money and wants a plan without a weekend of spreadsheets. "
            "Who it's not for: if you're behind on payments or dealing with collections, start with a nonprofit credit "
            "counselor (an NFCC member agency).\n\n"
            "Educational content, not financial advice. Made with the help of AI tools for drafting and layout, and checked "
            "by a person. A problem with a file? Reply to your receipt email.\n\n"
            "Next step: The 20-Minute Budget [LINK: 20-Minute Budget product page] turns the Week 3 budget into a weekly "
            "system with a spreadsheet.")


LISTINGS = [
    dict(slug="money-reset-30-day", name="The Money Reset: 30-Day Challenge Workbook", price=9.00, kind="print",
         title="30 Day Money Challenge Workbook Printable, Reset Budget Planner and Finance Tracker",
         tags=["money challenge", "30 day challenge", "money reset", "budget workbook", "finance planner",
               "budget printable", "financial reset", "money planner", "budget challenge", "save money",
               "debt payoff", "new year budget", "money workbook"],
         attributes={"Paper size": "US Letter, A4", "File type": "PDF", "Dated or undated": "Undated",
                     "Primary colour": "Green", "Secondary colour": "White"},
         category="Paper & Party Supplies > Paper > Calendars & Planners", status="active")
]
for _it in LISTINGS:
    _it["description"] = etsy_description(__import__("shop").opener(_it, what="a 21-page printable PDF workbook in US Letter and A4") + " " + HOOK, GET, HOW, GOOD, DISCLOSURE)
    _it["gumroad"] = _gumroad()
