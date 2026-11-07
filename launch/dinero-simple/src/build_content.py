"""Build launch/dinero-simple/content.json from the English Money Made Simple scripts
plus the Spanish copy in this folder.

Spanish replaces every audience-facing field. visual_prompt, sources and claims_to_verify
stay in English (the operator checks them); the mascot is swapped for Dinero Simple's.

    python launch/dinero-simple/src/build_content.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import carousels_a, carousels_b, long_videos, shorts_a, shorts_b  # noqa: E402
from links import add_youtube_links  # noqa: E402
from originals import apply as add_original_elements  # noqa: E402

# Long videos: UTM campaign id and the site pages linked at the end of the YouTube description.
YOUTUBE_LINKS = {22: ("launch-invertir-100", ["invertir", "gratis"]),
                 23: ("launch-30-dias", ["presupuesto", "paquete", "gratis"])}

MASCOT_EN = "the small round green piggy bank mascot with big eyes"
MASCOT_ES = "the small round coral piggy bank mascot with big eyes and a tiny teal scarf"
STYLE_EN = "Warm flat vector illustration, muted greens and cream with a mustard accent, simple shapes."
STYLE_ES = "Warm flat vector illustration, coral, teal and cream, simple shapes."

# Extra things to check that only exist because of the Spanish adaptation.
EXTRA_CLAIMS = {
    13: ["Most US bank/card statements show subscription charges with English words (monthly, subscription, "
         "renewal); confirm before saying 'casi todos los cargos llegan en inglés'"],
    9: ["App menu names are given in Spanish and English (Configuración / Settings); check they match common bank apps"],
    22: ["Spanish narration runs ~15% longer than English; re-time the chapter markers in the description after voicing"],
    23: ["Spanish narration runs ~15% longer than English; re-time the chapter markers after voicing",
         "Confirm studentaid.gov Loan Simulator is still the right tool name and that the repayment-plan changes line is current"],
    21: ["Some readers may only have an ITIN; consider adding a line on whether the brokerages you recommend accept "
         "an ITIN instead of an SSN (do not claim this without checking)"],
}


def build() -> list[dict]:
    english = json.loads((ROOT / "launch" / "money-made-simple" / "content.json").read_text())
    spanish = {**shorts_a.ITEMS, **shorts_b.ITEMS, **carousels_a.ITEMS, **carousels_b.ITEMS, **long_videos.ITEMS}
    out = []
    for idx in sorted(spanish):
        src = english[idx]
        es = spanish[idx]
        en_script = src["script"]
        if len(es["segments"]) != len(en_script["segments"]):
            raise SystemExit(f"#{idx}: {len(es['segments'])} Spanish segments vs {len(en_script['segments'])} English")
        segments = []
        for (heading, on_screen, narration), en_seg in zip(es["segments"], en_script["segments"]):
            prompt = en_seg["visual_prompt"].replace(MASCOT_EN, MASCOT_ES).replace(STYLE_EN, STYLE_ES)
            segments.append({"heading": heading, "narration": narration, "on_screen_text": on_screen,
                             "visual_prompt": prompt})
        script = {
            "title": es["title"], "hook": es["hook"], "segments": segments,
            "cta": es.get("cta", shorts_a.CTA), "caption": es["caption"], "hashtags": es["hashtags"],
            "description": add_youtube_links(es["description"], *YOUTUBE_LINKS.get(idx, ("", []))),
            "thumbnail_text": es["thumbnail_text"],
            "sources": en_script.get("sources", []),
            "claims_to_verify": en_script.get("claims_to_verify", []) + EXTRA_CLAIMS.get(idx, []),
            "title_variants": [], "hook_variants": [],
        }
        out.append({"format": src["format"], "pillar": src.get("pillar", ""), "idea_angle": src.get("idea_angle", ""),
                    "source_index": idx, "source_title": en_script["title"], "script": script})
    return add_original_elements(out)


if __name__ == "__main__":
    items = build()
    path = ROOT / "launch" / "dinero-simple" / "content.json"
    path.write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} items to {path.relative_to(ROOT)}")
