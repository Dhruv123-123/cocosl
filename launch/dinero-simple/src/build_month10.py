"""Build launch/dinero-simple/content-month-10.json (September 2027, "Tu familia, aquí y allá": Labor Day rights at
work, helping family without going broke, a family emergency plan, retirement when you start late; Hispanic
Heritage Month starts Sep 15): 14 Shorts, 8 carousels and 2 long videos, plus POSTING_PLAN_MONTH_10.md and
REVIEW_CHECKLIST_MONTH_10.md. Any piece that mentions the ITIN or immigration status gets an ATTORNEY REVIEW line.

    python launch/dinero-simple/src/build_month10.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month10_carousels, month10_long, month10_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402
from build_month6 import flag_attorney, mentions_itin  # noqa: E402

YOUTUBE_LINKS = {"l-familia-aqui-y-alla": ["art-envios", "presupuesto", "gratis"],
                 "l-retiro-tarde": ["art-itin-banco", "invertir", "gratis"]}

IMMIGRATION = ("ATTORNEY REVIEW: a licensed immigration attorney or DOJ-accredited representative has read this piece "
               "the week it posts (it mentions immigration status)")

# Wed Sep 1 opens the month; Mon/Wed/Fri plus a Short on Sun Sep 5 (Labor Day weekend; Labor Day is Mon Sep 6).
# Fiestas patrias on Mon Sep 13, before Sep 15/16/18. Long videos on Sundays Sep 12 and Sep 26.
SCHEDULE = [
    ("mié 1 sep", "12:30", "m10-familia-aqui-y-alla"),
    ("mié 1 sep", "20:00", "m10c-cuatro-conversaciones"),
    ("vie 3 sep", "12:30", "m10-lesion-en-el-trabajo"),
    ("vie 3 sep", "20:00", "m10c-lesion-en-el-trabajo"),
    ("dom 5 sep", "12:30", "m10-dias-de-enfermedad"),
    ("lun 6 sep", "12:30", "m10-linea-familia"),
    ("lun 6 sep", "20:00", "m10c-presupuesto-familia"),
    ("mié 8 sep", "12:30", "m10-decir-que-no"),
    ("vie 10 sep", "12:30", "m10-hermanos-cooperan"),
    ("vie 10 sep", "20:00", "m10c-plan-hermanos"),
    ("dom 12 sep", "20:00", "l-familia-aqui-y-alla"),
    ("lun 13 sep", "12:30", "m10-fiestas-patrias"),
    ("lun 13 sep", "20:00", "m10c-fiestas-patrias"),
    ("mié 15 sep", "12:30", "m10-hablar-con-hijos"),
    ("vie 17 sep", "12:30", "m10-plan-familiar"),
    ("vie 17 sep", "20:00", "m10c-plan-familiar"),
    ("lun 20 sep", "12:30", "m10-poder-notarial"),
    ("mié 22 sep", "12:30", "m10-creditos-seguro-social"),
    ("mié 22 sep", "20:00", "m10c-retiro-tarde"),
    ("vie 24 sep", "12:30", "m10-retiro-con-itin"),
    ("dom 26 sep", "20:00", "l-retiro-tarde"),
    ("lun 27 sep", "12:30", "m10-retiro-en-tu-pais"),
    ("lun 27 sep", "20:00", "m10c-retiro-fuera"),
    ("mié 29 sep", "12:30", "m10-cuenta-para-hijos"),
]
HIGH_RISK = ("the workers' compensation and immigration-status statements, paid sick leave rules, the family emergency "
             "plan and power-of-attorney pieces (attorney review), Social Security credits, full retirement age and "
             "payments abroad for noncitizens, the IRA-with-ITIN statements, the $200-a-month example, and that no "
             "bank, broker, remittance company or insurer is named")


def mentions_immigration(it: dict) -> bool:
    s = it["script"]
    text = " ".join([s["caption"]] + [g["narration"] for g in s["segments"]]).lower()
    return "migratori" in text or "notario" in text


def flag_immigration(items: list[dict]) -> list[dict]:
    for it in items:
        claims = it["script"]["claims_to_verify"]
        if mentions_immigration(it) and not claims[0].startswith("ATTORNEY REVIEW"):
            claims.insert(0, IMMIGRATION)
    return items


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    n_att = sum(1 for i in items if i["script"]["claims_to_verify"][0].startswith("ATTORNEY REVIEW"))
    n_legal = sum(1 for i in items if any("LEGAL CHECK" in c for c in i["script"]["claims_to_verify"]))
    return f"""# Dinero Simple: month 10 posting plan (September 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. September is **"Tu familia, aquí y allá"**, the money of families living between two countries, with Hispanic Heritage Month starting Sep 15. It opens around Labor Day with **rights at work**: getting hurt on the job and paid sick days. Then **helping family without going broke**: a fixed family line, saying "este mes no puedo", splitting the parents' needs among siblings, fiestas patrias on a budget and money talks with the kids. Then **a family emergency plan** and why a US notary is not a lawyer. It ends with **retirement when you start late**: Social Security credits, an IRA with an ITIN and retiring in your home country.

Mon/Wed/Fri 12:30 for Shorts, 20:00 for carousels, Sunday 20:00 for the long videos, plus one Short on Sun Sep 5 (Labor Day weekend). Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_10.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. {n_att} pieces mention the ITIN or immigration status and carry an ATTORNEY REVIEW line. {n_legal} pieces carry a LEGAL CHECK claim (work and family law changes by state). Never name a bank, broker, remittance company or insurer on camera. Everything is general information, not legal, tax or financial advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links (`LINKS.md`).

Source: `launch/dinero-simple/content-month-10.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-10/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = flag_immigration(flag_attorney(build(month10_shorts.ITEMS + month10_carousels.ITEMS + month10_long.ITEMS,
                                                 YOUTUBE_LINKS)))
    (DS / "content-month-10.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_10.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_10.md").write_text(review_checklist(items, 10, HIGH_RISK).replace(
        "Tax rules and dates change every year; check irs.gov the week you post.",
        "Rules, dates and prices change; check the sources the week you post."))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    n_att = sum(1 for i in items if i["script"]["claims_to_verify"][0].startswith("ATTORNEY REVIEW"))
    print(f"Wrote {len(items)} items {counts}, {sum(map(mentions_itin, items))} mention the ITIN, {n_att} flagged for attorney review")
