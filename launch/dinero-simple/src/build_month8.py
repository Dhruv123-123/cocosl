"""Build launch/dinero-simple/content-month-8.json (July 2027: the 4th of July, tandas and lending circles, 'business
opportunities' that are really recruiting, starting a small business, first steps to a home with an SSN or an ITIN,
back-to-school and rental scams): 14 Shorts, 8 carousels and 2 long videos, plus POSTING_PLAN_MONTH_8.md and
REVIEW_CHECKLIST_MONTH_8.md. Any piece that mentions the ITIN gets an ATTORNEY REVIEW line (flag_attorney).

    python launch/dinero-simple/src/build_month8.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month8_carousels, month8_long, month8_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402
from build_month6 import flag_attorney, mentions_itin  # noqa: E402

YOUTUBE_LINKS = {"l-tanda": ["art-itin-banco", "presupuesto", "gratis"],
                 "l-primera-casa": ["art-itin-banco", "fecha", "gratis"]}

# Thu Jul 1 opens the month (the cookout before the 4th); then Mon/Wed/Fri. Jul 5 is the observed federal holiday.
SCHEDULE = [
    ("jue 1 jul", "12:30", "m8-carne-asada-4-de-julio"),
    ("vie 2 jul", "12:30", "m8-tanda-riesgos"),
    ("vie 2 jul", "20:00", "m8c-4-de-julio"),
    ("lun 5 jul", "12:30", "m8-tanda-segura"),
    ("lun 5 jul", "20:00", "m8c-tanda-segura"),
    ("mié 7 jul", "12:30", "m8-circulo-de-prestamo"),
    ("vie 9 jul", "12:30", "m8-oportunidad-de-negocio"),
    ("vie 9 jul", "20:00", "m8c-oportunidad-de-negocio"),
    ("dom 11 jul", "20:00", "l-tanda"),
    ("lun 12 jul", "12:30", "m8-negocio-cuenta-aparte"),
    ("mié 14 jul", "12:30", "m8-ein-con-itin"),
    ("mié 14 jul", "20:00", "m8c-negocio-primeros-pasos"),
    ("vie 16 jul", "12:30", "m8-permisos-negocio"),
    ("lun 19 jul", "12:30", "m8-casa-enganche"),
    ("lun 19 jul", "20:00", "m8c-costos-de-comprar-casa"),
    ("mié 21 jul", "12:30", "m8-preaprobacion"),
    ("vie 23 jul", "12:30", "m8-hipoteca-con-itin"),
    ("vie 23 jul", "20:00", "m8c-preguntas-al-prestamista"),
    ("dom 25 jul", "20:00", "l-primera-casa"),
    ("lun 26 jul", "12:30", "m8-regreso-a-clases"),
    ("mié 28 jul", "12:30", "m8-comida-escolar-gratis"),
    ("mié 28 jul", "20:00", "m8c-regreso-a-clases"),
    ("vie 30 jul", "12:30", "m8-estafa-de-renta"),
    ("vie 30 jul", "20:00", "m8c-estafa-de-renta"),
]
HIGH_RISK = ("the ITIN mortgage, EIN-with-ITIN and lending-circle statements (attorney review), FHA's SSN requirement and "
             "the 3%/3.5% down payment programs, the tanda cost example, the school-meal guidance on immigration status, "
             "and that no company, lender or MLM is named")


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    n_itin = sum(1 for i in items if mentions_itin(i))
    return f"""# Dinero Simple: month 8 posting plan (July 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. July opens with the 4th of July cookout as a cooperacha. Then **tandas**: the real risks, how to make one safer, and nonprofit lending circles that also build credit. Then "business opportunities" that are really recruiting (the FTC's multi-level marketing warnings), and **starting a small business the right way**: a separate account, a free EIN (also with an ITIN), local permits and cottage-food rules. Then **first steps to a home**: the down payment myth, preapproval, ITIN mortgages, closing costs and the questions to ask any lender. July ends with back-to-school, free school meals and rental listing scams.

Mon/Wed/Fri 12:30 for Shorts, 20:00 for carousels, Sunday 20:00 for the long videos, plus one Short on Thu Jul 1. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_8.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. {n_itin} pieces mention the ITIN and carry an ATTORNEY REVIEW line. Never name a lender, bank, company or multi-level marketing brand on camera. Everything is general information, not legal, tax or financial advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links (`LINKS.md`).

Source: `launch/dinero-simple/content-month-8.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-8/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = flag_attorney(build(month8_shorts.ITEMS + month8_carousels.ITEMS + month8_long.ITEMS, YOUTUBE_LINKS))
    (DS / "content-month-8.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_8.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_8.md").write_text(review_checklist(items, 8, HIGH_RISK).replace(
        "Tax rules and dates change every year; check irs.gov the week you post.",
        "Rules, dates and prices change; check the sources the week you post."))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts}, {sum(map(mentions_itin, items))} flagged for attorney review")
