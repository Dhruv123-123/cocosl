"""Long-running worker for Docker: a tiny scheduler with no extra dependencies.

* every PUBLISH_EVERY minutes: publish due posts
* once a day at DAILY_AT (local time of the first brand): `daily` for each brand
* every METRICS_EVERY hours: collect metrics

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
    last_publish = last_metrics = datetime.min.replace(tzinfo=timezone.utc)
    last_daily_date = None
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
        time.sleep(30)


if __name__ == "__main__":
    run_forever()
