"""Render the originality-pass formats.

    python3 build.py            # HTML + PNG slides + MP4 walkthroughs into out/
    python3 build.py --html     # HTML only (no browser needed; used by tests)
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

import formats as F

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
esc = html.escape
WPS = 2.5  # narration speed for timing: 150 words a minute

CSS = """
:root{--ink:#0d1b2a;--cream:#f4f1ea;--teal:#2ec4b6;--teal-d:#178a80;--amber:#ff9f1c;--muted:#4a5868;--line:#d8d3c7;--paper:#fffdf9}
*{box-sizing:border-box}html,body{margin:0;font-family:Inter,system-ui,sans-serif;color:var(--ink)}
.kicker{font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--teal-d);font-size:26px}
mark{background:transparent;color:inherit;border-radius:8px;padding:0 4px;transition:all .35s}
mark.on{background:#ffe2b3;box-shadow:0 0 0 4px var(--amber);}
mark.on::after{content:attr(data-n);display:inline-block;background:var(--amber);color:var(--ink);font-weight:800;font-size:.7em;
  border-radius:50%;width:1.4em;height:1.4em;line-height:1.4em;text-align:center;margin-left:6px;vertical-align:middle}
.brand{display:flex;align-items:center;gap:14px;font-weight:800;font-size:30px}
.brand i{display:inline-block;width:34px;height:38px;background:var(--teal);border-radius:17px 17px 20px 20px/14px 14px 24px 24px}
"""


def mark(text: str, phrases: list[str]) -> str:
    out = esc(text)
    for n, ph in enumerate(phrases, 1):
        e = esc(ph)
        assert e in out, (ph, text)
        out = out.replace(e, f'<mark data-i="{n}" data-n="{n}">{e}</mark>', 1)
    return out


def secs(line: str) -> float:
    return round(max(4.0, len(line.split()) / WPS + 1.0), 1)


# ------------------------------------------------------------------ walkthrough page
def walkthrough_html(w: dict) -> tuple[str, float]:
    flags_by_msg: dict[int, list[tuple[int, str]]] = {}
    for n, (mi, ph, _) in enumerate(w["flags"], 1):
        flags_by_msg.setdefault(mi, []).append((n, ph))
    bubbles = []
    for mi, (side, text) in enumerate(w["messages"]):
        body = esc(text)
        for n, ph in flags_by_msg.get(mi, []):
            if ph == w["sender"]:
                continue
            e = esc(ph)
            assert e in body, (w["id"], ph)
            body = body.replace(e, f'<mark id="f{n}" data-n="{n}">{e}</mark>', 1)
        bubbles.append(f'<div class="b {side}" id="m{mi}">{body}</div>')
    sender = esc(w["sender"])
    for n, (mi, ph, _) in enumerate(w["flags"], 1):
        if ph == w["sender"]:
            sender = f'<mark id="f{n}" data-n="{n}">{sender}</mark>'
    labels = "".join(f'<li id="l{n}"><b>{n}</b>{esc(lab)}</li>' for n, (_, _, lab) in enumerate(w["flags"], 1))
    timeline, t = [], 0.0
    nflags, nsteps = len(w["flags"]), len(w["steps"])
    for k, (line, _) in enumerate(w["steps"]):
        d = secs(line)
        action = "msgs" if k == 0 else (f"flag{k}" if k <= nflags else ("do" if k == nsteps - 1 else "hold"))
        timeline.append({"t": round(t, 2), "d": d, "action": action, "cap": line})
        t += d
    total = round(t + 1.5, 1)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:1080px;height:1920px;background:var(--cream);overflow:hidden;position:relative}}
.top{{position:absolute;left:60px;right:60px;top:56px}} .top h1{{font-size:50px;line-height:1.1;margin:14px 0 0;font-weight:800}}
.phone{{position:absolute;left:90px;right:90px;top:300px;height:1040px;background:#fff;border:14px solid var(--ink);border-radius:64px;overflow:hidden}}
.bar{{background:#f2f2f5;border-bottom:1px solid #ddd;padding:26px 30px 18px;text-align:center;font-size:28px;color:#333}}
.bar small{{display:block;font-size:20px;color:#888;margin-bottom:4px}}
.chat{{padding:26px 26px;display:flex;flex-direction:column;gap:18px}}
.b{{max-width:86%;font-size:31px;line-height:1.36;padding:18px 24px;border-radius:30px;opacity:0;transform:translateY(16px);transition:all .4s}}
.b.show{{opacity:1;transform:none}} .b.in{{background:#e9e9eb;align-self:flex-start}} .b.out{{background:#2f7cf6;color:#fff;align-self:flex-end}}
.labels{{position:absolute;left:90px;right:90px;top:1370px;list-style:none;margin:0;padding:0;font-size:31px;line-height:1.3}}
.labels li{{display:flex;gap:16px;align-items:flex-start;margin-bottom:12px;opacity:0;transition:opacity .4s}} .labels li.show{{opacity:1}}
.labels b{{flex:0 0 46px;height:46px;border-radius:50%;background:var(--amber);display:flex;align-items:center;justify-content:center}}
.cap{{position:absolute;left:60px;right:60px;bottom:70px;background:var(--ink);color:var(--cream);font-size:34px;line-height:1.3;padding:22px 28px;border-radius:22px;min-height:120px}}
.do{{position:absolute;inset:300px 90px auto 90px;height:1040px;background:var(--ink);color:var(--cream);border-radius:64px;padding:90px 70px;opacity:0;transition:opacity .5s;display:flex;flex-direction:column;justify-content:center}}
.do.show{{opacity:1}} .do .kicker{{color:var(--amber)}} .do p{{font-size:58px;font-weight:800;line-height:1.15;margin:24px 0 0}}
.foot{{position:absolute;left:60px;bottom:22px;font-size:20px;color:var(--muted)}}
</style></head><body>
<div class="top"><div class="brand"><i></i>Scam Decoded · walkthrough</div><h1>{esc(w['title'])}</h1></div>
<div class="phone"><div class="bar"><small>{esc(w['app'])}</small>{sender}</div><div class="chat">{''.join(bubbles)}</div></div>
<ul class="labels">{labels}</ul>
<div class="do"><div class="kicker">What to do</div><p>{esc(w['do'])}</p></div>
<div class="cap" id="cap"></div>
<div class="foot">Fictional example. Links masked. Numbers in the 555-01xx range aren't real.</div>
<script>
const T={json.dumps(timeline)}, M={len(w['messages'])};
window.start=()=>{{T.forEach(s=>setTimeout(()=>run(s),s.t*1000));}};
function run(s){{document.getElementById('cap').textContent=s.cap;
 if(s.action==='msgs'){{for(let i=0;i<M;i++)setTimeout(()=>document.getElementById('m'+i).classList.add('show'),i*(s.d*1000/(M+0.5)));}}
 if(s.action.startsWith('flag')){{const n=s.action.slice(4);document.getElementById('f'+n).classList.add('on');document.getElementById('l'+n).classList.add('show');}}
 if(s.action==='do'){{document.querySelector('.do').classList.add('show');}}}}
if(location.hash==='#end'){{document.querySelectorAll('.b').forEach(b=>b.classList.add('show'));document.querySelectorAll('mark,li').forEach(e=>e.classList.add('on','show'));}}
</script></body></html>"""
    return page, total


# ------------------------------------------------------------------ quiz slides
def quiz_message(q: dict, upto: int) -> str:
    body, sender = esc(q["message"]), esc(q["sender"])
    for n, (ph, _) in enumerate(q["flags"], 1):
        e, tag = esc(ph), f'<mark data-i="{n}" data-n="{n}">{esc(ph)}</mark>'
        if e in body:
            body = body.replace(e, tag, 1)
        else:
            assert e in sender, (q["id"], ph)
            sender = sender.replace(e, tag, 1)
    box = {"text": "msg text", "email": "msg email", "call": "msg call"}[q["kind"]]
    head = {"text": f'<div class="from">{sender}</div>', "email": f'<div class="from">From: {sender}</div>',
            "call": f'<div class="from">📞 {sender}</div>'}[q["kind"]]
    html_ = f'<div class="{box}">{head}<div class="body">{body}</div></div>'
    for n in range(1, len(q["flags"]) + 1):
        if n <= upto:
            html_ = html_.replace(f'data-i="{n}"', f'data-i="{n}" class="on"', 1)
    return html_


SLIDE_CSS = CSS + """
body{width:1080px;height:1350px;overflow:hidden;background:var(--cream);position:relative}
.wrap{position:absolute;inset:70px 70px 110px}
h1{font-size:64px;line-height:1.08;margin:16px 0 34px;font-weight:800}
.msg{background:#fff;border-radius:34px;padding:34px 38px;font-size:36px;line-height:1.42;box-shadow:0 8px 30px rgba(13,27,42,.12)}
.msg .from{font-size:26px;color:var(--muted);margin-bottom:14px;font-weight:600}
.msg.text .body{background:#e9e9eb;border-radius:28px;padding:22px 26px}
.msg.call{background:var(--ink);color:var(--cream)} .msg.call .from{color:#9fb0c0}
.label{margin-top:34px;display:flex;gap:20px;align-items:center;font-size:40px;font-weight:700;line-height:1.2}
.label b{flex:0 0 70px;height:70px;border-radius:50%;background:var(--amber);display:flex;align-items:center;justify-content:center;font-size:38px}
.foot{position:absolute;left:70px;right:70px;bottom:40px;display:flex;justify-content:space-between;font-size:22px;color:var(--muted)}
.big{font-size:120px;font-weight:800;line-height:1;margin:40px 0 20px;color:var(--teal-d)}
.dark{background:var(--ink);color:var(--cream)} .dark .kicker{color:var(--amber)} .dark .foot{color:#9fb0c0}
"""


def slide(inner: str, n: int, total: int, dark: bool = False, note: str = "Fictional example. Links masked.") -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{SLIDE_CSS}</style></head>'
            f'<body class="{"dark" if dark else ""}"><div class="wrap">{inner}</div>'
            f'<div class="foot"><span class="brand" style="font-size:22px"><i style="width:22px;height:25px"></i>Scam Decoded</span>'
            f'<span>{esc(note)}</span><span>{n}/{total}</span></div></body></html>')


