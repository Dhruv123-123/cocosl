"""Undated digital budget planner for GoodNotes, Notability and other PDF note apps: hyperlinked tabs on every page.

Scouting's competitor-product-gaps.md (PR #2): hyperlinked digital planners are the top seller among digital planners
on Etsy. This one is built from the same pages as the 2027 planner, but undated (write in the dates, start any month),
with a tab bar down the right edge of every page (Home, Year, Goals, Bills, Save, Debt, Jan to Dec, Notes) and, on
each month's pages, links between that month's calendar, budget and spending log. Two PDFs: iPad portrait (3:4) and
landscape (4:3). Chromium keeps <a href="#id"> links as PDF link annotations; `link_report()` checks every one.

It's a planner (labels and blank pages, a few lines on how to use the tabs), so it's fine under Etsy's AI-guide rule.
"""
from __future__ import annotations

import html as _html
from pathlib import Path

import planner_2027 as P
from printables import MONTHS, page, table
from printables_more import box, boxes, lined

HERE = Path(__file__).resolve().parent
# 3:4 and 4:3. Landscape keeps the Letter height so every page from the paper planner fits without shrinking.
SIZES = {"Portrait": ("9in", "12in", "9in 12in"), "Landscape": ("14.667in", "11in", "14.667in 11in")}
TABS = ([("home", "Home"), ("year", "Year"), ("goals", "Goals"), ("bills", "Bills"), ("savings", "Save"), ("debt", "Debt")]
        + [(f"m{m}", MONTHS[m - 1][:3]) for m in range(1, 13)] + [("notes", "Notes")])

CSS = """
  .dp{ padding-right:1.2in; }
  .dp .foot{ right:1.2in; }
  .tabs{ position:absolute; top:.35in; bottom:.35in; right:0; width:.82in; display:flex; flex-direction:column; gap:4px; }
  .tabs a{ flex:1; display:flex; align-items:center; justify-content:center; border-radius:10px 0 0 10px; background:var(--tint);
    color:var(--ink); text-decoration:none; font-weight:800; font-size:8.5pt; letter-spacing:.02em; }
  .tabs a.on{ background:var(--green-d); color:#fff; }
  .tabs a.m{ background:#f4f1e8; }
  .tabs a.m.on{ background:var(--green-d); }
  .sub{ display:flex; gap:6px; } .sub a{ font-size:8.5pt; font-weight:800; color:var(--green-d); text-decoration:none;
    border:1.5px solid var(--green-d); border-radius:999px; padding:2px 9px; } .sub a.on{ background:var(--green-d); color:#fff; }
  .homegrid{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
  .homegrid a{ display:block; border:2px solid var(--ink); border-radius:12px; padding:14px 10px; text-align:center; font-weight:800;
    font-size:12pt; color:var(--ink); text-decoration:none; }
  .homegrid a.mo{ background:var(--tint); border-color:var(--green-d); }
  .ucal{ flex:1; display:grid; grid-template-columns:repeat(7,1fr); gap:0; border:1.5px solid var(--ink); }
  .ucal div{ border:1px solid var(--line); padding:3px 5px; font-size:7pt; color:#9aa59e; }
"""


def _tabs(active: str) -> str:
    return '<nav class="tabs">' + "".join(
        f'<a href="#{t}" class="{"m " if t.startswith("m") else ""}{"on" if t == active else ""}">{lbl}</a>' for t, lbl in TABS) + "</nav>"


def _sub(m: int, on: str) -> str:
    links = [(f"m{m}", "Calendar"), (f"m{m}-budget", "Budget"), (f"m{m}-log", "Spending")]
    return '<div class="sub">' + "".join(f'<a href="#{i}" class="{"on" if i == on else ""}">{t}</a>' for i, t in links) + "</div>"


def _meta(html_page: str, new: str) -> str:
    """Swap the page's top-right meta text for links."""
    i = html_page.index('<div class="meta">')
    j = html_page.index("</div>", i)
    return html_page[:i] + f'<div class="meta">{new}' + html_page[j:]


