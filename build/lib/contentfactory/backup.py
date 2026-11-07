"""Consistent database backups that are safe while the app, worker and renderer are running.

    factory backup                      # data/backups/factory-YYYYmmdd-HHMMSS.db, keeps the newest 14
    factory backup --out /mnt/bucket --keep 30 --with-config

Uses SQLite's online backup API, so the copy is consistent even mid-write. Media
(output/) is large and can be re-rendered; back it up separately with rsync or a
bucket sync if you want it. With BACKUP_DIR set, the worker makes one backup a day.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .pipeline import Factory


def backup_db(factory: Factory, out_dir: str | Path | None = None, keep: int = 14,
              with_config: bool = False) -> Path:
    out = Path(out_dir or os.environ.get("BACKUP_DIR") or Path(factory.settings.db_path).parent / "backups")
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    dest = out / f"factory-{stamp}.db"
    src = sqlite3.connect(factory.settings.db_path, timeout=30)
    try:
        dst = sqlite3.connect(dest)
        with dst:
            src.backup(dst)
        ok = dst.execute("PRAGMA integrity_check").fetchone()[0]
        dst.close()
    finally:
        src.close()
    if ok != "ok":
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"backup failed its integrity check: {ok}")
    if with_config:
        cfg = out / f"config-{stamp}"
        shutil.copytree(factory.settings.brands_dir, cfg / "brands", dirs_exist_ok=True)
        env = Path(factory.settings.home) / ".env"
        if env.exists():  # contains secrets: keep the backup folder private
            shutil.copy2(env, cfg / ".env")
            os.chmod(cfg / ".env", 0o600)
    olds = sorted(out.glob("factory-*.db"))
    for old in olds[:-keep] if keep > 0 else []:
        old.unlink(missing_ok=True)
    factory.db.log("backup.db", "", None, {"path": str(dest)})
    return dest


def register(sub, factory_fn) -> None:
    s = sub.add_parser("backup", help="consistent copy of the database (safe while everything runs)")
    s.add_argument("--out", help="folder (default BACKUP_DIR or data/backups)")
    s.add_argument("--keep", type=int, default=14, help="how many backups to keep")
    s.add_argument("--with-config", action="store_true", help="also copy brands/ and .env (secrets!)")
    s.set_defaults(func=lambda a: print(backup_db(factory_fn(a), a.out, a.keep, a.with_config)))
