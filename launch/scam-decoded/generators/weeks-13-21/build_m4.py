from pathlib import Path
import sys
import json, sys
from common import *
from m4_shorts_a import M4_SHORTS_A
from m4_shorts_b import M4_SHORTS_B
from m4_shorts_c import M4_SHORTS_C
from m4_carousels import M4_CAROUSELS as CAROUSELS
from m4_long import M4_LONG as M2_LONG

def segs(rows): return [seg(*r) for r in rows]

items = []
shorts = M4_SHORTS_A + M4_SHORTS_B + M4_SHORTS_C
for s in shorts:
    items.append({"format": "short", "pillar": s["pillar"], "idea_angle": s["angle"], "platforms": ["instagram", "youtube"],
      "script": {"title": s["title"], "hook": s["hook"], "segments": segs(s["short"]), "cta": CTA,
        "caption": s["caption"] + "\n\n" + CTA, "hashtags": s["hashtags"], "description": s["description"],
        "thumbnail_text": s["thumb"], "sources": s["sources"], "claims_to_verify": s["claims"],
        "title_variants": s["title_variants"], "hook_variants": s["hook_variants"]}})
for s in shorts:
    items.append({"format": "short", "pillar": s["pillar"], "idea_angle": s["angle"] + " (60-90s TikTok cut with a second worked example)",
      "platforms": ["tiktok"],
      "script": {"title": s["tt_title"], "hook": s["tt_hook"], "segments": segs(s["tiktok"]), "cta": CTA_TIKTOK,
        "caption": s["tt_caption"] + "\n\n" + CTA_TIKTOK, "hashtags": s["hashtags"] + ["fyp"][:0], "description": s["description"],
        "thumbnail_text": s["thumb"], "sources": s["sources"], "claims_to_verify": s["claims"],
        "title_variants": [s["title"]], "hook_variants": [s["hook"]]}})
for c in CAROUSELS:
    items.append({"format": "carousel", "pillar": c["pillar"], "idea_angle": c["angle"],
      "script": {"title": c["title"], "hook": c["hook"], "segments": segs(c["segs"]), "cta": CTA,
        "caption": c["caption"] + "\n\n" + CTA, "hashtags": c["hashtags"], "description": c["description"],
        "thumbnail_text": c["thumb"], "sources": c["sources"], "claims_to_verify": c["claims"]}})

import re
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from long_originals import apply as add_original_elements  # noqa: E402
def chapters(c, wpm=150):
    out, t = [], 0.0
    for sg in c["segs"]:
        out.append(f"{int(t//60)}:{int(t%60):02d} {sg[0]}")
        t += len(sg[1].split()) / wpm * 60
    return out

for c in M2_LONG:
    lines = chapters(c)
    c["description"] = re.sub(r"Chapters\n(?:\d+:\d\d [^\n]*\n?)+", "Chapters\n" + "\n".join(lines) + "\n", c["description"])
    assert lines[1] in c["description"], c["title"]
    items.append({"format": "long", "pillar": c["pillar"], "idea_angle": c["angle"], "platforms": ["youtube"],
      "script": {"title": c["title"], "hook": c["hook"], "segments": segs(c["segs"]), "cta": CTA_TIKTOK,
        "caption": c["caption"], "hashtags": c["hashtags"], "description": c["description"],
        "thumbnail_text": c["thumb"], "sources": c["sources"], "claims_to_verify": c["claims"],
        "title_variants": c["title_variants"]}})
add_original_elements(items)
json.dump(items, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
wc = lambda it: sum(len(x["narration"].split()) for x in it["script"]["segments"])
for i, it in enumerate(items):
    w = wc(it); print(i, it["format"], it.get("platforms"), w, f"~{w/160*60:.0f}s", it["script"]["title"])
    hook = it["script"]["hook"]
    assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
    for sg in it["script"]["segments"]:
        assert len(sg["on_screen_text"].split()) <= 12, sg["on_screen_text"]
