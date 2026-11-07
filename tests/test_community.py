"""Community inbox: comment fetching (mocked official APIs), triage, ideas,
drafts, human-only sending, dry run, rate limit and the /inbox page."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

import httpx
import pytest
from fastapi.testclient import TestClient

from contentfactory.community import (MAX_REPLIES_PER_HOUR, RateLimited, collect_comments, draft_replies,
                                      save_as_idea, send_reply, set_status)
from contentfactory.community import store, triage
from contentfactory.community.drafting import AI_LINE, AFFILIATE_NOTE, ReplyDraft, enforce
from contentfactory.community.platforms import YT_FORCE_SSL_SCOPE
from contentfactory.publish._http import GRAPH_API_VERSION

BRAND = "money-made-simple"
TOKEN = "inbox-test-token-value"


# --------------------------------------------------------------------------- fixtures
def _publish(factory, platform: str, remote_id: str, title: str = "HYSA in 60 seconds") -> int:
    db = factory.db
    post_id = db.insert("posts", {"brand": BRAND, "format": "short", "status": "published", "title": title})
    return db.insert("publications", {"post_id": post_id, "platform": platform, "status": "published",
                                      "remote_id": remote_id, "url": f"https://example.com/{remote_id}",
                                      "published_at": datetime.now(timezone.utc).isoformat()})


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("IG_USER_ID", "17841400000000000")
    monkeypatch.setenv("IG_ACCESS_TOKEN", "ig-secret")
    monkeypatch.setenv("YT_CLIENT_ID", "cid")
    monkeypatch.setenv("YT_CLIENT_SECRET", "csecret")
    monkeypatch.setenv("YT_REFRESH_TOKEN", "rtoken")


IG_PAGE_1 = {
    "data": [
        {"id": "c1", "text": "How much should I keep in an emergency fund?", "username": "sam_r",
         "timestamp": "2026-11-06T10:00:00+0000", "like_count": 4,
         "replies": {"data": [
             {"id": "r1", "text": "Thanks, great question!", "username": "moneymadesimple",
              "timestamp": "2026-11-06T11:00:00+0000", "like_count": 0},
             {"id": "r2", "text": "Same question here, how many months?", "username": "jo",
              "timestamp": "2026-11-06T12:00:00+0000", "like_count": 1}]}},
        {"id": "c2", "text": "DM me on WhatsApp to earn $500 a day with crypto signals", "username": "profit_guru",
         "timestamp": "2026-11-06T09:00:00+0000", "like_count": 0},
    ],
    "paging": {"cursors": {"after": "CUR1"}, "next": "https://graph.facebook.com/next"},
}
IG_PAGE_2 = {
    "data": [{"id": "c3", "text": "This was so helpful, thank you", "username": "lee",
              "timestamp": "2026-11-05T09:00:00+0000", "like_count": 2}],
    "paging": {"cursors": {"after": "CUR2"}},
}


def ig_transport(calls: list):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        path = request.url.path
        if request.method == "GET" and path.endswith("/m1/comments"):
            assert path.startswith(f"/{GRAPH_API_VERSION}/")
            q = request.url.params
            assert q["access_token"] == "ig-secret"
            assert "id,text,username,timestamp,like_count" in q["fields"] and "replies{" in q["fields"]
            return httpx.Response(200, json=IG_PAGE_2 if q.get("after") == "CUR1" else IG_PAGE_1)
        if request.method == "POST" and path.endswith("/replies"):
            form = parse_qs(request.content.decode())
            assert form["access_token"] == ["ig-secret"]
            return httpx.Response(200, json={"id": "reply-" + path.split("/")[-2], "echo": form["message"][0]})
        return httpx.Response(404, json={"error": {"message": f"unexpected {request.method} {path}", "code": 803}})
    return httpx.MockTransport(handler)


YT_THREADS = {
    "kind": "youtube#commentThreadListResponse",
    "items": [
        {"id": "t1", "snippet": {
            "channelId": "UC_OWN", "videoId": "vid1", "canReply": True, "totalReplyCount": 1,
            "topLevelComment": {"id": "yc1", "snippet": {
                "authorDisplayName": "@river", "authorChannelId": {"value": "UC_RIVER"},
                "textDisplay": "Can you do a video on Roth vs traditional IRA?", "likeCount": 7,
                "publishedAt": "2026-11-06T08:00:00Z"}}},
         "replies": {"comments": [{"id": "yc1.r1", "snippet": {
             "authorDisplayName": "@moneymadesimple", "authorChannelId": {"value": "UC_OWN"},
             "textDisplay": "On the list!", "parentId": "yc1", "likeCount": 0,
             "publishedAt": "2026-11-06T09:00:00Z"}}]}},
        {"id": "t2", "snippet": {
            "channelId": "UC_OWN", "videoId": "vid1",
            "topLevelComment": {"id": "yc2", "snippet": {
                "authorDisplayName": "@doubter", "authorChannelId": {"value": "UC_D"},
                "textDisplay": "This is misleading, rates dropped last month", "likeCount": 0,
                "publishedAt": "2026-11-06T07:00:00Z"}}}},
    ],
}


def yt_transport(calls: list):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "yt-access", "expires_in": 3600})
        assert request.headers.get("authorization") == "Bearer yt-access"
        if request.method == "GET" and request.url.path == "/youtube/v3/commentThreads":
            q = request.url.params
            assert q["part"] == "snippet,replies" and q["videoId"] == "vid1" and q["textFormat"] == "plainText"
            return httpx.Response(200, json=YT_THREADS)
        if request.method == "POST" and request.url.path == "/youtube/v3/comments":
            assert request.url.params["part"] == "snippet"
            body = json.loads(request.content)
            return httpx.Response(200, json={"kind": "youtube#comment", "id": "new-reply",
                                             "snippet": {**body["snippet"], "authorChannelId": {"value": "UC_OWN"}}})
        return httpx.Response(404, json={"error": {"code": 404, "message": "unexpected"}})
    return httpx.MockTransport(handler)


def _by_remote(factory, remote_id):
    return factory.db.one("SELECT * FROM comments WHERE remote_id = ?", [remote_id])


# --------------------------------------------------------------------------- fetching
def test_collect_instagram_paginates_skips_own_and_dedupes(factory, creds):
    pub = _publish(factory, "instagram", "m1")
    calls: list = []
    report = collect_comments(factory, transport=ig_transport(calls))
    assert report["fetched"] == 5 and report["skipped_own"] == 1 and report["new"] == 4, report
    assert len([c for c in calls if c.method == "GET"]) == 2  # followed the after cursor once
    c1, r2 = _by_remote(factory, "c1"), _by_remote(factory, "r2")
    assert c1["publication_id"] == pub and c1["author"] == "sam_r" and c1["like_count"] == 4
    assert c1["brand"] == BRAND and c1["created_at_remote"].startswith("2026-11-06")
    assert r2["parent_remote_id"] == "c1"
    assert _by_remote(factory, "r1") is None  # our own reply
    assert _by_remote(factory, "c2")["status"] == "flagged"
    again = collect_comments(factory, transport=ig_transport([]))
    assert again["new"] == 0
    assert factory.db.scalar("SELECT COUNT(*) FROM comments") == 4


def test_collect_youtube_threads_and_own_channel(factory, creds):
    _publish(factory, "youtube", "vid1")
    report = collect_comments(factory, platforms=["youtube"], transport=yt_transport([]))
    assert report["new"] == 2 and report["skipped_own"] == 1, report
    idea_req = _by_remote(factory, "yc1")
    assert idea_req["author"] == "@river" and idea_req["like_count"] == 7
    assert idea_req["category"] == "content_idea" and idea_req["idea_id"]
    assert _by_remote(factory, "yc2")["category"] == "criticism"


def test_collect_reports_missing_credentials(factory):
    _publish(factory, "instagram", "m1")
    report = collect_comments(factory, transport=ig_transport([]))
    assert report["new"] == 0 and any("IG_ACCESS_TOKEN" in e for e in report["errors"])


# --------------------------------------------------------------------------- triage
@pytest.mark.parametrize("text,cat", [
    ("How do I open a Roth IRA?", "question"),
    ("Love this, so helpful 🔥", "praise"),
    ("This is misleading and outdated", "criticism"),
    ("Check my profile for free followers www.boost.xyz", "spam"),
    ("you're an idiot", "abuse"),
    ("Where can I buy the budget template?", "purchase_intent"),
    ("Can you make a video on credit card churning", "content_idea"),
    ("first", "other"),
])
def test_keyword_fallback(text, cat):
    assert triage.keyword_category(text) == cat


def test_llm_cannot_unflag_keyword_spam(factory):
    class FakeLLM:
        provider = "anthropic"

        def structured(self, schema, **kw):
            return schema(items=[triage.TriageItem(index=0, category="praise", reason="model", idea_title=""),
                                 triage.TriageItem(index=1, category="question", reason="model", idea_title="")])
    items = triage.classify(FakeLLM(), factory.brand(BRAND),
                            [{"text": "Message me on telegram for investment manager"}, {"text": "Is a HYSA safe?"}])
    assert items[0].category == "spam"
    assert items[1].category == "question" and items[1].idea_title == "Is a HYSA safe?"


def test_questions_become_ideas_once(factory, creds):
    _publish(factory, "instagram", "m1")
    collect_comments(factory, transport=ig_transport([]))
    ideas = factory.db.query("SELECT * FROM ideas WHERE source = 'comment'")
    titles = [i["title"] for i in ideas]
    assert "How much should I keep in an emergency fund?" in titles
    assert len(titles) == len(set(titles))
    c1 = _by_remote(factory, "c1")
    assert save_as_idea(factory, c1["id"]) is None  # already linked
    # a new comment asking the same question links to the existing idea instead of duplicating it
    cid, _ = store.upsert(factory.db, {"brand": BRAND, "platform": "instagram", "remote_id": "dup",
                                       "text": "How much should I keep in an emergency fund??", "status": "new"})
    assert save_as_idea(factory, cid) is None
    assert factory.db.get("comments", cid)["idea_id"] == c1["idea_id"]
    meta = factory.db.get("ideas", c1["idea_id"])["meta"]
    assert meta["comment_id"] == c1["id"] and meta["platform"] == "instagram"
    spam = _by_remote(factory, "c2")
    with pytest.raises(PermissionError):
        save_as_idea(factory, spam["id"])


# --------------------------------------------------------------------------- drafts
def test_draft_replies_skips_flagged_and_sends_nothing(factory, creds):
    _publish(factory, "instagram", "m1")
    collect_comments(factory, transport=ig_transport([]))
    ids = draft_replies(factory, limit=10)
    assert len(ids) == 3
    assert _by_remote(factory, "c2")["status"] == "flagged" and not _by_remote(factory, "c2")["draft"]
    c3 = _by_remote(factory, "c3")
    assert c3["status"] == "drafted" and c3["draft"]
    assert factory.db.scalar("SELECT COUNT(*) FROM comments WHERE status = 'replied'") == 0


def test_enforce_rules(factory):
    brand = factory.brand(BRAND)
    text, _ = enforce(brand, {"text": "are you a bot?"}, ReplyDraft(reply="Haha, nope!", needs_human=False, note=""))
    assert AI_LINE in text
    text, notes = enforce(brand, {"text": "is this real?"},
                          ReplyDraft(reply="I'm a real person, promise.", needs_human=False, note=""))
    assert "real person" not in text and AI_LINE in text and any("human" in n for n in notes)
    text, _ = enforce(brand, {"text": "link?"},
                      ReplyDraft(reply="Here: https://example.com/go/hysa", needs_human=False, note=""))
    assert AFFILIATE_NOTE in text
    _, notes = enforce(brand, {"text": "should I?"},
                       ReplyDraft(reply="Guaranteed returns, you should invest in it", needs_human=False, note=""))
    assert any("promise" in n for n in notes)


# --------------------------------------------------------------------------- sending
def _comment(factory, platform="instagram", remote="c9", parent="", status="new", draft="Thanks!"):
    cid, _ = store.upsert(factory.db, {"brand": BRAND, "platform": platform, "remote_id": remote,
                                       "parent_remote_id": parent, "text": "hi", "status": status,
                                       "category": "praise", "draft": draft})
    return cid


def test_dry_run_send_calls_nothing(factory):
    calls: list = []
    cid = _comment(factory)
    res = send_reply(factory, cid, "Thank you!", transport=ig_transport(calls))
    assert res["status"] == "replied (dry run)" and not calls
    row = factory.db.get("comments", cid)
    assert row["status"] == "replied" and row["dry_run"] == 1 and row["reply_text"] == "Thank you!"
    with pytest.raises(ValueError):
        send_reply(factory, cid, "again")


def test_live_send_instagram_targets_top_level(factory, creds):
    factory.settings.dry_run = False
    calls: list = []
    cid = _comment(factory, remote="r5", parent="c5")
    res = send_reply(factory, cid, "Glad it helped!", transport=ig_transport(calls))
    assert res["remote_id"] == "reply-c5"
    post = [c for c in calls if c.method == "POST"][0]
    assert post.url.path == f"/{GRAPH_API_VERSION}/c5/replies"
    assert parse_qs(post.content.decode())["message"] == ["Glad it helped!"]
    row = factory.db.get("comments", cid)
    assert row["dry_run"] == 0 and row["reply_remote_id"] == "reply-c5"


def test_live_send_youtube_comments_insert(factory, creds):
    factory.settings.dry_run = False
    calls: list = []
    cid = _comment(factory, platform="youtube", remote="yc7")
    send_reply(factory, cid, "Thanks for watching!", transport=yt_transport(calls))
    post = [c for c in calls if c.method == "POST" and c.url.host == "www.googleapis.com"][0]
    assert json.loads(post.content) == {"snippet": {"parentId": "yc7", "textOriginal": "Thanks for watching!"}}


def test_youtube_scope_hint_on_403(factory, creds):
    factory.settings.dry_run = False

    def handler(request):
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "yt-access", "expires_in": 3600})
        return httpx.Response(403, json={"error": {"code": 403, "message": "Request had insufficient authentication scopes.",
                                                   "errors": [{"reason": "insufficientPermissions"}]}})
    cid = _comment(factory, platform="youtube", remote="yc8")
    from contentfactory.publish.base import PublishError
    with pytest.raises(PublishError, match="force-ssl"):
        send_reply(factory, cid, "hi", transport=httpx.MockTransport(handler))
    assert YT_FORCE_SSL_SCOPE.endswith("youtube.force-ssl")
    assert factory.db.get("comments", cid)["status"] == "new"


def test_flagged_never_sent(factory):
    cid = _comment(factory, status="flagged")
    with pytest.raises(PermissionError):
        send_reply(factory, cid, "hello")


def test_rate_limit_per_platform(factory, creds):
    factory.settings.dry_run = False
    now = datetime.now(timezone.utc)
    for i in range(MAX_REPLIES_PER_HOUR):
        cid = _comment(factory, remote=f"old{i}")
        factory.db.update("comments", cid, {"status": "replied", "dry_run": 0,
                                            "replied_at": (now - timedelta(minutes=i)).replace(microsecond=0).isoformat()})
    stale = _comment(factory, remote="stale")
    factory.db.update("comments", stale, {"status": "replied", "dry_run": 0,
                                          "replied_at": (now - timedelta(hours=2)).isoformat()})
    calls: list = []
    cid = _comment(factory, remote="next")
    with pytest.raises(RateLimited):
        send_reply(factory, cid, "hi", transport=ig_transport(calls))
    assert not calls
    yt = _comment(factory, platform="youtube", remote="ytok")  # other platform has its own budget
    send_reply(factory, yt, "hi", transport=yt_transport([]))
    # an hour later the window has rolled over
    send_reply(factory, cid, "hi", transport=ig_transport(calls), now=now + timedelta(minutes=61))
    assert factory.db.get("comments", cid)["status"] == "replied"


# --------------------------------------------------------------------------- page
@pytest.fixture
def inbox_client(factory, creds):
    from contentfactory.web.app import create_app
    factory.settings.dashboard_token = TOKEN
    _publish(factory, "instagram", "m1")
    collect_comments(factory, transport=ig_transport([]))
    draft_replies(factory, limit=10)
    app = create_app(factory)  # create_app mounts the inbox router itself
    with TestClient(app, client=("203.0.113.9", 4000), follow_redirects=False,
                    headers={"Authorization": f"Bearer {TOKEN}"}) as c:
        yield c


def test_inbox_page_renders_and_filters(inbox_client, factory):
    r = inbox_client.get("/inbox")
    assert r.status_code == 200, r.text[:400]
    html = r.text
    assert "Inbox" in html and "HYSA in 60 seconds" in html and "@sam_r" in html
    assert 'name="reply"' in html and ("Save as idea" in html or "idea #" in html)
    assert "Flagged comments are never replied to" in html  # spam card
    assert 'href="/inbox"' in html  # nav entry
    spam_only = inbox_client.get("/inbox?category=spam").text
    assert "profit_guru" in spam_only and "@sam_r" not in spam_only
    assert inbox_client.get("/inbox?status=replied").text.count('class="card cmt') == 0
    assert inbox_client.get(f"/inbox?brand={BRAND}&status=all").status_code == 200
    assert inbox_client.get("/inbox?status=bogus").status_code == 400
    anon = TestClient(inbox_client.app, client=("203.0.113.9", 4000), follow_redirects=False)
    assert anon.get("/inbox").status_code == 303


def test_inbox_actions(inbox_client, factory):
    c3 = _by_remote(factory, "c3")
    r = inbox_client.post(f"/inbox/{c3['id']}/send", data={"reply": "Thank you, Lee!"})
    assert r.status_code == 303 and "dry+run" in r.headers["location"]
    row = factory.db.get("comments", c3["id"])
    assert row["status"] == "replied" and row["dry_run"] == 1
    assert "replied (dry run)" in inbox_client.get("/inbox?status=replied").text
    r2 = _by_remote(factory, "r2")
    inbox_client.post(f"/inbox/{r2['id']}/save", data={"reply": "Edited draft"})
    assert factory.db.get("comments", r2["id"])["draft"] == "Edited draft"
    inbox_client.post(f"/inbox/{r2['id']}/status", data={"status": "ignored"})
    assert factory.db.get("comments", r2["id"])["status"] == "ignored"
    spam = _by_remote(factory, "c2")
    r = inbox_client.post(f"/inbox/{spam['id']}/send", data={"reply": "hi"})
    assert r.status_code == 303 and "err=" in r.headers["location"]
    assert factory.db.get("comments", spam["id"])["status"] == "flagged"
    set_status(factory.db, spam["id"], "new")
    r = inbox_client.post(f"/inbox/{spam['id']}/redraft")
    assert r.status_code == 303
    c1 = _by_remote(factory, "c1")
    r = inbox_client.post(f"/inbox/{c1['id']}/idea")
    assert r.status_code == 303 and "Already" in r.headers["location"].replace("+", " ")


def test_triage_tolerates_short_questions_and_bot_questions(factory):
    a, _ = store.upsert(factory.db, {"brand": BRAND, "platform": "instagram", "remote_id": "q1", "text": "Why?"})
    b, _ = store.upsert(factory.db, {"brand": BRAND, "platform": "instagram", "remote_id": "q2", "text": "Are you a bot?"})
    from contentfactory.community import triage_comments
    triage_comments(factory, [a, b])
    assert factory.db.get("comments", a)["category"] == "question"
    assert not factory.db.get("comments", a)["idea_id"] and not factory.db.get("comments", b)["idea_id"]


def test_inbox_mounted_and_cli_registered(factory, monkeypatch):
    from contentfactory.cli import build_parser
    from contentfactory.web.app import create_app
    factory.settings.dashboard_token = "t"
    client = TestClient(create_app(factory), client=("203.0.113.9", 4000), headers={"Authorization": "Bearer t"})
    assert client.get("/inbox").status_code == 200
    args = build_parser().parse_args(["comments", "draft", "--limit", "3"])
    assert args.limit == 3
