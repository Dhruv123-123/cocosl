from contentfactory.config import scoped_key


def test_brand_scoped_credentials_win_and_fall_back(factory, monkeypatch):
    monkeypatch.setenv("IG_ACCESS_TOKEN", "shared")
    monkeypatch.setenv("TINY_HISTORIES__IG_ACCESS_TOKEN", "th-own")
    assert scoped_key("tiny-histories", "IG_ACCESS_TOKEN") == "TINY_HISTORIES__IG_ACCESS_TOKEN"
    assert factory.settings.for_brand("tiny-histories").env("IG_ACCESS_TOKEN") == "th-own"
    assert factory.settings.for_brand("money-made-simple").env("IG_ACCESS_TOKEN") == "shared"
    assert factory.settings.env("IG_ACCESS_TOKEN") == "shared"
    th = factory.settings.for_brand("tiny-histories")
    assert th.env_key("IG_ACCESS_TOKEN") == "TINY_HISTORIES__IG_ACCESS_TOKEN"
    assert th.env_key("IG_TOKEN_EXPIRES_AT") == "IG_TOKEN_EXPIRES_AT"
    assert th.env_key("IG_TOKEN_EXPIRES_AT", write_scoped=True) == "TINY_HISTORIES__IG_TOKEN_EXPIRES_AT"


def test_publish_uses_each_brands_own_tokens(factory, fake_render, monkeypatch):
    from datetime import datetime, timedelta, timezone

    import contentfactory.publish as pubmod
    seen = []

    class P:
        def __init__(self, settings):
            self.settings = settings

        def publish(self, req):
            seen.append((req.brand.slug, self.settings.env("YT_REFRESH_TOKEN")))
            return type("R", (), {"remote_id": "x", "url": "u", "raw": {}})()

    monkeypatch.setattr(pubmod, "get_publisher", lambda platform, settings, dry_run=None: P(settings))
    monkeypatch.setenv("YT_REFRESH_TOKEN", "shared")
    monkeypatch.setenv("TINY_HISTORIES__YT_REFRESH_TOKEN", "th")
    monkeypatch.setattr("contentfactory.publish.tokens.refresh_long_lived", lambda s: None)
    for brand in ("money-made-simple", "tiny-histories"):
        idea = factory.ideas(brand, n=2, online=False)[0]
        pid = factory.produce(idea)
        factory.approve(pid)
        factory.schedule(pid, platforms=["youtube"])
    factory.settings.dry_run = False
    factory.publish_due(datetime.now(timezone.utc) + timedelta(days=30))
    assert sorted(seen) == [("money-made-simple", "shared"), ("tiny-histories", "th")]


def test_token_refresh_writes_back_to_the_brands_own_key(factory, monkeypatch):
    import time

    from contentfactory.publish import tokens
    monkeypatch.setenv("IG_API_HOST", "graph.instagram.com")
    monkeypatch.setenv("TINY_HISTORIES__IG_ACCESS_TOKEN", "old")
    monkeypatch.setenv("TINY_HISTORIES__IG_TOKEN_EXPIRES_AT", str(int(time.time()) + 60))
    monkeypatch.setattr("contentfactory.publish.oauth.instagram_login_refresh_token",
                        lambda tok, transport=None: {"access_token": "new", "expires_in": 5184000})
    done = tokens.refresh_long_lived(factory.settings.for_brand("tiny-histories"))
    assert done == ["instagram"]
    env = (factory.settings.home / ".env").read_text()
    assert "TINY_HISTORIES__IG_ACCESS_TOKEN=new" in env and "\nIG_ACCESS_TOKEN=" not in "\n" + env
