"""Funnel: double opt-in, unsubscribe, honeypot, rate limit, Stripe/Gumroad
webhooks, digest dry runs, link page disclosures and analytics. Offline."""
import json
import time
from email import message_from_bytes as _mfb
from email import policy


def message_from_bytes(data):
    return _mfb(data, policy=policy.default)
from pathlib import Path

import pytest

from contentfactory.db import now_iso
from contentfactory.funnel import analytics, linkpage, newsletter, payments, store

SECRET = "whsec_test_secret"


@pytest.fixture(autouse=True)
def funnel_env(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "FUNNEL_TRUST_PROXY",
                "STRIPE_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("FUNNEL_PUBLIC_URL", "https://links.example.com")
    monkeypatch.setenv("BUSINESS_ADDRESS", "123 Example St, Springfield, USA")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("GUMROAD_PING_SECRET", "gum-secret")


@pytest.fixture
def client(factory):
    try:
        from fastapi.testclient import TestClient

        from contentfactory.funnel.routes import get_factory, public_router, router
    except ImportError as e:  # pragma: no cover
        pytest.skip(f"web stack unavailable: {e}")
    from fastapi import FastAPI
    from contentfactory.funnel import routes
    routes.SUBSCRIBE_LIMITER.hits.clear()
    app = FastAPI()
    app.state.factory = factory
    app.include_router(public_router)
    app.include_router(router)
    app.dependency_overrides[get_factory] = lambda: factory
    return TestClient(app)


def _published_post(factory, brand="money-made-simple", title="How a HYSA works", url="https://youtu.be/abc",
                    views=1000):
    pid = factory.db.insert("posts", {"brand": brand, "format": "short", "status": "published", "title": title,
                                      "caption": "Your emergency fund deserves interest. Here's how to pick one."})
    pub = factory.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "published",
                                             "url": url, "published_at": now_iso()})
    factory.db.insert("metrics", {"publication_id": pub, "captured_at": now_iso(), "views": views})
    return pid


def _confirm_token(factory, email, brand="money-made-simple"):
    return factory.db.one("SELECT token FROM subscribers WHERE email = ? AND brand = ?", [email, brand])["token"]


# ------------------------------------------------------------------ store
def test_email_validation():
    assert store.normalize_email("  Ann@Example.COM ") == "Ann@example.com"
    for bad in ["", "nope", "a@b", "a@@b.com", "a b@c.com", "a@b..com", "x@localhost", "a@1.2"]:
        with pytest.raises(store.SubscribeError):
            store.normalize_email(bad)


def test_rate_limiter():
    rl = store.RateLimiter(limit=2, window=60)
    assert rl.allow("1.2.3.4") and rl.allow("1.2.3.4")
    assert not rl.allow("1.2.3.4")
    assert rl.allow("5.6.7.8")


# ------------------------------------------------------------------ routes
def test_double_opt_in_flow(client, factory):
    r = client.post("/subscribe/money-made-simple", data={"email": "reader@example.com", "website": ""})
    assert r.status_code == 200 and "Check your inbox" in r.text
    row = factory.db.one("SELECT * FROM subscribers WHERE email = 'reader@example.com'")
    assert row["status"] == "pending" and row["token"]
    # confirmation email written as .eml (no SMTP), with confirm + unsubscribe links
    outbox = factory.settings.output_dir / "money-made-simple" / "newsletter" / "outbox"
    emls = list(outbox.glob("confirm-*.eml"))
    assert len(emls) == 1
    msg = message_from_bytes(emls[0].read_bytes())
    body = msg.get_body(("plain",)).get_content()
    assert f"https://links.example.com/confirm/{row['token']}" in body
    assert f"/unsubscribe/{row['token']}" in msg["List-Unsubscribe"]
    # confirm -> lead magnet download
    r = client.get(f"/confirm/{row['token']}")
    assert r.status_code == 200 and "Download your free guide" in r.text
    assert factory.db.one("SELECT status FROM subscribers WHERE id = ?", [row["id"]])["status"] == "confirmed"
    r = client.get(f"/freebie/{row['token']}")
    assert r.status_code == 200 and "Checklist" in r.text
    # re-subscribing a confirmed address changes nothing and sends nothing
    client.post("/subscribe/money-made-simple", data={"email": "reader@example.com"})
    assert len(list(outbox.glob("confirm-*.eml"))) == 1


