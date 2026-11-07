"""One place that answers "is the factory running properly?" for `factory status` and /api/status."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
    if pubs.get("manual"):
        alerts.append(f"{pubs['manual']} post(s) to post by hand are due (TikTok): see Today.")
    if needs_check:
        alerts.append(f"{len(needs_check)} publication(s) were interrupted mid-upload: check the platform.")
    if not factory.settings.dry_run:
        from .publish import credential_status
        cache: dict = {}
        for row in db.query("SELECT s.brand, p.platform, COUNT(*) n FROM publications p JOIN posts s ON s.id = p.post_id "
                            "WHERE p.status = 'queued' GROUP BY s.brand, p.platform"):
            if row["brand"] not in cache:
                cache[row["brand"]] = credential_status(factory.settings.for_brand(row["brand"]))
            missing = cache[row["brand"]].get(row["platform"])
            if missing:
                alerts.append(f"{row['n']} {row['brand']} post(s) queued for {row['platform']} but it isn't connected "
                              f"(missing {', '.join(missing)}).")
    since = (now.replace(microsecond=0) - timedelta(hours=24)).isoformat()
    token_fail = db.one("SELECT detail FROM audit_log WHERE action = 'tokens.refresh_failed' AND ts >= ? "
                        "ORDER BY id DESC LIMIT 1", [since])
    if token_fail:
        alerts.append(f"Token refresh failed in the last 24 h: {str((token_fail['detail'] or {}).get('error', ''))[:160]}. "
                      "Re-run `factory auth <platform>`.")
    out_dir = factory.settings.output_dir
    soon = (now + timedelta(hours=48)).isoformat()
    for row in db.query("SELECT p.id, p.post_id, s.assets, s.format FROM publications p JOIN posts s ON s.id = p.post_id "
                        "WHERE p.status = 'queued' AND p.scheduled_at <= ?", [soon]):
        a = row["assets"] or {}
        files = a.get("slides") if row["format"] == "carousel" else [a.get("video")]
        if not files or any(not f or not (out_dir / f).exists() for f in files):
            alerts.append(f"Post #{row['post_id']} goes out within 48 h but its media files are missing: re-render it.")
    rq = rq_status(factory)
    if rq.get("waiting_for_voice") and not any(voice_ready(factory, b) for b in factory.brands()):
        alerts.append(f"{rq['waiting_for_voice']} video(s) waiting for a voice: set KOKORO_URL (docs/CREDENTIALS.md).")
    return {"dry_run": factory.settings.dry_run, "worker": {"heartbeat": hb, "minutes_since": age},
            "publications": pubs, "next_up": next_up, "needs_check": needs_check, "failed_recent": failed_recent,
            "render_queue": rq, "alerts": alerts}


def main() -> int:
    """Container healthcheck: `python -m contentfactory.health worker` exits 1 if the worker heartbeat is stale."""
    import sys
    f = Factory.create()
    if sys.argv[1:] == ["worker"]:
        st = system_status(f)
        mins = st["worker"]["minutes_since"]
        return 0 if mins is not None and mins < 15 else 1
    f.db.scalar("SELECT 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
