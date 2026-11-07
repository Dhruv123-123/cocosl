"""Thirty more printables for the Etsy shop (savings challenges, budgets, debt, records).

All original layouts drawn with HTML/CSS/inline SVG in the shop's house style (printables.css). Undated,
ink-friendly. Every challenge that names a total has amounts that add up to exactly that total (tested).
"""
from __future__ import annotations

import random

from printables import MONTHS, how_to, page, rows, table

TINT = "var(--tint)"


def box(label: str, h: int = 18, tint: bool = False, style: str = "") -> str:
    bg = f"background:{TINT};" if tint else ""
    return f'<div class="box" style="{bg}{style}"><div class="lbl">{label}</div><div style="height:{h}px"></div></div>'


def boxes(labels: list[str], h: int = 18, cls: str = "g3", tint_last: bool = True, style: str = "margin-top:auto") -> str:
    inner = "".join(box(lab, h, tint=tint_last and i == len(labels) - 1) for i, lab in enumerate(labels))
    return f'<div class="{cls}" style="{style}">{inner}</div>'


def lined(label: str, flex: float = 1) -> str:
    return f'<h3>{label}</h3><div class="lines" style="flex:{flex}"></div>'


def grid(cells: list[str], cols: int, gap: int = 6, style: str = "") -> str:
    return f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:{gap}px;{style}">{"".join(cells)}</div>'


# ---------------------------------------------------------------------------------- small SVG pieces
def envelope_svg(n, amount: str | None = None) -> str:
    amt = amount if amount is not None else f"${n}"
    return (f'<svg viewBox="0 0 60 42" style="width:100%;display:block"><rect x="1" y="1" width="58" height="40" rx="3" '
            f'fill="#fff" stroke="#0b1d13" stroke-width="1.4"/><polyline points="1.5,2 30,22 58.5,2" fill="none" '
            f'stroke="#c9c3b3" stroke-width="1.2"/><text x="30" y="36" text-anchor="middle" font-size="11" '
            f'font-weight="800" font-family="Inter,Arial" fill="#0b1d13">{amt}</text></svg>')


def die_svg(n: int, size: int = 26) -> str:
    pos = {1: [(13, 13)], 2: [(7, 7), (19, 19)], 3: [(7, 7), (13, 13), (19, 19)], 4: [(7, 7), (19, 7), (7, 19), (19, 19)],
           5: [(7, 7), (19, 7), (13, 13), (7, 19), (19, 19)], 6: [(7, 6), (19, 6), (7, 13), (19, 13), (7, 20), (19, 20)]}[n]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="2.3" fill="#0b1d13"/>' for x, y in pos)
    return (f'<svg viewBox="0 0 26 26" width="{size}" height="{size}"><rect x="1" y="1" width="24" height="24" rx="5" '
            f'fill="#fff" stroke="#0b1d13" stroke-width="1.4"/>{dots}</svg>')


def jar_svg(bands: int = 20) -> str:
    top, bottom, left, right = 70, 470, 40, 260
    lines = "".join(
        f'<line x1="{left + 4}" x2="{right - 4}" y1="{bottom - (bottom - top) * i / bands:.1f}" '
        f'y2="{bottom - (bottom - top) * i / bands:.1f}" stroke="#c9c3b3" stroke-width="1"/>'
        f'<text x="{right + 10}" y="{bottom - (bottom - top) * i / bands + 4:.1f}" font-size="11" fill="#5b6a61" '
        f'font-family="Inter,Arial">{i * 100 // bands}%</text>' for i in range(1, bands) if True)
    return f'''<svg viewBox="0 0 320 500" style="height:100%;max-height:6.4in">
      <rect x="70" y="20" width="160" height="34" rx="6" fill="#fff" stroke="#0b1d13" stroke-width="2.5"/>
      <path d="M85 54 C 40 62, 40 70, 40 95 L 40 450 Q 40 470 60 470 L 240 470 Q 260 470 260 450 L 260 95 C 260 70, 260 62, 215 54 Z"
        fill="#fff" stroke="#0b1d13" stroke-width="2.5"/>{lines}
      <text x="150" y="495" text-anchor="middle" font-size="12" font-weight="800" fill="#1e8a50" font-family="Inter,Arial">START HERE &#8593;</text></svg>'''


# ======================================================================== savings challenges (1-10)
ENVELOPE_HOW = [
    "Number 100 real envelopes 1 to 100, or just use this chart.",
    "Pick a number at random (shuffle, roll, or close your eyes), put that many dollars aside and colour that envelope.",
    "Do one a day, two a week, or whatever fits. Big numbers on payday, small ones on tight weeks.",
    "When every envelope is coloured you've saved the total at the top: 1 + 2 + ... + 100 = $5,050.",
    "Keep the cash safe or, better, move it into a savings account each week.",
]


def envelope_challenge() -> list[str]:
    pages = [how_to("100 <em>Envelope</em> Challenge", ENVELOPE_HOW)]
    for n, total, cols in ((100, 5050, 10), (50, 1275, 10)):
        cells = [envelope_svg(i) for i in range(1, n + 1)]
        pages.append(page(f"{n} <em>envelope</em> challenge", f"Goal: <strong>${total:,}</strong> &middot; started: _________",
                          grid(cells, cols, 7) + boxes(["Envelopes done", "Saved so far", f"Goal ${total:,}"]),
                          kicker=f"1 + 2 + ... + {n} = ${total:,}"))
    pages.append(page("Envelope <em>log</em>", "",
                      table(["Date", "Envelope #", "Amount", "Running total", "Moved to bank?"], 30,
                            ["16%", "16%", "16%", "", "18%"], cls="t26")))
    return pages


PAYCHECK_GOALS = [(520, 20), (1040, 40), (1300, 50), (2600, 100), (5200, 200)]


