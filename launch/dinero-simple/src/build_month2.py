"""Build launch/dinero-simple/content-month-2.json (January 2027): 14 Shorts, 8 carousels and 2 long
videos written in Spanish for Dinero Simple, plus POSTING_PLAN_MONTH_2.md and REVIEW_CHECKLIST_MONTH_2.md.

Month 2 runs alongside the scam series (Tue/Thu Shorts, Sat carousels), so it posts on the other days.

    python launch/dinero-simple/src/build_month2.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DS = ROOT / "launch" / "dinero-simple"
sys.path.insert(0, str(HERE))

import month2_carousels, month2_long, month2_shorts  # noqa: E402
from build_month1 import visual  # noqa: E402
from links import add_youtube_links  # noqa: E402
from month1_shorts_a import CTA  # noqa: E402

YOUTUBE_LINKS = {"l-plan-2027": ["paquete", "presupuesto", "gratis"],
                 "l-impuestos-2027": ["fecha", "gratis"]}

# (day, time, key). Times America/New_York. Scam-series slots (Tue/Thu 12:30, Sat 20:00) are left free.
SCHEDULE = [
    ("vie 1 ene", "12:30", "m2-meta-con-nombre"),
    ("sáb 2 ene", "12:30", "m2-estado-de-diciembre"),
    ("sáb 2 ene", "20:00", "m2c-fondos-2027"),
    ("dom 3 ene", "20:00", "l-plan-2027"),
    ("mar 5 ene", "20:00", "m2c-lista-de-deudas"),
    ("mié 6 ene", "12:30", "m2-lista-de-deudas"),
    ("vie 8 ene", "12:30", "m2-pruebas-gratis"),
    ("dom 10 ene", "12:30", "m2-primer-talon"),
    ("lun 11 ene", "12:30", "m2-bajar-la-tasa"),
    ("lun 11 ene", "20:00", "m2c-que-pagar-primero"),
    ("mié 13 ene", "12:30", "m2-reporte-gratis-semanal"),
    ("mié 13 ene", "20:00", "m2c-recorte-de-enero"),
    ("vie 15 ene", "12:30", "m2-itin-vence"),
    ("dom 17 ene", "20:00", "l-impuestos-2027"),
    ("lun 18 ene", "12:30", "m2-w2-1-feb"),
    ("lun 18 ene", "20:00", "m2c-calendario-impuestos"),
    ("mié 20 ene", "12:30", "m2-vita-gratis"),
    ("mié 20 ene", "20:00", "m2c-ayuda-gratis-impuestos"),
    ("vie 22 ene", "12:30", "m2-1099-trabajos"),
    ("lun 25 ene", "12:30", "m2-reembolso-cuando-llega"),
    ("mié 27 ene", "12:30", "m2-reembolso-con-trabajo"),
    ("mié 27 ene", "20:00", "m2c-reembolso-en-4"),
    ("vie 29 ene", "12:30", "m2-ira-hasta-abril"),
    ("vie 29 ene", "20:00", "m2c-antes-de-invertir"),
]
WHERE = {"short": "TikTok + YouTube Shorts + Instagram Reels", "carousel": "Instagram + TikTok (carousel)",
         "long": "YouTube (long-form)"}
HIGH_RISK = ("the 2027 filing-season opening date, the Feb 1, 2027 W-2 deadline, the ITIN expiration and W-7 rules, "
             "the VITA / Free File income limits (this year's figures), the PATH Act refund hold for EITC/ACTC, "
             "the 21-day refund line, and the April 15, 2027 IRA deadline for 2026")


def build() -> list[dict]:
    out = []
    for it in month2_shorts.ITEMS + month2_carousels.ITEMS + month2_long.ITEMS:
        segs = []
        for heading, on_screen, narration, scene in it["segments"]:
            if len(on_screen.split()) > 12:
                raise SystemExit(f"{it['key']}: on-screen text over 12 words: {on_screen}")
            segs.append({"heading": heading, "narration": narration, "on_screen_text": on_screen,
                         "visual_prompt": visual(scene)})
        desc = add_youtube_links(it["description"], it["key"], YOUTUBE_LINKS.get(it["key"], []))
        script = {"title": it["title"], "hook": it["hook"], "segments": segs, "cta": CTA,
                  "caption": it["caption"], "hashtags": it["hashtags"], "description": desc,
                  "thumbnail_text": it["thumbnail_text"], "sources": it["sources"],
                  "claims_to_verify": it["claims"], "title_variants": [], "hook_variants": []}
        out.append({"key": it["key"], "format": it["format"], "pillar": it["pillar"], "idea_angle": it["angle"],
                    "script": script})
    return out


def folder(items: list[dict], key: str) -> str:
    i = next(n for n, it in enumerate(items) if it["key"] == key)
    sub = "carousels" if items[i]["format"] == "carousel" else "videos"
    return f"{sub}/{i + 1:02d}-…"


def posting_plan(items: list[dict]) -> str:
    by_key = {it["key"]: it for it in items}
    assert sorted(k for _, _, k in SCHEDULE) == sorted(by_key), "schedule must list every piece exactly once"
    rows = []
    for day, time, key in SCHEDULE:
        it = by_key[key]
        tag = " · **producto**" if "Es nuestro producto" in it["script"]["caption"] else ""
        rows.append(f"| {day} | {time} | {WHERE[it['format']]} | {folder(items, key)} | {it['format']} | "
                    f"{it['script']['title']}{tag} |")
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    return f"""# Dinero Simple: month 2 posting plan (January 2027)

