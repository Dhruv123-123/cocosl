"""Build launch/dinero-simple/content-month-7.json (June 2027: the midyear check, getting paid every dollar you work
for, the June 15 estimated tax payment, Father's Day and plain insurance): 14 Shorts, 8 carousels and 2 long videos,
plus POSTING_PLAN_MONTH_7.md and REVIEW_CHECKLIST_MONTH_7.md. Any piece that mentions the ITIN gets an ATTORNEY
REVIEW line (flag_attorney).

    python launch/dinero-simple/src/build_month7.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month7_carousels, month7_long, month7_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402
from build_month6 import flag_attorney, mentions_itin  # noqa: E402

YOUTUBE_LINKS = {"l-tu-sueldo-completo": ["art-impuestos", "presupuesto", "gratis"],
                 "l-seguro-de-vida": ["fecha", "presupuesto", "gratis"]}

# Tue Jun 1 opens the month (midyear check); then Mon/Wed/Fri. Father's Day is Sun Jun 20, 2027.
SCHEDULE = [
    ("mar 1 jun", "12:30", "m7-mitad-de-ano"),
    ("mié 2 jun", "12:30", "m7-salario-robado"),
    ("mié 2 jun", "20:00", "m7c-mitad-de-ano"),
    ("vie 4 jun", "12:30", "m7-horas-extra"),
    ("vie 4 jun", "20:00", "m7c-horas-extra"),
    ("lun 7 jun", "12:30", "m7-anota-tus-horas"),
    ("lun 7 jun", "20:00", "m7c-cobrar-tu-salario"),
    ("mié 9 jun", "12:30", "m7-pago-en-efectivo"),
    ("vie 11 jun", "12:30", "m7-impuesto-estimado-junio"),
    ("vie 11 jun", "20:00", "m7c-impuesto-estimado"),
    ("dom 13 jun", "20:00", "l-tu-sueldo-completo"),
    ("lun 14 jun", "12:30", "m7-1099-o-w2"),
    ("mié 16 jun", "12:30", "m7-dia-del-padre"),
    ("mié 16 jun", "20:00", "m7c-dia-del-padre"),
    ("vie 18 jun", "12:30", "m7-cambiar-cheques"),
    ("lun 21 jun", "12:30", "m7-seguro-de-vida-plazo"),
    ("mié 23 jun", "12:30", "m7-plan-de-retiro-seguro"),
    ("mié 23 jun", "20:00", "m7c-seguro-de-vida"),
    ("vie 25 jun", "12:30", "m7-seguro-de-renta"),
    ("vie 25 jun", "20:00", "m7c-seguros-basicos"),
    ("dom 27 jun", "20:00", "l-seguro-de-vida"),
    ("lun 28 jun", "12:30", "m7-seguro-carro-minimo"),
    ("mié 30 jun", "12:30", "m7-choque-que-hacer"),
    ("mié 30 jun", "20:00", "m7c-si-chocas"),
]
HIGH_RISK = ("the overtime and unpaid-wage rules (FLSA, state daily overtime, the 2/3-year deadline, the WHD phone number "
             "and its policy on immigration status), the 2027 estimated tax dates, the life insurance cost example (keep it "
             "labelled as an example), and the check-cashing fee example")


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    n_itin = sum(1 for i in items if mentions_itin(i))
    return f"""# Dinero Simple: month 7 posting plan (June 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. June opens with the midyear money check. Then **getting paid every dollar you work for**: overtime with a worked example, your own record of hours, cash pay, contractor vs employee, and how to claim unpaid wages (free, confidential, and the federal law protects workers whatever their immigration status). Then the **June 15 estimated tax payment** for people who work for themselves, **Father's Day** (Sun Jun 20), cashing checks vs a free account, and **plain insurance**: term life, the "plan de retiro" that is really insurance, renter's and car insurance, and what to do after a crash.

Mon/Wed/Fri 12:30 for Shorts, 20:00 for carousels, Sunday 20:00 for the long videos, plus one Short on Tue Jun 1. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_7.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. {n_itin} pieces mention the ITIN and carry an ATTORNEY REVIEW line. The labor pieces say they are general information and point to worker centers and labor attorneys. Never name an employer, insurer, agent or bank on camera. Everything is general information, not legal, tax or financial advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links (`LINKS.md`).

Source: `launch/dinero-simple/content-month-7.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-7/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = flag_attorney(build(month7_shorts.ITEMS + month7_carousels.ITEMS + month7_long.ITEMS, YOUTUBE_LINKS))
    (DS / "content-month-7.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_7.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_7.md").write_text(review_checklist(items, 7, HIGH_RISK).replace(
        "Tax rules and dates change every year; check irs.gov the week you post.",
        "Rules, dates and prices change; check the sources the week you post."))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts}, {sum(map(mentions_itin, items))} flagged for attorney review")
