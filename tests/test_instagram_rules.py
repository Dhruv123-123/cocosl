from datetime import datetime, timedelta, timezone

import pytest

from contentfactory.guardrails import check_no_repost
from contentfactory.publish._text import pick_hashtags


def test_pick_hashtags_keeps_topic_and_brand():
    tags = ["history", "tinyhistories", "didyouknow", "fork", "foodhistory", "tablemanners", "medievalhistory"]
    out = pick_hashtags(tags, 5, "tinyhistories")
    assert len(out) == 5 and "didyouknow" not in out and out[-1] == "tinyhistories"
    assert pick_hashtags(["a", "b"], 5) == ["a", "b"]


def test_instagram_caption_has_at_most_5_hashtags(factory):
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "carousel", "status": "approved",
                                      "title": "t", "caption": "Body.", "script": {}, "disclosure": "",
                                      "hashtags": ["budgetingtips", "checkingaccount", "overdraftfees", "moneysystems",
                                                   "paydayroutine", "personalfinance20s", "moneymadesimple"],
                                      "meta": {}, "assets": {}})
    post = factory.db.get("posts", pid)
    ig = factory.build_request(post, "instagram").caption
    assert ig.count("#") == 5 and "#moneymadesimple" in ig and "#paydayroutine" not in ig
    assert factory.build_request(post, "facebook").caption.count("#") == 7
    from contentfactory.publish.instagram import HASHTAG_MAX
    assert HASHTAG_MAX == 5


def _post(f, text, status="approved"):
    return f.db.insert("posts", {"brand": "money-made-simple", "format": "carousel", "status": status, "title": text[:20],
                                 "caption": "", "script": {"title": text, "segments": [{"narration": text}]},
                                 "hashtags": [], "disclosure": "", "meta": {}, "assets": {"slides": ["x.png"]}})


def test_never_repost_on_instagram(factory):
    text = "The sinking fund method: name the bill, divide by the months left, automate it on payday every month."
    a = _post(factory, text, status="published")
    factory.db.insert("publications", {"post_id": a, "platform": "instagram", "status": "published",
                                       "scheduled_at": datetime.now(timezone.utc).isoformat()})
    b = _post(factory, text)  # same script, new post id
    rp = check_no_repost(factory.db, factory.db.get("posts", b), "instagram")
    assert rp.level == "block" and f"#{a}" in rp.message
    assert check_no_repost(factory.db, factory.db.get("posts", b), "youtube").level == "ok"
    rp = check_no_repost(factory.db, factory.db.get("posts", a), "instagram")
    assert rp.level == "block" and "already on instagram" in rp.message
    c = _post(factory, "A completely different idea about checking account overdraft buffers and alerts.")
    assert check_no_repost(factory.db, factory.db.get("posts", c), "instagram").level == "ok"


def test_schedule_skips_or_refuses_instagram_repost(factory, monkeypatch):
    monkeypatch.setattr("contentfactory.publish.preflight.check_post", lambda *a, **k: [])
    text = "Sinking funds turn surprise bills into boring line items you saw coming months ago."
    a = _post(factory, text, status="published")
    factory.db.insert("publications", {"post_id": a, "platform": "instagram", "status": "published",
                                       "scheduled_at": datetime.now(timezone.utc).isoformat()})
    b = _post(factory, text)
    with pytest.raises(ValueError, match="instagram"):
        factory.schedule(b, ["instagram"])
    ids = factory.schedule(b)  # automatic: Instagram dropped, the rest scheduled
    plats = {factory.db.get("publications", i)["platform"] for i in ids}
    assert "instagram" not in plats and plats


def test_publish_due_cancels_a_repost(factory):
    text = "Pay yourself first: move savings out on payday before the money has a chance to disappear."
    a = _post(factory, text, status="published")
    factory.db.insert("publications", {"post_id": a, "platform": "instagram", "status": "published",
                                       "scheduled_at": datetime.now(timezone.utc).isoformat()})
    b = _post(factory, text, status="scheduled")
    pub = factory.db.insert("publications", {"post_id": b, "platform": "instagram", "status": "queued",
                                             "scheduled_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()})
    res = factory.publish_due()
    assert res[0]["status"] == "cancelled" and factory.db.get("publications", pub)["status"] == "cancelled"