def test_freebie_locked_until_confirmed(client, factory):
    client.post("/subscribe/money-made-simple", data={"email": "p@example.com"})
    assert client.get(f"/freebie/{_confirm_token(factory, 'p@example.com')}").status_code == 403
    assert client.get("/confirm/not-a-token").status_code == 404


def test_unsubscribe(client, factory):
    client.post("/subscribe/money-made-simple", data={"email": "bye@example.com"})
    token = _confirm_token(factory, "bye@example.com")
    client.get(f"/confirm/{token}")
    r = client.get(f"/unsubscribe/{token}")  # GET only shows the button
    assert r.status_code == 200 and "Unsubscribe?" in r.text
    assert factory.db.one("SELECT status FROM subscribers WHERE token = ?", [token])["status"] == "confirmed"
    r = client.post(f"/unsubscribe/{token}")
    assert r.status_code == 200 and "unsubscribed" in r.text
    assert factory.db.one("SELECT status FROM subscribers WHERE token = ?", [token])["status"] == "unsubscribed"
    assert client.get(f"/confirm/{token}").status_code == 404  # can't re-confirm with an old link


def test_honeypot_drops_bots(client, factory):
    r = client.post("/subscribe/money-made-simple", data={"email": "bot@example.com", "website": "http://spam"})
    assert r.status_code == 200 and "Check your inbox" in r.text  # bot sees the normal page
    store.ensure_schema(factory.db)
    assert factory.db.scalar("SELECT COUNT(*) FROM subscribers") == 0


def test_invalid_email_and_rate_limit(client, factory):
    assert client.post("/subscribe/money-made-simple", data={"email": "nope"}).status_code == 400
    codes = [client.post("/subscribe/money-made-simple", data={"email": f"u{i}@example.com"}).status_code
             for i in range(6)]
    assert 429 in codes
    assert client.post("/subscribe/unknown-brand", data={"email": "a@example.com"}).status_code == 404


def test_link_page_route_and_static_build(client, factory):
    _published_post(factory)
    r = client.get("/l/money-made-simple")
    assert r.status_code == 200
    for needle in ("I may earn a commission", "AI-assisted", factory.brand("money-made-simple").ai_disclosure,
                   'action="https://links.example.com/subscribe/money-made-simple"', "https://links.example.com/go/hysa",
                   'name="website"', "How a HYSA works", "The 20-Minute Budget"):
        assert needle in r.text, needle
    path = linkpage.build_link_page(factory.settings, factory.brand("money-made-simple"), db=factory.db)
    assert path == factory.settings.output_dir / "money-made-simple" / "site" / "index.html"
    html = path.read_text()
    assert "I may earn a commission" in html and "<script" not in html and "http://" not in html.replace(
        "http://www.w3", "")
    assert factory.db.one("SELECT * FROM affiliate_links WHERE slug = 'hysa'")["brand"] == "money-made-simple"


def test_admin_pages_render(client, factory):
    if not Path(linkpage.__file__).parents[1].joinpath("web", "templates", "base.html").exists():
        pytest.skip("dashboard templates not installed")
    _published_post(factory)
    assert client.get("/funnel").status_code == 200
    r = client.post("/funnel/money-made-simple/digest", data={"days": "7"}, follow_redirects=False)
    assert r.status_code == 303
    page = client.get(r.headers["location"])
    assert page.status_code == 200 and "Dry run" in page.text
    assert client.get("/funnel/money-made-simple/subscribers").status_code == 200
    assert client.get("/funnel/money-made-simple/export.csv").text.startswith("email,")


# ------------------------------------------------------------------ stripe
def _event(eid="evt_1", pi="pi_1", amount=1200, etype="checkout.session.completed"):
    obj = {"id": "cs_1", "object": "checkout.session", "amount_total": amount, "currency": "usd",
           "payment_status": "paid", "payment_intent": pi, "created": 1_790_000_000,
           "metadata": {"brand": "money-made-simple", "product": "Budget template"}}
    if etype == "charge.succeeded":
        obj = {"id": "ch_1", "object": "charge", "amount": amount, "currency": "usd", "paid": True,
               "status": "succeeded", "payment_intent": pi, "created": 1_790_000_000, "metadata": {}}
    return json.dumps({"id": eid, "type": etype, "created": 1_790_000_000, "data": {"object": obj}}).encode()


