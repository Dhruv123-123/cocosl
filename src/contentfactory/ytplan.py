"""`factory youtube-plan`: the by-hand YouTube Studio work for a content pack, written beside it.

The Data API can't set end screens or a Short's related video, so each pack gets a YOUTUBE_PLAN.md:
* playlists: one per series (brand `youtube.playlists`, or one per pillar), long videos in pack order,
  plus a "Start here" playlist;
* end screen: the brand's layout (import it from the previous video in Studio), with the left tile
  set to the next video in the same playlist;
* every Short: the related video to set, i.e. the long video it leads into. Taken from the Short's
  `related_video` if the pack has one, otherwise the brand's long video with the same pillar and the
  most words in common. `--write` stores the pick in the pack so review and the Today page show it.

    factory youtube-plan launch/money-made-simple/content.json --brand money-made-simple [--write]
    factory youtube-plan --brand money-made-simple    # every launch/<brand>/*.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

STOP = set("a an and are as at be but by for from how i if in into is it its of on or that the this to was what "
           "when why with you your".split())


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", (text or "").lower()) if w not in STOP and len(w) > 2}


def _script(item: dict) -> dict:
    return item.get("script") or item


def _text(item: dict) -> str:
    sc = _script(item)
    return " ".join([sc.get("title", ""), sc.get("hook", ""), item.get("idea_angle", "")] +
                    [s.get("on_screen_text", "") for s in sc.get("segments") or []])


def playlists_for(brand) -> list[dict]:
    if brand.youtube.playlists:
        return [p.model_dump() for p in brand.youtube.playlists]
    return [{"title": p[:1].upper() + p[1:], "description": "", "pillars": [p], "keywords": []} for p in brand.pillars]


def playlist_of(item: dict, lists: list[dict]) -> str:
    sc = _script(item)
    if sc.get("playlist"):
        return sc["playlist"]
    title = (sc.get("title") or "").lower()
    for pl in lists:
        if item.get("pillar") in pl.get("pillars", []) or any(k.lower() in title for k in pl.get("keywords", [])):
            return pl["title"]
    return lists[0]["title"] if lists else ""


def related_video(item: dict, longs: list[dict]) -> str:
    sc = _script(item)
    if sc.get("related_video"):
        return sc["related_video"]
    if not longs:
        return ""
    mine = _words(_text(item))

    def score(lv):
        return (lv.get("pillar") == item.get("pillar"), len(mine & _words(_text(lv))))
    return _script(max(longs, key=score)).get("title", "")


def plan(brand, items: list[dict], longs_elsewhere: list[dict] | None = None) -> dict:
    lists = playlists_for(brand)
    longs = [i for i in items if i.get("format") == "long"]
    # a related video must already be on the channel: prefer this pack's long videos, and only reach for
    # another pack's when this one has none
    pool = longs or list(longs_elsewhere or [])
    by_list: dict[str, list[str]] = {pl["title"]: [] for pl in lists}
    for lv in longs:
        by_list.setdefault(playlist_of(lv, lists), []).append(_script(lv).get("title", ""))
    end_screens = []
    for lv in longs:
        pl = playlist_of(lv, lists)
        titles = by_list.get(pl, [])
        t = _script(lv).get("title", "")
        nxt = titles[titles.index(t) + 1] if t in titles and titles.index(t) + 1 < len(titles) else ""
        end_screens.append({"title": t, "playlist": pl, "left_tile": nxt or f"playlist: {pl}"})
    shorts = [{"title": _script(s).get("title", ""), "related": related_video(s, pool)}
              for s in items if s.get("format") in ("short", "mid")]
    return {"playlists": lists, "order": by_list, "end_screens": end_screens, "shorts": shorts,
            "start_here": brand.youtube.start_here, "layout": brand.youtube.end_screen}


def to_markdown(brand, p: dict, source: str) -> str:
    out = [f"# YouTube plan: {brand.name}", "",
           f"Made by `factory youtube-plan` from {source}. These are set by hand in YouTube Studio: the API has no",
           "end-screen or related-video endpoint. About 5 minutes per long video.", "",
           "## End screen layout (make it once, then \"Import from video\" on each upload)", ""]
    out += [f"- {x}" for x in p["layout"]]
    out += ["", "Every long video ends on a 20-second slate with space for these elements, so they never cover the",
            "explanation.", "", "## Playlists", ""]
    for pl in p["playlists"]:
        vids = p["order"].get(pl["title"], [])
        out.append(f"### {pl['title']}")
        if pl.get("description"):
            out.append(pl["description"])
        out += [f"{i}. {v}" for i, v in enumerate(vids, 1)] or ["(no long videos in this pack yet)"]
        out.append("")
    out += [f"### {p['start_here']}", "The 3-5 best long videos once you have view data; feature it on the channel home page.", "",
            "## Each long video", "", "| Video | Playlist | End screen left tile |", "|---|---|---|"]
    out += [f"| {e['title']} | {e['playlist']} | {e['left_tile']} |" for e in p["end_screens"]]
    out += ["", "## Each Short: related video (Studio > Short > Details > Related video)", "",
            "Links in Shorts descriptions aren't clickable, so this is the Short's one link to a long video.",
            "If the long video isn't up yet when the Short goes out, come back and set it once it is.", "",
            "| Short | Related video |", "|---|---|"]
    out += [f"| {s['title']} | {s['related'] or '(no long video yet: set it when one is up)'} |" for s in p["shorts"]]
    return "\n".join(out) + "\n"


def _load(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    return data if isinstance(data, list) else data.get("posts", [])


def run(home: Path, brand, files: list[Path], write: bool = False) -> list[Path]:
    """Write YOUTUBE_PLAN.md for each pack file's folder; with write=True also store related_video."""
    every = {f: _load(f) for f in files}
    all_longs = [i for items in every.values() for i in items if i.get("format") == "long"]
    made = []
    for f, items in every.items():
        p = plan(brand, items, all_longs)
        name = "YOUTUBE_PLAN.md" if len(files) == 1 or f.name == "content.json" else f"YOUTUBE_PLAN-{f.stem}.md"
        out = f.parent / name
        try:
            source = f.relative_to(home).as_posix()
        except ValueError:
            source = f.name
        out.write_text(to_markdown(brand, p, source))
        made.append(out)
        if write:
            rel = {s["title"]: s["related"] for s in p["shorts"]}
            changed = False
            for it in items:
                sc = _script(it)
                if it.get("format") in ("short", "mid") and not sc.get("related_video") and rel.get(sc.get("title")):
                    sc["related_video"] = rel[sc["title"]]
                    changed = True
            if changed:
                text = f.read_text()
                lines = text.splitlines()
                indent = (len(lines[1]) - len(lines[1].lstrip(" "))) if len(lines) > 1 else 2
                raw = json.loads(text)
                if isinstance(raw, dict):
                    raw["posts"] = items
                else:
                    raw = items
                f.write_text(json.dumps(raw, indent=indent or 2, ensure_ascii=False) + ("\n" if text.endswith("\n") else ""))
    return made


