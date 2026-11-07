"""Automatic number checks: recompute the money maths a script states and flag mismatches in review.

Two independent oracles, both permissive licences (picked in research/scouting/oss-landscape.md):
* numpy-financial (BSD-3): loan payments (pmt), total interest, payoff time (nper), compound growth (fv).
* Tax-Calculator / taxcalc (CC0, PSLmodels): US federal income tax and payroll tax for a wage earner.

    pip install -e ".[numbers]"        # numpy-financial + taxcalc (taxcalc is big: pandas, numba)

What it reads:
1. `script.calcs`: figures the writer declared, e.g.
     {"kind": "loan_payment", "principal": 25000, "rate": 7.5, "years": 5, "claimed": 501}
   kinds: loan_payment, total_interest, payoff_months, future_value, federal_tax, payroll_tax.
2. Sentences in the narration, on-screen text and caption that state a computed figure, e.g.
     "A $25,000 car loan at 7.5% for 5 years costs about $501 a month."
     "Pay $200 a month on $5,000 at 22% APR and it's gone in 32 months."
     "Invest $300 a month at 7% for 30 years and you'd have about $366,000."
     "Federal income tax on a $75,000 salary (single, 2026) is about $7,670."
   Sentences it can't parse fully are left alone (they stay on the human fact-check list).

A match must be within $1 or 1% (5% when the script hedges with "about", "roughly", "~"...), and
payoff times within 1 month. A mismatch on a declared figure blocks approval; a mismatch parsed from a
sentence is flagged (warn) with both numbers, since a sentence can be misread. When a library
isn't installed, the figure is listed as unverified (warn), never silently passed.
"""
from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from functools import lru_cache

MONEY = r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s*(k|K|thousand|million|m|M)?\b"
PCT = r"(\d+(?:\.\d+)?)\s?(?:%|percent)"
TERM = r"(\d+(?:\.\d+)?)[\s-]*(year|yr|month|mo)s?\b"
HEDGE = re.compile(r"\b(about|around|roughly|nearly|almost|approximately|close to|just (?:over|under)|over|under)\b|~|≈",
                   re.I)
MONTHLY = re.compile(r"(?:a|per|each|every) month|/\s?mo(?:nth)?\b|monthly", re.I)
LOAN = re.compile(r"\b(loan|mortgage|borrow\w*|financ\w*|car note|debt|balance|card|apr)\b", re.I)
GROWTH = re.compile(r"\b(grow\w*|becomes?|turns? into|end up with|worth|you'?d have|you'?ll have|compound\w*|invest\w*|sav\w*)\b",
                    re.I)
TAX = re.compile(r"\bfederal (?:income )?tax\b|\bincome tax\b", re.I)
FICA = re.compile(r"\b(fica|payroll tax|social security and medicare)\b", re.I)


@dataclass
class Figure:
    kind: str
    text: str
    claimed: float
    computed: float | None = None
    inputs: dict = field(default_factory=dict)
    status: str = "unverified"  # ok | mismatch | unverified
    note: str = ""
    declared: bool = False  # from script.calcs (exact) rather than parsed from a sentence

    def as_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- oracles
def _npf():
    try:
        import numpy_financial as npf
        return npf
    except ImportError:
        return None


def loan_payment(principal: float, rate: float, months: int) -> float:
    npf = _npf()
    if npf is None:
        raise ImportError("numpy-financial")
    return float(-npf.pmt(rate / 100 / 12, months, principal))


def payoff_months(balance: float, rate: float, payment: float) -> float:
    npf = _npf()
    if npf is None:
        raise ImportError("numpy-financial")
    n = float(npf.nper(rate / 100 / 12, -payment, balance))
    return math.inf if math.isnan(n) else n


def future_value(rate: float, years: float, monthly: float = 0.0, initial: float = 0.0) -> float:
    npf = _npf()
    if npf is None:
        raise ImportError("numpy-financial")
    return float(npf.fv(rate / 100 / 12, round(years * 12), -monthly, -initial))


@lru_cache(maxsize=256)
def _taxcalc(wages: float, married: bool, year: int) -> tuple[float, float]:
    """(federal income tax, employee payroll tax) for one wage earner taking the standard deduction."""
    import pandas as pd
    import taxcalc as tc
    df = pd.DataFrame({"RECID": [1], "MARS": [2 if married else 1], "XTOT": [2 if married else 1],
                       "e00200": [wages], "e00200p": [wages], "e00200s": [0.0], "FLPDYR": [year]})
    rec = tc.Records(data=df, start_year=year, gfactors=None, weights=None, adjust_ratios=None)
    calc = tc.Calculator(policy=tc.Policy(), records=rec)
    calc.calc_all()
    return float(calc.array("iitax")[0]), float(calc.array("payrolltax")[0]) / 2  # payrolltax counts both halves