def test_stripe_signature_verify():
    body = _event()
    now = 1_800_000_000
    good = payments.stripe_test_header(body, SECRET, now)
    assert payments.verify_stripe_signature(body, good, SECRET, now=now + 10) == now
    # multiple signatures (secret rotation) and a v0 scheme are tolerated
    assert payments.verify_stripe_signature(body, f"t={now},v0=abc,v1=deadbeef,{good.split(',')[1]}", SECRET,
                                            now=now)
    with pytest.raises(payments.SignatureError):
        payments.verify_stripe_signature(body, f"t={now},v1={'0' * 64}", SECRET, now=now)
    with pytest.raises(payments.SignatureError):
        payments.verify_stripe_signature(body + b" ", good, SECRET, now=now)  # tampered body
    with pytest.raises(payments.SignatureError):
        payments.verify_stripe_signature(body, good, SECRET, now=now + 301)  # stale timestamp
    with pytest.raises(payments.SignatureError):
        payments.verify_stripe_signature(body, f"t={now},v0={payments.stripe_signature(body, SECRET, now)}",
                                         SECRET, now=now)  # only v1 counts
    with pytest.raises(payments.SignatureError):
        payments.verify_stripe_signature(body, good, "", now=now)


def test_stripe_webhook_records_and_dedupes(client, factory):
    body = _event()
    r = client.post("/webhooks/stripe", content=body,
                    headers={"Stripe-Signature": payments.stripe_test_header(body, SECRET)})
    assert r.status_code == 200 and r.json()["recorded"] is True
    rev = factory.db.one("SELECT * FROM revenue")
    assert rev["amount_cents"] == 1200 and rev["source"] == "product" and rev["brand"] == "money-made-simple"
    # same delivery again, and the matching charge.succeeded event: no double count
    for b in (body, _event(eid="evt_2", etype="charge.succeeded")):
        r = client.post("/webhooks/stripe", content=b,
                        headers={"Stripe-Signature": payments.stripe_test_header(b, SECRET)})
        assert r.status_code == 200 and r.json()["recorded"] is False
    assert factory.db.scalar("SELECT COUNT(*) FROM revenue") == 1
    # bad and stale signatures are rejected
    assert client.post("/webhooks/stripe", content=body, headers={"Stripe-Signature": "t=1,v1=00"}).status_code == 400
    stale = payments.stripe_test_header(body, SECRET, int(time.time()) - 3600)
    assert client.post("/webhooks/stripe", content=body, headers={"Stripe-Signature": stale}).status_code == 400


def test_stripe_ignores_unpaid_and_other_events(factory):
    ev = json.loads(_event())
    ev["data"]["object"]["payment_status"] = "unpaid"
    assert payments.handle_stripe_event(factory.db, ev)["recorded"] is False
    assert payments.handle_stripe_event(factory.db, {"type": "customer.created", "data": {"object": {}}})[
        "recorded"] is False


def test_gumroad_ping(client, factory):
    form = {"sale_id": "S1", "price": "1200", "currency": "usd", "product_name": "Budget",
            "permalink": "budget", "refunded": "false", "test": "false"}
    assert client.post("/webhooks/gumroad", data=form).status_code == 403
    assert client.post("/webhooks/gumroad?secret=wrong", data=form).status_code == 403
    r = client.post("/webhooks/gumroad?secret=gum-secret", data=form)
    assert r.status_code == 200 and r.json()["recorded"] is True
    assert client.post("/webhooks/gumroad?secret=gum-secret", data=form).json()["recorded"] is False
    rev = factory.db.one("SELECT * FROM revenue WHERE external_id = 'gumroad:S1'")
    assert rev["amount_cents"] == 1200 and rev["brand"] == "money-made-simple"
    assert client.post("/webhooks/gumroad?secret=gum-secret", data={**form, "sale_id": "S2", "test": "true"}).json()[
        "recorded"] is False


def test_payment_link_needs_key():
    from contentfactory.publish.base import MissingCredentials
    with pytest.raises(MissingCredentials):
        payments.stripe_payment_link({"name": "Guide", "price": 9})


