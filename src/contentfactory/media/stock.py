"""Optional stock B-roll from Pexels or Pixabay (free tiers), for at most 1 beat in 3.

    factory broll 42                     # plan: which beats would get a clip, and the search for each
    factory broll 42 --apply             # download the clips, set Segment.broll, add credits; then re-render
    factory broll 42 --apply --provider pixabay

Keys (free): PEXELS_API_KEY (pexels.com/api, 200 requests an hour, 20,000 a month) or PIXABAY_API_KEY
(pixabay.com/api/docs). Without a key nothing happens. Rules, from scouting's licence check
(research/scouting/free-tools-round4.md on PR #2):
* At most 1 beat in 3, never two in a row, never a beat that already has a chart or your own footage. Stock
  is never counted as an original element (the originality audit ignores it).
* No clip whose tags or page mention a logo, bank, card network or brand: recognisable trademarks are not
  allowed commercially (Pixabay) and look like an endorsement.
* Pexels asks for "a prominent link to Pexels" and photographer credit where possible: every clip gets a
  sidecar .json, the post gets output/<brand>/post-<id>/credits.json, and the YouTube description gets a
  credit line ("B-roll: Pexels (pexels.com): <names>").
* Pixabay: no standalone resale of a clip. We only ever use clips inside our own edits.
Clips are saved under footage/<brand>/stock/ (relative to the factory home) and reused if already there.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import httpx

MAX_SHARE = 1 / 3
BAD_TAGS = re.compile(r"\b(logo|logos|brand|branded|trademark|visa|mastercard|amex|american express|paypal|venmo|"
                      r"chase|wells fargo|bank of america|citi|apple pay|google pay|cash app|zelle|amazon|"
                      r"bank|banking|credit card|debit card|atm)\b", re.I)
STYLE_WORDS = set("flat vector illustration clean warm style minimal no text logos real people simple colorful "
                  "background soft palette brand colors a an the of and with in on for to showing".split())
PROVIDERS = ("pexels", "pixabay")


class StockError(RuntimeError):
    pass


def key_for(provider: str) -> str:
    return os.environ.get({"pexels": "PEXELS_API_KEY", "pixabay": "PIXABAY_API_KEY"}[provider], "").strip()


def default_provider() -> str | None:
    want = os.environ.get("FACTORY_BROLL", "").strip().lower()
    if want in PROVIDERS and key_for(want):
        return want
    return next((p for p in PROVIDERS if key_for(p)), None)


def query_for(seg: dict) -> str:
    """A short stock search from the beat: heading words first, then the visual prompt's nouns."""
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", f"{seg.get('heading', '')} {seg.get('visual_prompt', '')}")
    out = []
    for w in words:
        lw = w.lower()
        if lw in STYLE_WORDS or len(lw) < 3 or lw in out:
            continue
        out.append(lw)
        if len(out) == 4:
            break
    return " ".join(out)


def pick_beats(segments: list[dict]) -> list[int]:
    """Beats that may get stock: no chart, footage or B-roll yet; at most 1 in 3; never adjacent; not the hook beat."""
    limit = int(len(segments) * MAX_SHARE)
    used = [i for i, s in enumerate(segments) if s.get("broll")]
    chosen: list[int] = []
    for i, s in enumerate(segments):
        if len(used) + len(chosen) >= limit:
            break
        if i == 0 or s.get("chart") or (s.get("footage") or "").strip() or s.get("broll"):
            continue
        if any(abs(i - j) <= 1 for j in chosen + used):
            continue
        if query_for(s):
            chosen.append(i)
    return chosen


def search(provider: str, query: str, portrait: bool = True, client: httpx.Client | None = None) -> list[dict]:
    """Candidates: {id, url (mp4), width, height, duration, page, author, author_url, tags, provider}."""
    key = key_for(provider)
    if not key:
        raise StockError(f"{provider}: set {'PEXELS_API_KEY' if provider == 'pexels' else 'PIXABAY_API_KEY'} (free) first")
    c = client or httpx.Client(timeout=20)
    out = []
    if provider == "pexels":
        r = c.get("https://api.pexels.com/v1/videos/search", headers={"Authorization": key},
                  params={"query": query, "per_page": 15, "orientation": "portrait" if portrait else "landscape"})
        r.raise_for_status()
        for v in r.json().get("videos", []):
            files = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and (f.get("width") or 0) >= 720]
            if not files:
                continue
            f = min(files, key=lambda f: f.get("width") or 0)
            user = v.get("user") or {}
            out.append({"id": str(v["id"]), "url": f["link"], "width": f.get("width"), "height": f.get("height"),
                        "duration": v.get("duration"), "page": v.get("url", ""), "author": user.get("name", ""),
                        "author_url": user.get("url", ""), "tags": " ".join(v.get("tags") or []) + " " + v.get("url", ""),
                        "provider": "pexels", "license": "Pexels License (pexels.com/license)"})
    else:
        r = c.get("https://pixabay.com/api/videos/", params={"key": key, "q": query, "per_page": 15, "safesearch": "true"})
        r.raise_for_status()
        for v in r.json().get("hits", []):
            vids = v.get("videos") or {}
            f = next((vids[k] for k in ("medium", "small", "large") if vids.get(k, {}).get("url")
                      and (vids[k].get("width") or 0) >= 720), None)
            if not f:
                continue
            out.append({"id": str(v["id"]), "url": f["url"], "width": f.get("width"), "height": f.get("height"),
                        "duration": v.get("duration"), "page": v.get("pageURL", ""), "author": v.get("user", ""),
                        "author_url": f"https://pixabay.com/users/{v.get('user', '')}-{v.get('user_id', '')}/",
                        "tags": v.get("tags", "") + " " + v.get("pageURL", ""), "provider": "pixabay",
                        "license": "Pixabay Content License (pixabay.com/service/license-summary)"})
    return [c for c in out if not BAD_TAGS.search(c["tags"])]


