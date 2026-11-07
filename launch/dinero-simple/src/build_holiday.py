"""Build launch/dinero-simple/content-holiday-2026.json (Nov 20 - Dec 31, 2026): 10 posts that fill the gaps month 1
leaves, rotating Shorts, TikTok mids, carousels and single images, plus POSTING_PLAN_HOLIDAY_2026.md and
REVIEW_CHECKLIST_HOLIDAY_2026.md. Slots never collide with month 1's (a test checks this).

    python launch/dinero-simple/src/build_holiday.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import holiday_2026  # noqa: E402
from build_month2 import build  # noqa: E402

WHERE = {"short": "TikTok + YouTube Shorts + Instagram Reels + Facebook Reels", "mid": "TikTok only (65-90 s)",
         "carousel": "Instagram + TikTok (carousel)", "image": "Instagram + Facebook (single image)",
         "long": "YouTube (long-form)"}
SCHEDULE = [
    ("dom 22 nov", "12:30", "h-precio-inflado"),
    ("lun 23 nov", "20:00", "hc-trampas-black-friday"),
    ("mié 25 nov", "20:00", "h-intereses-diferidos"),
    ("jue 26 nov", "20:00", "h-tres-preguntas-compra"),
    ("sáb 5 dic", "12:30", "h-envio-a-tiempo"),
    ("sáb 5 dic", "20:00", "h-calculadora-envios"),
    ("mié 9 dic", "12:30", "h-tope-intercambio"),
    ("vie 11 dic", "20:00", "hc-posada-entre-todos"),
    ("dom 13 dic", "12:30", "h-rifa-falsa"),
    ("vie 18 dic", "20:00", "hc-estafas-whatsapp"),
]
HIGH_RISK = ("the deferred-interest example (re-run the arithmetic), holiday hours and deposit timing (say 'many', never "
             "name a provider), the 1% cash remittance tax, and the calculator being live before the two posts that point to it")


def posting_plan(items: list[dict]) -> str:
    by_key = {it["key"]: (n, it) for n, it in enumerate(items, 1)}
    assert sorted(k for *_, k in SCHEDULE) == sorted(by_key), "schedule must list every piece exactly once"
    rows = []
    for day, time, key in SCHEDULE:
        n, it = by_key[key]
        sub = "carousels" if it["format"] in ("carousel", "image") else "videos"
        rows.append(f"| {day} | {time} | {WHERE[it['format']]} | {sub}/{n:02d}-… | {it['format']} | {it['script']['title']} |")
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "mid", "carousel", "image")}
    return f"""# Dinero Simple: holiday pack posting plan (Nov 20 – Dec 31, 2026)

{len(items)} extra posts for the holidays: {counts['short']} Shorts, {counts['mid']} TikTok mids (65–90 s), {counts['carousel']} carousels and {counts['image']} single images. They fill the gaps month 1 leaves (`POSTING_PLAN_MONTH_1.md`), so no slot is used twice. Month 1 already covers the 72-hour rule, the gift list, remittance rights, the 1% cash tax, the cost of hosting a posada and the 'paquete' text; this pack does not repeat them.

Formats rotate so no two days in a row look alike, which matters for YouTube's and TikTok's 'inauthentic' and 'unoriginal' rules: the mids are TikTok only, the single images go to Instagram and Facebook only.

The four Black Friday posts go up before Fri Nov 27. Remittance timing goes up Sat Dec 5, ahead of the "send before the 15th" advice. Scams run into the posada season.

**Before Dec 5:** the remittance calculator (`/calculadora-de-envios/` on the site) must be live, since two posts point to it. If it isn't, skip the image and cut the last line of the mid's caption.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_HOLIDAY_2026.md`) and the facts under CHECK BEFORE POSTING are confirmed. Never name a store, card or remittance company on camera. Times America/New_York.

Source: `launch/dinero-simple/content-holiday-2026.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/holiday-2026/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


def review_checklist(items: list[dict]) -> str:
    parts = [f"""# Dinero Simple holiday pack 2026: review checklist

Nothing in `content-factory/dinero-simple/holiday-2026/` goes out until both boxes for that piece are ticked: a fluent Spanish speaker has read every word (on screen, caption, narration) and fixed anything that sounds translated, and every fact listed under it has been checked. Each folder's `caption.txt` has the same facts under CHECK BEFORE POSTING.

Highest-risk facts (check these first): {HIGH_RISK}. Store terms and provider hours change; check them the week you post.
"""]
    for n, it in enumerate(items, 1):
        sub = "carousels" if it["format"] in ("carousel", "image") else "videos"
        lines = [f"### {n:02d}. {it['script']['title']} ({it['format']}, {sub}/)", "- [ ] Native Spanish read (screen, caption, narration)"]
        lines += [f"- [ ] {c}" for c in it["script"]["claims_to_verify"]]
        parts.append("\n".join(lines) + "\n")
    return "\n".join(parts)


if __name__ == "__main__":
    items = build(holiday_2026.ITEMS, {})
    (DS / "content-holiday-2026.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_HOLIDAY_2026.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_HOLIDAY_2026.md").write_text(review_checklist(items))
    print(f"Wrote {len(items)} items")
