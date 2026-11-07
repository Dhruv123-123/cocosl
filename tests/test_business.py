"""Business side: pricing, CRM/orders, ad-script guard, pitches, invoices,
CSV imports, reports, affiliates and the /business pages. All offline."""
from __future__ import annotations

import email
import importlib.util
from datetime import date

import pytest

from contentfactory.business import affiliates, invoices, pitch, products, revenue, ugc
from contentfactory.business._util import parse_date, to_cents
from contentfactory.db import now_iso
from contentfactory.schemas import AdScript, Segment


@pytest.fixture
def db(factory):
    return factory.db


@pytest.fixture(autouse=True)
def no_pdf(monkeypatch):
    monkeypatch.setenv("FACTORY_PDF", "0")


# --------------------------------------------------------------------------- helpers
def test_money_and_date_parsing():
    assert to_cents("$1,234.56") == 123456
    assert to_cents("(12.00)") == -1200
    assert to_cents("1.234,50") == 123450
    assert to_cents(12.5) == 1250
    assert parse_date("03/15/2026") == "2026-03-15"
    assert parse_date("Mar 15, 2026") == "2026-03-15"
    assert parse_date("2026-03-15T10:00:00Z") == "2026-03-15"


# --------------------------------------------------------------------------- pricing & orders
def test_quote_pricing():
    q = ugc.quote("starter")
    assert q["total_cents"] == ugc.PACKAGES["starter"].price_cents
    q = ugc.quote("growth", ["extra_hook", "paid_usage_90d"], rush=True)
    growth = ugc.PACKAGES["growth"]
    expected = growth.price_cents + growth.videos * 2_500 + 10_000 + 7_500
    assert q["total_cents"] == expected
    assert q["turnaround_days"] == growth.turnaround_days // 2
    assert sum(i["amount_cents"] for i in q["items"]) == q["total_cents"]
    with pytest.raises(KeyError):
        ugc.quote("platinum")


def test_client_pipeline_and_orders(db):
    cid = ugc.add_client(db, "Glow Co", email="hi@glow.example", website="https://glow.example", niche="skincare")
    assert ugc.add_client(db, "Glow duplicate", email="HI@glow.example") == cid
    ugc.set_client_status(db, cid, "contacted", note="sent intro")
    client = ugc.get_client(db, cid)
    assert client["status"] == "contacted" and "sent intro" in client["notes"]
    assert client["meta"]["next_follow_up"] > date.today().isoformat()
    ugc.set_follow_up(db, cid, "2000-01-01")
    assert [c["id"] for c in ugc.due_follow_ups(db)] == [cid]
    with pytest.raises(ValueError):
        ugc.set_client_status(db, cid, "ghosted")
    assert cid in [c["id"] for c in ugc.pipeline(db)["contacted"]]

    oid = ugc.create_order(db, cid, "starter", addons=["raw_files"])
    order = ugc.get_order(db, oid)
    assert order["price_cents"] == ugc.PACKAGES["starter"].price_cents + 7_500 and order["status"] == "brief"
    with pytest.raises(ValueError):
        ugc.set_order_status(db, oid, "delivered")  # must go through production first
    for st in ("in_production", "delivered", "revision", "delivered"):
        ugc.set_order_status(db, oid, st)
    ugc.set_order_status(db, oid, "paid")
    assert ugc.get_order(db, oid)["status"] == "paid"
    rev = db.query("SELECT * FROM revenue WHERE client_id = ?", [cid])
    assert len(rev) == 1 and rev[0]["amount_cents"] == ugc.PACKAGES["starter"].price_cents + 7_500 and rev[0]["source"] == "ugc"
    assert ugc.get_client(db, cid)["status"] == "won"


# --------------------------------------------------------------------------- ad scripts
class FakeLLM:
    """Returns queued AdScripts regardless of prompt."""
    provider = "fake"

    def __init__(self, *scripts):
        self.scripts = list(scripts)
        self.calls = 0

    def structured(self, schema, *, system, prompt, offline, purpose="", max_tokens=0):
        self.calls += 1
        return self.scripts.pop(0) if len(self.scripts) > 1 else self.scripts[0]


