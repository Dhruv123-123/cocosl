from PIL import Image

from contentfactory.media.signature import DEVICES, draw, resolve, stamp
from contentfactory.media.util import Palette


PAL = Palette(dark=(10, 20, 15), light=(245, 240, 230), accents=[(47, 191, 113), (242, 177, 52)])


def _sig(device, corner="top-right"):
    return {"device": device, "color": "accent", "corner": corner, "size": 0.16, "label": "MMS",
            "where": ["thumbnail", "intro", "cover"]}


def test_every_device_draws_in_its_corner():
    for dev in DEVICES:
        img = draw(Image.new("RGB", (1280, 720), (90, 90, 90)), _sig(dev), PAL).convert("RGB")
        right = img.crop((640, 0, 1280, 360)).getcolors(1 << 20)
        assert any(c == (47, 191, 113) for _, c in right), dev
        assert img.getpixel((5, 715)) == (90, 90, 90) or dev == "bracket"


def test_resolve_auto_none_and_brand(factory):
    mms = factory.brand("money-made-simple")
    assert resolve(mms)["device"] == "corner_block" and resolve(mms)["label"] == "MMS"
    mms.visual.signature.device = "auto"
    assert resolve(mms)["device"] in DEVICES
    mms.visual.signature.device = "none"
    assert resolve(mms) is None


def test_stamp_keeps_jpeg_twin(tmp_path):
    p = tmp_path / "t.png"
    Image.new("RGB", (400, 300), (0, 0, 0)).save(p)
    stamp(p, _sig("stripe"), PAL)
    assert (tmp_path / "t.jpg").exists()
    assert Image.open(p).getpixel((395, 150)) == (47, 191, 113)


def test_rendered_post_carries_signature(factory):
    pid = factory.import_script("money-made-simple", {"title": "Sig test", "hook": "h", "segments": [
        {"heading": "Hook", "narration": "", "on_screen_text": "Cover", "visual_prompt": "x"},
        {"heading": "Two", "narration": "n", "on_screen_text": "Two", "visual_prompt": "y"}],
        "cta": "", "caption": "c", "hashtags": [], "description": "", "thumbnail_text": "", "sources": [],
        "claims_to_verify": [], "title_variants": [], "hook_variants": []},
        "carousel", render=True)
    post = factory.db.get("posts", pid)
    assert post["assets"]["signature"] == "corner_block"
    slide = Image.open(factory.settings.output_dir / post["assets"]["slides"][0]).convert("RGB")
    w, _ = slide.size
    assert slide.getpixel((w - 5, 5)) == Palette.from_brand(factory.brand("money-made-simple")).accent
