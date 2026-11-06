"""Brand kit: files exist, sizes are right, bios respect limits and disclose AI."""
from PIL import Image

from contentfactory.brandkit import build_brand_kit
from contentfactory.brandkit.bios import AI_RE, LIMITS, BioPack, enforce_limits
from contentfactory.brandkit.draw import Palette, initials


def test_brand_kit_files_and_sizes(factory):
    brand = factory.brand("money-made-simple")
    paths = build_brand_kit(factory.settings, brand, llm=factory.llm)
    root = factory.settings.output_dir / brand.slug / "brand-kit"
    for p in paths.values():
        assert p.exists() and p.is_relative_to(root)
    sizes = {
        "profile_picture": (1080, 1080),
        "youtube_banner": (2560, 1440),
        "youtube_watermark": (150, 150),
    }
    for key, size in sizes.items():
        with Image.open(paths[key]) as im:
            assert im.size == size, key
    with Image.open(paths["youtube_watermark"]) as im:
        assert im.mode == "RGBA" and im.getpixel((0, 0))[3] == 0  # transparent corner
    highlights = [k for k in paths if k.startswith("highlight_")]
    assert len(highlights) == 5
    for k in highlights:
        with Image.open(paths[k]) as im:
            assert im.size == (1080, 1920)
    html = paths["style_sheet_html"].read_text()
    for colour in brand.visual.palette:
        assert colour.lower() in html.lower()
    assert paths["style_sheet_png"].stat().st_size > 10_000
    bio = paths["bio_pack"].read_text()
    assert "Instagram bio" in bio and "AI-assisted" in bio


def test_profile_picture_survives_circle_crop(factory):
    """Corners outside the inscribed circle are plain background (no content)."""
    brand = factory.brand("tiny-histories")
    paths = build_brand_kit(factory.settings, brand, llm=factory.llm)
    with Image.open(paths["profile_picture"]) as im:
        im = im.convert("RGB")
        pal = Palette.from_hex(brand.visual.palette)
        corner = im.getpixel((20, 20))
        assert sum(abs(a - b) for a, b in zip(corner, pal.accent)) > 60  # corner isn't the logo disc


def test_bios_limits_and_disclosure():
    long = "x " * 400
    pack = enforce_limits(BioPack(instagram=long, tiktok=long, youtube_about=long * 3, x=long, threads=long))
    assert len(pack.instagram) <= LIMITS["instagram"]
    assert len(pack.tiktok) <= LIMITS["tiktok"]
    assert len(pack.x) <= LIMITS["x"]
    assert len(pack.threads) <= LIMITS["threads"]
    assert len(pack.youtube_about) <= LIMITS["youtube_about"]
    for text in (pack.instagram, pack.tiktok, pack.x, pack.threads, pack.youtube_about):
        assert AI_RE.search(text)


def test_initials():
    assert initials("Money Made Simple") == "MS"
    assert initials("Tiny Histories") == "TH"
    assert initials("The Cosmos") == "CO"
