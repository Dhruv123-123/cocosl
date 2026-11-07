"""One place that answers "is the factory running properly?" for `factory status` and /api/status."""
from __future__ import annotations

from datetime import datetime, timezone

from .pipeline import Factory


def system_status(factory: Factory, now: datetime | None = None) -> dict:
    from .renderq import status as rq_status, voice_ready
    from .worker import read_heartbeat
    now = now or datetime.now(timezone.utc)
    db = factory.db
    hb = read_heartbeat(factory)
    age = None
    if hb and hb.get("at"):
        try:
            age = round((now - datetime.fromisoformat(hb["at"])).total_seconds() / 60, 1)
        except ValueError:
            pass
    pubs = {r["status"]: r["n"] for r in db.query("SELECT status, COUNT(*) n FROM publications GROUP BY status")}
    needs_check = db.query("SELECT id, post_id, platform, error FROM publications WHERE status = 'needs_check' "
                           "ORDER BY id DESC LIMIT 20")
    failed_recent = db.query("SELECT id, post_id, platform, error FROM publications WHERE status = 'failed' "
                             "ORDER BY id DESC LIMIT 5")
    next_up = db.query("SELECT p.id, p.post_id, p.platform, p.scheduled_at, s.brand FROM publications p "
                       "JOIN posts s ON s.id = p.post_id WHERE p.status = 'queued' ORDER BY p.scheduled_at LIMIT 5")
    alerts = []
    if hb is None:
        alerts.append("Worker has never run (start it: docker compose up -d worker).")
    elif age is not None and age > 15:
        alerts.append(f"Worker last ticked {age:.0f} min ago: it may be down.")
    for step, err in (hb or {}).get("errors", {}).items():
        alerts.append(f"Worker step '{step}' failing: {err}")
    if needs_check:
        alerts.append(f"{len(needs_check)} publication(s) were interrupted mid-upload: check the platform.")
    rq = rq_status(factory)
    if rq.get("waiting_for_voice") and not any(voice_ready(factory, b) for b in factory.brands()):
        alerts.append(f"{rq['waiting_for_voice']} video(s) waiting for a voice: set KOKORO_URL (docs/CREDENTIALS.md).")
    return {"dry_run": factory.settings.dry_run, "worker": {"heartbeat": hb, "minutes_since": age},
            "publications": pubs, "next_up": next_up, "needs_check": needs_check, "failed_recent": failed_recent,
            "render_queue": rq, "alerts": alerts}