def _ad(narration: str) -> AdScript:
    seg = Segment(heading="Hook", narration=narration, on_screen_text="Meet Glow", visual_prompt="product")
    return AdScript(concept="c", hook=narration, segments=[seg], cta="Shop now",
                    on_screen_disclosure="AI-generated presenter. Paid ad.", variations=["Try it"])


def test_offline_ad_script_is_clean(factory):
    ad = ugc.write_ad_script(factory.llm, {"product": "Glow Serum", "brand_name": "Glow Co",
                                           "benefits": ["lightweight daily hydration"]})
    assert all(c.level != "block" for c in ugc.check_ad_script(ad))
    assert "AI" in ad.on_screen_disclosure


def test_testimonial_is_caught_and_raises():
    bad = _ad("I've been using Glow Serum for a month and it changed my life.")
    llm = FakeLLM(bad)
    with pytest.raises(ugc.TestimonialError):
        ugc.write_ad_script(llm, {"product": "Glow Serum"})
    assert llm.calls == 2  # original + one revision attempt


def test_testimonial_is_revised():
    bad = _ad("I tried this serum and my skin loves it.")
    good = _ad("Here's how Glow Serum fits into a two-minute routine.")
    ad = ugc.write_ad_script(FakeLLM(bad, good), {"product": "Glow Serum"})
    assert ad.hook.startswith("Here's how")


def test_render_ad_builds_post_dict(factory):
    ad = ugc.write_ad_script(factory.llm, {"product": "Glow Serum", "brand_name": "Glow Co"})
    post = ugc.render_ad(factory.settings, {"name": "Glow Co", "palette": ["#111111", "#ffffff", "#ff66aa", "#ffcc00"]},
                         ad, order_id=3, variation=1)
    assert post["format"] == "short" and post["meta"]["ai_presenter"] and post["meta"]["sponsored"]
    assert post["script"]["hook"] == ad.variations[1]
    assert ad.on_screen_disclosure in post["script"]["segments"][0]["on_screen_text"]
    assert post["meta"]["brand_profile"]["visual"]["palette"][2] == "#ff66aa"


# --------------------------------------------------------------------------- pitches
def test_pitch_drafts_and_export(factory, tmp_path):
    db = factory.db
    csv_text = ("name,website,email,niche\nGlow Co,https://glow.example,hi@glow.example,skincare\n"
                "Bad Row,https://bad.example,not-an-email,pets\nGlow again,glow.example,,skincare\n"
                "Fit Gear,https://fit.example,team@fit.example,fitness\n")
    res = pitch.import_leads_csv(db, csv_text)
    assert res["added"] == 2 and res["duplicates"] == 1 and len(res["errors"]) == 1
    sender = {"name": "Dhruv", "business_name": "Studio D", "email": "d@studio.example"}
    ids = pitch.draft_all(db, factory.llm, sender)
    assert len(ids) == 2
    client = ugc.get_client(db, ids[0])
    draft = pitch.latest_draft(client)
    assert pitch.OPT_OUT_LINE in draft["body"] and pitch.ADDRESS_PLACEHOLDER in draft["body"]
    assert "Dhruv" in draft["body"] and client["name"] in draft["subject"]

    pitch.mark_opt_out(db, ids[1])
    out = pitch.export_drafts(db, tmp_path / "outreach", sender=sender)
    assert out["count"] == 1 and len(out["eml"]) == 1
    msg = email.message_from_bytes(open(out["eml"][0], "rb").read())
    assert msg["X-Unsent"] == "1" and "hi@glow.example" in msg["To"]
    assert pitch.OPT_OUT_LINE in msg.get_payload(decode=True).decode()
    rows = open(out["csv"]).read().splitlines()
    assert rows[0].startswith("client_id,name") and len([r for r in rows if "glow.example" in r]) >= 1


