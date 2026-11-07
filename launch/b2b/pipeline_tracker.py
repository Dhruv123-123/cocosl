#!/usr/bin/env python3
"""Make the B2B pipeline tracker: every prospect with its stage, follow-up dates and expected value.

    cd launch/b2b && python3 outreach_dates.py && python3 pipeline_tracker.py

Writes PIPELINE.csv (always) and PIPELINE.xlsx (when openpyxl is installed: drop-down stages, formulas for
expected value, follow-up flags and a per-offer summary). Rows come from OUTREACH_DATES.csv, so the planned
dates match the shared-inbox calendar. Re-running keeps what you've typed: stage, dates, value overrides and
notes are read back from an existing PIPELINE.csv, matched on product + prospect.

Expected value = deal value x stage probability. Deal values are first-year values at the plan most
prospects of that type would pick (edit OFFERS below, or type an override in the row). They're planning
numbers, not forecasts. Nothing here sends anything.
"""
import csv
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# product -> (offer name, typical plan, first-year value in $)
OFFERS = {
    "credit-union-alert": ("Weekly Scam Alert", "Standard $99/mo", 1188),
    "ncpw-sponsor": ("Consumer Protection Week", "Week package, one-time", 149),
    "employer-wellness": ("Money Made Simple at Work", "Standard $129/mo", 1548),
    "community-scam-watch": ("Scam Watch", "One site $19/mo", 228),
    "freelancer-client-letter": ("Freelancer Money Notes", "Standard $79/mo", 948),
    "schools": ("Money Made Simple for Schools", "School $299/yr", 299),
}
# partners (SHRM chapters, brokers, PEO) bring clients rather than pay; count one employer client each
PARTNER_VALUE = 1548

# stage -> chance of closing (planning guesses, roughly what small B2B cold outreach sees)
STAGES = [
    ("Not contacted", 0.00), ("Emailed", 0.02), ("Replied", 0.10), ("Sample sent", 0.25),
    ("Call booked", 0.40), ("Proposal sent", 0.60), ("Won", 1.00), ("Lost", 0.00),
    ("Not now (revisit)", 0.05), ("Do not contact", 0.00),
]
PROB = dict(STAGES)
COLS = ["product", "offer", "type", "prospect", "state", "fit_score", "stage", "email_1", "follow_up_1",
        "follow_up_2", "last_contact", "next_step", "next_step_date", "deal_value", "probability",
        "expected_value", "ncpw_add_on", "notes"]
KEEP = ["stage", "last_contact", "next_step", "next_step_date", "deal_value", "ncpw_add_on", "notes"]


def deal_value(product: str, kind: str) -> int:
    if kind == "Employer partner":
        return PARTNER_VALUE
    return OFFERS[product][2]


def rows(today: dt.date | None = None) -> list[dict]:
    src = ROOT / "OUTREACH_DATES.csv"
    if not src.exists():
        sys.exit("OUTREACH_DATES.csv not found: run python3 outreach_dates.py first")
    old = {}
    if (ROOT / "PIPELINE.csv").exists():
        for r in csv.DictReader(open(ROOT / "PIPELINE.csv", newline="")):
            old[(r["product"], r["prospect"])] = r
    out = []
    for r in csv.DictReader(open(src, newline="")):
        prev = old.get((r["product"], r["prospect"]), {})
        row = {
            "product": r["product"], "offer": OFFERS[r["product"]][0], "type": r["type"],
            "prospect": r["prospect"], "state": r["state"], "fit_score": r["fit_score"],
            "stage": "Not contacted", "email_1": r["email_1"], "follow_up_1": r["follow_up_1"],
            "follow_up_2": r["follow_up_2"], "last_contact": "", "next_step": "Email 1",
            "next_step_date": r["email_1"], "deal_value": str(deal_value(r["product"], r["type"])),
            "ncpw_add_on": "", "notes": "",
        }
        # credit unions can also buy the one-week package; flag the ones emailed before the Jan 29 order date
        if r["product"] == "credit-union-alert" and r["email_1"] <= "2027-01-29":
            row["ncpw_add_on"] = "pitch"
        for k in KEEP:
            if prev.get(k):
                row[k] = prev[k]
        if row["stage"] not in PROB:
            sys.exit(f"unknown stage {row['stage']!r} for {row['prospect']}; use one of {', '.join(PROB)}")
        p = PROB[row["stage"]]
        row["probability"] = f"{p:.2f}"
        row["expected_value"] = f"{float(row['deal_value'] or 0) * p:.0f}"
        out.append(row)
    return out