def test_payment_link_calls_stripe(monkeypatch):
    import httpx
    calls = []

    def handler(request: httpx.Request):
        calls.append((request.url.path, dict(httpx.QueryParams(request.content.decode()))))
        if request.url.path == "/v1/prices":
            return httpx.Response(200, json={"id": "price_1"})
        return httpx.Response(200, json={"id": "plink_1", "url": "https://buy.stripe.com/test_1"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    url = payments.stripe_payment_link({"name": "Guide", "price": 9.5}, brand="b", api_key="sk_test", client=client)
    assert url == "https://buy.stripe.com/test_1"
    assert calls[0][1]["unit_amount"] == "950" and calls[1][1]["line_items[0][price]"] == "price_1"
    assert calls[1][1]["metadata[brand]"] == "b"


# ------------------------------------------------------------------ digest
def _sub(factory, email, confirm=True, brand="money-made-simple"):
    res = store.subscribe(factory.db, brand, email, source="test")
    if confirm:
        store.confirm(factory.db, res.subscriber["token"])
    return res.subscriber


def test_digest_dry_run_only_confirmed(factory):
    _published_post(factory)
    a = _sub(factory, "a@example.com")
    _sub(factory, "b@example.com", confirm=False)
    c = _sub(factory, "c@example.com")
    store.unsubscribe(factory.db, c["token"])
    _sub(factory, "other@example.com", brand="tiny-histories")
    draft_id = newsletter.draft_digest(factory, "money-made-simple")
    draft = newsletter.get_draft(factory.db, draft_id)
    assert "How a HYSA works" in draft["html"] and draft["status"] == "draft"
    assert "I may earn a commission" in draft["html"] or "my own product" in draft["html"]
    result = newsletter.send_digest(factory, draft_id)  # default: dry run
    assert result["mode"] == "dry_run" and len(result["files"]) == 1
    eml = Path(result["files"][0])
    assert eml.suffix == ".eml" and "a@example.com" in eml.name
    msg = message_from_bytes(eml.read_bytes())
    assert msg["To"] == "a@example.com"
    text = msg.get_body(("plain",)).get_content()
    html = msg.get_body(("html",)).get_content()
    assert f"https://links.example.com/unsubscribe/{a['token']}" in text
    assert f"https://links.example.com/unsubscribe/{a['token']}" in html
    assert "123 Example St" in text and "123 Example St" in html
    assert msg["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    assert newsletter.get_draft(factory.db, draft_id)["status"] == "draft"


def test_send_for_real_requires_smtp_and_address(factory, monkeypatch):
    from contentfactory.publish.base import MissingCredentials
    draft_id = newsletter.draft_digest(factory, "money-made-simple")
    with pytest.raises(MissingCredentials):
        newsletter.send_digest(factory, draft_id, confirm=True)
    monkeypatch.delenv("BUSINESS_ADDRESS")
    with pytest.raises(ValueError):
        newsletter.send_digest(factory, draft_id, confirm=True)


def test_send_for_real_uses_smtp(factory, monkeypatch):
    from contentfactory.funnel import mailer
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_FROM", "News <news@example.com>")
    sent = []
    monkeypatch.setattr(mailer, "smtp_send", lambda cfg, msgs: [sent.append(m) or None for m in msgs])
    _sub(factory, "a@example.com")
    _sub(factory, "b@example.com")
    draft_id = newsletter.draft_digest(factory, "money-made-simple")
    r = newsletter.send_digest(factory, draft_id, confirm=True)
    assert r["sent"] == 2 and len(sent) == 2
    again = newsletter.send_digest(factory, draft_id, confirm=True)  # idempotent
    assert again["sent"] == 0 and again["skipped_already_sent"] == 2
    assert newsletter.get_draft(factory.db, draft_id)["status"] == "sent"


def test_export_csv_confirmed_only(factory):
    _sub(factory, "a@example.com")
    _sub(factory, "b@example.com", confirm=False)
    path = newsletter.export_subscribers_csv(factory, "money-made-simple")
    lines = path.read_text().strip().splitlines()
    assert lines[0].startswith("email,") and len(lines) == 2 and lines[1].startswith("a@example.com")


# ------------------------------------------------------------------ analytics
def test_funnel_stats(factory):
    _published_post(factory, views=2000)
    linkpage.sync_affiliate_links(factory.db, factory.brand("money-made-simple"))
    factory.db.execute("UPDATE affiliate_links SET clicks = 40 WHERE slug = 'hysa'")
    _sub(factory, "a@example.com")
    _sub(factory, "b@example.com")
    payments.handle_stripe_event(factory.db, json.loads(_event()))
    stats = {s["brand"]: s for s in analytics.funnel_stats(factory.db, list(factory.brands()))}
    s = stats["money-made-simple"]
    assert (s["views"], s["link_clicks"], s["subscribers"], s["sales"], s["revenue_cents"]) == (2000, 40, 2, 1, 1200)
    assert s["click_rate"] == 2.0 and s["signup_rate"] == 5.0 and s["sale_rate"] == 50.0
    assert stats["tiny-histories"]["views"] == 0
