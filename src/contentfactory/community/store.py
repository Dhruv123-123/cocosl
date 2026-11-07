"""Comment storage on the shared factory DB.

The `comments` table is created on demand (CREATE TABLE IF NOT EXISTS), so
db.py does not change. Comments are de-duplicated by (platform, remote_id).

Statuses: new | drafted | replied | ignored | flagged.
Categories: question | praise | criticism | spam | abuse | purchase_intent |
content_idea | other ('' until triaged).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..db import DB

SCHEMA = """
CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY,
  publication_id INTEGER REFERENCES publications(id),
  brand TEXT DEFAULT '',
  platform TEXT NOT NULL,
  remote_id TEXT NOT NULL,
  parent_remote_id TEXT DEFAULT '',     -- top-level comment id when this is a reply
  author TEXT DEFAULT '',
  text TEXT DEFAULT '',
  created_at_remote TEXT DEFAULT '',
  like_count INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'new',   -- new | drafted | replied | ignored | flagged
  category TEXT DEFAULT '',             -- set by triage
  meta TEXT DEFAULT '{}',               -- triage: {category, reason, source, idea_title}
  draft TEXT DEFAULT '',
  draft_notes TEXT DEFAULT '',
  reply_text TEXT DEFAULT '',
  reply_remote_id TEXT DEFAULT '',
  dry_run INTEGER DEFAULT 0,            -- 1 = 'replied (dry run)': nothing was sent
  replied_at TEXT,
  idea_id INTEGER,
  raw TEXT DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS comments_remote ON comments(platform, remote_id);
CREATE INDEX IF NOT EXISTS comments_status ON comments(brand, status);
CREATE INDEX IF NOT EXISTS comments_replied ON comments(platform, replied_at);
"""

STATUSES = ("new", "drafted", "replied", "ignored", "flagged")
CATEGORIES = ("question", "praise", "criticism", "spam", "abuse", "purchase_intent", "content_idea", "other")
FLAG_CATEGORIES = ("spam", "abuse")
CATEGORY_LABELS = {
    "question": "question", "praise": "praise", "criticism": "criticism", "spam": "spam / scam",
    "abuse": "abuse", "purchase_intent": "purchase intent", "content_idea": "content idea", "other": "other",
}

def ensure_schema(db: DB) -> None:
    if db.__dict__.get("_comments_ready"):
        return
    with db.lock:
        db.conn.executescript(SCHEMA)
        db.conn.commit()
    db.__dict__.get("_colcache", {}).pop("comments", None)
    db.__dict__["_comments_ready"] = True


def upsert(db: DB, row: dict) -> tuple[int, bool]:
    """Insert a comment unless (platform, remote_id) exists. Returns (id, created).
    Existing rows only get like_count / text refreshed; their status is kept."""
    ensure_schema(db)
    existing = db.one("SELECT id FROM comments WHERE platform = ? AND remote_id = ?",
                      [row["platform"], row["remote_id"]])
    if existing:
        db.update("comments", existing["id"], {"like_count": row.get("like_count", 0)})
        return existing["id"], False
    return db.insert("comments", row), True


def get(db: DB, comment_id: int) -> dict:
    ensure_schema(db)
    c = db.get("comments", comment_id)
    if not c:
        raise KeyError(f"No comment #{comment_id}")
    return c


def own_reply_ids(db: DB, platform: str) -> set[str]:
    ensure_schema(db)
    return {r["reply_remote_id"] for r in db.query(
        "SELECT reply_remote_id FROM comments WHERE platform = ? AND reply_remote_id != ''", [platform])}


def replies_last_hour(db: DB, platform: str, now: datetime | None = None) -> int:
    """Real (non dry-run) replies sent on a platform in the last 60 minutes."""
    ensure_schema(db)
    since = ((now or datetime.now(timezone.utc)) - timedelta(hours=1)).replace(microsecond=0).isoformat()
    return int(db.scalar("SELECT COUNT(*) FROM comments WHERE platform = ? AND status = 'replied' "
                         "AND dry_run = 0 AND replied_at >= ?", [platform, since]) or 0)


def inbox(db: DB, *, brand: str = "", status: str = "", category: str = "", limit: int = 100) -> list[dict]:
    """Comments joined with their post title and publication URL, newest first.
    status '' means the working set: new + drafted + flagged."""
    ensure_schema(db)
    where, params = [], []
    if brand:
        where.append("c.brand = ?")
        params.append(brand)
    if status == "all":
        pass
    elif status:
        where.append("c.status = ?")
        params.append(status)
    else:
        where.append("c.status IN ('new', 'drafted', 'flagged')")
    if category:
        where.append("c.category = ?")
        params.append(category)
    sql = ("SELECT c.*, p.title AS post_title, p.id AS post_id, pub.url AS post_url "
           "FROM comments c LEFT JOIN publications pub ON pub.id = c.publication_id "
           "LEFT JOIN posts p ON p.id = pub.post_id"
           + (" WHERE " + " AND ".join(where) if where else "")
           + " ORDER BY CASE c.status WHEN 'drafted' THEN 0 WHEN 'new' THEN 1 WHEN 'flagged' THEN 2 ELSE 3 END,"
             " c.created_at_remote DESC, c.id DESC LIMIT ?")
    return db.query(sql, [*params, limit])


def counts(db: DB, brand: str = "") -> dict[str, int]:
    ensure_schema(db)
    sql = "SELECT status, COUNT(*) AS n FROM comments" + (" WHERE brand = ?" if brand else "") + " GROUP BY status"
    out = {s: 0 for s in STATUSES}
    for r in db.query(sql, [brand] if brand else []):
        out[r["status"]] = r["n"]
    return out


def set_status(db: DB, comment_id: int, status: str, actor: str = "human") -> None:
    if status not in STATUSES:
        raise ValueError(f"Unknown status '{status}'")
    c = get(db, comment_id)
    if c["status"] == "replied":
        raise ValueError(f"Comment #{comment_id} was already replied to")
    db.update("comments", comment_id, {"status": status})
    db.log(f"comment.{status}", "comment", comment_id, {"from": c["status"]}, actor=actor)
