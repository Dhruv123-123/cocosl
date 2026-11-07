import importlib.util
import sys
from pathlib import Path

import pytest

PRODUCT = Path(__file__).resolve().parents[1] / "launch" / "scam-decoded" / "product"
TRAINING = PRODUCT / "team-training"


def _load(name, path):
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(path.parent))


def test_training_content_is_consistent():
    c = _load("training_content", TRAINING / "content.py")
    assert sum(s["minutes"] for s in c.SLIDES) == 45
    assert all(s["notes"].strip() for s in c.SLIDES)
    assert len(c.QUIZ) == 12
    for q, opts, ans, why in c.QUIZ:
        assert len(opts) == 4 and 0 <= ans < 4 and why
    assert sum(1 for s in c.SLIDES if s["kind"] == "scenario") == 3
    # example domains in mock emails must be reserved, never real
    for s in c.SLIDES:
        if s["kind"] == "email":
            assert s["email"]["sender"].rstrip(">").endswith(".example")


def test_training_pack_builds_editable_deck(tmp_path, monkeypatch):
    pytest.importorskip("pptx")
    from pptx import Presentation
    build = _load("training_build", TRAINING / "build.py")
    monkeypatch.setattr(build, "DIST", tmp_path / "dist")
    monkeypatch.setattr(sys, "argv", ["build.py", "--no-pdf"])
    build.main()
    deck = Presentation(tmp_path / "dist" / "Spot-It-Stop-It-Slides.pptx")
    assert len(deck.slides) == len(build.C.SLIDES)
    assert all(s.notes_slide.notes_text_frame.text.strip() for s in deck.slides)
    guide = (tmp_path / "dist" / "Facilitator-Guide.html").read_text()
    report_slide = next(i for i, s in enumerate(build.C.SLIDES, 1) if s["kind"] == "report")
    assert f"Slide {report_slide} · Reporting" in guide
    for name in ("Quiz", "Answer-Key", "Certificate", "Poster-Verify-Before-You-Pay"):
        assert (tmp_path / "dist" / f"{name}.html").exists()


def test_parents_guide_and_listings():
    html = (PRODUCT / "protect-your-parents" / "protect-your-parents.html").read_text()
    assert html.count('class="page') == 20
    assert (PRODUCT / "protect-your-parents" / "Protect-Your-Parents.pdf").stat().st_size > 50_000
    ladder = (PRODUCT / "LADDER.md").read_text()
    for code in ("KITPARENTS", "GUIDEKIT", "TEAMLAUNCH"):
        assert code in ladder
    assert "KITPARENTS" in (PRODUCT / "LISTING.md").read_text()
    for listing in (PRODUCT / "protect-your-parents" / "LISTING.md", TRAINING / "LISTING.md", PRODUCT / "LISTING.md"):
        assert "guarantee" not in listing.read_text().lower()