def paycheck_savings_challenge() -> list[str]:
    pages = [how_to("26-Paycheck <em>Savings</em> Challenge", [
        "Paid every two weeks? That's 26 paychecks a year. Pick a goal from the table and save the same amount from every check.",
        "Write the pay date, what you saved and the running total. Tick the box.",
        "Missed one? Add a little to the next few checks; the total still works out.",
        "Make it automatic: set a transfer for payday morning so it happens before you can spend it."])]
    goals = "".join(f"<tr><td>${g:,}</td><td>${a} per paycheck</td></tr>" for g, a in PAYCHECK_GOALS)
    body = "".join(f'<tr><td class="c"><strong>{i}</strong></td><td></td><td></td><td></td><td class="c"><span class="cb"></span></td></tr>'
                   for i in range(1, 27))
    pages.append(page("26-paycheck <em>challenge</em>", "Goal: $________ &middot; per check: $______", f'''
      <div style="display:flex;gap:14px;flex:1">
        <table class="t26" style="flex:1.6;align-self:flex-start"><tr><th class="c" style="width:10%">#</th><th>Pay date</th><th class="r">Saved</th>
          <th class="r">Total</th><th class="c" style="width:10%">Done</th></tr>{body}</table>
        <div style="flex:1;display:flex;flex-direction:column;gap:10px">
          <table><tr><th>Goal</th><th>Save</th></tr>{goals}</table>
          {box("Saving for", 40)}{box("Halfway (check 13)", 24)}{box("Finished!", 30, tint=True)}</div></div>'''))
    return pages


def _days(pattern: list[int], seed: int) -> list[int]:
    vals = pattern * 5
    random.Random(seed).shuffle(vals)
    return vals


THIRTY_DAY = {100: [1, 2, 3, 4, 5, 5], 250: [3, 5, 8, 10, 12, 12], 500: [5, 10, 15, 20, 25, 25]}


def thirty_day_challenge() -> list[str]:
    pages = [how_to("30-Day <em>Savings</em> Challenge", [
        "Pick a version: $100, $250 or $500 in 30 days.",
        "Each day, save the amount in one circle (any circle, any order) and colour it.",
        "Every set of 30 circles adds up to exactly the goal at the top of its page.",
        "Short on a day? Pick a small circle. Payday? Knock out a big one."])]
    for target, pat in THIRTY_DAY.items():
        vals = _days(pat, target)
        cells = [f'<div class="tile" style="font-size:15pt">${v}</div>' for v in vals]
        pages.append(page(f"Save <em>${target}</em> in 30 days", "Start date: ____________",
                          f'<div class="tiles" style="grid-template-columns:repeat(6,1fr);align-content:start;gap:12px;padding:4px 24px">{"".join(cells)}</div>'
                          + boxes(["Day I started", "Days done", f"Goal ${target}"]), kicker="30 circles &middot; colour one a day"))
    return pages


def roll_and_save() -> list[str]:
    key = "".join(f'<div style="display:flex;align-items:center;gap:8px">{die_svg(n)}<span><strong>${5 * n}</strong> or <strong>${10 * n}</strong></span></div>'
                  for n in range(1, 7))
    pages = [how_to("Roll &amp; Save <em>Dice</em> Challenge", [
        "Once a week, roll one die. Save $5 times the number you roll (or $10 times, for the bigger version).",
        "Draw the dots in that week's die and write the amount.",
        "Some weeks you roll a 1, some a 6. On average it comes out about $910 a year at $5, or $1,820 at $10.",
        "A fun one to do with kids or a partner: take turns rolling."],
        extra=f'<h3>The key</h3>{grid([key], 1)}')]
    cells = [f'<div class="box" style="padding:4px 6px;display:flex;align-items:center;gap:6px"><span class="note" style="width:18px">{i}</span>'
             f'<svg viewBox="0 0 26 26" width="26" height="26"><rect x="1" y="1" width="24" height="24" rx="5" fill="#fff" stroke="#0b1d13" stroke-width="1.4"/></svg>'
             f'<span style="flex:1;border-bottom:1px solid var(--line);height:16px"></span></div>' for i in range(1, 53)]
    pages.append(page("Roll &amp; <em>save</em>", "Each pip = $5 / $10 (circle one)",
                      grid(cells, 4, 6) + boxes(["Total saved", "Best roll", "Saving for"], 16), kicker="52 weeks &middot; one roll a week"))
    return pages


def spare_change_jar() -> list[str]:
    pages = [how_to("Spare Change <em>Jar</em> Tracker", [
        "Pick a goal for your jar and write it on the label line.",
        "Every time you add money (coins, a round-up, a skipped coffee), log it.",
        "Each line in the jar is 5% of the goal. Colour up to your new total.",
        "When it's full, bank it and start a new jar."])]
    pages.append(page("Spare change <em>jar</em>", "Goal: $________ &middot; each line = $______", f'''
      <div style="display:flex;gap:14px;flex:1;min-height:0">
        <div style="flex:1;display:flex;align-items:center;justify-content:center">{jar_svg()}</div>
        <div style="flex:1;display:flex;flex-direction:column">
          {box("Jar label: saving for", 28)}
          {table(["Date", "Added", "Total"], 24, ["30%", "", ""], cls="t26")}</div></div>'''))
    return pages


BINGO = {1000: [70, 70, 25, 30, 35, 40, 45, 50, 55, 20, 25, 30, 35, 40, 45, 50, 55, 20, 25, 30, 35, 40, 45, 50]}
BINGO[1000][0] += 1000 - sum(BINGO[1000])  # 24 squares = $1,000 exactly (checked in tests)
BINGO[2000] = [2 * v for v in BINGO[1000]]


def bingo_card(vals: list[int | str], title: str) -> str:
    vals = list(vals)
    random.Random(len(vals) + sum(v for v in vals if isinstance(v, int))).shuffle(vals)
    vals.insert(12, "FREE")
    cells = [f'<div class="sq" style="aspect-ratio:1/1;font-size:{18 if v == "FREE" else 16}pt;font-weight:900;color:var(--ink);'
             f'{"background:var(--tint);" if v == "FREE" else ""}">{v if isinstance(v, str) else "$" + str(v)}</div>' for v in vals]
    head = "".join(f'<div style="text-align:center;font-size:26pt;font-weight:900;color:var(--green-d)">{c}</div>' for c in "SAVER")
    return (f'<div style="width:6.4in;margin:0 auto"><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px">{head}</div><div style="display:grid;grid-template-columns:repeat(5,1fr);'
            f'gap:8px;margin-top:6px">{"".join(cells)}</div></div>')


def savings_bingo() -> list[str]:
    pages = [how_to("Savings <em>Bingo</em>", [
        "Each square is an amount to save. Save it, then colour the square. The middle one's free.",
        "Every five in a row (across, down or diagonal) earns a small, cheap reward you choose now.",
        "Colour the whole card and you've saved exactly the goal.",
        "The blank card is for your own amounts."])]
    for goal, vals in BINGO.items():
        pages.append(page(f"<em>${goal:,}</em> savings bingo", "Started: __________",
                          bingo_card(vals, str(goal)) + boxes(["Lines done", "My bingo reward", f"Card total ${goal:,}"]),
                          kicker="24 squares + free space"))
    pages.append(page("<em>Your own</em> savings bingo", "Goal: $________", bingo_card([""] * 24, "") +
                      boxes(["Lines done", "My bingo reward", "Card total"])))
    return pages


