from contentfactory.media.chapters import build, format_block, stamp, with_chapters


def test_build_merges_short_and_repeated():
    starts = [(0.4, "Hook"), (6, "Why it matters"), (20, "Why it matters"), (35, "Step one"), (39, "Step two"),
              (70, "Recap"), (95, "")]
    ch = build(starts, 100)
    assert ch == [(0.0, "Why it matters"), (39, "Step two"), (70, "Recap")]


def test_too_few_chapters_gives_none():
    assert build([(0, "A"), (30, "B")], 60) == []
    assert build([(0, "A"), (5, "B"), (8, "C")], 15) == []


def test_format_and_description():
    ch = [(0.0, "Intro"), (65.2, "The math"), (3700, "Wrap")]
    assert stamp(65.2) == "1:05" and stamp(3700) == "1:01:40"
    assert format_block(ch).splitlines()[1] == "0:00:00 Intro"
    desc = "What this video covers.\n\n00:00 Intro\n1:30 - Guess\nChapters:\n\nLinks below."
    out = with_chapters(desc, [(0.0, "Intro"), (40, "Math"), (90, "Wrap")])
    assert out == "What this video covers.\n\nChapters\n0:00 Intro\n0:40 Math\n1:30 Wrap\n\nLinks below."
    assert with_chapters(desc, []) == desc


def test_youtube_description_gets_real_chapters(factory):
    pid = factory.db.insert("posts", {
        "brand": "money-made-simple", "format": "long", "status": "approved", "title": "t", "caption": "c",
        "hashtags": [], "disclosure": "Made with AI tools.",
        "script": {"description": "Intro line.\n\n0:00 Start\n2:00 Guess"},
        "assets": {"video": "v.mp4", "chapters": [[0.0, "Start"], [42.5, "Math"], [100, "Wrap"]]}})
    req = factory.build_request(factory.db.get("posts", pid), "youtube")
    assert req.description.startswith("Intro line.\n\nChapters\n0:00 Start\n0:42 Math\n1:40 Wrap")
    assert "Guess" not in req.description and req.description.endswith("Made with AI tools.")
