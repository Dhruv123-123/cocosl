"""Review gate: every post has a review status, and nothing goes out (scheduling, export-week) unless it's approved.

Statuses, in order:  draft → native_review → legal_review → approved

* draft:          written but not yet passed by you (still in Review, or blocked by a guardrail).
* native_review:  waiting on a fluent speaker to read it (e.g. Dinero Simple's Spanish).
* legal_review:   waiting on an attorney / tax pro read (e.g. ITIN or immigration-adjacent money topics).
* approved:       you approved it in Review (fact-checked); it can be scheduled and exported.

Which reviews a post needs:
* the brand's `review_stages` (e.g. `review_stages: [native_review]` in brands/dinero-simple.yaml), plus
* the pack item's own `"review": "legal_review"` or `"review": ["native_review", "legal_review"]` on import,
* or `factory review-gate require <id> legal_review` later.
A post can only be approved once every review it needs has been passed (`factory review-gate pass`).

    factory review-gate                       # counts per brand and status
    factory review-gate list --status native_review [--brand dinero-simple]
    factory review-gate pass 42 native_review --by "Ana (native speaker)" --note "fixed 2 phrases"
    factory review-gate require 42 legal_review --note "ITIN claim"
    factory review-gate send-back 42 --note "needs a rewrite"   # back to draft, passed reviews cleared
"""
from __future__ import annotations

from datetime import datetime, timezone

STAGES = ("draft", "native_review", "legal_review", "approved")
REVIEWS = ("native_review", "legal_review")
APPROVED_POST_STATUSES = ("approved", "scheduled", "published")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _meta(post: dict) -> dict:
    m = post.get("meta")
    return m if isinstance(m, dict) else {}


def required(post: dict, brand=None) -> list[str]:
    r = _meta(post).get("review") or {}
    need = list(r.get("required") or [])
    for s in (getattr(brand, "review_stages", None) or []):
        if s not in need:
            need.append(s)
    return [s for s in REVIEWS if s in need]


def passed(post: dict) -> dict:
    return dict((_meta(post).get("review") or {}).get("passed") or {})


def pending(post: dict, brand=None) -> list[str]:
    done = passed(post)
    return [s for s in required(post, brand) if s not in done]


def status(post: dict, brand=None) -> str:
    """draft | native_review | legal_review | approved"""
    if post.get("status") in APPROVED_POST_STATUSES:
        return "approved"
    if post.get("status") in ("rejected", "failed"):
        return "draft"
    if post.get("status") in ("scripted", "rendered", "in_review", "blocked"):
        waiting = pending(post, brand)
        if waiting and (_meta(post).get("review") or {}).get("submitted", True):
            return waiting[0]
    return "draft"


def normalize(value) -> list[str]:
    if not value:
        return []
    items = [value] if isinstance(value, str) else list(value)
    out = []
    for v in items:
        v = str(v).strip().lower().replace("-", "_").replace(" ", "_")
        v = {"native": "native_review", "legal": "legal_review"}.get(v, v)
        if v not in REVIEWS:
            raise ValueError(f"Unknown review '{v}': use native_review or legal_review")
        if v not in out:
            out.append(v)
    return out


def _save(factory, post_id: int, review: dict, event: str, details: dict, actor: str) -> None:
    post = factory.db.get("posts", post_id)
    meta = dict(_meta(post))
    meta["review"] = review
    factory.db.update("posts", post_id, {"meta": meta})
    factory.db.log(f"review.{event}", "post", post_id, details, actor=actor)


def require(factory, post_id: int, stages, note: str = "", actor: str = "human") -> list[str]:
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    if post["status"] in ("scheduled", "published"):
        raise PermissionError(f"Post #{post_id} is {post['status']}: unschedule it first")
    r = dict(_meta(post).get("review") or {})
    need = list(r.get("required") or [])
    for s in normalize(stages):
        if s not in need:
            need.append(s)
    r["required"] = need
    r.setdefault("history", []).append({"at": _now(), "by": actor, "event": "require", "stages": need, "note": note})
    if post["status"] == "approved":  # a new review takes it back to Review
        factory.db.update("posts", post_id, {"status": "in_review"})
    _save(factory, post_id, r, "require", {"stages": need, "note": note}, actor)
    return need


