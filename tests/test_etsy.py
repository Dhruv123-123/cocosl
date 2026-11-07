"""Etsy listings stay inside Etsy's limits, and the printables render without errors."""
import sys
from pathlib import Path

ETSY = Path(__file__).resolve().parents[1] / "launch" / "etsy"
sys.path.insert(0, str(ETSY))

import listings  # noqa: E402
import printables  # noqa: E402
import printables_more  # noqa: E402


def test_listings_follow_etsy_limits():
    assert listings.validate() == []
    assert len(listings.LISTINGS) == 49
    for it in listings.LISTINGS:
        assert len(it["title"]) <= 140 and len(it["tags"]) == 13
        assert "DIGITAL DOWNLOAD" in it["description"] and "How it's made" in it["description"]


def test_every_printable_has_a_listing_and_pages():
    for slug, build in {**printables.PRINTABLES, **printables_more.MORE}.items():
        pages = build()
        assert len(pages) >= (3 if slug in printables.PRINTABLES else 2), slug
        assert listings.BY_SLUG[slug]["kind"] == "printable"
        assert all("moneymadesimple" in p for p in pages)


def test_printable_prices_are_low_cost():
    prices = [it["price"] for it in listings.LISTINGS if it["kind"] == "printable"]
    assert len(prices) == 40 and all(3 <= p <= 8 for p in prices)
    binder = listings.BY_SLUG["budget-binder-bundle"]
    assert binder["price"] < sum(listings.BY_SLUG[s]["price"] for s in binder["bundle"])


def test_savings_tiles_add_up_exactly():
    for target in printables.TILE_SETS:
        assert sum(printables.tiles_for(target)) == target


def test_fees_math():
    f = listings.fees(10.0)
    assert f["total"] == round(0.20 + 0.65 + 0.55, 2) and f["net"] == round(10 - f["total"], 2)


def test_new_printables_are_new_and_bundled():
    assert len(printables_more.MORE) == 30
    assert not set(printables_more.MORE) & set(printables.PRINTABLES)
    mega = listings.BY_SLUG["mega-budget-bundle"]
    every = [x["slug"] for x in listings.LISTINGS if x["kind"] == "printable"]
    assert sorted(mega["bundle"]) == sorted(every) and len(every) == 40
    for b in ("mega-budget-bundle", "savings-challenge-pack", "budget-binder-bundle"):
        it = listings.BY_SLUG[b]
        assert it["price"] < sum(listings.BY_SLUG[s]["price"] for s in it["bundle"])


def test_new_challenges_add_up():
    assert sum(printables_more.BINGO[1000]) == 1000 and sum(printables_more.BINGO[2000]) == 2000
    assert len(printables_more.BINGO[1000]) == 24
    for target, pattern in printables_more.THIRTY_DAY.items():
        days = printables_more._days(pattern, target)
        assert len(days) == 30 and sum(days) == target
    assert sum(range(1, 101)) == 5050 and sum(range(1, 51)) == 1275
    for goal, per_check in printables_more.PAYCHECK_GOALS:
        assert per_check * 26 == goal


def test_mockgen_layouts_render_html():
    sys.path.insert(0, str(ETSY))
    import mockgen
    pages = [Path("/tmp/a.png"), Path("/tmp/b.png"), Path("/tmp/c.png")]
    o = dict(title="Savings Bingo", price=3, label="Printable", chips=["Instant download"], brand="MMS")
    for size, (w, h) in mockgen.SIZES.items():
        doc = mockgen.hero(o, pages, w, h)
        assert f"width:{w}px;height:{h}px" in doc.replace(" ", "") or f"width:{w}px" in doc
        assert "Savings Bingo" in doc and "$3" in doc
    assert "40 items" in mockgen.inside(o, pages, 2000, 1500, count=40)
