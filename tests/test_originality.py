"""Guards against YouTube's "inauthentic content" pattern (research/scouting/youtube-monetization.md):
every video carries a format label, formats are mixed within each month, long videos each have one
original element, and no video's structure repeats most of the 20 before it."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "launch" / "money-made-simple"
FILES = sorted(ROOT.glob("month-*/content.json")) + [ROOT / "youtube-series" / "content.json"]
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


def test_every_video_has_a_format_and_months_are_mixed():
    vids = _videos()
    assert all(it.get("format_style") for _, it in vids)
    shorts = collections.Counter(it["format_style"] for _, it in vids if it["format"] == "short")
    assert all(shorts[f] >= 4 for f in NEW_FORMATS), shorts
    for month in {m for m, _ in vids if m.startswith("month-")}:
        styles = [it["format_style"] for m, it in vids if m == month and it["format"] == "short"]
        top = collections.Counter(styles).most_common(1)[0][1]
        assert top <= len(styles) / 2, (month, collections.Counter(styles))


def test_every_long_video_has_an_original_element():
    for month, it in _videos():
        if it["format"] != "long":
            continue
        el = it.get("original_element")
        assert el and el["type"] in ELEMENTS and len(el["detail"]) >= 30, (month, it["script"]["title"])
        assert el["chapter"] in [s["heading"] for s in it["script"]["segments"]], (month, el["chapter"])


def test_no_video_repeats_the_structure_of_the_last_20():
    vids = [it for _, it in _videos()]
    scores = []
    for k, it in enumerate(vids):
        prev = [p for p in vids[max(0, k - 20):k] if p["format"] == it["format"]]
        same = sum(_signature(p) == _signature(it) for p in prev)
        scores.append(same / max(1, len(prev)))
    assert max(scores) <= 0.5
    assert sum(scores) / len(scores) <= 0.12
