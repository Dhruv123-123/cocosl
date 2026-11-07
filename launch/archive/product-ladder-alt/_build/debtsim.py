"""Reference simulation for the Debt Payoff Planner spreadsheet.

Same monthly model as the workbook, so the two can be cross-checked:
  1. each balance grows by one month of interest (APR / 12),
  2. every debt gets its minimum (capped at what is owed),
  3. the rest of the monthly budget goes to debts in priority order.
The monthly budget = sum of all minimums + extra (+ one-time lump in its month),
so a paid-off debt's minimum rolls to the next target. "Minimums only" pays
each debt its own minimum with no rollover and no extra.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MONTHS = 360


@dataclass
class Debt:
    name: str
    balance: float
    apr: float          # percent, e.g. 24.9
    minimum: float
    custom: int | None = None


@dataclass
class Result:
    method: str
    order: list[int]                      # indexes into the debts list, priority order
    months: int | None                    # None = not paid off within MONTHS
    total_interest: float
    total_paid: float
    payoff_month: dict[int, int | None]   # debt index -> month
    interest_by_debt: dict[int, float]
    balances: list[list[float]] = field(repr=False, default_factory=list)  # [month][debt idx] end balance
    payments: list[list[float]] = field(repr=False, default_factory=list)
    interest: list[float] = field(repr=False, default_factory=list)


def order_for(debts: list[Debt], method: str) -> list[int]:
    active = [i for i, d in enumerate(debts) if d.balance > 0]
    if method == "avalanche":
        return sorted(active, key=lambda i: (-debts[i].apr, debts[i].balance, i))
    if method == "snowball":
        return sorted(active, key=lambda i: (debts[i].balance, -debts[i].apr, i))
    if method == "custom":
        return sorted(active, key=lambda i: ((debts[i].custom if (debts[i].custom or 0) > 0 else 999), i))
    if method == "minimums":
        return order_for(debts, "avalanche")
    raise ValueError(method)


def simulate(debts: list[Debt], method: str, extra: float = 0.0, lump: float = 0.0, lump_month: int = 0,
             months: int = MONTHS) -> Result:
    order = order_for(debts, method)
    bal = {i: float(debts[i].balance) for i in order}
    total_min = sum(debts[i].minimum for i in order)
    rollover = method != "minimums"
    payoff: dict[int, int | None] = {i: None for i in order}
    int_by: dict[int, float] = {i: 0.0 for i in order}
    hist_bal, hist_pay, hist_int = [], [], []
    tot_int = tot_paid = 0.0
    done_month = None
    for m in range(1, months + 1):
        grown = {i: bal[i] * (1 + debts[i].apr / 1200) for i in order}
        mins = {i: min(debts[i].minimum, grown[i]) for i in order}
        budget = total_min + extra + (lump if m == lump_month else 0.0)
        pool = (budget - sum(mins.values())) if rollover else 0.0
        used = 0.0
        month_int = month_paid = 0.0
        pay = {}
        for i in order:
            ex = max(0.0, min(pool - used, grown[i] - mins[i]))
            used += ex
            end = grown[i] - mins[i] - ex
            if end < 0.005:
                end = 0.0
            month_int += grown[i] - bal[i]
            int_by[i] += grown[i] - bal[i]
            pay[i] = mins[i] + ex
            month_paid += pay[i]
            if end == 0 and payoff[i] is None and bal[i] > 0:
                payoff[i] = m
            bal[i] = end
        tot_int += month_int
        tot_paid += month_paid
        hist_bal.append([bal.get(i, 0.0) for i in range(len(debts))])
        hist_pay.append([pay.get(i, 0.0) for i in range(len(debts))])
        hist_int.append(month_int)
        if done_month is None and sum(bal.values()) == 0:
            done_month = m
    return Result(method, order, done_month, tot_int, tot_paid, payoff, int_by, hist_bal, hist_pay, hist_int)


def amortize(principal: float, apr: float, term: int, extra: float = 0.0):
    """Standard fixed-payment loan, optional extra principal each month."""
    r = apr / 1200
    pmt = principal / term if r == 0 else principal * r / (1 - (1 + r) ** -term)
    bal, rows = principal, []
    m = 0
    while bal > 0.005 and m < 600:
        m += 1
        interest = bal * r
        pay = min(bal + interest, pmt + extra)
        bal = bal + interest - pay
        if bal < 0.005:
            bal = 0.0
        rows.append((m, pay, interest, pay - interest, bal))
    return pmt, rows


EXAMPLE = [
    Debt("Store card", 850, 29.99, 35, 1),
    Debt("Credit card", 4200, 24.49, 105, 2),
    Debt("Personal loan", 3100, 12.5, 120, 4),
    Debt("Car loan", 9800, 7.4, 265, 3),
    Debt("Student loan", 18500, 5.8, 205, 5),
]
EXAMPLE_EXTRA = 250.0

if __name__ == "__main__":
    for meth in ("avalanche", "snowball", "custom", "minimums"):
        r = simulate(EXAMPLE, meth, EXAMPLE_EXTRA)
        print(meth, r.months, round(r.total_interest, 2), round(r.total_paid, 2),
              {EXAMPLE[i].name: r.payoff_month[i] for i in r.order})
