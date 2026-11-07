"""Build launch/dinero-simple/content-estafas.json: 13 Shorts + 6 carousels about scams, in Spanish.

Some pieces are adapted from Scam Decoded (launch/scam-decoded/content.json). Others are new and cover
scams aimed at Spanish speakers: notario fraud, immigration impostors, remittance scams, virtual
kidnapping, money mules and ghost tax preparers. Everything needs a native-speaker read.

    python launch/dinero-simple/src/build_estafas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import estafas_carousels, estafas_shorts  # noqa: E402
from build_month1 import visual  # noqa: E402


def build() -> list[dict]:
    out = []
    for it in estafas_shorts.ITEMS + estafas_carousels.ITEMS:
        segs = []
        for heading, on_screen, narration, scene in it["segments"]:
            if len(on_screen.split()) > 12:
                raise SystemExit(f"{it['key']}: on-screen text over 12 words: {on_screen}")
            segs.append({"heading": heading, "narration": narration, "on_screen_text": on_screen,
                         "visual_prompt": visual(scene)})
        script = {"title": it["title"], "hook": it["hook"], "segments": segs, "cta": estafas_shorts.CTA,
                  "caption": it["caption"], "hashtags": it["hashtags"], "description": it["description"],
                  "thumbnail_text": it["thumbnail_text"], "sources": it["sources"],
                  "claims_to_verify": it["claims"], "title_variants": [], "hook_variants": []}
        out.append({"key": it["key"], "format": it["format"], "pillar": it["pillar"], "idea_angle": it["angle"],
                    "script": script})
    return out


if __name__ == "__main__":
    items = build()
    path = ROOT / "launch" / "dinero-simple" / "content-estafas.json"
    path.write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    counts = {f: sum(1 for i in items if i["format"] == f) for f in ("short", "carousel")}
    print(f"Wrote {len(items)} items {counts} to {path.relative_to(ROOT)}")
