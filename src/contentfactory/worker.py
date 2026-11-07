"""Long-running worker for Docker: a tiny scheduler with no extra dependencies.

Every brand runs on its own clock (brand.cadence.timezone):

* every PUBLISH_EVERY minutes (default 10): publish due posts for all brands
* once a day per brand at cadence.daily_at (or DAILY_AT, default 07:00 local):
  `daily` (ideas + cadence.daily_drafts drafts into the review queue);
  skipped for brands with cadence.paused: true
* every METRICS_EVERY hours (default 6): collect metrics
* every SEQUENCES_EVERY minutes (default 60): welcome-sequence emails
  (funnel.sequences.run_sequences; real sends only with FACTORY_DRY_RUN=0,
  SMTP_* and BUSINESS_ADDRESS, otherwise .eml dry runs)
* every COMMENTS_EVERY minutes (default 60, 0 = off): collect comments and
  draft replies into the inbox. Replies are only ever sent by a human click.
* Mondays after DAILY_AT (first brand's zone): save the weekly report to output/reports/
* with BACKUP_DIR set: one database backup a day (keeps BACKUP_KEEP, default 14)
* with CLEANUP_AFTER_DAYS set (14+): delete videos/audio of posts live everywhere for that long (cleanup.py)

Daily runs and the weekly report are recorded in the audit log, so a restart
never runs them twice on the same day. Each step has its own error handling:
one failing step (or brand) can't stop the others. A heartbeat file
(worker.json next to the database) feeds /api/status.

`daily` only fills the review queue. Approving stays with you. Rendering runs
in the renderer service when RENDER_QUEUE=1 (see renderq.py).
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .pipeline import Factory

log = logging.getLogger("factory.worker")
EPOCH = datetime.min.replace(tzinfo=timezone.utc)


def _minutes(name: str, default: int) -> timedelta:
    return timedelta(minutes=int(os.environ.get(name, str(default)) or 0))


def _hhmm(value: str) -> tuple[int, int]:
    hh, mm = (value or "07:00").split(":")
    return int(hh), int(mm)


def _zone(name: str):
    try:
        return ZoneInfo(name)
    except Exception:
        return timezone.utc


@dataclass
class Worker:
    factory: Factory
    publish_every: timedelta = field(default_factory=lambda: _minutes("PUBLISH_EVERY", 10))
    metrics_every: timedelta = field(default_factory=lambda: timedelta(hours=int(os.environ.get("METRICS_EVERY", "6"))))
    sequences_every: timedelta = field(default_factory=lambda: _minutes("SEQUENCES_EVERY", 60))
    comments_every: timedelta = field(default_factory=lambda: _minutes("COMMENTS_EVERY", 60))
    daily_at: str = field(default_factory=lambda: os.environ.get("DAILY_AT", "07:00"))
    last: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ helpers
    def _due(self, key: str, every: timedelta, now: datetime) -> bool:
        if not every:
            return False
        if now - self.last.get(key, EPOCH) >= every:
            self.last[key] = now
            return True
        return False

    def _step(self, key: str, fn, *args):
        try:
            res = fn(*args)
            self.errors.pop(key, None)
            return res
        except Exception as e:  # keep the worker alive; errors land in the log and the heartbeat
            log.exception("worker step %s failed", key)
            self.errors[key] = f"{type(e).__name__}: {e}"[:300]
            return None

    def _ran_since(self, action: str, entity: str, since_utc: datetime) -> bool:
        return bool(self.factory.db.scalar(
            "SELECT 1 FROM audit_log WHERE action = ? AND entity = ? AND ts >= ? LIMIT 1",
            [action, entity, since_utc.replace(microsecond=0).isoformat()]))

    @staticmethod
    def _local_midnight_utc(local: datetime) -> datetime:
        return local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)

    # ------------------------------------------------------------------ steps
    def daily_due(self, now: datetime) -> list[str]:
        """Brands whose local daily time has passed today and that haven't run yet."""
        due = []
        for slug, brand in self.factory.brands().items():
            c = brand.cadence
            if c.paused:
                continue
            local = now.astimezone(_zone(c.timezone))
            if (local.hour, local.minute) < _hhmm(c.daily_at or self.daily_at):
                continue
            if not self._ran_since("worker.daily", f"brand:{slug}", self._local_midnight_utc(local)):
                due.append(slug)
        return due

    def run_daily(self, slug: str, now: datetime) -> dict | None:
        c = self.factory.brand(slug).cadence
        # Record first so a crash mid-run doesn't retry it in a loop all day.
        self._mark("worker.daily", f"brand:{slug}", now)
        res = self._step(f"daily:{slug}", self.factory.daily, slug, c.daily_ideas, c.daily_drafts)
        log.info("daily %s: %s", slug, res)
        return res

    def weekly_report_due(self, now: datetime) -> bool:
        brands = list(self.factory.brands().values())
        local = now.astimezone(_zone(brands[0].cadence.timezone) if brands else timezone.utc)
        if local.weekday() != 0 or (local.hour, local.minute) < _hhmm(self.daily_at):
            return False
        return not self._ran_since("worker.report", "", self._local_midnight_utc(local))

    def _mark(self, action: str, entity: str, now: datetime) -> None:
        self.factory.db.insert("audit_log", {"ts": now.replace(microsecond=0).isoformat(), "actor": "worker",
                                             "action": action, "entity": entity, "detail": {}})

    def collect_comments(self) -> None:
        from .community import collect_comments, draft_replies
        res = collect_comments(self.factory)
        if res.get("new"):
            log.info("comments: %s; drafted %s", {k: v for k, v in res.items() if k != "errors"},
                     len(draft_replies(self.factory)))

    def run_sequences(self, now: datetime) -> None:
        from .funnel.sequences import run_sequences
        res = run_sequences(self.factory, now, confirm=True)
        if res["sent"] or res["dry_run"] or res["failed"]:
            log.info("sequences: mode=%s sent=%s dry_run=%s failed=%s skipped=%s blocked=%s", res["mode"],
                     res["sent"], res["dry_run"], res["failed"], res["skipped"], res["blocked"])

    def tick(self, now: datetime | None = None) -> dict:
        """One pass. Returns what ran (handy for tests and the heartbeat)."""
        now = now or datetime.now(timezone.utc)
        ran: dict = {}
        if self._due("publish", self.publish_every, now):
            res = self._step("publish", self.factory.publish_due, now)
            ran["publish"] = len(res or [])
            if res:
                log.info("published: %s", res)
        for slug in self._step("daily_due", self.daily_due, now) or []:
            ran.setdefault("daily", []).append(slug)
            self.run_daily(slug, now)
        if self._due("metrics", self.metrics_every, now):
            ran["metrics"] = self._step("metrics", self.factory.collect_metrics)
        if self._due("sequences", self.sequences_every, now):
            self._step("sequences", self.run_sequences, now)
            ran["sequences"] = True
        if self._due("comments", self.comments_every, now):
            self._step("comments", self.collect_comments)
            ran["comments"] = True
        if os.environ.get("BACKUP_DIR") and not self._ran_since("worker.backup", "", now - timedelta(hours=23)):
            from .backup import backup_db
            self._mark("worker.backup", "", now)
            ran["backup"] = str(self._step("backup", backup_db, self.factory, None,
                                           int(os.environ.get("BACKUP_KEEP", "14"))))
        from .cleanup import from_env as cleanup_days
        if (days := cleanup_days()) and not self._ran_since("worker.cleanup", "", now - timedelta(hours=23)):
            from .cleanup import run as cleanup
            self._mark("worker.cleanup", "", now)
            ran["cleanup"] = self._step("cleanup", cleanup, self.factory, days, True)
        if self._step("report_due", self.weekly_report_due, now):
            from .reports import save_report
            self._mark("worker.report", "", now)
            ran["report"] = self._step("report", save_report, self.factory)
            log.info("weekly report: %s", ran["report"])
        self.heartbeat(now, ran)
        return ran

    def heartbeat(self, now: datetime, ran: dict) -> None:
        try:
            path = heartbeat_path(self.factory)
            prev = json.loads(path.read_text()) if path.exists() else {}
            data = {"at": now.isoformat(), "pid": os.getpid(), "dry_run": self.factory.settings.dry_run,
                    "errors": self.errors,
                    "last_ran": {**prev.get("last_ran", {}), **{k: now.isoformat() for k in ran}}}
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=1, default=str))
            tmp.replace(path)
        except Exception:
            log.debug("heartbeat write failed", exc_info=True)


def heartbeat_path(factory: Factory) -> Path:
    return Path(factory.settings.db_path).parent / "worker.json"


def read_heartbeat(factory: Factory) -> dict | None:
    try:
        return json.loads(heartbeat_path(factory).read_text())
    except Exception:
        return None


def run_forever() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    factory = Factory.create()
    worker = Worker(factory)
    log.info("worker started; dry_run=%s brands=%s", factory.settings.dry_run, list(factory.brands()))
    while True:
        worker.tick()
        time.sleep(30)


if __name__ == "__main__":
    run_forever()
