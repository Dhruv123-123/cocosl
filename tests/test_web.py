"""Dashboard tests. Offline: FACTORY_LLM=offline, media rendering is faked."""
from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from contentfactory.config import Settings
from contentfactory.db import now_iso
from contentfactory.pipeline import Factory
from contentfactory.web.app import create_app
from contentfactory.web.deps import humanize, money, sparkline, templates

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ("127.0.0.1", 50000)
BRAND = "money-made-simple"


# --------------------------------------------------------------------------- seed helpers
def make_script(title: str, claims: list[str], n_segments: int = 3) -> dict:
    return {
        "title": title, "hook": f"Most people get {title.lower()} wrong.",
        "segments": [{"heading": f"Beat {i + 1}", "narration": f"Narration for beat {i + 1} of {title}.",
                      "on_screen_text": f"Point {i + 1}", "visual_prompt": "flat illustration"}
                     for i in range(n_segments)],
        "cta": "Follow for one money move a week.", "caption": f"{title}: the short version.",
        "hashtags": ["moneytips", "budgeting"], "description": f"{title} explained.",
        "thumbnail_text": title[:20], "sources": ["https://www.investor.gov/"], "claims_to_verify": claims,
    }


FAKE_ASSETS = {
    "video": "posts/1/video.mp4", "audio": "posts/1/voice.wav", "captions_srt": "posts/1/captions.srt",
    "images": ["posts/1/img_0.png"], "slides": [], "thumbnail": "posts/1/thumb.png", "duration": 41.0,
    "provenance": [{"path": "posts/1/img_0.png", "source": "generated", "tool": "cards", "prompt": "x", "license": ""}],
}


def fake_render(settings, brand, post):
    return {**FAKE_ASSETS, "video": f"posts/{post['id']}/video.mp4"}


def add_post(f: Factory, title: str, *, status: str = "in_review", fmt: str = "short", claims=None,
             caption: str | None = None, meta: dict | None = None, assets: dict | None = None,
             check: bool = True) -> int:
    script = make_script(title, claims if claims is not None else [])
    pid = f.db.insert("posts", {
        "brand": BRAND, "format": fmt, "status": status, "title": title, "script": script,
        "caption": caption if caption is not None else script["caption"] + " Made with AI tools.",
        "hashtags": script["hashtags"], "disclosure": f.brand(BRAND).ai_disclosure,
        "assets": assets if assets is not None else FAKE_ASSETS,
        "meta": meta or {"editor": {"score": 7, "hook_strength": 6, "originality": 7, "accuracy_risk": 3,
                                    "problems": ["CTA is generic"], "suggested_fixes": ["Name the app"]}},
    })
    if check:
        f.check(pid)
    return pid


def seed(f: Factory) -> dict:
    """A realistic little world: ideas, a review queue, a blocked post, a schedule, metrics, money."""
    ids = {}
    for i, (title, score, status) in enumerate([
        ("Why your budget fails in week two", 8.5, "new"),
        ("Roth IRA vs 401k in 60 seconds", 7.2, "approved"),
        ("The credit score myth that costs you", 6.1, "new"),
        ("Index funds explained with pizza", 5.0, "new"),
        ("Crypto pump red flags", 1.0, "rejected"),
    ]):
        ids.setdefault("ideas", []).append(f.db.insert("ideas", {
            "brand": BRAND, "title": title, "angle": f"Angle {i}", "format": "short", "pillar": "budgeting",
            "score": score, "status": status, "meta": {"hook": "Hook line", "monetization": "affiliate"}}))
    ids["review"] = add_post(f, "Three accounts every 22 year old needs",
                             claims=["HYSA rates are around 4% APY", "Roth IRA limit is $7,000 for 2026"])
    ids["carousel"] = add_post(f, "Budget apps compared honestly", fmt="carousel", claims=[],
                               assets={"slides": ["posts/c/s1.png", "posts/c/s2.png"], "provenance": []})
    ids["blocked"] = add_post(f, "The HYSA I recommend", claims=["Bonus is $50"],
                              meta={"affiliate_slugs": ["hysa"], "editor": {}})
    ids["scheduled"] = add_post(f, "Emergency fund in 5 steps", claims=[])
    f.approve(ids["scheduled"])
    f.schedule(ids["scheduled"])
    ids["published"] = add_post(f, "Credit utilization explained", claims=[])
    pub = f.db.insert("publications", {
        "post_id": ids["published"], "platform": "youtube", "status": "published", "remote_id": "abc",
        "url": "https://youtube.com/shorts/abc", "scheduled_at": now_iso(), "published_at": now_iso()})
    f.db.update("posts", ids["published"], {"status": "published"})
    for d, views in [(3, 120), (2, 800), (1, 1900), (0, 3400)]:
        f.db.insert("metrics", {"publication_id": pub, "views": views, "likes": views // 20, "comments": 4,
                                "captured_at": (datetime.now(timezone.utc) - timedelta(days=d)).isoformat()})
    f.db.insert("revenue", {"date": datetime.now(timezone.utc).date().isoformat(), "source": "affiliate",
                            "brand": BRAND, "amount_cents": 5000})
    f.db.insert("llm_usage", {"ts": now_iso(), "provider": "anthropic", "model": "claude-opus-5-5",
                              "purpose": "script", "input_tokens": 5000, "output_tokens": 3000, "cost_usd": 0.08})
    return ids


