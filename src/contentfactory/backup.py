"""Consistent database backups that are safe while the app, worker and renderer are running.

    factory backup                      # data/backups/factory-YYYYmmdd-HHMMSS.db, keeps the newest 14
    factory backup --out /mnt/bucket --keep 30 --with-config
    factory backup --archive            # data/backups/factory-archive-YYYY-mm-dd-HHMMSS.zip: everything to rebuild
    factory backup --archive --with-media --with-secrets
    factory restore <archive.zip>       # lists what it would restore; --yes restores (keeps a copy of what it replaces)

The archive holds the database (posts, schedule, stats imports, revenue, subscribers), brands/
(configs and sequences), launch/ (content packs), data/*.yaml|json (scorecard notes and other hand-filled
files), voice/ and footage/ (your recordings) and a MANIFEST.json. --with-media adds output/ (rendered
videos; large, and they can be re-rendered). --with-secrets adds .env, so keep that archive private.

Uses SQLite's online backup API, so the copy is consistent even mid-write. Media
(output/) is large and can be re-rendered; back it up separately with rsync or a
bucket sync if you want it. With BACKUP_DIR set, the worker makes one backup a day.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .pipeline import Factory


def backup_db(factory: Factory, out_dir: str | Path | None = None, keep: int = 14,
              with_config: bool = False) -> Path:
    out = Path(out_dir or os.environ.get("BACKUP_DIR") or Path(factory.settings.db_path).parent / "backups")
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
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


ARCHIVE_DIRS = ("brands", "launch", "voice", "footage")
SKIP_PARTS = {"__pycache__", ".git", "backups", ".venv", "node_modules"}


def _files(root: Path, rel: str):
    base = root / rel
    if base.is_file():
        yield base
    elif base.is_dir():
        for p in sorted(base.rglob("*")):
            if p.is_file() and not SKIP_PARTS & set(p.relative_to(root).parts):
                yield p


def backup_archive(factory: Factory, out_dir: str | Path | None = None, with_media: bool = False,
                   with_secrets: bool = False, keep: int = 8) -> Path:
    import json
    import tempfile
    import zipfile
    home = Path(factory.settings.home)
    out = Path(out_dir or os.environ.get("BACKUP_DIR") or Path(factory.settings.db_path).parent / "backups")
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S")
    dest = out / f"factory-archive-{stamp}.zip"
    manifest = {"created": stamp, "home": str(home), "files": 0, "with_media": with_media, "with_secrets": with_secrets,
                "db": "", "posts": factory.db.scalar("SELECT COUNT(*) FROM posts")}
    with tempfile.TemporaryDirectory() as tmp:
        snap = backup_db(factory, tmp, keep=0)  # consistent copy, integrity-checked
        db_rel = Path(factory.settings.db_path)
        db_rel = db_rel.relative_to(home) if db_rel.is_relative_to(home) else Path("data") / db_rel.name
        manifest["db"] = str(db_rel)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(snap, str(db_rel))
            n = 1
            rels = list(ARCHIVE_DIRS) + (["output"] if with_media else [])
            for rel in rels:
                for p in _files(home, rel):
                    z.write(p, str(p.relative_to(home)))
                    n += 1
            data = home / "data"
            for p in sorted(data.glob("*")) if data.is_dir() else []:
                if p.is_file() and p.suffix in (".yaml", ".yml", ".json", ".csv", ".md"):
                    z.write(p, str(p.relative_to(home)))
                    n += 1
            if with_secrets and (home / ".env").is_file():
                z.write(home / ".env", ".env")
                n += 1
            manifest["files"] = n
            z.writestr("MANIFEST.json", json.dumps(manifest, indent=2))
    if with_secrets:
        os.chmod(dest, 0o600)
    olds = sorted(out.glob("factory-archive-*.zip"))
    for old in olds[:-keep] if keep > 0 else []:
        old.unlink(missing_ok=True)
    factory.db.log("backup.archive", "", None, {"path": str(dest), "files": manifest["files"]})
    return dest


def restore_archive(home: Path, archive: Path, yes: bool = False) -> dict:
    """Restore an archive into `home`. Without yes, only reports. Replaced files go to
    data/pre-restore-<stamp>/ first, so a restore can itself be undone."""
    import json
    import zipfile
    home = Path(home)
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        if "MANIFEST.json" not in names:
            raise ValueError(f"{archive} isn't a factory archive (no MANIFEST.json)")
        manifest = json.loads(z.read("MANIFEST.json"))
        for n in names:
            if n.startswith("/") or ".." in Path(n).parts:
                raise ValueError(f"unsafe path in archive: {n}")
        files = [n for n in names if n != "MANIFEST.json"]
        replace = [n for n in files if (home / n).exists()]
        report = {"manifest": manifest, "files": len(files), "replace": len(replace), "restored": False, "saved_to": ""}
        if not yes:
            return report
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        keep = home / "data" / f"pre-restore-{stamp}"
        for n in replace:
            dst = keep / n
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(home / n, dst)
        db = manifest.get("db") or ""
        for suffix in ("-wal", "-shm"):  # a stale WAL would replay over the restored database
            if db and (home / (db + suffix)).exists():
                (home / (db + suffix)).unlink()
        for n in files:
            dst = home / n
            dst.parent.mkdir(parents=True, exist_ok=True)
            with z.open(n) as src, open(dst, "wb") as out:
                shutil.copyfileobj(src, out)
            if n == ".env":
                os.chmod(dst, 0o600)
        report.update(restored=True, saved_to=str(keep) if replace else "")
        return report


def register(sub, factory_fn) -> None:
    s = sub.add_parser("backup", help="consistent copy of the database (safe while everything runs)")
    s.add_argument("--out", help="folder (default BACKUP_DIR or data/backups)")
    s.add_argument("--keep", type=int, default=14, help="how many backups to keep")
    s.add_argument("--with-config", action="store_true", help="also copy brands/ and .env (secrets!)")
    s.add_argument("--archive", action="store_true", help="one dated zip: database, brands, packs, recordings, notes")
    s.add_argument("--with-media", action="store_true", help="archive: also output/ (rendered media; large)")
    s.add_argument("--with-secrets", action="store_true", help="archive: also .env (keep it private)")

    def cmd(a):
        f = factory_fn(a)
        if a.archive:
            print(backup_archive(f, a.out, a.with_media, a.with_secrets, a.keep if a.keep != 14 else 8))
        else:
            print(backup_db(f, a.out, a.keep, a.with_config))
    s.set_defaults(func=cmd)

    r = sub.add_parser("restore", help="restore a `factory backup --archive` zip (lists first; --yes restores)")
    r.add_argument("archive", type=Path)
    r.add_argument("--yes", action="store_true", help="restore now (replaced files are kept in data/pre-restore-*/)")

    def rcmd(a):
        from .config import Settings
        home = Path(Settings.load(a.home).home)
        rep = restore_archive(home, a.archive, a.yes)
        m = rep["manifest"]
        print(f"Archive from {m['created']}: {rep['files']} file(s), {m.get('posts', '?')} post(s) in its database; "
              f"{rep['replace']} would replace a file in {home}.")
        if not rep["restored"]:
            print("Nothing changed. Stop the worker and app, then run again with --yes.")
        else:
            print("Restored." + (f" What it replaced is in {rep['saved_to']}." if rep["saved_to"] else ""))
    r.set_defaults(func=rcmd)