def travel_fund() -> list[str]:
    pages = [how_to("Travel <em>Fund</em> Tracker", [
        "Fill in the trip budget first: transport, stay, food, things to do, getting around, extras.",
        "The total is your goal. Divide it by 40: each stamp on the passport page is worth that much.",
        "Stamp (colour) one every time you add that amount. Count the days down on the side.",
        "Book things as the fund allows, not before."])]
    stamps = [f'<div style="border:1.5px dashed var(--ink);border-radius:{"50%" if i % 3 == 0 else "8px"};aspect-ratio:1/1;display:flex;'
              f'align-items:center;justify-content:center;font-size:9pt;color:var(--muted);transform:rotate({(-6, 4, -2, 7)[i % 4]}deg)">{i + 1}</div>'
              for i in range(40)]
    pages.append(page("Travel <em>fund</em> passport", "Trip: ______________ &middot; each stamp = $______",
                      grid(stamps, 8, 12, "padding:6px 4px") +
                      f'<h3>Countdown</h3>{grid(["<div class=sq style=aspect-ratio:1/1></div>"] * 30, 15, 4)}' +
                      boxes(["Leaving on", "Saved so far", "Trip total"])))
    cats = ["Flights / train / fuel", "Where we're staying", "Food + drink", "Things to do", "Getting around there",
            "Insurance + documents", "Gifts + extras", "Buffer (10%)"]
    body = "".join(f"<tr><td>{c}</td><td></td><td></td><td></td></tr>" for c in cats)
    pages.append(page("Trip <em>budget</em>", "Dates: ______________", f'''
      <table class="t30"><tr><th style="width:40%">Cost</th><th class="r">Estimate</th><th class="r">Actual</th><th>Booked?</th></tr>{body}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td></tr></table>
      {lined("Packing + to-do")}{boxes(["Months to go", "Save per month", "Save per paycheck"])}'''))
    return pages


def emergency_fund() -> list[str]:
    pages = [how_to("Emergency <em>Fund</em> Tracker", [
        "Add up your essentials only: housing, utilities, food, insurance, transport, minimum debt payments.",
        "That's one month. Write the milestones: a starter amount, then 1, 2, 3 (and up to 6) months.",
        "Each square on the tracker is the 6-month total divided by 60. Colour as you save.",
        "Only for real emergencies: job loss, urgent repairs, medical bills. Refill it after."])]
    ess = ["Rent / mortgage", "Utilities", "Groceries", "Insurance", "Transport", "Phone", "Minimum debt payments", "Other must-pays"]
    body = "".join(f"<tr><td>{e}</td><td></td></tr>" for e in ess)
    steps = "".join(f'<tr><td>{m}</td><td></td><td class="c"><span class="cb"></span></td><td></td></tr>'
                    for m in ["Starter: $500 or $1,000", "1 month", "2 months", "3 months", "4 months", "5 months", "6 months"])
    sq = [f'<div class="sq" style="aspect-ratio:1/1">{i}</div>' for i in range(1, 61)]
    pages.append(page("Emergency <em>fund</em>", "Each square = $______", f'''
      <div class="g2"><table class="t26"><tr><th>Essential monthly cost</th><th class="r">$</th></tr>{body}
        <tr class="tot"><td>One month</td><td></td></tr></table>
        <table class="t26"><tr><th>Milestone</th><th class="r">Amount</th><th class="c">Hit</th><th>Date</th></tr>{steps}</table></div>
      <h3>60 squares to six months</h3>{grid(sq, 12, 5)}
      {boxes(["Months covered today", "Saved", "Full goal (6 months)"])}'''))
    return pages


def home_fund() -> list[str]:
    def wall() -> str:
        rows_html = []
        n = 1
        for r in range(10):
            off = r % 2
            cells = []
            if off:
                cells.append('<div style="flex:.5"></div>')
            for _ in range(10):
                cells.append(f'<div style="flex:1;border:1.4px solid var(--ink);height:30px;display:flex;align-items:center;'
                             f'justify-content:center;font-size:8pt;color:var(--muted)">{n}</div>')
                n += 1
            if not off:
                cells.append('<div style="flex:.5"></div>')
            rows_html.append(f'<div style="display:flex;gap:3px">{"".join(cells)}</div>')
        return "".join(reversed(rows_html))
    roof = ('<svg viewBox="0 0 100 26" style="width:100%;display:block"><polygon points="2,25 50,2 98,25" fill="#fff" '
            'stroke="#0b1d13" stroke-width="1.2"/><text x="50" y="20" text-anchor="middle" font-size="7" font-weight="800" '
            'fill="#1e8a50" font-family="Inter,Arial">HOME</text></svg>')
    pages = [how_to("Home <em>Fund</em> Brick Tracker", [
        "On the costs page, add up what buying (or moving) will really cost: deposit / down payment, closing costs, moving, a cushion.",
        "Divide the total by 100. Each brick is worth that much.",
        "Colour a brick, bottom row first, every time you save that amount. 100 bricks and the house is built.",
        "Check what you need with a lender or adviser where you live; this tracker just keeps count."])]
    pages.append(page("Build the <em>house</em>", "Goal: $________ &middot; each brick = $______",
                      f'<div style="width:92%;margin:0 auto">{roof}<div style="display:flex;flex-direction:column;gap:3px">{wall()}</div></div>'
                      + boxes(["Bricks laid", "Saved", "Move-in goal date"]), kicker="100 bricks &middot; build from the bottom"))
    costs = ["Down payment / deposit", "Closing costs + fees", "Inspection + survey", "Moving + van", "First furniture + basics",
             "Cushion for repairs", "", ""]
    body = "".join(f"<tr><td>{c}</td><td></td><td></td></tr>" for c in costs)
    pages.append(page("Home <em>costs</em>", "", f'''<table class="t30"><tr><th style="width:50%">Cost</th><th class="r">Estimate</th><th class="r">Saved</th></tr>{body}
      <tr class="tot"><td>Total goal</td><td></td><td></td></tr></table>{lined("Questions to ask")}{boxes(["Months to go", "Save per month", "Total"])}'''))
    return pages


