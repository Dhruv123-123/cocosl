"""Optional motion cards rendered with HyperFrames (HTML to MP4; open source, Apache-2.0), for number beats.

    factory motion 42                    # plan: which beats would get a motion card, and what it shows
    factory motion 42 --write            # write one HyperFrames project per beat (render it yourself)
    factory motion 42 --apply            # write and render them, set Segment.motion; then `factory rerender 42`

Off unless you opt in: set FACTORY_MOTION=hyperframes and have Node.js 22+ and FFmpeg. The CLI runs as
`npx --yes hyperframes@<HYPERFRAMES_VERSION> render` (default 0.9.19, the version scouting checked), which
needs headless Chrome; point HYPERFRAMES_BROWSER_PATH at one if it can't find its own.
Rules:
* A beat qualifies when it states a number ($, %, a year, a count) and has no chart, footage or B-roll of its
  own. At most 1 beat in 4, never two in a row, never the hook beat.
* The card is our own graphic (the beat's on-screen text, brand colours, the Inter font that ships with
  HyperFrames): it counts as made by us, not as stock. A chart beat already shows exact numbers and is left alone.
* Telemetry and update checks are switched off for every call (HYPERFRAMES_NO_TELEMETRY=1). The factory
  never runs `hyperframes publish` or signs in to anything; renders stay on this machine.
Projects are written to footage/<brand>/motion/post-<id>-beat<n>/ (index.html) and rendered to card.mp4 there.
"""
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
from pathlib import Path

MAX_SHARE = 1 / 4
NUMBER_RE = re.compile(r"(\$\s?\d[\d,]*(?:\.\d+)?\s?[kKmM]?|\d[\d,]*(?:\.\d+)?\s?%|\b(?:19|20)\d{2}\b|\b\d[\d,]{1,}\b)")
SECONDS = 4.0
SAFE_ENV = {"HYPERFRAMES_NO_TELEMETRY": "1", "HYPERFRAMES_NO_UPDATE_CHECK": "1", "HYPERFRAMES_NO_AUTO_INSTALL": "1",
            "HYPERFRAMES_NO_OPTIONAL_INSTALL": "1", "HYPERFRAMES_NO_PREVIEW_DISCOVERY": "1", "DO_NOT_TRACK": "1"}


class MotionError(RuntimeError):
    pass


def enabled() -> bool:
    return os.environ.get("FACTORY_MOTION", "").strip().lower() == "hyperframes"


def version() -> str:
    v = os.environ.get("HYPERFRAMES_VERSION", "0.9.19").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        raise MotionError(f"HYPERFRAMES_VERSION must be an exact version like 0.9.19, not '{v}'")
    return v


def the_number(seg: dict) -> str:
    for text in (seg.get("on_screen_text") or "", seg.get("narration") or "", seg.get("heading") or ""):
        m = NUMBER_RE.search(text)
        if m:
            return m.group(0).strip()
    return ""


def pick_beats(segments: list[dict]) -> list[int]:
    limit = int(len(segments) * MAX_SHARE)
    used = [i for i, s in enumerate(segments) if (s.get("motion") or "").strip()]
    chosen: list[int] = []
    for i, s in enumerate(segments):
        if len(used) + len(chosen) >= limit:
            break
        if i == 0 or s.get("chart") or (s.get("footage") or "").strip() or (s.get("broll") or "").strip() \
                or (s.get("motion") or "").strip():
            continue
        if any(abs(i - j) <= 1 for j in chosen + used):
            continue
        if the_number(s):
            chosen.append(i)
    return chosen


def plan(post: dict) -> list[dict]:
    segs = (post.get("script") or {}).get("segments") or []
    return [{"beat": i, "number": the_number(segs[i]),
             "label": (segs[i].get("on_screen_text") or segs[i].get("heading") or "").strip()} for i in pick_beats(segs)]


def composition(number: str, label: str, palette: list[str], portrait: bool = True, seconds: float = SECONDS) -> str:
    """One standalone HyperFrames composition: the number counts in, the label rises under it."""
    w, h = (1080, 1920) if portrait else (1920, 1080)
    bg, fg, accent = (palette + ["#0f172a", "#f8fafc", "#22d3ee"])[:3]
    label = label.replace(number, "").strip(" :-–—") or label
    num_px, lab_px = (220, 64) if portrait else (240, 60)
    e = html.escape
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8">
<style>
  html, body {{ margin: 0; background: {e(bg)}; }}
  #card-bg {{ position: absolute; inset: 0; background: {e(bg)}; }}
  #card-wrap {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
               justify-content: center; gap: 48px; padding: 0 10%; font-family: Inter, sans-serif; text-align: center; }}
  #card-num {{ font-size: {num_px}px; font-weight: 900; color: {e(accent)}; line-height: 1; }}
  #card-label {{ font-size: {lab_px}px; font-weight: 700; color: {e(fg)}; line-height: 1.2; max-width: 100%; }}
  #card-bar {{ width: 30%; height: 12px; border-radius: 6px; background: {e(accent)}; transform-origin: left center; }}
</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{seconds:g}" data-width="{w}" data-height="{h}">
    <div id="card-bg"></div>
    <div id="card-wrap" class="clip" data-start="0" data-duration="{seconds:g}" data-track-index="1">
      <div id="card-num">{e(number)}</div>
      <div id="card-bar"></div>
      <div id="card-label">{e(label)}</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#card-num", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.6)" }}, 0.15);
    tl.fromTo("#card-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.out" }}, 0.55);
    tl.fromTo("#card-label", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.75);
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""


