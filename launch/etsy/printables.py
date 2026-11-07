"""Ten low-cost printables for the Etsy shop. Each builder returns a list of page bodies (HTML).

Printer-friendly: white paper, thin ink lines, small green accents. Undated (works any year).
build_etsy.py wraps the pages, prints Letter and A4 PDFs, and checks nothing overflows a page.
"""
from __future__ import annotations

import random

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
FOOT = "&copy; Money Made Simple &middot; for personal use only, please don't resell or share the file"


def page(title: str, meta: str = "", body: str = "", kicker: str = "") -> str:
    return (f'<div class="top"><div>{f"<div class=kick>{kicker}</div>" if kicker else ""}<h1>{title}</h1></div>'
            f'<div class="meta">{meta}</div></div><div class="fill">{body}</div><div class="foot"><span>{FOOT}</span>'
            f'<span>moneymadesimple</span></div>')


def rows(n: int, cols: int, cls: str = "") -> str:
    return "".join("<tr>" + "".join(f'<td class="{cls}"></td>' for _ in range(cols)) + "</tr>" for _ in range(n))


def table(headers: list[str], n: int, widths: list[str] | None = None, total: str | None = None, cls: str = "") -> str:
    ws = widths or [""] * len(headers)
    head = "".join(f'<th style="width:{w}">{h}</th>' if w else f"<th>{h}</th>" for h, w in zip(headers, ws))
    tot = (f'<tr class="tot"><td>{total}</td>' + "<td></td>" * (len(headers) - 1) + "</tr>") if total else ""
    return f'<table class="{cls}"><tr>{head}</tr>{rows(n, len(headers))}{tot}</table>'


def how_to(title: str, steps: list[str], extra: str = "") -> str:
    lis = "".join(f'<li style="margin-bottom:8px">{s}</li>' for s in steps)
    return page(title, "Start here", f'''
      <p style="font-size:11pt">Thanks for your purchase! Print the pages you need, as many times as you like, for your own use.</p>
      <h3>How to use it</h3><ol style="font-size:10.5pt;padding-left:20px">{lis}</ol>
      <h3>Printing tips</h3>
      <ul style="font-size:10pt;padding-left:20px">
        <li>Choose the Letter file in the US and Canada, the A4 file almost everywhere else.</li>
        <li>Print at 100% / "actual size" for the best fit. Ink-friendly: mostly white with thin lines.</li>
        <li>Want to reuse it? Slip pages into a sheet protector and use a dry-erase marker, or fill it in on a tablet
            with an app that opens PDFs.</li>
      </ul>
      {extra}
      <div class="box" style="margin-top:auto"><div class="lbl">Good to know</div>
      <p style="margin:4px 0 0;font-size:9pt">This is an organising tool, not financial advice. Digital download: nothing is shipped.
      Questions or a printing problem? Message the shop through Etsy.</p></div>''', kicker="Money Made Simple")


