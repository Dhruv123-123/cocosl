"""The self-serve kits' email funnel (launch/ugc-service/kits-funnel) validates and exports for Sender."""
import shutil
from pathlib import Path

from contentfactory import sequence_export as se
from contentfactory.funnel.sequences import load_sequence, validate_sequence

KITS = Path(__file__).resolve().parents[1] / "launch" / "ugc-service" / "kits-funnel" / "brands"


def test_kits_funnel_validates_and_exports(factory, tmp_path):
    brands = tmp_path / "kits-brands"
    shutil.copytree(KITS, brands)
    factory.settings.brands_dir = brands
    brand = factory.brand("small-shop-kits")
    assert brand.cadence.paused and brand.welcome_via == "sender"
    seq = load_sequence(factory.settings, "small-shop-kits")
    assert [s.day_offset for s in seq.steps] == [0, 2, 5]
    assert validate_sequence(factory.settings, brand, seq) == []
    out, rows = se.export(factory, "small-shop-kits")
    assert len(rows) == 3 and not any(r[4] for r in rows)  # no launch/no-launch split: no discount in the copy
    last = (out / "03-day5" / "email.txt").read_text()
    assert "$35" in last and "$49" in last and "small-shop-bundle" in last
    for d in ("01-day0", "02-day2", "03-day5"):
        text = (out / d / "email.txt").read_text()
        assert "edited by a person" in text and "Unsubscribe:" not in text
        assert "human-written" not in text.lower() and "was $" not in text


def test_kits_funnel_is_not_a_factory_brand():
    root = Path(__file__).resolve().parents[1]
    assert not (root / "brands" / "small-shop-kits.yaml").exists()
