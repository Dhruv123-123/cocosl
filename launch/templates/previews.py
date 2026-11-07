"""HTML for screenshots, store covers and Start Here PDFs.

Sheet screenshots are drawn from the real workbook after LibreOffice recalculates it (values, fills, fonts,
column widths), so they show exactly what the buyer gets. Notion screenshots are drawn from the template spec
with every formula worked out on the example data (notion_spec.evaluate). Charts aren't drawn.
"""
from __future__ import annotations

import html
import re
from datetime import date, datetime

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries

import notion_spec as N

W, H = 1600, 1000
FONT = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
E = html.escape


# ---- spreadsheet screenshots -----------------------------------------------------------------------------
def fmt_cell(v, nf: str) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (datetime, date)):
        if "mmmm" in nf:
            return v.strftime("%B %Y")
        if "mmm yyyy" in nf:
            return v.strftime("%b %Y")
        return f"{v.strftime('%b')} {v.day}, {v.year}"
    if isinstance(v, (int, float)):
        if '"%"' in nf:
            return f"{v:.1f}%"
        if "%" in nf:
            return f"{v * 100:.0f}%"
        if "$" in nf:
            dec = 2 if ".00" in nf else 0
            s = f"${abs(v):,.{dec}f}"
            return "-" + s if v < 0 else s
        if nf == "0.0":
            return f"{v:.1f}"
        if nf == "0" or float(v).is_integer():
            return f"{round(v):,}" if abs(v) >= 10000 else str(round(v))
        return f"{v:,.2f}"
    return str(v)


def _rgb(color) -> str | None:
    try:
        rgb = color.rgb
    except AttributeError:
        return None
    if isinstance(rgb, str) and len(rgb) >= 6 and rgb not in ("00000000",):
        return "#" + rgb[-6:]
    return None


def sheet_html(styled: str, values: str, sheet: str, rng: str, title: str) -> str:
    ws = openpyxl.load_workbook(styled)[sheet]
    wv = openpyxl.load_workbook(values, data_only=True)
    vs = wv[sheet]
    c1, r1, c2, r2 = range_boundaries(rng)
    cols = [c for c in range(c1, c2 + 1) if not ws.column_dimensions[get_column_letter(c)].hidden]
    widths = {c: int((ws.column_dimensions[get_column_letter(c)].width or 8.43) * 7.2 + 6) for c in cols}
    heights = {r: int((ws.row_dimensions[r].height or 15.75) * 1.33) for r in range(1, r2 + 1)}
    allc = [1] + cols if c1 > 1 else cols
    widths.setdefault(1, int((ws.column_dimensions["A"].width or 2) * 7.2 + 6))
    x, xs = 46, {}
    for c in allc:
        xs[c] = x
        x += widths[c]
    total_w = x
    cells, y, ys = [], 26, {}
    for r in range(1, r2 + 1):
        ys[r] = y
        y += heights[r]
    total_h = y
    head = "".join(f'<div class="ch" style="left:{xs[c]}px;width:{widths[c]}px">{get_column_letter(c)}</div>' for c in allc)
    rows = "".join(f'<div class="rh" style="top:{ys[r]}px;height:{heights[r]}px">{r}</div>' for r in range(1, r2 + 1))
    for r in range(1, r2 + 1):
        for c in allc:
            sc, vc = ws.cell(r, c), vs.cell(r, c)
            v = vc.value if vc.value is not None else (sc.value if not str(sc.value or "").startswith("=") else None)
            fill = _rgb(sc.fill.fgColor) if sc.fill and sc.fill.fill_type == "solid" else None
            text = fmt_cell(v, sc.number_format or "General")
            if not text and not fill:
                continue
            f = sc.font
            color = _rgb(f.color) if f and f.color is not None else None
            num = isinstance(v, (int, float)) and not isinstance(v, bool)
            wrap = bool(sc.alignment and sc.alignment.wrap_text)
            style = [f"left:{xs[c]}px", f"top:{ys[r]}px", f"height:{heights[r]}px", f"min-width:{widths[c]}px"]
            nxt = allc[allc.index(c) + 1] if allc.index(c) + 1 < len(allc) else None
            blocked = nxt is not None and (vs.cell(r, nxt).value not in (None, "") or ws.cell(r, nxt).fill.fill_type == "solid")
            if fill or num or wrap or blocked:
                style.append(f"width:{widths[c]}px;overflow:hidden")
            if fill:
                style.append(f"background:{fill}")
            if color and color.lower() != "#000000":
                style.append(f"color:{color}")
            if f and f.bold:
                style.append("font-weight:700")
            if f and f.italic:
                style.append("font-style:italic")
            if f and f.sz:
                style.append(f"font-size:{min(f.sz, 20) * 1.3:.0f}px")
            if num:
                style.append("justify-content:flex-end")
            if wrap:
                style.append("white-space:normal;line-height:1.1;overflow:hidden")
            cells.append(f'<div class="c" style="{";".join(style)}">{E(text)}</div>')
    tabs = "".join(f'<span class="{"on" if n == sheet else ""}">{E(n)}</span>' for n in ws.parent.sheetnames)
    scale = min(1.0, (W - 40) / total_w, (H - 150) / total_h)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;width:{W}px;height:{H}px;background:#e9e5da;font-family:{FONT};overflow:hidden}}
