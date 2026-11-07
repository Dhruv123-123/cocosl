"""Two undated KDP low-content books with original interiors: a Debt Payoff Journal and a 52-Week Savings Challenge Log.

Each builder returns a list of page bodies in the same house style as the Etsy printables (printables.css), so
build_kdp.py can render them at 8.5 x 11 in. Undated on purpose: they sell all year and never go out of date.
"""
from __future__ import annotations

from printables import page, table
from printables_more import box, boxes, lined

TINT = "var(--tint)"


def title_page(kick: str, title_html: str, sub: str, motif: str) -> str:
    return f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:16px;padding:0 .3in">
      <div class="kick" style="font-size:11pt">{kick}</div>
      <div style="font-size:54pt;font-weight:900;letter-spacing:-.03em;line-height:.95">{title_html}</div>
      <div style="font-size:13pt;color:var(--muted)">{sub}</div>
      <div style="margin-top:22px">{motif}</div>
      <div class="box" style="width:4.2in;margin-top:14px"><div class="lbl">This journal belongs to</div><div style="height:26px"></div></div>
      <div class="box" style="width:4.2in"><div class="lbl">Started on</div><div style="height:20px"></div></div></div>
      <div class="foot"><span>Money Made Simple</span><span>moneymadesimple</span></div>'''


def how_page(title: str, steps: list[str], tips: list[str]) -> str:
    lis = "".join(f'<li style="margin-bottom:9px">{s}</li>' for s in steps)
    tps = "".join(f"<li>{t}</li>" for t in tips)
    return page(title, "Start here", f'''
      <ol style="font-size:10.5pt;padding-left:20px">{lis}</ol>
      <h3>Tips</h3><ul style="font-size:10pt;padding-left:20px">{tps}</ul>
      <div class="box" style="margin-top:auto"><div class="lbl">Good to know</div><p style="margin:4px 0 0;font-size:9pt">An
      organising journal, not financial advice. If debt feels unmanageable, a nonprofit credit counsellor (for example an
      NFCC member agency in the US) can help you look at options for free or at low cost.</p></div>''', kicker="Money Made Simple")


def blocks_svg(n: int = 100, cols: int = 10, label_every: int = 10) -> str:
    cells = "".join(
        f'<rect x="{6 + (i % cols) * 50}" y="{6 + (i // cols) * 50}" width="44" height="44" rx="5" fill="#fff" '
        f'stroke="#0b1d13" stroke-width="1.6"/><text x="{28 + (i % cols) * 50}" y="{33 + (i // cols) * 50}" '
        f'text-anchor="middle" font-size="12" font-family="Inter,Arial" fill="#9aa59e">{n - i}%</text>'
        if (n - i) % label_every == 0 else
        f'<rect x="{6 + (i % cols) * 50}" y="{6 + (i // cols) * 50}" width="44" height="44" rx="5" fill="#fff" '
        f'stroke="#0b1d13" stroke-width="1.6"/>' for i in range(n))
    rows = (n + cols - 1) // cols
    return f'<svg viewBox="0 0 {cols * 50 + 8} {rows * 50 + 8}" style="width:100%;max-height:6.6in">{cells}</svg>'


# =============================================================================================== Debt Payoff Journal
DEBT_PROMPTS = [
    "Why am I paying this off? Write the reason you'll want to remember on a hard day.",
    "What did debt cost me this month, beyond the interest? Time, sleep, choices?",
    "Which spending surprised me this month, and was it worth it?",
    "Three free things that made this month good.",
    "What would I tell a friend who was where I was when I started?",
    "Halfway check: what's working, and what's one thing to change?",
    "Which habit is helping most? How can I make it automatic?",
    "What does 'enough' look like for me: money, things, plans?",
    "Where am I still buying my way out of a bad day? What could I do instead?",
    "What will I do with the payments once a debt is gone?",
    "Who helped me this year, and how can I say thanks without spending?",
    "Looking back over twelve months: what am I proud of?",
]


def _debt_month(n: int) -> list[str]:
    snap = page(f"Month <em>{n}</em> &middot; balances", "Month: ______________  Year: ________", f'''
      {table(["Debt", "Start of month", "Paid", "Interest charged", "End of month"], 10, ["30%", "", "", "", ""], total="Total", cls="t30")}
      <div class="g3" style="margin-top:10px">{box("Paid off this month", 26)}{box("Extra paid on top of minimums", 26)}{box("Total debt now", 26, tint=True)}</div>
      <h3>Colour the countdown</h3><p class="note" style="margin:0">Total paid so far &divide; starting total = % done.
      Colour that many blocks on the Debt-free countdown page.</p>
      {lined("Notes")}''')
    log = page(f"Month <em>{n}</em> &middot; payment log", "", f'''
      {table(["Date", "Debt", "Amount", "Minimum or extra?", "Confirmation #"], 22, ["13%", "27%", "15%", "20%", ""], cls="t26")}
      {boxes(["Payments this month", "Extra found this month", "Next due date"], 20, "g3", True, "margin-top:10px")}''')
    weeks = "".join(f'''<div class="box" style="display:flex;gap:10px"><div style="width:62px"><div class="lbl">Week {w}</div></div>
        <div style="flex:1"><div class="lbl">Extra I found</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">A win</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">A struggle</div><div class="line"></div></div></div>''' for w in range(1, 6))
    check = page(f"Month <em>{n}</em> &middot; weekly check-ins", "10 minutes, same day each week", f'''
      <div style="display:flex;flex-direction:column;gap:8px">{weeks}</div>
      <div class="g2" style="margin-top:12px">{box("No-spend days this month", 30)}{box("Money moved to debt from cuts or sales", 30)}</div>
      <h3>Before next month</h3><div class="g3">{box("Keep doing", 50)}{box("Stop doing", 50)}{box("Try", 50, tint=True)}</div>''')
    journal = page(f"Month <em>{n}</em> &middot; journal", "", f'''
      <div class="box" style="background:{TINT}"><div class="lbl">This month's prompt</div>
      <p style="margin:6px 0 0;font-size:12pt;font-weight:600">{DEBT_PROMPTS[n - 1]}</p></div>
      <div class="lines" style="margin-top:10px"></div>''')
    return [snap, log, check, journal]


def debt_payoff_journal() -> list[str]:
    pages = [
        title_page("Money Made Simple", 'Debt Payoff <em style="font-style:normal;color:var(--green-d)">Journal</em>',
                   "Track every debt, every payment and every win until you owe nothing.",
                   blocks_svg(30, 10, 99).replace("max-height:6.6in", "width:3.6in")),
        "COPYRIGHT",
        how_page("How to use this <em>journal</em>", [
            "<strong>List every debt</strong> on My debts: balance, interest rate (APR), minimum payment and due day.",
            "<strong>Pick an order</strong>. Snowball pays the smallest balance first for quick wins; avalanche pays the highest "
            "rate first and costs the least interest. Either works if you stick with it.",
            "<strong>Each month has four pages:</strong> balances, a payment log, weekly check-ins and a journal prompt.",
            "<strong>Colour the countdown</strong> as you go: each block is 1% of what you owed when you started.",
            "<strong>When a debt is gone,</strong> add its payment to the next one on your list, and log the date on Milestones.",
        ], ["Start any month of any year: nothing is dated.", "Write balances from your statements, not from memory.",
            "Missed a month? Skip it and carry on. The journal works with gaps."]),
        page("Why I'm <em>doing this</em>", "", f'''
          <div class="g2">{box("Total I owe today", 30)}{box("Date I'm starting", 30)}</div>
          {lined("The reason I'm paying this off")}
          <div class="g2">{box("The date I'm aiming for", 30, tint=True)}{box("What I'll do with the money after", 30)}</div>
          {lined("A note to the future me who's debt-free")}'''),
        page("My <em>debts</em>", "Update this page when a balance or rate changes", f'''
          {table(["Debt", "Lender", "Balance", "APR %", "Minimum", "Due day"], 12, ["22%", "20%", "", "11%", "", "11%"], total="Total", cls="t34")}
          <div class="g2" style="margin-top:12px">{box("Total minimum payments", 26)}{box("Extra I can pay each month", 26, tint=True)}</div>
          {lined("Accounts to close or freeze once paid")}'''),
        page("My payoff <em>order</em>", "", f'''
          <div class="g2"><div class="box"><div class="lbl">Snowball</div><p style="margin:4px 0 0;font-size:9.5pt">Smallest balance
          first. Quick wins keep you going.</p></div><div class="box"><div class="lbl">Avalanche</div><p style="margin:4px 0 0;font-size:9.5pt">
          Highest interest rate first. Costs the least overall.</p></div></div>
          <h3>I'm using: &nbsp;&#9744; Snowball &nbsp;&nbsp; &#9744; Avalanche &nbsp;&nbsp; &#9744; My own order</h3>
          {table(["#", "Debt", "Balance", "Payment now", "Payment once the debt above is gone", "Paid off on"], 10,
                 ["6%", "24%", "14%", "14%", "", "14%"], cls="t34")}
          <p class="note">Rolling payments: when debt #1 is paid off, add its whole payment to debt #2, and so on. The payment
          grows each time, like a snowball.</p>'''),
        page("Debt-free <em>countdown</em>", "Each block = 1% of what I owed at the start", f'''
          <div style="flex:1;display:flex;align-items:center;justify-content:center">{blocks_svg()}</div>
          {boxes(["Starting total", "Each block is worth", "Blocks coloured"], 20)}'''),
        page("<em>Milestones</em>", "Celebrate cheaply: the point is to notice", f'''
          {table(["Milestone", "Date reached", "How I'll celebrate (free or almost)"], 10, ["30%", "18%", ""], cls="t34")}
          {lined("Debts paid off, in order")}'''),
        page("Find extra <em>money</em>", "Every dollar found goes on the debt at the top of your list", f'''
          <div class="g2"><div>{table(["Cut or cancel", "Saves / month"], 10, ["70%", ""])}</div>
            <div>{table(["Sell", "Raised"], 10, ["70%", ""])}</div></div>
          <h3>Extra income ideas</h3>{table(["Idea", "Expected", "Done?"], 6, ["60%", "", "14%"])}
          {lined("Bills to call about (a lower rate, a better plan)")}'''),
    ]
    for m in range(1, 13):
        pages += _debt_month(m)
    pages += [
        page("<em>Debt-free</em>", "Fill this in on the day", f'''
          <div class="g3">{box("Debt-free on", 34, tint=True)}{box("Total paid", 34)}{box("Months it took", 34)}</div>
          {lined("How it feels")}{lined("A letter to the person who started this journal")}'''),
        page("Looking <em>back</em>", "", f'''
          {table(["Month", "Total debt", "Paid that month"], 12, ["30%", "", ""], cls="t34")}
          <div class="g2" style="margin-top:10px">{box("What I'd tell someone starting today", 80)}{box("What I'll do next: saving, investing, giving", 80, tint=True)}</div>'''),
    ]
    return pages


# =============================================================================================== 52-Week Savings Log
CLASSIC = list(range(1, 53))


def _strip(week: int) -> str:
    cells = "".join(f'<div style="height:12px;border:1px solid {"#0b1d13" if i + 1 == week else "#c9c3b3"};'
                    f'{"background:#2fbf71;" if i + 1 == week else ""}border-radius:2px"></div>' for i in range(52))
    return (f'<div style="display:grid;grid-template-columns:repeat(52,1fr);gap:2px;margin:2px 0 10px">{cells}</div>')


def _week(n: int) -> str:
    days = "".join(f'<div class="box" style="padding:4px 6px;text-align:center"><div class="lbl">{d}</div>'
                   f'<span class="cb"></span></div>' for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))
    return page(f"Week <em>{n}</em>", f"of 52 &middot; dates: ______ to ______", f'''
      {_strip(n)}
      <div class="g4">{box("Classic amount", 22)}{box("My amount this week", 22)}{box("Saved", 22)}{box("Running total", 22, tint=True)}</div>
      <h3>Where this week's money came from</h3>{table(["Skipped, cut, sold or earned", "Amount"], 5, ["78%", ""])}
      <h3>No-spend days</h3><div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px">{days}</div>
      <div class="g2" style="margin-top:10px">{box("A win", 46)}{box("Next week I'll", 46)}</div>
      {lined("Notes")}''')


def _quarter(q: int) -> str:
    w0 = (q - 1) * 13 + 1
    return page(f"Quarter <em>{q}</em> review", f"Weeks {w0} to {w0 + 12}", f'''
      <div class="g3">{box("Saved this quarter", 30)}{box("Total so far", 30, tint=True)}{box("Weeks I hit my amount", 30)}</div>
      {table(["Week", "Planned", "Saved", "Week", "Planned", "Saved"], 7, ["10%", "", "", "10%", "", ""], cls="t30")}
      <div class="g2" style="margin-top:10px;flex:1">{box("What made saving easier", 90)}{box("What got in the way", 90)}</div>
      {lined("Plan for the next 13 weeks", .7)}''')


def savings_log() -> list[str]:
    plans = "".join(f"<tr><td class='c'><strong>{w}</strong></td><td class='r'>${w}</td><td class='r'>${sum(CLASSIC[:w]):,}</td>"
                    f"<td class='r'>${53 - w}</td><td class='r'>${sum(CLASSIC[::-1][:w]):,}</td><td></td></tr>" for w in range(1, 27))
    plans2 = "".join(f"<tr><td class='c'><strong>{w}</strong></td><td class='r'>${w}</td><td class='r'>${sum(CLASSIC[:w]):,}</td>"
                     f"<td class='r'>${53 - w}</td><td class='r'>${sum(CLASSIC[::-1][:w]):,}</td><td></td></tr>" for w in range(27, 53))
    head = ("<tr><th class='c' style='width:9%'>Week</th><th class='r'>Classic</th><th class='r'>Total</th><th class='r'>Reverse</th>"
            "<th class='r'>Total</th><th>My amount</th></tr>")
    circles = "".join(f'<div class="tile" style="font-size:9pt">{w}</div>' for w in range(1, 53))
    pages = [
        title_page("Money Made Simple", '52-Week <em style="font-style:normal;color:var(--green-d)">Savings</em> Log',
                   "One page a week for a year of saving. Classic, reverse or your own amounts.",
                   '<div style="display:grid;grid-template-columns:repeat(13,22px);gap:5px">' + "".join(
                       f'<div style="width:22px;height:22px;border-radius:50%;border:2px solid #0b1d13;'
                       f'{"background:#2fbf71;" if i in (0, 1, 2, 3, 4, 5, 6, 14, 15, 28) else ""}"></div>' for i in range(52)) + "</div>"),
        "COPYRIGHT",
        how_page("How to use this <em>log</em>", [
            "<strong>Pick a plan.</strong> Classic: $1 in week 1, $2 in week 2, up to $52 in week 52 ($1,378 in a year). "
            "Reverse: start at $52 and finish at $1 (the same $1,378, hardest weeks first, before the holidays). "
            "Or choose your own weekly amount.",
            "<strong>Write your why and your goal</strong> on the next page.",
            "<strong>Each week has its own page:</strong> what you planned, what you saved, where the money came from, "
            "your no-spend days and one win. The strip at the top shows where you are in the year.",
            "<strong>Colour a circle</strong> on the year chart every week you save.",
            "<strong>Every 13 weeks</strong> there's a quarter review. Adjust your amount if you need to and keep going.",
        ], ["Start any week of any year: nothing is dated.", "Move the money the same day you write it down, ideally to a separate savings account.",
            "Missed a week? Double up next week, or just carry on. Finishing matters more than being perfect."]),
        page("My <em>why</em>", "", f'''
          <div class="g3">{box("I'm saving for", 30)}{box("My goal", 30, tint=True)}{box("Starting week", 30)}</div>
          <h3>My plan: &nbsp;&#9744; Classic ($1,378) &nbsp; &#9744; Reverse ($1,378) &nbsp; &#9744; $____ a week &nbsp; &#9744; My own amounts</h3>
          {lined("Why this matters to me")}
          <div class="g2">{box("Where the money will live", 30)}{box("My reward at week 52 (small!)", 30)}</div>'''),
        page("Weekly <em>amounts</em>", "Weeks 1 to 26", f'<table class="t26">{head}{plans}</table>'),
        page("Weekly <em>amounts</em>", "Weeks 27 to 52", f'<table class="t26">{head}{plans2}</table>'
             '<p class="note">Classic and reverse both add up to $1,378. Use the last column for your own plan.</p>'),
        page("The year at a <em>glance</em>", "Colour one circle each week you save", f'''
          <div class="tiles" style="grid-template-columns:repeat(8,1fr);flex:none">{circles}</div>
          {boxes(["Weeks done", "Total saved", "Goal"], 22)}'''),
    ]
    for w in range(1, 53):
        pages.append(_week(w))
        if w % 13 == 0:
            pages.append(_quarter(w // 13))
    pages += [
        page("Year in <em>review</em>", "", f'''
          <div class="g3">{box("Total saved", 34, tint=True)}{box("Weeks completed", 34)}{box("Best week", 34)}</div>
          {lined("What saving every week taught me")}
          <div class="g2">{box("Next year's goal", 40)}{box("Next year's plan", 40)}</div>'''),
    ]
    return pages