# ----------------------------------------------------------------------------------------------- 1
def monthly_budget_planner() -> list[str]:
    pages = [how_to("Monthly <em>Budget</em> Planner", [
        "Fill in the <strong>Year at a glance</strong> page with your take-home pay and big goals.",
        "At the start of each month, list income, bills, savings and debt payments on that month's page.",
        "Take bills, savings and debt from income. What's left is your spending money for the month; divide by the number of weeks to get a weekly number.",
        "Check in once a week: tick paid bills and track spending against your weekly number.",
        "At month end, write what went well and one change for next month."])]
    yr = "".join(f"<tr><td style='height:28px'><strong>{m}</strong></td><td></td><td></td><td></td><td></td></tr>" for m in MONTHS)
    pages.append(page("Year at a <em>glance</em>", "Year: __________", f'''
      <table><tr><th style="width:22%">Month</th><th class="r">Income</th><th class="r">Spent</th><th class="r">Saved</th><th class="r">Debt paid</th></tr>{yr}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td><td></td></tr></table>
      <div class="g3" style="margin-top:12px">
        <div class="box" style="height:110px"><div class="lbl">Goal 1</div></div>
        <div class="box" style="height:110px"><div class="lbl">Goal 2</div></div>
        <div class="box" style="height:110px"><div class="lbl">Goal 3</div></div></div>
      <h3>Notes</h3><div class="lines"></div>'''))
    for m in MONTHS:
        pages.append(page(f"<em>{m}</em> budget", "Year: ________", f'''
          <div class="g4" style="margin-bottom:8px">
            <div class="box"><div class="lbl">Income</div><div style="height:22px"></div></div>
            <div class="box"><div class="lbl">Bills + debt</div><div style="height:22px"></div></div>
            <div class="box"><div class="lbl">Savings</div><div style="height:22px"></div></div>
            <div class="box" style="background:var(--tint)"><div class="lbl">Left to spend</div><div style="height:22px"></div></div></div>
          <div class="g2">
            <div>{table(["Income", "Expected", "Actual"], 4, ["46%", "", ""])}
                 <h3>Savings &amp; goals</h3>{table(["Goal", "Amount", "&#10003;"], 5, ["58%", "", "14%"])}</div>
            <div>{table(["Bill", "Due", "Amount", "Paid"], 12, ["44%", "13%", "", "13%"], total="Total")}</div></div>
          <h3>Weekly spending check-in &middot; weekly number: $________</h3>
          {table(["Week", "Spent", "Left", "One thing I'll do differently"], 5, ["12%", "16%", "16%", ""])}
          <h3>Month-end notes</h3><div class="lines"></div>'''))
    pages.append(page("<em>Notes</em>", "", '<div class="lines"></div>'))
    return pages


# ----------------------------------------------------------------------------------------------- 2
def paycheck_budget_planner() -> list[str]:
    def one(n: str) -> str:
        return f'''<div class="box" style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div style="display:flex;gap:10px"><div style="flex:1"><div class="lbl">Paycheck {n} &middot; date</div><div class="line"></div></div>
            <div style="flex:1"><div class="lbl">Amount</div><div class="line"></div></div></div>
          <div class="g2" style="flex:1">
            <div>{table(["Bills from this check", "$", "&#10003;"], 7, ["58%", "", "14%"])}</div>
            <div>{table(["Savings / debt / goals", "$", "&#10003;"], 4, ["58%", "", "14%"])}
              <div class="box" style="margin-top:8px;background:var(--tint)"><div class="lbl">Paycheck &minus; bills &minus; goals = spending money</div><div style="height:24px"></div></div></div></div></div>'''
    pages = [how_to("Paycheck <em>Budget</em> Planner", [
        "Use one block per paycheck. Write the pay date and the amount you actually received.",
        "List the bills due before your next paycheck and pay them from this one.",
        "Pay your savings, extra debt payment and goals next, before spending.",
        "What's left is your spending money until the next payday.",
        "Use the year tracker to see every paycheck at a glance (26 rows for every-two-weeks pay)."])]
    for _ in range(2):
        pages.append(page("Paycheck <em>plan</em>", "Month: ____________",
                          f'<div style="display:flex;flex-direction:column;gap:10px;flex:1">{one("A")}{one("B")}</div>'))
    yr = "".join(f"<tr><td class=c style='height:28px'>{i}</td><td></td><td></td><td></td><td></td><td></td></tr>" for i in range(1, 27))
    pages.append(page("Paycheck <em>year</em> tracker", "Year: ________", f'''
      <table><tr><th class="c" style="width:7%">#</th><th>Date</th><th class="r">Take-home</th><th class="r">Bills</th><th class="r">Saved</th><th class="r">Spending</th></tr>{yr}
      <tr class="tot"><td></td><td>Total</td><td></td><td></td><td></td><td></td></tr></table>'''))
    return pages


