import json
import sqlite3
from datetime import datetime, timezone

from contentfactory.backup import backup_db
from contentfactory.cli import main


def test_backup_is_consistent_and_rotates(factory, tmp_path):
    factory.db.log("x", "", None, {})
    paths = [backup_db(factory, tmp_path / "b", keep=2) for _ in range(3)]
    left = sorted((tmp_path / "b").glob("factory-*.db"))
    assert len(left) <= 2 and paths[-1] in left
    con = sqlite3.connect(paths[-1])
    assert con.execute("SELECT COUNT(*) FROM audit_log WHERE action='x'").fetchone()[0] == 1


def test_worker_backs_up_daily_when_configured(factory, tmp_path, monkeypatch):
    from contentfactory.worker import Worker
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "nightly"))
    w = Worker(factory, publish_every=__import__("datetime").timedelta(0))
    factory.daily = lambda *a, **k: {}
    w.run_sequences = lambda now: None
    w.collect_comments = lambda: None
    now = datetime.now(timezone.utc)
    assert "backup" in w.tick(now)
    assert "backup" not in w.tick(now)
    assert list((tmp_path / "nightly").glob("factory-*.db"))


def test_import_is_rerunnable(home, monkeypatch, fake_render, tmp_path):
    monkeypatch.chdir(home)
    script = {"title": "Rerun me", "hook": "h", "segments": [{"heading": "a", "narration": "One two three.",
              "on_screen_text": "x", "visual_prompt": "y"}], "cta": "c", "caption": "cap", "hashtags": ["a"],
              "description": "d", "thumbnail_text": "t", "sources": [], "claims_to_verify": []}
    f = tmp_path / "c.json"
    f.write_text(json.dumps([{"script": script, "format": "short"}]))
    main(["import", str(f), "--brand", "money-made-simple", "--no-render"])
    main(["import", str(f), "--brand", "money-made-simple"])   # resumes the unrendered one, no duplicate
    from contentfactory.config import Settings
    from contentfactory.pipeline import Factory
    fac = Factory.create(Settings.load(home))
    rows = fac.db.query("SELECT id, status, assets FROM posts WHERE title = 'Rerun me'")
    assert len(rows) == 1


def test_archive_and_restore(factory, tmp_path):
    import json
    import zipfile
    from pathlib import Path

    from contentfactory.backup import backup_archive, restore_archive
    home = factory.settings.home
    (home / "voice" / "money-made-simple").mkdir(parents=True, exist_ok=True)
    (home / "voice" / "money-made-simple" / "post-1.wav").write_bytes(b"take")
    (home / "data").mkdir(exist_ok=True)
    (home / "data" / "scorecard-manual.yaml").write_text("x: 1\n")
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "approved", "title": "Keep me",
                                      "caption": "", "script": {}, "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})
    z = backup_archive(factory, tmp_path / "b")
    names = zipfile.ZipFile(z).namelist()
    assert "MANIFEST.json" in names and "voice/money-made-simple/post-1.wav" in names
    assert "data/scorecard-manual.yaml" in names and ".env" not in names
    assert any(n.startswith("brands/") for n in names)
    m = json.loads(zipfile.ZipFile(z).read("MANIFEST.json"))
    assert m["posts"] >= 1

    # restore into a fresh home
    new = tmp_path / "new"
    rep = restore_archive(new, z)
    assert not rep["restored"] and not (new / "voice").exists()
    rep = restore_archive(new, z, yes=True)
    assert rep["restored"] and (new / "voice/money-made-simple/post-1.wav").read_bytes() == b"take"
    import sqlite3
    con = sqlite3.connect(new / m["db"])
    assert con.execute("SELECT title FROM posts WHERE id = ?", [pid]).fetchone()[0] == "Keep me"
    con.close()
    (new / "data" / "scorecard-manual.yaml").write_text("changed")
    rep = restore_archive(new, z, yes=True)
    assert rep["saved_to"] and (new / "data" / "scorecard-manual.yaml").read_text() == "x: 1\n"
    assert any(p.read_text() == "changed" for p in Path(rep["saved_to"]).rglob("scorecard-manual.yaml"))


def test_restore_refuses_unsafe(tmp_path):
    import zipfile
    import pytest
    from contentfactory.backup import restore_archive
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("MANIFEST.json", "{}")
        z.writestr("../evil.txt", "x")
    with pytest.raises(ValueError):
        restore_archive(tmp_path / "h", bad, yes=True)
