"""Render queue: rendering runs in its own process so publishing never waits on ffmpeg.

    factory renderq revoice                 # queue every post that was rendered without a voice
    factory renderq add 12 13 14            # queue specific posts
    factory renderq run --forever           # the renderer process (docker compose service `renderer`)
    factory renderq status

Jobs live in the `render_jobs` table. A failed render is retried with backoff
(5, 10 min) and then marked failed with the error. A job left `running` by a
crash is picked up again after RENDER_STALE_MINUTES (default 120).

Voice jobs (reason "voice") wait in the queue until a real voice is
configured (Kokoro, Piper, espeak, ElevenLabs or OpenAI), so you can queue
everything now and it voices itself the moment KOKORO_URL is set.

Re-rendering changes what people will see and hear, so a re-rendered post
goes back to review. Scheduled or published posts are never re-rendered.
"""
from __future__ import annotations

import logging
import os
import time
import traceback
from datetime import datetime, timedelta, timezone

from .db import now_iso
from .pipeline import Factory

log = logging.getLogger("factory.renderq")

SCHEMA = """
CREATE TABLE IF NOT EXISTS render_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  reason TEXT DEFAULT '',
  status TEXT DEFAULT 'queued',          -- queued | running | done | failed | cancelled
  priority INTEGER DEFAULT 0,
  attempts INTEGER DEFAULT 0,
  not_before TEXT DEFAULT '',
  error TEXT DEFAULT '',
  started_at TEXT DEFAULT '',
  finished_at TEXT DEFAULT '',
  created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S+00:00','now'))
);
CREATE INDEX IF NOT EXISTS render_jobs_status ON render_jobs(status, priority, id);
"""
MAX_ATTEMPTS = 3
LOCKED_STATUSES = ("scheduled", "published", "publishing")


def ensure_schema(db) -> None:
    db.conn.executescript(SCHEMA)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def voice_ready(factory: Factory, brand_slug: str) -> bool:
    """True when the configured TTS would produce a real voice, not room tone."""
    from .media import tts
    wanted = (factory.settings.tts_provider or "auto").lower()
    if wanted == "silent":
        return False
    brand = factory.brand(brand_slug)
    names = [n for n in tts.ORDER if n != "silent"] if wanted == "auto" else [wanted]
    return any(tts.PROVIDERS[n](factory.settings, brand).available() for n in names if n in tts.PROVIDERS)


def voice_of(post: dict) -> str | None:
    """The TTS provider a rendered video used, or None for carousels / unrendered posts."""
    for p in (post.get("assets") or {}).get("provenance") or []:
        if str(p.get("path", "")).endswith("audio.wav"):
            return p.get("provider") or p.get("tool")
    return None


def enqueue(factory: Factory, post_id: int, reason: str = "", priority: int = 0) -> int | None:
    """Queue a post; returns the job id, or None if it's already queued or locked."""
    db = factory.db
    ensure_schema(db)
    post = factory._post(post_id)
    if post["status"] in LOCKED_STATUSES:
        return None
    if db.one("SELECT id FROM render_jobs WHERE post_id = ? AND status IN ('queued','running')", [post_id]):
        return None
    job = db.insert("render_jobs", {"post_id": post_id, "reason": reason, "priority": priority})
    db.log("render.queued", "post", post_id, {"job": job, "reason": reason})
    return job


def enqueue_unvoiced(factory: Factory, brand: str | None = None, include_approved: bool = False) -> list[int]:
    """Queue every video post that was rendered with the silent placeholder voice."""
    allowed = ["rendered", "in_review", "blocked", "failed", "scripted"] + (["approved"] if include_approved else [])
    sql = f"SELECT * FROM posts WHERE format != 'carousel' AND status IN ({','.join('?' * len(allowed))})"
    params: list = list(allowed)
    if brand:
        sql += " AND brand = ?"
        params.append(brand)
    jobs = []
    for post in factory.db.query(sql + " ORDER BY id", params):
        if voice_of(post) in (None, "silent") and (job := enqueue(factory, post["id"], reason="voice")):
            jobs.append(job)
    return jobs


def recover_stale(factory: Factory, minutes: int | None = None) -> int:
    ensure_schema(factory.db)
    minutes = minutes or int(os.environ.get("RENDER_STALE_MINUTES", "120"))
    cutoff = (_now() - timedelta(minutes=minutes)).isoformat()
    cur = factory.db.execute("UPDATE render_jobs SET status='queued', error='recovered after crash' "
                             "WHERE status='running' AND started_at < ?", [cutoff])
    return getattr(cur, "rowcount", 0) or 0


def _claim(factory: Factory, now: datetime) -> dict | None:
    db = factory.db
    voice_cache: dict[str, bool] = {}
    for job in db.query("SELECT j.*, p.brand FROM render_jobs j JOIN posts p ON p.id = j.post_id "
                        "WHERE j.status='queued' AND (j.not_before = '' OR j.not_before <= ?) "
                        "ORDER BY j.priority DESC, j.id", [now.isoformat()]):
        if job["reason"] == "voice":
            if job["brand"] not in voice_cache:
                voice_cache[job["brand"]] = voice_ready(factory, job["brand"])
            if not voice_cache[job["brand"]]:
                continue  # wait for a voice to be configured
        cur = db.execute("UPDATE render_jobs SET status='running', started_at=?, attempts=attempts+1 "
                         "WHERE id=? AND status='queued'", [now.isoformat(), job["id"]])
        if getattr(cur, "rowcount", 1):
            job["attempts"] += 1
            return job
    return None