# ----------------------------------------------------------------------------------------------- 3
TILE_SETS = {
    500: [(5, 20), (10, 20), (20, 10)],
    1000: [(5, 30), (10, 40), (15, 30)],
    2500: [(10, 20), (20, 20), (25, 40), (45, 20)],
    5000: [(25, 20), (40, 30), (50, 30), (90, 20)],
}


def tiles_for(target: int) -> list[int]:
    vals = [v for v, n in TILE_SETS[target] for _ in range(n)]
    assert sum(vals) == target, target
    random.Random(target).shuffle(vals)
    return vals


def savings_challenge() -> list[str]:
    pages = [how_to("Savings <em>Challenge</em> Tracker", [
        "Pick a challenge: $500, $1,000, $2,500 or $5,000. Write your goal and a target date at the top.",
        "Every time you move money into savings, colour or cross off a circle with that amount.",
        "Do circles in any order: a big one on payday, small ones on tight weeks.",
        "When every circle is coloured, you've saved the full amount. Every set of circles adds up exactly to the goal.",
        "Keep the money in a separate savings account so it's out of sight."])]
    for target in (500, 1000, 2500, 5000):
        vals = tiles_for(target)
        cols = 10 if len(vals) == 100 else 8
        fs = "9pt" if target >= 2500 else "10pt"
        tiles = "".join(f'<div class="tile" style="font-size:{fs}">${v}</div>' for v in vals)
        pages.append(page(f"Save <em>${target:,}</em>", "Saving for: ______________________<br>Target date: _____________", f'''
          <div class="tiles" style="grid-template-columns:repeat({cols},1fr);align-content:start">{tiles}</div>
          <div class="g3" style="margin-top:auto"><div class="box"><div class="lbl">Started</div><div style="height:18px"></div></div>
            <div class="box"><div class="lbl">Halfway (${target // 2:,})</div><div style="height:18px"></div></div>
            <div class="box"><div class="lbl">Done!</div><div style="height:18px"></div></div></div>''',
                          kicker=f"{len(vals)} circles &middot; adds up to exactly ${target:,}"))
    return pages


# ----------------------------------------------------------------------------------------------- 4
def week_grid(amounts: list[str | int]) -> str:
    cells = "".join(
        f'<tr><td class="c"><strong>{i}</strong></td><td class="r">{"$" + str(a) if a != "" else ""}</td><td></td>'
        f'<td class="c"><span class="cb"></span></td></tr>' for i, a in enumerate(amounts[:26], start=1))
    cells2 = "".join(
        f'<tr><td class="c"><strong>{i}</strong></td><td class="r">{"$" + str(a) if a != "" else ""}</td><td></td>'
        f'<td class="c"><span class="cb"></span></td></tr>' for i, a in enumerate(amounts[26:], start=27))
    head = '<tr><th class="c" style="width:16%">Week</th><th class="r">Deposit</th><th>Total saved</th><th class="c" style="width:14%">Done</th></tr>'
    return f'<div class="g2"><table class="t28">{head}{cells}</table><table class="t28">{head}{cells2}</table></div>'


def week_52_challenge() -> list[str]:
    classic = list(range(1, 53))
    totals = sum(classic)
    pages = [how_to("52-Week <em>Savings</em> Challenge", [
        f"<strong>Classic:</strong> save $1 in week 1, $2 in week 2, up to $52 in week 52. Total: ${totals:,}.",
        "<strong>Reverse:</strong> start with $52 and count down. Easier at the end of the year, when holiday spending hits.",
        "<strong>Your own amounts:</strong> use the blank sheet for any amount, e.g. $10 or $25 a week.",
        "Write a running total each week and tick the box. Start any week of the year.",
        "Set up an automatic weekly transfer to make it effortless."])]
    pages.append(page("52-week <em>challenge</em>", f"Classic: $1 &rarr; $52 &middot; total ${totals:,}", week_grid(classic) +
                      f'<div class="box" style="margin-top:auto;background:var(--tint)"><div class="lbl">Goal</div><div class="big-num" style="font-size:22pt">${totals:,}</div></div>'))
    pages.append(page("52-week <em>reverse</em>", f"Reverse: $52 &rarr; $1 &middot; total ${totals:,}", week_grid(classic[::-1]) +
                      f'<div class="box" style="margin-top:auto;background:var(--tint)"><div class="lbl">Goal</div><div class="big-num" style="font-size:22pt">${totals:,}</div></div>'))
    pages.append(page("52-week <em>my way</em>", "Weekly amount: $________ &middot; goal: $________", week_grid([""] * 52) +
                      '<div class="box" style="margin-top:auto"><div class="lbl">Saving for</div><div style="height:24px"></div></div>'))
    return pages


