"""The dated 2027 Budget Planner (works for any year: change YEAR or call build(year)).

Comes in Sunday-start and Monday-start versions, each in US Letter and A4. Calendars are generated from Python's
calendar module, so every date is right. US federal holidays and the main US tax dates are marked; the tax dates
say "check irs.gov" because the IRS can move them.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta

from printables import MONTHS, page, table
from printables_more import box, boxes, lined

YEAR = 2027
DOW = {"sun": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], "mon": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}


def _nth(year: int, month: int, weekday: int, n: int) -> date:
    """n-th weekday (Mon=0) of a month; n=-1 is the last."""
    if n > 0:
        d = date(year, month, 1)
        d += timedelta(days=(weekday - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    d = date(year, month, calendar.monthrange(year, month)[1])
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def key_dates(year: int) -> dict[date, str]:
    """US federal holidays (actual dates) and the main US tax dates."""
    d = {
        date(year, 1, 1): "New Year's Day",
        _nth(year, 1, 0, 3): "MLK Jr. Day",
        _nth(year, 2, 0, 3): "Presidents' Day",
        _nth(year, 5, 0, -1): "Memorial Day",
        date(year, 6, 19): "Juneteenth",
        date(year, 7, 4): "Independence Day",
        _nth(year, 9, 0, 1): "Labor Day",
        _nth(year, 10, 0, 2): "Columbus / Indigenous Peoples' Day",
        date(year, 11, 11): "Veterans Day",
        _nth(year, 11, 3, 4): "Thanksgiving",
        date(year, 12, 25): "Christmas Day",
    }
    tax = {date(year, 1, 15): "Q4 estimated tax due*", date(year, 4, 15): "Tax Day*: returns + Q1 estimated tax",
           date(year, 6, 15): "Q2 estimated tax due*", date(year, 9, 15): "Q3 estimated tax due*",
           date(year, 10, 15): "Extended returns due*"}
    for k, v in tax.items():
        d[k] = (d[k] + " / " + v) if k in d else v
    return d


def _weeks(year: int, month: int, start: str) -> list[list[date]]:
    return calendar.Calendar(6 if start == "sun" else 0).monthdatescalendar(year, month)


def mini_month(year: int, month: int, start: str, marks: dict) -> str:
    head = "".join(f'<th class="c" style="padding:1px;font-size:6.5pt;background:none;border:0">{d[0]}</th>' for d in DOW[start])
    body = ""
    for wk in _weeks(year, month, start):
        body += "<tr>" + "".join(
            f'<td class="c" style="height:15px;border:0;padding:0;font-size:7.5pt;'
            f'{"color:#c9c3b3;" if d.month != month else ""}{"font-weight:800;color:var(--green-d);" if d in marks and d.month == month else ""}">'
            f'{d.day}</td>' for d in wk) + "</tr>"
    return (f'<div class="box" style="padding:5px 6px"><div style="font-weight:800;font-size:9.5pt;margin-bottom:2px">{MONTHS[month - 1]}</div>'
            f'<table style="font-size:7pt"><tr>{head}</tr>{body}</table></div>')


def cover(year: int, start: str) -> str:
    dots = "".join(f'<circle cx="{40 + (i % 6) * 52}" cy="{40 + (i // 6) * 52}" r="{18 if i % 5 else 22}" '
                   f'fill="{"#2fbf71" if i in (3, 8, 13, 14, 20) else "none"}" stroke="#0b1d13" stroke-width="2.5"/>' for i in range(24))
    return f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:0 .3in">
      <div class="kick" style="font-size:11pt">Money Made Simple</div>
      <div style="font-size:120pt;font-weight:900;letter-spacing:-.05em;line-height:.85;color:var(--ink)">{year}</div>
      <div style="font-size:40pt;font-weight:900;letter-spacing:-.02em;line-height:1">Budget <em style="font-style:normal;color:var(--green-d)">Planner</em></div>
      <div style="font-size:12pt;color:var(--muted)">January to December {year} &middot; {"Sunday" if start == "sun" else "Monday"} start</div>
      <svg viewBox="0 0 330 230" style="width:3.6in;margin-top:24px">{dots}</svg>
      <div class="box" style="width:4.2in;margin-top:10px"><div class="lbl">This planner belongs to</div><div style="height:26px"></div></div></div>
      <div class="foot"><span>&copy; Money Made Simple &middot; for personal use only, please don't resell or share the file</span><span>moneymadesimple</span></div>'''


def how_to_use(year: int, book: bool = False) -> str:
    steps = [
        f"<strong>Start with the front pages</strong> (about 30 minutes, once): your {year} goals, your pay dates, the bills that come once a year, your savings goals and your debts.",
        "<strong>Each month has three pages:</strong> a calendar (write paydays and due dates), a budget (plan the month before it starts), and a spending log (fill it as you go).",
        "<strong>Budget before the month starts.</strong> List income, then bills, then savings and debt. What's left is spending money; divide it by the weeks to get a weekly number.",
        "<strong>Check in once a week,</strong> 10 minutes: log spending, tick paid bills, look at your weekly number.",
        "<strong>End of each month:</strong> fill the month on the Year overview page and write one thing to change next month.",
        "<strong>December:</strong> the Year in review page and the next-year page close the loop.",
    ]
    lis = "".join(f'<li style="margin-bottom:9px">{s}</li>' for s in steps)
    return page(f"How to use your <em>{year}</em> planner", "Start here", f'''
      <ol style="font-size:10.5pt;padding-left:20px">{lis}</ol>
      {_how_extra(book)}
      <p class="note">* Dates marked with a star are the usual US tax deadlines. The IRS can move them; check irs.gov. Holidays shown are US federal holidays.</p>
      <div class="box" style="margin-top:auto"><div class="lbl">Good to know</div><p style="margin:4px 0 0;font-size:9pt">An organising tool, not financial
      advice. {"Write in pencil if you like to change your mind." if book else "Digital download: nothing is shipped. Questions or a printing problem? Message the shop through Etsy."}</p></div>''',
                kicker="Money Made Simple")


def _how_extra(book: bool) -> str:
    if book:
        return ('<h3>Tips</h3><ul style="font-size:10pt;padding-left:20px">'
                '<li>A pencil or a fine-tip pen that doesn\'t bleed works best on this paper.</li>'
                '<li>Keep a sticky note on the current month so the book opens where you need it.</li>'
                '<li>Fill in the front pages in January; they make every month quicker.</li></ul>')
    return ('<h3>Printing</h3><ul style="font-size:10pt;padding-left:20px">'
            '<li>Letter for the US and Canada, A4 almost everywhere else. Print at 100% / actual size. Double-sided works well.</li>'
            '<li>Print it all and put it in a binder, or print one month at a time.</li>'
            '<li>Prefer a tablet? Open the PDF in any note app that lets you write on PDFs.</li></ul>')


def year_page(year: int, start: str) -> str:
    marks = key_dates(year)
    minis = "".join(mini_month(year, m, start, marks) for m in range(1, 13))
    lst = "".join(f'<div style="display:flex;gap:8px;font-size:8pt;border-bottom:1px solid var(--line);padding:2px 0">'
                  f'<strong style="width:46px">{d.strftime("%b")} {d.day}</strong><span>{n}</span></div>' for d, n in sorted(marks.items()))
    return page(f"<em>{year}</em> at a glance", "", f'''
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:7px">{minis}</div>
      <h3>Key dates (US)</h3><div style="columns:2;column-gap:16px">{lst}</div>''')


def goals_page(year: int) -> str:
    g = "".join(f'''<div class="box" style="display:flex;gap:10px;align-items:stretch">
        <div style="flex:3"><div class="lbl">Goal {i}</div><div class="line"></div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">Amount</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">By</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">Per month</div><div class="line"></div></div></div>''' for i in (1, 2, 3))
    return page(f"My <em>{year}</em> money goals", "", f'''
      <div class="g3">{box("In " + str(year) + " I want to", 80)}{box("I'll stop", 80)}{box("I'll start", 80)}</div>
      <h3>Three goals</h3><div style="display:flex;flex-direction:column;gap:8px">{g}</div>
      {lined("By December " + str(year) + ", my money life looks like")}
      {table(["Quarter", "Focus", "Done?"], 4, ["16%", "", "12%"], cls="t30")}''')


def overview_page(year: int) -> str:
    body = "".join(f"<tr><td><strong>{m[:3]}</strong></td>" + "<td></td>" * 6 + "</tr>" for m in MONTHS)
    return page(f"<em>{year}</em> overview", "Fill in at the end of each month", f'''
      <table class="t34"><tr><th style="width:9%">Month</th><th class="r">Income</th><th class="r">Bills</th><th class="r">Spending</th>
        <th class="r">Saved</th><th class="r">Debt paid</th><th class="r">Left over</th></tr>{body}
        <tr class="tot"><td>Year</td>{"<td></td>" * 6}</tr></table>
      {boxes(["Best month", "Total saved in " + str(year), "Total debt paid"], 20)}''')


def annual_bills_page(year: int) -> str:
    cells = "".join(f'<div class="box" style="padding:5px 7px;display:flex;flex-direction:column"><div class="lbl">{m}</div>'
                    f'<div class="lines" style="flex:1"></div></div>' for m in MONTHS)
    return page("Yearly bills + <em>renewals</em>", str(year), f'''
      <p class="note" style="margin:0 0 6px">Insurance, registrations, memberships, subscriptions that renew once a year, gifts.
      Add them up and divide by 12: set that aside every month.</p>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:1fr;gap:7px;flex:1">{cells}</div>
      {boxes(["Yearly bills total", "&divide; 12 = set aside monthly"], 16, "g2")}''')


def paycheck_page(year: int) -> str:
    body = "".join(f'<tr><td class="c"><strong>{i}</strong></td><td></td><td></td><td></td><td></td><td class="c"><span class="cb"></span></td></tr>'
                   for i in range(1, 27))
    return page(f"<em>{year}</em> paychecks", "Paid every two weeks? 26 rows. Monthly? Use the first 12.", f'''
      <table class="t26"><tr><th class="c" style="width:6%">#</th><th style="width:18%">Pay date</th><th class="r">Take-home</th>
        <th class="r">To bills</th><th class="r">To savings</th><th class="c" style="width:8%">&#10003;</th></tr>{body}
        <tr class="tot"><td></td><td>Year</td><td></td><td></td><td></td><td></td></tr></table>''')


def savings_page(year: int) -> str:
    months = "".join(f'<th class="c" style="width:5.4%;padding:3px 0">{m[:1]}</th>' for m in MONTHS)
    rows = "".join("<tr><td></td><td></td>" + "<td></td>" * 12 + "<td></td></tr>" for _ in range(8))
    return page(f"<em>{year}</em> savings goals", "", f'''
      <table class="t34"><tr><th style="width:20%">Goal</th><th class="r" style="width:10%">Target</th>{months}<th class="r">Saved</th></tr>{rows}</table>
      <p class="note">Write what you add to each goal every month. The last column is the running total.</p>
      <h3>Emergency fund</h3>{boxes(["Essentials per month", "Months I want covered", "Target", "Saved by Dec"], 18, "g4", False, "")}
      {lined("Notes")}''')


def debt_page(year: int) -> str:
    months = "".join(f'<th class="c" style="width:5.4%;padding:3px 0">{m[:1]}</th>' for m in MONTHS)
    rows = "".join("<tr><td></td><td></td><td></td>" + "<td></td>" * 12 + "</tr>" for _ in range(8))
    return page(f"<em>{year}</em> debt payoff", "Write each balance at month end", f'''
      <table class="t34"><tr><th style="width:18%">Debt</th><th class="r" style="width:9%">Jan 1</th><th class="r" style="width:6%">Rate</th>{months}</tr>{rows}</table>
      {boxes(["Total debt Jan 1", "Total debt Dec 31", "Paid off in " + str(year)], 20, style="margin-top:10px")}
      <h3>Payoff order (snowball: smallest first &middot; avalanche: highest rate first)</h3>
      {table(["#", "Debt", "Paid off on", "Its payment rolls to"], 6, ["6%", "34%", "20%", ""], cls="t30")}''')


def month_calendar(year: int, month: int, start: str, marks: dict) -> str:
    weeks = _weeks(year, month, start)
    head = "".join(f'<div class="h">{d}</div>' for d in DOW[start])
    cells = ""
    for wk in weeks:
        for d in wk:
            other = d.month != month
            note = f'<span style="display:block;font-size:6.5pt;font-weight:600;color:var(--green-d);line-height:1.1;margin-top:2px">{marks[d]}</span>' \
                if d in marks and not other else ""
            cells += (f'<div style="{"background:#f7f6f2;color:#c9c3b3;" if other else ""}">{d.day}{note}</div>')
    nm = MONTHS[month - 1]
    return page(f"<em>{nm}</em> {year}", f"Month {month} of 12", f'''
      <div class="cal" style="grid-template-rows:auto repeat({len(weeks)},1fr)">{head}{cells}</div>
      <div class="g3" style="margin-top:8px">{box("Paydays", 34)}{box("Bills due", 34)}{box("This month's focus", 34, tint=True)}</div>''')


def month_budget(year: int, month: int) -> str:
    nm = MONTHS[month - 1]
    return page(f"<em>{nm}</em> budget", str(year), f'''
      {boxes(["Income", "Bills + debt", "Savings", "Left to spend"], 18, "g4", True, "margin-bottom:8px")}
      <div class="g2">
        <div>{table(["Income", "Expected", "Actual"], 4, ["46%", "", ""])}
          <h3>Savings + extra debt</h3>{table(["Where", "Plan", "&#10003;"], 5, ["58%", "", "14%"])}
          <h3>Spending</h3>{table(["Category", "Plan", "Actual"], 7, ["46%", "", ""])}</div>
        <div>{table(["Bill", "Due", "Amount", "Paid"], 15, ["44%", "13%", "", "13%"], total="Total")}</div></div>
      <h3>Weekly check-in &middot; weekly number: $________</h3>
      {table(["Week", "Spent", "Left", "Note"], 5, ["12%", "16%", "16%", ""])}''')


def month_log(year: int, month: int) -> str:
    nm = MONTHS[month - 1]
    return page(f"<em>{nm}</em> spending + review", str(year), f'''
      {table(["Date", "What", "Category", "Amount"], 24, ["11%", "45%", "22%", ""], cls="t26")}
      <div class="g2" style="margin-top:8px;flex:1">
        <div class="box" style="display:flex;flex-direction:column"><div class="lbl">Month-end: what went well</div><div class="lines" style="flex:1"></div></div>
        <div class="box" style="display:flex;flex-direction:column;background:var(--tint)"><div class="lbl">Next month I'll</div><div class="lines" style="flex:1"></div></div></div>''')


def review_pages(year: int) -> list[str]:
    return [
        page(f"<em>{year}</em> in review", "", f'''
          {boxes(["Total income", "Total saved", "Debt paid off", "Net worth change"], 22, "g4", False, "")}
          <div class="g2" style="flex:1;margin-top:6px"><div style="display:flex;flex-direction:column">{lined("Proudest money moment")}{lined("What I learned")}</div>
            <div style="display:flex;flex-direction:column">{lined("What I'd do differently")}{lined("Thank you, past me, for")}</div></div>'''),
        page(f"Looking ahead to <em>{year + 1}</em>", "", f'''
          <div class="g3">{box("Keep doing", 90)}{box("Stop doing", 90)}{box("Start doing", 90)}</div>
          <h3>{year + 1} goals</h3>{table(["Goal", "Amount", "By", "Per month"], 5, ["46%", "", "", ""], cls="t34")}
          {lined("Notes")}'''),
        page("<em>Notes</em>", "", '<div class="lines"></div>'),
    ]


def build(year: int = YEAR, start: str = "sun") -> list[str]:
    marks = key_dates(year)
    pages = [cover(year, start), how_to_use(year), year_page(year, start), goals_page(year), overview_page(year),
             annual_bills_page(year), paycheck_page(year), savings_page(year), debt_page(year)]
    for m in range(1, 13):
        pages += [month_calendar(year, m, start, marks), month_budget(year, m), month_log(year, m)]
    return pages + review_pages(year)


VARIANTS = {"Sunday-start": "sun", "Monday-start": "mon"}
