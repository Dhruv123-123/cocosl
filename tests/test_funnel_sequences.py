"""Welcome sequence engine, sales pages, UTM attribution. Offline."""
import json
from datetime import datetime, timedelta, timezone
from email import message_from_bytes as _mfb
from email import policy
from pathlib import Path

import pytest

from contentfactory.funnel import analytics, attribution, linkpage, payments, salespage, sequences, store

SECRET = "whsec_test_secret"
BRAND = "money-made-simple"
BEFORE_LAUNCH_END = datetime(2026, 11, 10, 15, tzinfo=timezone.utc)
AFTER_LAUNCH_END = datetime(2026, 12, 1, 15, tzinfo=timezone.utc)


def msg_from(path):
    return _mfb(Path(path).read_bytes(), policy=policy.default)


@pytest.fixture(autouse=True)
def funnel_env(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "SUPPORT_EMAIL"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("FUNNEL_PUBLIC_URL", "https://links.example.com")
    monkeypatch.setenv("BUSINESS_ADDRESS", "123 Example St, Springfield, USA")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("GUMROAD_PING_SECRET", "gum-secret")


@pytest.fixture
def client(factory):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from contentfactory.funnel import routes
    routes.SUBSCRIBE_LIMITER.hits.clear()
    app = FastAPI()
    app.state.factory = factory
    app.include_router(routes.public_router)
    app.include_router(routes.router)
    app.dependency_overrides[routes.get_factory] = lambda: factory
    return TestClient(app)


def _sub(factory, email, confirmed_at=None, confirm=True, brand=BRAND):
    res = store.subscribe(factory.db, brand, email, source="test")
    if confirm:
        store.confirm(factory.db, res.subscriber["token"])
        if confirmed_at:
            factory.db.execute("UPDATE subscribers SET confirmed_at = ? WHERE id = ?",
                               [confirmed_at.replace(microsecond=0).isoformat(), res.subscriber["id"]])
    return factory.db.get("subscribers", res.subscriber["id"])


def _kinds(factory, sid):
    return [(r["kind"], r["status"]) for r in factory.db.query(
        "SELECT kind, status FROM emails_sent WHERE subscriber_id = ? AND kind LIKE 'sequence:%' ORDER BY id", [sid])]


# ------------------------------------------------------------------ sequence file
def test_money_made_simple_sequence_is_valid(factory):
    b = factory.brand(BRAND)
    seq = sequences.load_sequence(factory.settings, BRAND)
    assert [s.day_offset for s in seq.steps] == [0, 1, 2, 3, 4, 5, 6, 7, 9]
    assert sequences.validate_sequence(factory.settings, b) == []
    day7 = next(s for s in seq.steps if s.day_offset == 7)  # leads with the bundle, the $5 kit as the fallback
    assert seq.links[day7.cta_url_key] == "product:money-toolkit-bundle"
    assert "{link:bill_cut_page}" in day7.body_markdown and "$62" in day7.body_markdown
    assert linkpage.lead_magnet(b, factory.settings)["title"] == "The 7-Day Money Reset Checklist"
    checklist = linkpage.ensure_lead_magnet(factory.settings, b)
    assert len(checklist.sections) == 7 and checklist.sections[0].heading.startswith("Day 1")


def test_copy_rules(factory):
    """No hype phrases, AI + not-advice footer, affiliate disclosure next to the affiliate link."""
    b = factory.brand(BRAND)
    seq = sequences.load_sequence(factory.settings, BRAND)
    fake = {"id": 0, "token": "tok", "email": "x@example.com"}
    banned = [p.lower() for p in b.voice.banned_phrases] + ["guaranteed", "get rich", "testimonial"]
    for now in (BEFORE_LAUNCH_END, AFTER_LAUNCH_END):
        for step in seq.steps:
            r = sequences.render_step(factory.settings, b, seq, step, fake, base="https://links.example.com", now=now)
            low = r["text"].lower()
            assert not any(p in low for p in banned), step.day_offset
            assert "not financial advice" in low and "ai tools" in low
            assert "https://links.example.com/unsubscribe/tok" in r["text"] and "123 Example St" in r["text"]
            assert "{" not in r["subject"] + r["text"]
            if "/go/hysa" in r["text"]:
                assert "affiliate link" in low and "commission" in low
    day9 = seq.steps[-1]
    assert "/go/hysa" in sequences.render_step(factory.settings, b, seq, day9, fake, base="https://x.com",
                                               now=AFTER_LAUNCH_END)["text"]


def test_launch_price_only_while_true(factory):
    b = factory.brand(BRAND)
    seq = sequences.load_sequence(factory.settings, BRAND)
    fake = {"id": 0, "token": "tok", "email": "x@example.com"}
    d6, d9 = seq.steps[6], seq.steps[-1]
    during = sequences.render_step(factory.settings, b, seq, d6, fake, base="https://x.com", now=BEFORE_LAUNCH_END)
    after = sequences.render_step(factory.settings, b, seq, d6, fake, base="https://x.com", now=AFTER_LAUNCH_END)
    assert "$7" in during["text"] and "LAUNCH" in during["text"] and "November 14" in during["text"]
    assert "$7" not in after["text"] and "LAUNCH" not in after["text"] and "$12" in after["text"]
    s_during = sequences.render_step(factory.settings, b, seq, d9, fake, base="https://x.com", now=BEFORE_LAUNCH_END)
    s_after = sequences.render_step(factory.settings, b, seq, d9, fake, base="https://x.com", now=AFTER_LAUNCH_END)
    assert s_during["subject"].startswith("Launch price ends") and "Launch" not in s_after["subject"]


def test_links_carry_utm(factory):
    b = factory.brand(BRAND)
    seq = sequences.load_sequence(factory.settings, BRAND)
    r = sequences.render_step(factory.settings, b, seq, seq.steps[6], {"id": 1, "token": "tok", "email": "a@b.co"},
                              base="https://links.example.com", now=BEFORE_LAUNCH_END)
    page = [u for u in r["links"] if "/p/money-made-simple/20-minute-budget" in u]
    assert page and all("utm_source=welcome-sequence" in u and "utm_medium=email" in u
                        and "utm_campaign=welcome-d6" in u for u in page)
    d0 = sequences.render_step(factory.settings, b, seq, seq.steps[0], {"id": 1, "token": "tok", "email": "a@b.co"},
                               base="https://links.example.com", now=BEFORE_LAUNCH_END)
    assert "https://links.example.com/freebie/tok" in d0["text"]


def test_markdown_subset():
    html = sequences.markdown_to_html("Hi **you**.\n\n- one\n- [two](https://x.com/a?b=1&c=2)\n\n## Head\n\n1. a\n2. b")
    assert "<strong>you</strong>" in html and "<ul" in html and "<ol" in html and "<h2" in html
    assert 'href="https://x.com/a?b=1&amp;c=2"' in html
    assert "<script>" not in sequences.markdown_to_html("<script>alert(1)</script>")
    assert sequences.markdown_to_text("[two](https://x.com)") == "two (https://x.com)"


# ------------------------------------------------------------------ engine
def test_dry_run_sends_due_steps_once(factory):
    t0 = datetime(2026, 11, 8, 9, tzinfo=timezone.utc)
    a = _sub(factory, "a@example.com", confirmed_at=t0)
    _sub(factory, "pending@example.com", confirm=False)
    c = _sub(factory, "gone@example.com", confirmed_at=t0)
    store.unsubscribe(factory.db, c["token"])
    _sub(factory, "other@example.com", confirmed_at=t0, brand="tiny-histories")  # no sequence file

    r = sequences.run_sequences(factory, now=t0 + timedelta(minutes=30))
    assert r["mode"] == "dry_run" and r["dry_run"] == 1 and len(r["files"]) == 1
    msg = msg_from(r["files"][0])
    assert msg["To"] == "a@example.com" and msg["Subject"] == "Your 7-Day Money Reset is here"
    assert msg["List-Unsubscribe"] == f"<https://links.example.com/unsubscribe/{a['token']}>"
    assert msg["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    html = msg.get_body(("html",)).get_content()
    assert "123 Example St" in html and f"/unsubscribe/{a['token']}" in html and f"/freebie/{a['token']}" in html

    # same hour again: nothing new; next day: day 1 only
    assert sequences.run_sequences(factory, now=t0 + timedelta(hours=1))["dry_run"] == 0
    r = sequences.run_sequences(factory, now=t0 + timedelta(days=1, hours=1))
    assert r["dry_run"] == 1 and "Day 1" in msg_from(r["files"][0])["Subject"]
    assert _kinds(factory, a["id"]) == [("sequence:welcome:0", "dry_run"), ("sequence:welcome:1", "dry_run")]


def test_one_email_per_run_and_gap(factory):
    t0 = datetime(2026, 11, 1, 9, tzinfo=timezone.utc)
    a = _sub(factory, "a@example.com", confirmed_at=t0)
    now = t0 + timedelta(days=2, hours=1)  # day 0, 1 and 2 all due
    assert sequences.run_sequences(factory, now=now)["dry_run"] == 1
    assert sequences.run_sequences(factory, now=now + timedelta(hours=2))["dry_run"] == 0  # 20h gap
    assert sequences.run_sequences(factory, now=now + timedelta(hours=21))["dry_run"] == 1
    assert [k for k, _ in _kinds(factory, a["id"])] == ["sequence:welcome:0", "sequence:welcome:1"]


def test_stale_steps_are_skipped_not_burst(factory):
    t0 = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
    a = _sub(factory, "old@example.com", confirmed_at=t0)
    r = sequences.run_sequences(factory, now=t0 + timedelta(days=60))
    assert r["dry_run"] == 0 and r["skipped"] == 9
    assert {s for _, s in _kinds(factory, a["id"])} == {"dry_skipped"}
    # day 6 due 2 days ago (within max_late_days) is still sent, older ones skipped
    b = _sub(factory, "mid@example.com", confirmed_at=t0)
    r = sequences.run_sequences(factory, now=t0 + timedelta(days=8, hours=12))
    assert r["dry_run"] == 1 and "d06" in r["files"][0]
    assert ("sequence:welcome:5", "dry_skipped") in _kinds(factory, b["id"])


def test_live_send_needs_all_gates(factory, monkeypatch):
    from contentfactory.funnel import mailer
    from contentfactory.publish.base import MissingCredentials
    t0 = datetime(2026, 11, 8, 9, tzinfo=timezone.utc)
    a = _sub(factory, "a@example.com", confirmed_at=t0)
    now = t0 + timedelta(hours=1)
    # confirm=True but FACTORY_DRY_RUN on and no SMTP: falls back to a dry run with reasons
    r = sequences.run_sequences(factory, now=now, confirm=True)
    assert r["mode"] == "dry_run" and any("FACTORY_DRY_RUN" in x for x in r["blocked"])
    with pytest.raises((ValueError, MissingCredentials)):
        sequences.run_sequences(factory, now=now, confirm=True, strict=True)
    factory.settings.dry_run = False
    with pytest.raises(MissingCredentials):
        sequences.run_sequences(factory, now=now, confirm=True, strict=True)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_FROM", "Money <hi@example.com>")
    monkeypatch.delenv("BUSINESS_ADDRESS")
    assert sequences.run_sequences(factory, now=now, confirm=True)["mode"] == "dry_run"
    monkeypatch.setenv("BUSINESS_ADDRESS", "123 Example St, Springfield, USA")
    sent = []
    monkeypatch.setattr(mailer, "smtp_send", lambda cfg, msgs: [sent.append(m) or None for m in msgs])
    # an earlier dry run doesn't count as sent: the real day-0 email still goes out, once
    r = sequences.run_sequences(factory, now=now, confirm=True)
    assert r["mode"] == "send" and r["sent"] == 1 and sent[0]["To"] == "a@example.com"
    assert sequences.run_sequences(factory, now=now + timedelta(hours=1), confirm=True)["sent"] == 0
    assert ("sequence:welcome:0", "sent") in _kinds(factory, a["id"])
    # failures are retried, then given up on
    monkeypatch.setattr(mailer, "smtp_send", lambda cfg, msgs: ["SMTPError: boom" for _ in msgs])
    later = t0 + timedelta(days=1, hours=1)
    for i in range(4):
        sequences.run_sequences(factory, now=later + timedelta(minutes=i), confirm=True)
    assert [s for k, s in _kinds(factory, a["id"]) if k.endswith(":1")] == ["failed"] * 3
    status = sequences.sequence_status(factory, BRAND)
    assert status["steps"][0]["sent"] == 1 and status["confirmed"] == 1


def test_confirm_route_triggers_welcome_email(client, factory):
    client.post(f"/subscribe/{BRAND}", data={"email": "new@example.com"})
    token = factory.db.one("SELECT token FROM subscribers WHERE email = 'new@example.com'")["token"]
    assert client.get(f"/confirm/{token}").status_code == 200
    folder = factory.settings.output_dir / BRAND / "newsletter" / "sequences" / "welcome" / "dry-run"
    files = list(folder.glob("*-d00-*.eml"))
    assert len(files) == 1
    client.get(f"/confirm/{token}")  # second click: nothing new
    assert len(list(folder.glob("*.eml"))) == 1
    # confirmation email describes the welcome series honestly
    outbox = factory.settings.output_dir / BRAND / "newsletter" / "outbox"
    body = msg_from(next(outbox.glob("confirm-*.eml"))).get_body(("plain",)).get_content()
    assert "welcome series" in body


def test_preview_sequence(factory):
    paths = sequences.preview_sequence(factory, BRAND, now=BEFORE_LAUNCH_END)
    assert len(paths) == 9 and all(p.exists() and p.with_suffix(".eml").exists() for p in paths)
    store.ensure_schema(factory.db)
    assert factory.db.scalar("SELECT COUNT(*) FROM emails_sent") == 0


# ------------------------------------------------------------------ sales page
def test_sales_page_build(factory, monkeypatch):
    monkeypatch.setenv("SUPPORT_EMAIL", "help@example.com")
    b = factory.brand(BRAND)
    product = next(p for p in b.products if p.get("slug") == "20-minute-budget")
    path = salespage.build_sales_page(factory.settings, b, product)
    assert path == factory.settings.output_dir / BRAND / "site" / "20-minute-budget.html"
    html = salespage.render_sales_page(factory.settings, b, product, now=BEFORE_LAUNCH_END)
    for needle in ("A budget you set up once", "What's inside", "It's not for you if", "Questions",
                   "help@example.com within 14 days", "made with help from AI tools", "not financial",
                   "https://example.gumroad.com/l/budget/LAUNCH?utm_source=salespage", "$7", "<s>$12</s>",
                   'name="viewport"'):
        assert needle in html, needle
    assert "testimonial" not in html.lower() and "countdown" not in html.lower()
    after = salespage.render_sales_page(factory.settings, b, product, now=AFTER_LAUNCH_END)
    assert "LAUNCH" not in after and "$7" not in after and "Get it for $12" in after
    assert 'href="https://example.gumroad.com/l/budget?utm_source=salespage' in after


def test_sales_page_previews_and_defaults(factory, tmp_path):
    from PIL import Image
    img = tmp_path / "p1.png"
    Image.new("RGB", (1600, 1000), "white").save(img)
    b = factory.brand(BRAND)
    product = {"name": "Mystery Pack", "url": "https://buy.stripe.com/test_123", "price": 5}
    ctx = salespage.sales_page_context(factory.settings, b, product, utm={"utm_source": "email",
                                                                         "utm_campaign": "c1"})
    assert ctx["slug"] == "mystery-pack" and ctx["headline"] == "Mystery Pack" and ctx["previews"] == []
    assert "client_reference_id=email__salespage__c1" not in ctx["buy_url"]  # medium defaults to web
    assert "client_reference_id=email__web__c1" in ctx["buy_url"]
    assert salespage._image_src(factory.settings, str(img)).startswith("data:image/jpeg;base64,")


def test_sales_page_route(client, factory):
    r = client.get(f"/p/{BRAND}/20-minute-budget?utm_source=tiktok&utm_medium=bio&utm_campaign=launch")
    assert r.status_code == 200 and "utm_source=tiktok" in r.text and "utm_campaign=launch" in r.text
    assert client.get(f"/p/{BRAND}/nope").status_code == 404
    assert client.get("/p/unknown/20-minute-budget").status_code == 404


def test_link_page_links_sales_page_with_utm(client, factory):
    html = client.get(f"/l/{BRAND}").text
    assert ("https://links.example.com/p/money-made-simple/20-minute-budget?utm_source=linkpage&amp;utm_medium=bio"
            "&amp;utm_campaign=20-minute-budget") in html
    assert "https://links.example.com/go/hysa?s=linkpage&amp;utm_source=linkpage" in html
    assert "The 7-Day Money Reset Checklist" in html


# ------------------------------------------------------------------ attribution
def test_attribution_helpers():
    url = attribution.tag_link("https://buy.stripe.com/x", "email", "sequence", "welcome-d6")
    assert "utm_source=email" in url and "client_reference_id=email__sequence__welcome-d6" in url
    assert attribution.parse_client_reference("email__sequence__welcome-d6") == {
        "utm_source": "email", "utm_medium": "sequence", "utm_campaign": "welcome-d6"}
    assert attribution.with_utm("https://x.com/?utm_source=keep", "new") == "https://x.com/?utm_source=keep"
    assert attribution.utm_from_mapping({"url_params[utm_campaign]": "c", "url_params": '{"utm_source": "s"}'}) == {
        "utm_campaign": "c", "utm_source": "s"}
    note = "Gumroad: x" + attribution.note_suffix({"utm_source": "a b", "utm_campaign": "c"})
    assert attribution.parse_note(note) == {"utm_source": "a-b", "utm_campaign": "c"}


def _stripe(client, obj, etype="checkout.session.completed", eid="evt_1"):
    body = json.dumps({"id": eid, "type": etype, "created": 1_790_000_000, "data": {"object": obj}}).encode()
    return client.post("/webhooks/stripe", content=body,
                       headers={"Stripe-Signature": payments.stripe_test_header(body, SECRET)})


def test_webhooks_store_utm_and_stats_by_campaign(client, factory):
    # charge.succeeded (no metadata) first, then the checkout session that carries the UTM
    _stripe(client, {"id": "ch_1", "amount": 700, "currency": "usd", "paid": True, "status": "succeeded",
                     "payment_intent": "pi_1", "metadata": {}}, etype="charge.succeeded", eid="evt_0")
    r = _stripe(client, {"id": "cs_1", "amount_total": 700, "currency": "usd", "payment_status": "paid",
                         "payment_intent": "pi_1", "client_reference_id": "email__sequence__welcome-d6",
                         "metadata": {"brand": BRAND, "product": "Budget"}})
    assert r.status_code == 200
    rev = factory.db.one("SELECT * FROM revenue WHERE external_id = 'stripe:pi_1'")
    assert "utm_campaign=welcome-d6" in rev["note"] and rev["brand"] == BRAND
    _stripe(client, {"id": "cs_2", "amount_total": 1200, "currency": "usd", "payment_status": "paid",
                     "payment_intent": "pi_2", "metadata": {"brand": BRAND, "utm_source": "linkpage",
                                                           "utm_medium": "bio", "utm_campaign": "20-minute-budget"}},
            eid="evt_2")
    form = {"sale_id": "S1", "price": "700", "currency": "usd", "product_name": "Budget", "permalink": "budget",
            "url_params[utm_source]": "welcome-sequence", "url_params[utm_campaign]": "welcome-d6"}
    assert client.post("/webhooks/gumroad?secret=gum-secret", data=form).json()["recorded"] is True
    _stripe(client, {"id": "cs_3", "amount_total": 500, "currency": "usd", "payment_status": "paid",
                     "payment_intent": "pi_3", "metadata": {"brand": BRAND}}, eid="evt_3")
    stats = {s["brand"]: s for s in analytics.funnel_stats(factory.db, list(factory.brands()))}
    camps = {c["campaign"]: c for c in stats[BRAND]["campaigns"]}
    assert camps["welcome-d6"]["sales"] == 2 and camps["welcome-d6"]["revenue_cents"] == 1400
    assert camps["welcome-d6"]["source"] == "email, welcome-sequence"
    assert camps["20-minute-budget"]["revenue_cents"] == 1200 and camps["(none)"]["sales"] == 1
    assert stats[BRAND]["revenue_cents"] == 3100
    assert analytics.revenue_by_campaign(factory.db, BRAND)[0]["campaign"] == "welcome-d6"
