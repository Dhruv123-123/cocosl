"""Sinking Funds Sheet for Google Sheets (also opens in Excel and Numbers).

Scouting's product-ideas-round2.md (PR #2): "sinking funds" gets 27,100 searches a month, peaking in January, and we
only had a printable. This sheet pairs with the apps thread's free sinking-funds planner (PR #8,
apps/budget/lib/sinking.js):
- the eight example funds are the planner's English presets, with the same names, targets and month counts;
- the Funds tab uses the planner's export layout (the same as Money Dashboard Pro's Sinking Funds tab): funds at A5
  (Fund, Target, Needed by) and deposits at K5 (Date, Fund, Amount), so the planner's "Copy" output pastes in as is;
- the maths matches: months left = 0 once the date has passed, else DATEDIF(today, due, "m") + 1, and save each
  month = still to save / months left (all of it when no months are left).
Yellow = input, white = calculated, made-up example data, and only functions Google Sheets imports cleanly.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font, PatternFill

import sheets_templates as ST
from sheets_templates import OK, RED, S, _start

# (name, target, months ahead; 0 = the next Dec 1 for holidays, Aug 1 for school), as in sinking.js PRESETS.en
PRESETS = [("Car insurance", 900, 6), ("Holidays and gifts", 800, 0), ("Car repairs and tires", 600, 12),
           ("Back to school", 400, 0), ("Vet and pet care", 500, 12), ("Annual subscriptions and memberships", 200, 9),
           ("Home repairs", 1000, 12), ("Travel", 1500, 8)]
N_FUNDS, N_DEP = 20, 300
F0, D0 = 5, 5          # first fund row (A5) and first deposit row (K5), as in the planner's export
DONE = PatternFill("solid", fgColor="E3F4EA")


def months_ahead(today: date, months: int, day: int = 1) -> date:
    y, m = divmod(today.month - 1 + months, 12)
    return date(today.year + y, m + 1, day)


def preset_date(name: str, months: int, today: date) -> date:
    """Same rule as sinking.js presetDate()."""
    if months:
        return months_ahead(today, months)
    month = 8 if "school" in name.lower() else 12
    return date(today.year if today.month < month else today.year + 1, month, 1)


def example_deposits(today: date) -> list[tuple[date, str, float]]:
    out = []
    for i, (name, target, _m) in enumerate(PRESETS):
        for k in range(1 + i % 3):
            out.append((today - timedelta(days=60 - 25 * k), name, round(target * (0.08 + 0.04 * k), 0)))
    return sorted(out)


def build_sinking(path: Path, today: date | None = None) -> Path:
    today = today or date.today()
    wb = Workbook()
    _start(wb, "Sinking Funds Sheet", "Save a little each month for the bills you know are coming, and see exactly how much each fund needs.",
           ["On Funds, list each fund with its target and the date you need it by (A5 down).",
            "Add each deposit at K5 down: the date, the fund (pick it from the list) and the amount.",
            "Saved, still to save, months left and save each month fill in. A fund that's late turns red; a full one turns green.",
            "On Dashboard, set how many paychecks you get a month to see the amount to move each payday."],
           [("Funds", "Your funds and every deposit. Same layout as our free sinking-funds planner's export."),
            ("Dashboard", "Totals, the monthly and per-paycheck amount, the next fund due, and a chart."),
            ("Year ahead", "What comes due in each of the next 12 months.")])

    fs = S._sheet(wb, "Funds", "Sinking funds", "Funds at A5, deposits at K5. Paste from the free planner's Copy buttons here.",
                  widths={"A": 30, "B": 12, "C": 13, "D": 12, "E": 13, "F": 9, "G": 14, "H": 9, "I": 14, "J": 3, "K": 13, "L": 30, "M": 12})
    fs["B1"], fs["B2"], fs["B3"] = None, None, None
    fs["A1"] = "Sinking funds"
    fs["A1"].font = Font(name="Inter", size=18, bold=True, color=S.INK)
    fs["A2"] = "Funds at A5, deposits at K5. Paste from the free sinking-funds planner's Copy buttons straight into those cells."
    fs["A2"].font = Font(name="Inter", size=10, color="4B5A51")
    fs["A3"] = "Yellow cells = your inputs. White cells calculate automatically. Example data shown; type over it."
    fs["A3"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    S._header(fs, 4, ["Fund", "Target", "Needed by", "Saved", "Still to save", "Months left", "Save each month", "% saved", "Progress"], col=1)
    S._header(fs, 4, ["Date", "Fund", "Amount"], col=11)
    last, dlast = F0 + N_FUNDS - 1, D0 + N_DEP - 1
    cl, ca = f"$L${D0}:$L${dlast}", f"$M${D0}:$M${dlast}"
    for k in range(N_FUNDS):
        r = F0 + k
        name, target, due = (PRESETS[k][0], PRESETS[k][1], preset_date(PRESETS[k][0], PRESETS[k][2], today)) if k < len(PRESETS) else (None, None, None)
        S._inp(fs[f"A{r}"], name)
        S._inp(fs[f"B{r}"], target, S.MONEY0)
        S._inp(fs[f"C{r}"], due, "mmm d, yyyy")
        S._calc(fs[f"D{r}"], f'=IF(A{r}="","",SUMIF({cl},A{r},{ca}))', S.MONEY0)
        S._calc(fs[f"E{r}"], f'=IF(A{r}="","",MAX(0,B{r}-D{r}))', S.MONEY0)
        S._calc(fs[f"F{r}"], f'=IF(OR(A{r}="",C{r}=""),"",IF(C{r}<=TODAY(),0,DATEDIF(TODAY(),C{r},"m")+1))', "0")
        S._calc(fs[f"G{r}"], f'=IF(OR(A{r}="",F{r}=""),"",IF(E{r}=0,0,IF(F{r}=0,E{r},E{r}/F{r})))', S.MONEY)
        S._calc(fs[f"H{r}"], f'=IF(OR(A{r}="",B{r}="",B{r}=0),"",MIN(1,D{r}/B{r}))', "0%")
        ST._bar(fs[f"I{r}"], f"H{r}", 10)
        S._calc(fs[f"O{r}"], f'=IF(AND(A{r}<>"",N(E{r})>0,N(C{r})>TODAY()),C{r},"")', "mmm d, yyyy")   # helper: next-due candidates
    t = last + 1
    S._label(fs, f"A{t}", "Total")
    for c in "BDEG":
        S._calc(fs[f"{c}{t}"], f"=SUM({c}{F0}:{c}{last})", S.MONEY0, bold=True)
    fs.conditional_formatting.add(f"A{F0}:I{last}", FormulaRule(formula=[f'AND($H{F0}<>"",$H{F0}>=1)'], fill=DONE))
    fs.conditional_formatting.add(f"F{F0}:G{last}", FormulaRule(formula=[f'AND($F{F0}<>"",$F{F0}=0,$E{F0}>0)'],
                                                             fill=RED))
    deps = example_deposits(today)
    for k in range(N_DEP):
        r = D0 + k
        d, f, a = deps[k] if k < len(deps) else (None, None, None)
        S._inp(fs[f"K{r}"], d, "mmm d, yyyy")
        S._inp(fs[f"L{r}"], f)
        S._inp(fs[f"M{r}"], a, S.MONEY)
    ST._range_validation(fs, f"$A${F0}:$A${last}", f"L{D0}:L{dlast}")
    fs[f"A{t + 2}"] = ("Months left counts the month the fund is due, so a bill due next month has 2 months: this one and next. "
                       "Dates that have passed show 0 months and the whole amount still to save, in red.")
    fs[f"A{t + 2}"].font = Font(name="Inter", size=9, italic=True, color="4B5A51")
    fs.column_dimensions["O"].hidden = True
    fs.freeze_panes = "A5"

    db = S._sheet(wb, "Dashboard", "Dashboard", "The whole picture on one screen.", widths={"B": 34, "C": 18})
    S._label(db, "B5", "Paychecks a month (4 weekly, 2 every two weeks or twice a month, 1 monthly)", bold=False)
    S._inp(db["C5"], 2, "0")
    F = lambda c: f"Funds!${c}${F0}:${c}${last}"  # noqa: E731
    rows = [("Funds", f'=COUNTA({F("A")})', "0"),
            ("Total target", f"=SUM({F('B')})", S.MONEY0),
            ("Saved so far", f"=SUM({F('D')})", S.MONEY0),
            ("Still to save", f"=SUM({F('E')})", S.MONEY0),
            ("Move each month", f"=SUM({F('G')})", S.MONEY),
            ("Move each paycheck", "=IF(C5>0,C11/C5,C11)", S.MONEY),
            ("Funds full", f'=COUNTIF({F("H")},">=1")', "0"),
            ("Funds late (date passed, not full)", f'=COUNTIFS({F("F")},0,{F("E")},">0")', "0"),
            ("Next fund due", f'=IF(MIN({F("O")})=0,"None",INDEX({F("A")},MATCH(MIN({F("O")}),{F("O")},0)))', None),
            ("Due on", f'=IF(MIN({F("O")})=0,"",MIN({F("O")}))', "mmm d, yyyy")]
    for i, (lab, f, fmt) in enumerate(rows):
        r = 7 + i
        S._label(db, f"B{r}", lab, bold=lab in ("Move each month", "Move each paycheck"))
        S._calc(db[f"C{r}"], f, fmt, bold=lab in ("Move each month", "Move each paycheck"))
    db.conditional_formatting.add("C14", FormulaRule(formula=["C14>0"], fill=RED))
    db.conditional_formatting.add("C13", FormulaRule(formula=["AND(C13>0,C13=C7)"], fill=OK))
    ch = BarChart()
    ch.type, ch.title, ch.height, ch.width = "bar", "Saved vs target", 9, 16
    ch.add_data(Reference(fs, min_col=2, max_col=2, min_row=4, max_row=4 + len(PRESETS)), titles_from_data=True)
    ch.add_data(Reference(fs, min_col=4, max_col=4, min_row=4, max_row=4 + len(PRESETS)), titles_from_data=True)
    ch.set_categories(Reference(fs, min_col=1, min_row=5, max_row=4 + len(PRESETS)))
    ch.x_axis.scaling.orientation = "maxMin"
    ch.y_axis.number_format = '"$"#,##0'
    ch.series[0].graphicalProperties.solidFill = "DDD6C4"
    ch.series[1].graphicalProperties.solidFill = S.GREEN
    db.add_chart(ch, "E5")
    S._foot(db, 20)

    ya = S._sheet(wb, "Year ahead", "Year ahead", "What comes due each month, starting this month.",
                  widths={"B": 14, "C": 14, "D": 16})
    S._header(ya, 5, ["Month", "Funds due", "Targets due"])
    for i in range(12):
        r = 6 + i
        S._calc(ya[f"B{r}"], f"=EDATE(DATE(YEAR(TODAY()),MONTH(TODAY()),1),{i})", "mmm yyyy")
        rng = f'{F("C")},">="&B{r},{F("C")},"<"&EDATE(B{r},1)'
        S._calc(ya[f"C{r}"], f"=COUNTIFS({rng})", "0")
        S._calc(ya[f"D{r}"], f"=SUMIFS({F('B')},{rng})", S.MONEY0)
    S._label(ya, "B18", "Total")
    S._calc(ya["C18"], "=SUM(C6:C17)", "0", bold=True)
    S._calc(ya["D18"], "=SUM(D6:D17)", S.MONEY0, bold=True)
    S._foot(ya, 20)

    wb.save(path)
    return path


ST.SHEETS["sinking-funds-sheet"] = ("Sinking-Funds-Sheet.xlsx", build_sinking)
