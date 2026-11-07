import csv
import io
import zipfile
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from contentfactory import export_week as ew


def _pub(f, day, hour, platform, title, status="scheduled"):
    out = f.settings.output_dir / "money-made-simple" / f"{title}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(title.encode())
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": status, "title": title,
                                "caption": f"Caption for {title}.", "script": {"title": title}, "hashtags": ["budget"],
                                "disclosure": "", "meta": {}, "assets": {"video": f"money-made-simple/{title}.mp4"}})
    at = datetime.combine(day, time(hour), ZoneInfo("America/New_York")).isoformat()
    return f.db.insert("publications", {"post_id": pid, "platform": platform, "status": "queued", "scheduled_at": at})


def test_export_week_zip(factory, monkeypatch):
    monkeypatch.setenv("MANUAL_PLATFORMS", "tiktok,pinterest")
    monday = date(2026, 11, 23)
    _pub(factory, monday + timedelta(days=2), 18, "tiktok", "Wednesday post")
    _pub(factory, monday, 9, "tiktok", "Monday post")
    _pub(factory, monday, 12, "youtube", "Monday short")
    _pub(factory, monday + timedelta(days=1), 9, "tiktok", "Unreviewed", status="in_review")
    _pub(factory, monday + timedelta(days=8), 9, "tiktok", "Next week")
    path = ew.export(factory, "money-made-simple", monday)
    assert path.name == "money-made-simple-week-2026-11-23.zip"
    z = zipfile.ZipFile(path)
    names = z.namelist()
    folders = sorted({n.split("/")[1] for n in names if n.count("/") >= 2})
    assert folders[0].startswith("01-Mon-0900-tiktok") and folders[1].startswith("02-Mon-1200-youtube")
    assert folders[2].startswith("03-Wed-1800-tiktok") and len(folders) == 3
    root = names[0].split("/")[0]
    week = z.read(f"{root}/WEEK.md").decode()
    assert week.index("Monday post") < week.index("Wednesday post")
    assert "Caption for Monday post." in week and "Unreviewed" not in week and "Next week" not in week
    assert z.read(f"{root}/{folders[0]}/video.mp4") == b"Monday post"
    assert any(n.endswith(f"{folders[1]}/title.txt") for n in names)
    rows = list(csv.DictReader(io.StringIO(z.read(f"{root}/schedule.csv").decode())))
    assert [r["title"] for r in rows] == ["Monday post", "Monday short", "Wednesday post"]
    only = zipfile.ZipFile(ew.export(factory, "money-made-simple", monday, manual_only=True))
    assert not any("youtube" in n for n in only.namelist())
    assert ew.export(factory, "money-made-simple", monday - timedelta(weeks=1)) is None
    # publications keep their status
    assert {p["status"] for p in factory.db.query("SELECT status FROM publications")} == {"queued"}


def test_cli(factory, capsys):
    from contentfactory.cli import main
    main(["export-week", "money-made-simple", "--weeks", "2"])
    assert "nothing scheduled" in capsys.readouterr().out