def _download(url: str, dest: Path, client: httpx.Client | None = None) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size:
        return dest
    c = client or httpx.Client(timeout=60, follow_redirects=True)
    with c.stream("GET", url) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(".part")
        with tmp.open("wb") as fh:
            for chunk in r.iter_bytes():
                fh.write(chunk)
    tmp.replace(dest)
    return dest


def credit_line(credits: list[dict]) -> str:
    by = {}
    for c in credits:
        by.setdefault(c["provider"], []).append(c["author"])
    parts = []
    if "pexels" in by:
        parts.append("Pexels (pexels.com): " + ", ".join(dict.fromkeys(a for a in by["pexels"] if a)))
    if "pixabay" in by:
        parts.append("Pixabay (pixabay.com): " + ", ".join(dict.fromkeys(a for a in by["pixabay"] if a)))
    return "B-roll: " + "; ".join(parts) if parts else ""


def plan(post: dict) -> list[dict]:
    segs = (post.get("script") or {}).get("segments") or []
    return [{"beat": i, "query": query_for(segs[i])} for i in pick_beats(segs)]


def apply(factory, post_id: int, provider: str | None = None, client: httpx.Client | None = None) -> dict:
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    if post["status"] in ("scheduled", "published"):
        raise PermissionError(f"Post #{post_id} is {post['status']}: unschedule it first")
    if post["format"] not in ("short", "mid", "long"):
        raise ValueError("B-roll is for videos")
    provider = provider or default_provider()
    if not provider:
        raise StockError("No stock key: set PEXELS_API_KEY or PIXABAY_API_KEY (both free) in .env")
    script = dict(post["script"])
    segs = [dict(s) for s in script.get("segments") or []]
    portrait = post["format"] != "long"
    home = Path(factory.settings.home)
    credits, added = [], []
    for item in plan({"script": {"segments": segs}}):
        found = search(provider, item["query"], portrait, client)
        if not found:
            continue
        c = found[0]
        rel = Path("footage") / post["brand"] / "stock" / f"post-{post_id}-beat{item['beat'] + 1}-{c['provider']}-{c['id']}.mp4"
        _download(c["url"], home / rel, client)
        meta = {k: c[k] for k in ("provider", "id", "page", "author", "author_url", "license")} | {"query": item["query"]}
        (home / rel).with_suffix(".json").write_text(json.dumps(meta, indent=2))
        segs[item["beat"]]["broll"] = str(rel)
        credits.append(meta | {"beat": item["beat"] + 1, "file": str(rel)})
        added.append(item["beat"] + 1)
    if not credits:
        return {"added": [], "credits": []}
    line = credit_line(credits)
    desc = script.get("description") or ""
    desc = re.sub(r"\n*B-roll: .*$", "", desc, flags=re.M).rstrip()
    script["description"] = f"{desc}\n\n{line}".strip()
    script["segments"] = segs
    meta = dict(post.get("meta") or {})
    meta["stock_credits"] = credits
    factory.db.update("posts", post_id, {"script": script, "meta": meta})
    out = factory.settings.output_dir / post["brand"] / f"post-{post_id}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "credits.json").write_text(json.dumps(credits, indent=2))
    factory.db.log("post.broll", "post", post_id, {"beats": added, "provider": provider})
    return {"added": added, "credits": credits, "credit_line": line}


def register(sub, factory_fn) -> None:
    s = sub.add_parser("broll", help="optional Pexels / Pixabay B-roll for up to 1 beat in 3 (free keys; plan unless --apply)")
    s.add_argument("post_id", type=int)
    s.add_argument("--apply", action="store_true")
    s.add_argument("--provider", choices=PROVIDERS, default=None)

    def cmd(a):
        f = factory_fn(a)
        post = f.db.get("posts", a.post_id)
        if not post:
            raise SystemExit(f"No post #{a.post_id}")
        if not a.apply:
            items = plan(post)
            for it in items:
                print(f"beat {it['beat'] + 1}: search “{it['query']}”")
            print(f"{len(items)} beat(s) could get stock B-roll (max 1 in 3). "
                  + ("Run with --apply." if default_provider() or a.provider else "Set PEXELS_API_KEY or PIXABAY_API_KEY first."))
            return
        res = apply(f, a.post_id, a.provider)
        if not res["added"]:
            print("No suitable clip found (logo-free, 720p+). Nothing changed.")
            return
        print(f"B-roll on beat(s) {', '.join(map(str, res['added']))}. {res['credit_line']}")
        print(f"Re-render: factory rerender {a.post_id}")
    s.set_defaults(func=cmd)