def command(project: Path) -> list[str]:
    return ["npx", "--yes", f"hyperframes@{version()}", "render", "-o", "card.mp4"]


def _check_tools() -> None:
    if not shutil.which("npx") or not shutil.which("node"):
        raise MotionError("HyperFrames needs Node.js 22+ (npx on PATH)")
    out = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
    m = re.match(r"v(\d+)", out)
    if not m or int(m.group(1)) < 22:
        raise MotionError(f"HyperFrames needs Node.js 22+, found {out or 'none'}")
    if not shutil.which("ffmpeg"):
        raise MotionError("HyperFrames needs FFmpeg on PATH")


def render_project(project: Path, run=subprocess.run, timeout: int = 600) -> Path:
    env = {**os.environ, **SAFE_ENV}
    res = run(command(project), cwd=str(project), env=env, capture_output=True, text=True, timeout=timeout)
    out = project / "card.mp4"
    if res.returncode != 0 or not out.is_file():
        tail = ((res.stderr or "") + (res.stdout or ""))[-600:]
        raise MotionError(f"hyperframes render failed in {project} (exit {res.returncode}): {tail}")
    return out


def write_projects(factory, post: dict) -> list[dict]:
    brand = factory.brand(post["brand"])
    portrait = post["format"] != "long"
    home = Path(factory.settings.home)
    made = []
    for item in plan(post):
        rel = Path("footage") / post["brand"] / "motion" / f"post-{post['id']}-beat{item['beat'] + 1}"
        d = home / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(composition(item["number"], item["label"], brand.visual.palette, portrait))
        (d / "RENDER.txt").write_text("Render this card (Node.js 22+, FFmpeg):\n\n  cd " + str(d) + "\n  "
                                      + " ".join(command(d)) + "\n\nTelemetry off: HYPERFRAMES_NO_TELEMETRY=1\n")
        made.append({**item, "dir": rel})
    return made


def apply(factory, post_id: int, run=subprocess.run, check_tools: bool = True) -> dict:
    if not enabled():
        raise MotionError("Motion cards are off: set FACTORY_MOTION=hyperframes in .env to use HyperFrames")
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    if post["status"] in ("scheduled", "published"):
        raise PermissionError(f"Post #{post_id} is {post['status']}: unschedule it first")
    if post["format"] not in ("short", "mid", "long"):
        raise ValueError("Motion cards are for videos")
    if check_tools:
        _check_tools()
    home = Path(factory.settings.home)
    script = dict(post["script"])
    segs = [dict(s) for s in script.get("segments") or []]
    added, errors = [], []
    for item in write_projects(factory, post):
        try:
            clip = render_project(home / item["dir"], run=run)
        except MotionError as e:
            errors.append(str(e))
            continue
        segs[item["beat"]]["motion"] = str(clip.relative_to(home))
        added.append(item["beat"] + 1)
    if added:
        script["segments"] = segs
        meta = dict(post.get("meta") or {})
        meta["motion_cards"] = [{"beat": b, "tool": f"hyperframes@{version()}"} for b in added]
        factory.db.update("posts", post_id, {"script": script, "meta": meta})
        factory.db.log("post.motion", "post", post_id, {"beats": added, "tool": f"hyperframes@{version()}"})
    return {"added": added, "errors": errors}


def register(sub, factory_fn) -> None:
    s = sub.add_parser("motion", help="optional HyperFrames motion cards for number beats (max 1 in 4; "
                                      "FACTORY_MOTION=hyperframes, Node 22+; plan unless --write/--apply)")
    s.add_argument("post_id", type=int)
    s.add_argument("--write", action="store_true", help="write the HyperFrames projects only (render them yourself)")
    s.add_argument("--apply", action="store_true", help="write, render with npx hyperframes, and set the beats")

    def cmd(a):
        f = factory_fn(a)
        post = f.db.get("posts", a.post_id)
        if not post:
            raise SystemExit(f"No post #{a.post_id}")
        if a.apply:
            try:
                res = apply(f, a.post_id)
            except MotionError as e:
                raise SystemExit(str(e))
            for err in res["errors"]:
                print(err)
            if res["added"]:
                print(f"Motion cards on beat(s) {', '.join(map(str, res['added']))}. Re-render: factory rerender {a.post_id}")
            elif not res["errors"]:
                print("No beat qualifies (a number, no chart/footage/B-roll, max 1 in 4). Nothing changed.")
            return
        if a.write:
            made = write_projects(f, post)
            for m in made:
                print(f"beat {m['beat'] + 1}: {m['dir']}/index.html")
            print(f"{len(made)} project(s). Render each with the command in its RENDER.txt, then set the beat's "
                  "motion clip with --apply (or render here with FACTORY_MOTION=hyperframes).")
            return
        items = plan(post)
        for it in items:
            print(f"beat {it['beat'] + 1}: {it['number']} · {it['label'][:70]}")
        print(f"{len(items)} beat(s) could get a motion card (max 1 in 4)."
              + ("" if enabled() else " Set FACTORY_MOTION=hyperframes to render them here."))
    s.set_defaults(func=cmd)
