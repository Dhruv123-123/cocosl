"""SQLite storage. Plain sqlite3, JSON columns for flexible payloads.

Every table has an integer id and created_at. Helper functions return dicts
with JSON columns already decoded so callers never touch raw rows.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS ideas (
  id INTEGER PRIMARY KEY,
  brand TEXT NOT NULL,
  title TEXT NOT NULL,
  angle TEXT DEFAULT '',
  format TEXT DEFAULT 'short',
  pillar TEXT DEFAULT '',
  score REAL DEFAULT 0,
  source TEXT DEFAULT 'llm',
  status TEXT DEFAULT 'new',          -- new | approved | rejected | used
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ideas_brand_status ON ideas(brand, status);

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY,
  brand TEXT NOT NULL,
  idea_id INTEGER REFERENCES ideas(id),
  format TEXT NOT NULL,               -- short | long | carousel | image
  status TEXT NOT NULL DEFAULT 'draft',
  title TEXT DEFAULT '',
  script TEXT DEFAULT '{}',           -- structured script JSON
  caption TEXT DEFAULT '',
  hashtags TEXT DEFAULT '[]',
  disclosure TEXT DEFAULT '',
  assets TEXT DEFAULT '{}',           -- {video, audio, images[], slides[], thumbnail, captions_srt}
  checks TEXT DEFAULT '{}',           -- guardrail results
  review_notes TEXT DEFAULT '',
  scheduled_at TEXT,
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS posts_brand_status ON posts(brand, status);

CREATE TABLE IF NOT EXISTS publications (
  id INTEGER PRIMARY KEY,
  post_id INTEGER NOT NULL REFERENCES posts(id),
  platform TEXT NOT NULL,
  account TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'queued',  -- queued | publishing | published | failed | dry_run
  scheduled_at TEXT,
  remote_id TEXT DEFAULT '',
  url TEXT DEFAULT '',
  error TEXT DEFAULT '',
  attempts INTEGER DEFAULT 0,
  published_at TEXT,
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS pubs_status ON publications(status, scheduled_at);

CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY,
  publication_id INTEGER NOT NULL REFERENCES publications(id),
  captured_at TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  saves INTEGER DEFAULT 0,
  reach INTEGER DEFAULT 0,
  watch_seconds REAL DEFAULT 0,
  avg_view_pct REAL DEFAULT 0,
  follows INTEGER DEFAULT 0,
  link_clicks INTEGER DEFAULT 0,
  raw TEXT DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS revenue (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  source TEXT NOT NULL,               -- affiliate | adsense | creator_fund | sponsorship | ugc | product | other
  brand TEXT DEFAULT '',
  post_id INTEGER,
  client_id INTEGER,
  amount_cents INTEGER NOT NULL,
  currency TEXT DEFAULT 'USD',
  note TEXT DEFAULT '',
  external_id TEXT DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS revenue_ext ON revenue(source, external_id) WHERE external_id != '';

CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  category TEXT NOT NULL,             -- llm | gpu | tts | stock | software | ads | other
  amount_cents INTEGER NOT NULL,
  currency TEXT DEFAULT 'USD',
  note TEXT DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS affiliate_links (
  id INTEGER PRIMARY KEY,
  brand TEXT DEFAULT '',
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL,
  commission TEXT DEFAULT '',
  clicks INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  contact_name TEXT DEFAULT '',
  email TEXT DEFAULT '',
  website TEXT DEFAULT '',
  niche TEXT DEFAULT '',
  status TEXT DEFAULT 'lead',         -- lead | contacted | replied | negotiating | won | lost | churned
  source TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY,
  client_id INTEGER NOT NULL REFERENCES clients(id),
  package TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  status TEXT DEFAULT 'brief',        -- brief | in_production | delivered | revision | paid | cancelled
  brief TEXT DEFAULT '{}',
  deliverables TEXT DEFAULT '[]',
  due_date TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY,
  client_id INTEGER NOT NULL REFERENCES clients(id),
  order_id INTEGER REFERENCES orders(id),
  number TEXT NOT NULL UNIQUE,
  items TEXT DEFAULT '[]',
  total_cents INTEGER NOT NULL,
  currency TEXT DEFAULT 'USD',
  status TEXT DEFAULT 'draft',        -- draft | sent | paid | void
  issued_at TEXT,
  due_at TEXT,
  paid_at TEXT,
  path TEXT DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  brand TEXT DEFAULT '',
  name TEXT NOT NULL,
  kind TEXT DEFAULT 'guide',          -- guide | template | checklist | prompt_pack | preset
  price_cents INTEGER DEFAULT 0,
  status TEXT DEFAULT 'draft',        -- draft | ready | listed
  url TEXT DEFAULT '',
  path TEXT DEFAULT '',
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  actor TEXT DEFAULT 'system',
  action TEXT NOT NULL,
  entity TEXT DEFAULT '',
  entity_id INTEGER,
  detail TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS llm_usage (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  provider TEXT,
  model TEXT,
  purpose TEXT,
  input_tokens INTEGER DEFAULT 0,
  output_tokens INTEGER DEFAULT 0,
  cost_usd REAL DEFAULT 0
);
"""

