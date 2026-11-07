"""The factory line.

    idea --produce--> post[scripted] --render--> post[in_review]
         --approve--> post[approved] --schedule--> publications[queued]
         --publish_due--> publications[published] --collect_metrics--> metrics

Post statuses: draft, scripted, rendered, in_review, approved, scheduled,
published, rejected, blocked, failed.
Nothing is published without status 'approved', and approval is a human action
unless the brand explicitly sets require_human_review: false.
"""
from __future__ import annotations

import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import BrandProfile, Settings, load_brand, load_brands
from .db import DB, now_iso
from .guardrails import check_cadence, run_content_checks, summarize
from .llm import LLM
from .writer import write_with_review


def _affiliates_in(brand: BrandProfile, caption: str, title: str) -> tuple[list[str], list[str]]:
    """(offers whose link is actually in the caption, offers that would fit by keyword)."""
    present = [a.slug or a.name for a in brand.affiliates
               if a.url in caption or (a.slug and f"/go/{a.slug}" in caption)]
    text = f"{caption} {title}".lower()
    fits = [a.slug or a.name for a in brand.affiliates if any(k.lower() in text for k in a.keywords)]
    return present, fits


@dataclass
class Factory:
    settings: Settings
    db: DB
    llm: LLM

    @classmethod
    def create(cls, settings: Settings | None = None) -> "Factory":
        settings = settings or Settings.load()
        db = DB(settings.db_path)
        llm = LLM(settings.llm_provider, settings.anthropic_model, settings.anthropic_effort, db=db)
        return cls(settings, db, llm)

    # ------------------------------------------------------------------ brands
    def brands(self) -> dict[str, BrandProfile]:
        return load_brands(self.settings.brands_dir)

    def brand(self, slug: str) -> BrandProfile:
        return load_brand(self.settings.brands_dir, slug)

    # ------------------------------------------------------------------ ideas
    def ideas(self, brand: str, n: int = 10, online: bool = True) -> list[int]:
        from .ideas import generate_ideas
        return generate_ideas(self.db, self.llm, self.brand(brand), n=n, online=online)

    # ------------------------------------------------------------------ produce
    def produce(self, idea_id: int, render: bool = True, notes: str = "", research: bool | None = None) -> int:
        from . import research as rs
        idea = self.db.get("ideas", idea_id)
        if not idea:
            raise KeyError(f"No idea #{idea_id}")
        brand = self.brand(idea["brand"])
        # Research only when a real model will read it; offline drafts don't need it.
        do_research = (self.llm.provider != "offline") if research is None else research
        sources = rs.gather(idea["title"], online=do_research)
        script, verdict = write_with_review(self.llm, brand, idea["title"], idea["angle"], idea["format"],
                                            notes=notes, research=rs.as_prompt(sources))
        for s in sources:
            if s.url and s.url not in script.sources:
                script.sources.append(s.url)
        affiliate_slugs, affiliate_ideas = _affiliates_in(brand, script.caption, script.title)
        post_id = self.db.insert("posts", {
            "brand": brand.slug, "idea_id": idea_id, "format": idea["format"], "status": "scripted",
            "title": script.title, "script": script.model_dump(), "caption": script.caption,
            "hashtags": script.hashtags, "disclosure": brand.ai_disclosure,
            "meta": {"editor": verdict.model_dump(), "affiliate_slugs": affiliate_slugs,
                     "affiliate_suggestions": affiliate_ideas,
                     "llm": self.llm.provider},
        })
        self.db.update("ideas", idea_id, {"status": "used"})
        self.db.log("post.scripted", "post", post_id, {"idea": idea_id, "editor_score": verdict.score})
        if render:
            self.render(post_id)
        else:
            self.check(post_id)
        return post_id

    def import_script(self, brand_slug: str, script: dict, fmt: str, pillar: str = "", angle: str = "",
                      render: bool = True, source: str = "import", platforms: list[str] | None = None) -> int:
        """Load a hand-written or externally written script as a post for review.

        `platforms` pins the post to some of the brand's accounts, e.g. a 60-90s
        cut that should only go to TikTok while the 30-45s version goes elsewhere."""
        from .schemas import Script
        brand = self.brand(brand_slug)
        sc = Script.model_validate(script)
        platforms = [p for p in (platforms or []) if p]
        unknown = [p for p in platforms if not brand.account(p)]
        if unknown:
            raise ValueError(f"{brand.slug} has no enabled account for: {', '.join(unknown)}")
        idea_id = self.db.insert("ideas", {"brand": brand.slug, "title": sc.title, "angle": angle,
                                           "format": fmt, "pillar": pillar, "source": source, "status": "used"})
        affiliate_slugs, affiliate_ideas = _affiliates_in(brand, sc.caption, sc.title)
        post_id = self.db.insert("posts", {
            "brand": brand.slug, "idea_id": idea_id, "format": fmt, "status": "scripted",
            "title": sc.title, "script": sc.model_dump(), "caption": sc.caption, "hashtags": sc.hashtags,
            "disclosure": brand.ai_disclosure, "meta": {"affiliate_slugs": affiliate_slugs, "affiliate_suggestions": affiliate_ideas, "llm": source,
                                                         "human_edited": True,
                                                         **({"platforms": platforms} if platforms else {})},
        })
        self.db.log("post.imported", "post", post_id, {"source": source})
        if render:
            self.render(post_id)
        else:
            self.check(post_id)
        return post_id

    def render(self, post_id: int) -> dict:
        from .media import render_post
        post = self._post(post_id)
        brand = self.brand(post["brand"])
        try:
            assets = render_post(self.settings, brand, post)
        except Exception as e:
            self.db.update("posts", post_id, {"status": "failed",
                                              "review_notes": f"Render failed: {e}"})
            self.db.log("post.render_failed", "post", post_id, {"error": str(e), "tb": traceback.format_exc()[-2000:]})
            raise
        self.db.update("posts", post_id, {"assets": assets, "status": "rendered"})
        self.db.log("post.rendered", "post", post_id, {"files": len(assets.get("provenance", []))})
        self.check(post_id)
        return assets

    def check(self, post_id: int) -> dict:
        post = self._post(post_id)
        brand = self.brand(post["brand"])
        result = summarize(run_content_checks(self.db, brand, post))
        status = "blocked" if result["status"] == "block" else "in_review"
        if status == "in_review" and not brand.require_human_review and result["status"] == "ok":
            status = "approved"
        self.db.update("posts", post_id, {"checks": result, "status": status})
        return result

    def _post(self, post_id: int) -> dict:
        post = self.db.get("posts", post_id)
        if not post:
            raise KeyError(f"No post #{post_id}")
        return post

    # ------------------------------------------------------------------ review
    def edit(self, post_id: int, *, caption: str | None = None, script: dict | None = None,
             title: str | None = None, rerender: bool = False, actor: str = "human") -> None:
        post = self._post(post_id)
        changes: dict = {}
        if caption is not None:
            changes["caption"] = caption
        if title is not None:
            changes["title"] = title
        if script is not None:
            changes["script"] = script
        meta = post.get("meta") or {}
        meta["human_edited"] = True
        changes["meta"] = meta
        self.db.update("posts", post_id, changes)
        self.db.log("post.edited", "post", post_id, {"fields": list(changes)}, actor=actor)
        if rerender:
            self.render(post_id)
        else:
            self.check(post_id)

    def approve(self, post_id: int, actor: str = "human", notes: str = "") -> None:
        post = self._post(post_id)
        if post["status"] == "blocked":
            raise PermissionError("Post is blocked by a guardrail; fix it and re-check before approving")
        if post["status"] not in ("in_review", "rendered", "scripted", "approved"):
            raise ValueError(f"Can't approve a post in status {post['status']}")
        self.db.update("posts", post_id, {"status": "approved", "review_notes": notes})
        self.db.log("post.approved", "post", post_id, {"notes": notes}, actor=actor)

    def reject(self, post_id: int, reason: str = "", actor: str = "human") -> None:
        self._post(post_id)
        self.db.update("posts", post_id, {"status": "rejected", "review_notes": reason})
        self.db.log("post.rejected", "post", post_id, {"reason": reason}, actor=actor)

    # ------------------------------------------------------------------ schedule
    def schedule(self, post_id: int, platforms: list[str] | None = None,
                 at: datetime | None = None) -> list[int]:
        from .scheduler import next_slot
        post = self._post(post_id)
        if post["status"] != "approved":
            raise PermissionError("Only approved posts can be scheduled")
        brand = self.brand(post["brand"])
        pinned = (post.get("meta") or {}).get("platforms") or []
        targets = platforms or [a.platform for a in brand.accounts
                                if a.enabled and post["format"] in a.formats
                                and (not pinned or a.platform in pinned)]
        if not targets:
            raise ValueError(f"No enabled account in {brand.slug} accepts format '{post['format']}'")
        pub_ids = []
        for platform in targets:
            slot = at or next_slot(self.db, brand, platform)
            cadence = check_cadence(self.db, brand, platform, slot)
            if cadence.level == "block":
                raise PermissionError(cadence.message)
            acct = brand.account(platform)
            pub_ids.append(self.db.insert("publications", {
                "post_id": post_id, "platform": platform, "account": acct.handle if acct else "",
                "status": "queued", "scheduled_at": slot.isoformat(),
            }))
        self.db.update("posts", post_id, {"status": "scheduled", "scheduled_at": min(
            self.db.get("publications", p)["scheduled_at"] for p in pub_ids)})
        self.db.log("post.scheduled", "post", post_id, {"publications": pub_ids})
        return pub_ids

    # ------------------------------------------------------------------ publish
    def build_request(self, post: dict, platform: str):
        from .publish import PublishRequest
        brand = self.brand(post["brand"])
        assets = post.get("assets") or {}
        out = self.settings.output_dir
        tags = post.get("hashtags") or []
        hashtag_line = " ".join("#" + t.lstrip("#").replace(" ", "") for t in tags)
        disclosure = post.get("disclosure") or ""
        caption = "\n\n".join(x for x in [post.get("caption", ""), disclosure, hashtag_line] if x)
        script = post.get("script") or {}
        images = [out / p for p in (assets.get("slides") or assets.get("images") or [])]
        video = out / assets["video"] if assets.get("video") else None
        thumb = out / assets["thumbnail"] if assets.get("thumbnail") else None
        base = self.settings.public_media_base_url
        public = {}
        if base:
            for p in [*(assets.get("slides") or []), *(assets.get("images") or []), assets.get("video"), assets.get("thumbnail")]:
                if p:
                    public[str(out / p)] = f"{base}/{p}"
        description = "\n\n".join(x for x in [script.get("description", ""), disclosure] if x)
        return PublishRequest(
            platform=platform, brand=brand, settings=self.settings, format=post["format"],
            title=post.get("title", ""), caption=caption, description=description, tags=tags,
            video_path=video, image_paths=images, thumbnail_path=thumb, public_urls=public,
            ai_generated=True, realistic_synthetic=brand.realistic_synthetic_media,
            has_paid_promotion=bool((post.get("meta") or {}).get("sponsored")),
        )

    def publish_due(self, now: datetime | None = None, max_attempts: int = 3) -> list[dict]:
        from .publish import PublishError, get_publisher
        now = now or datetime.now(timezone.utc)
        due = self.db.query(
            "SELECT * FROM publications WHERE status = 'queued' AND scheduled_at <= ? AND attempts < ? ORDER BY scheduled_at",
            [now.isoformat(), max_attempts])
        results = []
        if due and not self.settings.dry_run:
            from .publish.tokens import refresh_long_lived, refresh_tiktok_if_needed
            try:
                if any(p["platform"] == "tiktok" for p in due):
                    refresh_tiktok_if_needed(self.settings)
                refresh_long_lived(self.settings)
            except Exception as e:  # a failed refresh surfaces as a publish error below
                self.db.log("tokens.refresh_failed", "", None, {"error": str(e)})
        for pub in due:
            post = self.db.get("posts", pub["post_id"])
            if post["status"] not in ("scheduled", "published"):
                self.db.update("publications", pub["id"], {"status": "failed", "error": f"post status {post['status']}"})
                continue
            publisher = get_publisher(pub["platform"], self.settings)
            self.db.update("publications", pub["id"], {"status": "publishing", "attempts": pub["attempts"] + 1})
            try:
                res = publisher.publish(self.build_request(post, pub["platform"]))
                status = "dry_run" if res.raw.get("dry_run") else "published"
                self.db.update("publications", pub["id"], {
                    "status": status, "remote_id": res.remote_id, "url": res.url,
                    "published_at": now_iso(), "meta": res.raw, "error": ""})
                self.db.update("posts", post["id"], {"status": "published"})
                self.db.log(f"publication.{status}", "publication", pub["id"], {"platform": pub["platform"], "url": res.url})
                results.append({"publication": pub["id"], "status": status, "url": res.url})
            except PublishError as e:
                retry = e.retryable and pub["attempts"] + 1 < max_attempts
                self.db.update("publications", pub["id"], {"status": "queued" if retry else "failed", "error": str(e)})
                self.db.log("publication.failed", "publication", pub["id"], {"error": str(e), "retry": retry})
                results.append({"publication": pub["id"], "status": "failed", "error": str(e)})
        return results

    # ------------------------------------------------------------------ analytics
    def collect_metrics(self) -> int:
        from .publish import get_publisher
        pubs = self.db.query("SELECT * FROM publications WHERE status = 'published' AND remote_id != ''")
        n = 0
        for pub in pubs:
            try:
                snap = get_publisher(pub["platform"], self.settings, dry_run=False).fetch_metrics(pub["remote_id"])
            except Exception as e:
                self.db.log("metrics.failed", "publication", pub["id"], {"error": str(e)})
                continue
            self.db.insert("metrics", {"publication_id": pub["id"], "captured_at": now_iso(),
                                       **{k: v for k, v in snap.__dict__.items()}})
            n += 1
        return n

    # ------------------------------------------------------------------ daily run
    def daily(self, brand: str, n_ideas: int = 8, n_produce: int = 2, online: bool = True) -> dict:
        """One cron-able tick: top up ideas, produce the best few for review,
        publish whatever is due, refresh metrics. Never auto-approves."""
        from .ideas import top_ideas
        from .insights import rescore_backlog
        report: dict = {"brand": brand}
        report["rescored"] = rescore_backlog(self.db, brand)
        backlog = top_ideas(self.db, brand, limit=100)
        if len(backlog) < n_produce * 3:
            report["new_ideas"] = len(self.ideas(brand, n=n_ideas, online=online))
        pending = self.db.scalar("SELECT COUNT(*) FROM posts WHERE brand = ? AND status = 'in_review'", [brand])
        produced = []
        # Don't pile up an unreviewable queue: cap at 2 days of production.
        room = max(0, n_produce * 2 - (pending or 0))
        limit = min(n_produce, room)
        queue = top_ideas(self.db, brand, limit=limit, status="approved")
        queue += top_ideas(self.db, brand, limit=limit - len(queue), status="new") if len(queue) < limit else []
        for idea in queue:
            try:
                produced.append(self.produce(idea["id"]))
            except Exception as e:
                report.setdefault("errors", []).append(f"idea {idea['id']}: {e}")
        report["produced"] = produced
        report["published"] = self.publish_due()
        try:
            report["metrics"] = self.collect_metrics()
        except Exception as e:
            report["metrics_error"] = str(e)
        self.db.log("daily.run", "brand", None, report)
        return report

    def asset_path(self, rel: str) -> Path:
        return self.settings.output_dir / rel