def federal_tax(wages: float, married: bool = False, year: int | None = None) -> float:
    return _taxcalc(float(wages), married, year or date.today().year)[0]


def payroll_tax(wages: float, year: int | None = None) -> float:
    return _taxcalc(float(wages), False, year or date.today().year)[1]


# --------------------------------------------------------------------------- parsing
def _money(m: re.Match) -> float:
    v = float(m.group(1).replace(",", "") + (m.group(2) or ""))
    unit = (m.group(3) or "").lower()
    return v * (1000 if unit in ("k", "thousand") else 1_000_000 if unit in ("m", "million") else 1)


def _months(m: re.Match) -> int:
    n = float(m.group(1))
    return round(n * 12) if m.group(2).lower().startswith(("year", "yr")) else round(n)


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z$\"'(])|\n+", text or "") if s.strip()]


def _after(sentence: str, m: re.Match, pattern: re.Pattern, window: int = 24) -> bool:
    """Does `pattern` follow this amount, before the next amount?"""
    tail = sentence[m.end():m.end() + window]
    nxt = tail.find("$")
    return bool(pattern.search(tail[:nxt] if nxt >= 0 else tail))


def parse(sentence: str) -> Figure | None:
    """One computed figure from one sentence, or None if it isn't a full, checkable statement."""
    monies = list(re.finditer(MONEY, sentence))
    pct = re.search(PCT, sentence)
    term = re.search(TERM, sentence)
    year = re.search(r"\b(20[2-4]\d)\b", sentence)
    if TAX.search(sentence) and len(monies) >= 2 and not FICA.search(sentence):
        wages, claimed = _money(monies[0]), _money(monies[-1])
        married = bool(re.search(r"\bmarried\b|\bjointly\b|\bcouple\b", sentence, re.I))
        return Figure("federal_tax", sentence, claimed,
                      inputs={"wages": wages, "married": married, "year": int(year.group(1)) if year else None})
    if FICA.search(sentence) and len(monies) >= 2:
        return Figure("payroll_tax", sentence, _money(monies[-1]),
                      inputs={"wages": _money(monies[0]), "year": int(year.group(1)) if year else None})
    if not pct or not monies:
        return None
    rate = float(pct.group(1))
    monthly_amts = [m for m in monies if _after(sentence, m, MONTHLY)]
    others = [m for m in monies if m not in monthly_amts]
    if LOAN.search(sentence):
        # payment stated before the time ("$275/month: about 18 months") = how long to pay it off;
        # time before the payment ("for 5 years costs $501 a month") = the payment on a fixed term
        mm = next((t for t in re.finditer(TERM, sentence) if not t.group(2).lower().startswith("y")
                   and monthly_amts and t.start() > monthly_amts[0].end()), None)
        if mm and others:
            return Figure("payoff_months", sentence, float(_months(mm)),
                          inputs={"balance": _money(others[0]), "rate": rate, "payment": _money(monthly_amts[0])})
        if term and re.search(r"\bin interest\b|\binterest (?:total|alone)\b|\btotal interest\b", sentence, re.I) \
                and len(others) >= 2:
            return Figure("total_interest", sentence, _money(others[-1]),
                          inputs={"principal": _money(others[0]), "rate": rate, "months": _months(term)})
        if term and monthly_amts and others:
            return Figure("loan_payment", sentence, _money(monthly_amts[0]),
                          inputs={"principal": _money(others[0]), "rate": rate, "months": _months(term)})
    if GROWTH.search(sentence) and term and len(monies) >= 2:
        claimed = monies[-1]
        if claimed in monthly_amts:
            return None
        monthly = _money(monthly_amts[0]) if monthly_amts else 0.0
        initial = _money(others[0]) if others and others[0] is not claimed else 0.0
        if not monthly and not initial:
            return None
        return Figure("future_value", sentence, _money(claimed),
                      inputs={"rate": rate, "years": _months(term) / 12, "monthly": monthly, "initial": initial})
    return None


