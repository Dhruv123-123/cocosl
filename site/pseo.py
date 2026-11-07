"""Data-driven pages: "how to budget on a $X salary" and "cost of living budget in [city]".

Every number on these pages is computed from two data files, so a page is only as good as its data:
  content/data/tax_rules.json   2026 federal, state and local tax rules (single filer, W-2 wages)
  content/data/cities.json      HUD Fair Market Rents for the 25 largest US cities' metro areas
Update both every November (tax year) and October (HUD FMR year). build.py calls build_pseo().
"""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path
from urllib.parse import urlencode

esc = html.escape
DATA = Path(__file__).resolve().parent / "content" / "data"

SALARIES = [30000, 40000, 50000, 60000, 75000, 100000, 150000, 200000]
# Salary pages retired in the Nov 2026 merge (20 pages -> 8 bands): old URL -> nearest band, 301 on Netlify.
SALARY_REDIRECTS = {25000: 30000, 35000: 40000, 45000: 50000, 55000: 60000, 65000: 60000, 70000: 75000,
                    80000: 75000, 90000: 100000, 110000: 100000, 120000: 100000, 130000: 150000, 175000: 200000}
CITY_SALARIES = [40000, 50000, 60000, 75000, 100000, 125000]
# States shown side by side on every salary page: none, flat, progressive, and progressive + city tax.
SALARY_COMPARE = [("TX", None, "Texas (no state income tax)"), ("NC", None, "North Carolina (flat 3.99%)"),
                  ("CA", None, "California"), ("NY", "nyc", "New York City (state + city)")]


def fmt_day(iso: str) -> str:
    from datetime import date as _d
    d = _d.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def sal_path_(s: int) -> str:
    return f"/budget/{s}-salary/"


def load_examples() -> dict[int, str]:
    """content/budget-examples.md: one hand-written worked example per salary page, under '## <salary>'."""
    text = (DATA.parent / "budget-examples.md").read_text()
    out = {int(k): v.strip() for k, v in re.findall(r"^## (\d+)\n(.*?)(?=^## |\Z)", text, re.S | re.M)}
    missing = [x for x in SALARIES if x not in out]
    if missing:
        raise SystemExit(f"content/budget-examples.md: no worked example for {missing}")
    return out


def load():
    return (json.loads((DATA / "tax_rules.json").read_text()), json.loads((DATA / "cities.json").read_text()))


# ------------------------------------------------------------------------------------------------- tax maths
def brackets_tax(amount: float, brackets) -> float:
    tax, lower = 0.0, 0.0
    for upper, rate in brackets:
        top = math.inf if upper is None else upper
        if amount <= lower:
            break
        tax += (min(amount, top) - lower) * rate
        lower = top
    return tax


def marginal(amount: float, brackets) -> float:
    for upper, rate in brackets:
        if upper is None or amount <= upper:
            return rate
    return brackets[-1][1]


def state_tax(rules: dict, code: str, wages: float) -> float:
    s = rules["states"][code]
    if s.get("none"):
        return 0.0
    fed_taxable = max(0.0, wages - rules["federal"]["standard_deduction"])
    if code == "CO":
        return fed_taxable * s["flat"]
    if code == "OH":
        ex = next((e for cap, e in s["exemption_by_agi"] if wages <= cap), 0)
        return max(0.0, wages - ex - s["zero_bracket"]) * s["flat"]
    taxable = max(0.0, wages - s.get("deduction", 0) - s.get("exemption", 0))
    tax = taxable * s["flat"] if "flat" in s else brackets_tax(taxable, s["brackets"])
    return max(0.0, tax - s.get("credit", 0))


def local_tax(rules: dict, key: str | None, wages: float) -> float:
    if not key:
        return 0.0
    loc = rules["local"][key]
    if "brackets" in loc:
        return brackets_tax(max(0.0, wages - loc.get("deduction", 0)), loc["brackets"])
    if loc.get("on") == "wages":
        return wages * loc["flat"]
    return max(0.0, wages - loc.get("exemption", 0)) * loc["flat"]


def take_home(rules: dict, salary: float, state: str | None = None, local: str | None = None,
              pretax401k: float = 0.0) -> dict:
    """Same federal maths as the take-home pay calculator (lib/tax2026.js). 401(k) lowers income tax, not FICA."""
    f = rules["federal"]
    agi = max(0.0, salary - pretax401k)
    taxable = max(0.0, agi - f["standard_deduction"])
    federal = brackets_tax(taxable, f["brackets"])
    ss = min(salary, f["social_security"]["wage_base"]) * f["social_security"]["rate"]
    med = salary * f["medicare"]["rate"] + max(0.0, salary - f["medicare"]["additional_threshold"]) * f["medicare"]["additional_rate"]
    st = state_tax(rules, state, agi) if state else 0.0
    lo = local_tax(rules, local, agi if local == "nyc" else salary)
    net = salary - pretax401k - federal - ss - med - st - lo
    return {"salary": salary, "taxable": taxable, "federal": federal, "ss": ss, "medicare": med, "state": st,
            "local": lo, "net": net, "month": net / 12, "paycheck": net / 26,
            "marginal": marginal(taxable, f["brackets"]), "effective": (federal + st + lo) / salary if salary else 0}


# ---------------------------------------------------------------------------------------------- formatting
def money(x: float) -> str:
    return f"${x:,.0f}"


def pct(x: float, digits: int = 0) -> str:
    return f"{x * 100:.{digits}f}%"


def k(s: int) -> str:
    return f"${s // 1000}k" if s % 1000 == 0 else money(s)


def plan_split(salary: float) -> tuple[str, dict]:
    """Starting-point split of take-home pay for the four-line plan, by income band."""
    if salary < 40000:
        return "tight", {"bills": 0.60, "funds": 0.08, "goals": 0.10}
    if salary < 75000:
        return "middle", {"bills": 0.50, "funds": 0.10, "goals": 0.15}
    if salary < 130000:
        return "upper", {"bills": 0.45, "funds": 0.10, "goals": 0.20}
    return "high", {"bills": 0.40, "funds": 0.10, "goals": 0.25}