def holiday_fund() -> list[str]:
    pages = [how_to("Holiday <em>Savings</em> Planner", [
        "On the plan page, estimate this year's holiday costs: gifts, food, travel, decorations, events, giving.",
        "Divide the total by the months you have left. That's your monthly holiday saving.",
        "Log each month's saving. By the time the season comes, it's already paid for.",
        "Use the gift list (or the Gift Budget Planner) for who gets what."])]
    cats = ["Gifts", "Food + hosting", "Travel", "Decorations", "Cards + wrapping", "Events + outings", "Giving / charity", "Clothes"]
    body = "".join(f"<tr><td>{c}</td><td></td><td></td></tr>" for c in cats)
    m = "".join(f"<tr><td>{x}</td><td></td><td></td><td class='c'><span class='cb'></span></td></tr>" for x in MONTHS)
    pages.append(page("Holiday <em>plan</em>", "Year: ________", f'''
      <div class="g2"><div><h3 style="margin-top:0">Spending plan</h3><table class="t28"><tr><th>Category</th><th class="r">Budget</th><th class="r">Spent</th></tr>{body}
        <tr class="tot"><td>Total</td><td></td><td></td></tr></table></div>
        <div><h3 style="margin-top:0">Saving plan</h3><table class="t26"><tr><th>Month</th><th class="r">Save</th><th class="r">Total</th><th class="c">&#10003;</th></tr>{m}</table></div></div>
      {boxes(["Holiday total", "Months left", "Save each month"])}'''))
    return pages


# ======================================================================== budgets (11-19)
def weekly_budget() -> list[str]:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def week() -> str:
        cols = "".join(f'<div class="box" style="padding:5px 6px;display:flex;flex-direction:column"><div class="lbl">{d}</div>'
                       f'<div class="lines" style="flex:1"></div><div style="border-top:1.5px solid var(--ink);font-size:8pt;font-weight:800">$</div></div>'
                       for d in days)
        return f'<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:5px;flex:1">{cols}</div>'
    pages = [how_to("Weekly <em>Budget</em> Planner", [
        "Monday: write this week's money in (if any), bills due and your spending limit.",
        "Each day, jot what you spent and the day's total at the bottom.",
        "Sunday: add up the week, see what's left and move it to savings or next week.",
        "Print one page per week, 52 a year, or slip it in a sheet protector."])]
    for _ in range(2):
        pages.append(page("Weekly <em>budget</em>", "Week of: ____________", f'''
          {boxes(["Money in this week", "Bills due this week", "Savings this week", "Spending limit"], 16, "g4", style="margin-bottom:8px")}
          {week()}
          <div class="g2" style="margin-top:8px">{table(["Bill", "Due", "$", "&#10003;"], 5, ["44%", "", "", "12%"])}
            <div style="display:flex;flex-direction:column;gap:6px">{box("Spent this week", 16)}{box("Left over &rarr; savings", 16, tint=True)}</div></div>'''))
    return pages


def zero_based() -> list[str]:
    secs = [("Giving + saving", 4), ("Housing + utilities", 5), ("Food", 3), ("Transport", 3), ("Debt", 4),
            ("Insurance + health", 3), ("Personal + fun", 4), ("Other", 3)]
    blocks = "".join(f'<div>{table([s, "Planned", "Actual"], n, ["52%", "", ""])}</div>' for s, n in secs)
    pages = [how_to("Zero-Based <em>Budget</em> Worksheet", [
        "Write this month's take-home income at the top.",
        "Give every dollar a job in the sections below, savings and debt included, until Income minus Planned is exactly zero.",
        "Zero doesn't mean spend it all: savings is a job too.",
        "During the month, fill in Actual. Next month, adjust."])]
    for _ in range(2):
        pages.append(page("Zero-based <em>budget</em>", "Month: ____________", f'''
          {boxes(["Take-home income", "Total planned", "Income &minus; planned = 0"], 18, style="margin-bottom:6px")}
          <div class="g2" style="gap:8px">{blocks}</div>''', kicker="every dollar gets a job"))
    return pages


def fifty_thirty_twenty() -> list[str]:
    def col(name: str, pct: int, examples: str, n: int = 10) -> str:
        return (f'<div class="box" style="display:flex;flex-direction:column;gap:4px"><div class="big-num" style="font-size:28pt">{pct}%</div>'
                f'<div style="font-weight:800">{name}</div><div class="note">{examples}</div>'
                f'<div style="display:flex;gap:6px"><div style="flex:1"><div class="lbl">Target $</div><div class="line"></div></div>'
                f'<div style="flex:1"><div class="lbl">Actual $</div><div class="line"></div></div></div>'
                f'{table(["Item", "$"], n, ["70%", ""])}</div>')
    pages = [how_to("50/30/20 <em>Budget</em> Worksheet", [
        "Write your monthly take-home pay.",
        "Multiply by 0.5, 0.3 and 0.2 to get your three targets: needs, wants, and savings + extra debt payments.",
        "List what goes in each and compare to the target.",
        "It's a starting point, not a rule: where rent is high, needs may be 60%. The point is to see your split."])]
    pages.append(page("50 / 30 / <em>20</em>", "Month: ____________", f'''
      {boxes(["Take-home pay", "&times; 0.5 = needs", "&times; 0.3 = wants", "&times; 0.2 = savings + debt"], 16, "g4", False, "margin-bottom:8px")}
      <div class="g3" style="flex:1">{col("Needs", 50, "Housing, utilities, groceries, insurance, transport, minimum payments")}
        {col("Wants", 30, "Eating out, fun, shopping, subscriptions, hobbies, travel")}
        {col("Savings + debt", 20, "Emergency fund, goals, retirement, extra debt payments")}</div>
      {boxes(["My split this month: __% / __% / __%", "One change for next month"], 16, "g2")}'''))
    return pages


