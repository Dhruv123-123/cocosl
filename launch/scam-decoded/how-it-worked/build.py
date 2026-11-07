"""Build the 'How the scam actually worked' series.

    python3 build.py           ->  ../how-it-worked.json, ../HOW_IT_WORKED_SERIES.md, out/<slug>.html
    python3 build.py --png     ->  also renders out/<slug>.png (1920x1080) with Playwright via render_boards.mjs

Parts 1-8 take the second Sunday long-video slot of each month, Jul 2027 - Feb 2028 (no weekly plan exists yet for those weeks),
so the series runs monthly without breaking the one-long-video-a-week cap. Future weekly plans must leave them free.
"""
import html
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "generators" / "weeks-22-26"))
from common import CTA_TIKTOK, P_FAMILY, P_INVEST, P_SECURITY, P_TEXT, seg  # noqa: E402
from series import OUTLINE, PARTS as PARTS_1_3  # noqa: E402
from parts_4_8 import PARTS_4_8  # noqa: E402

PARTS = PARTS_1_3 + PARTS_4_8

OUT = HERE / "out"
ROOT = HERE.parent
SLOTS = {1: "2027-07-11", 2: "2027-08-08", 3: "2027-09-12", 4: "2027-10-10", 5: "2027-11-14", 6: "2027-12-12",
         7: "2028-01-09", 8: "2028-02-13"}
PILLAR = {1: P_FAMILY, 2: P_SECURITY, 3: P_TEXT, 4: P_TEXT, 5: P_FAMILY, 6: P_INVEST, 7: P_FAMILY, 8: P_FAMILY}
esc = html.escape


def chapters(rows, wpm=150):
    out, t = [], 0.0
    for h, n in rows:
        out.append(f"{int(t // 60)}:{int(t % 60):02d} {h}")
        t += len(n.split()) / wpm * 60
    return out


def board_html(p):
    b = p["board"]
    facts = "".join(f'<div class="fact"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for v, k in b["facts"])
    steps = "".join(f'<li><i>{n}</i><span>{esc(s)}</span></li>' for n, s in enumerate(b["steps"], 1))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
:root{{--ink:#0d1b2a;--cream:#f4f1ea;--teal:#2ec4b6;--teal-d:#178a80;--amber:#ff9f1c;--muted:#4a5868;--paper:#fffdf9}}
*{{box-sizing:border-box}}body{{margin:0;width:1920px;height:1080px;background:var(--ink);font-family:Inter,system-ui,sans-serif;color:var(--cream);padding:72px 96px;display:flex;flex-direction:column}}
.kicker{{font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);font-size:26px}}
h1{{font-size:76px;margin:14px 0 36px;line-height:1.05}}
.row{{display:flex;gap:64px;flex:1}}
.facts{{display:flex;flex-direction:column;gap:22px;width:520px}}
.fact{{background:#16283b;border-left:10px solid var(--amber);border-radius:14px;padding:22px 30px}}
.fact b{{display:block;font-size:68px;color:var(--amber);line-height:1}}.fact span{{font-size:28px;color:#c9d3dc}}
ol{{list-style:none;margin:0;padding:0;flex:1;display:flex;flex-direction:column;gap:18px}}
li{{display:flex;align-items:center;gap:24px;background:var(--paper);color:var(--ink);border-radius:16px;padding:20px 28px;font-size:34px;font-weight:600}}
li i{{font-style:normal;flex:0 0 58px;height:58px;border-radius:50%;background:var(--teal);color:var(--ink);display:flex;align-items:center;justify-content:center;font-weight:800}}
.src{{font-size:22px;color:#9fb0bf;margin-top:24px}}
.brand{{position:absolute;right:96px;bottom:60px;font-weight:800;font-size:28px;display:flex;gap:12px;align-items:center}}
.brand em{{display:inline-block;width:30px;height:34px;background:var(--teal);border-radius:15px 15px 18px 18px/12px 12px 22px 22px}}
</style></head><body><div class="brand"><em></em>Scam Decoded</div>
<div class="kicker">How the scam actually worked · Part {p['part']} · {esc(b['kicker'])}</div>
<h1>{esc(b['headline'])}</h1>
<div class="row"><div class="facts">{facts}</div><ol>{steps}</ol></div>
<div class="src">{esc(b['source'])}</div></body></html>"""


def item(p):
    rows = list(p["segs"])
    desc = (p["description_intro"] + "\n\nChapters\n" + "\n".join(chapters(rows)) + "\n\nSources\n" +
            "\n".join(p["sources"]) + "\n\nOther examples in this video are fictional.")
    return {"format": "long", "pillar": PILLAR[p["part"]], "platforms": ["youtube"], "series": "How the scam actually worked",
            "part": p["part"], "post_on": f"{SLOTS[p['part']]} 10:00", "look": "screen recording",
            "original_element": p["original_element"], "idea_angle": p["description_intro"],
            "script": {"title": p["title"], "hook": p["hook"],
                       "segments": [seg(h, n, h, "Face cam with the case board and source document; see original_element")
                                    for h, n in rows],
                       "cta": CTA_TIKTOK, "caption": p["caption"], "hashtags": p["hashtags"], "description": desc,
                       "thumbnail_text": p["thumb"], "sources": p["sources"], "claims_to_verify": p["claims"],
                       "title_variants": p["title_variants"]}}


def series_md(items):
    out = ["# How the scam actually worked: series plan", "",
           "One real, documented scam per long video, told step by step from public records (DOJ, FTC, court filings), "
           "ending with the three checks that stop it. From the competitor teardown on PR #2 (idea 4). Every part has "
           "an original element: a case board we draw from the public record, plus Dhruv on camera with the source "
           "document, in his own voice.", "",
           "Schedule: one part a month, in the second Sunday 10:00 long-video slot of the month, Jul 11 2027 to "
           "Feb 13 2028 (no weekly plan covers those months yet). That keeps the one-long-video-a-week cap. Future weekly plans must leave "
           "these Sundays free. Nothing has been posted.", "",
           "Rules for every part: say \"alleged\" for anything not proven in court, and say defendants are presumed "
           "innocent until convicted. Use only facts in the cited public record. No real victims' names or faces. "
           "Re-check every claim against its source the week it posts.", "",
           "| Part | Status | Case | Angle |", "|---|---|---|---|"]
    for o in OUTLINE:
        out.append(f"| {o['part']} | {o['status']} | [{o['case']}]({o['source']}) | {o['angle']} |")
    out += ["", "## Produced parts", ""]
    for i in items:
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        out.append(f"- **Part {i['part']}, {i['post_on'][:10]}:** {i['script']['title']} ({w} words, about "
                   f"{round(w / 150)} minutes). Case board: `how-it-worked/out/{PARTS[i['part'] - 1]['slug']}.png`.")
    return "\n".join(out) + "\n"


def main():
    items = [item(p) for p in PARTS]
    OUT.mkdir(exist_ok=True)
    for p in PARTS:
        (OUT / f"{p['slug']}.html").write_text(board_html(p))
    for i in items:
        assert any(ch.isdigit() for ch in i["script"]["hook"].split(".")[0][:60]), i["script"]["hook"]
    (ROOT / "how-it-worked.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "HOW_IT_WORKED_SERIES.md").write_text(series_md(items))
    if "--png" in sys.argv:
        subprocess.run(["node", str(HERE / "render_boards.mjs"), str(OUT)], check=True)
    for i in items:
        print(i["part"], i["post_on"], sum(len(s["narration"].split()) for s in i["script"]["segments"]), i["script"]["title"])


if __name__ == "__main__":
    main()