def summary(data: list[dict]) -> list[dict]:
    by = {}
    for r in data:
        s = by.setdefault(r["offer"], {"offer": r["offer"], "prospects": 0, "contacted": 0, "won": 0,
                                       "pipeline_value": 0.0, "expected_value": 0.0})
        s["prospects"] += 1
        s["contacted"] += r["stage"] not in ("Not contacted",)
        s["won"] += r["stage"] == "Won"
        if r["stage"] not in ("Lost", "Do not contact"):
            s["pipeline_value"] += float(r["deal_value"] or 0)
        s["expected_value"] += float(r["expected_value"])
    return list(by.values())


def write_xlsx(data: list[dict], path: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter as L
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    hdr, fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F5C8B")
    how = wb.active
    how.title = "How to use"
    for line in [
        "B2B pipeline tracker (nothing has been sent yet). One row per prospect, dated from OUTREACH_DATES.md.",
        "",
        "1. When you send an email, set Stage to Emailed and Last contact to today.",
        "2. Any reply stops the cold follow-ups: set Stage, then a Next step and its date.",
        "3. 'No thanks' or 'unsubscribe' = Do not contact, the same day. Skip their remaining dates.",
        "4. Red Next step date = overdue. Yellow = due within 3 days.",
        "5. Expected value = Deal value x the stage's chance (Stages tab). Override Deal value per row if you know better.",
        "6. 'ncpw_add_on' = pitch: also offer the $149 Consumer Protection Week package (orders close Jan 29, 2027). "
        "Change it to pitched, won or no; the Summary counts wins.",
        "7. Re-running pipeline_tracker.py keeps your edits in PIPELINE.csv (stage, dates, value, notes); "
        "the xlsx is rebuilt from it. If you track in the xlsx, export it back to PIPELINE.csv before re-running.",
        "",
        "Replies: B2B_START_HERE.md and each offer's COLD_EMAILS.md / OBJECTIONS.md.",
    ]:
        how.append([line])
    how.column_dimensions["A"].width = 120
    how["A1"].font = Font(bold=True, size=13)

    st = wb.create_sheet("Stages")
    st.append(["Stage", "Chance of closing"])
    for name, p in STAGES:
        st.append([name, p])
    st.append([])
    st.append(["Offer", "Typical plan", "First-year value"])
    for name, plan, v in OFFERS.values():
        st.append([name, plan, v])
    st.append(["Employer partner", "one employer client", PARTNER_VALUE])
    for c in ("A", "B", "C"):
        st.column_dimensions[c].width = 32
    for cell in st[1]:
        cell.font, cell.fill = hdr, fill

    ws = wb.create_sheet("Pipeline", 1)
    ws.append(COLS)
    widths = dict(product=20, offer=26, type=16, prospect=36, state=6, fit_score=8, stage=18, notes=40,
                  next_step=22, ncpw_add_on=12)
    for i, c in enumerate(COLS, 1):
        cell = ws.cell(1, i)
        cell.font, cell.fill = hdr, fill
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[L(i)].width = widths.get(c, 13)
    ix = {c: L(i) for i, c in enumerate(COLS, 1)}
    n = len(STAGES) + 1
    for r, row in enumerate(data, 2):
        for i, c in enumerate(COLS, 1):
            v = row[c]
            if c in ("email_1", "follow_up_1", "follow_up_2", "last_contact", "next_step_date") and v:
                v = dt.date.fromisoformat(v)
                ws.cell(r, i).number_format = "yyyy-mm-dd"
            elif c == "fit_score" and v:
                v = int(v)
            elif c == "deal_value":
                v = float(v or 0)
            elif c == "probability":
                v = f'=IFERROR(VLOOKUP({ix["stage"]}{r},Stages!$A$2:$B${n},2,FALSE),0)'
            elif c == "expected_value":
                v = f'={ix["deal_value"]}{r}*{ix["probability"]}{r}'
                ws.cell(r, i).number_format = '"$"#,##0'
            ws.cell(r, i, v)
        ws.cell(r, COLS.index("deal_value") + 1).number_format = '"$"#,##0'
    last = len(data) + 1
    dv = DataValidation(type="list", formula1=f"=Stages!$A$2:$A${n}", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"{ix['stage']}2:{ix['stage']}{last + 200}")
    nd = f"{ix['next_step_date']}2:{ix['next_step_date']}{last}"
    open_stage = f'AND(${ix["stage"]}2<>"Won",${ix["stage"]}2<>"Lost",${ix["stage"]}2<>"Do not contact")'
    ws.conditional_formatting.add(nd, FormulaRule(
        formula=[f'AND(${ix["next_step_date"]}2<>"",${ix["next_step_date"]}2<TODAY(),{open_stage})'],
        fill=PatternFill("solid", fgColor="FBEBEB"), font=Font(bold=True, color="9C1C1C")))
    ws.conditional_formatting.add(nd, FormulaRule(
        formula=[f'AND(${ix["next_step_date"]}2<>"",${ix["next_step_date"]}2-TODAY()<=3,{open_stage})'],
        fill=PatternFill("solid", fgColor="FFF6DC")))
    ws.conditional_formatting.add(f"A2:{L(len(COLS))}{last}", FormulaRule(
        formula=[f'${ix["stage"]}2="Won"'], fill=PatternFill("solid", fgColor="E5F4E4")))
    ws.freeze_panes = "E2"
    ws.auto_filter.ref = f"A1:{L(len(COLS))}{last}"

    sm = wb.create_sheet("Summary", 1)
    sm.append(["Offer", "Prospects", "Contacted", "Won", "Open pipeline value", "Expected value"])
    for cell in sm[1]:
        cell.font, cell.fill = hdr, fill
    rng = lambda c: f"Pipeline!${ix[c]}$2:${ix[c]}${last}"  # noqa: E731
    offers = [o[0] for o in OFFERS.values() if any(r["offer"] == o[0] for r in data)]
    for i, name in enumerate(offers, 2):
        sm.append([name, f'=COUNTIF({rng("offer")},A{i})',
                   f'=COUNTIFS({rng("offer")},A{i},{rng("stage")},"<>Not contacted")',
                   f'=COUNTIFS({rng("offer")},A{i},{rng("stage")},"Won")',
                   f'=SUMIFS({rng("deal_value")},{rng("offer")},A{i},{rng("stage")},"<>Lost",{rng("stage")},"<>Do not contact")',
                   f'=SUMIFS({rng("expected_value")},{rng("offer")},A{i})'])
    # the one-week Consumer Protection Week package rides on credit union rows (ncpw_add_on: pitch / pitched / won / no)
    i = len(offers) + 2
    sm.append(["Consumer Protection Week (add-on)", f'=COUNTIF({rng("ncpw_add_on")},"?*")',
               f'=COUNTIF({rng("ncpw_add_on")},"pitched")+COUNTIF({rng("ncpw_add_on")},"won")',
               f'=COUNTIF({rng("ncpw_add_on")},"won")', f"=D{i}*{OFFERS['ncpw-sponsor'][2]}", f"=D{i}*{OFFERS['ncpw-sponsor'][2]}"])
    offers.append("ncpw")
    t = len(offers) + 2
    # prospects and contacted count people once (the add-on row repeats credit unions); wins and dollars add up
    sm.append(["Total"] + [f"=SUM({c}2:{c}{t - 2})" for c in "BC"] + [f"=SUM({c}2:{c}{t - 1})" for c in "DEF"])
    for row in sm.iter_rows(min_row=2, min_col=5, max_col=6):
        for cell in row:
            cell.number_format = '"$"#,##0'
    sm[f"A{t}"].font = Font(bold=True)
    sm.append([])
    sm.append(["Planning numbers only: deal values and stage chances are guesses to rank effort, not a forecast."])
    for c, w in zip("ABCDEF", (32, 11, 11, 8, 20, 16)):
        sm.column_dimensions[c].width = w
    wb.save(path)


def main() -> None:
    data = rows()
    with open(ROOT / "PIPELINE.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(data)
    tot = summary(data)
    print(f"wrote PIPELINE.csv ({len(data)} prospects)")
    for s in tot:
        print(f"  {s['offer']:<32} {s['prospects']:>3} prospects  open ${s['pipeline_value']:>9,.0f}  "
              f"expected ${s['expected_value']:>7,.0f}")
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        print("openpyxl not installed, so no PIPELINE.xlsx (pip install openpyxl)")
        return
    write_xlsx(data, ROOT / "PIPELINE.xlsx")
    print("wrote PIPELINE.xlsx")


if __name__ == "__main__":
    main()
