"""Weeks 31-34 (Sun Jun 6 - Sat Jul 3 2027): 12 Shorts, 12 TikTok minute cuts, 8 carousels, 4 long videos.

    python3 build.py   ->  ../../weeks-31-34.json and ../../POSTING_PLAN_WEEKS_31-34.md
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "weeks-22-26"))
from common import CTA, CTA_TIKTOK, KIT, seg  # noqa: E402
from shorts import SHORTS  # noqa: E402
from carousels import CAROUSELS  # noqa: E402
from long import LONG  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from long_originals import apply as add_original_elements  # noqa: E402

ROOT = HERE.parent.parent
VOICE = "Dhruv records the narration in his own voice. No AI voice on TikTok cuts."
LOOK_NOTE = {
    "illustrated": "Illustrated beats with on-screen text.",
    "walkthrough": "Phone-screen walkthrough mockup (originality/render.mjs style), messages and flags timed to the narration.",
    "face cam": "Dhruv on camera for the hook and the fix, illustrated beats between.",
    "data chart": "A real FTC number on screen as its own beat, drawn like originality/out/charts.",
    "quiz pause": "A 3-second PAUSE card before the answer, quiz-style.",
    "screen recording": "Face cam plus Dhruv's own screen recordings (see original_element).",
}
WEEK_START = {31: dt.date(2027, 6, 6), 32: dt.date(2027, 6, 13), 33: dt.date(2027, 6, 20), 34: dt.date(2027, 6, 27)}
PUSH = {31: "newsletter", 32: "kit", 33: "Protect Your Parents", 34: "kit"}


def segs(rows):
    return [seg(*r) for r in rows]


def words(item):
    return sum(len(s["narration"].split()) for s in item["script"]["segments"])


def chapters(rows, wpm=150):
    out, t = [], 0.0
    for h, n in rows:
        out.append(f"{int(t // 60)}:{int(t % 60):02d} {h}")
        t += len(n.split()) / wpm * 60
    return out


def build():
    items, slots = [], []
    by_week = lambda xs, w: [x for x in xs if x["week"] == w]
    for w, start in WEEK_START.items():
        day = lambda n: (start + dt.timedelta(days=n)).isoformat()
        L = by_week(LONG, w)[0]
        rows = [(h, n) for h, n in L["segs"]]
        desc = L["description_intro"] + "\n\nChapters\n" + "\n".join(chapters(rows)) + "\n\nExamples are fictional."
        items.append({"format": "long", "pillar": L["pillar"], "platforms": ["youtube"], "week": w, "post_on": f"{day(0)} 10:00",
                      "look": "screen recording", "original_element": L["original_element"],
                      "idea_angle": L["description_intro"],
                      "script": {"title": L["title"], "hook": L["hook"],
                                 "segments": [seg(h, n, h, "Face cam or screen recording; see original_element") for h, n in rows],
                                 "cta": CTA_TIKTOK, "caption": L["caption"], "hashtags": L["hashtags"], "description": desc,
                                 "thumbnail_text": L["thumb"], "sources": L["sources"], "claims_to_verify": L["claims"],
                                 "title_variants": L["title_variants"]}})
        shorts, cars = by_week(SHORTS, w), by_week(CAROUSELS, w)
        for k, (s, d) in enumerate(zip(shorts, (1, 3, 5))):
            plug = f"\n\n{KIT}" if PUSH[w] == "kit" and k == 0 else ""
            items.append({"format": "short", "pillar": s["pillar"], "platforms": ["instagram", "youtube"], "week": w,
                          "post_on": f"{day(d)} 12:00", "look": s["look"],
                          "original_element": s.get("original_element", LOOK_NOTE[s["look"]]),
                          "idea_angle": s["description"],
                          "script": {"title": s["title"], "hook": s["hook"], "segments": segs(s["short"]), "cta": CTA,
                                     "caption": s["caption"] + plug + "\n\n" + CTA, "hashtags": s["hashtags"],
                                     "description": s["description"], "thumbnail_text": s["thumb"],
                                     "sources": s["sources"], "claims_to_verify": s["claims"]}})
            tt_rows = [("Hook", s["tt_hook"] + " " + s["short"][0][1], s["thumb"], s["short"][0][3])]
            tt_rows += list(s["short"][1:-1]) + list(s["tt_extra"]) + [s["short"][-1]]
            items.append({"format": "short", "pillar": s["pillar"], "platforms": ["tiktok"], "week": w,
                          "post_on": f"{day(d)} 18:00", "look": s["tt_look"],
                          "original_element": LOOK_NOTE[s["tt_look"]] + " " + VOICE,
                          "idea_angle": s["description"] + " (65-90s TikTok minute cut with a pause beat)",
                          "script": {"title": s["tt_title"], "hook": s["tt_hook"], "segments": segs(tt_rows),
                                     "cta": CTA_TIKTOK, "caption": s["caption"] + "\n\n" + CTA_TIKTOK,
                                     "hashtags": s["hashtags"], "description": s["description"],
                                     "thumbnail_text": s["thumb"], "sources": s["sources"],
                                     "claims_to_verify": s["claims"], "title_variants": [s["title"]]}})
        for c, d in zip(cars, (2, 4)):
            items.append({"format": "carousel", "pillar": c["pillar"], "platforms": ["instagram"], "week": w,
                          "post_on": f"{day(d)} 19:30", "look": c["look"],
                          "original_element": f"Carousel in {c['look']} format.",
                          "idea_angle": c["description"],
                          "script": {"title": c["title"], "hook": c["hook"], "segments": segs(c["segs"]), "cta": CTA,
                                     "caption": c["caption"] + "\n\n" + CTA, "hashtags": c["hashtags"],
                                     "description": c["description"], "thumbnail_text": c["thumb"],
                                     "sources": c["sources"], "claims_to_verify": c["claims"]}})
    items.sort(key=lambda i: i["post_on"])
    return items


def check(items):
    videos = [i for i in items if i["format"] != "carousel"]
    for a, b in zip(videos, videos[1:]):
        assert a["look"] != b["look"], (a["script"]["title"], b["script"]["title"], a["look"])
    for i in items:
        w, hook = words(i), i["script"]["hook"]
        assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
        if i["platforms"] == ["tiktok"]:
            assert 165 <= w <= 230, (i["script"]["title"], w)
        elif i["format"] == "short":
            assert 60 <= w <= 120, (i["script"]["title"], w)
        for s in i["script"]["segments"]:
            assert len(s["on_screen_text"].split()) <= 12, s["on_screen_text"]


def plan(items):
    out = ["# Scam Decoded: weeks 31–34 posting plan (Sun Jun 6 – Sat Jul 3, 2027)", "",
           "36 items: 12 Shorts (Reels + YouTube Shorts, 12:00), 12 TikTok minute cuts (18:00, 65–90 s, Dhruv's own "
           "voice), 8 Instagram carousels (19:30) and 4 YouTube long videos (Sundays 10:00). Times America/New_York.", "",
           "Format rotation (ORIGINALITY_PASS.md): consecutive videos never share a visual format; the `Look` column "
           "says which. Each long video has its own `original_element` (screen recordings Dhruv makes).", "",
           "Weekly themes and push: wk 31 teens and summer money (newsletter), wk 32 car and small business scams before "
           "Father's Day (Family kit), wk 33 official-looking scams, starting Father's Day Sun Jun 20 (Protect Your "
           "Parents), wk 34 the 4th of July weekend (Family kit). Juneteenth is Sat Jun 19; Sun Jul 4 is the next "
           "plan's first day.", "",
           "| # | When | Where | Format | Look | Title |", "|---|---|---|---|---|---|"]
    where = lambda i: {"youtube": "YouTube", "tiktok": "TikTok", "instagram": "Instagram"}[i["platforms"][0]] \
        if len(i["platforms"]) == 1 else "Reels + Shorts"
    for n, i in enumerate(items):
        d = dt.date.fromisoformat(i["post_on"][:10])
        fmt = {"long": "Long", "carousel": "Carousel"}.get(i["format"], "TikTok cut" if i["platforms"] == ["tiktok"] else "Short")
        out.append(f"| #{n} | {d.strftime('%a %b')} {d.day} {i['post_on'][11:]} | {where(i)} | {fmt} | {i['look']} | "
                   f"{i['script']['title']} |")
    out += ["", "Before publishing: verify every item's `claims_to_verify` against its `sources` that week, record the "
            "voiceovers (TikTok cuts and long videos in Dhruv's own voice), and make the screen recordings listed in "
            "each long video's `original_element`."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    items = build()
    check(items)
    add_original_elements(items)
    (ROOT / "weeks-31-34.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "POSTING_PLAN_WEEKS_31-34.md").write_text(plan(items))
    for n, i in enumerate(items):
        print(n, i["post_on"], i["format"], i["platforms"][0], i["look"], words(i), i["script"]["title"][:60])