{counts['short']} Shorts, {counts['carousel']} carousels and {counts['long']} long videos, written in Spanish for this audience. January's theme is starting the year in order: the December card statement, a debt list, the yearly 'surprise' costs, cutting bills, and the 2027 tax season (W-2, ITIN, free help through VITA, refunds and what to do with them).

It runs alongside the scam series (`POSTING_PLAN_ESTAFAS.md`), which keeps Tue and Thu at 12:30 and Sat at 20:00, so month 2 uses the other slots. The tax pieces go out before the scam series' ghost-preparer and IRS pieces, so they back each other up. Times America/New_York.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_MONTH_2.md`) and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. The tax pieces are general information, not tax advice; keep that line in every caption.

**producto** marks pieces whose caption mentions one of our own kits. The long videos end their YouTube description with UTM-tagged links (`LINKS.md`).

Source: `launch/dinero-simple/content-month-2.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/month-2/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


def review_checklist(items: list[dict]) -> str:
    parts = [f"""# Dinero Simple month 2: review checklist

Nothing in `content-factory/dinero-simple/month-2/` goes out until both boxes for that piece are ticked: a fluent Spanish speaker has read every word (on screen, caption, narration) and fixed anything that sounds translated, and every fact listed under it has been checked against its source. Each folder's `caption.txt` has the same facts under CHECK BEFORE POSTING.

Highest-risk facts this month (check these first): {HIGH_RISK}. Tax rules and dates change every year; check irs.gov the week you post.
"""]
    names = {"short": "Shorts", "carousel": "Carousels", "long": "Long videos"}
    last = None
    for n, it in enumerate(items, 1):
        if it["format"] != last:
            last = it["format"]
            first = n
            end = first + sum(1 for i in items if i["format"] == last) - 1
            sub = "carousels" if last == "carousel" else "videos"
            parts.append(f"\n## {names[last]} ({sub}/{first:02d}–{end:02d})\n")
        lines = [f"### {n:02d}. {it['script']['title']}", "- [ ] Native Spanish read (screen, caption, narration)"]
        lines += [f"- [ ] {c}" for c in it["script"]["claims_to_verify"]]
        parts.append("\n".join(lines) + "\n")
    return "\n".join(parts)


if __name__ == "__main__":
    items = build()
    (DS / "content-month-2.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_MONTH_2.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_MONTH_2.md").write_text(review_checklist(items))
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts} plus the posting plan and review checklist")