@pytest.fixture
def factory(tmp_path, monkeypatch) -> Factory:
    for key in ("FACTORY_DB", "FACTORY_OUTPUT", "FACTORY_BRANDS", "DASHBOARD_TOKEN", "FACTORY_DRY_RUN",
                "FACTORY_HOME", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("FACTORY_LLM", "offline")
    monkeypatch.setenv("FACTORY_PREFLIGHT", "0")  # placeholder media
    shutil.copytree(ROOT / "brands", tmp_path / "brands")
    import contentfactory.media as media
    monkeypatch.setattr(media, "render_post", fake_render)
    f = Factory.create(Settings.load(tmp_path))
    f.seed_ids = seed(f)  # type: ignore[attr-defined]
    return f


@pytest.fixture
def client(factory) -> TestClient:
    with TestClient(create_app(factory), client=LOCAL) as c:
        yield c


# --------------------------------------------------------------------------- pages
@pytest.mark.parametrize("path", ["/", "/ideas", f"/ideas?brand={BRAND}&show_rejected=1", "/review",
                                  "/calendar", "/published", "/settings", "/today"])
def test_pages_render(client, path):
    r = client.get(path)
    assert r.status_code == 200, r.text[:500]
    assert "Content Factory" in r.text
    assert "DASHBOARD_TOKEN" in r.text  # local-only banner


def test_post_detail_and_404(client, factory):
    pid = factory.seed_ids["review"]
    r = client.get(f"/posts/{pid}")
    assert r.status_code == 200
    assert "HYSA rates are around 4% APY" in r.text
    assert f"/media/posts/1/video.mp4" in r.text
    assert "Platform check" in r.text and "video file is missing" in r.text  # placeholder media isn't on disk
    assert client.get("/posts/9999").status_code == 404


def test_overview_kpis(client):
    html = client.get("/").text
    assert "$50.00" in html          # revenue last 30d
    assert "3.4k" in html            # views from metrics
    assert "$0.08" in html           # LLM spend
    assert "affiliate" in html.lower() and "blocked" in html


def test_review_page_shows_claims_checks_and_media(client, factory):
    html = client.get("/review").text
    assert 'name="verified" value="0"' in html and 'name="verified" value="1"' in html
    assert "data-needs-claims" in html
    assert "<video" in html and "posts/c/s1.png" in html
    assert "Affiliate link without a clear disclosure" in html
    assert "CTA is generic" in html


# --------------------------------------------------------------------------- auth
def test_no_token_refuses_remote_clients(factory):
    app = create_app(factory)
    remote = TestClient(app, client=("203.0.113.9", 4000))
    assert remote.get("/").status_code == 403
    assert remote.get("/api/posts").status_code == 403
    assert remote.get("/api/health").json() == {"ok": True}
    proxied = TestClient(app, client=LOCAL, headers={"X-Forwarded-For": "203.0.113.9"})
    assert proxied.get("/").status_code == 403


def test_token_auth_cookie_and_bearer(factory):
    factory.settings.dashboard_token = "s3cret-token-value"
    app = create_app(factory)
    c = TestClient(app, client=("203.0.113.9", 4000), follow_redirects=False)
    r = c.get("/review")
    assert r.status_code == 303 and r.headers["location"].startswith("/login?next=/review")
    assert c.get("/api/posts").status_code == 401
    assert c.get("/api/posts", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.get("/api/posts", headers={"Authorization": "Bearer s3cret-token-value"}).status_code == 200
    assert c.get("/login").status_code == 200
    assert "Review" not in c.get("/login").text.split("<main>")[0]  # no nav for anonymous visitors
    assert c.post("/login", data={"token": "nope", "next": "/"}).status_code == 401
    r = c.post("/login", data={"token": "s3cret-token-value", "next": "/review"})
    assert r.status_code == 303 and r.headers["location"] == "/review"
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "s3cret-token-value" not in cookie
    assert c.get("/review").status_code == 200
    assert "Local-only mode" not in c.get("/").text
    # the public redirect route must never require auth
    anon = TestClient(app, client=("203.0.113.9", 4000), follow_redirects=False)
    r = anon.get("/go/hysa")
    assert r.status_code not in (401, 403) and "/login" not in r.headers.get("location", "")
    assert anon.get("/static/style.css").status_code == 200


def test_login_redirect_rejects_offsite_next(factory):
    factory.settings.dashboard_token = "tok"
    c = TestClient(create_app(factory), follow_redirects=False)
    r = c.post("/login", data={"token": "tok", "next": "//evil.example/x"})
    assert r.headers["location"] == "/"


def test_cross_site_post_refused(client, factory):
    pid = factory.seed_ids["review"]
    r = client.post(f"/posts/{pid}/reject", data={"reason": "x"}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403
    assert factory.db.get("posts", pid)["status"] == "in_review"


# --------------------------------------------------------------------------- review actions (forms)
def test_form_approve_requires_every_claim(client, factory):
    pid = factory.seed_ids["review"]
    r = client.post(f"/posts/{pid}/approve", data={"verified": ["0"], "and_schedule": "1"},
                    headers={"Referer": "http://testserver/review"})
    assert r.status_code == 200 and "not marked as fact-checked" in r.text
    assert factory.db.get("posts", pid)["status"] == "in_review"
    r = client.post(f"/posts/{pid}/approve", data={"verified": ["0", "1"], "and_schedule": "1"})
    assert r.status_code == 200 and "Approved and scheduled" in r.text
    post = factory.db.get("posts", pid)
    assert post["status"] == "scheduled"
    assert post["meta"]["claims_verified"]["claims"][0].startswith("HYSA")
    pubs = factory.db.query("SELECT * FROM publications WHERE post_id = ?", [pid])
    assert {p["platform"] for p in pubs} == {"instagram", "youtube", "tiktok", "facebook"}
    assert all(p["status"] == "queued" for p in pubs)


def test_form_blocked_post_cannot_be_approved(client, factory):
    pid = factory.seed_ids["blocked"]
    assert factory.db.get("posts", pid)["status"] == "blocked"
    r = client.post(f"/posts/{pid}/approve", data={"verified": ["0"]})
    assert "blocked by a guardrail" in r.text
    assert factory.db.get("posts", pid)["status"] == "blocked"


def test_form_edit_rechecks_and_unblocks(client, factory):
    pid = factory.seed_ids["blocked"]
    r = client.post(f"/posts/{pid}/edit", data={
        "title": "The HYSA I use", "caption": "Why I picked this HYSA. Affiliate link: I may earn a commission. Made with AI tools."})
    assert r.status_code == 200
    post = factory.db.get("posts", pid)
    assert post["status"] == "in_review" and post["meta"]["human_edited"] is True


def test_form_reject_needs_reason(client, factory):
    pid = factory.seed_ids["carousel"]
    assert "Give a reason" in client.post(f"/posts/{pid}/reject", data={"reason": " "}).text
    client.post(f"/posts/{pid}/reject", data={"reason": "weak hook"})
    post = factory.db.get("posts", pid)
    assert post["status"] == "rejected" and post["review_notes"] == "weak hook"


def test_form_produce_and_rerender_run_in_background(client, factory):
    idea = factory.seed_ids["ideas"][0]
    r = client.post(f"/ideas/{idea}/produce")
    assert r.status_code == 200 and "Producing idea" in r.text
    client.app.state.jobs.wait()
    post = factory.db.one("SELECT * FROM posts WHERE idea_id = ?", [idea])
    assert post and post["status"] in ("in_review", "blocked") and post["assets"]["video"]
    assert factory.db.get("ideas", idea)["status"] == "used"
    client.post(f"/posts/{post['id']}/rerender")
    client.app.state.jobs.wait()
    job = client.app.state.jobs.all()[0]
    assert job.kind == "render" and job.status == "done"


def test_form_idea_status_and_generate(client, factory):
    idea = factory.seed_ids["ideas"][2]
    client.post(f"/ideas/{idea}/status", data={"status": "rejected"})
    assert factory.db.get("ideas", idea)["status"] == "rejected"
    before = factory.db.scalar("SELECT COUNT(*) FROM ideas")
    client.post("/ideas/generate", data={"brand": BRAND, "n": "4"})  # online unchecked -> offline signals
    client.app.state.jobs.wait()
    assert factory.db.scalar("SELECT COUNT(*) FROM ideas") > before


def test_calendar_publish_due_and_metrics(client, factory):
    pid = factory.seed_ids["scheduled"]
    factory.db.execute("UPDATE publications SET scheduled_at = ? WHERE post_id = ?",
                       [(datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(), pid])
    assert "due now" in client.get("/calendar").text
    r = client.post("/publish/due")
    assert "dry run" in r.text
    assert {p["status"] for p in factory.db.query("SELECT status FROM publications WHERE post_id = ?", [pid])} <= {"dry_run", "manual"}
    assert "Captured" in client.post("/metrics/collect").text


# --------------------------------------------------------------------------- JSON API
def test_api_health_and_posts(client, factory):
    assert client.get("/api/health").json() == {"ok": True}
    posts = client.get("/api/posts", params={"status": "in_review"}).json()["posts"]
    assert posts and all(p["status"] == "in_review" for p in posts)
    review = next(p for p in posts if p["id"] == factory.seed_ids["review"])
    assert len(review["claims_to_verify"]) == 2
    assert client.get("/api/posts", params={"status": "in_review,blocked"}).status_code == 200
    r = client.get("/api/posts/9999")
    assert r.status_code == 404 and "No post #9999" in r.json()["error"]


def test_api_approve_requires_verified_claims(client, factory):
    pid = factory.seed_ids["review"]
    r = client.post(f"/api/posts/{pid}/approve", json={})
    assert r.status_code == 403 and "fact-checked" in r.json()["error"]
    r = client.post(f"/api/posts/{pid}/approve", json={"verified": [0]})
    assert r.status_code == 403
    r = client.post(f"/api/posts/{pid}/approve",
                    json={"verified": [0, "Roth IRA limit is $7,000 for 2026"], "schedule": True,
                          "platforms": ["youtube"]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["post"]["status"] == "approved" and len(body["publications"]) == 1
    assert factory.db.get("posts", pid)["status"] == "scheduled"


def test_api_errors_map_to_status_codes(client, factory):
    blocked = factory.seed_ids["blocked"]
    assert client.post(f"/api/posts/{blocked}/approve", json={"verified": [0]}).status_code == 403
    assert client.post(f"/api/posts/{blocked}/schedule").status_code == 403  # not approved
    assert client.post("/api/posts/9999/reject", json={"reason": "x"}).status_code == 404
    assert client.post(f"/api/posts/{blocked}/reject", json={"reason": ""}).status_code == 400
    assert client.post("/api/ideas/generate", json={"brand": "nope", "n": 2}).status_code == 404
    assert client.post("/api/posts/1/schedule", json={"at": "tomorrow"}).status_code in (400, 403)
    assert client.post("/api/ideas/generate", json={"n": 2}).status_code == 422


def test_api_reject_and_schedule(client, factory):
    carousel = factory.seed_ids["carousel"]
    r = client.post(f"/api/posts/{carousel}/reject", json={"reason": "off-brand"})
    assert r.status_code == 200 and r.json()["post"]["status"] == "rejected"
    pid = add_post(factory, "Sinking funds for irregular bills", claims=[])
    factory.approve(pid)
    at = (datetime.now(timezone.utc) + timedelta(days=3)).replace(microsecond=0).isoformat()
    r = client.post(f"/api/posts/{pid}/schedule", json={"platforms": ["instagram"], "at": at})
    assert r.status_code == 200, r.text
    pubs = r.json()["publications"]
    assert len(pubs) == 1 and pubs[0]["platform"] == "instagram" and pubs[0]["scheduled_at"] == at


def test_api_generate_produce_publish_metrics_daily(client, factory):
    r = client.post("/api/ideas/generate", json={"brand": BRAND, "n": 3, "online": False})
    assert r.status_code == 200, r.text
    new_ids = r.json()["job"]["result"]["idea_ids"]
    assert new_ids
    r = client.post(f"/api/ideas/{new_ids[0]}/produce", json={"wait": True})
    assert r.status_code == 200, r.text
    post_id = r.json()["job"]["result"]["post_id"]
    assert factory.db.get("posts", post_id)["status"] in ("in_review", "blocked")
    r = client.post(f"/api/ideas/{new_ids[1]}/produce", json={"wait": False})
    assert r.status_code == 202
    job_id = r.json()["job"]["id"]
    client.app.state.jobs.wait()
    assert client.get(f"/api/jobs/{job_id}").json()["job"]["status"] == "done"
    assert client.get("/api/jobs/999").status_code == 404

    r = client.post("/api/publish/due")
    assert r.status_code == 200 and r.json()["dry_run"] is True
    r = client.post("/api/metrics/collect")
    assert r.status_code == 200 and "snapshots" in r.json()
    r = client.post("/api/daily", json={"brand": BRAND, "online": False, "n_produce": 1})
    assert r.status_code == 200, r.text
    report = r.json()["job"]["result"]
    assert report["brand"] == BRAND and "published" in report


def test_api_job_failure_is_500(client, factory, monkeypatch):
    import contentfactory.media as media

    def boom(*a, **k):
        raise RuntimeError("ffmpeg exploded")
    monkeypatch.setattr(media, "render_post", boom)
    idea = factory.seed_ids["ideas"][1]
    r = client.post(f"/api/ideas/{idea}/produce", json={})
    assert r.status_code == 500 and "ffmpeg exploded" in r.json()["error"]


# --------------------------------------------------------------------------- deps contract
def test_deps_contract():
    assert money(123456) == "$1,234.56" and money(-500, "EUR") == "-€5.00" and money(None) == "$0.00"
    past = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    assert humanize(past) == "3 h ago"
    assert sparkline([1, 2, 3]) and sparkline([1]) == ""
    loader_dirs = [str(p) for p in templates.env.loader.searchpath]
    assert any(d.endswith("web/templates") for d in loader_dirs)
    assert any(d.endswith("business/templates") for d in loader_dirs)
    for f in ("money", "humanize", "pretty_json", "localtime", "media_url"):
        assert f in templates.env.filters


def test_today_post_by_hand(client, factory):
    from datetime import datetime, timedelta, timezone
    pid = factory.db.insert("posts", {"brand": BRAND, "format": "short", "status": "scheduled", "title": "Hand post",
                                      "caption": "Copy me", "script": {}, "hashtags": [], "disclosure": "",
                                      "meta": {}, "assets": {}})
    pub = factory.db.insert("publications", {"post_id": pid, "platform": "tiktok", "status": "queued",
                                             "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()})
    r = client.get("/today")
    assert "Post by hand" in r.text and "Hand post" in r.text and "Copy caption" in r.text
    assert "post by hand" in client.get("/calendar").text
    r = client.post(f"/manual/{pub}/done", data={"url": "https://www.tiktok.com/@x/video/1"}, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert factory.db.get("publications", pub)["status"] == "published"


def test_fast_review(client, factory):
    ids = factory.seed_ids
    r = client.get("/review/fast")
    assert r.status_code == 200 and "Fast review" in r.text and "Approve a whole week" in r.text
    assert "2 claim(s) not ticked" in r.text or "Not ready" in r.text
    rid = ids["review"]
    r = client.post(f"/review/fast/{rid}/tick", data={"claims": ["0"]})
    assert r.json()["why"] == "1 claim(s) not ticked"
    client.post(f"/review/fast/{rid}/tick", data={"claims": ["0", "1"]})
    from contentfactory.web.fastreview import week_of
    wk = week_of(factory.db.get("posts", rid)).isoformat()
    r = client.post("/review/fast/approve-week", data={"week": wk, "brand": BRAND}, follow_redirects=False)
    assert r.status_code == 303 and "Approved" in r.headers["location"]
    assert factory.db.get("posts", rid)["status"] == "approved"
    assert factory.db.get("posts", ids["blocked"])["status"] == "blocked"  # never batch-approved
    assert "Skipped" in r.headers["location"] or "err=" in r.headers["location"]


def test_fast_review_gate(client, factory):
    from contentfactory import review
    pid = add_post(factory, "Needs a native read", claims=[])
    review.require(factory, pid, "native_review")
    from contentfactory.web.queries import review_queue
    idx = [p["id"] for p in review_queue(factory)].index(pid)
    r = client.get(f"/review/fast?i={idx}")
    assert "needs native review" in r.text and "Native review passed" in r.text
    r = client.post(f"/review/fast/{pid}/pass", data={"stage": "native_review", "by": "Ana"}, follow_redirects=False)
    assert r.status_code == 303
    assert review.status(factory.db.get("posts", pid), factory.brand(BRAND)) == "draft"
