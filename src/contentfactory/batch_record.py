"""`factory batch-record`: one plan for everything waiting on you to record, across every brand.

It takes the list `factory recordings` shows (narration takes for own-voice brands, footage beats whose
file isn't on disk yet, and planned screen recordings for long videos) and groups it into recording
sessions by setup, so you set up the mic or the screen recorder once and do a whole batch:

* voice sessions: one teleprompter script per post, read straight through. Save each take where the
  factory looks for it (voice/<brand>/post-<id>.wav), then `factory voice` is not even needed.
* screen sessions: a shot list per post (what to show, roughly how long, the file name to save as).

Sessions are filled soonest-publishing first, up to `--minutes` of recording each (finished minutes x
`--takes`, for retakes and setup). Each session folder gets SHOT_LIST.md, teleprompter.html (big text,
dark, adjustable size and scroll, mirror for a glass prompter), teleprompter.txt and session.json.

    factory batch-record                       # output/batch-record/<date>/session-NN-<brand>-<setup>/
    factory batch-record --brand scam-decoded --days 21 --minutes 30
    factory batch-record attach <session dir>  # link the recorded screen files into their posts' beats

Nothing is recorded, posted or changed by planning; `attach` only sets Segment.footage on the beats
whose file now exists, and the post needs `factory render <id>` again afterwards.
"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from .originality import element_text

WPM = 150  # spoken words per minute
STOP = set(["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "how", "i", "if", "in", "into", "is", "it", "its", "of", "on", "or", "that", "the", "this", "to", "was", "what", "when", "why", "with", "you", "your", "my", "our"])


def _words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", (t or "").lower()) if w not in STOP and len(w) > 2}


def _minutes(text: str) -> float:
    return round(len((text or "").split()) / WPM, 1)


def _best_beat(segs: list[dict], what: str) -> int:
    """The beat a planned recording belongs on: most words in common, else the second beat."""
    want = _words(what)
    scores = [len(want & _words(f"{s.get('heading', '')} {s.get('narration', '')}")) for s in segs]
    if scores and max(scores) > 0:
        return scores.index(max(scores))
    return min(1, len(segs) - 1) if segs else 0


def tasks(factory, brand: str = "", days: int | None = None, now: datetime | None = None) -> list[dict]:
    from .planner import recordings
    now = now or datetime.now(UTC)
    horizon = (now + timedelta(days=days)).isoformat() if days else None
    out = []
    for t in recordings(factory):
        if brand and t["brand"] != brand:
            continue
        if horizon and t["publish_at"] and t["publish_at"] > horizon:
            continue
        post = factory.db.get("posts", t["post_id"]) or {}
        script = post.get("script") if isinstance(post.get("script"), dict) else {}
        segs = script.get("segments") or []
        base = {"post_id": t["post_id"], "brand": t["brand"], "format": t["format"], "title": t["title"],
                "publish_at": t["publish_at"]}
        for need in t["needs"]:
            if need.startswith("voice"):
                lines = [script.get("hook", "")] + [s.get("narration", "") for s in segs] + [script.get("cta", "")]
                lines = [ln.strip() for ln in lines if ln and ln.strip()]
                # the hook is usually the first beat's opening line; don't read it twice
                if len(lines) > 1 and lines[1].startswith(lines[0]):
                    lines = lines[1:]
                out.append({**base, "kind": "voice", "save_as": f"voice/{t['brand']}/post-{t['post_id']}.wav",
                            "minutes": _minutes(" ".join(lines)), "lines": lines})
            elif need.startswith("footage"):
                m = re.match(r"footage: beat (\d+) expects (.+)", need)
                i = int(m.group(1)) - 1 if m else 0
                seg = segs[i] if i < len(segs) else {}
                out.append({**base, "kind": "screen", "beat": i, "save_as": m.group(2) if m else "",
                            "minutes": max(0.2, _minutes(seg.get("narration", ""))),
                            "show": seg.get("on_screen_text") or seg.get("heading", ""),
                            "narration": seg.get("narration", "")})
            elif need.startswith("screen recording"):
                what = element_text(script.get("original_element")) or need.split(":", 1)[1].strip()
                i = _best_beat(segs, what)
                seg = segs[i] if i < len(segs) else {}
                out.append({**base, "kind": "screen", "beat": i, "planned": True,
                            "save_as": f"footage/{t['brand']}/post-{t['post_id']}-beat{i + 1}.mp4",
                            "minutes": max(0.5, _minutes(seg.get("narration", ""))), "show": what,
                            "narration": seg.get("narration", "")})
    return out


def sessions(items: list[dict], minutes: float = 45, takes: float = 2.5) -> list[dict]:
    """Group by (brand, setup), soonest first, and split so each session is about `minutes` long."""
    groups = defaultdict(list)
    for t in items:
        groups[(t["brand"], t["kind"])].append(t)
    out = []
    for (brand, kind), group in groups.items():
        group.sort(key=lambda t: (t["publish_at"] == "", t["publish_at"], t["post_id"]))
        cur, used = [], 0.0
        for t in group:
            cost = t["minutes"] * takes
            if cur and used + cost > minutes:
                out.append({"brand": brand, "kind": kind, "tasks": cur, "minutes": round(used)})
                cur, used = [], 0.0
            cur.append(t)
            used += cost
        if cur:
            out.append({"brand": brand, "kind": kind, "tasks": cur, "minutes": round(used)})
    out.sort(key=lambda s: (s["tasks"][0]["publish_at"] == "", s["tasks"][0]["publish_at"], s["brand"], s["kind"]))
    for n, s in enumerate(out, 1):
        s["n"] = n
        s["due"] = s["tasks"][0]["publish_at"][:10]
    return out


def _when(t: dict) -> str:
    return t["publish_at"][:16].replace("T", " ") + " UTC" if t["publish_at"] else "not scheduled"


def shot_list(s: dict) -> str:
    head = "Voice takes" if s["kind"] == "voice" else "Screen recordings"
    out = [f"# Session {s['n']}: {s['brand']} · {head}", "",
           f"About {s['minutes']} minutes with retakes. First one publishes {_when(s['tasks'][0])}.", ""]
    if s["kind"] == "voice":
        out += ["Setup: quiet room, same mic and distance every take, 44.1 or 48 kHz WAV. Read from "
                "teleprompter.html. Pause a beat between lines so the factory can split them.", ""]
    else:
        out += ["Setup: 1080p or larger, notifications off, a test account or blurred personal details "
                "(never show real account numbers, names or a real scam victim's info). Record a few seconds "
                "longer than listed; the render trims to the narration.", ""]
    out += ["| # | Post | Publishes | Beat | Save as | About | What to show |", "|---|---|---|---|---|---|---|"]
    for k, t in enumerate(s["tasks"], 1):
        beat = "all" if t["kind"] == "voice" else str(t["beat"] + 1)
        show = "Read the whole script" if t["kind"] == "voice" else t["show"].replace("|", "/")[:160]
        out.append(f"| {k} | #{t['post_id']} {t['title'][:50].replace('|', '/')} | {_when(t)} | {beat} | "
                   f"`{t['save_as']}` | {t['minutes']} min | {show} |")
    out += ["", "After recording:"]
    if s["kind"] == "voice":
        out.append("- Put each take at its `Save as` path (relative to the factory home); the next render uses it.")
    else:
        out.append("- Save each file at its `Save as` path, then run `factory batch-record attach {this folder}`.")
    out.append("- Re-render the posts (`factory render <id>`) and review them before they're scheduled.")
    return "\n".join(out) + "\n"


def teleprompter_text(s: dict) -> str:
    out = []
    for t in s["tasks"]:
        out.append(f"=== #{t['post_id']} {t['title']} → {t['save_as']} ===")
        out += (t.get("lines") or [t.get("narration", "")]) + [""]
    return "\n".join(out)


PROMPTER_CSS = """
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#000;color:#f4f1ea;font:600 var(--fs,44px)/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
#bar{position:fixed;top:0;left:0;right:0;display:flex;gap:8px;flex-wrap:wrap;padding:8px 16px;background:#111d;font:14px system-ui;z-index:2}
#bar button{font:inherit;padding:6px 10px;border-radius:6px;border:1px solid #444;background:#222;color:#eee}
main{max-width:1100px;margin:0 auto;padding:40vh 16px 80vh}.take{margin-bottom:2.5em}
.take h2{font-size:.4em;color:#9aa;font-weight:500;margin:0 0 .6em;border-top:1px solid #333;padding-top:.8em}
p{margin:0 0 .8em}body.mirror main{transform:scaleX(-1)}#guide{position:fixed;top:38vh;left:0;right:0;border-top:2px solid #e5484d55;pointer-events:none}
"""
PROMPTER_JS = """
let speed=0,fs=44,t=null;const set=()=>document.body.style.setProperty('--fs',fs+'px');
function go(d){speed=Math.max(0,speed+d);document.getElementById('sp').textContent=speed;clearInterval(t);if(speed)t=setInterval(()=>window.scrollBy(0,speed/2),30)}
document.addEventListener('keydown',e=>{if(e.key===' '){e.preventDefault();go(speed?-speed:2)}if(e.key==='ArrowUp')go(1);if(e.key==='ArrowDown')go(-1)});
"""


def teleprompter_html(s: dict) -> str:
    e = html.escape
    takes = []
    for t in s["tasks"]:
        lines = t.get("lines") or ([t["narration"]] if t.get("narration") else [])
        cue = "" if t["kind"] == "voice" else f"<p style='color:#8cf;font-size:.6em'>On screen: {e(t['show'])}</p>"
        takes.append(f"<section class='take'><h2>#{t['post_id']} {e(t['title'])} · save as {e(t['save_as'])}</h2>{cue}"
                     + "".join(f"<p>{e(ln)}</p>" for ln in lines) + "</section>")
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Teleprompter {s['n']}</title><style>{PROMPTER_CSS}</style></head><body><div id='bar'>"
            "<button onclick='go(1)'>Faster</button><button onclick='go(-1)'>Slower</button>"
            "<button onclick='fs+=4;set()'>A+</button><button onclick='fs=Math.max(20,fs-4);set()'>A-</button>"
            "<button onclick=\"document.body.classList.toggle('mirror')\">Mirror</button>"
            "<span style='align-self:center'>speed <b id='sp'>0</b> · space starts and stops, arrows change speed</span></div>"
            f"<div id='guide'></div><main>{''.join(takes)}</main><script>{PROMPTER_JS}</script></body></html>")


def write(factory, plan: list[dict], when: date | None = None) -> Path:
    root = factory.settings.output_dir / "batch-record" / (when or date.today()).isoformat()
    root.mkdir(parents=True, exist_ok=True)
    index = ["# Recording sessions", "", "| Session | Brand | Setup | Takes | About | First publishes |",
             "|---|---|---|---|---|---|"]
    for s in plan:
        d = root / f"session-{s['n']:02d}-{s['brand']}-{s['kind']}"
        d.mkdir(exist_ok=True)
        (d / "SHOT_LIST.md").write_text(shot_list(s))
        (d / "teleprompter.html").write_text(teleprompter_html(s))
        (d / "teleprompter.txt").write_text(teleprompter_text(s))
        (d / "session.json").write_text(json.dumps(s, indent=2))
        index.append(f"| [{s['n']}]({d.name}/SHOT_LIST.md) | {s['brand']} | {s['kind']} | {len(s['tasks'])} | "
                     f"{s['minutes']} min | {s['due'] or 'not scheduled'} |")
    (root / "README.md").write_text("\n".join(index) + "\n")
    return root


def attach(factory, session_dir: Path) -> list[str]:
    """Set Segment.footage for every screen task whose file now exists."""
    s = json.loads((Path(session_dir) / "session.json").read_text())
    home, done = factory.settings.home, []
    for t in s["tasks"]:
        if t["kind"] != "screen" or not (home / t["save_as"]).is_file():
            continue
        post = factory.db.get("posts", t["post_id"])
        if not post or not isinstance(post.get("script"), dict):
            continue
        script = post["script"]
        segs = script.get("segments") or []
        if t["beat"] < len(segs):
            segs[t["beat"]]["footage"] = t["save_as"]
            factory.db.update("posts", t["post_id"], {"script": script})
            done.append(f"#{t['post_id']} beat {t['beat'] + 1} ← {t['save_as']}")
    return done


def register(sub, factory_fn) -> None:
    s = sub.add_parser("batch-record", help="group everything waiting on your voice or screen into recording "
                                            "sessions: shot list + teleprompter per session")
    s.add_argument("action", nargs="?", default="plan", choices=["plan", "attach"])
    s.add_argument("session", nargs="?", type=Path, help="attach: the session folder")
    s.add_argument("--brand", default="")
    s.add_argument("--days", type=int, default=None, help="only posts publishing in the next N days")
    s.add_argument("--minutes", type=float, default=45, help="recording time per session, retakes included")
    s.add_argument("--takes", type=float, default=2.5, help="recording minutes per finished minute")

    def cmd(a):
        f = factory_fn(a)
        if a.action == "attach":
            if not a.session:
                raise SystemExit("usage: factory batch-record attach <session folder>")
            done = attach(f, a.session)
            print("\n".join(done) if done else "No recorded files found yet at the session's Save as paths.")
            if done:
                print("Re-render those posts with `factory render <id>`.")
            return
        plan = sessions(tasks(f, a.brand, a.days), a.minutes, a.takes)
        if not plan:
            print("Nothing waiting on you to record.")
            return
        root = write(f, plan)
        for p in plan:
            print(f"Session {p['n']}: {p['brand']} {p['kind']} · {len(p['tasks'])} take(s) · ~{p['minutes']} min · "
                  f"first publishes {p['due'] or 'not scheduled'}")
        print(f"\nShot lists and teleprompters: {root}")
    s.set_defaults(func=cmd)
