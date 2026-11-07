"""Couples Money Date Pack: a Valentine's printable set for Money Made Simple's Etsy shop (live early February).

Trackers and prompts with blank space, no advice text, so it's a planner under Etsy's 22 Oct 2026 AI-guide rule.
Undated, Letter + A4, in the shop's house style. Kept out of the undated bundles (it's seasonal): the Mega Bundle still
holds exactly the 40 core printables. The heart tracker's 50 hearts at $10 add up to exactly $500 (tested).
"""
from __future__ import annotations

from printables import how_to, page
from printables_more import box, boxes, grid, lined

HEARTS = [10] * 50
HEART_GOAL = sum(HEARTS)


def heart_svg(amount: int) -> str:
    return ('<svg viewBox="0 0 40 36" style="width:100%;display:block"><path d="M20 34 C 8 25 1 18 1 10.5 C 1 5 5 1 10.5 1 '
            'C 14.5 1 18 3.5 20 7 C 22 3.5 25.5 1 29.5 1 C 35 1 39 5 39 10.5 C 39 18 32 25 20 34 Z" fill="#fff" '
            'stroke="#0b1d13" stroke-width="1.4"/><text x="20" y="19" text-anchor="middle" font-size="9" font-weight="800" '
            f'font-family="Inter,Arial" fill="#0b1d13">${amount}</text></svg>')


def _two(prompts: list[str], h: int = 40) -> str:
    """Side-by-side answers: one box for each partner."""
    head = '<div class="g2" style="margin-bottom:4px"><div class="lbl">Partner 1: ____________</div><div class="lbl">Partner 2: ____________</div></div>'
    body = "".join(f'<h3 style="margin:8px 0 4px">{p}</h3><div class="g2">{box("", h)}{box("", h)}</div>' for p in prompts)
    return head + body


def money_date() -> str:
    agenda = ["Wins since last time", "What came in and what went out", "Bills and dates coming up", "Goals: how far along",
              "One thing to change", "Something fun to plan"]
    rows = "".join(f'<tr><td class="c" style="width:6%"><span class="cb"></span></td><td style="width:34%">{a}</td><td></td></tr>' for a in agenda)
    return page("Money <em>date</em> night", "Date: __________ &middot; Where: __________", f'''
      <table class="t34"><tr><th></th><th>On the agenda</th><th>Notes</th></tr>{rows}</table>
      {lined("Decisions we made")}
      {boxes(["Next money date", "Treat after", "How it went (1-5)"])}''', kicker="For two")


def money_story() -> str:
    return page("Our money <em>stories</em>", "Answer side by side", _two([
        "Money growing up felt like", "A purchase I loved", "Something about money that worries me",
        "Enough money would mean", "A dream I'd save for"], 66), kicker="For two")


def shared_goals() -> str:
    def card(n: int) -> str:
        bar = grid(['<div class="sq" style="aspect-ratio:1/1"></div>'] * 10, 10, 4)
        return (f'<div class="box" style="display:flex;flex-direction:column;gap:6px"><div class="lbl">Goal {n}</div>'
                f'<div class="line"></div><div class="g3">{box("Target $", 14)}{box("By", 14)}{box("Each month $", 14)}</div>'
                f'<div class="lbl">Progress (each square = 10%)</div>{bar}</div>')
    return page("Shared <em>goals</em>", "Pick up to three", f'''
      <div style="display:flex;flex-direction:column;gap:12px;flex:1">{card(1)}{card(2)}{card(3)}</div>
      {boxes(["Saving for these in", "Check in on", "Celebrate with"])}''', kicker="For two")


def who_pays() -> str:
    rows = "".join("<tr>" + "<td></td>" * 6 + "</tr>" for _ in range(18))
    return page("Who pays <em>what</em>", "Bills and accounts", f'''
      <table class="t30"><tr><th style="width:26%">Bill</th><th>Amount</th><th>Due</th><th>Paid by (1 / 2 / joint)</th>
      <th>From account</th><th>Autopay</th></tr>{rows}<tr class="tot"><td>Total</td><td></td><td></td><td></td><td></td><td></td></tr></table>
      {lined("Notes")}{boxes(["Partner 1 share", "Partner 2 share", "Joint account"])}''', kicker="For two")


def joint_budget() -> str:
    cats = ["Housing", "Utilities", "Groceries", "Transport", "Insurance", "Debt payments", "Savings", "Eating out",
            "Subscriptions", "Kids / pets", "Gifts", "Other"]
    body = "".join(f"<tr><td>{c}</td><td></td><td></td><td></td></tr>" for c in cats)
    return page("Our monthly <em>budget</em>", "Month: ____________", f'''
      <div class="g4">{box("Partner 1 income", 16)}{box("Partner 2 income", 16)}{box("Other income", 16)}{box("Total", 16, True)}</div>
      <table class="t28" style="margin-top:10px"><tr><th style="width:34%">Category</th><th class="r">Plan</th><th class="r">Actual</th>
      <th>Note</th></tr>{body}<tr class="tot"><td>Total</td><td></td><td></td><td></td></tr></table>
      {lined("Notes")}{boxes(["Fun money: partner 1", "Fun money: partner 2", "Left over"])}''', kicker="For two")


def heart_tracker() -> str:
    cells = [heart_svg(a) for a in HEARTS]
    return page("Save <em>together</em>", f"Goal: <strong>${HEART_GOAL}</strong> &middot; for: ______________",
                grid(cells, 10, 8, "padding:4px") +
                lined("What we're saving for", 0.6) +
                boxes(["Hearts filled", "Saved so far", f"Goal ${HEART_GOAL}"]),
                kicker=f"50 hearts &times; $10 = ${HEART_GOAL}")


def date_log() -> str:
    rows = "".join("<tr>" + "<td></td>" * 4 + '<td class="c">&#9825; &#9825; &#9825; &#9825; &#9825;</td></tr>' for _ in range(20))
    return page("Date night <em>log</em>", "Budget per date: $________", f'''
      <table class="t30"><tr><th style="width:14%">Date</th><th style="width:34%">What we did</th><th>Cost</th><th>Who planned</th>
      <th class="c" style="width:20%">Rating</th></tr>{rows}<tr class="tot"><td>Total</td><td></td><td></td><td></td><td></td></tr></table>
      {boxes(["Dates this year", "Spent on dates", "Favourite so far"])}''', kicker="For two")


def check_in() -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rows = "".join(f"<tr><td><b>{m}</b></td>" + "<td></td>" * 5 + "</tr>" for m in months)
    return page("Year of <em>check-ins</em>", "One line a month", f'''
      <table class="t44"><tr><th style="width:9%"></th><th>Money date held?</th><th>Saved together</th><th>Debt paid</th>
      <th>Goal progress</th><th style="width:26%">Highlight</th></tr>{rows}</table>
      {lined("Notes")}{boxes(["Best money decision this year", "Next year we'll"], 26, "g2")}''', kicker="For two")


HOW = ["Pick a night for your first money date and print the agenda page.",
       "Fill in your money stories side by side, then choose up to three shared goals.",
       "Use the bills and budget pages each month; colour a heart each time you save $10 together."]


def pages() -> list[str]:
    return [how_to("Couples Money <em>Date Pack</em>", HOW), money_date(), money_story(), shared_goals(), who_pays(),
            joint_budget(), heart_tracker(), date_log(), check_in()]
