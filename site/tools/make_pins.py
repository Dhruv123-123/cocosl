#!/usr/bin/env python3
"""Render the 10 Pinterest pins in site/PINS.md to upload-ready 1000x1500 PNGs.

    python3 site/tools/make_pins.py              # writes site/pins/*.png and site/pins/pins.csv
    python3 site/tools/make_pins.py --out DIR

Numbers on the salary pins come from pseo.py (the same maths as the pages), so re-run this after the
tax data changes. The footer shows the site's domain from site.json > url. Needs Playwright + Chromium
(CHROMIUM_PATH if the browser lives somewhere unusual) and the Inter font for the intended look.
pins.csv has each pin's title, description, alt text, board and tracked link for Pinterest's bulk upload.
"""
from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
import pseo  # noqa: E402

esc = html.escape
CFG = json.loads((SITE / "site.json").read_text())
DOMAIN = urlparse(CFG["url"]).netloc
SHOP = {i["slug"]: i for i in json.loads((SITE / "content" / "shop.json").read_text())["items"]}
RULES, _ = pseo.load()


def money(x: float) -> str:
    return f"${x:,.0f}"


def month(s: int) -> str:
    return money(pseo.take_home(RULES, s)["month"])


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1000px;height:1500px}
body{font-family:Inter,system-ui,sans-serif;position:relative;overflow:hidden;
  --ink:#0b1d13;--ink2:#1e2e24;--paper:#f4f1e8;--green:#2fbf71;--green-d:#1a7a45;--gold:#f2b134;--goldt:#fdf3dd;--muted:#4b5a51}
.dark{background:radial-gradient(90% 70% at 85% 0%,#1d3d2a 0%,var(--ink) 60%);color:var(--paper)}
.light{background:var(--paper);color:var(--ink)}
.brand{position:absolute;left:60px;top:60px;display:flex;align-items:center;gap:16px;font-weight:800;font-size:30px}
.mark{width:56px;height:56px;border-radius:50%;background:var(--gold);color:var(--ink);display:grid;place-items:center;font-weight:900;font-size:22px;letter-spacing:-.02em}
.foot{position:absolute;left:60px;right:60px;bottom:140px;font-size:28px;font-weight:600;opacity:.75}
.body{position:absolute;left:60px;right:60px;top:170px;bottom:200px;display:flex;flex-direction:column;gap:36px}
.kick{font-size:32px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--gold)}
.light .kick{color:var(--green-d)}
.dek{font-size:38px;font-weight:500;line-height:1.3;opacity:.85}
.spacer{flex:1}
h1{font-weight:850;letter-spacing:-.035em;line-height:1.03}
.sub{font-size:42px;font-weight:600;line-height:1.2}
.btn{align-self:flex-start;border-radius:999px;padding:24px 40px;font-size:40px;font-weight:800}
.btn.gold{background:var(--gold);color:var(--ink)} .btn.ink{background:var(--ink);color:var(--paper)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.card{background:var(--paper);color:var(--ink);border-radius:24px;padding:30px 28px}
.card b{display:block;font-size:44px;font-weight:800;letter-spacing:-.02em}
.card span{display:block;font-size:30px;color:var(--muted);margin-top:8px;line-height:1.25}
.ticks{display:flex;flex-direction:column;gap:22px;font-size:40px;font-weight:650}
.ticks div{display:flex;align-items:center;gap:22px}
.ticks i{flex:none;width:58px;height:58px;border-radius:50%;background:var(--green);color:var(--ink);font-style:normal;font-weight:900;display:grid;place-items:center;font-size:34px}
.num i{background:var(--gold)}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;flex:1}
.col{background:var(--paper);color:var(--ink);border-radius:24px;padding:36px 26px;display:flex;flex-direction:column;gap:20px}
.col b{font-size:42px;font-weight:800;line-height:1.05}
.col span{font-size:34px;line-height:1.25}
.rows{display:flex;flex-direction:column;gap:22px}
.row{background:var(--ink);color:var(--paper);border-radius:22px;padding:34px 40px;display:flex;justify-content:space-between;align-items:center}
.row b{font-size:56px;font-weight:800} .row em{font-style:normal;color:var(--gold);font-size:64px;font-weight:850}
.note{font-size:32px;color:var(--muted);line-height:1.3}
.bar{display:flex;height:84px;border-radius:16px;overflow:hidden}
.bar div{height:100%}
.legend{display:grid;grid-template-columns:repeat(4,1fr);font-size:30px;font-weight:650;gap:10px}
.legend span{display:flex;align-items:center;gap:10px}.legend i{width:22px;height:22px;border-radius:6px;display:inline-block}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.tile{background:var(--goldt);border-radius:24px;aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;font-size:32px;font-weight:750;text-align:center;padding:16px}
.tile svg{width:96px;height:96px}
.pill{display:inline-block;border-radius:999px;padding:18px 34px;font-size:40px;font-weight:800}
.tablecard{background:var(--paper);color:var(--ink);border-radius:28px;padding:40px;position:relative}
.trow{display:flex;align-items:center;justify-content:space-between;gap:30px;padding:22px 0;border-bottom:2px solid #d9d3c3;font-size:38px;font-weight:650}
.trow:last-child{border-bottom:0}
.trow s{display:block;height:26px;border-radius:13px;background:var(--green);text-decoration:none}
.sticker{position:absolute;right:-14px;top:-40px;background:var(--gold);color:var(--ink);border-radius:18px;padding:16px 22px;font-size:30px;font-weight:850;transform:rotate(4deg)}
"""

ICONS = {  # simple line icons, ink stroke
    "calendar": '<rect x="10" y="18" width="76" height="68" rx="10"/><path d="M10 38h76M30 8v20M66 8v20"/>',
    "envelope": '<rect x="8" y="22" width="80" height="54" rx="8"/><path d="M8 26l40 30 40-30"/>',
    "bag": '<path d="M18 32h60l-6 54H24z"/><path d="M34 32a14 14 0 0128 0"/><path d="M14 14l68 68"/>',
    "bingo": '<rect x="10" y="10" width="76" height="76" rx="8"/><path d="M35 10v76M61 10v76M10 35h76M10 61h76"/>',
    "die": '<rect x="14" y="14" width="68" height="68" rx="14"/><circle cx="34" cy="34" r="5"/><circle cx="62" cy="62" r="5"/><circle cx="48" cy="48" r="5"/>',
    "list": '<rect x="16" y="10" width="64" height="76" rx="8"/><path d="M30 32h36M30 48h36M30 64h22"/>',
    "chart": '<path d="M10 84h76"/><path d="M14 72l20-26 18 14 30-40"/><path d="M66 20h16v16"/>',
    "grid": '<rect x="10" y="10" width="34" height="34" rx="6"/><rect x="52" y="10" width="34" height="34" rx="6"/><rect x="10" y="52" width="34" height="34" rx="6"/><rect x="52" y="52" width="34" height="34" rx="6"/>',
    "jar": '<path d="M28 16h40v12l8 10v42a8 8 0 01-8 8H28a8 8 0 01-8-8V38l8-10z"/><path d="M20 54h56"/>',
}


def icon(name):
    return (f'<svg viewBox="0 0 96 96" fill="none" stroke="#0b1d13" stroke-width="6" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</svg>')


def page(theme: str, body: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body class="{theme}"><div class="brand"><span class="mark">MS</span>Money Made Simple</div>'
            f'<div class="body">{body}</div><div class="foot">{esc(DOMAIN)}</div>{FIT}</body></html>')


FIT = """<script>window.fitPin = () => { const b = document.querySelector('.body'), h = b.querySelector('.fit');
  if (!h) return; let s = parseFloat(getComputedStyle(h).fontSize);
  const over = () => [...b.children].some(e => e.getBoundingClientRect().bottom > b.getBoundingClientRect().bottom + 1);
  const art = b.querySelector('img.art'); let w = art ? art.width : 0;
  while (art && over() && w > 300) { w -= 20; art.style.width = art.style.height = w + 'px'; }
  while (over() && s > 54) { s -= 4; h.style.fontSize = s + 'px'; }
  const d = b.querySelector('.dek'); if (d && over()) d.remove(); }</script>"""


def img_data(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def pins() -> list[dict]:
    s50, s60, s75 = month(50000), month(60000), month(75000)
    kit, pack = SHOP["money-toolkit-bundle"], SHOP["savings-challenge-pack"]
    split = [(0.50, "#1a7a45", "Bills"), (0.10, "#2fbf71", "Funds"), (0.15, "#f2b134", "Goals"),
             (0.25, "#f4f1e8", "Weekly number")]
    P = []
    P.append(dict(slug="quiz-1", path="/quiz/", board="Budgeting for beginners",
        title="What's your money personality? Take the 1-minute quiz",
        desc="Six questions, one minute, and you'll know whether you're an avoider, a spender, a juggler or a saver, plus the one money move that suits your type. Free, no sign-up needed to see your result.",
        alt="Four cards labelled Avoider, Spender, Juggler and Saver under the question \"What's your money personality?\"",
        html=page("dark", '<h1 style="font-size:104px">What\'s your money personality?</h1><div class="grid2">'
            + "".join(f'<div class="card"><b>The {n}</b><span>{h}</span></div>' for n, h in [
                ("Avoider", "puts off opening the app"), ("Spender", "the money finds a way out"),
                ("Juggler", "too many due dates"), ("Saver", "saves, but feels stuck")])
            + '</div><div class="btn gold">Take the 1-minute quiz →</div>')))
    P.append(dict(slug="quiz-2", path="/quiz/", board="Budgeting for beginners",
        title="Why your budget keeps failing (it might be your money personality)",
        desc="Some people need fewer decisions, some need guard rails, some need fewer due dates. Take the six-question quiz to find your type and the budget style that fits it.",
        alt="Headline \"Your budget isn't broken. It might just be the wrong type.\" above four circles and a link to a one-minute quiz.",
        html=page("light", '<div style="background:var(--gold);border-radius:32px;padding:56px 48px">'
            '<h1 style="font-size:96px">Your budget isn\'t broken. It might just be the wrong type.</h1></div>'
            '<div style="display:flex;gap:28px">' + "".join(
                f'<div style="width:130px;height:130px;border-radius:50%;background:var(--ink);color:var(--paper);display:grid;place-items:center;font-size:56px;font-weight:850">{c}</div>'
                for c in "ASJS") + '</div><p class="sub">6 questions · 1 minute · free</p>'
            '<div class="btn ink">Find your money personality →</div>')))
    P.append(dict(slug="compare-budgeting-apps-1", path="/compare/best-budgeting-apps/", board="Money apps and tools",
        title="Budgeting apps compared honestly, including when not to pay for one",
        desc="Six budgeting apps compared by price model, budgeting style and bank syncing, and who should skip each one. Includes the free and spreadsheet options, so you don't pay for an app you won't open.",
        alt="A comparison card listing cost, budgeting style, bank syncing and who each budgeting app is not for.",
        html=page("dark", '<h1 style="font-size:100px">Budgeting apps, compared honestly</h1>'
            '<div class="tablecard"><div class="sticker">Who it\'s NOT for</div>' + "".join(
                f'<div class="trow">{t}<s style="width:{w}px"></s></div>' for t, w in [
                    ("What it costs", 220), ("How it budgets", 300), ("Bank syncing", 160), ("Who it's NOT for", 260)])
            + '</div><p class="sub">Plus the free options that work just as well</p>')))
    P.append(dict(slug="compare-hysa-1", path="/compare/best-high-yield-savings-accounts/", board="Saving money tips",
        title="How to pick a high-yield savings account (and switch in 15 minutes)",
        desc="What actually matters when you choose a high-yield savings account: deposit insurance, fees, how the rate has moved, and transfer times. Five well-known online options side by side, and the 15-minute switch.",
        alt="\"Is your savings account earning almost nothing?\" with a checklist: FDIC insured, no monthly fees, rate history, fast transfers.",
        html=page("light", '<h1 style="font-size:98px">Is your savings account earning <span style="box-shadow:inset 0 -26px 0 var(--gold)">almost nothing?</span></h1>'
            '<p class="sub">What to compare in a high-yield account</p>'
            '<div style="background:var(--ink);color:var(--paper);border-radius:28px;padding:44px" class="ticks">' + "".join(
                f'<div><i>✓</i>{t}</div>' for t in ["FDIC insured", "No monthly fees", "Rate history", "Fast transfers"])
            + '</div><div class="btn ink">Switch in 15 minutes →</div>')))
    P.append(dict(slug="compare-rm-ynab-monarch-1", path="/compare/rocket-money-vs-ynab-vs-monarch/", board="Money apps and tools",
        title="Rocket Money vs YNAB vs Monarch: which budgeting app fits you?",
        desc="Three popular budgeting apps head to head: how each one budgets, what's free, what it costs, how it handles subscriptions, couples and net worth, and who should skip each one.",
        alt="Three columns comparing Rocket Money, YNAB and Monarch under the question \"Which one fits you?\"",
        html=page("dark", '<h1 style="font-size:100px;color:var(--gold)">Which one fits you?</h1><div class="cols">' + "".join(
                f'<div class="col"><b>{n}</b><span>{d}</span></div>' for n, d in [
                    ("Rocket Money", "Finds subscriptions"), ("YNAB", "Every dollar a job"), ("Monarch", "Big-picture dashboard")])
            + '</div><p class="sub">What each costs, and who should skip it</p>')))
    P.append(dict(slug="compare-balance-transfer-1", path="/compare/best-balance-transfer-cards/", board="Debt payoff",
        title="0% balance transfer: do the maths before you apply",
        desc="A balance transfer can save hundreds or cost you more. How to compare the intro period, the transfer fee and the rate afterwards, with a worked example and the mistakes that cancel out the savings.",
        alt="A large \"0%\" with three checks for a balance transfer: intro period, transfer fee, rate after.",
        html=page("light", '<div style="font-size:330px;font-weight:900;letter-spacing:-.06em;line-height:.9">0%<span style="color:var(--gold)">*</span></div>'
            '<h1 style="font-size:84px">Balance transfer: worth the fee?</h1><div class="ticks num">' + "".join(
                f'<div><i>{n}</i>{t}</div>' for n, t in [(1, "Intro period long enough?"), (2, "Transfer fee vs interest saved"), (3, "The rate after the intro")])
            + '</div><div class="btn ink">See the worked example →</div>')))
    bar = "".join(f'<div style="width:{p*100}%;background:{c}"></div>' for p, c, _ in split)
    legend = "".join(f'<span><i style="background:{c}"></i>{n}</span>' for _, c, n in split)
    P.append(dict(slug="budget-50000-1", path="/budget/50000-salary/", board="Budgeting for beginners",
        title=f"How to budget on a $50,000 salary ({RULES['tax_year']} take-home numbers)",
        desc=f"What a $50,000 salary actually leaves you each month in {RULES['tax_year']}, a line-by-line budget for it, how much rent fits, and how much your state changes the numbers. With the maths shown.",
        alt=f"\"$50,000 a year is about {s50} a month take-home\", above a bar split into bills, funds, goals and a weekly spending number.",
        html=page("dark", '<p class="sub" style="font-size:72px;font-weight:800">$50,000 a year</p>'
            f'<div style="font-size:190px;font-weight:900;color:var(--gold);letter-spacing:-.05em;line-height:1">≈ {s50}</div>'
            '<p class="sub">a month take-home after federal tax + FICA*</p>'
            f'<div class="bar">{bar}</div><div class="legend">{legend}</div>'
            f'<p style="font-size:28px;opacity:.75">*{RULES["tax_year"]}, single filer, no state income tax. Estimate.</p>')))
    P.append(dict(slug="budget-hub-1", path="/budget/", board="Budgeting for beginners",
        title=f"How much rent can you afford? Real {RULES['tax_year']} numbers by salary",
        desc="The 30% rule in real dollars, plus take-home pay, a monthly plan and the big cities where a one-bedroom fits, from $30,000 to $200,000.",
        alt="Rent at 30% of gross pay: $1,250 a month on $50,000, $1,500 on $60,000, $1,875 on $75,000.",
        html=page("light", '<h1 style="font-size:96px">How much rent fits your salary?</h1><div class="rows">' + "".join(
                f'<div class="row"><b>${s // 1000}k</b><em>{money(s * 0.3 / 12)}/mo</em></div>' for s in (50000, 60000, 75000))
            + '</div><p class="note">30% of gross pay. Take-home, budgets and city rents for your salary →</p>')))
    P.append(dict(slug="shop-toolkit-1", path="/shop/money-toolkit-bundle/", board="Budget printables",
        title=f"5 money kits in one: budget, bills, credit, debt and investing (${kit['price']:g})",
        desc="All five Money Made Simple guide-and-spreadsheet kits in one download, with a Start Here map and a 30-day plan that uses all five. Excel, Google Sheets or Numbers. One payment, no subscription.",
        alt=f"The Money Made Simple Toolkit cover with five kits listed and a ${kit['price']:g} price tag.",
        html=page("light", '<h1 style="font-size:84px">Your money system, sorted in 30 days</h1>'
            f'<div style="position:relative;align-self:center"><img src="{img_data(SITE / "static" / kit["image"].lstrip("/"))}" '
            'style="width:480px;height:480px;border-radius:20px;transform:rotate(-4deg);box-shadow:0 30px 60px rgba(0,0,0,.3)">'
            f'<div class="pill" style="position:absolute;right:-60px;bottom:-24px;background:var(--gold)">${kit["price"]:g} · ${kit["separately"]:g} separately</div></div>'
            '<div class="ticks" style="font-size:34px;gap:12px">' + "".join(
                f'<div><i style="width:20px;height:20px;background:var(--gold)"></i>{t}</div>' for t in [
                    "Bill Cut Kit", "20-Minute Budget", "Credit Report Audit", "Debt-Free Date Planner",
                    "Start Investing With $100 a Month"]) + "</div>")))
    P.append(dict(slug="shop-savings-pack-1", path="/shop/savings-challenge-pack/", board="Budget printables",
        title=f"12 printable savings challenges in one pack (${pack['price']:g})",
        desc="Make saving a habit (and a bit of a game): every savings challenge from the shop in one printable pack, from the 52-week challenge to savings bingo. Letter and A4 PDFs.",
        alt="Six tiles showing printable savings challenges, including 52-week, 100 envelopes and savings bingo.",
        html=page("light", '<h1 style="font-size:92px">12 savings challenges, one download</h1><div class="tiles">' + "".join(
                f'<div class="tile">{icon(i)}{t}</div>' for i, t in [
                    ("calendar", "52-week"), ("envelope", "100 envelopes"), ("bag", "No-spend"),
                    ("bingo", "Savings bingo"), ("die", "Roll and save"), ("jar", "30-day")])
            + f'</div><div class="pill" style="align-self:flex-start;background:var(--ink);color:var(--paper)">Letter + A4 · ${pack["price"]:g}</div>')))
    for p in P:
        p["link"] = (CFG["url"] + p["path"].split("#")[0] + "?utm_source=pinterest&utm_medium=social&utm_campaign=pin-"
                     + p["slug"] + ("#" + p["path"].split("#")[1] if "#" in p["path"] else ""))
    return P


# ------------------------------------------------------------------------------------------ library pins
# One page -> two designs: A (dark, headline + one-line pitch) and B (light, gold headline block + what's
# inside). Pages: every shop product, Compare page and article. Text comes from each page's own front matter
# and headings, so a pin never says something its page doesn't.
import re  # noqa: E402

sys.path.insert(0, str(SITE))
GENERIC_H2 = {"common questions", "our verdict", "the short version", "alternatives", "sources", "side by side",
              "the quick comparison", "the bottom line", "faq", "related", "the verdict"}
BOARDS = {"budgeting": ("Budgeting for beginners", "Saving money tips"),
          "credit-and-debt": ("Debt payoff", "Budgeting for beginners"),
          "investing": ("Investing for beginners", "Money apps and tools"),
          "money-tools": ("Money apps and tools", "Budgeting for beginners")}
KIND = {"kit": "Guide + spreadsheet kit", "sheets": "Google Sheets template", "notion": "Notion template",
        "printable": "Printable · Letter + A4 PDF"}
GROUP_ICON = {"budget": "calendar", "savings": "jar", "debt": "chart", "trackers": "list"}
SHOP_BOARD = {"savings": "Saving money tips", "debt": "Debt payoff"}


def split_title(t: str) -> tuple[str, str]:
    """'YNAB review: is it worth $109?' -> ('YNAB review', 'Is it worth $109?'); no colon -> ('', title)."""
    if ": " in t:
        k, h = t.split(": ", 1)
        if len(k) <= 34:
            return k, h[:1].upper() + h[1:]
    return "", t


def first_sentence(s: str, n: int = 150) -> str:
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"[*_`]", "", s)).strip()
    m = re.match(r"(.+?[.!?])(\s|$)", s)
    s = m.group(1) if m else s
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def bullets(md: str, kind: str) -> list[str]:
    hs = [re.sub(r"[*_`]|\[|\]\([^)]*\)", "", h).strip() for h in re.findall(r"^## (.+)$", md, re.M)]
    hs = [re.sub(r"^Step \d+:\s*", "", h) for h in hs if h.lower() not in GENERIC_H2]
    hs = [h[:1].upper() + h[1:] for h in hs if 6 <= len(h) <= 44][:3]
    if len(hs) >= 2:
        return hs
    return {"review": ["How it works", "What it costs", "Who should skip it"],
            "compare": ["What each one costs", "Side-by-side features", "Who each one is NOT for"]}.get(
        kind, ["The short version", "The maths, shown", "What to do next"])


def tracked(path: str, campaign: str) -> str:
    base, _, frag = path.partition("#")
    return (CFG["url"] + base + "?utm_source=pinterest&utm_medium=social&utm_campaign=" + campaign
            + ("#" + frag if frag else ""))


def design_a(kicker, headline, dek, cta, art=""):
    return page("dark", (f'<p class="kick">{esc(kicker)}</p>' if kicker else "")
                + f'<h1 class="fit" style="font-size:100px">{esc(headline)}</h1>'
                + (f'<p class="dek">{esc(dek)}</p>' if dek else "") + '<div class="spacer"></div>' + art + '<div class="spacer"></div>'
                + f'<div class="btn gold">{esc(cta)} →</div>')


def design_b(kicker, headline, items, cta, tag=""):
    return page("light", '<div style="background:var(--gold);border-radius:32px;padding:48px 44px">'
                + (f'<p class="kick" style="color:var(--ink);margin-bottom:14px">{esc(kicker)}</p>' if kicker else "")
                + f'<h1 class="fit" style="font-size:92px">{esc(headline)}</h1></div><div class="spacer"></div>'
                + '<div class="ticks" style="font-size:44px;gap:30px">' + "".join(f"<div><i>✓</i>{esc(t)}</div>" for t in items) + "</div>"
                + '<div class="spacer"></div><div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">'
                + f'<div class="btn ink">{esc(cta)} →</div>'
                + (f'<div class="pill" style="background:var(--goldt)">{esc(tag)}</div>' if tag else "") + "</div>")


def library() -> list[dict]:
    import build
    redirects = CFG.get("blog_redirects", {})
    out = []

    def add(slug, kind, path, board2, title, desc, alt_subject, html_a, html_b, priority, live=None):
        for v, h in (("a", html_a), ("b", html_b)):
            camp = f"pin-{slug}-{v}"
            out.append(dict(slug=f"{slug}-{v}", page=slug, variant=v, kind=kind, path=path, board=board2[0],
                            board2=board2[1], title=title[:100], desc=desc[:500],
                            alt=f"Pin {('A' if v == 'a' else 'B')} for {alt_subject}: \"{title[:90]}\"",
                            html=h, link=tracked(path, camp), priority=priority, live=str(live or "")))

    for f in sorted((SITE / "content" / "compare").glob("*.md")):
        meta, md = build.parse_front_matter(f.read_text())
        k, h = split_title(meta["title"])
        slug = "compare-" + f.stem
        add(slug, "compare", f"/compare/{f.stem}/", ("Money apps and tools", "Budgeting for beginners")
            if "credit" not in f.stem and "balance" not in f.stem else ("Debt payoff", "Money apps and tools"),
            meta["title"], meta["description"], "a comparison page",
            design_a(k or "Compared honestly", h, first_sentence(meta["description"]), "See the comparison"),
            design_b(meta.get("short", "Compared"), h, bullets(md, "compare"), "Compare them"), 1, meta["date"])
    for f in sorted((SITE / "content" / "blog").glob("*.md")):
        if f.stem in redirects:
            continue
        meta, md = build.parse_front_matter(f.read_text())
        if meta.get("status") == "draft":
            continue
        k, h = split_title(meta["title"])
        kind = "review" if f.stem.endswith("-review") else "article"
        mins = meta.get("read_minutes")
        add(f.stem, kind, f"/blog/{f.stem}/", BOARDS.get(meta.get("pillar"), BOARDS["budgeting"]),
            meta["title"], meta["description"], "an article",
            design_a(k or CFG.get("pillars", {}).get(meta.get("pillar"), ""), h,
                     first_sentence(meta["description"]), "Read it" + (f" in {mins} min" if mins else "")),
            design_b(k or "Plain-English guide", h, bullets(md, kind), "Read the guide"), 3, meta["date"])
    for it in json.loads((SITE / "content" / "shop.json").read_text())["items"]:
        price = f"${it['price']:g}" if it["price"] else "Free"
        label = "Bundle" if it.get("bundle") else KIND.get(it["kind"], "Download")
        if it.get("image"):
            art = (f'<img src="{img_data(SITE / "static" / it["image"].lstrip("/"))}" class="art" style="width:440px;height:440px;'
                   'border-radius:20px;align-self:center;transform:rotate(-3deg);box-shadow:0 30px 60px rgba(0,0,0,.35)">')
        else:
            art = ('<div style="align-self:center;width:300px;height:300px;border-radius:40px;background:var(--goldt);'
                   f'display:grid;place-items:center">{icon(GROUP_ICON.get(it.get("group"), "list"))}</div>')
            art = art.replace('<svg viewBox', '<svg style="width:170px;height:170px" viewBox')
        pitch = first_sentence(it.get("blurb", ""), 160)
        board = SHOP_BOARD.get(it.get("group"), "Budget printables")
        inc = [label, "One payment, no subscription", "Instant download"] if it["kind"] != "printable" else \
            ["Letter + A4 PDF", "Print at home or fill on a tablet", "Instant download"]
        if it.get("separately"):
            inc[1] = f"${it['separately']:g} if bought separately"
        add("shop-" + it["slug"], "shop", it.get("page") or f"/shop/{it['slug']}/", (board, "Budget printables"
            if board != "Budget printables" else "Budgeting for beginners"),
            f"{it['name']} ({price.lower() if price == 'Free' else price})", it.get("blurb", it["name"]), f"the {it['name']}",
            design_a(f"{label} · {price}", it["name"], pitch, "Get it in the shop", art),
            design_b(label, it["name"], inc, "See it in the shop", price),
            0 if it.get("bundle") or it["kind"] == "kit" else 2)
    return out


RAMP = [(14, 1), (16, 2), (30, 3)]  # (days, new pins a day): 1 a day for two weeks, then 2, then 3 (days 31-60)
B_GAP = 14  # days between a page's design A and design B
URL_GAP = 7  # days between any two pins that link to the same page (scouting's Pinterest playbook)
DAY1 = date(2026, 11, 16)  # launch Day 1 in launch/money-made-simple/LAUNCH_WEEK.md (PR #5); site pins start in week 3
# LAUNCH_WEEK.md's "start with these site pins", in its order: they go first in the schedule.
LAUNCH_LEAD = ["/quiz/", "/blog/how-to-freeze-your-credit/", "/blog/401k-match-explained/",
               "/blog/how-to-build-an-emergency-fund/", "/blog/sinking-funds-explained/",
               "/blog/find-and-cancel-subscriptions/", "/blog/how-to-start-investing-with-100-a-month/",
               "/blog/expense-ratios-explained/"]


def _page(p: dict) -> str:
    """The page a pin links to, without the domain or UTM tags."""
    return urlparse(p["link"]).path


def schedule(featured: list[dict], lib: list[dict], start: date) -> list[dict]:
    """60 days of fresh pins at 1-3 a day (no re-pins of the same image). Featured pins go first, then each page's
    design A, mixing kits/bundles, comparisons, printables and articles; design B follows at least B_GAP days later.
    A pin is never scheduled before its page's publish date (articles and comparisons are released over six
    weeks). Pins that don't fit in 60 days are listed after, undated, as the backlog for the next run."""
    times = {1: ["12:00"], 2: ["09:00", "19:00"], 3: ["08:00", "13:00", "20:00"]}
    queues: dict[int, list] = {}
    for p in lib:
        if p["variant"] == "a":
            queues.setdefault(p["priority"], []).append(p)
    order = []
    while any(queues.values()):  # round-robin: 0 kits/bundles, 1 compare, 2 printables, 3 articles
        for k in sorted(queues):
            if queues[k]:
                order.append(queues[k].pop(0))
    b_of = {p["page"]: p for p in lib if p["variant"] == "b"}
    pending = [dict(p, live="") for p in featured] + order
    lead = []
    for path in LAUNCH_LEAD:  # first pin for each launch page, in LAUNCH_WEEK's order
        hit = next((p for p in pending if _page(p) == path and p.get("variant", "a") == "a"), None)
        if hit:
            pending.remove(hit)
            lead.append(hit)
    pending = lead + pending
    posted_a: dict[str, date] = {}
    last_url: dict[str, date] = {}
    rows, day = [], 0
    for span, per_day in RAMP:
        for _ in range(span):
            d = start + timedelta(days=day)
            day += 1
            todays = []
            for p in list(pending):
                if len(todays) == per_day:
                    break
                if p.get("live") and date.fromisoformat(p["live"]) > d:
                    continue  # page not published yet
                if p.get("variant") == "b" and (d - posted_a[p["page"]]).days < B_GAP:
                    continue
                if _page(p) in last_url and (d - last_url[_page(p)]).days < URL_GAP:
                    continue
                todays.append(p)
                pending.remove(p)
                last_url[_page(p)] = d
                if p.get("variant") == "a":
                    posted_a[p["page"]] = d
                    pending.append(b_of[p["page"]])  # B goes to the back of the queue
            for t, p in zip(times[per_day], todays):
                rows.append(_row(p, d.isoformat(), t))
    rows += [_row(p, "", "") for p in pending]
    return rows


def _row(p: dict, d: str, t: str) -> dict:
    return {"date": d, "time_et": t, "file": p["file"], "board": p["board"], "title": p["title"],
            "description": p["desc"], "alt_text": p["alt"], "link": p["link"],
            "page_live": p.get("live") or ""}


def render(pg, items: list[dict], out: Path) -> None:
    for p in items:
        pg.set_content(p["html"], wait_until="load")
        pg.evaluate("() => window.fitPin && window.fitPin()")
        over = pg.evaluate("""() => { const b = document.querySelector('.body'), r = b.getBoundingClientRect();
            return [...b.querySelectorAll('*')].some(e => e.getBoundingClientRect().bottom > r.bottom + 1) }""")
        if over:
            raise SystemExit(f"pin {p['slug']}: content runs past the safe area")
        pg.screenshot(path=str(out / p["file"]), clip={"x": 0, "y": 0, "width": 1000, "height": 1500})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(SITE / "pins"))
    ap.add_argument("--all", action="store_true", help="also render a pin pair for every shop product, Compare "
                    "page and article into <out>/library/, and write <out>/schedule.csv")
    ap.add_argument("--start", default=(DAY1 + timedelta(days=14)).isoformat(),
                    help="first pin date (default: week 3 after launch Day 1, as LAUNCH_WEEK.md says)")
    ap.add_argument("--no-render", action="store_true", help="write the CSVs only")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    P = pins()
    for n, p in enumerate(P, 1):
        p["file"] = f"{n:02d}-{p['slug']}.png"
    L = library() if a.all else []
    for p in L:
        p["file"] = f"library/{p['slug']}.png"
    if not a.no_render:
        from playwright.sync_api import sync_playwright
        exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None)
        (out / "library").mkdir(exist_ok=True) if L else None
        with sync_playwright() as pw:
            b = pw.chromium.launch(**({"executable_path": exe} if exe else {}))
            for start in range(0, len(P) + len(L), 40):  # fresh page every 40 pins keeps memory flat
                pg = b.new_page(viewport={"width": 1000, "height": 1500}, device_scale_factor=1)
                render(pg, (P + L)[start:start + 40], out)
                pg.close()
            b.close()
    with (out / "pins.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "title", "description", "alt_text", "board", "link"])
        for p in P + L:
            w.writerow([p["file"], p["title"], p["desc"], p["alt"], p["board"], p["link"]])
    if L:
        rows = schedule(P, L, date.fromisoformat(a.start))
        with (out / "schedule.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        dated = [r for r in rows if r["date"]]
        print(f"schedule: {len(dated)} pins from {dated[0]['date']} to {dated[-1]['date']}, "
              f"{len(rows) - len(dated)} in the backlog")
    print(f"{len(P) + len(L)} pins -> {out}")


if __name__ == "__main__":
    main()