def quiz_slides(q: dict) -> list[str]:
    nf = len(q["flags"])
    total = nf + 3
    s = [slide(f'<div class="kicker">Spot the red flags</div><h1>How many can you find?</h1>{quiz_message(q, 0)}'
               f'<div class="label">Count them, then swipe →</div>', 1, total)]
    s.append(slide(f'<div class="kicker">Your answer?</div><div class="big">?</div><h1>Got a number?<br>Swipe to check.</h1>'
                   f'<p style="font-size:38px">Hint: there are {nf}.</p>', 2, total, dark=True))
    for k, (_, lab) in enumerate(q["flags"], 1):
        s.append(slide(f'<div class="kicker">Red flag {k} of {nf}</div>{quiz_message(q, k)}'
                       f'<div class="label"><b>{k}</b>{esc(lab)}</div>', k + 2, total))
    s.append(slide(f'<div class="kicker">{nf} red flags</div><h1>What to do</h1><p style="font-size:44px;line-height:1.3">{esc(q["fix"])}</p>'
                   f'<p style="font-size:34px;margin-top:60px">How many did you get? Save this, and send it to someone who\'d fall for it.</p>',
                   total, total, dark=True))
    return s


# ------------------------------------------------------------------ chart slides
def chart_svg(c: dict, w: int = 940, h: int = 760) -> str:
    vals, labs, vlabs = c["values"], c["labels"], c["value_labels"]
    mx = max(vals)
    parts = []
    if c["kind"] == "bars":
        n = len(vals); gap = 26; bw = (w - gap * (n + 1)) / n; base = h - 70
        for i, (v, lab, vl) in enumerate(zip(vals, labs, vlabs)):
            bh = (base - 80) * v / mx; x = gap + i * (bw + gap)
            col = "#ff9f1c" if i == n - 1 else "#2ec4b6"
            parts.append(f'<rect x="{x:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="10" fill="{col}"/>')
            parts.append(f'<text x="{x+bw/2:.1f}" y="{base-bh-16:.1f}" text-anchor="middle" font-size="{34 if n < 4 else 30}" font-weight="800" fill="#0d1b2a">{esc(vl)}</text>')
            parts.append(f'<text x="{x+bw/2:.1f}" y="{base+46:.1f}" text-anchor="middle" font-size="30" fill="#4a5868">{esc(lab)}</text>')
        parts.append(f'<line x1="0" x2="{w}" y1="{base}" y2="{base}" stroke="#0d1b2a" stroke-width="3"/>')
    else:
        n = len(vals); rh = (h - 20) / n; lw = 270
        for i, (v, lab, vl) in enumerate(zip(vals, labs, vlabs)):
            bw = (w - lw - 140) * v / mx; y = 10 + i * rh
            col = "#ff9f1c" if i == 0 else "#2ec4b6"
            parts.append(f'<text x="{lw-18}" y="{y+rh/2+11:.1f}" text-anchor="end" font-size="31" fill="#0d1b2a">{esc(lab)}</text>')
            parts.append(f'<rect x="{lw}" y="{y+rh*0.18:.1f}" width="{bw:.1f}" height="{rh*0.64:.1f}" rx="10" fill="{col}"/>')
            parts.append(f'<text x="{lw+bw+14:.1f}" y="{y+rh/2+12:.1f}" font-size="34" font-weight="800" fill="#0d1b2a">{esc(vl)}</text>')
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Inter, sans-serif">{"".join(parts)}</svg>'


