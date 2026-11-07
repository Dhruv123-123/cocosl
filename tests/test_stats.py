from contentfactory.insights import latest_metrics
from contentfactory.stats import detect, import_files, scorecard, to_markdown, _read

BRAND = "money-made-simple"

YT = """Content,Video title,Video publish time,Duration,Views,Watch time (hours),Subscribers,Impressions,Impressions click-through rate (%)
Total,,,,3500,120.5,40,50000,5.1
VID1,Stop letting your bank underpay you,"Nov 2, 2026",612,3000,110.2,35,40000,6.0
abcXYZ,A video nobody made here,"Nov 3, 2026",40,500,10.3,5,10000,1.5
"""
TT = """Video title,Video link,Post time,Total views,Total likes,Total comments,Total shares
The budget that finally stuck #money,https://www.tiktok.com/@mms/video/7300000000000000001,2026-11-04,12000,900,40,120
"""
VISITORS = "date,visitors,pageviews\n2026-11-01,120,200\n2026-11-02,80,150\n"
GOALS = "name,unique_conversions,total_conversions,conversion_rate\nNewsletter signup,14,15,7\nOutbound Link: Click,33,40,16\n"
CAMPAIGNS = "name,visitors,bounce_rate\nweek1-budget,90,40\n,30,50\n"


def _post(f, title, platform=None, remote="", status="published"):
    pid = f.db.insert("posts", {"brand": BRAND, "format": "short", "status": status, "title": title, "script": {}})
    if platform:
        f.db.insert("publications", {"post_id": pid, "platform": platform, "status": status if status == "published" else "dry_run",
                                     "remote_id": remote, "scheduled_at": "2026-11-02T17:00:00+00:00",
                                     "published_at": "2026-11-02T17:00:00+00:00"})
    return pid


def test_import_scorecard_and_learning(factory, tmp_path):
    f = factory
    yt_post = _post(f, "Stop letting your bank underpay you", "youtube", remote="VID1")
    tt_post = _post(f, "The budget that finally stuck", "tiktok", status="approved")  # posted by hand
    files = {"Table data.csv": YT, "tiktok-content.csv": TT, "visitors.csv": VISITORS, "conversions.csv": GOALS,
             "utm_campaigns.csv": CAMPAIGNS}
    paths = []
    for name, text in files.items():
        (tmp_path / name).write_text(text)
        paths.append(tmp_path / name)
    kinds = [detect(p, _read(p)) for p in paths]
    assert kinds == ["youtube", "tiktok", "plausible_visitors", "plausible_goals", "plausible_campaigns"]
    res = import_files(f, BRAND, paths)
    assert res["matched"] == 2 and res["unmatched"] == ["youtube: A video nobody made here"]
    # the hand-posted TikTok now counts as published, with views the learning loop can read
    assert f.db.get("posts", tt_post)["status"] == "published"
    views = {r["post_id"]: r["views"] for r in latest_metrics(f.db, brand=BRAND)}
    assert views[yt_post] == 3000 and views[tt_post] == 12000
    card = scorecard(f, BRAND)
    yt = card["platforms"]["youtube"]
    assert yt["views"] == 3500 and yt["watch_hours"] == 120.5 and abs(yt["ctr"] - 5.1) < 0.01
    assert card["site"] == {"import": card["site"]["import"], "visitors": 200, "signups": 14, "clicks": 33,
                            "campaigns": [{"name": "week1-budget", "visitors": 90}, {"name": "", "visitors": 30}]}
    text = to_markdown([card, scorecard(f, "tiny-histories")])
    assert "**youtube**: 3,500 views" in text and "14 signups" in text and "No exports imported yet" in text


def test_reimport_shows_change(factory, tmp_path):
    p = tmp_path / "Table data.csv"
    p.write_text(YT)
    import_files(factory, BRAND, [p])
    import time
    time.sleep(1.1)
    p.write_text(YT.replace("3000", "6000").replace("3500", "6500"))
    import_files(factory, BRAND, [p])
    assert "vs previous export" in to_markdown([scorecard(factory, BRAND)])
