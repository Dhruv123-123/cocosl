import pytest

from contentfactory.scaffold import create, remove


def test_scaffold_rent_smart_then_remove(factory):
    home = factory.settings.home
    made = create(home, "rent-smart", "Rent Smart", "money for renters", "renters in their 20s and 30s",
                  "America/Chicago")
    assert made["brand"].exists() and (home / "voice/rent-smart/README.txt").exists()
    brand = factory.brands()["rent-smart"]
    assert brand.name == "Rent Smart" and brand.require_human_review
    assert brand.cadence.max_posts_per_day_per_platform == 1
    import json
    samples = json.loads(made["samples"].read_text())
    assert [s["format"] for s in samples] == ["short", "carousel", "long"]
    assert samples[2]["script"]["original_element"]
    with pytest.raises(FileExistsError):
        create(home, "rent-smart")
    with pytest.raises(ValueError):
        create(home, "Rent Smart")
    pid = factory.import_script("rent-smart", samples[0]["script"], "short", "", "", render=False)
    gone = remove(factory, "rent-smart")
    assert made["brand"] in gone and not (home / "voice/rent-smart").exists()
    assert "rent-smart" not in factory.brands()
    assert factory.db.one("SELECT status FROM posts WHERE id = ?", [pid])["status"] == "rejected"


def test_remove_refuses_live_brand(factory):
    create(factory.settings.home, "rent-smart")
    pid = factory.db.insert("posts", {"brand": "rent-smart", "format": "short", "status": "scheduled", "title": "x",
                                      "caption": "", "script": {}, "hashtags": [], "disclosure": "", "meta": {},
                                      "assets": {}})
    factory.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "queued",
                                       "scheduled_at": "2030-01-01T00:00:00+00:00"})
    with pytest.raises(PermissionError):
        remove(factory, "rent-smart")