def cash_envelopes() -> list[str]:
    def card(name: str = "") -> str:
        return (f'<div class="box" style="display:flex;flex-direction:column;padding:6px 8px">'
                f'<div style="display:flex;gap:8px"><div style="flex:2"><div class="lbl">Envelope</div><div class="line">{name}</div></div>'
                f'<div style="flex:1"><div class="lbl">Budget $</div><div class="line"></div></div></div>'
                f'{table(["Date", "Spent", "Left"], 7, ["34%", "", ""])}</div>')
    names = ["Groceries", "Eating out", "Fuel", "Fun", "Personal", "Gifts", "Household", "Kids / pets"]
    pages = [how_to("Cash <em>Envelope</em> Trackers", [
        "Pick the categories you overspend on. Give each a monthly (or per-paycheck) amount.",
        "Withdraw that cash, or keep a 'virtual envelope' on paper and pay by card.",
        "Each time you spend from an envelope, log it and write what's left.",
        "When an envelope is empty, that category is done for the month. Moving money between envelopes is allowed: write it down."])]
    pages.append(page("Cash <em>envelopes</em>", "Month: ____________", grid([card(n) for n in names[:6]], 2, 8, "flex:1")))
    pages.append(page("Cash <em>envelopes</em>", "Month: ____________", grid([card(n) for n in names[6:]] + [card() for _ in range(4)], 2, 8, "flex:1")))
    pages.append(page("Cash <em>plan</em>", "Month: ____________",
                      table(["Envelope", "Per month", "Per paycheck", "$20s", "$10s", "$5s", "$1s"], 14,
                            ["26%", "", "", "9%", "9%", "9%", "9%"], total="Total", cls="t34") +
                      '<p class="note">Breaking it into notes before you go to the bank makes filling envelopes quick.</p>'))
    return pages


def daily_spending() -> list[str]:
    body = "".join(f'<tr><td class="c"><strong>{d}</strong></td><td></td><td></td><td class="c"><span class="cb"></span></td>'
                   f'<td class="c"><span class="cb"></span></td><td></td></tr>' for d in range(1, 32))
    pages = [how_to("Daily <em>Spending</em> Log", [
        "Every evening, write what you spent today (check your banking app). Zero days count too.",
        "Tick need or want for the biggest thing.",
        "Keep a running total. Compare it with your monthly spending limit.",
        "At month end, count your zero-spend days and your 'want' days."])]
    pages.append(page("Daily <em>spending</em>", "Month: ____________ &middot; limit: $______", f'''
      <table class="t26"><tr><th class="c" style="width:7%">Day</th><th class="r" style="width:13%">Spent</th><th>What on</th>
        <th class="c" style="width:8%">Need</th><th class="c" style="width:8%">Want</th><th class="r" style="width:16%">Running total</th></tr>{body}</table>
      {boxes(["Zero-spend days", "Total spent", "Under / over limit"], 14)}'''))
    return pages


def grocery_budget() -> list[str]:
    pages = [how_to("Grocery <em>Budget</em> Tracker", [
        "Set a monthly grocery budget and split it into weeks.",
        "Plan meals for the week first, then write the list from the plan (and from what's already in the cupboard).",
        "Log each shop's receipt. See the week's total against your weekly budget.",
        "End of month: what was wasted? Plan one less meal of it next month."])]
    wk = "".join(f'<tr><td>Week {i}</td><td></td><td></td><td></td><td></td></tr>' for i in range(1, 6))
    pages.append(page("Grocery <em>budget</em>", "Month: ____________ &middot; budget: $______", f'''
      <table class="t30"><tr><th>Week</th><th class="r">Budget</th><th class="r">Shop 1</th><th class="r">Shop 2</th><th class="r">Left</th></tr>{wk}
      <tr class="tot"><td>Month</td><td></td><td></td><td></td><td></td></tr></table>
      <h3>Receipt log</h3>{table(["Date", "Store", "Amount", "Notes"], 14, ["14%", "30%", "16%", ""])}
      {boxes(["Spent", "Saved vs budget", "Cheapest week's trick"], 14)}'''))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    plan = "".join(f"<tr><td><strong>{d}</strong></td><td></td><td></td><td></td></tr>" for d in days)
    lst = "".join(f'<div class="todo-line" style="display:flex;gap:6px;align-items:center;border-bottom:1px solid var(--line);height:22px">'
                  f'<span class="cb"></span></div>' for _ in range(16))
    pages.append(page("Meal plan + <em>list</em>", "Week of: ____________", f'''
      <table class="t34"><tr><th style="width:10%">Day</th><th>Breakfast</th><th>Lunch</th><th>Dinner</th></tr>{plan}</table>
      <div class="g3" style="margin-top:10px;flex:1">
        <div class="box"><div class="lbl">Produce</div>{lst}</div><div class="box"><div class="lbl">Pantry + fridge</div>{lst}</div>
        <div class="box"><div class="lbl">Other</div>{lst}</div></div>'''))
    return pages


def irregular_income() -> list[str]:
    pages = [how_to("Irregular <em>Income</em> Budget", [
        "List your bare-minimum monthly costs in priority order on the baseline page. That number is the income you need every month.",
        "Every time money comes in, log it and fill the buckets in order: essentials, bills, a buffer, then goals.",
        "Good month? Build the buffer until it covers a lean month. Lean month? Use the buffer for the gap.",
        "Freelance or self-employed? Set a share of each payment aside for tax and check the amount with a tax professional."])]
    pri = table(["#", "Must-pay", "Amount", "Due"], 16, ["7%", "50%", "", "14%"], total="Baseline / month", cls="t28")
    pages.append(page("Baseline <em>budget</em>", "Month: ____________", pri + f'''
      <h3>Fill the buckets, in order</h3>{boxes(["1. Essentials", "2. Bills + minimums", "3. Buffer (lean months)", "4. Goals + extra"], 30, "g4", False, "")}
      {boxes(["Baseline", "Buffer today", "Months covered"], 14)}'''))
    pages.append(page("Income <em>log</em>", "Month: ____________",
                      table(["Date", "From", "Amount", "Tax set aside", "To buckets", "Running total"], 24,
                            ["12%", "26%", "", "", "", ""], total="Total", cls="t28") +
                      boxes(["Income this month", "Baseline covered?", "Extra &rarr; buffer / goals"], 14)))
    return pages


UTILS = ["Electric", "Gas / heating", "Water", "Internet", "Phone", "Trash / other"]


def utility_tracker() -> list[str]:
    head = "".join(f'<th class="r">{u}</th>' for u in UTILS)
    body = "".join(f"<tr><td><strong>{m[:3]}</strong></td>" + "<td></td>" * (len(UTILS) + 1) + "</tr>" for m in MONTHS)
    pages = [how_to("Utility <em>Bill</em> Tracker", [
        "Each month, write each utility bill's amount (and usage, like kWh, if you track it).",
        "Total the month across, and each utility down.",
        "Compare with the same month last year: a jump is worth a call or a meter check.",
        "Use the notes for rate changes, providers and account numbers' last 4 digits."])]
    pages.append(page("Utility <em>bills</em>", "Year: ________", f'''
      <table class="t34"><tr><th style="width:9%">Month</th>{head}<th class="r">Total</th></tr>{body}
      <tr class="tot"><td>Year</td>{"<td></td>" * (len(UTILS) + 1)}</tr></table>
      <div class="g2" style="margin-top:10px;flex:1"><div class="box"><div class="lbl">Providers + account hints</div><div class="lines" style="height:90%"></div></div>
      <div class="box"><div class="lbl">Ways to lower them</div><div class="lines" style="height:90%"></div></div></div>'''))
    return pages


