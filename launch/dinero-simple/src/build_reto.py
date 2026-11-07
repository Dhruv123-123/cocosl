"""Build launch/dinero-simple/content-reto-ahorro-2026.json, the "Reto de diciembre: $10 al día" savings challenge
(Nov 30 - Dec 28, 2026): 7 posts, plus POSTING_PLAN_RETO_AHORRO_2026.md and REVIEW_CHECKLIST_RETO_AHORRO_2026.md.
Slots never collide with month 1's or the holiday pack's, and no day gets more than two posts on one platform
(a test checks both).

    python launch/dinero-simple/src/build_reto.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import reto_ahorro_2026  # noqa: E402
from build_holiday import plan_rows, review_checklist  # noqa: E402
from build_month2 import build  # noqa: E402

SCHEDULE = [
    ("lun 30 nov", "20:00", "r-dia-1"),
    ("mié 2 dic", "20:00", "rc-tabla-del-reto"),
    ("dom 6 dic", "20:00", "r-semana-1"),
    ("dom 13 dic", "20:00", "r-semana-2"),
    ("dom 20 dic", "12:30", "r-semana-3"),
    ("dom 27 dic", "12:30", "r-semana-4"),
    ("lun 28 dic", "20:00", "rc-que-hacer-con-el-reto"),
]
HIGH_RISK = ("every running total ($70, $140, $210, $280 and the $5/$2 versions), the week date ranges against the 2026 "
             "calendar, and that no post says or implies 'you will save' or shows invented personal progress")


def posting_plan(items: list[dict]) -> str:
    rows = plan_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "mid", "carousel", "image")}
    return f"""# Dinero Simple: "Reto de diciembre: $10 al día" posting plan (Nov 30 – Dec 28, 2026)

A savings challenge the viewer does *with* us: set aside $10 a day for 28 days, Nov 30 to Dec 27. That comes to $280 in the example, or $140 at $5 a day and $56 at $2. Why: PR #2's scouting (`research/scouting/finance-formats-nov-2026.md`) found the savings-challenge hook had about 6x the reach of other hook types on finance TikTok, and Dinero Simple had none.

{len(items)} posts: {counts['short']} Shorts, {counts['mid']} TikTok mid (65–90 s), {counts['carousel']} carousels and {counts['image']} single image. Day 1, a tracker to save, a check-in every Sunday, and a finale on what to do with the money. They use only free slots next to month 1 (`POSTING_PLAN_MONTH_1.md`) and the holiday pack, never more than two posts a day on one platform, and formats rotate so no two in a row look alike.

## Rules for every post in the series

1. **The numbers are an example, not a promise.** Say "si apartas $10 al día, son $280", never "vas a ahorrar".
2. **No fake progress.** We're faceless, so there's no invented "yo ahorré $X". Show only the plan's arithmetic. If followers share real results later, use them only with their permission, word for word.
3. **Each check-in stands alone** and sends new viewers to day 1. **Pin the day-1 video** on TikTok and Instagram the day it goes up. On YouTube, set day 1 as each later Short's related video.
4. **Nobody is left out:** every post offers the $5 and $2 versions.
5. **No bank or app is named.** "Un apartado o una cuenta de ahorro" is enough.

Nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_RETO_AHORRO_2026.md`) and the facts under CHECK BEFORE POSTING are confirmed. Times America/New_York.

Source: `launch/dinero-simple/content-reto-ahorro-2026.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/reto-ahorro-2026/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = build(reto_ahorro_2026.ITEMS, {})
    (DS / "content-reto-ahorro-2026.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_RETO_AHORRO_2026.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_RETO_AHORRO_2026.md").write_text(review_checklist(
        items, "savings challenge (Reto de diciembre) 2026", "reto-ahorro-2026", HIGH_RISK,
        "Native-speaker review matters most here: the challenge voice has to sound like a friend, not a translation."))
    print(f"Wrote {len(items)} items")
