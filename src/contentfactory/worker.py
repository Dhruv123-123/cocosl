"""Long-running worker for Docker: a tiny scheduler with no extra dependencies.

* every PUBLISH_EVERY minutes: publish due posts
* once a day at DAILY_AT (local time of the first brand): `daily` for each brand
* every METRICS_EVERY hours: collect metrics
* every SEQUENCES_EVERY minutes (default 60): welcome-sequence emails
  (funnel.sequences.run_sequences; real sends only with FACTORY_DRY_RUN=0,
  SMTP_* and BUSINESS_ADDRESS, otherwise .eml dry runs)
* every COMMENTS_EVERY minutes (default 60, 0 = off): collect comments and
  draft replies into the inbox. Replies are only ever sent by a human click.
* Mondays after DAILY_AT: save the weekly report to output/reports/

`daily` only fills the review queue. Approving stays with you.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .pipeline import Factory

log = logging.getLogger("factory.worker")


def run_forever() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    factory = Factory.create()
    publish_every = timedelta(minutes=int(os.environ.get("PUBLISH_EVERY", "10")))
    metrics_every = timedelta(hours=int(os.environ.get("METRICS_EVERY", "6")))
    daily_at = os.environ.get("DAILY_AT", "07:00")
    brands = factory.brands()
    tz = ZoneInfo(next(iter(brands.values())).cadence.timezone) if brands else timezone.utc
    sequences_every = timedelta(minutes=int(os.environ.get("SEQUENCES_EVERY", "60")))
    comments_every = timedelta(minutes=int(os.environ.get("COMMENTS_EVERY", "60")))
    last_publish = last_metrics = last_sequences = last_comments = datetime.min.replace(tzinfo=timezone.utc)
    last_daily_date = last_report_date = None
    log.info("worker started; dry_run=%s brands=%s", factory.settings.dry_run, list(brands))
    while True:
        now = datetime.now(timezone.utc)
        try:
            if now - last_publish >= publish_every:
                res = factory.publish_due(now)
                if res:
                    log.info("published: %s", res)
                last_publish = now
            local = now.astimezone(tz)
            hh, mm = map(int, daily_at.split(":"))
            if local.date() != last_daily_date and (local.hour, local.minute) >= (hh, mm):
                for slug in factory.brands():
                    log.info("daily %s: %s", slug, factory.daily(slug))
                last_daily_date = local.date()
            if now - last_metrics >= metrics_every:
                log.info("metrics snapshots: %s", factory.collect_metrics())
                last_metrics = now
        except Exception:  # keep the worker alive; errors land in the log
            log.exception("worker tick failed")
        if now - last_sequences >= sequences_every:  # own try: a failing step above can't starve it
            last_sequences = now
            try:
                from .funnel.sequences import run_sequences
                res = run_sequences(factory, now, confirm=True)
                if res["sent"] or res["dry_run"] or res["failed"]:
                    log.info("sequences: mode=%s sent=%s dry_run=%s failed=%s skipped=%s blocked=%s", res["mode"],
                             res["sent"], res["dry_run"], res["failed"], res["skipped"], res["blocked"])
            except Exception:
                log.exception("sequence run failed")
        if comments_every and now - last_comments >= comments_every:
            last_comments = now
            try:
                from .community import collect_comments, draft_replies
                res = collect_comments(factory)
                if res.get("new"):
                    log.info("comments: %s; drafted %s", {k: v for k, v in res.items() if k != "errors"},
                             len(draft_replies(factory)))
            except Exception:
                log.exception("comment collection failed")
        try:
            local = now.astimezone(tz)
            hh, mm = map(int, daily_at.split(":"))
            if local.weekday() == 0 and local.date() != last_report_date and (local.hour, local.minute) >= (hh, mm):
                from .reports import save_report
                log.info("weekly report: %s", save_report(factory))
                last_report_date = local.date()
        except Exception:
            log.exception("weekly report failed")
        time.sleep(30)


if __name__ == "__main__":
    run_forever()