def car_expenses() -> list[str]:
    pages = [how_to("Car <em>Expense</em> Tracker", [
        "Log every fill-up: date, miles (odometer), amount and cost. Miles since the last fill &divide; amount = your mileage.",
        "Log every repair and service with what was done. Handy when you sell the car.",
        "List the yearly costs: insurance, registration, inspection, parking. Divide by 12 and save that each month.",
        "Add it all up: that's what the car really costs per month."])]
    pages.append(page("Fuel <em>log</em>", "Vehicle: ____________",
                      table(["Date", "Odometer", "Amount", "Cost", "Mileage", "Station / notes"], 30,
                            ["12%", "15%", "12%", "12%", "12%", ""], total="Total", cls="t26")))
    yearly = "".join(f"<tr><td>{c}</td><td></td><td></td><td></td></tr>" for c in
                     ["Insurance", "Registration / tax", "Inspection / MOT", "Parking / tolls", "Roadside cover", ""])
    pages.append(page("Service + <em>yearly costs</em>", "Vehicle: ____________",
                      table(["Date", "Odometer", "Work done", "Shop", "Cost"], 13, ["12%", "14%", "34%", "", ""], cls="t28") +
                      f'<h3>Yearly costs</h3><table class="t28"><tr><th style="width:40%">Cost</th><th class="r">Per year</th><th>Due</th>'
                      f'<th class="r">&divide; 12</th></tr>{yearly}<tr class="tot"><td>Total</td><td></td><td></td><td></td></tr></table>'
                      + boxes(["Fuel per month", "Yearly costs per month", "True monthly cost"], 14)))
    return pages


# ======================================================================== goals + net worth (20-22)
def goals_planner() -> list[str]:
    def goal(n: int) -> str:
        steps = "".join('<div style="display:flex;gap:6px;align-items:center;border-bottom:1px solid var(--line);height:22px">'
                        '<span class="cb"></span></div>' for _ in range(5))
        bar = "".join(f'<div style="flex:1;border-right:1px solid var(--line);font-size:6.5pt;color:#9aa59e;padding:1px">{(i + 1) * 10}%</div>'
                      for i in range(10))
        return f'''<div class="box" style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div style="display:flex;gap:8px"><div style="flex:3"><div class="lbl">Goal {n}</div><div class="line"></div></div>
            <div style="flex:1"><div class="lbl">Amount $</div><div class="line"></div></div><div style="flex:1"><div class="lbl">By</div><div class="line"></div></div>
            <div style="flex:1"><div class="lbl">Per month</div><div class="line"></div></div></div>
          <div class="g2"><div><div class="lbl">Why it matters</div><div class="line"></div><div class="line"></div></div>
            <div><div class="lbl">Steps</div>{steps}</div></div>
          <div><div class="lbl">Progress</div><div style="display:flex;border:1.5px solid var(--ink);border-radius:8px;height:22px;overflow:hidden">{bar}</div></div></div>'''
    pages = [how_to("Financial <em>Goals</em> Planner", [
        "Write up to three goals for the year on the vision page. Big, small, whatever matters to you.",
        "Give each one an amount and a date, then work out the monthly amount (amount &divide; months).",
        "Break it into steps you can tick off. The first step should take less than a day.",
        "Colour the progress bar every month."])]
    pages.append(page("Money <em>vision</em>", "Year: ________", f'''
      <div class="g3">{box("This year I want to", 90)}{box("I'll stop", 90)}{box("I'll start", 90)}</div>
      {lined("A year from now, my money life looks like")}
      {table(["Quarter", "Focus", "Done?"], 4, ["16%", "", "12%"], cls="t34")}'''))
    pages.append(page("Goal <em>plans</em>", "", f'<div style="display:flex;flex-direction:column;gap:10px;flex:1">{goal(1)}{goal(2)}{goal(3)}</div>'))
    return pages


def net_worth() -> list[str]:
    assets = ["Checking", "Savings", "Emergency fund", "Retirement", "Investments", "Home value", "Car value", "Other"]
    debts = ["Credit cards", "Car loan", "Student loans", "Mortgage", "Personal loans", "Medical / other"]
    a = "".join(f"<tr><td>{x}</td><td></td></tr>" for x in assets)
    d = "".join(f"<tr><td>{x}</td><td></td></tr>" for x in debts)
    pages = [how_to("Net <em>Worth</em> Tracker", [
        "Pick one day a month (or a quarter). Write what everything's worth today and what you owe.",
        "Net worth = what you own &minus; what you owe. It can be negative, and that's a fine place to start.",
        "Log it on the yearly page and plot it on the chart. The direction matters more than the number.",
        "Use rough values for a home or car; be consistent."])]
    pages.append(page("Net worth <em>snapshot</em>", "Date: ____________", f'''
      <div class="g2" style="align-items:start"><table class="t30"><tr><th>I own</th><th class="r">Value</th></tr>{a}<tr class="tot"><td>Total assets</td><td></td></tr></table>
        <table class="t30"><tr><th>I owe</th><th class="r">Balance</th></tr>{d}<tr class="tot"><td>Total debts</td><td></td></tr></table></div>
      {boxes(["Total assets", "&minus; total debts", "= Net worth"], 24)}{lined("Since last time")}'''))
    yr = "".join(f"<tr><td>{m[:3]}</td><td></td><td></td><td></td><td></td></tr>" for m in MONTHS)
    chart = "".join("<div></div>" for _ in range(12 * 10))
    pages.append(page("Net worth <em>year</em>", "Year: ________", f'''
      <table class="t26"><tr><th>Month</th><th class="r">Assets</th><th class="r">Debts</th><th class="r">Net worth</th><th class="r">Change</th></tr>{yr}</table>
      <h3>Plot it</h3><div style="display:grid;grid-template-columns:repeat(12,1fr);grid-template-rows:repeat(10,1fr);flex:1;
        border-left:1.5px solid var(--ink);border-bottom:1.5px solid var(--ink);background-image:linear-gradient(var(--line) 1px,transparent 1px),
        linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:calc(100%/12) 10%">{chart}</div>
      <div style="display:grid;grid-template-columns:repeat(12,1fr);font-size:7pt;color:var(--muted);text-align:center">{"".join(f"<span>{m[:3]}</span>" for m in MONTHS)}</div>'''))
    return pages