def run_one(factory: Factory, now: datetime | None = None) -> dict | None:
    """Render the next eligible job. Returns a summary, or None if nothing is ready."""
    ensure_schema(factory.db)
    now = now or _now()
    job = _claim(factory, now)
    if not job:
        return None
    db, post_id = factory.db, job["post_id"]
    post = db.get("posts", post_id)
    if not post or post["status"] in LOCKED_STATUSES:
        db.update("render_jobs", job["id"], {"status": "cancelled", "finished_at": now_iso(),
                                              "error": "post missing or already scheduled/published"})
        return {"job": job["id"], "post": post_id, "status": "cancelled"}
    started = time.monotonic()
    try:
        factory.render(post_id)
    except Exception as e:
        retry = job["attempts"] < MAX_ATTEMPTS
        db.update("render_jobs", job["id"], {
            "status": "queued" if retry else "failed", "error": f"{type(e).__name__}: {e}"[:1000],
            "not_before": (now + timedelta(minutes=5 * job["attempts"])).isoformat() if retry else "",
            "finished_at": "" if retry else now_iso()})
        log.warning("render job %s (post %s) failed: %s", job["id"], post_id, traceback.format_exc(limit=3))
        return {"job": job["id"], "post": post_id, "status": "retry" if retry else "failed", "error": str(e)}
    voice = voice_of(db.get("posts", post_id))
    db.update("render_jobs", job["id"], {"status": "done", "finished_at": now_iso(), "error": ""})
    return {"job": job["id"], "post": post_id, "status": "done", "voice": voice,
            "seconds": round(time.monotonic() - started, 1)}


def run(factory: Factory, limit: int | None = None, max_seconds: float | None = None) -> list[dict]:
    """Drain the queue (up to `limit` jobs or `max_seconds`)."""
    recover_stale(factory)
    done: list[dict] = []
    t0 = time.monotonic()
    while (limit is None or len(done) < limit) and (max_seconds is None or time.monotonic() - t0 < max_seconds):
        res = run_one(factory)
        if res is None:
            break
        done.append(res)
    return done


def status(factory: Factory) -> dict:
    ensure_schema(factory.db)
    rows = factory.db.query("SELECT status, COUNT(*) n FROM render_jobs GROUP BY status")
    out = {r["status"]: r["n"] for r in rows}
    waiting_voice = factory.db.scalar("SELECT COUNT(*) FROM render_jobs WHERE status='queued' AND reason='voice'")
    out["waiting_for_voice"] = int(waiting_voice or 0)
    out["recent_failures"] = factory.db.query(
        "SELECT id, post_id, error FROM render_jobs WHERE status='failed' ORDER BY id DESC LIMIT 5")
    return out


def run_forever(poll_seconds: int = 20) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    factory = Factory.create()
    log.info("renderer started; tts=%s", factory.settings.tts_provider)
    while True:
        try:
            for res in run(factory, limit=1):
                log.info("render: %s", res)
                break
            else:
                time.sleep(poll_seconds)
        except Exception:
            log.exception("renderer tick failed")
            time.sleep(poll_seconds)


def register(sub, factory_fn) -> None:
    q = sub.add_parser("renderq", help="render queue: re-voice posts, render in a separate process")
    qs = q.add_subparsers(dest="renderq_cmd", required=True)

    s = qs.add_parser("add", help="queue posts for (re)rendering")
    s.add_argument("ids", type=int, nargs="+")
    s.add_argument("--priority", type=int, default=0)

    def add(a):
        f = factory_fn(a)
        for pid in a.ids:
            job = enqueue(f, pid, reason="manual", priority=a.priority)
            print(f"post {pid}: " + (f"job {job}" if job else "skipped (already queued, scheduled or published)"))
    s.set_defaults(func=add)

    s = qs.add_parser("revoice", help="queue every video rendered without a voice; runs once a voice is set up")
    s.add_argument("--brand")
    s.add_argument("--include-approved", action="store_true",
                   help="also approved (not yet scheduled) posts; they go back to review after re-voicing")

    def revoice(a):
        f = factory_fn(a)
        jobs = enqueue_unvoiced(f, a.brand, a.include_approved)
        ready = {b: voice_ready(f, b) for b in f.brands()}
        print(f"queued {len(jobs)} post(s) for a voice")
        for b, ok in ready.items():
            print(f"  {b}: " + ("voice ready, the renderer will pick them up" if ok
                                else "no voice configured yet (set KOKORO_URL, see docs/CREDENTIALS.md)"))
    s.set_defaults(func=revoice)

    s = qs.add_parser("run", help="render queued jobs")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-minutes", type=float)
    s.add_argument("--forever", action="store_true", help="keep polling (the renderer service)")

    def run_cmd(a):
        if a.forever:
            return run_forever()
        f = factory_fn(a)
        res = run(f, a.limit, a.max_minutes * 60 if a.max_minutes else None)
        for r in res:
            print(r)
        print(f"{len(res)} job(s) processed; {status(f)['waiting_for_voice']} waiting for a voice")
    s.set_defaults(func=run_cmd)

    s = qs.add_parser("status", help="queue counts and recent failures")

    def stat(a):
        st = status(factory_fn(a))
        fails = st.pop("recent_failures")
        print(st)
        for r in fails:
            print(f"  failed job {r['id']} post {r['post_id']}: {r['error'][:160]}")
    s.set_defaults(func=stat)


if __name__ == "__main__":
    run_forever()
