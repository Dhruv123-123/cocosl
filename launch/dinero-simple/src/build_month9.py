"""Build launch/dinero-simple/content-month-9.json (August 2027, "Tu primer año": money basics for recent arrivals and
Spanish-first adults, then renting safely): 14 Shorts, 8 carousels and 2 long videos, plus POSTING_PLAN_MONTH_9.md
and REVIEW_CHECKLIST_MONTH_9.md. Any piece that mentions the ITIN gets an ATTORNEY REVIEW line (flag_attorney);
renting pieces carry a LEGAL CHECK claim because tenant rules vary by state and city.

    python launch/dinero-simple/src/build_month9.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month9_carousels, month9_long, month9_shorts  # noqa: E402
from build_month2 import build, review_checklist, schedule_rows  # noqa: E402
from build_month6 import flag_attorney, mentions_itin  # noqa: E402

YOUTUBE_LINKS = {"l-primer-ano": ["art-itin-banco", "presupuesto", "gratis"],
                 "l-rentar": ["presupuesto", "fecha", "gratis"]}

# Sun Aug 1 opens the series; then Mon/Wed/Fri. Long videos on Sundays Aug 8 and Aug 22.
SCHEDULE = [
    ("dom 1 ago", "12:30", "m9-primeros-30-dias"),
    ("lun 2 ago", "12:30", "m9-efectivo-en-casa"),
    ("lun 2 ago", "20:00", "m9c-primer-mes"),
    ("mié 4 ago", "12:30", "m9-debito-o-credito"),
    ("mié 4 ago", "20:00", "m9c-abrir-cuenta"),
    ("vie 6 ago", "12:30", "m9-apps-de-pago"),
    ("vie 6 ago", "20:00", "m9c-tarjeta-robada"),
    ("dom 8 ago", "20:00", "l-primer-ano"),
    ("lun 9 ago", "12:30", "m9-impuesto-de-ventas"),
    ("mié 11 ago", "12:30", "m9-propinas"),
    ("mié 11 ago", "20:00", "m9c-precio-real"),
    ("vie 13 ago", "12:30", "m9-luz-sin-historial"),
    ("lun 16 ago", "12:30", "m9-carpeta-de-papeles"),
    ("mié 18 ago", "12:30", "m9-colchon-primer-ano"),
    ("mié 18 ago", "20:00", "m9c-colchon"),
    ("vie 20 ago", "12:30", "m9-antes-de-firmar"),
    ("vie 20 ago", "20:00", "m9c-contrato-de-renta"),
    ("dom 22 ago", "20:00", "l-rentar"),
    ("lun 23 ago", "12:30", "m9-fotos-al-entrar"),
    ("lun 23 ago", "20:00", "m9c-depositos"),
    ("mié 25 ago", "12:30", "m9-reparaciones"),
    ("vie 27 ago", "12:30", "m9-desalojo"),
    ("vie 27 ago", "20:00", "m9c-derechos-inquilino"),
    ("lun 30 ago", "12:30", "m9-clinica-comunitaria"),
]
HIGH_RISK = ("the debit/credit liability limits and deadlines, the ITIN and account-opening statements (attorney review), "
             "every tenant-law statement marked LEGAL CHECK (they vary by state and city: deposits, notice, eviction, "
             "rent increases), the community health center sliding-fee statement, and that no bank, app, landlord or "
             "company is named")


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    n_itin = sum(1 for i in items if mentions_itin(i))
    n_legal = sum(1 for i in items if any("LEGAL CHECK" in c for c in i["script"]["claims_to_verify"]))
    return f"""# Dinero Simple: month 9 posting plan (August 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos. August is **"Tu primer año"**, the money basics nobody explains when you have just arrived: documents safe, an insured account (with a passport, consular ID or ITIN where accepted), how debit and credit cards protect you, payment apps as cash, the real price (sales tax and tips), utility deposits without a credit history, a first-year folder, a $500 emergency fund and community health centers. The second half is **renting without getting ripped off**: the lease, the deposit, repairs in writing, tenant rights and eviction basics.

Mon/Wed/Fri 12:30 for Shorts, 20:00 for carousels, Sunday 20:00 for the long videos, plus the opening Short on Sun Aug 1. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_9.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. {n_itin} pieces mention the ITIN and carry an ATTORNEY REVIEW line. {n_legal} renting pieces carry a LEGAL CHECK claim: tenant law changes by state and city, so confirm each one or soften it to "en muchos estados". Never name a bank, app, landlord or company on camera. Everything is general information, not legal, tax or financial advice.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links (`LINKS.md`).

Source: `launch/dinero-simple/content-month-9.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-9/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = flag_attorney(build(month9_shorts.ITEMS + month9_carousels.ITEMS + month9_long.ITEMS, YOUTUBE_LINKS))
    (DS / "content-month-9.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_9.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_9.md").write_text(review_checklist(items, 9, HIGH_RISK).replace(
        "Tax rules and dates change every year; check irs.gov the week you post.",
        "Rules, dates and prices change; check the sources the week you post."))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts}, {sum(map(mentions_itin, items))} flagged for attorney review")
