"""Build launch/dinero-simple/content-month-6.json (May 2027: Mother's Day, medical bills, a used car, teens' first
jobs, the trip home and the kids' summer): 14 Shorts, 8 carousels and 2 long videos, plus POSTING_PLAN_MONTH_6.md
and REVIEW_CHECKLIST_MONTH_6.md. Any piece that mentions the ITIN gets an ATTORNEY REVIEW line (flag_attorney).

    python launch/dinero-simple/src/build_month6.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month6_carousels, month6_long, month6_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402

YOUTUBE_LINKS = {"l-carro-usado": ["art-itin-banco", "fecha", "gratis"],
                 "l-viaje-a-casa": ["art-envios", "presupuesto", "gratis"]}

# Mother's Day (May 9 in the US, May 10 in Mexico) first, then medical bills, the used car, teens and the summer.
SCHEDULE = [
    ("sáb 1 may", "12:30", "m6-envio-10-de-mayo"),
    ("lun 3 may", "12:30", "m6-regalo-que-sirve"),
    ("lun 3 may", "20:00", "m6c-10-de-mayo"),
    ("mié 5 may", "12:30", "m6-graduacion-cuenta"),
    ("vie 7 may", "12:30", "m6-factura-medica"),
    ("vie 7 may", "20:00", "m6c-factura-medica"),
    ("lun 10 may", "12:30", "m6-deuda-medica-credito"),
    ("mié 12 may", "12:30", "m6-carro-precio-total"),
    ("mié 12 may", "20:00", "m6c-antes-de-comprar-carro"),
    ("vie 14 may", "12:30", "m6-vin-gratis"),
    ("vie 14 may", "20:00", "m6c-letrero-ventana"),
    ("dom 16 may", "20:00", "l-carro-usado"),
    ("lun 17 may", "12:30", "m6-yo-yo"),
    ("mié 19 may", "12:30", "m6-primer-trabajo-teen"),
    ("mié 19 may", "20:00", "m6c-primer-trabajo"),
    ("vie 21 may", "12:30", "m6-roth-para-jovenes"),
    ("dom 23 may", "20:00", "l-viaje-a-casa"),
    ("lun 24 may", "12:30", "m6-boletos-falsos"),
    ("lun 24 may", "20:00", "m6c-viaje-a-casa"),
    ("mié 26 may", "12:30", "m6-campamento-credito"),
    ("mié 26 may", "20:00", "m6c-verano-ninos"),
    ("vie 28 may", "12:30", "m6-calor-luz"),
    ("lun 31 may", "12:30", "m6-deposito-renta"),
    ("lun 31 may", "20:00", "m6c-deposito-de-renta"),
]
HIGH_RISK = ("the medical-debt credit reporting rules (bureau policies and the status of the vacated 2025 CFPB rule), "
             "SUN Bucks states and amount for 2027, LIHEAP cooling help and funding, the 2027 IRA limit, the FTC Used Car "
             "Rule's Spanish Buyers Guide requirement, and the car-loan arithmetic")
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
    return f"""# Dinero Simple: month 6 posting plan (May 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. May opens with Mother's Day (Sun May 9 in the US, Mon May 10 in Mexico and much of Latin America): the remittance by May 5 and gifts without debt. Then medical bills and medical debt on credit reports, buying a used car (total price, free VIN checks, the window sticker, yo-yo financing), teens' first summer jobs (W-4, custodial Roth IRA), the trip home and fake ticket sellers, the kids' summer (SUN Bucks, free meals, the day-camp credit), the summer electric bill and getting the rent deposit back.

Mon/Wed/Fri 12:30 for Shorts, 20:00 for carousels, Sunday 20:00 for the long videos, plus one Short on Sat May 1. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_6.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. {n_itin} pieces mention the ITIN and carry an ATTORNEY REVIEW line. Never name a dealer, lender, bank or remittance company on camera. Everything is general information, not financial or tax advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links (`LINKS.md`).

Source: `launch/dinero-simple/content-month-6.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-6/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = flag_attorney(build(month6_shorts.ITEMS + month6_carousels.ITEMS + month6_long.ITEMS, YOUTUBE_LINKS))
    (DS / "content-month-6.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_6.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_6.md").write_text(review_checklist(items, 6, HIGH_RISK).replace("Tax rules and dates change every year; check irs.gov the week you post.", "Rules, programs and amounts change; check the sources the week you post."))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts}, {sum(map(mentions_itin, items))} flagged for attorney review")
