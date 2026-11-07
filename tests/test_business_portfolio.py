"""Portfolio gallery, client proposals, outreach cadence and order onboarding. All offline."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from contentfactory.business import onboarding, pitch, portfolio, proposals, ugc
from contentfactory.business._util import add_days, today

ROOT = Path(__file__).resolve().parents[1]
ADS_JSON = ROOT / "launch" / "ugc-service" / "portfolio" / "ads.json"


@pytest.fixture(autouse=True)
def no_pdf(home, monkeypatch):  # after `home`, which clears FACTORY_* vars
    monkeypatch.setenv("FACTORY_PDF", "0")


@pytest.fixture
def db(factory):
    return factory.db


def _lead(db, name="Glow Co", email="hi@glow.example", **kw):
    return ugc.add_client(db, name, email=email, niche=kw.pop("niche", "skincare"), **kw)


# --------------------------------------------------------------------------- portfolio
def test_portfolio_ads_are_clean_and_fictional():
    ads = portfolio.load_ads(ADS_JSON)
    assert [a["slug"] for a in ads] == ["trailsip", "lumen-and-loaf", "hound-and-hollow", "deskline",
                                        "fern-street-studio"]
    assert portfolio.check_portfolio_ads(ads) == []
    for a in ads:
        assert "AI-generated" in a["script"].on_screen_disclosure
        assert len(a["script"].variations) >= 2


def test_portfolio_html_without_rendering(factory, tmp_path):
    ads = portfolio.load_ads(ADS_JSON)
    res = portfolio.build_portfolio(factory.settings, ads, tmp_path / "out", copy_to=tmp_path / "repo", render=False)
    page = Path(res["html"]).read_text()
    assert page.startswith("<!doctype html>") and 'name="viewport"' in page
    for a in ads:
        assert f'src="videos/{a["slug"]}.mp4"' in page and f'poster="posters/{a["slug"]}.jpg"' in page
        assert a["brand"].replace("&", "&amp;") in page
    assert "fictional" in page.lower() and portfolio.FICTIONAL_LABEL in page and "AI-generated" in page
    assert "<script src=" not in page and "<link" not in page  # self-contained
    assert (tmp_path / "repo" / "portfolio.html").exists() and not (tmp_path / "repo" / "videos").exists()


def test_portfolio_blocks_testimonials(factory, tmp_path):
    ads = portfolio.load_ads(ADS_JSON)[:1]
    raw = ads[0]["script"].model_dump()
    raw["segments"][0]["narration"] = "I've been using TrailSip every day and it changed my life."
    with pytest.raises(ugc.TestimonialError):
        portfolio.build_portfolio(factory.settings, [{**ads[0], "script": raw}], tmp_path, render=False)


def test_portfolio_render_uses_labels_and_subdir(factory, tmp_path, monkeypatch):
    seen = {}

    def fake_render_ad_video(settings, brand_like, ad, **kw):
        seen.update(brand=brand_like, kw=kw)
        raise RuntimeError("stop after the call")
    monkeypatch.setattr(ugc, "render_ad_video", fake_render_ad_video)
    entry = portfolio.load_ads(ADS_JSON)[0]
    with pytest.raises(RuntimeError):
        portfolio.render_portfolio_ad(factory.settings, entry, tmp_path / "out", tmp_path / "work")
    assert seen["kw"] == {"output_subdir": "portfolio/trailsip", "headline_disclosure": False}
    assert seen["brand"]["palette"] == entry["palette"]
    assert portfolio.disclosure_label(factory.settings, entry) == portfolio.SILENT_LABEL  # tts=silent in tests


def test_render_ad_options(factory):
    ad = ugc.write_ad_script(factory.llm, {"product": "Glow Serum", "brand_name": "Glow Co"})
    post = ugc.render_ad(factory.settings, "Glow Co", ad, output_subdir="portfolio/glow", headline_disclosure=False)
    assert post["meta"]["output_subdir"] == "portfolio/glow"
    assert ad.on_screen_disclosure not in post["script"]["segments"][0]["on_screen_text"]


# --------------------------------------------------------------------------- proposals
def test_offline_concepts_differ_by_style(factory):
    client = {"id": 1, "name": "Glow Co", "notes": "", "niche": "skincare"}
    concepts = proposals.ad_concepts(factory.llm, client, ["Vitamin C Serum"])
    assert [c["style"] for c in concepts] == ["spokesperson", "demo", "offer"]
    assert len({c["script"]["hook"] for c in concepts}) == 3
    for c in concepts:
        assert all(chk.level != "block" for chk in ugc.check_ad_script(ugc.AdScript.model_validate(c["script"])))


def test_proposal_numbers_and_sections(factory, tmp_path):
    db = factory.db
    cid = _lead(db, contact_name="Maya Lee", notes="Runs Meta ads; creative is stale.")
    ugc.add_note(db, cid, "Wants hook tests before Black Friday.")
    res = proposals.build_proposal(db, cid, "growth", ["paid_usage_90d"], llm=factory.llm, out_dir=tmp_path,
                                   products=["Vitamin C Serum"], sender={"name": "Dhruv", "business_name": "Northlight",
                                                                         "payment_instructions": "Pay via Stripe link"})
    assert res["total_cents"] == 44_900 + 10_000 == ugc.quote("growth", ["paid_usage_90d"])["total_cents"]
    assert res["deposit_cents"] == 27_450
    page = res["html_text"]
    for section in ("The opportunity", "What we heard from you", "What you get", "Three starting concepts",
                    "Timeline", "Investment", "Next steps", "How to pay", "How we use AI"):
        assert section in page, section
    assert "$549.00" in page and "$274.50" in page and "Pay via Stripe link" in page
    assert "Wants hook tests before Black Friday." in page and "[2026" not in page  # timestamps stripped
    assert "Maya Lee" in page and "Vitamin C Serum" in page
    assert "180 days of paid ads" in page  # 90 included with Growth + 90 add-on
    assert page.count('class="concept"') == 3
    assert Path(res["html"]).exists() and res["pdf"] is None
    meta = ugc.get_client(db, cid)["meta"]
    assert meta["proposals"][-1]["total_cents"] == 54_900
    again = proposals.build_proposal(db, cid, "starter", [], llm=factory.llm, out_dir=tmp_path)
    assert again["number"] != res["number"]  # same day, new number


def test_proposal_retainer_and_rush(factory):
    db = factory.db
    cid = _lead(db)
    ctx = proposals.proposal_context(db, cid, "retainer", [], llm=factory.llm)
    assert ctx["deposit_cents"] == ctx["quote"]["total_cents"] == 79_900 and ctx["balance_cents"] == 0
    assert "per month" in proposals.render_proposal_html(ctx)
    ctx = proposals.proposal_context(db, cid, "starter", ["rush"], llm=factory.llm, start="2026-01-05")
    assert ctx["quote"]["total_cents"] == 24_900 + 7_500
    assert ctx["timeline"][0]["when"] == "2026-01-05"
    assert ctx["timeline"][2]["when"] == add_days("2026-01-05", proposals.SCRIPT_DAYS + 3)  # 7 // 2
    assert "[Payment link" in proposals.render_proposal_html(ctx)  # placeholder when not configured


def test_proposal_pdf_when_chromium_available(factory, tmp_path, monkeypatch):
    from contentfactory.business import pdf
    monkeypatch.setenv("FACTORY_PDF", "1")
    if not pdf.pdf_available():
        pytest.skip("node not available")
    cid = _lead(factory.db)
    res = proposals.build_proposal(factory.db, cid, "starter", [], out_dir=tmp_path)
    if res["pdf"] is None:
        pytest.skip("playwright/chromium not available")
    assert Path(res["pdf"]).read_bytes()[:4] == b"%PDF"


# --------------------------------------------------------------------------- cadence
def test_cadence_schedules_and_stops(factory):
    db = factory.db
    cid = _lead(db)
    with pytest.raises(ValueError):
        pitch.mark_pitch_sent(db, cid)  # no draft yet
    pitch.save_pitch_draft(db, cid, pitch.draft_pitch(factory.llm, ugc.get_client(db, cid)))
    plan = pitch.outreach_today(db)
    assert [x["client"]["id"] for x in plan["first_touch"]] == [cid] and plan["count"] == 1

    cad = pitch.mark_pitch_sent(db, cid, sent_on="2026-03-02")
    assert [s["due"] for s in cad["steps"]] == ["2026-03-05", "2026-03-09"]
    assert all(pitch.OPT_OUT_LINE in s["body"] for s in cad["steps"])
    client = ugc.get_client(db, cid)
    assert client["status"] == "contacted" and client["meta"]["next_follow_up"] == "2026-03-05"

    assert pitch.outreach_today(db, on="2026-03-04")["count"] == 0
    due = pitch.outreach_today(db, on="2026-03-05")["follow_ups"]
    assert len(due) == 1 and due[0]["step"] == 1 and due[0]["days_late"] == 0
    late = pitch.outreach_today(db, on="2026-03-10")["follow_ups"]
    assert len(late) == 1 and late[0]["step"] == 1 and late[0]["days_late"] == 5  # earliest pending first

    assert pitch.mark_sent(db, cid, sent_on="2026-03-05")["step"]["n"] == 1
    assert ugc.get_client(db, cid)["meta"]["next_follow_up"] == "2026-03-09"
    assert pitch.outreach_today(db, on="2026-03-09")["follow_ups"][0]["step"] == 2

    ugc.set_client_status(db, cid, "replied", note="Asked for prices")
    assert pitch.outreach_today(db, on="2026-03-09")["count"] == 0
    cad = ugc.get_client(db, cid)["meta"]["cadence"]
    assert cad["stopped"] == "status: replied" and cad["steps"][1]["status"] == "cancelled"
    with pytest.raises(ValueError):
        pitch.mark_follow_up_sent(db, cid)


def test_cadence_completes_and_respects_opt_out(factory):
    db = factory.db
    a, b = _lead(db, "A Co", "a@a.example"), _lead(db, "B Co", "b@b.example")
    for cid in (a, b):
        pitch.save_pitch_draft(db, cid, pitch.draft_pitch(factory.llm, ugc.get_client(db, cid)))
        pitch.mark_sent(db, cid, sent_on="2026-03-02")
    pitch.mark_opt_out(db, b)
    assert ugc.get_client(db, b)["meta"]["cadence"]["stopped"] == "opted out"
    with pytest.raises(ValueError):
        pitch.mark_pitch_sent(db, b)
    assert [x["client"]["id"] for x in pitch.outreach_today(db, on="2026-03-20")["follow_ups"]] == [a]
    pitch.mark_sent(db, a)
    pitch.mark_sent(db, a)
    client = ugc.get_client(db, a)
    assert client["meta"]["cadence"]["stopped"] == "completed" and "next_follow_up" not in client["meta"]
    assert pitch.outreach_today(db, on="2026-04-01")["count"] == 0


def test_export_today_writes_drafts(factory, tmp_path):
    db = factory.db
    cid = _lead(db)
    pitch.save_pitch_draft(db, cid, pitch.draft_pitch(factory.llm, ugc.get_client(db, cid)))
    res = pitch.export_today(db, tmp_path)
    assert res["count"] == 1 and Path(res["eml"][0]).name.endswith("-pitch.eml")
    assert b"X-Unsent: 1" in Path(res["eml"][0]).read_bytes()


# --------------------------------------------------------------------------- onboarding
def test_order_gets_questionnaire_and_checklist(factory):
    db = factory.db
    cid = _lead(db)
    oid = ugc.create_order(db, cid, "growth", addons=["raw_files", "paid_usage_90d"])
    order = ugc.get_order(db, oid)
    brief = order["brief"]
    assert brief["questionnaire"]["status"] == "waiting" and brief["quote"]["total_cents"] == 44_900 + 7_500 + 10_000
    keys = [i["key"] for i in brief["checklist"]]
    assert {"deposit", "brief", "label", "raw", "balance", "final"} <= set(keys) and "report" not in keys
    assert any("24 files" in i["label"] for i in brief["checklist"])

    md = onboarding.questionnaire_markdown(order, ugc.get_client(db, cid))
    assert md.startswith("# Ad brief for Glow Co") and "Claims you can back up" in md and "AI label" in md

    res = onboarding.save_answers(db, oid, {"product": "Vitamin C Serum\nNight Cream"})
    assert not res["complete"] and "audience" in res["missing"] and "ack:ai_label" in res["missing"]
    full = {"product": "Vitamin C Serum", "audience": "busy commuters", "problem": "a faster morning routine",
            "features": "- 30 ml\n- fragrance-free", "approved_claims": "Dermatologist-tested (report on file)",
            "cta": "Shop at glow.example", "assets": "drive link", "platforms": "TikTok, Reels, paid",
            "presenter": "AI voiceover only (product footage)", "approver": "Maya, maya@glow.example"}
    res = onboarding.save_answers(db, oid, full, acknowledgements=[k for k, _ in onboarding.ACKNOWLEDGEMENTS])
    assert res["complete"]
    order = ugc.get_order(db, oid)
    assert order["brief"]["answers"]["features"] == ["30 ml", "fragrance-free"]
    assert next(i for i in order["brief"]["checklist"] if i["key"] == "brief")["done"]
    ab = onboarding.ad_brief_from_answers(db, oid)
    assert ab.product == "Vitamin C Serum" and ab.style == "demo" and ab.approved_claims
    onboarding.set_check(db, oid, "deposit")
    assert onboarding.progress(ugc.get_order(db, oid))["done"] == 2
    with pytest.raises(KeyError):
        onboarding.set_check(db, oid, "nope")


def test_retainer_checklist_has_report(factory):
    cid = _lead(factory.db)
    oid = ugc.create_order(factory.db, cid, "retainer")
    keys = [i["key"] for i in ugc.get_order(factory.db, oid)["brief"]["checklist"]]
    assert "report" in keys


# --------------------------------------------------------------------------- web
def _client(home, monkeypatch):
    if importlib.util.find_spec("contentfactory.web.app") is None:
        pytest.skip("dashboard not available")
    from fastapi.testclient import TestClient
    from contentfactory.config import Settings
    from contentfactory.pipeline import Factory
    from contentfactory.web.app import create_app
    monkeypatch.setenv("DASHBOARD_TOKEN", "test-token")
    factory = Factory.create(Settings.load(home))
    client = TestClient(create_app(factory), follow_redirects=False)
    client.headers["Authorization"] = "Bearer test-token"
    return client, factory


def test_business_pages_for_cadence_proposal_and_brief(home, monkeypatch):
    client, factory = _client(home, monkeypatch)
    db = factory.db
    cid = _lead(db)
    assert client.post(f"/business/clients/{cid}/pitch").status_code == 303
    page = client.get("/business/clients")
    assert page.status_code == 200 and "Today: 1 email to send" in page.text and "mailto:" in page.text
    r = client.post(f"/business/clients/{cid}/sent", data={"back": "/business/clients"})
    assert r.status_code == 303 and "Follow-up" in r.headers["location"].replace("+", " ")
    assert ugc.get_client(db, cid)["meta"]["cadence"]["steps"][0]["due"] == add_days(today(), 3)
    assert "Follow-up cadence" in client.get(f"/business/clients/{cid}").text

    assert client.get(f"/business/clients/{cid}/proposal").status_code == 404
    r = client.post(f"/business/clients/{cid}/proposal", data={"package": "growth", "addons": ["raw_files"]})
    assert r.status_code == 303 and "err=" not in r.headers["location"]
    view = client.get(f"/business/clients/{cid}/proposal")
    assert view.status_code == 200 and "Three starting concepts" in view.text and "$524.00" in view.text
    assert client.get(f"/business/clients/{cid}/proposal?pdf=1").status_code == 404  # PDF disabled in tests

    r = client.post(f"/business/clients/{cid}/orders", data={"package": "starter"})
    oid = db.one("SELECT id FROM orders")["id"]
    assert r.headers["location"].startswith(f"/business/orders/{oid}/brief")
    page = client.get(f"/business/orders/{oid}/brief")
    assert page.status_code == 200 and "Delivery checklist" in page.text and "Claims you can back up" in page.text
    md = client.get(f"/business/orders/{oid}/brief.md")
    assert md.status_code == 200 and md.text.startswith("# Ad brief")
    data = {"product": "Serum", "audience": "a", "problem": "b", "features": "c", "approved_claims": "d",
            "cta": "Shop", "assets": "link", "platforms": "TikTok", "presenter": "Mix", "approver": "Maya",
            "ack": [k for k, _ in onboarding.ACKNOWLEDGEMENTS]}
    r = client.post(f"/business/orders/{oid}/brief", data=data)
    assert "msg=" in r.headers["location"]
    assert ugc.get_order(db, oid)["brief"]["questionnaire"]["status"] == "complete"
    assert client.post(f"/business/orders/{oid}/checklist", data={"key": "deposit", "done": "1"}).status_code == 303
    assert client.post(f"/business/orders/{oid}/ad-script-from-brief").status_code == 303
    assert ugc.get_order(db, oid)["brief"]["ad_scripts"]

    anon = client.__class__(client.app, follow_redirects=False)
    anon_r = anon.get(f"/business/orders/{oid}/brief")
    assert anon_r.status_code in (302, 303, 401, 403)


def test_cli_commands(home, monkeypatch, capsys):
    from contentfactory.cli import main
    monkeypatch.setenv("FACTORY_HOME", str(home))
    main(["clients", "add", "--name", "Glow Co", "--email", "hi@glow.example"])
    main(["pitch", "draft", "--id", "1"])
    capsys.readouterr()
    main(["pitch", "today"])
    assert "first pitch" in capsys.readouterr().out
    main(["pitch", "sent", "--id", "1"])
    assert "follow-up drafts due" in capsys.readouterr().out
    main(["proposal", "--client", "1", "--package", "starter", "--no-pdf"])
    assert "total $249.00" in capsys.readouterr().out
    main(["order", "create", "--client", "1", "--package", "starter"])
    main(["order", "brief", "--id", "1"])
    assert "# Ad brief for Glow Co" in capsys.readouterr().out
    main(["portfolio", "page", "--out", str(home / "pf")])
    out = json.loads(capsys.readouterr().out)
    assert Path(out["html"]).exists()
