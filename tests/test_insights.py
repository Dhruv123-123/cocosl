"""Learning from metrics: compare each post to its own platform's median."""
from datetime import datetime, timedelta, timezone

from contentfactory.insights import score_multipliers, winners_prompt

BRAND = "money-made-simple"


def _published(db, title, fmt, pillar, platform, views, days_ago=10):
    idea = db.insert("ideas", {"brand": BRAND, "title": title, "angle": "a", "format": fmt, "pillar": pillar})
    post = db.insert("posts", {"brand": BRAND, "idea_id": idea, "format": fmt, "status": "published", "title": title,
                               "script": {}})
    at = (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(microsecond=0).isoformat()
    pub = db.insert("publications", {"post_id": post, "platform": platform, "status": "published",
                                     "scheduled_at": at, "published_at": at})
    db.insert("metrics", {"publication_id": pub, "captured_at": at, "views": views, "created_at": at})
    return post


def test_platform_normalised_multipliers_and_prompt(factory):
    db = factory.db
    # TikTok numbers are 10x YouTube's; carousels on Instagram are the real winners for their platform.
    for i, v in enumerate([10_000, 11_000, 9_000]):
        _published(db, f"TikTok short {i}", "short", "budgeting", "tiktok", v)
    for i, v in enumerate([300, 1_000, 1_200]):
        _published(db, f"Carousel {i}", "carousel", "credit", "instagram", v)
    for i, v in enumerate([900, 1_000, 1_100]):
        _published(db, f"YouTube short {i}", "short", "budgeting", "youtube", v)
    mult = score_multipliers(db, BRAND)
    # Raw averages would crown TikTok shorts; per-platform, nothing is far from typical except the 300-view flop.
    assert 0.6 < mult["format"]["short"] < 1.4 and 0.5 <= mult["format"]["carousel"] <= 1.4
    _published(db, "Brand new", "short", "budgeting", "youtube", 5, days_ago=0)
    text = winners_prompt(db, BRAND)
    assert text.startswith("How past posts did") and "Brand new" not in text  # still settling
    assert "Underperformed:" in text and "Carousel 0" in text.split("Underperformed:")[1]
    assert winners_prompt(db, "nobody") == ""