# ----------------------------------------------------------------------------------------------- 5
def bill_tracker() -> list[str]:
    pages = [how_to("Bill <em>Payment</em> Tracker", [
        "List every bill once on the <strong>Bill list</strong>: who, due day, usual amount, autopay or not.",
        "Copy the bills into the <strong>12-month checklist</strong> and tick each month as you pay.",
        "Use the <strong>bill calendar</strong> to write bills on their due dates. Print one per month.",
        "Use the <strong>yearly bills</strong> page for once-a-year costs (renewals, insurance, fees), so they're not a surprise."])]
    pages.append(page("Bill <em>list</em>", "Updated: ____________",
                      table(["Bill / company", "Due day", "Amount", "Autopay?", "Account / login hint"], 22,
                            ["30%", "11%", "13%", "12%", ""], total="Monthly total", cls="t30")))
    months = "".join(f'<th class="c" style="width:5.2%">{m[:3]}</th>' for m in MONTHS)
    body = "".join("<tr><td></td><td></td>" + '<td class="c"><span class="cb"></span></td>' * 12 + "</tr>" for _ in range(22))
    pages.append(page("12-month <em>checklist</em>", "Year: ________",
                      f'<table class="t34"><tr><th style="width:24%">Bill</th><th class="c" style="width:9%">Due</th>{months}</tr>{body}</table>'))
    days = "".join(f'<div class="h">{d}</div>' for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    days += "".join("<div></div>" for _ in range(35))
    pages.append(page("Bill <em>calendar</em>", "Month: ____________",
                      f'<p class="note" style="margin:0 0 6px">Write the dates in the corners, then add each bill on its due date.</p>'
                      f'<div class="cal" style="grid-template-rows:auto repeat(5,1fr)">{days}</div>'
                      f'<div class="g3" style="margin-top:8px"><div class="box"><div class="lbl">Total bills</div><div style="height:16px"></div></div>'
                      f'<div class="box"><div class="lbl">Paid so far</div><div style="height:16px"></div></div>'
                      f'<div class="box"><div class="lbl">Still to pay</div><div style="height:16px"></div></div></div>'))
    pages.append(page("Yearly <em>bills</em>", "Year: ________",
                      table(["Bill", "Month due", "Amount", "Save per month (&divide;12)", "Paid"], 16, ["32%", "16%", "14%", "", "10%"],
                            total="Total", cls="t34") +
                      '<p class="note">Divide each yearly bill by 12 and set that aside every month, so the money is waiting when the bill comes.</p>'))
    return pages


# ----------------------------------------------------------------------------------------------- 6
def thermometer(name: str = "", segs: int = 20) -> str:
    cells = "".join(f"<div>{i * 5}%</div>" if i % 2 == 0 else "<div></div>" for i in range(1, segs + 1))
    return f'''<div class="box" style="display:flex;flex-direction:column;gap:5px">
      <div><div class="lbl">Fund</div><div class="line">{name}</div></div>
      <div style="display:flex;gap:8px"><div style="flex:1"><div class="lbl">Goal $</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">By</div><div class="line"></div></div></div>
      <div style="display:flex;gap:8px;flex:1;min-height:0">
        <div class="thermo" style="width:44px;flex:none">{cells}</div>
        <table style="flex:1;align-self:flex-start" class="t28"><tr><th>Date</th><th class="r">Added</th><th class="r">Total</th></tr>{rows(12, 3)}</table></div></div>'''


def sinking_funds() -> list[str]:
    pages = [how_to("Sinking <em>Funds</em> Tracker", [
        "A sinking fund is money you set aside every month for a cost you know is coming: car repairs, gifts, holidays, renewals.",
        "On the <strong>overview</strong>, list each fund, its goal and the date you need it. Goal &divide; months left = monthly amount.",
        "Give each fund a tracker. Every time you add money, log it and colour the thermometer up to the new total.",
        "When you spend from a fund, log it as a negative amount. That's what it's for: no guilt.",
        "Keep the money in a savings account. Many banks let you split one account into named 'buckets'."])]
    ov = table(["Fund", "Goal", "Need by", "Months left", "Per month", "Saved"], 14, ["26%", "", "", "", "", ""],
               total="Total per month", cls="t34")
    pages.append(page("Sinking funds <em>overview</em>", "Year: ________", ov +
                      '<h3>Ideas</h3><p class="note">Car repairs &middot; car insurance &middot; gifts &amp; holidays &middot; travel &middot; '
                      'medical &amp; dental &middot; pet care &middot; home repairs &middot; annual subscriptions &middot; clothing &middot; '
                      'back to school &middot; new phone &middot; moving</p>'))
    names = ["Car repairs", "Gifts &amp; holidays", "Travel", "Medical", "", "", "", ""]
    for i in range(0, 8, 2):
        pages.append(page("Sinking fund <em>trackers</em>", "",
                          f'<div class="g2" style="flex:1">{thermometer(names[i])}{thermometer(names[i + 1])}</div>'))
    return pages


# ----------------------------------------------------------------------------------------------- 7
def debt_coloring() -> list[str]:
    pages = [how_to("Debt Payoff <em>Coloring</em> Trackers", [
        "List your debts on the <strong>debt list</strong>: balance, interest rate, minimum payment.",
        "Pick a tracker for each debt (or one for your total). Divide the balance by the number of spaces: that's what each space is worth.",
        "Every time the balance drops by that much, colour a space.",
        "Pay the minimum on everything, then put any extra on one debt at a time. Highest rate first saves the most interest; smallest balance first gives quicker wins.",
        "Stick it on the fridge. Watching it fill up is the point."])]
    pages.append(page("My <em>debt</em> list", "Started: ____________",
                      table(["Debt", "Balance", "Rate %", "Minimum", "Order", "Paid off on"], 10,
                            ["28%", "", "11%", "", "10%", ""], total="Total", cls="t28") +
                      '<div class="g2" style="margin-top:12px"><div class="box" style="height:90px"><div class="lbl">Total debt today</div></div>'
                      '<div class="box" style="height:90px;background:var(--tint)"><div class="lbl">Debt-free date goal</div></div></div>'
                      '<h3>Why I\'m doing this</h3><div class="lines"></div>'))
    sq = "".join(f'<div class="sq">{i}</div>' for i in range(1, 101))
    pages.append(page("100 <em>squares</em>", "Debt: ____________ &middot; each square = $______",
                      f'<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:5px;aspect-ratio:1/1;max-height:6.6in;margin:0 auto;width:100%">{sq}</div>'
                      '<div class="g3" style="margin-top:auto"><div class="box"><div class="lbl">Start balance</div><div style="height:16px"></div></div>'
                      '<div class="box"><div class="lbl">Halfway!</div><div style="height:16px"></div></div><div class="box"><div class="lbl">Paid off on</div><div style="height:16px"></div></div></div>'))
    therm = "".join(f'<div>{100 - i * 2}%</div>' if i % 5 == 0 else "<div></div>" for i in range(50))[::-1]
    therm = "".join(f'<div>{(i + 1) * 2}%</div>' if (i + 1) % 5 == 0 else "<div></div>" for i in range(50))
    pages.append(page("Debt <em>thermometer</em>", "Debt: ____________ &middot; each line = $______",
                      f'<div style="display:flex;gap:18px;flex:1;min-height:0"><div class="thermo" style="width:120px;flex:none;border-radius:60px">{therm}</div>'
                      f'<div style="flex:1;display:flex;flex-direction:column">{table(["Date", "Payment", "New balance"], 22)}</div></div>'))
    path = "".join(f'<div class="tile" style="font-size:9pt;width:100%">{i}</div>' for i in range(1, 51))
    pages.append(page("Debt-free <em>staircase</em>", "Debt: ____________ &middot; each step = $______",
                      f'<p class="note" style="margin:0 0 8px">50 steps from the bottom-left to "FREE". Colour one each time you pay off another 2%.</p>'
                      f'<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:7px;direction:ltr">{path}</div>'
                      '<div style="margin-top:14px;text-align:center"><span class="big-num">FREE</span></div>'
                      '<h3>Rewards (small, cheap, at milestones)</h3>'
                      '<table><tr><th>At</th><th>My reward</th></tr><tr><td>25%</td><td></td></tr><tr><td>50%</td><td></td></tr>'
                      '<tr><td>75%</td><td></td></tr><tr><td>100%</td><td></td></tr></table>'))
    return pages


# ----------------------------------------------------------------------------------------------- 8
def expense_tracker() -> list[str]:
    pages = [how_to("Monthly <em>Expense</em> Tracker", [
        "Each time you spend, write the date, what it was, a category and the amount. Or catch up once a day from your banking app.",
        "Use short categories: Food, Eating out, Transport, Home, Fun, Shopping, Health, Other.",
        "At month end, add up each category on the <strong>summary</strong> page.",
        "Circle the one category that surprised you most. That's next month's focus. Just one."])]
    for part in (1, 2):
        pages.append(page(f"Expense <em>log</em> {part}", "Month: ____________",
                          table(["Date", "What", "Category", "Amount"], 38, ["12%", "44%", "22%", ""])))
    cats = ["Groceries", "Eating out", "Transport", "Home", "Bills", "Fun", "Shopping", "Health", "Gifts", "Other", "", ""]
    body = "".join(f"<tr><td>{c}</td><td></td><td></td><td></td></tr>" for c in cats)
    pages.append(page("Month <em>summary</em>", "Month: ____________", f'''
      <table><tr><th style="width:34%">Category</th><th class="r">Planned</th><th class="r">Actual</th><th class="r">Difference</th></tr>{body}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td></tr></table>
      <div class="g2" style="margin-top:12px"><div class="box" style="height:110px"><div class="lbl">Biggest surprise</div></div>
        <div class="box" style="height:110px;background:var(--tint)"><div class="lbl">Next month I'll</div></div></div>
      <h3>Notes</h3><div class="lines"></div>'''))
    return pages


# ----------------------------------------------------------------------------------------------- 9
def no_spend_challenge() -> list[str]:
    pages = [how_to("No-Spend <em>Challenge</em>", [
        "Choose your length: a weekend, 7 days, or the full 30 days.",
        "Write your rules first. Essentials (rent, bills, groceries, medicine, transport to work) are always allowed.",
        "Colour a circle for every day you spend nothing outside your rules.",
        "Slipped? Write it down, no guilt, and keep going. The point is noticing, not perfection.",
        "At the end, move the money you didn't spend to savings or a debt, and write the amount on the reflection page."])]
    circles = "".join(f'<div class="tile" style="font-size:16pt">{i}</div>' for i in range(1, 31))
    pages.append(page("30-day <em>no-spend</em>", "Start date: ____________", f'''
      <div class="tiles" style="grid-template-columns:repeat(6,1fr);align-content:start;gap:14px;padding:6px 20px">{circles}</div>
      <div class="g3" style="margin-top:auto"><div class="box"><div class="lbl">No-spend days</div><div style="height:22px"></div></div>
        <div class="box"><div class="lbl">Money not spent</div><div style="height:22px"></div></div>
        <div class="box" style="background:var(--tint)"><div class="lbl">Moved to savings / debt</div><div style="height:22px"></div></div></div>'''))
    pages.append(page("My <em>rules</em>", "", '''
      <div class="g2" style="flex:1"><div class="box" style="display:flex;flex-direction:column"><div class="lbl">Allowed (essentials)</div>
        <p class="note">Rent / mortgage &middot; bills &middot; groceries (list-only) &middot; medicine &middot; fuel / transit to work</p><div class="lines"></div></div>
        <div class="box" style="display:flex;flex-direction:column"><div class="lbl">Not allowed</div>
        <p class="note">e.g. takeout, coffee out, online shopping, new clothes, impulse buys</p><div class="lines"></div></div></div>
      <h3>Free things to do instead</h3><div class="lines" style="flex:.6"></div>'''))
    pages.append(page("<em>Reflection</em>", "Finished: ____________", '''
      <h3>What was hardest?</h3><div class="lines" style="flex:1"></div>
      <h3>What didn't I miss at all?</h3><div class="lines" style="flex:1"></div>
      <h3>One habit I'm keeping</h3><div class="lines" style="flex:.6"></div>
      <div class="box" style="background:var(--tint)"><div class="lbl">Total saved</div><div class="big-num" style="font-size:26pt">$</div></div>'''))
    return pages


# ----------------------------------------------------------------------------------------------- 10
def subscription_tracker() -> list[str]:
    pages = [how_to("Subscription <em>Tracker</em>", [
        "Look through 3 months of bank and card statements, your phone's app store subscriptions, PayPal and your email for receipts.",
        "List every recurring charge with how often it bills and its yearly cost (monthly &times; 12, weekly &times; 52).",
        "Decide for each one: <strong>K</strong>eep, <strong>C</strong>ancel, <strong>D</strong>owngrade or <strong>N</strong>egotiate.",
        "Write renewal dates for yearly ones and set a reminder a week before.",
        "Log every cancellation with the date and a confirmation number, then check next month's statement."])]
    pages.append(page("Subscription <em>tracker</em>", "Checked on: ____________",
                      table(["Subscription", "Cost", "Billed", "Yearly", "Renews", "K/C/D/N"], 20,
                            ["30%", "", "13%", "", "13%", "10%"], total="Total per year", cls="t28") +
                      '<div class="g2" style="margin-top:8px"><div class="box"><div class="lbl">Yearly cost before</div><div style="height:18px"></div></div>'
                      '<div class="box" style="background:var(--tint)"><div class="lbl">Saved per year</div><div style="height:18px"></div></div></div>'))
    pages.append(page("Cancellation <em>log</em>", "",
                      table(["Date", "Subscription", "How cancelled", "Confirmation #", "Stopped?"], 20,
                            ["12%", "26%", "20%", "", "11%"], cls="t34") +
                      '<p class="note">Tick "Stopped?" once you see the charge has gone from next month\'s statement.</p>'))
    return pages


PRINTABLES = {
    "monthly-budget-planner": monthly_budget_planner,
    "paycheck-budget-planner": paycheck_budget_planner,
    "savings-challenge-tracker": savings_challenge,
    "52-week-savings-challenge": week_52_challenge,
    "bill-payment-tracker": bill_tracker,
    "sinking-funds-tracker": sinking_funds,
    "debt-payoff-coloring-tracker": debt_coloring,
    "monthly-expense-tracker": expense_tracker,
    "no-spend-challenge": no_spend_challenge,
    "subscription-tracker": subscription_tracker,
}