def register(sub, factory_fn) -> None:
    s = sub.add_parser("youtube-plan", help="playlists, end screens and Shorts related videos for a pack "
                                            "(set by hand in Studio)")
    s.add_argument("files", nargs="*", type=Path)
    s.add_argument("--brand", required=True)
    s.add_argument("--write", action="store_true", help="store each Short's related_video in the pack")

    def cmd(a):
        f = factory_fn(a)
        home = f.settings.home
        files = a.files or sorted((home / "launch" / a.brand).glob("*.json"))
        if not files:
            raise SystemExit(f"No pack files for {a.brand} (looked in launch/{a.brand}/)")
        for p in run(home, f.brand(a.brand), [Path(x).resolve() if not Path(x).is_absolute() else Path(x)
                                              for x in files], a.write):
            print(p)
    s.set_defaults(func=cmd)


def studio_todos(factory, days: int = 7) -> list[dict]:
    """YouTube uploads in the next `days`, with the Studio step each needs (end screen, playlist, related video)."""
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    rows = factory.db.query(
        """SELECT pub.id, pub.scheduled_at, pub.status, s.id post_id, s.brand, s.format, s.title, s.script,
                  COALESCE(i.pillar, '') pillar FROM publications pub JOIN posts s ON s.id = pub.post_id
           LEFT JOIN ideas i ON i.id = s.idea_id
           WHERE pub.platform = 'youtube' AND pub.status IN ('queued', 'published', 'dry_run')
             AND pub.scheduled_at >= ? AND pub.scheduled_at < ? ORDER BY pub.scheduled_at""",
        [(now - timedelta(days=2)).isoformat(), (now + timedelta(days=days)).isoformat()])
    brands = factory.brands()
    out = []
    for r in rows:
        sc = r["script"] if isinstance(r["script"], dict) else {}
        b = brands.get(r["brand"])
        if r["format"] == "long":
            pl = sc.get("playlist") or (playlist_of({"pillar": r["pillar"], "script": sc}, playlists_for(b)) if b else "")
            todo = f"Import the end screen (left tile: next in the series) and add to playlist “{pl}”"
        elif r["format"] in ("short", "mid"):
            rel = sc.get("related_video")
            todo = f"Set related video: “{rel}”" if rel else "Set related video: the long video this Short leads into"
        else:
            continue
        out.append({**{k: r[k] for k in ("id", "scheduled_at", "status", "post_id", "brand", "format", "title")},
                    "todo": todo})
    return out
