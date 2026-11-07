"""The Money Made Simple ebook: structure, cross-references, copy rules, covers and the Kindle EPUB."""
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

EBOOK = Path(__file__).resolve().parents[1] / "launch" / "ebook"
sys.path.insert(0, str(EBOOK))

import build_ebook as B  # noqa: E402


def test_chapters_and_structure():
    assert [f for f in B.ORDER if not (B.CHAPTERS / f).exists()] == []
    assert sorted(p.name for p in B.CHAPTERS.glob("*.md")) == sorted(B.ORDER)
    heads = B.outline()
    parts = [h for h in heads if h["kind"] == "part"]
    chapters = [h for h in heads if h["kind"] == "chapter"]
    assert len(parts) == 5 and 15 <= len(chapters) <= 22
    assert [c["num"] for c in chapters] == list(range(1, len(chapters) + 1))
    ids = [c["id"] for c in chapters]
    assert all(ids) and len(set(ids)) == len(ids)
    assert heads[0]["title"].startswith("Introduction")


def test_cross_references_resolve_and_length():
    src = B.resolved_source()
    assert "{{" not in src and "}}" not in src
    assert "Chapter 7 bankruptcy" in src           # the legal term, not a cross-reference
    nums = {h["id"]: h["num"] for h in B.outline() if h["kind"] == "chapter"}
    assert f"Chapter {nums['lower-rate']} lists the options" in src
    assert 22_000 <= B.word_count() <= 30_000


def test_copy_rules():
    src = B.resolved_source()
    B.check_copy(src)
    low = src.lower()
    assert "not financial" in low and "fictional" in low and "ai writing tools" in low
    # No sales links, discount codes or store placeholders carried over from the product guides.
    assert not re.search(r"\b[A-Z]{4,}\d\b", src)          # codes like BILLCUT5
    assert "http" not in src and "store link" not in low
    # US spelling throughout (the source guides mixed in some British spellings).
    for word in ("organis", "colour", "counsell", "tyre", "maths", "prioritis", "categoris", "recognis"):
        assert word not in low, word
    # The worked examples match the guides they came from.
    for figure in ("$184.62", "$2,150", "$1,378", "$5,050", "$242,077", "$41,174", "39 months", "$3,804", "$631"):
        assert figure in src, figure


def test_maya_and_balance_transfer_math():
    pool = 3500 - 2150 - 200 - 350
    assert pool == 800 and int(pool * 12 / 52) == 184
    bal, interest = 3000.0, 0.0
    while bal > 0:
        i = bal * 0.249 / 12
        interest += i
        bal = bal + i - 200
    assert round(interest) == 631


def test_print_and_epub_markup():
    src = B.resolved_source()
    md = B.epub_markdown(src)
    assert "# 1. The Four Lines" in md and "# Copyright" in md and "# Part One: See Your Money" in md
    body = B.print_body_md(src)
    assert body.count('class="partpage"') == 5 and '<div class="kick">Chapter 1</div>' in body
    toc = B.toc_html({h["title"]: i + 4 for i, h in enumerate(B.outline())})
    assert toc.count('class="t"') == len([h for h in B.outline() if h["kind"] != "part"])


def test_cover_sizes():
    w, h = B.cover_size(104)
    assert h == 9.25 and abs(w - (12.25 + 104 * 0.002252)) < 1e-3
    assert 'class="sptxt"' in B.paperback_cover_html(104)
    assert 'class="sptxt"' not in B.paperback_cover_html(60)       # KDP: no spine text on thin books
    assert "not financial" in B.BACK_FINE and "AI" in B.BACK_FINE
    k = B.kindle_cover_html()
    assert "Money<br>Made<br><em>Simple</em>" in k


@pytest.mark.skipif(not shutil.which("pandoc"), reason="pandoc not installed")
def test_epub_builds(tmp_path):
    from PIL import Image
    cover = tmp_path / "c.jpg"
    Image.new("RGB", (160, 256), "#f4f1e8").save(cover)
    epub = B.build_epub(B.resolved_source(), tmp_path, cover, tmp_path)
    z = zipfile.ZipFile(epub)
    assert z.namelist()[0] == "mimetype" and z.read("mimetype") == b"application/epub+zip"
    nav = z.read("EPUB/nav.xhtml").decode()
    assert "1. The Four Lines" in nav and "Glossary" in nav
    opf = z.read("EPUB/content.opf").decode()
    assert "Money Made Simple" in opf and "en-US" in opf
    text = " ".join(z.read(n).decode() for n in z.namelist() if n.endswith(".xhtml"))
    assert "$184" in text and "<math" not in text      # dollar amounts stay text, never TeX math


@pytest.mark.skipif(not (shutil.which("pandoc") and shutil.which("pdftotext")), reason="pandoc/poppler not installed")
def test_interior_html_has_every_chapter():
    out = B.interior_html(B.resolved_source())
    for h in B.outline():
        if h["kind"] == "chapter":
            assert f'id="{h["id"]}"' in out
    assert subprocess.run(["pdftotext", "-v"], capture_output=True).returncode == 0
