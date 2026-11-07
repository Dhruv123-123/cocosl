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
