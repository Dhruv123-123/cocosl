"""Recalculate Debt-Payoff-Planner.xlsx in LibreOffice headless and compare with debtsim.

Usage: python3 verify_planner.py [path.xlsx]
Runs the shipped example plus extra scenarios (written to a temp copy with openpyxl).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import openpyxl

from debtsim import EXAMPLE, EXAMPLE_EXTRA, Debt, amortize, simulate

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parents[1] / "debt-payoff-planner" / "Debt-Payoff-Planner.xlsx")
FIRST = 13
TOL = 0.02


def recalc(path: Path, outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
                    "--outdir", str(outdir), str(path)], check=True, capture_output=True, timeout=300)
    return outdir / path.name


def write_scenario(dst: Path, debts: list[Debt], extra, method, lump=0, lump_month=1, loan=None):
    wb = openpyxl.load_workbook(dst)
    ws = wb["My Debts"]
    for k in range(8):
        r = FIRST + k
        d = debts[k] if k < len(debts) else None
        ws[f"B{r}"] = d.name if d else None
        ws[f"C{r}"] = d.balance if d else None
        ws[f"D{r}"] = d.apr if d else None
        ws[f"E{r}"] = d.minimum if d else None
        ws[f"F{r}"] = d.custom if d else None
    ws["C6"] = method
    ws["C7"] = extra
    ws["C9"] = lump
    ws["C10"] = lump_month
    if loan:
        a = wb["Loan Amortization"]
        a["C6"], a["C7"], a["C8"], a["C10"] = loan
    wb.save(dst)


def close(a, b, tol=TOL):
    if a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return a == b
    return abs(float(a) - float(b)) <= tol


def check(xlsx: Path, debts, extra, plan, lump=0, lump_month=1, loan=(18500, 5.8, 120, 50), label=""):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    errs = []
    names = {"Avalanche": "avalanche", "Snowball": "snowball", "Custom": "custom", "Minimums only": "minimums"}
    cmp_ = wb["Compare"]
    for j, (lbl, meth) in enumerate(names.items()):
        col = "CDEF"[j]
        sim = simulate(debts, meth, extra, lump, lump_month)
        months = cmp_[f"{col}6"].value
        exp_m = sim.months if sim.months is not None else "30+ yrs"
        if not close(months, exp_m, 0):
            errs.append(f"{lbl} months {months} != {exp_m}")
        if sim.months is not None and not close(cmp_[f"{col}8"].value, sim.total_interest):
            errs.append(f"{lbl} interest {cmp_[f'{col}8'].value} != {sim.total_interest:.2f}")
        if sim.months is not None and not close(cmp_[f"{col}9"].value, sim.total_paid):
            errs.append(f"{lbl} paid {cmp_[f'{col}9'].value} != {sim.total_paid:.2f}")
        # per-debt payoff months (Compare rows 18..25)
        for i, d in enumerate(debts):
            v = cmp_[f"{col}{17 + i}"].value
            e = sim.payoff_month.get(i)
            e = e if e is not None else "30+ yrs"
            if d.balance > 0 and not close(v, e, 0):
                errs.append(f"{lbl} payoff {d.name}: {v} != {e}")
    # My Debts: chosen plan
    md = wb["My Debts"]
    meth = names.get(plan, plan.lower())
    sim = simulate(debts, meth, extra, lump, lump_month)
    for i, d in enumerate(debts):
        r = FIRST + i
        e = sim.payoff_month.get(i)
        if d.balance > 0:
            if not close(md[f"L{r}"].value, e if e is not None else "30+ yrs", 0):
                errs.append(f"My Debts L{r} {md[f'L{r}'].value} != {e}")
            if not close(md[f"N{r}"].value, sim.interest_by_debt[i] if e is not None else "n/a"):
                errs.append(f"My Debts N{r} {md[f'N{r}'].value} != {sim.interest_by_debt[i]:.2f}")
    # Payoff Plan: month 1..N payments/balances
    pp = wb["Payoff Plan"]
    n = sim.months or 360
    for m in range(1, n + 1):
        r = 7 + m
        for i, d in enumerate(debts):
            if d.balance <= 0:
                continue
            pay = pp.cell(row=r, column=4 + 2 * i).value
            bal = pp.cell(row=r, column=5 + 2 * i).value
            bal = 0 if bal in (None, "") else bal  # blank after payoff
            if not close(pay, sim.payments[m - 1][i]) or not close(bal, sim.balances[m - 1][i]):
                errs.append(f"Payoff Plan m{m} {d.name}: pay {pay} bal {bal} vs "
                            f"{sim.payments[m-1][i]:.2f} {sim.balances[m-1][i]:.2f}")
                break
        if len(errs) > 20:
            break
    if sim.months and pp.cell(row=7 + sim.months + 1, column=2).value not in (None, ""):
        errs.append("Payoff Plan shows rows after debt-free month")
    # Loan amortization
    a = wb["Loan Amortization"]
    P, apr, term, ex = loan
    pmt, rows = amortize(P, apr, term, ex)
    _, rows0 = amortize(P, apr, term, 0)
    std_int = sum(x[2] for x in rows0)
    if not close(a["C13"].value, pmt):
        errs.append(f"PMT {a['C13'].value} != {pmt}")
    if not close(a["C14"].value, std_int, 0.5):
        errs.append(f"std interest {a['C14'].value} != {std_int}")
    if not close(a["C15"].value, len(rows), 0):
        errs.append(f"amort months {a['C15'].value} != {len(rows)}")
    if not close(a["C17"].value, sum(x[2] for x in rows)):
        errs.append(f"amort interest {a['C17'].value} != {sum(x[2] for x in rows)}")
    # no error values anywhere on user sheets
    for sh in ("My Debts", "Compare", "Payoff Plan", "Loan Amortization", "Chart Data"):
        for row in wb[sh].iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith(("#", "Err:")) and c.value[:2] != "# " \
                        and c.value not in ("#",) and not c.value.startswith("#1") and not c.value.startswith("#2"):
                    errs.append(f"{sh}!{c.coordinate} = {c.value}")
    status = "PASS" if not errs else "FAIL"
    print(f"[{status}] {label}: plan={plan} months={sim.months} interest={sim.total_interest:,.2f}")
    for e in errs[:25]:
        print("   ", e)
    return not errs, wb


def main():
    tmp = Path(tempfile.mkdtemp(prefix="dpp-"))
    ok = True
    # 1. shipped file as-is
    out = recalc(SRC, tmp / "shipped")
    good, wb = check(out, EXAMPLE, EXAMPLE_EXTRA, "Avalanche", label="shipped example")
    ok &= good
    md = wb["My Debts"]
    print("    summary:", [(md[f"B{r}"].value, md[f"C{r}"].value) for r in range(25, 33)])
    scenarios = [
        ("snowball + lump sum", EXAMPLE, 100, "Snowball", 1500, 3, (9800, 7.4, 48, 0)),
        ("custom with blanks + zero APR", [Debt("Family loan", 2000, 0, 100, None), Debt("Card A", 3000, 22.9, 90, 1),
                                         Debt("Card B", 3000, 22.9, 90, None), Debt("Med bill", 400, 0, 25, 2)],
         75, "Custom", 0, 1, (5000, 0, 24, 100)),
        ("min below interest", [Debt("Card", 5000, 29.99, 100), Debt("Loan", 2000, 9, 80)], 0, "Avalanche", 0, 1,
         (30000, 6.5, 60, 0)),
        ("8 debts", [Debt(f"D{i}", 500 + 900 * i, 4 + 3.1 * i, 25 + 12 * i, 8 - i) for i in range(8)], 300,
         "Custom", 2500, 12, (250000, 6.9, 360, 200)),
        ("no extra, rollover only", EXAMPLE[:3], 0, "Avalanche", 0, 1, (12000, 9.9, 60, 25)),
    ]
    for label, debts, extra, plan, lump, lm, loan in scenarios:
        dst = tmp / ("".join(ch if ch.isalnum() else "_" for ch in label) + ".xlsx")
        shutil.copy(SRC, dst)
        write_scenario(dst, debts, extra, plan, lump, lm, loan)
        out = recalc(dst, tmp / "out")
        good, _ = check(out, debts, extra, plan, lump, lm, loan, label=label)
        ok &= good
    print("ALL PASS" if ok else "FAILURES")
    print("recalculated copies in", tmp)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
