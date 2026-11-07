"""Build launch/dinero-simple/content-month-3.json (February 2027, tax season and the ITIN): 14 Shorts,
8 carousels and 2 long videos, plus POSTING_PLAN_MONTH_3.md and REVIEW_CHECKLIST_MONTH_3.md.

The scam series runs until Feb 16 (Tue/Thu 12:30, Sat 20:00), so month 3 posts in the other slots.

    python launch/dinero-simple/src/build_month3.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import month3_carousels, month3_long, month3_shorts  # noqa: E402
from build_month2 import WHERE, build, review_checklist, schedule_rows  # noqa: E402

YOUTUBE_LINKS = {"l-itin-guia": ["art-impuestos", "art-itin-banco", "gratis"],
                 "l-si-debes-o-carta": ["presupuesto", "art-impuestos", "gratis"]}

SCHEDULE = [
    ("lun 1 feb", "12:30", "m3-primer-itin"),
    ("lun 1 feb", "20:00", "m3c-primer-itin"),
    ("mié 3 feb", "12:30", "m3-itin-no-es-permiso"),
    ("mié 3 feb", "20:00", "m3c-mitos-itin"),
    ("vie 5 feb", "12:30", "m3-itin-dependientes"),
    ("dom 7 feb", "20:00", "l-itin-guia"),
    ("lun 8 feb", "12:30", "m3-por-que-declarar"),
    ("lun 8 feb", "20:00", "m3c-documentos-itin"),
    ("mié 10 feb", "12:30", "m3-estado-civil"),
    ("mié 10 feb", "20:00", "m3c-estado-civil"),
    ("vie 12 feb", "12:30", "m3-pin-de-proteccion"),
    ("dom 14 feb", "12:30", "m3-ya-declararon-con-tu-numero"),
    ("dom 14 feb", "20:00", "m3c-robo-de-identidad-fiscal"),
    ("lun 15 feb", "12:30", "m3-reembolso-a-tu-cuenta"),
    ("mar 16 feb", "20:00", "m3-divide-tu-reembolso"),
    ("mié 17 feb", "12:30", "m3-tu-estado-tambien"),
    ("mié 17 feb", "20:00", "m3c-antes-de-firmar"),
    ("jue 18 feb", "12:30", "m3-guarda-copias"),
    ("sáb 20 feb", "12:30", "m3-carta-del-irs"),
    ("sáb 20 feb", "20:00", "m3c-carta-del-irs"),
    ("dom 21 feb", "20:00", "l-si-debes-o-carta"),
    ("lun 22 feb", "12:30", "m3-debes-y-no-alcanza"),
    ("lun 22 feb", "20:00", "m3c-si-debes"),
    ("mié 24 feb", "12:30", "m3-ajusta-tu-w4"),
]
HIGH_RISK = ("anything about the IRS sharing information with immigration authorities (the 2025 IRS-DHS agreement and its court "
             "cases: get a licensed immigration attorney to read the ITIN myths carousel and the 'Privacidad' segment of the ITIN "
             "guide the week they post, and cut them if in doubt), the 2025 changes to SSN rules for the Child Tax Credit, ITIN "
             "documents and W-7 rules for dependents, ITIN processing times, CalEITC for ITIN filers, and the IRS penalty rates")


def posting_plan(items: list[dict]) -> str:
    rows = schedule_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    return f"""# Dinero Simple: month 3 posting plan (February 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos for tax season, centred on filing with an ITIN: what an ITIN is and isn't, the first W-7, documents, dependents, filing status, getting the refund into your own account, the IP PIN and tax identity theft, IRS letters, owing and payment plans, and the W-4.

The scam series (`POSTING_PLAN_ESTAFAS.md`) runs until Tue Feb 16 on Tue and Thu at 12:30 and Sat at 20:00, so month 3 uses the other slots until then. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_3.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. Everything here is general information, not tax or legal advice. The ITIN pieces send immigration questions to a licensed attorney or a DOJ-accredited representative, never a notario; keep that line.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links to the site's tax-prep and ITIN banking comparisons (`LINKS.md`).

Source: `launch/dinero-simple/content-month-3.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-3/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = build(month3_shorts.ITEMS + month3_carousels.ITEMS + month3_long.ITEMS, YOUTUBE_LINKS)
    (DS / "content-month-3.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_3.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_3.md").write_text(review_checklist(items, 3, HIGH_RISK))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts} plus the posting plan and review checklist")
