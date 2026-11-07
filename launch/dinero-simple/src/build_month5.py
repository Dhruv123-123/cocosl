"""Build launch/dinero-simple/content-month-5.json (April 2027: taxes for workers in the US, the ITIN deadline,
and sending money home for less): 14 Shorts, 8 carousels and 2 long videos, plus POSTING_PLAN_MONTH_5.md and
REVIEW_CHECKLIST_MONTH_5.md.

Every piece that mentions the ITIN gets an ATTORNEY REVIEW line on its checklist: a licensed immigration
attorney reads it the week it posts.

    python launch/dinero-simple/src/build_month5.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month5_carousels, month5_long, month5_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402

YOUTUBE_LINKS = {"l-impuestos-trabajador": ["art-impuestos", "presupuesto", "gratis"],
                 "l-envios-del-ano": ["art-envios", "presupuesto", "gratis"]}

# April 15, 2027 is a Thursday. Mon/Wed/Fri 12:30 Shorts, 20:00 carousels, Sunday 20:00 long videos; the tax pieces
# go out before the 15th, the remittance pieces after, when refunds arrive.
SCHEDULE = [
    ("vie 2 abr", "12:30", "m5-w2-o-1099"),
    ("vie 2 abr", "20:00", "m5c-w2-o-1099"),
    ("dom 4 abr", "20:00", "l-impuestos-trabajador"),
    ("lun 5 abr", "12:30", "m5-pago-en-efectivo"),
    ("lun 5 abr", "20:00", "m5c-trabajo-por-tu-cuenta"),
    ("mié 7 abr", "12:30", "m5-gastos-de-trabajo"),
    ("mié 7 abr", "20:00", "m5-itin-y-miedo"),
    ("vie 9 abr", "12:30", "m5-propinas"),
    ("vie 9 abr", "20:00", "m5c-propinas-y-extras"),
    ("dom 11 abr", "12:30", "m5-horas-extra"),
    ("lun 12 abr", "12:30", "m5-ultima-semana"),
    ("lun 12 abr", "20:00", "m5c-semana-del-15"),
    ("mié 14 abr", "12:30", "m5-itin-15-abril"),
    ("mié 14 abr", "20:00", "m5c-itin-temporada"),
    ("vie 16 abr", "12:30", "m5-dos-trabajos"),
    ("dom 18 abr", "20:00", "l-envios-del-ano"),
    ("lun 19 abr", "12:30", "m5-reembolso-y-remesa"),
    ("lun 19 abr", "20:00", "m5c-remesa-en-presupuesto"),
    ("mié 21 abr", "12:30", "m5-envio-con-tarjeta"),
    ("mié 21 abr", "20:00", "m5c-envio-barato"),
    ("vie 23 abr", "12:30", "m5-como-recibe"),
    ("lun 26 abr", "12:30", "m5-numero-de-envio"),
    ("lun 26 abr", "20:00", "m5c-numero-de-envio"),
    ("mié 28 abr", "12:30", "m5-numero-fijo"),
]
HIGH_RISK = ("the 2025 IRS-ICE data-sharing agreement and its court cases (a licensed immigration attorney signs off "
             "'¿Miedo de declarar con ITIN?' and every ITIN piece the week it posts; cut it if in doubt), the tips and overtime "
             "deductions (caps, years, income limits, SSN rule, how the 2026 W-2 reports them), the 2027 VITA and Free File "
             "income limits, the April 15 and estimated-tax dates, and the 1% cash remittance tax")
ATTORNEY = ("ATTORNEY REVIEW: a licensed immigration attorney or DOJ-accredited representative has read this piece "
            "the week it posts (it mentions the ITIN)")


def mentions_itin(it: dict) -> bool:
    s = it["script"]
    text = " ".join([s["title"], s["caption"]] + [g["narration"] + " " + g["on_screen_text"] for g in s["segments"]])
    return "itin" in text.lower()


def flag_attorney(items: list[dict]) -> list[dict]:
    for it in items:
        claims = it["script"]["claims_to_verify"]
        if mentions_itin(it) and ATTORNEY not in claims:
            claims.insert(0, ATTORNEY)
    return items


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    n_itin = sum(1 for i in items if mentions_itin(i))
    return f"""# Dinero Simple: month 5 posting plan (April 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. The first half of April is taxes for workers before Thursday April 15: W-2 or 1099 (with numbers), expenses, cash pay, the new tips and overtime deductions (which need a valid SSN), two jobs, filing with an ITIN, and the last week. The second half, when refunds arrive, is sending money home for less: how much and how often, how to pay, how the family receives it, the 1% cash tax, your rights and the transfer-number scam.

Mon/Wed/Fri at 12:30 for Shorts, 20:00 for carousels, Sunday 20:00 for the long videos (plus one Short on Wed Apr 7 at 20:00 and Sun Apr 11 at 12:30). Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_5.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. **{n_itin} pieces mention the ITIN and carry an ATTORNEY REVIEW line: a licensed immigration attorney or DOJ-accredited representative reads them the week they post.** '¿Miedo de declarar con ITIN? No lo decidas solo' is the riskiest piece this month; if no attorney can read it that week, skip it. Never name a remittance company on camera. Everything is general information, not tax, legal or financial advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links to the site's tax-prep and money-transfer comparisons and the budget kit (`LINKS.md`).

Source: `launch/dinero-simple/content-month-5.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-5/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = flag_attorney(build(month5_shorts.ITEMS + month5_carousels.ITEMS + month5_long.ITEMS, YOUTUBE_LINKS))
    (DS / "content-month-5.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_5.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_5.md").write_text(review_checklist(items, 5, HIGH_RISK))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts}, {sum(map(mentions_itin, items))} flagged for attorney review")