def cover() -> str:
    return f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:0 .2in">
      <div class="kick" style="font-size:11pt">Money Made Simple</div>
      <div style="font-size:54pt;font-weight:900;letter-spacing:-.03em;line-height:.95">Digital Budget <em style="font-style:normal;color:var(--green-d)">Planner</em></div>
      <div style="font-size:13pt;color:var(--muted)">Undated &middot; 12 months &middot; tap a tab to jump to any page</div>
      <div><a href="#home" style="display:inline-block;background:var(--ink);color:#fff;text-decoration:none;font-weight:800;
        font-size:13pt;border-radius:999px;padding:10px 22px">Open the planner</a></div>
      <div class="box" style="width:4.2in;margin-top:20px"><div class="lbl">This planner belongs to</div><div style="height:26px"></div></div></div>
      <div class="foot"><span>&copy; Money Made Simple &middot; for personal use only, please don't resell or share the file</span><span>moneymadesimple</span></div>'''


def home() -> str:
    fronts = [("year", "Year at a glance"), ("goals", "Goals"), ("bills", "Yearly bills"), ("paychecks", "Paychecks"),
              ("savings", "Savings goals"), ("debt", "Debt payoff"), ("how", "How to use"), ("notes", "Notes")]
    a = "".join(f'<a href="#{i}">{t}</a>' for i, t in fronts)
    mo = "".join(f'<a class="mo" href="#m{m}">{MONTHS[m - 1]}</a>' for m in range(1, 13))
    return page("<em>Home</em>", "Tap any box", f'''
      <h3>Start of the year</h3><div class="homegrid">{a}</div>
      <h3 style="margin-top:16px">Months</h3><div class="homegrid">{mo}</div>
      <p class="note" style="margin-top:auto">The tabs on the right work on every page. "Home" brings you back here.</p>''',
                kicker="Money Made Simple")


def how_to() -> str:
    steps = [
        "<strong>Import it</strong> into GoodNotes, Notability, Noteshelf or any app that lets you write on PDFs (open the PDF and choose your app, or import it from Files).",
        "<strong>Tap a tab</strong> on the right to jump to a section or a month. In GoodNotes, links work in read-only mode; tap the pen icon to switch back to writing.",
        "<strong>It's undated:</strong> write the year and the dates in, and start with any month.",
        "<strong>Each month</strong> has a calendar, a budget and a spending log, linked at the top of each page.",
        "<strong>Need more pages?</strong> Duplicate a page in your app; the tabs keep working on the copy.",
    ]
    lis = "".join(f'<li style="margin-bottom:9px">{s}</li>' for s in steps)
    return page("How to use your <em>digital planner</em>", "Start here", f'''
      <ol style="font-size:11pt;padding-left:20px">{lis}</ol>
      <div class="box" style="margin-top:auto"><div class="lbl">Good to know</div><p style="margin:4px 0 0;font-size:9.5pt">An organising
      tool, not financial advice. Digital download: nothing is shipped. Questions? Message the shop through Etsy.</p></div>''')


def year_page() -> str:
    cells = "".join(f'<a href="#m{m}" class="box" style="text-decoration:none;color:var(--ink);display:flex;flex-direction:column">'
                    f'<div style="font-weight:800;font-size:10pt">{MONTHS[m - 1]}</div><div class="lines" style="flex:1"></div></a>'
                    for m in range(1, 13))
    return page("Year at a <em>glance</em>", "Year: ________", f'''
      <div style="display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:1fr;gap:8px;flex:1">{cells}</div>
      <p class="note">Tap a month to open it. Write the big dates for each month here: birthdays, renewals, paydays that move.</p>''')


def goals_page() -> str:
    g = "".join(f'''<div class="box" style="display:flex;gap:10px"><div style="flex:3"><div class="lbl">Goal {i}</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">Amount</div><div class="line"></div></div><div style="flex:1"><div class="lbl">By</div><div class="line"></div></div>
        <div style="flex:1"><div class="lbl">Per month</div><div class="line"></div></div></div>''' for i in (1, 2, 3))
    return page("My money <em>goals</em>", "Year: ________", f'''
      <div class="g3">{box("This year I want to", 80)}{box("I'll stop", 80)}{box("I'll start", 80)}</div>
      <h3>Three goals</h3><div style="display:flex;flex-direction:column;gap:8px">{g}</div>
      {lined("By the end of the year, my money life looks like")}''')


def _undate(html_page: str, title_from: str, title_to: str, meta: str) -> str:
    return _meta(html_page.replace(title_from, title_to), meta)