def money_review() -> list[str]:
    pages = [how_to("Monthly <em>Money</em> Review", [
        "Last day of the month, 20 minutes, with a drink you like.",
        "Fill in the numbers from your accounts and budget.",
        "Answer the questions honestly. Wins first.",
        "Pick one thing to do differently next month. Just one."])]
    for _ in range(2):
        pages.append(page("Money <em>review</em>", "Month: ____________", f'''
          {boxes(["Income", "Spent", "Saved", "Debt paid"], 16, "g4", False, "")}
          <div class="g2" style="margin-top:8px">{box("Net worth change", 16)}{box("Mood about money (1-10)", 16)}</div>
          <div class="g2" style="flex:1;margin-top:4px"><div style="display:flex;flex-direction:column">{lined("Wins (any size)")}{lined("What surprised me")}</div>
            <div style="display:flex;flex-direction:column">{lined("What I'd skip next time")}{lined("Bills or dates coming up")}</div></div>
          {box("Next month, I'll", 30, tint=True)}'''))
    return pages


# ======================================================================== debt (23-26)
def credit_card_payoff() -> list[str]:
    def card() -> str:
        sq = [f'<div class="sq" style="aspect-ratio:1/1;font-size:7pt">{i}</div>' for i in range(1, 31)]
        return f'''<div class="box" style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div class="g4"><div><div class="lbl">Card</div><div class="line"></div></div><div><div class="lbl">Balance $</div><div class="line"></div></div>
            <div><div class="lbl">APR %</div><div class="line"></div></div><div><div class="lbl">Minimum $</div><div class="line"></div></div></div>
          <div style="display:flex;gap:10px;flex:1"><div style="flex:1"><div class="lbl">30 squares &middot; each = $____</div>{grid(sq, 6, 4)}</div>
            <div style="flex:1.3">{table(["Date", "Paid", "Balance"], 8, ["30%", "", ""])}</div></div></div>'''
    pages = [how_to("Credit Card <em>Payoff</em> Tracker", [
        "One block per card. Write the balance, APR and minimum from your statement.",
        "Divide the balance by 30: each square is worth that much. Colour a square each time the balance drops by it.",
        "Log every payment and the new balance from your statement.",
        "Stop adding new charges to the card you're paying off. Lowering the APR (a quick call) helps too."])]
    for _ in range(2):
        pages.append(page("Credit card <em>payoff</em>", "", f'<div style="display:flex;flex-direction:column;gap:10px;flex:1">{card()}{card()}</div>'))
    return pages


def debt_snowball() -> list[str]:
    body = "".join(f'<tr><td class="c">{i}</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>' for i in range(1, 11))
    pages = [how_to("Debt <em>Snowball</em> Worksheet", [
        "List your debts from <strong>smallest balance to largest</strong> (snowball) or <strong>highest rate to lowest</strong> (avalanche: saves the most interest).",
        "Pay the minimum on everything. Put every extra dollar on debt #1.",
        "When #1 is paid off, add its whole payment to #2's minimum. That's the rollover; the 'snowball' grows.",
        "Keep going down the list. Write each paid-off date and celebrate it."])]
    for method in ("snowball", "avalanche"):
        pages.append(page(f"Debt <em>{method}</em>", "Started: ____________ &middot; extra per month: $______", f'''
          <p class="note" style="margin:0 0 6px">Order: {"smallest balance first" if method == "snowball" else "highest interest rate first"}.</p>
          <table class="t34"><tr><th class="c" style="width:6%">#</th><th style="width:22%">Debt</th><th class="r">Balance</th><th class="r">Rate %</th>
            <th class="r">Minimum</th><th class="r">Payment (min + rollover)</th><th>Paid off</th></tr>{body}
          <tr class="tot"><td></td><td>Total</td><td></td><td></td><td></td><td></td><td></td></tr></table>
          <h3>The rollover, written out</h3>{table(["When this is paid off", "Its payment of", "goes to", "New payment"], 6, ["30%", "", "30%", ""])}
          {boxes(["Total debt today", "Paid off so far", "Debt-free date goal"])}'''))
    return pages


def debt_mountain() -> list[str]:
    rows_html, n = [], 100
    for width in range(1, 20, 2):          # 1, 3, ..., 19 blocks: 100 in all
        cells = []
        for _ in range(width):
            cells.append(f'<div style="width:5.1%;aspect-ratio:1/1;border:1.3px solid var(--ink);border-radius:3px;display:flex;'
                         f'align-items:center;justify-content:center;font-size:6.5pt;color:var(--muted)">{n}</div>')
            n -= 1
        rows_html.append(f'<div style="display:flex;justify-content:center;gap:3px">{"".join(reversed(cells))}</div>')
    flag = ('<svg viewBox="0 0 40 40" width="34" height="34" style="display:block;margin:0 auto"><line x1="12" y1="4" x2="12" y2="38" '
            'stroke="#0b1d13" stroke-width="2"/><polygon points="12,5 34,11 12,17" fill="#2fbf71" stroke="#0b1d13" stroke-width="1.2"/></svg>')
    pages = [how_to("Debt <em>Mountain</em> Coloring Chart", [
        "Write the debt (or your total debt) and divide it by 100. Each block is worth that much.",
        "Start at the bottom: colour block 1 when you've paid off the first 1%, and climb.",
        "The rows get shorter as you go up, so the climb feels quicker near the top. The summit flag is debt-free.",
        "Make one for each debt, or one for everything."])]
    pages.append(page("Debt <em>mountain</em>", "Debt: ____________ &middot; each block = $______",
                      f'<div style="display:flex;flex-direction:column;gap:3px;margin:auto 0">{flag}{"".join(rows_html)}</div>'
                      + boxes(["Start balance", "Base camp (50%)", "Summit date"]), kicker="100 blocks &middot; climb from the bottom"))
    return pages


