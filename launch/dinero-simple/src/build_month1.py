"""Build launch/dinero-simple/content-month-1.json (Nov 21 - Dec 31, 2026): 20 Shorts, 10 carousels
and 2 long videos written in Spanish for Dinero Simple (not adapted from English).

    python launch/dinero-simple/src/build_month1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import month1_carousels, month1_long, month1_shorts_a, month1_shorts_b  # noqa: E402
from build_content import MASCOT_ES, STYLE_ES  # noqa: E402

NATIVE = "A fluent es-US speaker has reviewed every word (original Spanish copy, not a translation)"


def visual(scene: str) -> str:
    scene = scene.replace("M ", MASCOT_ES + " ", 1) if scene.startswith("M ") else scene
    return f"{STYLE_ES} {scene}. No text, no logos, no real people."


def build() -> list[dict]:
    out = []
    for it in month1_shorts_a.ITEMS + month1_shorts_b.ITEMS + month1_carousels.ITEMS + month1_long.ITEMS:
        segs = []
        for heading, on_screen, narration, scene in it["segments"]:
            if len(on_screen.split()) > 12:
                raise SystemExit(f"{it['key']}: on-screen text over 12 words: {on_screen}")
            segs.append({"heading": heading, "narration": narration, "on_screen_text": on_screen,
                         "visual_prompt": visual(scene)})
        script = {"title": it["title"], "hook": it["hook"], "segments": segs, "cta": month1_shorts_a.CTA,
                  "caption": it["caption"], "hashtags": it["hashtags"], "description": it["description"],
                  "thumbnail_text": it["thumbnail_text"], "sources": it["sources"],
                  "claims_to_verify": it["claims"], "title_variants": [], "hook_variants": []}
        out.append({"key": it["key"], "format": it["format"], "pillar": it["pillar"], "idea_angle": it["angle"],
                    "script": script})
    return out


if __name__ == "__main__":
    items = build()
    path = ROOT / "launch" / "dinero-simple" / "content-month-1.json"
    path.write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel", "long")}
    print(f"Wrote {len(items)} items {counts} to {path.relative_to(ROOT)}")