def bills_page() -> str:
    return _undate(P.annual_bills_page(0), "Yearly bills + <em>renewals</em>", "Yearly bills + <em>renewals</em>", "Year: ________")


def paycheck_page() -> str:
    return _undate(P.paycheck_page(0), "<em>0</em> paychecks", "<em>Paychecks</em>", "Every two weeks? 26 rows. Monthly? Use 12.")


def savings_page() -> str:
    return _undate(P.savings_page(0), "<em>0</em> savings goals", "Savings <em>goals</em>", "Year: ________")


def debt_page() -> str:
    p = P.debt_page(0).replace("Jan 1", "Start").replace("Total debt Dec 31", "Total debt at year end").replace("Paid off in 0", "Paid off this year")
    return _undate(p, "<em>0</em> debt payoff", "Debt <em>payoff</em>", "Write each balance at month end")


def month_calendar(m: int) -> str:
    head = "".join('<div style="background:var(--tint);height:22px"></div>' for _ in range(7))
    cells = "".join("<div></div>" for _ in range(42))
    return page(f"<em>{MONTHS[m - 1]}</em>", _sub(m, f"m{m}"), f'''
      <div class="ucal" style="grid-template-rows:22px repeat(6,1fr)">{head}{cells}</div>
      <p class="note" style="margin:4px 0">Write the days of the week in the top row and the dates in the corners.</p>
      <div class="g3">{box("Paydays", 34)}{box("Bills due", 34)}{box("This month's focus", 34, tint=True)}</div>''')


def month_budget(m: int) -> str:
    return _meta(P.month_budget(0, m), _sub(m, f"m{m}-budget"))


def month_log(m: int) -> str:
    return _meta(P.month_log(0, m), _sub(m, f"m{m}-log"))


def pages() -> list[tuple[str, str, str]]:
    """(anchor id, tab to highlight, page HTML) in order."""
    out = [("cover", "", cover()), ("home", "home", home()), ("how", "home", how_to()), ("year", "year", year_page()),
           ("goals", "goals", goals_page()), ("bills", "bills", bills_page()), ("paychecks", "bills", paycheck_page()),
           ("savings", "savings", savings_page()), ("debt", "debt", debt_page())]
    for m in range(1, 13):
        out += [(f"m{m}", f"m{m}", month_calendar(m)), (f"m{m}-budget", f"m{m}", month_budget(m)), (f"m{m}-log", f"m{m}", month_log(m))]
    out += [("notes", "notes", page("<em>Notes</em>", "", '<div class="lines"></div>')),
            ("notes-2", "notes", page("<em>Notes</em>", "", '<div class="lines"></div>'))]
    return out


def build(variant: str = "Portrait") -> list[str]:
    """Page bodies, for page counts and checks (tabs included)."""
    return [(_tabs(tab) if pid != "cover" else "") + body for pid, tab, body in pages()]


def html(variant: str, title: str = "Digital Budget Planner") -> str:
    w, h, size = SIZES[variant]
    css = (HERE / "printables.css").read_text().replace("--w:8.5in; --h:11in;", f"--w:{w}; --h:{h};")
    body = "".join(f'<section class="page{" dp" if pid != "cover" else ""}" id="{pid}">{"" if pid == "cover" else _tabs(tab)}{p}</section>\n'
                   for pid, tab, p in pages())
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{_html.escape(title)}</title>'
            f'<style>@page{{size:{size};margin:0}}\n{css}\n{CSS}</style></head><body>{body}</body></html>')


def link_report(pdf: Path) -> dict:
    """Count link annotations per page and check each points inside the file."""
    from pypdf import PdfReader
    r = PdfReader(str(pdf))
    dests = set(r.named_destinations)
    per_page, broken = [], []
    for i, pg in enumerate(r.pages):
        n = 0
        for a in pg.get("/Annots") or []:
            a = a.get_object()
            if a.get("/Subtype") != "/Link":
                continue
            n += 1
            d = a.get("/Dest")
            act = a.get("/A")
            if d is None and act is not None:
                act = act.get_object()
                d = act.get("/D")
                if act.get("/S") == "/URI":
                    broken.append((i + 1, str(act.get("/URI"))))
                    continue
            if isinstance(d, str) and d not in dests:
                broken.append((i + 1, d))
        per_page.append(n)
    return dict(pages=len(r.pages), links=per_page, broken=broken)
