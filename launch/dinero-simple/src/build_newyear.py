"""Build launch/dinero-simple/content-newyear-2027.json (Jan 1-31, 2027): 8 posts that fill the gaps month 2 and the
scam series leave, rotating TikTok mids, single images, carousels and Shorts, plus POSTING_PLAN_NEWYEAR_2027.md and
REVIEW_CHECKLIST_NEWYEAR_2027.md. Slots never collide with month 2's or the scam series' (a test checks this).

    python launch/dinero-simple/src/build_newyear.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
sys.path.insert(0, str(HERE))

import newyear_2027  # noqa: E402
from build_holiday import plan_rows, review_checklist  # noqa: E402
from build_month2 import build  # noqa: E402

SCHEDULE = [
    ("vie 1 ene", "20:00", "a-propositos-fallan"),
    ("lun 4 ene", "20:00", "a-proposito-con-numero"),
    ("jue 7 ene", "20:00", "ac-actualiza-en-enero"),
    ("vie 8 ene", "20:00", "a-aumento-de-enero"),
    ("mar 12 ene", "20:00", "a-talon-linea-por-linea"),
    ("jue 14 ene", "20:00", "a-calculadora-de-sueldo"),
    ("jue 21 ene", "20:00", "ac-que-formulario-te-llega"),
    ("dom 24 ene", "12:30", "a-sin-formulario-igual-cuenta"),
]
HIGH_RISK = ("the 1099-NEC ($2,000) and 1099-K ($20,000 and 200 payments) thresholds for 2026 under the 2025 law, the "
             "Feb 1, 2027 W-2/1099 date, the 2027 Social Security wage base, and the paycheck calculator's tables: update "
             "them to 2027 (IRS inflation adjustments for 2027, SSA fact sheet for 2027) before the Jan 12 and Jan 14 posts")


def posting_plan(items: list[dict]) -> str:
    rows = plan_rows(items, SCHEDULE)
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "mid", "carousel", "image")}
    return f"""# Dinero Simple: New Year pack posting plan (January 2027)

{len(items)} extra posts for January: {counts['mid']} TikTok mids (65–90 s), {counts['image']} single images, {counts['carousel']} carousels and {counts['short']} Shorts. January is already full: month 2 (`POSTING_PLAN_MONTH_2.md`) has 24 pieces on the yearly plan, debts, the first pay stub, the W-2, free tax help and refunds, and the scam series runs Tue/Thu 12:30 and Sat 20:00. So this pack is small. It only uses empty 20:00 slots (plus Sun Jan 24 at 12:30), never more than two posts a day on one platform, and it takes new angles:

- **Propósitos:** why money resolutions die by February, and a one-line resolution template.
- **The money reset:** seven things to update in January, and what to do with a raise.
- **Tax-season prep for workers:** the pay stub line by line, which tax form arrives for each kind of work under the new higher 1099 thresholds, and why income counts without a form.

Formats rotate mid, image, carousel, Short, so no two posts in a row look alike.

**Before Jan 12:** the take-home pay calculator (`/calculadora-de-sueldo/` on the site) must be live, with the 2027 federal tables. It ships with 2026's, so paychecks dated 2027 need the IRS's 2027 numbers (the TABLES block at the top of its script). Two posts point to it. If it isn't updated, skip the image and cut the calculator line from the mid's caption.

Rules: nothing goes out until a fluent Spanish speaker has signed off the piece (`REVIEW_CHECKLIST_NEWYEAR_2027.md`) and the facts under CHECK BEFORE POSTING are confirmed. Times America/New_York.

Source: `launch/dinero-simple/content-newyear-2027.json`. Folder numbers match the rendered pack in project files `content-factory/dinero-simple/newyear-2027/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    items = build(newyear_2027.ITEMS, {})
    (DS / "content-newyear-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (DS / "POSTING_PLAN_NEWYEAR_2027.md").write_text(posting_plan(items))
    (DS / "REVIEW_CHECKLIST_NEWYEAR_2027.md").write_text(review_checklist(
        items, "New Year pack 2027", "newyear-2027", HIGH_RISK, "Tax thresholds and tables change every year; check irs.gov and ssa.gov the week you post."))
    print(f"Wrote {len(items)} items")