def compute(fig: Figure) -> Figure:
    i = fig.inputs
    try:
        if fig.kind == "loan_payment":
            fig.computed = loan_payment(i["principal"], i["rate"], int(i.get("months") or i["years"] * 12))
        elif fig.kind == "total_interest":
            n = int(i.get("months") or i["years"] * 12)
            fig.computed = loan_payment(i["principal"], i["rate"], n) * n - i["principal"]
        elif fig.kind == "payoff_months":
            fig.computed = payoff_months(i["balance"], i["rate"], i["payment"])
        elif fig.kind == "future_value":
            fig.computed = future_value(i["rate"], i["years"], i.get("monthly", 0), i.get("initial", 0))
        elif fig.kind == "federal_tax":
            fig.computed = federal_tax(i["wages"], bool(i.get("married")), i.get("year"))
        elif fig.kind == "payroll_tax":
            fig.computed = payroll_tax(i["wages"], i.get("year"))
        else:
            fig.note = f"unknown kind {fig.kind}"
            return fig
    except ImportError as e:
        lib = "taxcalc" if "tax" in fig.kind else "numpy-financial"
        fig.note = f"{lib} isn't installed ({e.name or e}); pip install -e \".[numbers]\""
        return fig
    except (KeyError, TypeError, ValueError) as e:
        fig.note = f"couldn't compute: {e}"
        return fig
    hedged = bool(HEDGE.search(fig.text))
    if fig.kind == "payoff_months":
        ok = math.isfinite(fig.computed) and abs(fig.computed - fig.claimed) <= (2 if hedged else 1)
        fig.note = "never paid off: the payment doesn't cover the interest" if not math.isfinite(fig.computed) else ""
    else:
        tol = max(1.0, abs(fig.claimed) * (0.05 if hedged else 0.01))
        ok = abs(fig.computed - fig.claimed) <= tol
    fig.status = "ok" if ok else "mismatch"
    return fig


def check_script(script: dict, caption: str = "") -> list[Figure]:
    figs: list[Figure] = []
    for c in script.get("calcs") or []:
        c = dict(c)
        kind, claimed = c.pop("kind", ""), c.pop("claimed", None)
        if claimed is None:
            continue
        figs.append(Figure(kind, c.pop("text", "") or f"{kind} (declared)", float(claimed), inputs=c, declared=True))
    texts = [script.get("hook", "")]
    for seg in script.get("segments") or []:
        texts += [seg.get("narration", ""), seg.get("on_screen_text", "")]
    texts += [script.get("description", ""), caption]
    seen = set()
    for t in texts:
        for s in sentences(t):
            key = re.sub(r"\W+", " ", s.lower()).strip()
            if key in seen:
                continue
            seen.add(key)
            f = parse(s)
            if f:
                figs.append(f)
    return [compute(f) for f in figs]


def _fmt(f: Figure) -> str:
    if f.kind == "payoff_months":
        return f"{f.computed:.1f} months" if f.computed is not None and math.isfinite(f.computed) else "never"
    return f"${f.computed:,.2f}" if f.computed is not None else "?"


def as_check(figs: list[Figure]):
    """One guardrails Check summarising the figures (None when the script states no computed figures)."""
    from .guardrails import Check
    if not figs:
        return None
    bad = [f for f in figs if f.status == "mismatch"]
    unverified = [f for f in figs if f.status == "unverified"]
    if bad:
        detail = "; ".join(f"“{f.text[:90]}” says {f.claimed:,.0f}{' months' if f.kind == 'payoff_months' else ''}, "
                           f"the maths gives {_fmt(f)}" for f in bad[:3])
        # declared figures are exact, so a mismatch blocks; a parsed sentence could be misread, so it flags
        level = "block" if any(f.declared for f in bad) else "warn"
        return Check("number_check", level, f"{len(bad)} computed figure(s) don't add up: {detail}")
    if unverified:
        return Check("number_check", "warn", f"{len(unverified)} computed figure(s) not verified: "
                     + "; ".join(f.note or f.kind for f in unverified[:3]))
    return Check("number_check", "ok", f"{len(figs)} computed figure(s) verified "
                 "(numpy-financial / Tax-Calculator)")


def register(sub, factory_fn) -> None:
    s = sub.add_parser("numbers", help="recompute the loan, growth and tax figures a post states")
    s.add_argument("post_id", type=int, nargs="?")
    s.add_argument("--text", default="", help="check a sentence instead of a post")

    def cmd(a):
        if a.text:
            figs = [compute(f) for f in [parse(x) for x in sentences(a.text)] if f]
        else:
            f = factory_fn(a)
            post = f.db.get("posts", a.post_id)
            if not post:
                raise SystemExit(f"No post #{a.post_id}")
            figs = check_script(post.get("script") or {}, post.get("caption", ""))
        if not figs:
            print("No computed figures found.")
        for g in figs:
            print(f"[{g.status}] {g.kind}: claimed {g.claimed:,.2f}, computed {_fmt(g)}  {g.note}\n    {g.text[:140]}")
        if any(g.status == "mismatch" for g in figs):
            raise SystemExit(2)
    s.set_defaults(func=cmd)
