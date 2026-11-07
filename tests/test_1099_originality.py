"""1099 Money version of tests/test_originality.py (YouTube "inauthentic content", research/scouting/
youtube-monetization.md): every video carries a format label, formats are mixed within each month, each
long video has one original element, and no video's structure repeats most of the 20 before it."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "launch" / "1099-money"
FILES = [ROOT / "content.json"] + sorted(ROOT.glob("month-*/content.json")) + [ROOT / "drivers" / "content.json"]
FILES += [ROOT / "youtube-6wk" / "content.json", ROOT / "jar-challenge" / "content.json", ROOT / "couples" / "content.json", ROOT / "july-bridge" / "content.json",
          ROOT / "tax-season-push" / "content.json"]
NEW_FORMATS = {"on-screen-calculation", "myth-vs-fact", "question-reply", "countdown", "real-numbers"}
ELEMENTS = {"worked-example-chart", "screen-recording", "human-segment"}


def _videos():
    return [(p.parent.name, it) for p in FILES for it in json.loads(p.read_text()) if it["format"] in ("short", "long")]


def _signature(it):
    sc = it["script"]
    hook, title = sc["hook"], sc["title"]
    hook_kind = "you" if re.match(r"(If you|You|Your)", hook) else "num" if re.match(r"[\$\d]", hook) else "q" if "?" in hook.split(".")[0] else "stmt"
    title_kind = "num" if re.match(r"[\$\d]", title) else "colon" if ":" in title else "q" if "?" in title else "plain"
    return (it["format"], len(sc["segments"]), hook_kind, title_kind, it["format_style"])


def _scores():
    vids = [it for _, it in _videos()]
    out = []
    for k, it in enumerate(vids):
        prev = [p for p in vids[max(0, k - 20):k] if p["format"] == it["format"]]
        out.append(sum(_signature(p) == _signature(it) for p in prev) / max(1, len(prev)))
    return out


def test_every_video_has_a_format_and_batches_are_mixed():
    vids = _videos()
    assert all(it.get("format_style") for _, it in vids)
    shorts = collections.Counter(it["format_style"] for _, it in vids if it["format"] == "short")
    assert all(shorts[f] >= 4 for f in NEW_FORMATS), shorts
    for batch in {b for b, _ in vids}:
        styles = [it["format_style"] for b, it in vids if b == batch and it["format"] == "short"]
        if not styles:  # a long-form-only plan has no Shorts to mix
            continue
        top = collections.Counter(styles).most_common(1)[0][1]
        assert top <= len(styles) / 2, (batch, collections.Counter(styles))


def test_reformatted_shorts_say_what_they_are():
    for _, it in _videos():
        segs, style = it["script"]["segments"], it.get("format_style")
        if style == "myth-vs-fact" and it["format"] == "short":
            assert sum("Myth:" in s["narration"] and "Fact:" in s["narration"] for s in segs) >= 2, it["script"]["title"]
        if style == "question-reply" and it["format"] == "short":
            assert segs[0]["heading"] == "Common question" and "common question" in segs[0]["narration"].lower()
        if style == "countdown" and it["format"] == "short":
            assert [s["heading"] for s in segs if s["heading"].startswith("Number")][-1] == "Number 1"


def test_every_long_video_has_an_original_element():
    for batch, it in _videos():
        if it["format"] != "long":
            continue
        el = it.get("original_element")
        assert el and el["type"] in ELEMENTS and len(el["detail"]) >= 30, (batch, it["script"]["title"])
        assert el["chapter"] in [s["heading"] for s in it["script"]["segments"]], (batch, el["chapter"])
    types = collections.Counter(it["original_element"]["type"] for _, it in _videos() if it["format"] == "long")
    assert set(types) == ELEMENTS, types


def test_no_video_repeats_the_structure_of_the_last_20():
    scores = _scores()
    assert max(scores) <= 0.5
    assert sum(scores) / len(scores) <= 0.12


def test_worked_example_longs_carry_their_chart():
    # The pack's original-element check blocks a long video with no chart or footage; a worked-example
    # chart is ready to render, so it must be drawn on its own chapter.
    for batch, it in _videos():
        el = it.get("original_element") or {}
        if it["format"] == "long" and el.get("type") == "worked-example-chart":
            seg = next(s for s in it["script"]["segments"] if s["heading"] == el["chapter"])
            chart = seg.get("chart") or {}
            assert len(chart.get("labels", [])) == len(chart.get("values", [])) >= 2, (batch, it["script"]["title"])