# --------------------------------------------------------------------------- invoices
def test_invoice_numbering_and_paid_records_revenue(factory):
    db = factory.db
    cid = ugc.add_client(db, "Glow Co", email="hi@glow.example")
    year = date.today().year
    assert invoices.next_invoice_number(db) == f"INV-{year}-0001"
    i1 = invoices.create_invoice(db, cid, [{"description": "Starter pack", "qty": 1, "unit_price": "299"},
                                           {"description": "Extra hook", "qty": 4, "unit_cents": 2500}])
    i2 = invoices.create_invoice(db, cid, [{"description": "Raw files", "unit_cents": 7500}], tax_pct=10)
    inv1, inv2 = invoices.get_invoice(db, i1), invoices.get_invoice(db, i2)
    assert inv1["number"] == f"INV-{year}-0001" and inv2["number"] == f"INV-{year}-0002"
    assert inv1["total_cents"] == 39_900 and inv2["total_cents"] == 8_250

    html = invoices.render_invoice_html(db, i1)
    assert inv1["number"] in html and "$399.00" in html and "Glow Co" in html

    rid = invoices.mark_paid(db, i1)
    assert invoices.mark_paid(db, i1) == rid  # idempotent
    rows = db.query("SELECT * FROM revenue")
    assert len(rows) == 1 and rows[0]["source"] == "ugc" and rows[0]["client_id"] == cid
    assert rows[0]["amount_cents"] == 39_900 and rows[0]["external_id"] == inv1["number"]
    with pytest.raises(ValueError):
        invoices.void_invoice(db, i1)

    saved = invoices.save_invoice(factory.settings, db, i2, pdf=False)
    assert saved["pdf"] is None and (factory.settings.output_dir / saved["path"]).exists()


def test_invoice_pdf_when_chromium_available(factory, monkeypatch):
    monkeypatch.setenv("FACTORY_PDF", "1")
    from contentfactory.business.pdf import pdf_available
    if not pdf_available():
        pytest.skip("node/chromium not available")
    cid = ugc.add_client(factory.db, "PDF Co")
    iid = invoices.create_invoice(factory.db, cid, [{"description": "Thing", "unit_cents": 100}])
    saved = invoices.save_invoice(factory.settings, factory.db, iid)
    if saved["pdf"] is None:
        pytest.skip("playwright could not launch chromium here")
    assert open(saved["pdf"], "rb").read(4) == b"%PDF"


# --------------------------------------------------------------------------- products
def test_product_build_and_gumroad_import(factory):
    brand = factory.brand("money-made-simple")
    outline = products.outline_product(factory.llm, brand, "a 30-day budget reset", kind="checklist")
    res = products.build_product(factory.settings, brand, outline, db=factory.db, kind="checklist", pdf=False)
    html = (factory.settings.output_dir / res["html"]).read_text()
    assert brand.visual.palette[0] in html and outline.title in html and html.count('class="page') >= 3
    row = factory.db.get("products", res["id"])
    assert row["status"] == "ready" and row["brand"] == brand.slug

    gumroad = (f"Purchase ID,Item Name,Purchase Date,Sale Price ($),Net Total ($),Refunded?\n"
               f"abc1,{outline.title},2026-10-02,12,10.50,false\nabc2,{outline.title},2026-10-03,12,10.50,true\n"
               f"abc3,{outline.title},2026-10-04,12,10.50,false\n")
    r1 = products.import_gumroad_sales(factory.db, gumroad)
    assert r1["imported"] == 2 and r1["skipped"] == 1 and r1["total_cents"] == 2100
    r2 = products.import_gumroad_sales(factory.db, gumroad)
    assert r2["imported"] == 0 and r2["duplicates"] == 2
    listed = products.products(factory.db)[0]
    assert listed["sales"] == 2 and listed["revenue_cents"] == 2100
    assert {r["brand"] for r in factory.db.query("SELECT brand FROM revenue")} == {brand.slug}