JSON_COLUMNS = {
    "meta", "script", "hashtags", "assets", "checks", "raw", "brief",
    "deliverables", "items", "detail",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class DB:
    """Thin wrapper around a sqlite3 connection. Thread-safe enough for the
    dashboard + a worker in the same process (one connection, a lock)."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL") if self.path != ":memory:" else None
        self.lock = threading.RLock()
        with self.lock:
            self.conn.executescript(SCHEMA)
            self.conn.commit()

    # -- low level -----------------------------------------------------------
    @staticmethod
    def _encode(values: dict[str, Any]) -> dict[str, Any]:
        out = {}
        for k, v in values.items():
            if k in JSON_COLUMNS and not isinstance(v, str):
                v = json.dumps(v, default=str)
            out[k] = v
        return out

    @staticmethod
    def _decode(row: sqlite3.Row | None) -> dict | None:
        if row is None:
            return None
        d = dict(row)
        for k in JSON_COLUMNS & d.keys():
            if isinstance(d[k], str):
                try:
                    d[k] = json.loads(d[k])
                except json.JSONDecodeError:
                    pass
        return d

    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        with self.lock:
            cur = self.conn.execute(sql, tuple(params))
            self.conn.commit()
            return cur

    def query(self, sql: str, params: Iterable[Any] = ()) -> list[dict]:
        with self.lock:
            rows = self.conn.execute(sql, tuple(params)).fetchall()
        return [self._decode(r) for r in rows]

    def one(self, sql: str, params: Iterable[Any] = ()) -> dict | None:
        with self.lock:
            row = self.conn.execute(sql, tuple(params)).fetchone()
        return self._decode(row)

    def scalar(self, sql: str, params: Iterable[Any] = ()) -> Any:
        with self.lock:
            row = self.conn.execute(sql, tuple(params)).fetchone()
        return row[0] if row else None

    # -- CRUD helpers --------------------------------------------------------
    def insert(self, table: str, values: dict[str, Any]) -> int:
        values = dict(values)
        cols = self._columns(table)
        ts = now_iso()
        if "created_at" in cols:
            values.setdefault("created_at", ts)
        if "updated_at" in cols:
            values.setdefault("updated_at", ts)
        values = self._encode({k: v for k, v in values.items() if k in cols})
        keys = ", ".join(values)
        marks = ", ".join("?" for _ in values)
        cur = self.execute(f"INSERT INTO {table} ({keys}) VALUES ({marks})", values.values())
        return int(cur.lastrowid)

    def update(self, table: str, row_id: int, values: dict[str, Any]) -> None:
        cols = self._columns(table)
        values = dict(values)
        if "updated_at" in cols:
            values["updated_at"] = now_iso()
        values = self._encode({k: v for k, v in values.items() if k in cols and k != "id"})
        if not values:
            return
        sets = ", ".join(f"{k} = ?" for k in values)
        self.execute(f"UPDATE {table} SET {sets} WHERE id = ?", [*values.values(), row_id])

    def get(self, table: str, row_id: int) -> dict | None:
        return self.one(f"SELECT * FROM {table} WHERE id = ?", [row_id])

    def delete(self, table: str, row_id: int) -> None:
        self.execute(f"DELETE FROM {table} WHERE id = ?", [row_id])

    def _columns(self, table: str) -> set[str]:
        cache = self.__dict__.setdefault("_colcache", {})
        if table not in cache:
            with self.lock:
                cache[table] = {r[1] for r in self.conn.execute(f"PRAGMA table_info({table})")}
        return cache[table]

    def log(self, action: str, entity: str = "", entity_id: int | None = None,
            detail: dict | None = None, actor: str = "system") -> None:
        self.insert("audit_log", {
            "ts": now_iso(), "actor": actor, "action": action,
            "entity": entity, "entity_id": entity_id, "detail": detail or {},
        })
