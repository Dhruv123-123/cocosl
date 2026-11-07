"""Build launch/dinero-simple/content-month-4.json (March 2027: credit from zero and banking without fees, with
or without a Social Security number, plus the last stretch to April 15): 14 Shorts, 8 carousels and 2 long
videos, plus POSTING_PLAN_MONTH_4.md and REVIEW_CHECKLIST_MONTH_4.md.

    python launch/dinero-simple/src/build_month4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month4_carousels, month4_long, month4_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402

YOUTUBE_LINKS = {"l-credito-desde-cero": ["art-itin-banco", "fecha", "gratis"],
                 "l-banco-sin-cargos": ["art-itin-banco", "presupuesto", "gratis"]}

SCHEDULE = [
    ("lun 1 mar", "12:30", "m4-credito-con-itin"),
    ("lun 1 mar", "20:00", "m4c-credito-desde-cero"),
    ("mié 3 mar", "12:30", "m4-tarjeta-asegurada"),
    ("mié 3 mar", "20:00", "m4c-preguntas-tarjeta-asegurada"),
    ("vie 5 mar", "12:30", "m4-prestamo-constructor"),
    ("dom 7 mar", "20:00", "l-credito-desde-cero"),
    ("lun 8 mar", "12:30", "m4-usuario-autorizado"),
    ("mié 10 mar", "12:30", "m4-renta-al-credito"),
    ("mié 10 mar", "20:00", "m4c-mitos-puntaje"),
    ("vie 12 mar", "12:30", "m4-disputa-error"),
    ("vie 12 mar", "20:00", "m4c-disputa-paso-a-paso"),
    ("lun 15 mar", "12:30", "m4-lo-que-no-cuenta"),
    ("mié 17 mar", "12:30", "m4-cuenta-sin-ssn"),
    ("mié 17 mar", "20:00", "m4c-cuenta-sin-ssn"),
    ("vie 19 mar", "12:30", "m4-sobregiro"),
    ("dom 21 mar", "20:00", "l-banco-sin-cargos"),
    ("lun 22 mar", "12:30", "m4-cambiar-cheques"),
    ("lun 22 mar", "20:00", "m4c-cargos-evitables"),
    ("mié 24 mar", "12:30", "m4-cooperativa"),
    ("mié 24 mar", "20:00", "m4c-banco-o-cooperativa"),
    ("vie 26 mar", "12:30", "m4-cargos-del-banco"),
    ("lun 29 mar", "12:30", "m4-prorroga"),
    ("lun 29 mar", "20:00", "m4c-antes-del-15-abril"),
    ("mié 31 mar", "12:30", "m4-estimados"),
]
HIGH_RISK = ("the overdraft opt-in rule for debit and ATM purchases (and any 2027 changes to overdraft rules), credit-bureau "
             "dispute timelines, rent-reporting use in score models, the Form 4868 and estimated-tax dates for 2027 (check for "
             "weekend or disaster shifts), the 2026 IRA deadline, and any bank or credit union named on camera (don't name one)")


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    return f"""# Dinero Simple: month 4 posting plan (March 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. After two months of taxes, March turns to credit and banking from zero, with or without a Social Security number: credit with an ITIN, secured cards, credit-builder loans, authorized users, rent reporting, disputes, opening an account with an ITIN or matrícula, overdraft, check-cashing and bank fees, banks versus credit unions. The month ends with the April 15 stretch (extension, estimated taxes and a checklist).

No other series runs in March, so the month uses Mon/Wed/Fri at 12:30 for Shorts, 20:00 for carousels, and Sunday 20:00 for the long videos. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_4.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. Never name a specific bank, credit union or card on camera. Everything is general information, not financial or tax advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links to the site's ITIN banking and credit comparison and the kits (`LINKS.md`).

Source: `launch/dinero-simple/content-month-4.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-4/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = build(month4_shorts.ITEMS + month4_carousels.ITEMS + month4_long.ITEMS, YOUTUBE_LINKS)
    (DS / "content-month-4.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_4.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_4.md").write_text(review_checklist(items, 4, HIGH_RISK).replace(
        "Tax rules and dates change every year; check irs.gov the week you post.",
        "Bank rules, fees and tax dates change; check the sources the week you post."))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts} plus the posting plan and review checklist")