def chart_slide(c: dict) -> str:
    inner = (f'<div class="kicker">Real FTC data</div><h1 style="font-size:54px;margin-bottom:20px">{esc(c["title"])}</h1>'
             f'{chart_svg(c)}<p style="font-size:38px;font-weight:700;margin:18px 0 0">{esc(c["takeaway"])}</p>'
             f'<p style="font-size:21px;color:var(--muted);margin:16px 0 0;line-height:1.35">Source: {esc(c["source"])}</p>')
    return slide(inner, 1, 1, note="Data: FTC Consumer Sentinel")


# ------------------------------------------------------------------ build
def main() -> None:
    html_only = "--html" in sys.argv
    shutil.rmtree(OUT, ignore_errors=True)
    jobs, index = [], {"walkthroughs": [], "quizzes": [], "charts": []}
    for w in F.WALKTHROUGHS:
        page, total = walkthrough_html(w)
        d = OUT / "walkthroughs" / w["id"]; d.mkdir(parents=True, exist_ok=True)
        (d / "page.html").write_text(page)
        vo = "\n\n".join(f"[{i+1}] {line}" for i, (line, _) in enumerate(w["steps"]))
        (d / "voiceover.txt").write_text(f"{w['title']}\nRead at an easy pace; each line has its own on-screen step.\n\n{vo}\n")
        jobs.append({"type": "video", "html": str(d / "page.html"), "out": str(d / f"{w['id']}.mp4"), "w": 1080, "h": 1920, "duration": total})
        jobs.append({"type": "png", "html": str(d / "page.html") + "#end", "out": str(d / "cover.png"), "w": 1080, "h": 1920})
        index["walkthroughs"].append({"id": w["id"], "title": w["title"], "seconds": total, "flags": len(w["flags"])})
    for q in F.QUIZZES:
        d = OUT / "quizzes" / q["id"]; d.mkdir(parents=True, exist_ok=True)
        for k, s in enumerate(quiz_slides(q), 1):
            (d / f"slide-{k:02d}.html").write_text(s)
            jobs.append({"type": "png", "html": str(d / f"slide-{k:02d}.html"), "out": str(d / f"slide-{k:02d}.png"), "w": 1080, "h": 1350})
        index["quizzes"].append({"id": q["id"], "title": q["title"], "slides": len(q["flags"]) + 3})
    for c in F.CHARTS:
        d = OUT / "charts"; d.mkdir(parents=True, exist_ok=True)
        (d / f"{c['id']}.html").write_text(chart_slide(c))
        jobs.append({"type": "png", "html": str(d / f"{c['id']}.html"), "out": str(d / f"{c['id']}.png"), "w": 1080, "h": 1350})
        index["charts"].append({"id": c["id"], "title": c["title"], "source_url": c["url"]})
    (OUT / "index.json").write_text(json.dumps(index, indent=2))
    (OUT / "manifest.json").write_text(json.dumps(jobs, indent=2))
    if not html_only:
        subprocess.run(["node", str(HERE / "render.mjs"), str(OUT / "manifest.json")], check=True)
    print(json.dumps({k: len(v) for k, v in index.items()}))


if __name__ == "__main__":
    main()
