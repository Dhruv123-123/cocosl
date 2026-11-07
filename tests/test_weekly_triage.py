from datetime import datetime, timedelta, timezone

from contentfactory.stats import import_files
from contentfactory.triage import collect, to_markdown, to_text
from contentfactory.weekly_html import brand_page, save, to_html

BRAND = "money-made-simple"
YT = """Content,Video title,Video publish time,Duration,Views,Watch time (hours),Subscribers,Impressions,Impressions click-through rate (%)
V1,Sinking funds explained,"Nov 2, 2026",612,9000,110.2,35,40000,6.0
V2,"The 50/30/20 budget on $3,200","Nov 3, 2026",40,500,10.3,5,10000,1.5
V3,Index funds for beginners,"Nov 4, 2026",40,2000,10.3,5,10000,1.5
V4,Credit score myths,"Nov 5, 2026",40,1500,10.3,5,10000,1.5
V5,APR vs APY,"Nov 6, 2026",40,300,10.3,5,10000,1.5
"""


def test_weekly_html_per_brand(factory, tmp_path):
    p = tmp_path / "Table data.csv"
    p.write_text(YT)
    import_files(factory, BRAND, [p])
    factory.db.insert("ideas", {"brand": BRAND, "title": "Sinking funds for car repairs", "pillar": "", "status": "new"})
    page = brand_page(factory, factory.brand(BRAND))
    assert page["best"][0]["title"] == "Sinking funds explained" and page["worst"][0]["title"] == "APR vs APY"
    topics = [i["topic"] for i in page["ideas"]]
    assert "Sinking funds for car repairs" in topics and any(t.startswith("Follow-up to") for t in topics)
    html = to_html(page, "2026-11-02")
    assert "Best posts" in html and "Suggested next topics" in html and "prefers-color-scheme" in html
    paths = save(factory)
    assert paths[0].name == "index.html" and {p.name for p in paths[1:]} == {f"{s}.html" for s in factory.brands()}
    assert "No exports imported yet" in (paths[0].parent / "tiny-histories.html").read_text()


def test_triage_lists_what_waits_on_you(factory):
    pid = factory.db.insert("posts", {"brand": BRAND, "format": "short", "status": "blocked", "title": "Loan maths",
                                      "script": {}, "checks": {"status": "block", "checks": [
                                          {"name": "number_check", "level": "block", "message": "says 450, maths gives 500.95"}]}})
    tt = factory.db.insert("posts", {"brand": BRAND, "format": "short", "status": "scheduled", "title": "Hand post",
                                     "script": {}, "caption": "c"})
    factory.db.insert("publications", {"post_id": tt, "platform": "tiktok", "status": "manual",
                                       "scheduled_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()})
    items = collect(factory)
    kinds = [(i.urgency, i.kind) for i in items]
    assert ("now", "post by hand (tiktok)") in kinds
    assert any(i.kind == "review (blocked)" and f"#{pid}" in i.what and "500.95" in i.what for i in items)
    assert any(i.urgency == "setup" and i.kind == "brand file" for i in items)
    assert not any("tiktok" in i.kind and "missing" in i.what for i in items)  # TikTok is by hand: no keys nagging
    assert [i.urgency for i in items] == sorted((i.urgency for i in items), key=["now", "soon", "setup"].index)
    assert "Do now" in to_text(items) and "- [ ]" in to_markdown(items)