# --------------------------------------------------------------------------- revenue imports
def test_csv_imports_with_dedupe(db):
    generic = "date,amount,source,brand,note\n2026-10-01,$25.00,sponsorship,money-made-simple,deal\n" \
              "2026-10-05,10,weird,,misc\n2026-10-06,,other,,blank\n"
    r = revenue.import_csv(db, generic)
    assert r["imported"] == 2 and r["skipped"] == 1
    assert revenue.import_csv(db, generic)["duplicates"] == 2
    assert db.scalar("SELECT source FROM revenue WHERE note = 'misc'") == "other"

    amazon = ("Fee-Earnings reports from 10-01-2026 to 10-31-2026\n"
              "Name,ASIN,Tracking ID,Date Shipped,Price($),Items Shipped,Ad Fees($)\n"
              "Desk Lamp,B000,mms-20,2026-10-03,30.00,1,1.20\n"
              "Desk Lamp,B000,mms-20,2026-10-03,30.00,1,1.20\n")
    r = revenue.import_csv(db, amazon, "amazon", brand_map={"mms-20": "money-made-simple"})
    assert r["imported"] == 2 and r["total_cents"] == 240  # identical rows in one file both count
    assert revenue.import_csv(db, amazon, "amazon")["duplicates"] == 2

    youtube = "Date,Estimated revenue (USD)\nTotal,5.00\n2026-10-01,2.50\n2026-10-02,2.50\n"
    r = revenue.import_csv(db, youtube, "youtube", brand="money-made-simple")
    assert r["imported"] == 2 and r["skipped"] == 1
    assert db.scalar("SELECT COUNT(*) FROM revenue WHERE source = 'adsense'") == 2

    impact = "Action Id,Action Date,Campaign,Payout,Status\nA1,10/07/2026,Example HYSA,$50.00,Approved\n" \
             "A2,10/08/2026,Example HYSA,$50.00,Reversed\n"
    r = revenue.import_csv(db, impact, "impact")
    assert r["imported"] == 1 and r["skipped"] == 1

    custom = "When,Payout Amount,Ref\n2026-10-09,7.00,X1\n"
    r = revenue.import_csv(db, custom, "generic", mapping={"date": "When", "amount": "Payout Amount",
                                                           "external_id": "Ref"}, revenue_source="affiliate")
    assert r["imported"] == 1 and revenue.import_csv(db, custom, "generic", mapping={
        "date": "When", "amount": "Payout Amount", "external_id": "Ref"}, revenue_source="affiliate")["duplicates"] == 1


