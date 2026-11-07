"""Worked examples for the Scam Decoded long videos.

Each long video gets one fictional case followed step by step, from the first message to the money lost
(or saved), so the video teaches by walking through one story instead of listing tips. Examples are made
up: names, amounts and messages are fictional, and the narration says so.

long_originals.apply() inserts these (after the named beat) and recomputes the description's chapters,
so every pack JSON and every generator picks them up. Safe to rerun: earlier copies of the beats are replaced.

Content lives in examples_*.py files next to this one, one dict per batch:
    EXAMPLES[title prefix] = (insert after this heading, [(heading, on-screen text, narration, scene), ...])
"""
import importlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STYLE = ("Clean flat vector illustration, deep navy and cream with teal and amber warning accents, simple shapes: "
         "{scene}. No text, no logos, no real people.")


def examples() -> dict:
    out = {}
    for p in sorted(HERE.glob("examples_*.py")):
        mod = importlib.import_module(p.stem)
        out.update(mod.EXAMPLES)
    return out


def chapters(segments, wpm=150) -> list[str]:
    out, t = [], 0.0
    for s in segments:
        out.append(f"{int(t // 60)}:{int(t % 60):02d} {s['heading']}")
        t += len(s["narration"].split()) / wpm * 60
    return out


def _rechapter(script: dict) -> None:
    desc = script.get("description") or ""
    lines = desc.split("\n")
    idx = [i for i, l in enumerate(lines) if re.match(r"^\d+:\d\d ", l)]
    if not idx:
        return
    new = chapters(script["segments"])
    lines[idx[0]:idx[-1] + 1] = new
    script["description"] = "\n".join(lines)


def apply_examples(item: dict, table: dict | None = None) -> bool:
    table = examples() if table is None else table
    script = item["script"]
    hits = [v for k, v in table.items() if script["title"].startswith(k)]
    if not hits:
        return False
    after, beats = hits[0]
    mine = {b[0] for b in beats}
    script["segments"] = [s for s in script["segments"] if s["heading"] not in mine]  # rerun = replace
    heads = [s["heading"] for s in script["segments"]]
    k = heads.index(after) + 1
    new = [{"heading": h, "narration": n, "on_screen_text": o,
            "visual_prompt": STYLE.format(scene=scene)} for h, o, n, scene in beats]
    script["segments"][k:k] = new
    _rechapter(script)
    return True
