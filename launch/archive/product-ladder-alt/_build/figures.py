"""Every number printed in the PDFs is computed here (no hand-typed results)."""
from __future__ import annotations

from datetime import date

from debtsim import EXAMPLE, EXAMPLE_EXTRA, amortize, simulate

START = date(2026, 12, 1)


def month_label(n: int) -> str:
    """Payment month n (1 = START) as 'Mon YYYY'."""
    y, m = divmod(START.month - 1 + n - 1, 12)
    return date(START.year + y, m + 1, 1).strftime("%b %Y")


# ---------------------------------------------------------------- debt planner guide
def planner_context() -> dict:
    res = {m: simulate(EXAMPLE, m, EXAMPLE_EXTRA) for m in ("avalanche", "snowball", "custom", "minimums")}
    debts = []
    for i, d in enumerate(EXAMPLE):
        debts.append({
            "name": d.name, "balance": d.balance, "apr": d.apr, "minimum": d.minimum, "custom": d.custom,
            "interest_now": d.balance * d.apr / 1200,
            "av_rank": res["avalanche"].order.index(i) + 1, "sb_rank": res["snowball"].order.index(i) + 1,
            "av": res["avalanche"].payoff_month[i], "sb": res["snowball"].payoff_month[i],
            "cu": res["custom"].payoff_month[i], "mn": res["minimums"].payoff_month[i],
        })
    methods = []
    for key, label in (("avalanche", "Avalanche"), ("snowball", "Snowball"), ("custom", "Custom"),
                       ("minimums", "Minimums only")):
        r = res[key]
        methods.append({"key": key, "label": label, "months": r.months, "date": month_label(r.months),
                        "interest": r.total_interest, "paid": r.total_paid,
                        "first": min(v for v in r.payoff_month.values() if v)})
    av = res["avalanche"]
    first_rows = []
    for m in range(1, 7):
        first_rows.append({"m": m, "date": month_label(m), "pays": av.payments[m - 1], "bals": av.balances[m - 1],
                           "interest": av.interest[m - 1], "total": sum(av.payments[m - 1]),
                           "owed": sum(av.balances[m - 1])})
    pmt, rows_x = amortize(18500, 5.8, 120, 50)
    _, rows_0 = amortize(18500, 5.8, 120, 0)
    loan = {"P": 18500, "apr": 5.8, "term": 120, "extra": 50, "pmt": pmt,
            "int0": sum(r[2] for r in rows_0), "intx": sum(r[2] for r in rows_x), "monthsx": len(rows_x),
            "first": rows_0[0], "last": rows_0[-1]}
    loan["saved"] = loan["int0"] - loan["intx"]
    total_bal = sum(d.balance for d in EXAMPLE)
    total_min = sum(d.minimum for d in EXAMPLE)
    return {"debts": debts, "methods": methods, "m": {x["key"]: x for x in methods}, "extra": EXAMPLE_EXTRA,
            "total_bal": total_bal, "total_min": total_min, "budget": total_min + EXAMPLE_EXTRA,
            "first_rows": first_rows, "loan": loan, "start": START.strftime("%B %Y"),
            "av_sb_diff": res["snowball"].total_interest - res["avalanche"].total_interest,
            "saved_vs_min": res["minimums"].total_interest - res["avalanche"].total_interest,
            "months_vs_min": res["minimums"].months - res["avalanche"].months,
            "names_av": [EXAMPLE[i].name for i in av.order],
            "names_sb": [EXAMPLE[i].name for i in res["snowball"].order],
            "names_cu": [EXAMPLE[i].name for i in res["custom"].order]}


# ---------------------------------------------------------------- investing kit
def fv_monthly(pmt: float, annual: float, years: int, start: float = 0.0) -> float:
    """Future value of monthly contributions at the END of each month, monthly compounding."""
    r = annual / 12
    n = years * 12
    bal = start
    for _ in range(n):
        bal = bal * (1 + r) + pmt
    return bal


def investing_context() -> dict:
    rate = 0.06
    amounts = [100, 250, 500]
    years = [10, 20, 30, 40]
    grid = [{"pmt": a, "cells": [{"years": y, "fv": fv_monthly(a, rate, y), "in": a * 12 * y} for y in years]}
            for a in amounts]
    rates = [0.04, 0.06, 0.08]
    rate_rows = [{"rate": r, "fv": fv_monthly(200, r, 30), "in": 200 * 360} for r in rates]
    # early vs late
    a_at_35 = fv_monthly(200, rate, 10)
    a_at_65 = a_at_35 * (1 + rate / 12) ** (30 * 12)
    b_at_65 = fv_monthly(200, rate, 30)
    early = {"a35": a_at_35, "a65": a_at_65, "a_in": 200 * 120, "b65": b_at_65, "b_in": 200 * 360}
    # fees
    fees = []
    for f in (0.0005, 0.0050, 0.0100):
        fees.append({"fee": f * 100, "fv": fv_monthly(300, rate - f, 30), "yearly_on_10k": 10000 * f})
    for x in fees:
        x["lost"] = fees[0]["fv"] - x["fv"]
    # employer match
    salary = 50000
    match = [
        {"label": "100% match up to 4% of pay", "you": 0.04 * salary, "emp": 0.04 * salary},
        {"label": "50% match up to 6% of pay", "you": 0.06 * salary, "emp": 0.03 * salary},
    ]
    # Roth vs Traditional
    growth = (1 + rate) ** 30
    pre = 1000
    rt = []
    for later in (0.12, 0.22, 0.24):
        trad = pre * growth * (1 - later)
        roth = pre * (1 - 0.22) * growth
        rt.append({"later": later * 100, "trad": trad, "roth": roth})
    one_time = {"amt": 1000, "y": [(y, 1000 * (1 + rate) ** y) for y in (10, 20, 30, 40)]}
    # chart: $250/month for 40 years at 6%
    W, H, pad = 600, 260, 0
    yearly = [(y, fv_monthly(250, rate, y), 250 * 12 * y) for y in range(0, 41)]
    top = yearly[-1][1]
    def pt(y, v):
        return f"{y / 40 * W:.1f},{H - v / top * H:.1f}"
    chart = {"W": W, "H": H, "total": f"0,{H} " + " ".join(pt(y, v) for y, v, _ in yearly) + f" {W},{H}",
             "contrib": f"0,{H} " + " ".join(pt(y, c) for y, _, c in yearly) + f" {W},{H}",
             "end": yearly[-1][1], "end_in": yearly[-1][2], "mid": yearly[20],
             "grid": [(round(H - g / top * H, 1), g) for g in (100000, 200000, 300000, 400000)]}
    return {"chart": chart, "rate": rate * 100, "grid": grid, "years": years, "rate_rows": rate_rows, "early": early,
            "fees": fees, "salary": salary, "match": match, "growth30": growth, "rt": rt, "pre": pre,
            "one_time": one_time, "rule72": 72 / (rate * 100)}


# ---------------------------------------------------------------- covers
def cover_context(which: str) -> dict:
    if which == "planner":
        ctx = planner_context()
        return {"ctx": ctx}
    if which == "invest":
        return {"ctx": investing_context()}
    return {"ctx": {}}


if __name__ == "__main__":
    import json
    print(json.dumps(planner_context()["methods"], indent=1, default=str))
    ic = investing_context()
    for k in ("grid", "rate_rows", "early", "fees", "match", "rt", "one_time"):
        print(k, ic[k])
