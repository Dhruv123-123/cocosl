"""Background jobs for slow factory work (idea generation, producing, rendering).

One worker thread on purpose: rendering is CPU/GPU heavy and the SQLite
connection is shared, so jobs run one after another. State lives in memory;
the durable record is the audit_log the Factory writes.
"""
from __future__ import annotations

import itertools
import threading
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from ..db import now_iso


@dataclass
class Job:
    id: int
    kind: str                 # ideas | produce | render | daily
    label: str
    entity: str = ""          # "idea" | "post" | "brand"
    entity_id: Any = None
    status: str = "queued"    # queued | running | done | failed
    result: Any = None
    error: str = ""
    created_at: str = field(default_factory=now_iso)
    finished_at: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


class JobRunner:
    def __init__(self, max_history: int = 50):
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="factory-job")
        self._jobs: dict[int, Job] = {}
        self._futures: dict[int, Future] = {}
        self._ids = itertools.count(1)
        self._lock = threading.Lock()
        self._max = max_history

    def submit(self, kind: str, label: str, fn: Callable[[], Any], entity: str = "",
               entity_id: Any = None) -> Job:
        job = Job(id=next(self._ids), kind=kind, label=label, entity=entity, entity_id=entity_id)
        with self._lock:
            self._jobs[job.id] = job
            self._trim()
        self._futures[job.id] = self._pool.submit(self._run, job, fn)
        return job

    def _run(self, job: Job, fn: Callable[[], Any]) -> Any:
        job.status = "running"
        try:
            job.result = fn()
            job.status = "done"
        except Exception as e:  # recorded for the UI; the Factory logs details to audit_log
            job.status = "failed"
            job.error = f"{type(e).__name__}: {e}"
            job.result = {"traceback": traceback.format_exc()[-1500:]}
        finally:
            job.finished_at = now_iso()
        return job.result

    def _trim(self) -> None:
        done = [j for j in self._jobs.values() if j.status in ("done", "failed")]
        for j in sorted(done, key=lambda j: j.id)[: max(0, len(self._jobs) - self._max)]:
            self._jobs.pop(j.id, None)
            self._futures.pop(j.id, None)

    def get(self, job_id: int) -> Job | None:
        return self._jobs.get(job_id)

    def all(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda j: -j.id)

    def running(self) -> list[Job]:
        return [j for j in self.all() if j.status in ("queued", "running")]

    def active_for(self, entity: str, entity_id: Any) -> Job | None:
        return next((j for j in self.running() if j.entity == entity and j.entity_id == entity_id), None)

    def wait(self, job_id: int | None = None, timeout: float = 60) -> None:
        """Block until one job (or all jobs) finish. Used by tests and wait=true API calls."""
        futures = [self._futures[job_id]] if job_id else list(self._futures.values())
        for f in futures:
            f.result(timeout=timeout)

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)