def pass_stage(factory, post_id: int, stage: str, by: str = "", note: str = "", actor: str = "human") -> str:
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    (stage,) = normalize(stage)
    brand = factory.brands().get(post["brand"])
    if stage not in required(post, brand):
        raise ValueError(f"Post #{post_id} doesn't need {stage} (it needs: {', '.join(required(post, brand)) or 'none'})")
    r = dict(_meta(post).get("review") or {})
    r.setdefault("passed", {})[stage] = {"by": by or actor, "at": _now(), "note": note}
    r.setdefault("history", []).append({"at": _now(), "by": by or actor, "event": "pass", "stage": stage, "note": note})
    _save(factory, post_id, r, "pass", {"stage": stage, "by": by, "note": note}, actor)
    return status(factory.db.get("posts", post_id), brand)


def send_back(factory, post_id: int, note: str = "", actor: str = "human") -> None:
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    if post["status"] in ("scheduled", "published"):
        raise PermissionError(f"Post #{post_id} is {post['status']}: unschedule it first")
    r = dict(_meta(post).get("review") or {})
    r["passed"] = {}
    r.setdefault("history", []).append({"at": _now(), "by": actor, "event": "send_back", "note": note})
    if post["status"] == "approved":
        factory.db.update("posts", post_id, {"status": "in_review"})
    _save(factory, post_id, r, "send_back", {"note": note}, actor)


def check_can_approve(post: dict, brand=None) -> None:
    waiting = pending(post, brand)
    if waiting:
        raise PermissionError(f"Post #{post['id']} still needs {' and '.join(w.replace('_', ' ') for w in waiting)} "
                              f"(`factory review-gate pass {post['id']} {waiting[0]}` once it's done)")


def counts(factory, brand: str | None = None) -> dict:
    brands = factory.brands()
    out: dict = {}
    sql = "SELECT * FROM posts WHERE status NOT IN ('rejected', 'failed')" + (" AND brand = ?" if brand else "")
    for p in factory.db.query(sql, [brand] if brand else []):
        s = status(p, brands.get(p["brand"]))
        out.setdefault(p["brand"], dict.fromkeys(STAGES, 0))[s] += 1
    return out


def listing(factory, stage: str | None = None, brand: str | None = None) -> list[dict]:
    brands = factory.brands()
    sql = "SELECT * FROM posts WHERE status NOT IN ('rejected', 'failed')" + (" AND brand = ?" if brand else "") + " ORDER BY id"
    rows = []
    for p in factory.db.query(sql, [brand] if brand else []):
        s = status(p, brands.get(p["brand"]))
        if stage and s != stage:
            continue
        rows.append({"id": p["id"], "brand": p["brand"], "title": p["title"], "format": p["format"], "review": s,
                     "needs": pending(p, brands.get(p["brand"])), "passed": sorted(passed(p))})
    return rows


def register(sub, factory_fn) -> None:
    s = sub.add_parser("review-gate", help="review status per post (draft, native_review, legal_review, approved); "
                                           "pass, require or send back a review")
    s.add_argument("action", nargs="?", default="counts", choices=["counts", "list", "pass", "require", "send-back"])
    s.add_argument("post_id", nargs="?", type=int)
    s.add_argument("stage", nargs="?", default="")
    s.add_argument("--status", default="", choices=["", *STAGES])
    s.add_argument("--brand", default=None)
    s.add_argument("--by", default="", help="who did the review (name, role)")
    s.add_argument("--note", default="")

    def cmd(a):
        f = factory_fn(a)
        if a.action == "counts":
            c = counts(f, a.brand)
            if not c:
                print("No posts yet.")
            for brand, n in c.items():
                print(f"{brand}: " + " · ".join(f"{k.replace('_', ' ')} {v}" for k, v in n.items()))
            return
        if a.action == "list":
            rows = listing(f, a.status or None, a.brand)
            for r in rows:
                extra = f" · needs {', '.join(r['needs'])}" if r["needs"] and r["review"] != "approved" else ""
                print(f"#{r['id']} [{r['brand']}] {r['review']} · {r['format']} · {r['title'][:70]}{extra}")
            print(f"{len(rows)} post(s)")
            return
        if a.post_id is None:
            raise SystemExit(f"usage: factory review-gate {a.action} <post id>" + (" <stage>" if a.action != "send-back" else ""))
        if a.action == "pass":
            print(f"#{a.post_id}: {pass_stage(f, a.post_id, a.stage, a.by, a.note)}")
        elif a.action == "require":
            print(f"#{a.post_id} needs: {', '.join(require(f, a.post_id, a.stage, a.note))}")
        else:
            send_back(f, a.post_id, a.note)
            print(f"#{a.post_id}: back to draft")
    s.set_defaults(func=cmd)