# --------------------------------------------------------------------------- reports
def _post_with_views(db, brand: str, views: int, platform: str = "youtube") -> int:
    pid = db.insert("posts", {"brand": brand, "format": "short", "status": "published", "title": "Post"})
    pub = db.insert("publications", {"post_id": pid, "platform": platform, "status": "published", "remote_id": f"v{pid}"})
    db.insert("metrics", {"publication_id": pub, "captured_at": now_iso(), "views": views // 2})
    db.insert("metrics", {"publication_id": pub, "captured_at": now_iso(), "views": views, "link_clicks": 7})
    return pid


def test_pnl_math_and_reports(db):
    revenue.add_revenue(db, "affiliate", "100", date="2026-09-10", brand="mms")
    revenue.add_revenue(db, "ugc", "300", date="2026-09-20")
    revenue.add_revenue(db, "product", "50", date="2026-10-01", brand="mms")
    revenue.add_expense(db, "software", "20", date="2026-09-15")
    revenue.add_expense(db, "llm", "5", date="2026-10-02")
    db.insert("llm_usage", {"ts": "2026-09-12T10:00:00+00:00", "provider": "anthropic", "model": "m",
                            "purpose": "script", "cost_usd": 1.25})
    db.insert("llm_usage", {"ts": "2026-10-12T10:00:00+00:00", "provider": "anthropic", "model": "m",
                            "purpose": "script", "cost_usd": 3.0})
    rows = {r["month"]: r for r in revenue.pnl_by_month(db)}
    sep, octo = rows["2026-09"], rows["2026-10"]
    assert sep["revenue_cents"] == 40_000 and sep["expense_cents"] == 2_000 and sep["llm_cents"] == 125
    assert sep["profit_cents"] == 40_000 - 2_000 - 125
    assert octo["llm_cents"] == 0  # manual llm expense replaces the estimate
    assert octo["profit_cents"] == 5_000 - 500
    totals = revenue.pnl_totals(list(rows.values()))
    assert totals["profit_cents"] == sep["profit_cents"] + octo["profit_cents"]

    by_source = {r["key"]: r["cents"] for r in revenue.revenue_by_source(db)}
    assert by_source == {"ugc": 30_000, "affiliate": 10_000, "product": 5_000}
    assert {r["key"]: r["cents"] for r in revenue.revenue_by_brand(db)}["mms"] == 15_000
    spend = revenue.llm_spend(db)
    assert spend["total_usd"] == 4.25 and spend["by_purpose"][0]["key"] == "script"

    pid = _post_with_views(db, "mms", 10_000)
    revenue.add_revenue(db, "affiliate", "20", date="2026-10-03", brand="mms", post_id=pid)
    attr = revenue.post_attribution(db)
    assert attr[0]["post_id"] == pid and attr[0]["views"] == 10_000 and attr[0]["rpm_cents"] == 200
    rpm = revenue.effective_rpm(db)
    mms = next(r for r in rpm["by_brand"] if r["brand"] == "mms")
    assert mms["revenue_cents"] == 17_000 and mms["rpm_cents"] == 1_700
    yt = next(r for r in rpm["by_platform"] if r["platform"] == "youtube")
    assert yt["revenue_cents"] == 2_000 and yt["views"] == 10_000


def test_goal_progress(db, monkeypatch):
    monkeypatch.setenv("FACTORY_MONTHLY_GOAL", "1000")
    revenue.add_revenue(db, "ugc", "300", date="2026-11-01")
    revenue.add_revenue(db, "ugc", "200", date="2026-11-10")
    g = revenue.goal_progress(db, month="2026-11", on=date(2026, 11, 10))
    assert g["goal_cents"] == 100_000 and g["revenue_cents"] == 50_000 and g["pct"] == 50.0
    assert g["projected_cents"] == 150_000 and g["on_track"]
    assert g["remaining_cents"] == 50_000 and g["needed_per_day_cents"] == 2_500
    past = revenue.goal_progress(db, month="2026-11", on=date(2026, 12, 5))
    assert past["days_elapsed"] == 30 and past["projected_cents"] == 50_000 and not past["on_track"]
    assert set(revenue.summary(db)) >= {"pnl", "goal", "by_source", "by_brand", "llm", "rpm", "top_posts"}


# --------------------------------------------------------------------------- affiliates
def test_affiliate_links_and_disclosure(factory):
    db = factory.db
    res = affiliates.sync_from_brands(db, factory.brands())
    assert "hysa" in res["added"]  # other example brands bring their own placeholder links
    again = affiliates.sync_from_brands(db, factory.brands())
    assert "hysa" in again["updated"] and not again["added"]
    url = affiliates.resolve_click(db, "hysa", post_id="12", platform="instagram")
    assert url.startswith("https://example.com/go/hysa?") and "utm_source=instagram" in url
    assert "utm_content=post-12" in url and "utm_campaign=hysa" in url
    assert affiliates.resolve_click(db, "nope") is None
    assert db.one("SELECT clicks FROM affiliate_links WHERE slug = 'hysa'")["clicks"] == 1
    tagged = affiliates.resolve_click(db, "hysa", platform="tiktok",
                                      utm={"utm_campaign": "launch<x>", "utm_term": "hysa", "utm_bogus": "1"})
    assert "utm_campaign=launchx" in tagged and "utm_term=hysa" in tagged and "bogus" not in tagged
    assert affiliates.clicks_by_post(db)[0]["post_id"] == 12
    assert affiliates.with_utm("https://x.example/?utm_source=keep", source="new").count("utm_source") == 1

    cap = "Open a high-yield savings account: https://links.example/go/hysa"
    out = affiliates.ensure_disclosure(cap)
    assert out.startswith(cap) and "commission" in out
    assert affiliates.ensure_disclosure(out) == out
    assert affiliates.ensure_disclosure("No links here.") == "No links here."
    already = cap + "\n#ad"
    assert affiliates.ensure_disclosure(already) == already
    assert "commission" in affiliates.ensure_disclosure("Go: https://example.com/go/hysa?x",
                                                        known_urls=["https://example.com/go/hysa"])
    assert affiliates.tracked_url("hysa", post_id=3, platform="tiktok", base="https://l.example") == \
        "https://l.example/go/hysa?p=3&s=tiktok"


# --------------------------------------------------------------------------- routes
def _client(home, monkeypatch):
    if importlib.util.find_spec("contentfactory.web.deps") is None or \
            importlib.util.find_spec("contentfactory.web.app") is None:
        pytest.skip("dashboard (web/deps.py, web/app.py) not available yet")
    from fastapi.testclient import TestClient
    from contentfactory.config import Settings
    from contentfactory.pipeline import Factory
    from contentfactory.web.app import create_app
    monkeypatch.setenv("DASHBOARD_TOKEN", "test-token")
    factory = Factory.create(Settings.load(home))
    client = TestClient(create_app(factory), follow_redirects=False)
    client.headers["Authorization"] = "Bearer test-token"
    return client, factory


def test_business_pages(home, monkeypatch):
    client, factory = _client(home, monkeypatch)
    db = factory.db
    for path in ("/business/clients", "/business/orders", "/business/products", "/business/revenue",
                 "/business/affiliates"):
        r = client.get(path)
        assert r.status_code == 200, (path, r.text[:500])

    r = client.post("/business/clients", data={"name": "Glow Co", "email": "hi@glow.example", "niche": "skincare"})
    assert r.status_code == 303
    cid = db.one("SELECT id FROM clients")["id"]
    assert client.post(f"/business/clients/{cid}/pitch").status_code == 303
    assert client.post(f"/business/clients/{cid}/status", data={"status": "negotiating"}).status_code == 303
    assert client.post(f"/business/clients/{cid}/orders",
                       data={"package": "starter", "addons": ["raw_files"], "product": "Serum"}).status_code == 303
    oid = db.one("SELECT id FROM orders")["id"]
    assert client.post(f"/business/orders/{oid}/ad-script", data={"product": "Serum"}).status_code == 303
    assert db.get("orders", oid)["brief"]["ad_scripts"]
    page = client.get(f"/business/clients/{cid}")
    assert page.status_code == 200 and "Glow Co" in page.text and pitch.OPT_OUT_LINE.split('"')[0] in page.text
    assert "Serum" in client.get("/business/orders").text

    r = client.post(f"/business/orders/{oid}/invoice")
    iid = int(r.headers["location"].rsplit("/", 1)[1])
    assert "INV-" in client.get(f"/business/invoices/{iid}").text
    assert client.post(f"/business/invoices/{iid}/paid").status_code == 303
    assert db.scalar("SELECT COUNT(*) FROM revenue WHERE source = 'ugc'") == 1

    files = {"file": ("leads.csv", b"name,website,email,niche\nFit,https://fit.example,a@fit.example,fitness\n",
                      "text/csv")}
    assert client.post("/business/clients/import", files=files).status_code == 303
    assert db.scalar("SELECT COUNT(*) FROM clients") == 2
    files = {"file": ("rev.csv", b"date,amount\n2026-10-01,5\n", "text/csv")}
    r = client.post("/business/revenue/import", data={"kind": "generic"}, files=files)
    assert "Imported+1" in r.headers["location"] or "Imported%201" in r.headers["location"]
    assert client.post("/business/revenue/add", data={"source": "affiliate", "amount": "12.5"}).status_code == 303
    assert client.post("/business/revenue/expense", data={"category": "software", "amount": "3"}).status_code == 303
    assert "$" in client.get("/business/revenue").text

    assert client.post("/business/products/new", data={"brand": "money-made-simple", "idea": "budget reset",
                                                       "kind": "guide"}).status_code == 303
    assert db.scalar("SELECT COUNT(*) FROM products") == 1

    assert client.post("/business/affiliates/sync").status_code == 303
    public = client.__class__(client.app, follow_redirects=False)  # no auth header
    r = public.get("/go/hysa?p=1&s=youtube")
    assert r.status_code == 302 and r.headers["location"].startswith("https://example.com/go/hysa")
    assert public.get("/go/unknown").status_code == 404