.win{{position:absolute;left:20px;top:20px;right:20px;bottom:20px;background:#fff;border-radius:14px;overflow:hidden;
box-shadow:0 20px 50px rgba(11,29,19,.25)}}
.bar{{height:58px;display:flex;align-items:center;gap:14px;padding:0 22px;border-bottom:1px solid #e3e3e3}}
.ico{{width:30px;height:36px;border-radius:4px;background:#1e8a50;position:relative}}
.ico:after{{content:"";position:absolute;left:7px;right:7px;top:10px;bottom:9px;border:2px solid #fff;border-radius:1px;
background:linear-gradient(#fff,#fff) 50% 0/2px 100% no-repeat,linear-gradient(#fff,#fff) 0 50%/100% 2px no-repeat}}
.bar b{{font-size:20px;color:#0b1d13}} .bar i{{font-style:normal;color:#5b6a61;font-size:15px;margin-left:auto}}
.grid{{position:absolute;top:58px;left:0;transform-origin:0 0;transform:scale({scale:.3f});width:{total_w}px;height:{total_h}px}}
.ch,.rh{{position:absolute;background:#f3f3f1;color:#777;font-size:12px;display:flex;align-items:center;justify-content:center}}
.ch{{top:0;height:26px;border-right:1px solid #ddd;border-bottom:1px solid #ccc}}
.rh{{left:0;width:46px;border-bottom:1px solid #ddd;border-right:1px solid #ccc}}
.c{{position:absolute;display:flex;align-items:center;padding:0 5px;white-space:nowrap;font-size:13px;color:#0b1d13;
border-bottom:1px solid #eeeae0}}
.tabs{{position:absolute;left:0;right:0;bottom:0;height:44px;background:#f6f5f1;border-top:1px solid #ddd;display:flex;gap:4px;
padding:0 16px;align-items:stretch}}
.tabs span{{padding:0 18px;display:flex;align-items:center;font-size:14px;color:#5b6a61}}
.tabs .on{{background:#fff;color:#1e8a50;font-weight:700;border-bottom:3px solid #1e8a50}}
</style></head><body><div class="win"><div class="bar"><div class="ico"></div><b>{E(title)}</b>
<i>Example data shown &middot; works in Google Sheets, Excel and Numbers</i></div>
<div class="grid">{head}{rows}{"".join(cells)}</div><div class="tabs">{tabs}</div></div></body></html>"""


# ---- Notion-style previews -----------------------------------------------------------------------------
PILL = {"green": ("#dbeddb", "#1c3829"), "blue": ("#d3e5ef", "#183347"), "purple": ("#e8deee", "#412454"),
        "yellow": ("#fdecc8", "#402c1b"), "red": ("#ffe2dd", "#5d1715"), "default": ("#e3e2e0", "#32302c")}


def _val(db: dict, name: str, v) -> str:
    kind, cfg = next((k, c) for n, k, c in db["props"] if n == name) if any(p[0] == name for p in db["props"]) else ("x", {})
    if kind == "select":
        bg, fg = PILL[N.GROUP_COLORS.get(v, "default")]
        return f'<span class="pill" style="background:{bg};color:{fg}">{E(str(v))}</span>'
    if kind == "relation" or isinstance(v, list):
        return "".join(f'<span class="rel">📄 {E(x["Name"])}</span>' for x in v)
    if kind == "checkbox":
        return '<span class="cb on">✓</span>' if v else '<span class="cb"></span>'
    if isinstance(v, (date, datetime)):
        return f"{v.strftime('%B')} {v.day}, {v.year}"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if cfg.get("format") == "dollar":
            return ("-" if v < 0 else "") + f"${abs(v):,.2f}"
        return f"{v:g}"
    if isinstance(v, str) and v[:1] in "■□":
        n = v.count("■")
        pct = v.split(" ")[-1]
        return (f'<span class="bar"><span style="width:{n * 10}%"></span></span><span class="pct">{E(pct)}</span>')
    return E(str(v))


def _icon(kind: str) -> str:
    return {"title": "Aa", "number": "#", "select": "◉", "date": "▦", "relation": "↗", "formula": "Σ",
            "checkbox": "☑", "rich_text": "≡"}.get(kind, "·")


def table(db: dict, rows: list[dict], cols: list[str], view: str, group: str | None = None, limit: int = 12,
          sums: tuple = ()) -> str:
    kinds = {n: k for n, k, _ in db["props"]}
    head = "".join(f'<th><span class="pi">{_icon(kinds.get(c, "relation"))}</span>{E(c)}</th>' for c in cols)

    def body(rs):
        return "".join("<tr>" + "".join(f'<td class="{"t" if kinds.get(c) == "title" else ""}">{_val(db, c, r.get(c))}</td>'
                                        for c in cols) + "</tr>" for rs_ in [rs] for r in rs_)

    def foot(rs):
        if not sums:
            return ""
        cells = []
        for c in cols:
            if c in sums:
                total = sum(r.get(c) or 0 for r in rs)
                cells.append(f'<td class="sum"><span>Sum</span> {_val(db, c, round(total, 2))}</td>')
            else:
                cells.append("<td></td>")
        return f'<tr class="foot">{"".join(cells)}</tr>'

    if group:
        parts, n = [], 0
        for g in dict.fromkeys(r.get(group) for r in rows):
            rs = [r for r in rows if r.get(group) == g]
            take = rs[:max(0, limit - n)]
            n += len(take)
            if not take:
                break
            parts.append(f'<tr class="grp"><td colspan="{len(cols)}">{_val(db, group, g)} <span class="cnt">{len(rs)}</span></td></tr>'
                         + body(take) + foot(rs))
        inner = "".join(parts)
    else:
        inner = body(rows[:limit]) + foot(rows)
    return (f'<div class="dbt"><span class="dbi">{db["icon"]}</span>{E(db["title"])}</div>'
            f'<div class="tabs"><span class="on">▤ {E(view)}</span></div>'
            f'<table><thead><tr>{head}</tr></thead><tbody>{inner}</tbody></table>')


def gallery(db: dict, rows: list[dict], fields: list[str], view: str) -> str:
    cards = "".join(f'<div class="card"><div class="ct">{E(r["Name"])}</div>' +
                    "".join(f'<div class="cf"><span>{E(f)}</span>{_val(db, f, r.get(f))}</div>' for f in fields) + "</div>"
                    for r in rows)
    return (f'<div class="dbt"><span class="dbi">{db["icon"]}</span>{E(db["title"])}</div>'
            f'<div class="tabs"><span class="on">▦ {E(view)}</span></div><div class="gal">{cards}</div>')


def blocks(items: list[tuple], links_label=True) -> str:
    out = []
    for it in items:
        k = it[0]
        if k == "callout":
            out.append(f'<div class="callout"><span>{it[1]}</span><div>{E(it[2])}</div></div>')
        elif k == "h2":
            out.append(f"<h2>{E(it[1])}</h2>")
        elif k == "p":
            out.append(f"<p>{E(it[1])}</p>")
        elif k == "small":
            out.append(f'<p class="small">{E(it[1])}</p>')
        elif k == "todo":
            out.append(f'<div class="todo"><span class="cb"></span>{E(it[1])}</div>')
        elif k == "bullet":
            out.append(f'<div class="todo">•&nbsp; {E(it[1])}</div>')
        elif k == "link":
            out.append(f'<p class="lnk">→ {E(it[1])}</p>')
        elif k == "divider":
            out.append("<hr>")
        elif k == "page":
            out.append(f'<div class="child">{it[1]} <u>{E(it[2])}</u></div>')
    return "".join(out)


def notion_page(t: dict, content: str, breadcrumb: str | None = None, head: bool = True) -> str:
    top = (f'<div class="icon">{t["icon"]}</div><h1>{E(t["name"].replace(" (free)", ""))}</h1>' if head else "")
    crumb = E(breadcrumb or t["name"].replace(" (free)", ""))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;width:{W}px;height:{H}px;background:#e9e5da;font-family:{FONT};overflow:hidden;color:#37352f}}
.win{{position:absolute;left:20px;top:20px;right:20px;bottom:20px;background:#fff;border-radius:14px;overflow:hidden;
box-shadow:0 20px 50px rgba(11,29,19,.25)}}
.top{{height:46px;border-bottom:1px solid #eee;display:flex;align-items:center;padding:0 20px;font-size:15px;color:#5f5e5b;gap:10px}}
.top i{{margin-left:auto;font-style:normal;font-size:13px;color:#9b9a97}}
.pg{{padding:30px 90px 0;}}
.icon{{font-size:64px;line-height:1}} h1{{font-size:40px;margin:14px 0 18px;font-weight:700;color:#191919}}
h2{{font-size:24px;margin:26px 0 8px;color:#191919}} p{{font-size:16px;margin:6px 0;line-height:1.5}}
.small{{font-size:13px;color:#9b9a97;font-style:italic}} .lnk{{font-weight:700;text-decoration:underline}}
.callout{{display:flex;gap:12px;background:#f1f1ef;border-radius:6px;padding:16px 18px;font-size:16px;line-height:1.5;margin:10px 0}}
.callout span{{font-size:22px}}
.todo{{display:flex;gap:10px;align-items:center;font-size:16px;margin:6px 0}}
.cb{{display:inline-block;width:16px;height:16px;border:1.5px solid #9b9a97;border-radius:3px;flex:none;font-size:12px;
text-align:center;line-height:14px}} .cb.on{{background:#2383e2;border-color:#2383e2;color:#fff}}
hr{{border:0;border-top:1px solid #e9e9e7;margin:18px 0}}
.child{{font-size:17px;margin:8px 0;font-weight:600}} .child u{{text-decoration-color:#ccc}}
.dbt{{font-size:20px;font-weight:700;margin:18px 0 6px;color:#191919}} .dbi{{margin-right:8px}}
.tabs{{display:flex;gap:14px;border-bottom:1px solid #e9e9e7;font-size:14px;color:#9b9a97;padding-bottom:6px}}
.tabs .on{{color:#37352f;font-weight:600;border-bottom:2px solid #37352f;padding-bottom:5px;margin-bottom:-7px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th{{text-align:left;color:#787774;font-weight:500;padding:7px 8px;border-bottom:1px solid #e9e9e7;border-right:1px solid #f1f1ef;white-space:nowrap}}
.pi{{font-size:11px;color:#a5a4a0;margin-right:6px}}
td{{padding:6px 8px;border-bottom:1px solid #f1f1ef;border-right:1px solid #f1f1ef;white-space:nowrap}}
td.t{{font-weight:600}} .grp td{{border:0;padding-top:12px;font-weight:600}} .cnt{{color:#9b9a97;font-weight:400;margin-left:6px}}
.foot td{{border:0;color:#37352f;font-size:13px}} .sum span{{color:#9b9a97;font-size:11px;text-transform:uppercase}}
.pill{{border-radius:4px;padding:2px 7px;font-size:13px}} .rel{{border-bottom:1px solid #ccc;margin-right:6px}}
.bar{{display:inline-block;width:90px;height:7px;background:#ebebea;border-radius:9px;vertical-align:middle;overflow:hidden}}
.bar span{{display:block;height:100%;background:#2fbf71;border-radius:9px}} .pct{{margin-left:8px;color:#787774;font-size:13px}}
.gal{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:14px}}
.card{{border:1px solid #e9e9e7;border-radius:8px;padding:14px 16px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.ct{{font-weight:700;font-size:16px;margin-bottom:8px}} .cf{{font-size:14px;margin:5px 0;display:flex;gap:10px;align-items:center}}
.cf>span{{color:#9b9a97;width:84px;flex:none;font-size:12px}}
</style></head><body><div class="win"><div class="top">{t["icon"]} {crumb}<i>Template preview with example data</i></div>
<div class="pg">{top}{content}</div></div></body></html>"""


def notion_shots(t: dict, today: date) -> list[tuple[str, str]]:
    """[(label, html)] screenshots for a Notion template."""
    rows = N.evaluate(t, today)
    dbs = {d["key"]: d for d in N.all_dbs(t)}
    L = t["layout"]
    slug = t["slug"]
    if slug == "notion-budget":
        cats = dbs["categories"]
        tx = [r for r in rows["transactions"] if (r["Date"].year, r["Date"].month) == (today.year, today.month)]
        tx.sort(key=lambda r: r["Date"], reverse=True)
        return [
            ("page", notion_page(t, blocks(L[:3]) + table(cats, rows["categories"], ["Name", "Group", "Monthly budget",
                    "This month", "Left", "Used", "Status"], "This month", group="Group", limit=10,
                    sums=("Monthly budget", "This month", "Left")))),
            ("transactions", notion_page(t, blocks(L[4:6]) + table(dbs["transactions"], tx, ["Name", "Date", "Amount",
                    "Category", "Group"], "This month", limit=14, sums=("Amount",)), head=False)),
            ("last-month", notion_page(t, table(cats, rows["categories"], ["Name", "Group", "Monthly budget", "Last month",
                    "Used", "Status"], "This month", limit=15) + blocks(L[7:12]), head=False)),
        ]
    if slug == "notion-debt-payoff":
        d = dbs["debts"]
        av = sorted(rows["debts"], key=lambda r: -r["APR %"])
        sb = sorted(rows["debts"], key=lambda r: r["Balance now"])
        cols = ["Name", "Balance now", "APR %", "Monthly payment", "Debt-free", "Progress"]
        return [
            ("page", notion_page(t, blocks(L[:3]) + table(d, av, cols, "Avalanche (least interest)",
                                                           sums=("Balance now", "Monthly payment")) + blocks(L[4:5]))),
            ("snowball", notion_page(t, table(d, sb, cols + ["Interest this month"], "Snowball (quick wins)",
                                              sums=("Balance now", "Monthly payment", "Interest this month")), head=False)),
            ("payments", notion_page(t, blocks(L[5:7]) + table(dbs["payments"], sorted(rows["payments"], key=lambda r: r["Date"],
                    reverse=True), ["Name", "Date", "Paid", "Interest", "Principal", "Debt"], "All payments",
                    sums=("Paid", "Interest", "Principal")) + blocks(L[8:12]), head=False)),
        ]
    if slug == "notion-savings-goals":
        g = dbs["goals"]
        return [
            ("page", notion_page(t, blocks(L[:3]) + gallery(g, rows["goals"], ["Progress", "Saved", "Per month", "Status"],
                                                             "Goals"))),
            ("plan", notion_page(t, table(g, rows["goals"], ["Name", "Type", "Target", "Saved", "Left", "Target date",
                                                              "Per month"], "Plan", group="Type",
                                          sums=("Target", "Saved", "Left", "Per month")), head=False)),
            ("deposits", notion_page(t, blocks(L[4:6]) + table(dbs["deposits"], sorted(rows["deposits"], key=lambda r: r["Date"],
                    reverse=True), ["Name", "Date", "Amount", "Goal"], "All deposits", limit=10, sums=("Amount",))
                    + blocks(L[7:10]), head=False)),
        ]
    if slug == "notion-money-hq":
        c = dbs["checkins"]
        kids = [("page", ch["icon"], ch["name"]) for ch in t["children"]]
        home = notion_page(t, blocks(L[:2]) + blocks(kids) + blocks(L[3:5]) + table(
            c, sorted(rows["checkins"], key=lambda r: r["Date"], reverse=True),
            ["Name", "Date"] + [p[0] for p in c["props"] if p[1] == "checkbox"] + ["Score"], "Check-ins"))
        return [("home", home)] + [(f"{ch['slug']}", notion_shots(ch, today)[0][1]
                                    .replace(f'{ch["icon"]} {E(ch["name"])}<i>', f'{t["icon"]} Notion Money HQ / {ch["icon"]} {E(ch["name"])}<i>'))
                                   for ch in t["children"]]
    if slug == "notion-money-starter":
        b, g = dbs["starter_budget"], dbs["starter_goal"]
        return [
            ("page", notion_page(t, blocks(L[:3]) + table(b, rows["starter_budget"], ["Name", "Group", "Budget", "Spent",
                                                                                     "Left", "Used"], "Budget",
                                                         sums=("Budget", "Spent", "Left")))),
            ("goal", notion_page(t, blocks(L[4:6]) + table(g, rows["starter_goal"], ["Name", "Target", "Saved", "Progress"],
                                                            "Goal") + blocks(L[7:]), head=False)),
        ]
    raise KeyError(slug)


# ---- covers + Start Here -----------------------------------------------------------------------------------
def cover_html(item: dict, shot: str, w: int, h: int) -> str:
    kind = item["kind"]
    label = {"sheets": "Google Sheets template", "sheets-bundle": "Google Sheets bundle", "notion": "Notion template",
             "notion-bundle": "Notion bundle", "free": "Free Notion template"}[kind]
    price = "FREE" if item["price"] == 0 else f"${item['price']}"
    square = w == h
    name = E(item["name"])
    img = (f'<img src="file://{shot}" style="position:absolute;{"left:60px;right:-120px;bottom:-60px;width:620px" if square else "right:-80px;top:120px;width:780px"};'
           f'transform:rotate(-3deg);border-radius:10px;box-shadow:0 30px 60px rgba(0,0,0,.45)">') if shot else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:{w}px;height:{h}px;background:#0b1d13;color:#f4f1e8;font-family:{FONT};overflow:hidden;position:relative}}
.t{{position:absolute;left:{44 if square else 70}px;top:{44 if square else 0}px;{"" if square else "bottom:0;"}width:{w - 100 if square else 520}px;
display:flex;flex-direction:column;justify-content:center;z-index:2}}
.tag{{color:#f2b134;letter-spacing:.16em;text-transform:uppercase;font-weight:800;font-size:{14 if square else 17}px}}
h1{{font-size:{52 if square else 70}px;line-height:.98;font-weight:900;letter-spacing:-.03em;margin:16px 0 22px}}
.price{{display:inline-block;align-self:flex-start;background:#2fbf71;color:#0b1d13;font-weight:900;border-radius:999px;padding:6px 20px;font-size:{22 if square else 26}px}}
.brand{{position:absolute;left:{44 if square else 70}px;bottom:{26 if square else 40}px;font-weight:800;letter-spacing:.12em;font-size:13px;color:#9fb3a6;z-index:2}}
</style></head><body><div class="t"><div class="tag">{label}</div><h1>{name}</h1><span class="price">{price}</span></div>
{img}{"" if square else '<div class="brand">MONEY MADE SIMPLE</div>'}</body></html>"""


def start_here_html(item: dict, links: list[tuple[str, str]], how: list[str], tips: list[str], nxt: dict | None) -> str:
    def md(s):
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", E(s))

    link_boxes = "".join(
        f'<div class="lk"><div class="ll">{E(label)}</div>' + (
            f'<a href="{E(url)}">{E(url)}</a>' if url and not url.startswith("TODO") else
            '<span class="todo">[link added before launch]</span>') + "</div>" for label, url in links)
    steps = "".join(f"<li>{md(s)}</li>" for s in how)
    tip = "".join(f"<li>{md(s)}</li>" for s in tips)
    nx = ""
    if nxt:
        nx = (f'<div class="next"><b>Next step: {E(nxt["name"])}</b> (${nxt["price"]}). {E(nxt["tagline"])} '
              f'Already bought this one? Reply to your receipt email and we\'ll send a code for the difference.</div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:8.5in 11in;margin:0}} *{{box-sizing:border-box}}
body{{margin:0;font-family:{FONT};color:#0b1d13}} .page{{width:8.5in;height:11in;padding:.7in .75in;position:relative;overflow:hidden}}
.k{{letter-spacing:.16em;text-transform:uppercase;font-weight:800;font-size:9pt;color:#1e8a50}}
h1{{font-size:32pt;line-height:1;margin:8px 0 10px;letter-spacing:-.02em}} .sub{{font-size:12pt;color:#4b5a51;margin:0 0 22px}}
h2{{font-size:14pt;margin:22px 0 8px}}
.lk{{border:2px solid #0b1d13;border-radius:14px;padding:12px 16px;margin:10px 0;background:#eaf6ef}}
.ll{{font-weight:800;font-size:10pt;margin-bottom:4px}} .lk a{{color:#1e8a50;font-weight:700;font-size:11pt;word-break:break-all}}
.todo{{color:#c0392b;font-weight:700}}
ol,ul{{padding-left:20px;font-size:11pt;line-height:1.5}} li{{margin-bottom:5px}}
.next{{margin-top:22px;background:#0b1d13;color:#f4f1e8;border-radius:14px;padding:14px 18px;font-size:10.5pt;line-height:1.45}}
.next b{{color:#2fbf71}}
.foot{{position:absolute;left:.75in;right:.75in;bottom:.45in;font-size:7.5pt;color:#8a958e;line-height:1.4}}
</style></head><body><section class="page"><div class="k">Money Made Simple &middot; Start here</div>
<h1>{E(item["name"])}</h1><p class="sub">{E(item["tagline"])}</p>
<h2>Your template link{"s" if len(links) > 1 else ""}</h2>{link_boxes}
<h2>Get set up (5 minutes)</h2><ol>{steps}</ol><h2>Good to know</h2><ul>{tip}</ul>{nx}
<div class="foot">Thank you for buying from a small business. Questions or a link not working? Reply to your receipt email.<br>
Educational organising tool, not financial advice. Example data is fictional. For personal use by the buyer; please don't
resell or share the link. &copy; Money Made Simple</div></section></body></html>"""
