import json

import pytest

from contentfactory import review


def _imported(factory, fake_render, tmp_path, items):
    from contentfactory.cli import main
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(items))
    main(["--home", str(factory.settings.home), "import", str(pack), "--brand", "money-made-simple"])
    return [p["id"] for p in factory.db.query("SELECT id FROM posts ORDER BY id")]


def _item(title, **kw):
    return {"format": "short", "script": {"title": title, "hook": "h", "segments": [
        {"heading": "a", "narration": f"{title}: " + {"Plain one": "save the first ten dollars of every paycheck.",
         "Spanish one": "renters can ask the landlord to report rent to the bureaus.",
         "Tricky one": "an ITIN lets you file taxes without a Social Security number.",
         "Needs a read": "check your credit report free at the official site each week."}[title],
         "on_screen_text": "a", "visual_prompt": "x"}],
        "cta": "c", "caption": f"{title}. Made with AI tools.", "hashtags": ["money"], "description": "d",
        "thumbnail_text": "t", "sources": [], "claims_to_verify": []}, **kw}


def test_gate_blocks_until_reviews_pass(factory, fake_render, tmp_path):
    ids = _imported(factory, fake_render, tmp_path, [_item("Plain one"), _item("Spanish one", review="native_review"),
                                                     _item("Tricky one", review=["native", "legal"])])
    plain, native, both = ids
    st = lambda i: review.status(factory.db.get("posts", i), factory.brand("money-made-simple"))  # noqa: E731
    assert st(plain) == "draft" and st(native) == "native_review" and st(both) == "native_review"
    with pytest.raises(PermissionError, match="native review"):
        factory.approve(native)
    assert review.pass_stage(factory, native, "native_review", by="Ana") == "draft"
    factory.approve(native)
    assert st(native) == "approved"
    review.pass_stage(factory, both, "native_review")
    assert st(both) == "legal_review"
    with pytest.raises(PermissionError, match="legal review"):
        factory.approve(both)
    with pytest.raises(ValueError):
        review.pass_stage(factory, plain, "legal_review")
    # adding a review to an approved post sends it back to Review
    factory.approve(plain)
    review.require(factory, plain, "legal_review", note="ITIN claim")
    assert factory.db.get("posts", plain)["status"] == "in_review" and st(plain) == "legal_review"
    c = review.counts(factory)["money-made-simple"]
    assert c["approved"] == 1 and c["legal_review"] == 2
    review.send_back(factory, native)
    assert st(native) == "native_review" and factory.db.get("posts", native)["status"] == "in_review"


def test_brand_review_stages_and_export_week(factory, fake_render, tmp_path, monkeypatch):
    brand = factory.brand("money-made-simple")
    brand.review_stages = ["native_review"]
    monkeypatch.setattr(factory, "brand", lambda slug: brand)
    monkeypatch.setattr(factory, "brands", lambda: {"money-made-simple": brand})
    (pid,) = _imported(factory, fake_render, tmp_path, [_item("Needs a read")])
    assert review.status(factory.db.get("posts", pid), brand) == "native_review"
    with pytest.raises(PermissionError):
        factory.approve(pid)
    # a post that sneaks into the queue without approval never reaches export-week
    from datetime import date, datetime, time
    from zoneinfo import ZoneInfo

    from contentfactory import export_week as ew
    monday = date(2026, 11, 23)
    factory.db.update("posts", pid, {"status": "in_review"})
    factory.db.insert("publications", {"post_id": pid, "platform": "tiktok", "status": "queued",
                                       "scheduled_at": datetime.combine(monday, time(18), ZoneInfo("America/New_York")).isoformat()})
    assert ew.export(factory, "money-made-simple", monday) is None