def loan_payoff() -> list[str]:
    sq = [f'<div class="sq" style="aspect-ratio:1/1;flex-direction:column;font-size:7pt">{i}</div>' for i in range(1, 61)]
    pages = [how_to("Loan <em>Payoff</em> Tracker", [
        "For a car, student or personal loan. Write the details from your loan statement.",
        "Colour one box per monthly payment (60 boxes = a 5-year loan; cross out the ones you don't need).",
        "Log extra payments separately and ask the lender to apply them to principal.",
        "Each extra payment shortens the loan: cross off boxes from the end."])]
    pages.append(page("Loan <em>payoff</em>", "Loan: ____________", f'''
      {boxes(["Original amount", "Rate %", "Monthly payment", "Payoff date"], 16, "g4", False, "margin-bottom:8px")}
      <h3 style="margin-top:0">One box per payment</h3>{grid(sq, 12, 5)}
      <h3>Extra payments</h3>{table(["Date", "Extra paid", "Applied to principal?", "New balance"], 9, ["16%", "", "", ""], cls="t26")}
      {boxes(["Payments left", "Balance today", "New payoff date"], 14)}'''))
    return pages


# ======================================================================== records (27-30)
def savings_register() -> list[str]:
    pages = [how_to("Savings Account <em>Register</em>", [
        "One register per savings account (or per goal).",
        "Write every deposit, withdrawal and interest payment with the new balance.",
        "Check it against the bank once a month and tick the line you checked.",
        "Withdrawals aren't failures: write what they were for."])]
    for _ in range(2):
        pages.append(page("Savings <em>register</em>", "Account / goal: ____________",
                          table(["Date", "Description", "Deposit", "Withdrawal", "Interest", "Balance", "&#10003;"], 30,
                                ["11%", "", "12%", "12%", "10%", "13%", "6%"], cls="t26")))
    return pages


def account_register() -> list[str]:
    pages = [how_to("Checking Account <em>Register</em>", [
        "Write every payment, card purchase, transfer and deposit, with the new balance.",
        "Type: CARD, CHK (cheque number), ATM, TFR, DEP, AUTO.",
        "Once a week, check against your banking app and tick each cleared line.",
        "Catch fees, double charges and forgotten autopays early."])]
    for _ in range(2):
        pages.append(page("Account <em>register</em>", "Account: ____________",
                          table(["Date", "Type / #", "Description", "Payment", "Deposit", "&#10003;", "Balance"], 30,
                                ["10%", "10%", "", "12%", "12%", "6%", "13%"], cls="t26")))
    return pages


def gift_budget() -> list[str]:
    pages = [how_to("Gift <em>Budget</em> Planner", [
        "List everyone you buy for in a year and each occasion: birthdays, holidays, weddings, thank-yous.",
        "Set a budget per gift and total it. Divide by 12: that's your monthly gift saving.",
        "Write ideas as you hear them. Tick bought and wrapped.",
        "The calendar page keeps birthdays and dates in one place."])]
    pages.append(page("Gift <em>list</em>", "Year: ________",
                      table(["Who", "Occasion", "Date", "Idea", "Budget", "Spent", "&#10003;"], 24,
                            ["16%", "13%", "9%", "", "10%", "10%", "6%"], total="Total", cls="t28") +
                      boxes(["Gift budget for the year", "&divide; 12 = save each month", "Spent so far"], 14)))
    cells = [f'<div class="box" style="padding:5px 7px;display:flex;flex-direction:column"><div class="lbl">{m}</div><div class="lines" style="flex:1"></div></div>'
             for m in MONTHS]
    pages.append(page("Birthdays + <em>dates</em>", "", grid(cells, 3, 8, "flex:1;grid-auto-rows:1fr")))
    return pages


def side_hustle() -> list[str]:
    pages = [how_to("Side Hustle <em>Income</em> Tracker", [
        "Name up to four income sources (shop, freelance, delivery, tutoring...).",
        "Each month, write what each one earned, your costs, and the profit.",
        "Set aside a share of the profit for tax as you go. How much depends on where you live and your total income, so check with a tax professional.",
        "Keep receipts for costs; log them on the expenses page."])]
    body = "".join(f"<tr><td><strong>{m[:3]}</strong></td>" + "<td></td>" * 7 + "</tr>" for m in MONTHS)
    pages.append(page("Side income <em>year</em>", "Year: ________", f'''
      <table class="t34"><tr><th style="width:8%">Month</th><th class="r">Source 1</th><th class="r">Source 2</th><th class="r">Source 3</th>
        <th class="r">Source 4</th><th class="r">Costs</th><th class="r">Profit</th><th class="r">Tax set aside</th></tr>{body}
      <tr class="tot"><td>Year</td>{"<td></td>" * 7}</tr></table>
      {boxes(["Source 1 / 2 / 3 / 4 names", "Best month", "Year profit"], 22)}'''))
    pages.append(page("Business <em>expenses</em>", "Year: ________",
                      table(["Date", "What", "Source", "Category", "Amount", "Receipt?"], 30,
                            ["11%", "", "14%", "16%", "12%", "10%"], total="Total", cls="t26")))
    return pages


MORE = {
    "100-envelope-challenge": envelope_challenge,
    "paycheck-savings-challenge": paycheck_savings_challenge,
    "30-day-savings-challenge": thirty_day_challenge,
    "roll-and-save-challenge": roll_and_save,
    "spare-change-jar-tracker": spare_change_jar,
    "savings-bingo": savings_bingo,
    "travel-fund-tracker": travel_fund,
    "emergency-fund-tracker": emergency_fund,
    "home-fund-tracker": home_fund,
    "holiday-savings-planner": holiday_fund,
    "weekly-budget-planner": weekly_budget,
    "zero-based-budget-worksheet": zero_based,
    "50-30-20-budget-worksheet": fifty_thirty_twenty,
    "cash-envelope-trackers": cash_envelopes,
    "daily-spending-log": daily_spending,
    "grocery-budget-tracker": grocery_budget,
    "irregular-income-budget": irregular_income,
    "utility-bill-tracker": utility_tracker,
    "car-expense-tracker": car_expenses,
    "financial-goals-planner": goals_planner,
    "net-worth-tracker": net_worth,
    "monthly-money-review": money_review,
    "credit-card-payoff-tracker": credit_card_payoff,
    "debt-snowball-worksheet": debt_snowball,
    "debt-mountain-coloring-chart": debt_mountain,
    "loan-payoff-tracker": loan_payoff,
    "savings-account-register": savings_register,
    "checking-account-register": account_register,
    "gift-budget-planner": gift_budget,
    "side-hustle-income-tracker": side_hustle,
}
