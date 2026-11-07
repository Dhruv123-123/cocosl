"""The one 30-minute recording session the 14 launch days need from Dhruv, in `factory batch-record` format.

    python3 recordings.py   ->  ../../launch-recording/  (SHOT_LIST.md, teleprompter.html, teleprompter.txt, session.json)

Of the 31 long-video recordings in LONG_VIDEO_RECORDINGS.md, the launch uses 3 (its three long videos). The rest of
this session is the short inserts from LAUNCH_WEEK.md's originality table that need a camera, his phone or his own
card: the trailer, face-cam openers and hands-on shots. Generated walkthroughs, quizzes and charts aren't in here
(the factory makes those). The last setup is the voice takes for week 1's four TikTok cuts; week 2's go in the
next `factory batch-record --brand scam-decoded` session once the launch posts are imported.

Shots are in setup order, so each setup (phone, computer, hands, face cam) is done once. The file layout and the
SHOT_LIST / teleprompter output come from contentfactory.batch_record, so it reads like every other session.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "launch-recording"
TAKES = 2.5            # same allowance batch_record uses for retakes and setup
BUDGET = 30            # minutes


def _build():
    spec = importlib.util.spec_from_file_location("scam_decoded_launch_week", HERE / "build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _batch_record():
    sys.path.insert(0, str(ROOT.parent.parent / "src"))
    try:
        from contentfactory import batch_record
    finally:
        sys.path.pop(0)
    return batch_record


F = "footage/scam-decoded/"
# (setup, post key, day, beat (0-based), minutes, save_as, what to show, lines to say or None)
SHOTS = [
 ("phone", "long:A", 1, 4, 0.5, F + "how-to-protect-your-parents-from-scams-t--phone-settings.mp4",
  "Your own phone: silence unknown callers, the carrier spam filter, and adding a contact as a favourite.", None),
 ("phone", 1, 6, 3, 0.3, F + "launch-01-freeze-on-phone.mp4",
  "One bureau's freeze page on your phone, typed in, scrolling to the freeze button. Stop at sign-in.", None),
 ("computer", "long:B", 6, 4, 0.5, F + "identity-theft-recovery-step-by-step-wha--3-report.mp4",
  "IdentityTheft.gov (typed in): start a report, pick a category, stop before personal details.", None),
 ("computer", "long:C", 11, 1, 0.5, F + "credit-freeze-vs-fraud-alert-vs-monitori--freeze.mp4",
  "Type one bureau's freeze page address and find the freeze button. Stop at sign-in.", None),
 ("computer", 15, 7, 2, 0.7, F + "launch-15-three-bureaus.mp4",
  "Equifax, Experian, TransUnion freeze pages, typed in, one after another. Stop at each sign-in.", None),
 ("computer", 21, 9, 4, 0.2, F + "launch-21-sign-in-settings.mp4",
  "Your email's security page: where two-step sign-in and passkeys are. Blur the address.", None),
 ("hands", 0, 8, 1, 0.2, F + "launch-00-gift-card-back.mp4",
  "Gift card packaging on a table; flip one to the back. No real card numbers in shot.", None),
 ("hands", 4, 5, 3, 0.2, F + "launch-04-card-back.mp4",
  "The back of your own bank card, number covered; thumb on the printed phone number.", None),
 ("hands", 18, 5, 5, 0.2, F + "launch-18-dial-card-number.mp4",
  "Dial the number from the back of your card (screen shows only the first digits), then hang up.", None),
 ("face cam", "trailer", 1, 0, 0.8, F + "launch-trailer.mp4", "Face cam, chest up, eye level, window light.", "TRAILER"),
 ("face cam", 3, 3, 0, 0.2, F + "launch-03-safe-word-open.mp4",
  "Face cam opener. On-screen text beside you will show the fake call.",
  ["One word, picked tonight, beats a cloned voice of someone you love.", "What's our word?"]),
 ("face cam", 6, 12, 0, 0.2, F + "launch-06-delivery-open.mp4",
  "Face cam, holding your phone up to camera with a fictional delivery text on it.",
  ["One question kills every fake delivery text.", "Did I actually ask for updates?"]),
 ("face cam", 26, 10, 0, 0.3, F + "launch-26-kiosk-open.mp4", "Face cam opener and sign-off for the Bitcoin ATM TikTok.",
  ["Two scam scripts end at a Bitcoin ATM, and over a hundred and ten million dollars was reported lost there in 2023.",
   "No agency, bank or business will ever send you to a Bitcoin ATM. Hang up."]),
]


# Week-1 TikTok cuts (days 2-7) in Dhruv's own voice; week 2's voice takes go in the next batch-record session.
VOICE = [(16, 2), (17, 3), (18, 5), (15, 7)]


def plan():
    lw = _build()
    content, longs = lw.load()
    names = {"long:A": lw.LONG_A, "long:B": lw.LONG_B, "long:C": lw.LONG_C}
    tasks = []
    for setup, key, day, beat, minutes, save_as, show, lines in SHOTS:
        if key == "trailer":
            title, segs = "Channel trailer", []
            lines = [say for _, say, _ in lw.TRAILER]
        elif isinstance(key, str):
            title = names[key]
            segs = longs[title]["script"]["segments"]
        else:
            title = content[key]["script"]["title"]
            segs = content[key]["script"]["segments"]
        narration = segs[beat]["narration"] if beat < len(segs) else ""
        t = {"post_id": key if isinstance(key, str) else f"launch-{key}", "brand": "scam-decoded",
             "format": "long" if str(key).startswith("long") else "short", "title": title,
             "publish_at": f"Day {day:02d}", "kind": "screen", "beat": beat, "save_as": save_as,
             "minutes": minutes, "show": f"[{setup}] {show}", "narration": narration, "setup": setup}
        if lines:
            t["lines"] = lines
        tasks.append(t)
    for key, day in VOICE:
        sc = content[key]["script"]
        lines = [s["narration"] for s in sc["segments"] if s.get("narration")] + [sc["cta"]]
        words = sum(len(x.split()) for x in lines)
        tasks.append({"post_id": f"launch-{key}", "brand": "scam-decoded", "format": "short", "title": sc["title"],
                      "publish_at": f"Day {day:02d}", "kind": "screen", "beat": 0,
                      "save_as": f"voice/scam-decoded/launch-{key}.wav", "minutes": round(words / 150, 1),
                      "show": "[voice] Read the whole TikTok cut straight through, in your own voice.",
                      "narration": "", "lines": lines, "setup": "voice"})
    used = round(sum(t["minutes"] for t in tasks) * TAKES)
    return {"n": 1, "brand": "scam-decoded", "kind": "screen", "tasks": tasks, "minutes": used, "due": "Day 01"}


def check(s):
    assert s["minutes"] <= BUDGET, s["minutes"]
    setups = [t["setup"] for t in s["tasks"]]
    assert setups == sorted(setups, key=["phone", "computer", "hands", "face cam", "voice"].index), "shots must be in setup order"
    lw = _build()
    long_titles = {lw.LONG_A, lw.LONG_B, lw.LONG_C}
    rec = (ROOT / "LONG_VIDEO_RECORDINGS.md").read_text()
    for t in s["tasks"]:
        if t["title"] in long_titles:   # the three long-video files must match the long recordings list
            assert f"`{t['save_as']}`" in rec, t["save_as"]
    assert len({t["save_as"] for t in s["tasks"]}) == len(s["tasks"])


def files(s):
    br = _batch_record()
    order = ["", "## Shot order (one setup at a time)", ""]
    last = None
    for k, t in enumerate(s["tasks"], 1):
        if t["setup"] != last:
            order.append(f"**{t['setup'].capitalize()}**")
            last = t["setup"]
        order.append(f"{k}. {t['title'][:60]} ({t['publish_at']}): {t['show'].split('] ', 1)[1]}")
    head = ("Made by `launch/scam-decoded/generators/launch-week/recordings.py` for LAUNCH_WEEK.md. "
            "'Publishes' is the launch day, because Day 1 isn't picked yet. These posts aren't in the factory "
            "database, so skip `batch-record attach`: save each file at its path under the factory home (the same "
            "convention as LONG_VIDEO_RECORDINGS.md). Face cam: chest up, eye level, window light, phone mic is fine.\n")
    shot = br.shot_list(s).replace(" UTC |", " |").replace(" UTC.", ".").replace("\n\n", "\n\n" + head + "\n", 1)
    shot = shot.replace("\nAfter recording:", "\n".join(order) + "\n\nAfter recording:", 1)
    return {"SHOT_LIST.md": shot, "teleprompter.html": br.teleprompter_html(s),
            "teleprompter.txt": br.teleprompter_text(s), "session.json": json.dumps(s, indent=2) + "\n"}


def main():
    s = plan()
    check(s)
    OUT.mkdir(exist_ok=True)
    for name, text in files(s).items():
        (OUT / name).write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}/ ({len(s['tasks'])} shots, about {s['minutes']} min)")


if __name__ == "__main__":
    main()