def table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table" tabindex="0"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def faq_html(faq: list[tuple[str, str]]) -> str:
    return '<h2 id="common-questions">Common questions</h2>' + "".join(
        f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq)


# ------------------------------------------------------------------------------------------------- builder
def build_pseo(ctx: dict) -> list[tuple[str, str]]:
    cfg, u, absu, layout, write = ctx["CFG"], ctx["u"], ctx["absu"], ctx["layout"], ctx["write"]
    org_ld, magnet_box, product_card, prod = ctx["org_ld"], ctx["magnet_box"], ctx["product_card"], ctx["product"]
    rules, cdata = load()
    cities = cdata["cities"]
    year = rules["tax_year"]
    as_of = cdata["as_of"]
    calc_base = cfg.get("calculators_url", cfg["url"] + "/calculators").rstrip("/") + "/take-home-pay/"
    urls: list[tuple[str, str]] = []
    today = ctx["today"]
    examples = load_examples()
    for old, new in SALARY_REDIRECTS.items():
        ctx["redirects"].append((sal_path_(old), sal_path_(new)))

    def calc_link(salary: float, state_rate: float, text: str) -> str:
        q = urlencode({"salary": int(salary), "pretax401k": 0, "pretaxHealth": 0,
                       "stateRate": round(state_rate * 100, 1), "payPeriods": 26})
        return (f'<a class="btn" href="{esc(calc_base)}?{esc(q)}" '
                f'data-calc="take-home-pay">{esc(text)}</a>')

    def city_name(c):
        return c["name"]

    def rent_of(c, roommate=False):
        return c["br2"] / 2 if roommate else c["br1"]

    def city_net(c, salary):
        return take_home(rules, salary, c["state"], c.get("local"))

    def src_url(c):
        return cdata["sources"][c["src"]]

    def notes_block(extra: str = "") -> str:
        return (f'<p class="disclaimer">Estimates for a single filer with W-2 wages and the standard deduction, '
                f'tax year {year}. They leave out credits, itemised deductions, pre-tax health premiums and payroll '
                f'deductions such as state disability insurance. Rents are HUD Fair Market Rents (rent plus utilities '
                f'for a modest unit, 40th percentile), as of {esc(as_of)}; verify current figures before you sign a '
                f'lease. {extra}{esc(cfg["disclaimer"])}</p>')

    def article_ld(path, title, desc, faq, crumb_name, crumb_path):
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
               "datePublished": "2026-11-07", "dateModified": today, "mainEntityOfPage": absu(path),
               "image": absu("/img/og-default.png"),
               "author": ctx["author_ld"](),
               "publisher": org_ld()},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": cfg["url"] + "/"},
                  {"@type": "ListItem", "position": 2, "name": crumb_name, "item": absu(crumb_path)},
                  {"@type": "ListItem", "position": 3, "name": title, "item": absu(path)}]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                  {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                  for q, a in faq]}]
        return ld

    def og(section):
        return {"article:published_time": "2026-11-07", "article:modified_time": today,
                "article:section": section, "article:author": cfg["name"]}

    sal_path = lambda s: f"/budget/{s}-salary/"  # noqa: E731
    city_path = lambda c: f"/cost-of-living/{c['slug']}/"  # noqa: E731

    # ============================================================== salary pages
    for i, s in enumerate(SALARIES):
        base = take_home(rules, s)
        band, split = plan_split(s)
        m = base["month"]
        bills, funds, goals = (m * split[x] for x in ("bills", "funds", "goals"))
        weekly = (m - bills - funds - goals) * 12 / 52
        hourly = s / 2080
        gross_m = s / 12
        rent30 = gross_m * 0.30
        rent_net = m * 0.35
        fits = sorted((c for c in cities if c["br1"] <= rent30), key=lambda c: c["br1"])
        fits_room = sorted((c for c in cities if c["br1"] > rent30 and rent_of(c, True) <= rent30),
                           key=lambda c: rent_of(c, True))
        stretch = sorted((c for c in cities if rent_of(c, True) > rent30), key=lambda c: -c["br1"])
        ef3, ef6 = bills * 3, bills * 6
        months_to_ef = math.ceil(ef3 / goals) if goals else 0
        five = take_home(rules, s, pretax401k=s * 0.05)
        cost5 = base["net"] - five["net"]
        match = s * 0.03  # 50% match on 6%: modelled as half of 6%
        six = take_home(rules, s, pretax401k=s * 0.06)
        cost6 = base["net"] - six["net"]
        fb = rules["federal"]["brackets"]
        nxt = next(((up, r) for (up, r) in fb if up is not None and base["taxable"] <= up), None)
        nxt_rate = next((r for (up, r) in fb if r > base["marginal"]), None)
        cmp_rows = []
        for code, loc, label in SALARY_COMPARE:
            t = take_home(rules, s, code, loc)
            cmp_rows.append([esc(label), money(t["state"] + t["local"]), money(t["month"]), money(t["paycheck"])])
        ca = take_home(rules, s, "CA")
        ny = take_home(rules, s, "NY", "nyc")
        gap = base["month"] - ny["month"]

        band_text = {
            "tight": (f"On {money(s)} there's very little slack, so the order you pay things in matters more than "
                      f"the percentages. Cover rent, utilities, food and minimum payments first. The goals line is "
                      f"small on purpose: {money(goals)} a month still builds a {money(ef3)} emergency fund in about "
                      f"{months_to_ef} months, and that fund is what stops one car repair turning into card debt. "
                      f"If bills take more than 60% of take-home, the fix is usually housing (a roommate, or a "
                      f"cheaper area) rather than cutting coffee."),
            "middle": (f"{money(s)} is enough to cover the basics with room for goals, if fixed bills stay around "
                       f"half of take-home. The biggest lever is rent: at {money(rent30)} a month (30% of gross) you "
                       f"keep the plan below balanced. Paying more than that is common, but every $100 over comes "
                       f"straight out of the goals or weekly lines."),
            "upper": (f"At {money(s)} the risk shifts from not having enough to lifestyle creep: a bigger "
                      f"apartment, a newer car and more subscriptions can absorb a raise without anyone deciding it "
                      f"should. Fixing goals at 20% of take-home ({money(goals)} a month) before the weekly number is "
                      f"what turns this salary into savings."),
            "high": (f"At {money(s)} taxes are the second-biggest line after housing: your top federal rate is "
                     f"{pct(base['marginal'])}, so every pre-tax dollar into a 401(k) saves {pct(base['marginal'])} "
                     f"in federal tax now. A 25% goals line ({money(goals)} a month) is realistic here, and maxing out "
                     f"workplace retirement accounts is usually the first job for it."),
        }[band]

        if fits:
            fit_text = ("A one-bedroom at the HUD fair market rent stays under 30% of your gross pay in "
                        + ", ".join(f'<a href="{u(city_path(c))}">{esc(city_name(c))}</a> ({money(c["br1"])})'
                                    for c in fits) + ".")
        else:
            fit_text = (f"None of the 25 largest US cities has a fair-market one-bedroom under {money(rent30)}. "
                        f"The cheapest is {esc(min(cities, key=lambda c: c['br1'])['name'])} at "
                        f"{money(min(c['br1'] for c in cities))}.")
        room_text = ""
        if fits_room:
            room_text = (" With a roommate splitting a two-bedroom, these also fit: "
                         + ", ".join(f'<a href="{u(city_path(c))}">{esc(city_name(c))}</a> '
                                     f'({money(rent_of(c, True))} each)' for c in fits_room) + ".")
        stretch_text = ""
        if stretch and fits:
            stretch_text = (f" Even shared, rent would go over 30% of your pay in "
                            + ", ".join(f'<a href="{u(city_path(c))}">{esc(city_name(c))}</a>'
                                        for c in stretch[:5]) + ".")

        bracket_text = (f"Your taxable income (salary minus the {money(rules['federal']['standard_deduction'])} "
                        f"standard deduction) is {money(base['taxable'])}, which puts your top dollars in the "
                        f"{pct(base['marginal'])} federal bracket. Your average federal rate is only "
                        f"{pct(base['federal'] / s, 1)}, because each bracket only applies to the dollars inside it.")
        if nxt and nxt_rate:
            bracket_text += (f" You could earn {money(nxt[0] - base['taxable'])} more before any dollar is taxed "
                             f"at {pct(nxt_rate)}, and even then only the dollars above that line are. A raise "
                             f"never lowers your take-home pay.")

        faq = [
            (f"How much is {money(s)} a year after taxes?",
             f"About {money(base['net'])} a year, or {money(base['month'])} a month, for a single filer in a state "
             f"with no income tax in {year}, after {money(base['federal'])} of federal income tax and "
             f"{money(base['ss'] + base['medicare'])} of Social Security and Medicare. In California it's about "
             f"{money(ca['month'])} a month; in New York City about {money(ny['month'])}."),
            (f"How much is {money(s)} a year per hour?",
             f"About {money(hourly)} an hour before tax, based on 40 hours a week for 52 weeks (2,080 hours). "
             f"After federal tax and FICA it's about {money(base['net'] / 2080)} an hour."),
            (f"How much rent can I afford on {money(s)}?",
             f"The common 30%-of-gross rule gives {money(rent30)} a month. Measured against take-home pay, a "
             f"35% cap gives about {money(rent_net)} with no state income tax. Either way, rent plus your other "
             f"fixed bills should stay near {pct(split['bills'])} of take-home for the plan on this page to work."),
            (f"How much should I save on {money(s)}?",
             f"A starting point is {pct(split['goals'])} of take-home pay, about {money(goals)} a month, split "
             f"between an emergency fund of {money(ef3)} to {money(ef6)} (three to six months of bills) and "
             f"retirement. If your employer matches 401(k) contributions, contribute enough to get the full match first."),
        ]
        title = f"How to budget on a {money(s)} salary"
        seo_title = f"How to budget on {money(s)} a year ({year} take-home)"
        desc = (f"{money(s)} a year is about {money(base['month'])} a month after federal tax and FICA. A month-by-"
                f"month budget, how much rent fits, and what changes by state, with the maths shown.")
        path = sal_path(s)
        prev_s = SALARIES[i - 1] if i else None
        next_s = SALARIES[i + 1] if i + 1 < len(SALARIES) else None
        pager = "".join(f'<a href="{u(sal_path(x))}">{lbl}: {money(x)}</a>'
                        for lbl, x in (("Lower", prev_s), ("Higher", next_s)) if x)
        body = f"""<article class="wrap article">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/budget/')}">Budget by salary</a> / <span>{money(s)}</span></p>
  <h1>{esc(title)}</h1>
  <p class="dek">{money(s)} a year is {money(gross_m)} a month before tax and about <strong>{money(base['month'])}</strong> after federal income tax, Social Security and Medicare. Here's a plan for that money, how much rent it supports, and how much your state changes it.</p>
  <p class="meta">{year} tax figures · Rents as of {esc(as_of)} · Hypothetical single filer, numbers rounded</p>
  <p class="calc-cta">{calc_link(s, 0, "Check your own take-home pay")}</p>
  <div class="prose">
<h2 id="take-home">Your take-home pay on {money(s)}</h2>
<p>For a single filer taking the standard deduction, before any 401(k) or health premiums:</p>
{table(["Item", "Per year", "Per month"], [
            ["Salary", money(s), money(gross_m)],
            ["Federal income tax", "−" + money(base["federal"]), "−" + money(base["federal"] / 12)],
            ["Social Security (6.2%)", "−" + money(base["ss"]), "−" + money(base["ss"] / 12)],
            ["Medicare (1.45%" + (" + 0.9% over $200k" if s > 200000 else "") + ")", "−" + money(base["medicare"]), "−" + money(base["medicare"] / 12)],
            ["<strong>Take-home, no state income tax</strong>", f"<strong>{money(base['net'])}</strong>", f"<strong>{money(base['month'])}</strong>"]])}
<p>That's about {money(base['paycheck'])} per paycheck if you're paid every two weeks. State and city income tax come out on top of this:</p>
{table(["Where you live", "State + local tax / yr", "Take-home / month", "Per paycheck (26)"], cmp_rows)}
<p>The gap between Texas and New York City at this salary is {money(gap)} a month. <a href="{u('/cost-of-living/')}">Compare all 25 big cities</a> with their rents.</p>

<h2 id="budget">A {money(s)} budget, line by line</h2>
<p>This is the four-line plan from <a href="{u('/blog/how-to-make-a-budget-you-will-keep/')}">how to make a budget you'll keep</a>, filled in with {money(base['month'])} a month. The percentages are starting points for this income, not rules:</p>
{table(["Line", "Share of take-home", "Per month", "What goes in it"], [
            ["Bills", pct(split["bills"]), money(bills), "Rent, utilities, phone, insurance, groceries baseline, minimum debt payments"],
            ["Funds", pct(split["funds"]), money(funds), f'Monthly amounts for irregular costs: car repairs, gifts, renewals (<a href="{u("/blog/sinking-funds-explained/")}">sinking funds</a>)'],
            ["Goals", pct(split["goals"]), money(goals), "Emergency fund, extra debt payments, retirement. Moved on payday."],
            ["Weekly number", pct(1 - sum(split.values())), f"{money(weekly)} a week", "Eating out, fun, shopping, top-up groceries. When it's gone, the week's done."]])}
<p>{band_text}</p>
<p>For comparison, the 50/30/20 rule would give {money(m * 0.5)} for needs, {money(m * 0.3)} for wants and {money(m * 0.2)} for savings.</p>

<h2 id="example">A worked example at {money(s)}</h2>
<p class="meta">A hypothetical person, written for this page. Your own numbers will differ.</p>
{ctx["markdown"](examples[s])[0]}

<h2 id="rent">How much rent fits on {money(s)}</h2>
<p>The 30%-of-gross rule says up to <strong>{money(rent30)} a month</strong>. Measured against take-home pay, 35% is about {money(rent_net)}. Here's how that compares with fair market rents in the 25 largest US cities:</p>
<p>{fit_text}{room_text}{stretch_text}</p>

<h2 id="emergency-fund">Emergency fund target</h2>
<p>Three months of the bills line is {money(ef3)}; six months is {money(ef6)}. Putting the whole goals line toward it, the three-month version takes about {months_to_ef} months. Keep it in a <a href="{u('/compare/best-high-yield-savings-accounts/')}">high-yield savings account</a> so it earns something while it waits. More in <a href="{u('/blog/how-to-build-an-emergency-fund/')}">how to build an emergency fund</a>.</p>

<h2 id="retirement">What a 401(k) costs you at this salary</h2>
<p>Contributing 5% ({money(s * 0.05)} a year) lowers your take-home by only about {money(cost5)} a year, {money(cost5 / 26)} a paycheck, because traditional 401(k) money goes in before federal income tax. If your employer matches 50% of the first 6%, contributing 6% costs you about {money(cost6)} a year in take-home and adds {money(match)} of employer money. See <a href="{u('/blog/401k-match-explained/')}">how a 401(k) match works</a>.</p>

<h2 id="tax-bracket">Your tax bracket on {money(s)}</h2>
<p>{bracket_text}</p>

{faq_html(faq)}
  </div>
  {notes_block()}
  <nav class="pager" aria-label="Other salaries">{pager}</nav>
  {ctx["apps_tools"](["take-home-pay", "afford", "emergency-fund"]) if "apps_tools" in ctx else ""}
  {magnet_box(f"budget-{s}")}
  {f'<section class="next"><h2>Tool for this</h2>{product_card(prod)}</section>' if prod else ''}
</article>"""
        write(path, layout(title=seo_title, description=desc, path=path, body=body, og_type="article",
                           jsonld=article_ld(path, title, desc, faq, "Budget by salary", "/budget/"),
                           og=og("Budget by salary")))
        urls.append((path, today))

    # salary hub
    rows = []
    for s in SALARIES:
        t = take_home(rules, s)
        rows.append([f'<a href="{u(sal_path(s))}">{money(s)}</a>', money(t["month"]), money(t["paycheck"]),
                     money(s / 12 * 0.3)])
    hub_desc = (f"Budgets for {len(SALARIES)} salaries from {money(SALARIES[0])} to {money(SALARIES[-1])}: {year} take-home pay, a line-by-line monthly "
                f"plan, how much rent fits and what your state changes.")
    write("/budget/", layout(title="How to budget on your salary", description=hub_desc, path="/budget/",
                             jsonld=[org_ld()], body=f"""<section class="wrap">
  <h1>How to budget on your salary</h1>
  <p class="dek">Pick the salary closest to yours. Each page shows {year} take-home pay, a four-line monthly plan, how much rent fits, and how your state changes the numbers. Live somewhere specific? See <a href="{u('/cost-of-living/')}">cost of living by city</a>.</p>
  <p class="calc-cta">{calc_link(60000, 0, "Or calculate your exact take-home pay")}</p>
  {table(["Salary", "Take-home / month*", "Per paycheck (26)", "Rent at 30% of gross"], rows)}
  <p class="disclaimer">*Single filer, standard deduction, no state income tax, tax year {year}. Your state and any pre-tax deductions change these numbers.</p>
</section>"""))
    urls.append(("/budget/", today))

    # ============================================================== city pages
    ref = 60000
    at_ref = {c["slug"]: city_net(c, ref)["month"] - c["br1"] for c in cities}
    ranked_left = sorted(cities, key=lambda c: -at_ref[c["slug"]])
    ranked_rent = sorted(cities, key=lambda c: -c["br1"])
    median_left = sorted(at_ref.values())[len(at_ref) // 2]
    for c in cities:
        st_rules = rules["states"][c["state"]]
        loc = rules["local"].get(c.get("local") or "", None)
        need = math.ceil(c["br1"] * 12 / 0.30 / 1000) * 1000
        need_room = math.ceil(rent_of(c, True) * 12 / 0.30 / 1000) * 1000
        rows = []
        for s in CITY_SALARIES:
            t = city_net(c, s)
            rows.append([money(s), money(t["state"] + t["local"]), money(t["month"]),
                         pct(c["br1"] / t["month"]), money(t["month"] - c["br1"]),
                         money(t["month"] - rent_of(c, True))])
        tn = city_net(c, need)
        band, split = plan_split(need)
        m = tn["month"]
        funds, goals = m * split["funds"], m * split["goals"]
        other_bills = max(0.0, m * split["bills"] - c["br1"])
        weekly = (m - c["br1"] - other_bills - funds - goals) * 12 / 52
        rank_rent = ranked_rent.index(c) + 1
        rank_left = ranked_left.index(c) + 1
        if rank_rent == 1:
            rank_phrase = "the highest of the 25 largest US cities"
        elif rank_rent == len(cities):
            rank_phrase = "the lowest of the 25 largest US cities"
        else:
            suf = "th" if 10 <= rank_rent % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(rank_rent % 10, "th")
            rank_phrase = f"the {rank_rent}{suf} highest of the 25 largest US cities"
        diff = at_ref[c["slug"]] - median_left
        t60 = city_net(c, ref)
        if st_rules.get("none"):
            tax_text = f"{esc(st_rules['name'])} has no state income tax on wages"
            if st_rules.get("note"):
                tax_text += f" ({esc(st_rules['note'])})"
            tax_text += ", so your paycheck loses only federal income tax, Social Security and Medicare."
        else:
            kind = "a flat" if "flat" in st_rules else "a graduated"
            tax_text = (f"{esc(st_rules['name'])} has {kind} state income tax: on {money(ref)} it's about "
                        f"{money(t60['state'])} a year ({pct(t60['state'] / ref, 1)} of salary).")
            if st_rules.get("note"):
                tax_text += " " + esc(st_rules["note"])
        if loc:
            tax_text += (f" Living in the city adds the {esc(loc['name'])}, about {money(t60['local'])} a year on "
                         f"{money(ref)}.")
            if loc.get("verify"):
                tax_text += " Check the current county rate before relying on this figure."
        cheaper = [x for x in ranked_left if at_ref[x["slug"]] > at_ref[c["slug"]]][-3:][::-1]
        pricier = [x for x in ranked_left if at_ref[x["slug"]] < at_ref[c["slug"]]][:3]
        neighbours = ""
        if cheaper:
            neighbours += ("Cities where the same salary leaves a little more after rent: "
                           + ", ".join(f'<a href="{u(city_path(x))}">{esc(x["name"])}</a> '
                                       f'({money(at_ref[x["slug"]])})' for x in cheaper) + ". ")
        if pricier:
            neighbours += ("A little less: " + ", ".join(
                f'<a href="{u(city_path(x))}">{esc(x["name"])}</a> ({money(at_ref[x["slug"]])})'
                for x in pricier) + ".")
        n = c["name"]
        faq = [
            (f"How much do you need to make to live in {n}?",
             f"To keep a fair-market one-bedroom ({money(c['br1'])} a month) at 30% of gross pay, about "
             f"{money(need)} a year. Sharing a two-bedroom brings that down to about {money(need_room)}. Those are "
             f"rent-based rules of thumb; your other costs decide the rest."),
            (f"What is the fair market rent in {n}?",
             f"HUD's FY{c['fy']} fair market rent for the {c['metro']} area is {money(c['br1'])} a month for a "
             f"one-bedroom and {money(c['br2'])} for a two-bedroom, including utilities. It's set at the 40th "
             f"percentile of rents for a standard unit, so many listings will be higher, especially in "
             f"popular neighbourhoods."),
            (f"Does {n} have a state or city income tax?",
             (f"{st_rules['name']} has no state income tax on wages." if st_rules.get("none") else
              f"Yes. On a {money(ref)} salary, {st_rules['name']} income tax is about {money(t60['state'])} a "
              f"year.") + (f" There's also the {loc['name']}, about {money(t60['local'])} a year at that salary."
                           if loc else "")),
            (f"How much is {money(ref)} after taxes in {n}?",
             f"About {money(t60['net'])} a year, or {money(t60['month'])} a month, for a single filer in {year}. "
             f"After a fair-market one-bedroom that leaves {money(at_ref[c['slug']])} a month for everything else."),
        ]
        title = f"Cost of living budget in {n}"
        seo_title = f"Cost of living in {n}: a budget ({year} rent + taxes)"
        if len(seo_title) > 60:
            seo_title = f"{n} cost of living budget ({year})"
        desc = (f"A one-bedroom in {n} runs about {money(c['br1'])} a month (HUD fair market rent). What you need to "
                f"earn, take-home pay after {c['state']} taxes, and a monthly budget that fits.")
        path = city_path(c)
        calc_rate = (t60["state"] + t60["local"]) / ref
        body = f"""<article class="wrap article">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/cost-of-living/')}">Cost of living by city</a> / <span>{esc(n)}</span></p>
  <h1>{esc(title)}</h1>
  <p class="dek">A modest one-bedroom in {esc(n)} costs about <strong>{money(c['br1'])} a month</strong> with utilities, {rank_phrase}. To keep it at 30% of your pay you'd earn about {money(need)} a year. Here's what different salaries leave you with after {esc(c['state'])} taxes and rent.</p>
  <p class="meta">HUD FY{c['fy']} fair market rents · {year} tax figures · As of {esc(as_of)} · Hypothetical single filer</p>
  <p class="calc-cta">{calc_link(ref, calc_rate, f"Check your take-home pay in {n}")}</p>
  <div class="prose">
<h2 id="rent">Rent in {esc(n)}</h2>
<p>HUD's fair market rent for the {esc(c['metro'])} area is {money(c['br1'])} for a one-bedroom and {money(c['br2'])} for a two-bedroom ({money(rent_of(c, True))} each if you split it). Fair market rent includes utilities and sits at the 40th percentile of rents for a standard unit: a realistic "modest apartment" number, not a luxury listing and not a bargain.</p>

<h2 id="take-home">Take-home pay in {esc(n)} by salary</h2>
{table(["Salary", "State + local tax / yr", "Take-home / month", "1-bed rent as % of take-home", "Left after 1-bed", "Left after shared 2-bed"], rows)}
<p>{tax_text}</p>

<h2 id="budget">A monthly budget for {esc(n)} on {money(need)}</h2>
<p>At {money(need)} a year (the 30% rule for a one-bedroom) you take home about {money(m)} a month. Using the four-line plan from <a href="{u('/blog/how-to-make-a-budget-you-will-keep/')}">how to make a budget you'll keep</a>:</p>
{table(["Line", "Per month", "Notes"], [
            ["Rent (1-bed, with utilities)", money(c["br1"]), "HUD fair market rent"],
            ["Other bills", money(other_bills), "Phone, insurance, transport, groceries baseline, minimum payments"],
            ["Funds", money(funds), f'Irregular costs saved monthly (<a href="{u("/blog/sinking-funds-explained/")}">sinking funds</a>)'],
            ["Goals", money(goals), "Emergency fund, debt, retirement"],
            ["Weekly number", f"{money(weekly)} a week", "Food out, fun, shopping"]])}
<p>The "other bills" line is what's left of a {pct(split['bills'])} bills budget after rent. Transport is the swing cost: if you need a car here, insurance, fuel and a payment can easily take most of it, so put your own numbers in.</p>

<h2 id="getting-around">Getting around {esc(n)}</h2>
<p>{esc(c['local_fact']['text'])} If transit covers your commute, that's what goes in the "other bills" line instead of a car payment, insurance and fuel, which together usually cost several times more. (Checked {fmt_day(c['local_fact']['checked'])}; fares change, so confirm on the agency's site.)</p>

<h2 id="compare">How {esc(n)} compares</h2>
<p>On a {money(ref)} salary, {esc(n)} leaves {money(at_ref[c['slug']])} a month after taxes and a one-bedroom: {'the most' if rank_left == 1 else 'the least' if rank_left == len(cities) else f'number {rank_left}'} of the 25 cities, and {money(abs(diff))} {'more' if diff >= 0 else 'less'} than the middle city. {neighbours}</p>
<p>See what any salary looks like without the city: <a href="{u(sal_path(60000))}">budgeting on $60,000</a>, <a href="{u(sal_path(100000))}">$100,000</a> or <a href="{u('/budget/')}">pick yours</a>.</p>

{faq_html(faq)}
<h2 id="sources">Sources</h2>
<ul><li><a href="{esc(src_url(c))}" rel="noopener">HUD FY{c['fy']} fair market rents for {esc(c['metro'])}</a> (republished table; official data at <a href="{esc(cdata['sources']['hud'])}" rel="noopener">huduser.gov</a>)</li>
<li><a href="{esc(rules['sources']['state'])}" rel="noopener">Tax Foundation: state income tax rates and brackets, {year}</a></li>
<li><a href="{esc(rules['sources']['federal'])}" rel="noopener">IRS: {year} tax inflation adjustments</a></li>
{f'<li><a href="{esc(rules["sources"][c["local"]])}" rel="noopener">{esc(loc["name"])}</a></li>' if loc else ''}
<li><a href="{esc(c['local_fact']['source'])}" rel="noopener">{esc(c['local_fact']['source_name'])}</a></li></ul>
  </div>
  {notes_block()}
  {ctx["apps_tools"](["rent-vs-buy", "take-home-pay", "afford"]) if "apps_tools" in ctx else ""}
  {magnet_box(f"col-{c['slug']}")}
</article>"""
        write(path, layout(title=seo_title, description=desc, path=path, body=body, og_type="article",
                           jsonld=article_ld(path, title, desc, faq, "Cost of living by city", "/cost-of-living/"),
                           og=og("Cost of living")))
        urls.append((path, today))

    rows = []
    for c in sorted(cities, key=lambda c: c["name"]):
        t = city_net(c, ref)
        rows.append([f'<a href="{u(city_path(c))}">{esc(c["name"])}</a>', money(c["br1"]), money(c["br2"]),
                     money(math.ceil(c["br1"] * 12 / 0.30 / 1000) * 1000), money(t["month"] - c["br1"])])
    write("/cost-of-living/", layout(
        title="Cost of living budgets for the 25 biggest US cities",
        description=(f"Rent, take-home pay and a monthly budget for the 25 largest US cities: HUD fair market "
                     f"rents, {year} state and city taxes, and the salary a one-bedroom needs."),
        path="/cost-of-living/", jsonld=[org_ld()], body=f"""<section class="wrap">
  <h1>Cost of living budgets by city</h1>
  <p class="dek">For each of the 25 largest US cities: what a modest apartment costs, what you'd need to earn, and what's left after {year} state and local taxes.</p>
  <p class="calc-cta">{calc_link(ref, 0, "Calculate your exact take-home pay")}</p>
  {table(["City", "1-bed rent", "2-bed rent", "Salary for 1-bed at 30%", f"Left after 1-bed on {money(ref)}"], rows)}
  {notes_block()}
</section>"""))
    urls.append(("/cost-of-living/", today))
    return urls


# ================================================================================ debt payoff timelines
DEBT_LEVELS = [2500, 5000, 7500, 10000, 15000, 20000, 25000, 30000, 40000, 50000]
DETAIL_EXTRA = {2500: 100, 5000: 150, 7500: 200, 10000: 250, 15000: 300, 20000: 400, 25000: 500, 30000: 500,
                40000: 600, 50000: 750}
EXTRAS = [0, 100, 250, 500, 1000]
# (name, share of total, APR %, minimum: ("card", pct) or ("loan", months left))
MIXES = {
    "small": [("Card A", 0.55, 24.99, ("card", 0.03)), ("Card B", 0.30, 19.99, ("card", 0.03)),
              ("Store card", 0.15, 29.99, ("card", 0.03))],
    "mid": [("Card A", 0.30, 24.99, ("card", 0.03)), ("Card B", 0.20, 21.99, ("card", 0.03)),
            ("Store card", 0.05, 29.99, ("card", 0.03)), ("Personal loan", 0.45, 12.99, ("loan", 48))],
    "large": [("Card A", 0.25, 24.99, ("card", 0.03)), ("Card B", 0.15, 21.99, ("card", 0.03)),
              ("Personal loan", 0.20, 12.99, ("loan", 48)), ("Car loan", 0.40, 7.49, ("loan", 60))],
    "largest": [("Card A", 0.15, 24.99, ("card", 0.03)), ("Card B", 0.10, 21.99, ("card", 0.03)),
                ("Personal loan", 0.15, 12.99, ("loan", 48)), ("Car loan", 0.25, 7.49, ("loan", 60)),
                ("Student loan", 0.35, 5.5, ("loan", 120))],
}


def mix_for(total: int) -> str:
    return "small" if total <= 7500 else "mid" if total <= 20000 else "large" if total <= 30000 else "largest"


def amortized(balance: float, apr: float, months: int) -> float:
    r = apr / 100 / 12
    return balance * r / (1 - (1 + r) ** -months)


def debts_for(total: int) -> list[dict]:
    out = []
    for i, (name, share, apr, (kind, val)) in enumerate(MIXES[mix_for(total)]):
        bal = round(total * share)
        mn = max(25, round(bal * val)) if kind == "card" else round(amortized(bal, apr, val))
        out.append({"index": i, "name": name, "balance": bal, "apr": apr, "minPayment": mn, "kind": kind})
    return out


def payoff(debts: list[dict], extra: float = 0, strategy: str = "avalanche", schedule: bool = False) -> dict:
    """Port of debtPayoff() in the calculators' lib/calc.js: fixed monthly budget = minimums + extra,
    freed-up minimums roll into the target debt."""
    lst = [dict(d) for d in debts]
    budget = sum(d["minPayment"] for d in lst) + extra
    order = sorted(lst, key=(lambda d: (-d["apr"], d["balance"])) if strategy == "avalanche"
                   else (lambda d: (d["balance"], -d["apr"])))
    month, interest, paid_off, rows = 0, 0.0, {}, []
    while any(d["balance"] > 0.005 for d in lst):
        month += 1
        if month > 1200:
            return {"feasible": False, "months": math.inf, "interest": math.inf, "budget": budget}
        for d in lst:
            if d["balance"] > 0:
                i = d["balance"] * d["apr"] / 100 / 12
                d["balance"] += i
                interest += i
        avail = budget
        for d in lst:
            if d["balance"] > 0:
                pay = min(d["minPayment"], d["balance"], avail)
                d["balance"] -= pay
                avail -= pay
        for o in order:
            if avail <= 0:
                break
            d = lst[o["index"]]
            if d["balance"] > 0:
                pay = min(d["balance"], avail)
                d["balance"] -= pay
                avail -= pay
        if schedule:
            rows.append(sum(max(0, d["balance"]) for d in lst))
        for d in lst:
            if d["balance"] <= 0.005 and d["name"] not in paid_off:
                d["balance"] = 0
                paid_off[d["name"]] = month
    return {"feasible": True, "months": month, "interest": interest, "budget": budget,
            "order": [o["name"] for o in order], "paid_off": paid_off, "schedule": rows}


def extra_for_months(debts, months: int) -> float:
    """Smallest extra (to $10) that clears everything within `months` using avalanche."""
    lo, hi = 0, 20000
    if payoff(debts, 0)["months"] <= months:
        return 0
    while hi - lo > 10:
        mid = (lo + hi) // 2
        if payoff(debts, mid)["months"] <= months:
            hi = mid
        else:
            lo = mid
    return hi


def yrs(m: float) -> str:
    if m == math.inf:
        return "never"
    y, r = divmod(int(m), 12)
    parts = ([f"{y} year{'s' if y != 1 else ''}"] if y else []) + ([f"{r} month{'s' if r != 1 else ''}"] if r else [])
    return " ".join(parts) or "0 months"


EXAMPLES = [5000, 15000, 30000]  # worked examples on the one debt payoff page


def load_debt_notes() -> dict[int, str]:
    text = (DATA.parent / "debt-examples.md").read_text()
    out = {int(k): v.strip() for k, v in re.findall(r"^## (\d+)\n(.*?)(?=^## |\Z)", text, re.S | re.M)}
    missing = [x for x in EXAMPLES if x not in out]
    if missing:
        raise SystemExit(f"content/debt-examples.md: no notes for {missing}")
    return out


def build_debt(ctx: dict) -> list[tuple[str, str]]:
    """/debt-payoff/: one page with an in-page calculator (static/debt-calc.js, same maths as payoff()) and three
    worked examples. The ten per-amount pages it replaced (Nov 2026) 301 to it."""
    cfg, u, absu, layout, write = ctx["CFG"], ctx["u"], ctx["absu"], ctx["layout"], ctx["write"]
    org_ld, magnet_box = ctx["org_ld"], ctx["magnet_box"]
    today = ctx["today"]
    calc = cfg.get("calculators_url", cfg["url"] + "/calculators").rstrip("/") + "/debt-payoff/"
    shop = ctx.get("shop", {})
    notes = load_debt_notes()
    for t in DEBT_LEVELS:
        ctx["redirects"].append((f"/debt-payoff/{t}-debt/", "/debt-payoff/"))

    sections, faq = [], []
    for total in EXAMPLES:
        debts = debts_for(total)
        x = DETAIL_EXTRA[total]
        mins = sum(d["minPayment"] for d in debts)
        av, sb = payoff(debts, x, "avalanche"), payoff(debts, x, "snowball")
        e36 = extra_for_months(debts, 36)
        rows_debts = [[esc(d["name"]), money(d["balance"]), f'{d["apr"]:.2f}%', money(d["minPayment"])] for d in debts]
        rows_cmp = []
        for e in sorted(set(EXTRAS + [x])):
            a, s_ = payoff(debts, e, "avalanche"), payoff(debts, e, "snowball")
            rows_cmp.append([("Minimums only" if e == 0 else f"+{money(e)}"), money(mins + e),
                             yrs(a["months"]), money(a["interest"]), yrs(s_["months"]), money(s_["interest"])])
        q = urlencode({"d": json.dumps([{k: d[k] for k in ("name", "balance", "apr", "minPayment")} for d in debts],
                                       separators=(",", ":")), "extra": x})
        sid = f"example-{total}"
        sections.append(f"""<section aria-labelledby="{sid}">
<h2 id="{sid}">Worked example: {money(total)} of debt</h2>
{table(["Debt", "Balance", "APR", "Minimum"], rows_debts)}
{ctx["markdown"](notes[total])[0]}
{table(["Extra a month", "Total a month", "Avalanche: time", "Avalanche: interest", "Snowball: time", "Snowball: interest"], rows_cmp)}
<p>To be debt-free in three years with this mix, pay about {money(mins + e36)} a month. <button type="button" class="link-btn" data-load="{esc(json.dumps(debts))}" data-extra="{x}">Load this example into the calculator</button> or <a href="{esc(calc)}?{esc(q)}" data-calc="debt-payoff">open it in the full calculator</a>.</p>
</section>""")
        faq.append((f"How long does it take to pay off {money(total)} of debt?",
                    f"In this page's example ({len(debts)} debts, {money(mins)} of minimums), paying {money(mins + x)} a "
                    f"month clears it in about {yrs(av['months'])} with the avalanche method and {money(av['interest'])} "
                    f"of interest (snowball: {yrs(sb['months'])}, {money(sb['interest'])}). Your own rates change "
                    f"this; the calculator above uses them."))
    faq += [("Snowball or avalanche: which is better?",
             "Avalanche (highest rate first) always costs the same or less interest. Snowball (smallest balance "
             "first) gives you an earlier win. The gap depends on your mix: in the examples here it ranges from "
             "about $58 to $522. If the early win keeps you going, snowball is worth it."),
            ("Does the calculator store my numbers?",
             "No. It runs in your browser and nothing you type is sent anywhere.")]
    tool = shop.get("debt-free-date-planner")
    tool_html = (f'<p>Want a payment log and a debt-free date on paper? <strong>{esc(tool["name"])}</strong> '
                 f'({money(tool["price"])}) is a guide plus spreadsheet. <a href="{u("/shop/#item-debt-free-date-planner")}">'
                 f'See it in the shop</a>.</p>') if tool else ""
    start = debts_for(15000)
    rows_in = "".join(f"""<tr><td><label class="sr-only" for="dn{i}">Debt {i + 1} name</label><input id="dn{i}" name="name" value="{esc(d['name']) if d else ''}" autocomplete="off"></td>
<td><label class="sr-only" for="db{i}">Debt {i + 1} balance in dollars</label><input id="db{i}" name="balance" type="number" min="0" step="1" inputmode="decimal" value="{d['balance'] if d else ''}"></td>
<td><label class="sr-only" for="da{i}">Debt {i + 1} APR percent</label><input id="da{i}" name="apr" type="number" min="0" max="99" step="0.01" inputmode="decimal" value="{d['apr'] if d else ''}"></td>
<td><label class="sr-only" for="dm{i}">Debt {i + 1} minimum payment in dollars</label><input id="dm{i}" name="min" type="number" min="0" step="1" inputmode="decimal" value="{d['minPayment'] if d else ''}"></td></tr>"""
                      for i, d in enumerate(start + [None] * (6 - len(start))))
    title = "Debt payoff calculator: snowball vs avalanche"
    desc = ("Put in your debts and see your debt-free date with the snowball and avalanche methods, the interest "
            "each costs, and three worked examples from $5,000 to $30,000.")
    body = f"""<article class="wrap article">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <span>Debt payoff</span></p>
  <h1>Debt payoff calculator: snowball vs avalanche</h1>
  <p class="dek">Enter your debts and what you can pay each month. You'll see when you'd be debt-free with each method and what it costs in interest. Below it, three worked examples show how the numbers play out.</p>
  <p class="meta">Runs in your browser; nothing is sent anywhere · Computed monthly at the APR you enter</p>
  <form class="debt-calc" id="debt-calc" novalidate>
    <div class="table" tabindex="0"><table><caption class="sr-only">Your debts</caption>
      <thead><tr><th scope="col">Debt</th><th scope="col">Balance ($)</th><th scope="col">APR (%)</th><th scope="col">Minimum ($/mo)</th></tr></thead>
      <tbody id="debt-rows">{rows_in}</tbody></table></div>
    <p class="debt-extra"><label for="extra">Extra each month on top of the minimums ($)</label>
      <input id="extra" name="extra" type="number" min="0" step="1" inputmode="decimal" value="{DETAIL_EXTRA[15000]}"></p>
    <p><button type="submit" class="btn">Work it out</button></p>
    <div class="debt-out" id="debt-out" aria-live="polite"><noscript><p>The calculator needs JavaScript. The worked examples below don't, and the <a href="{esc(calc)}">full calculator</a> is another option.</p></noscript></div>
  </form>
  <div class="prose">
<p>How it works: you pay a fixed total each month (all the minimums plus your extra). The extra goes to one target debt; when a debt is paid off, its minimum rolls on to the next one. <strong>Avalanche</strong> targets the highest rate first, <strong>snowball</strong> the smallest balance. More in <a href="{u('/blog/debt-avalanche-vs-snowball/')}">debt avalanche vs snowball</a>.</p>
{"".join(sections)}
<h2 id="speed-up">Ways to speed it up</h2>
<p>The fastest lever is usually the rate on your cards: a 0% <a href="{u('/compare/best-balance-transfer-cards/')}">balance transfer</a> (watch the fee and the rate after the intro) or simply asking your card company for a lower APR. Then find the extra payment in the <a href="{u('/budget/')}">budget for your salary</a>.</p>
{tool_html}
{faq_html(faq)}
  </div>
  <p class="disclaimer">Example debts, rates and payments are hypothetical. Interest is calculated monthly at the APR shown, with on-time payments, no new charges, fees or rate changes. Card minimums are held at their starting amount. {esc(cfg['disclaimer'])}</p>
   {ctx["apps_tools"](["credit-card-minimum", "student-loans", "afford"]) if "apps_tools" in ctx else ""}
   {magnet_box("debt-payoff")}
</article>
<script src="{u('/debt-calc.js')}" defer></script>"""
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": title, "description": desc,
           "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "url": absu("/debt-payoff/"),
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": org_ld()},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q_, "acceptedAnswer": {"@type": "Answer", "text": a}} for q_, a in faq]}]
    write("/debt-payoff/", layout(title=title, description=desc, path="/debt-payoff/", body=body, jsonld=ld))
    return [("/debt-payoff/", today)]
