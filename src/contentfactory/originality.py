"""`factory audit-originality`: a per-channel risk score against YouTube's inauthentic-content policy.

YouTube judges the channel as a whole: "image slideshows, templated storylines, or scrolling text with
minimal or no narrative" and "AI-generated content made with generic or unoriginal templates giving the
impression of mass production" (answer 1311392; research/scouting/youtube-policy-review-nov-2026.md).

    factory audit-originality                     # every brand's posts in the database
    factory audit-originality --packs             # every launch/<brand>/*.json pack on disk
    factory audit-originality --packs path/to/content.json --brand scam-decoded

Signals per channel (each 0-1, weighted into a 0-100 score):
* original element (30): long videos with no chart and no owner footage. A planned element that isn't
  in the video yet (a screen recording still to make) counts as half missing.
* thin long videos (15): long scripts under 800 words of narration.
* templated sameness (20): videos built like most of the others (same beat count, title pattern and
  hook pattern), and title patterns shared by 4+ videos.
* reused narration (20): sentences of 8+ words repeated across videos (calls to action excluded), and
  pairs of videos with heavy overlap.
* no real footage (15): the channel has no owner footage in any long video yet.

Score under 25: low. 25-49: medium. 50+: high (fix before the channel's first 10 long videos go up).
Nothing is changed; it prints the score, the reasons with examples, and what to fix first.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .guardrails import _shape, jaccard, shingles

WEIGHTS = {"original_element": 30, "thin": 15, "sameness": 20, "reused_narration": 20, "no_footage": 15}
CTA_RE = re.compile(r"\b(follow|subscribe|link in (?:bio|description)|comment below|like this video|"
                    r"turn on notifications|newsletter|watch (?:this )?next)\b", re.I)
THIN_WORDS = 800


@dataclass
class Signal:
    name: str
    value: float
    detail: str
    examples: list[str] = field(default_factory=list)


@dataclass
class ChannelRisk:
    brand: str
    longs: int
    shorts: int
    score: int
    level: str
    signals: list[Signal]
    fixes: list[str]


def _segs(script: dict) -> list[dict]:
    return script.get("segments") or []


def _narration(script: dict) -> str:
    return " ".join(s.get("narration", "") for s in _segs(script))


def _sentences(text: str) -> list[str]:
    return [s.strip().lower() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.split()) >= 8]


def element_text(value) -> str:
    """original_element is free text in some packs and {type, detail, chapter} in others."""
    if isinstance(value, dict):
        return " ".join(str(value.get(k) or "") for k in ("type", "detail", "what", "chapter")).strip()
    return str(value or "").strip()


def _element(script: dict, home: Path | None) -> str:
    """'footage' | 'chart' | 'planned' | 'none'."""
    segs = _segs(script)
    foot = [s.get("footage") for s in segs if (s.get("footage") or "").strip()]
    if foot and (home is None or any((home / f).is_file() or Path(f).is_file() for f in foot)):
        return "footage"
    if any(s.get("chart") for s in segs):
        return "chart"
    if foot or element_text(script.get("original_element")):
        return "planned"
    return "none"


def audit(items: list[dict], brand: str, cta: str = "", home: Path | None = None) -> ChannelRisk:
    """items: [{"id", "format", "script"}] for one channel."""
    vids = [i for i in items if i.get("format") in ("short", "mid", "long")]
    longs = [i for i in vids if i["format"] == "long"]
    shorts = [i for i in vids if i["format"] in ("short", "mid")]
    label = lambda i: f"#{i['id']} {(i['script'].get('title') or '')[:60]}"  # noqa: E731
    signals: list[Signal] = []

    kinds = {i["id"]: _element(i["script"], home) for i in longs}
    missing = [i for i in longs if kinds[i["id"]] == "none"]
    planned = [i for i in longs if kinds[i["id"]] == "planned"]
    v = (len(missing) + 0.5 * len(planned)) / len(longs) if longs else 0.0
    signals.append(Signal("original_element", v, f"{len(missing)} of {len(longs)} long videos have no original "
                          f"element; {len(planned)} only plan one (a recording still to make)",
                          [label(i) for i in missing[:5]]))

    thin = [i for i in longs if len(_narration(i["script"]).split()) < THIN_WORDS]
    avg = round(sum(len(_narration(i["script"]).split()) for i in longs) / len(longs)) if longs else 0
    signals.append(Signal("thin", len(thin) / len(longs) if longs else 0.0,
                          f"{len(thin)} of {len(longs)} long videos under {THIN_WORDS} words (average {avg})",
                          [f"{label(i)} ({len(_narration(i['script']).split())} words)" for i in thin[:5]]))

    # templated sameness, per format
    alike_ids, pattern_hits = set(), []
    for fmt_group in (longs, shorts):
        shapes = [(i, (min(len(_segs(i["script"])), 12) // 2, _shape(i["script"].get("title", "")),
                       _shape(i["script"].get("hook", ""), 4))) for i in fmt_group]
        for i, sh in shapes:
            same = sum(1 for j, sh2 in shapes if j is not i and sum(a == b for a, b in zip(sh, sh2)) >= 2)
            if len(shapes) >= 6 and same * 2 > len(shapes) - 1:
                alike_ids.add(i["id"])
        titles = Counter(_shape(i["script"].get("title", "")) for i in fmt_group)
        pattern_hits += [(p, n) for p, n in titles.items() if n >= 4 and p.strip()]
    titled = sum(n for _, n in pattern_hits)
    v = max(len(alike_ids) / len(vids) if vids else 0.0, titled / len(vids) if vids else 0.0)
    signals.append(Signal("sameness", v, f"{len(alike_ids)} of {len(vids)} videos built like most of the others; "
                          f"{titled} share a title pattern used 4+ times",
                          [f"“{p} …” × {n}" for p, n in sorted(pattern_hits, key=lambda x: -x[1])[:4]]))

    # reused narration
    cta_l = (cta or "").lower()
    where = defaultdict(set)
    for i in vids:
        for s in set(_sentences(_narration(i["script"]))):
            if CTA_RE.search(s) or (cta_l and s in cta_l):
                continue
            where[s].add(i["id"])
    reused = {s: ids for s, ids in where.items() if len(ids) > 1}
    hit = Counter(pid for ids in reused.values() for pid in ids)
    heavy = [pid for pid, n in hit.items() if n >= 2]
    pairs = []
    sh = {i["id"]: shingles(_narration(i["script"])) for i in longs}
    ids = list(sh)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            j = jaccard(sh[ids[a]], sh[ids[b]])
            if j >= 0.25:
                pairs.append((ids[a], ids[b], j))
    boiler = {s: ids for s, ids in reused.items() if len(ids) >= max(3, len(vids) // 4)}  # a stock line
    in_boiler = set().union(*boiler.values()) if boiler else set()
    v = min(1.0, (len(set(heavy) | in_boiler) + 2 * len(pairs)) / len(vids)) if vids else 0.0
    signals.append(Signal("reused_narration", v, f"{len(reused)} sentence(s) repeated across videos, in "
                          f"{len(set(heavy))} video(s) with 2+ repeats; {len(boiler)} stock line(s) in {len(in_boiler)} videos; "
                          f"{len(pairs)} long-video pair(s) overlap 25%+",
                          [f"“{s[:80]}” in {len(i)} videos" for s, i in sorted(reused.items(), key=lambda x: -len(x[1]))[:3]]
                          + [f"#{a} and #{b}: {j:.0%} overlap" for a, b, j in pairs[:2]]))

    has_footage = any(k == "footage" for k in kinds.values())
    signals.append(Signal("no_footage", 0.0 if has_footage or not longs else 1.0,
                          "owner footage in at least one long video" if has_footage else
                          "no long video has your own footage yet (screen recordings are the cheapest proof a person makes the channel)"))

    score = round(sum(WEIGHTS[s.name] * min(1.0, s.value) for s in signals))
    level = "high" if score >= 50 else "medium" if score >= 25 else "low"
    fixes = []
    by = {s.name: s for s in signals}
    if missing:
        fixes.append(f"Give the {len(missing)} long video(s) without one an original element: a chart from the "
                     "video's own numbers, a screen recording, or your own segment (Segment.chart / Segment.footage).")
    if planned:
        fixes.append(f"Record the {len(planned)} planned screen recording(s) (`factory recordings`), newest videos first.")
    if by["thin"].value > 0.3:
        fixes.append(f"Lengthen the thinnest long scripts to 900+ words with a worked example.")
    if by["sameness"].value > 0.3:
        fixes.append("Vary the structure: different openings, beat counts and title patterns from video to video.")
    if by["reused_narration"].value > 0.2:
        fixes.append("Rewrite the repeated sentences so each video says things its own way.")
    if not has_footage and longs:
        fixes.append("Get your own footage into the first long videos before launch.")
    return ChannelRisk(brand, len(longs), len(shorts), score, level, signals, fixes)


def from_db(factory) -> dict[str, list[dict]]:
    out = defaultdict(list)
    for p in factory.db.query("SELECT id, brand, format, script FROM posts WHERE status NOT IN ('rejected', 'failed') "
                              "AND format IN ('short', 'mid', 'long') ORDER BY id"):
        out[p["brand"]].append({"id": p["id"], "format": p["format"],
                                "script": p["script"] if isinstance(p["script"], dict) else {}})
    return out


def from_packs(paths: list[Path]) -> list[dict]:
    items, n = [], 0
    for path in paths:
        data = json.loads(Path(path).read_text())
        for it in data if isinstance(data, list) else data.get("posts", []):
            if isinstance(it, dict) and it.get("format") in ("short", "mid", "long"):
                n += 1
                script = dict(it.get("script") or it)
                if it.get("original_element") and not script.get("original_element"):
                    script["original_element"] = it["original_element"]  # some packs keep it on the item
                items.append({"id": n, "format": it["format"], "script": script})
    return items


def to_text(r: ChannelRisk) -> str:
    out = [f"{r.brand}: {r.score}/100 ({r.level.upper()} risk) · {r.longs} long, {r.shorts} Shorts"]
    for s in r.signals:
        out.append(f"  {s.name:17s} {round(WEIGHTS[s.name] * min(1, s.value)):>2}/{WEIGHTS[s.name]}  {s.detail}")
        out += [f"      e.g. {e}" for e in s.examples[:3]]
    if r.fixes:
        out.append("  Fix first:")
        out += [f"    {k}. {f}" for k, f in enumerate(r.fixes, 1)]
    return "\n".join(out)


def register(sub, factory_fn) -> None:
    s = sub.add_parser("audit-originality", help="per-channel YouTube inauthentic-content risk score")
    s.add_argument("--packs", nargs="*", type=Path, default=None,
                   help="audit pack files instead of the database (no paths: every launch/<brand>/*.json)")
    s.add_argument("--brand", default="", help="only this brand (or the brand of the given pack files)")
    s.add_argument("--json", action="store_true")

    def cmd(a):
        f = factory_fn(a)
        brands = f.brands()
        if a.packs is not None:
            groups = {}
            if a.packs:
                groups[a.brand or a.packs[0].parent.name] = from_packs(a.packs)
            else:
                for d in sorted((f.settings.home / "launch").glob("*/")):
                    files = sorted(d.rglob("*.json"))
                    if files and (not a.brand or d.name == a.brand):
                        groups[d.name] = from_packs(files)
        else:
            groups = {k: v for k, v in from_db(f).items() if not a.brand or k == a.brand}
        results = [audit(items, slug, brands[slug].cta if slug in brands else "", f.settings.home)
                   for slug, items in groups.items() if items]
        if a.json:
            from dataclasses import asdict
            print(json.dumps([asdict(r) for r in results], indent=2))
        elif not results:
            print("No videos to audit.")
        else:
            print("\n\n".join(to_text(r) for r in sorted(results, key=lambda r: -r.score)))
        if any(r.level == "high" for r in results):
            raise SystemExit(2)
    s.set_defaults(func=cmd)
