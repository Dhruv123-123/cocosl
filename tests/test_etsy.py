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
    assert len(listings.LISTINGS) == 50
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
    prices = [it["price"] for it in listings.LISTINGS if it["kind"] == "printable" and not it.get("dated")]
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
    every = [x["slug"] for x in listings.LISTINGS if x["kind"] == "printable" and not x.get("dated")]
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


def test_2027_planner_dates_are_right():
    import calendar as cal
    from datetime import date
    import planner_2027 as P
    k = P.key_dates(2027)
    assert date(2027, 1, 18) in k and date(2027, 5, 31) in k and date(2027, 9, 6) in k and date(2027, 11, 25) in k
    assert "Tax Day" in k[date(2027, 4, 15)] and len(P.build(2027)) == 48
    for start, first in (("sun", 6), ("mon", 0)):
        for m in range(1, 13):
            weeks = P._weeks(2027, m, start)
            assert all(wk[0].weekday() == first for wk in weeks)
            assert sum(d.month == m for wk in weeks for d in wk) == cal.monthrange(2027, m)[1]
    it = listings.BY_SLUG["2027-budget-planner"]
    assert it["dated"] and it["price"] == 12 and len(it["variants"]) * 2 <= 5
    assert "2027-budget-planner" not in listings.BY_SLUG["mega-budget-bundle"]["bundle"]


def test_seo_covers_every_listing():
    import seo
    assert set(seo.S) == set(listings.BY_SLUG)
    for it in listings.LISTINGS:
        assert len(it["title"].split()) <= 15 and it["title"] == seo.S[it["slug"]][0]
        assert it["attributes"]["Primary color"] and len(it["tags"]) == 13
        assert "Attributes" in listings.listing_md(it)
    assert "debt snowball" in listings.BY_SLUG["debt-free-date-planner"]["tags"]


def test_pod_posters_copy_and_layout():
    import sys as _s
    _s.path.insert(0, str(Path(__file__).resolve().parents[1] / "launch" / "pod"))
    import posters
    import build_pod
    assert len(posters.POSTERS) == 10 and len({p["slug"] for p in posters.POSTERS}) == 10
    for p in posters.POSTERS:
        assert len(p["title"]) <= 140 and len(p["title"].split()) <= 15
        assert len(p["tags"]) == 13 and len(set(p["tags"])) == 13 and all(len(t) <= 20 for t in p["tags"])
        d = posters.description(p)
        assert "production partner" in d and "not financial advice" in d and "AI" in d
        for k in posters.RATIOS:
            h = build_pod.poster_html(p, k)
            assert '<div class="chart">' in h and "please don't resell" not in h


def test_kdp_book_specs():
    import sys as _s
    _s.path.insert(0, str(Path(__file__).resolve().parents[1] / "launch" / "kdp"))
    import build_kdp as K
    for year in (2027, 2028):
        pages = K.interior_pages(year)
        assert len(pages) % 4 == 0 and 24 <= len(pages) <= 150
        assert not any("Etsy" in p or "resell" in p for p in pages)
    n = len(K.interior_pages(2027))
    w, h = K.cover_size(n)
    assert abs(w - (0.25 + 17 + n * 0.002252)) < 1e-3 and h == 11.25
    assert "Not financial" not in K.cover_html(2027, n) and "not financial advice" in K.cover_html(2027, n)
