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

import os

import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import i18n
from .config import BrandProfile, Settings, load_brand, load_brands
from .db import DB, now_iso
from .guardrails import check_cadence, run_content_checks, summarize
from .llm import LLM
from .writer import write_with_review


def voice_of_assets(assets: dict) -> str | None:
    """The voice provider a rendered video used (human = the owner's recording)."""
    for e in (assets or {}).get("provenance") or []:
        if str(e.get("path", "")).endswith("audio.wav"):
            return e.get("provider") or e.get("tool")
    return None


def _affiliates_in(brand: BrandProfile, caption: str, title: str) -> tuple[list[str], list[str]]:
    """(offers whose link is actually in the caption, offers that would fit by keyword)."""
    present = [a.slug or a.name for a in brand.affiliates
               if a.url in caption or (a.slug and f"/go/{a.slug}" in caption)]
    text = f"{caption} {title}".lower()
    fits = [a.slug or a.name for a in brand.affiliates if any(k.lower() in text for k in a.keywords)]
    return present, fits


def _plan_day(post: dict, brand: BrandProfile) -> datetime | None:
    """Start of the post's planned local day (`"date"` on a pack item), or None when it has none or it's past."""
    from datetime import date as _date
    from zoneinfo import ZoneInfo
    raw = (post.get("meta") or {}).get("plan_date")
    if not raw:
        return None
    try:
        tz = ZoneInfo(brand.cadence.timezone)
        day = _date.fromisoformat(str(raw)[:10])
    except (ValueError, KeyError):
        return None
    if day < datetime.now(tz).date():
        return None  # the plan slid: fall back to the next free slot
    return datetime.combine(day, datetime.min.time(), tzinfo=tz) - timedelta(seconds=1)


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
        sources = rs.gather(idea["title"], online=do_research, lang=i18n.lang_of(brand))
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
        self._render_or_queue(post_id, render)
        return post_id

    def import_script(self, brand_slug: str, script: dict, fmt: str, pillar: str = "", angle: str = "",
                      render: bool = True, source: str = "import") -> int:
        """Load a hand-written or externally written script as a post for review."""
        from .schemas import Script
        brand = self.brand(brand_slug)
        sc = Script.model_validate(script)
        idea_id = self.db.insert("ideas", {"brand": brand.slug, "title": sc.title, "angle": angle,
                                           "format": fmt, "pillar": pillar, "source": source, "status": "used"})
        affiliate_slugs, affiliate_ideas = _affiliates_in(brand, sc.caption, sc.title)
        post_id = self.db.insert("posts", {
            "brand": brand.slug, "idea_id": idea_id, "format": fmt, "status": "scripted",
            "title": sc.title, "script": sc.model_dump(), "caption": sc.caption, "hashtags": sc.hashtags,
            "disclosure": brand.ai_disclosure, "meta": {"affiliate_slugs": affiliate_slugs, "affiliate_suggestions": affiliate_ideas, "llm": source,
                                                         "human_edited": True},
        })
        self.db.log("post.imported", "post", post_id, {"source": source})
        self._render_or_queue(post_id, render)
        return post_id

    def _render_or_queue(self, post_id: int, render: bool) -> None:
        """Render now, or (RENDER_QUEUE=1, as in docker-compose) hand it to the renderer process."""
        if render and os.environ.get("RENDER_QUEUE", "0") == "1":
            self.check(post_id)
            from .renderq import enqueue
            enqueue(self, post_id, reason="new")
        elif render:
            self.render(post_id)
        else:
            self.check(post_id)

    def render(self, post_id: int) -> dict:
        from .media import render_post
        post = self._post(post_id)
        brand = self.brand(post["brand"])
        if (post.get("meta") or {}).get("challenge") and post["format"] == "image":
            self.check(post_id)  # a challenge day's image is its tracker (factory challenge), not generated art
            return post.get("assets") or {}
        if post["format"] in ("short", "mid", "long"):  # vary the look against this channel's recent videos
            recent = self.db.query("SELECT assets FROM posts WHERE brand = ? AND id != ? AND format IN ('short','mid','long') "
                                   "AND status != 'rejected' ORDER BY id DESC LIMIT 8", [brand.slug, post_id])
            post["_recent_looks"] = [(r["assets"] or {}).get("look") for r in recent if (r["assets"] or {}).get("look")]
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
        if self.render_pending(post_id):
            raise PermissionError("Post is still waiting in the render queue; review it once it has rendered")
        from .review import check_can_approve
        check_can_approve(post, self.brands().get(post["brand"]))
        self.db.update("posts", post_id, {"status": "approved", "review_notes": notes})
        self.db.log("post.approved", "post", post_id, {"notes": notes}, actor=actor)

    def choose_thumbnail(self, post_id: int, index: int, actor: str = "human") -> str:
        """Use thumbnail variant `index` (0 = the original) as the post's thumbnail."""
        post = self._post(post_id)
        if post["status"] in ("scheduled", "published"):
            raise PermissionError("The thumbnail is already on its way to the platforms; unschedule first")
        assets = dict(post.get("assets") or {})
        variants = assets.get("thumbnail_variants") or []
        if not 0 <= index < len(variants):
            raise ValueError(f"Post #{post_id} has {len(variants)} thumbnail option(s)")
        assets["thumbnail"] = variants[index]
        self.db.update("posts", post_id, {"assets": assets})
        self.db.log("post.thumbnail_chosen", "post", post_id, {"thumbnail": variants[index]}, actor=actor)
        return variants[index]

    def render_pending(self, post_id: int) -> bool:
        try:
            return bool(self.db.one("SELECT id FROM render_jobs WHERE post_id = ? AND status IN ('queued','running')",
                                    [post_id]))
        except Exception:  # queue table not created yet
            return False

    def mark_language_reviewed(self, post_id: int, reviewer: str, actor: str = "human") -> dict:
        """Record that a fluent speaker read and corrected a non-English post."""
        reviewer = reviewer.strip()
        if not reviewer:
            raise ValueError("Give the reviewer's name")
        post = self._post(post_id)
        meta = post.get("meta") or {}
        meta["native_review"] = reviewer
        meta["native_review_at"] = now_iso()
        self.db.update("posts", post_id, {"meta": meta})
        self.db.log("post.language_reviewed", "post", post_id, {"reviewer": reviewer}, actor=actor)
        return self.check(post_id)

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
        assets = post.get("assets") or {}
        if not (assets.get("slides") if post["format"] in ("carousel", "image") else assets.get("video")):
            raise PermissionError("Post has no rendered media yet; render it before scheduling")
        brand = self.brand(post["brand"])
        targets = platforms or [a.platform for a in brand.accounts
                                if a.enabled and post["format"] in a.formats]
        if not targets:
            raise ValueError(f"No enabled account in {brand.slug} accepts format '{post['format']}'")
        if post["format"] in ("short", "mid", "long") and (brand.own_voice or (post.get("meta") or {}).get("own_voice")):
            from .media.tts import human_voice_source
            if human_voice_source(self.settings, brand, post_id) is None or \
                    (voice_of_assets(assets) or "") != "human":
                raise PermissionError("Waiting for your narration: `factory voice "
                                      f"{post_id} <recording>` (see `factory recordings`)")
        from .guardrails import check_no_repost
        for platform in list(targets):
            rp = check_no_repost(self.db, post, platform, output_dir=self.settings.output_dir)
            if rp.level == "block":
                if platforms:  # asked for explicitly: say no
                    raise ValueError(f"Not scheduling on {platform}: {rp.message}")
                targets.remove(platform)  # automatic: skip that platform, schedule the rest
                self.db.log("post.skipped_repost", "post", post_id, {"platform": platform, "reason": rp.message})
        if not targets:
            raise ValueError("Every platform for this post would be a repost; nothing scheduled")
        from .publish.preflight import blocking, check_post
        stop = blocking(check_post(self, post, targets), self.settings.dry_run)
        if stop:
            raise PermissionError("Media check failed: " + "; ".join(map(str, stop)))
        # Work out every slot first so a cadence block can't leave a half-scheduled post behind.
        plan = []
        from .scheduler import platform_cap_reached, same_day_slots
        plan_day = _plan_day(post, brand)
        if at:
            slots = {p: at for p in targets}
        elif plan_day:  # a pack's planned date: that day's slots; the plan already set the weekly mix
            slots = same_day_slots(self.db, brand, targets, post["format"], after=plan_day, weekly_cap=False)
        else:
            slots = same_day_slots(self.db, brand, targets, post["format"])
        for platform in list(targets):
            slot = slots[platform]
            cap = platform_cap_reached(self.db, brand, platform, post["format"], slot)
            if cap is not None:
                if platforms:
                    raise PermissionError(f"{platform} already has {cap} {post['format']} post(s) that week (platform_weekly_caps)")
                self.db.log("post.skipped_cap", "post", post_id, {"platform": platform, "cap": cap})
                continue
            cadence = check_cadence(self.db, brand, platform, slot)
            if cadence.level == "block":
                raise PermissionError(cadence.message)
            plan.append((platform, slot))
        if not plan:
            raise ValueError("Every platform for this post is at its weekly cap; nothing scheduled")
        pub_ids = []
        for platform, slot in plan:
            acct = brand.account(platform)
            pub_ids.append(self.db.insert("publications", {
                "post_id": post_id, "platform": platform, "account": acct.handle if acct else "",
                "status": "queued", "scheduled_at": slot.isoformat(),
            }))
        self.db.update("posts", post_id, {"status": "scheduled", "scheduled_at": min(s for _, s in plan).isoformat()})
        self.db.log("post.scheduled", "post", post_id, {"publications": pub_ids})
        from .manual import prepare
        prepare(self, pub_ids)  # post-by-hand platforms get their package now, so they can be batched
        return pub_ids

    def unschedule(self, post_id: int, actor: str = "human") -> int:
        """Cancel a post's queued publications and put it back to approved. Returns how many were cancelled."""
        post = self._post(post_id)
        if post["status"] != "scheduled":
            raise ValueError(f"Post #{post_id} is {post['status']}, not scheduled")
        cur = self.db.execute("UPDATE publications SET status = 'cancelled', error = 'unscheduled', updated_at = ? "
                              "WHERE post_id = ? AND status = 'queued'", [now_iso(), post_id])
        live = self.db.scalar("SELECT COUNT(*) FROM publications WHERE post_id = ? AND status IN "
                              "('publishing','published','dry_run','needs_check')", [post_id])
        self.db.update("posts", post_id, {"status": "published" if live else "approved", "scheduled_at": None})
        self.db.log("post.unscheduled", "post", post_id, {"cancelled": cur.rowcount}, actor=actor)
        return cur.rowcount or 0

    def schedule_approved(self, brand: str | None = None, limit: int | None = None) -> dict:
        """Put every approved, rendered post into the next free slots (oldest approval first).
        Posts that can't be scheduled are reported, not raised."""
        sql, params = "SELECT id FROM posts WHERE status = 'approved'", []
        if brand:
            sql += " AND brand = ?"
            params.append(brand)
        out: dict = {"scheduled": {}, "skipped": {}}
        # planned posts first, in plan order; on one day Shorts, then long videos, then carousels take the slots
        order = (" ORDER BY json_extract(meta, '$.plan_date') IS NULL, json_extract(meta, '$.plan_date'), "
                 "CASE format WHEN 'short' THEN 0 WHEN 'mid' THEN 1 WHEN 'long' THEN 2 ELSE 3 END, updated_at, id")
        for row in self.db.query(sql + order, params)[: limit or None]:
            try:
                pubs = self.schedule(row["id"])
                out["scheduled"][row["id"]] = [self.db.get("publications", p)["scheduled_at"] for p in pubs]
            except (PermissionError, ValueError, RuntimeError) as e:
                out["skipped"][row["id"]] = str(e)
        return out

    # ------------------------------------------------------------------ publish
    def build_request(self, post: dict, platform: str):
        from .publish import PublishRequest
        brand = self.brand(post["brand"])
        assets = post.get("assets") or {}
        out = self.settings.output_dir
        tags = post.get("hashtags") or []
        from .publish._text import PLATFORM_HASHTAG_MAX, pick_hashtags
        if platform in PLATFORM_HASHTAG_MAX:  # choose which tags go, rather than letting the publisher cut the last ones
            tags = pick_hashtags(tags, PLATFORM_HASHTAG_MAX[platform], brand.slug.replace("-", ""))
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
        body = script.get("description", "")
        if post["format"] == "long" and assets.get("chapters"):
            from .media.chapters import with_chapters
            body = with_chapters(body, assets["chapters"])
        description = "\n\n".join(x for x in [body, disclosure] if x)
        return PublishRequest(
            platform=platform, brand=brand, settings=self.settings, format=post["format"],
            title=post.get("title", ""), caption=caption, description=description, tags=tags,
            video_path=video, image_paths=images, thumbnail_path=thumb, public_urls=public,
            captions_path=out / assets["captions_srt"] if assets.get("captions_srt") else None,
            ai_generated=True, realistic_synthetic=brand.realistic_synthetic_media,
            has_paid_promotion=bool((post.get("meta") or {}).get("sponsored")),
        )

    def publish_due(self, now: datetime | None = None, max_attempts: int = 3) -> list[dict]:
        from .publish import PublishError, get_publisher
        now = now or datetime.now(timezone.utc)
        self.flag_interrupted(now)
        due = self.db.query(
            "SELECT * FROM publications WHERE status = 'queued' AND scheduled_at <= ? AND attempts < ? ORDER BY scheduled_at",
            [now.isoformat(), max_attempts])
        results = []
        if due and not self.settings.dry_run:
            from .publish.tokens import refresh_long_lived, refresh_tiktok_if_needed
            brands_due: dict[str, set] = {}
            for p in due:
                b = self.db.scalar("SELECT brand FROM posts WHERE id = ?", [p["post_id"]]) or ""
                brands_due.setdefault(b, set()).add(p["platform"])
            for b, platforms in brands_due.items():
                scoped = self.settings.for_brand(b)
                try:
                    from .manual import is_manual
                    if "tiktok" in platforms and not is_manual("tiktok"):
                        refresh_tiktok_if_needed(scoped)
                    refresh_long_lived(scoped)
                except Exception as e:  # a failed refresh surfaces as a publish error below
                    self.db.log("tokens.refresh_failed", "", None, {"error": str(e), "brand": b})
        for pub in due:
            post = self.db.get("posts", pub["post_id"])
            if not post or post["status"] not in ("scheduled", "published"):
                self.db.update("publications", pub["id"], {
                    "status": "failed", "error": f"post status {post['status'] if post else 'missing'}"})
                continue
            late_hours = float(os.environ.get("PUBLISH_LATE_HOURS", "6") or 0)
            if late_hours and pub["scheduled_at"] < (now - timedelta(hours=late_hours)).isoformat():
                # The worker was down: don't dump a backlog all at once (that reads as spam). Move it on.
                from .scheduler import next_slot
                slot = next_slot(self.db, self.brand(post["brand"]), pub["platform"], after=now)
                self.db.update("publications", pub["id"], {"scheduled_at": slot.isoformat()})
                self.db.log("publication.rescheduled_late", "publication", pub["id"],
                            {"was": pub["scheduled_at"], "now": slot.isoformat()})
                results.append({"publication": pub["id"], "status": "rescheduled", "at": slot.isoformat()})
                continue
            if self.db.one("SELECT id FROM publications WHERE post_id = ? AND platform = ? AND id != ? "
                           "AND status = 'published'", [pub["post_id"], pub["platform"], pub["id"]]):
                self.db.update("publications", pub["id"], {"status": "cancelled",
                                                           "error": "already published on this platform"})
                continue
            from .manual import hand_off, is_manual
            if is_manual(pub["platform"]):  # never uploaded by the factory: package it for you to post by hand
                rel = hand_off(self, pub, post)
                results.append({"publication": pub["id"], "status": "manual", "package": rel["dir"]})
                continue
            from .guardrails import check_no_repost
            rp = check_no_repost(self.db, post, pub["platform"], exclude_pub_id=pub["id"],
                                 output_dir=self.settings.output_dir)
            if rp.level == "block":
                self.db.update("publications", pub["id"], {"status": "cancelled", "error": rp.message[:1000]})
                self.db.log("publication.cancelled_repost", "publication", pub["id"], {"error": rp.message})
                results.append({"publication": pub["id"], "status": "cancelled", "error": rp.message})
                continue
            from .publish.preflight import blocking, check
            stop = blocking(check(post, pub["platform"], self.settings.output_dir,
                                  self.settings.public_media_base_url), self.settings.dry_run)
            if stop:  # media changed or vanished since scheduling: fail clearly instead of half-uploading
                err = "Media check failed: " + "; ".join(map(str, stop))
                self.db.update("publications", pub["id"], {"status": "failed", "error": err[:1000],
                                                           "updated_at": now_iso()})
                self.db.log("publication.failed", "publication", pub["id"], {"error": err[:1000], "retry": False})
                results.append({"publication": pub["id"], "status": "failed", "error": err, "retry": False})
                continue
            # Claim it atomically so a second process (dashboard "publish now") can't post it twice.
            cur = self.db.execute("UPDATE publications SET status = 'publishing', attempts = attempts + 1, "
                                  "updated_at = ? WHERE id = ? AND status = 'queued'", [now_iso(), pub["id"]])
            if not cur.rowcount:
                continue
            attempts = pub["attempts"] + 1
            try:
                publisher = get_publisher(pub["platform"], self.settings.for_brand(post["brand"]))
                res = publisher.publish(self.build_request(post, pub["platform"]))
            except Exception as e:  # PublishError, network errors, bad files: never leave it 'publishing'
                retryable = getattr(e, "retryable", isinstance(e, (OSError, TimeoutError))
                                    or type(e).__module__.startswith("httpx"))
                retry = bool(retryable) and attempts < max_attempts
                err = str(e) if isinstance(e, PublishError) else f"{type(e).__name__}: {e}"
                upd = {"status": "queued" if retry else "failed", "error": err[:1000]}
                if retry:  # back off 5, 10, 15... minutes
                    upd["scheduled_at"] = (now + timedelta(minutes=5 * attempts)).isoformat()
                self.db.update("publications", pub["id"], upd)
                self.db.log("publication.failed", "publication", pub["id"], {"error": err[:1000], "retry": retry})
                results.append({"publication": pub["id"], "status": "failed", "error": err, "retry": retry})
                continue
            status = "dry_run" if res.raw.get("dry_run") else "published"
            self.db.update("publications", pub["id"], {
                "status": status, "remote_id": res.remote_id, "url": res.url,
                "published_at": now_iso(), "meta": res.raw, "error": ""})
            self.db.update("posts", post["id"], {"status": "published"})
            self.db.log(f"publication.{status}", "publication", pub["id"], {"platform": pub["platform"], "url": res.url})
            results.append({"publication": pub["id"], "status": status, "url": res.url})
        return results

    def flag_interrupted(self, now: datetime | None = None, minutes: int = 30) -> int:
        """A publication stuck in 'publishing' means the process died mid-upload. It may or may not be
        live, so it is never retried automatically: it's marked needs_check for a human to look at."""
        now = now or datetime.now(timezone.utc)
        cutoff = (now - timedelta(minutes=minutes)).replace(microsecond=0).isoformat()
        cur = self.db.execute(
            "UPDATE publications SET status = 'needs_check', error = 'Interrupted mid-publish. Check the platform: "
            "if it is live, mark it published; if not, requeue it.' WHERE status = 'publishing' "
            "AND COALESCE(updated_at, created_at) < ?", [cutoff])
        return cur.rowcount or 0

    def resolve_publication(self, pub_id: int, action: str, url: str = "", actor: str = "human") -> None:
        """Human decision on an interrupted (needs_check) or failed publication:
        'live' = it did go out (record it), 'requeue' = try again at the next free slot, 'drop' = give up."""
        pub = self.db.get("publications", pub_id)
        if not pub:
            raise KeyError(f"No publication #{pub_id}")
        if pub["status"] not in ("needs_check", "failed"):
            raise ValueError(f"Publication #{pub_id} is {pub['status']}; only needs_check or failed can be resolved")
        if action == "live":
            self.db.update("publications", pub_id, {"status": "published", "url": url or pub["url"],
                                                    "published_at": pub["published_at"] or now_iso(), "error": ""})
            self.db.update("posts", pub["post_id"], {"status": "published"})
        elif action == "requeue":
            from .scheduler import next_slot
            post = self._post(pub["post_id"])
            slot = next_slot(self.db, self.brand(post["brand"]), pub["platform"])
            self.db.update("publications", pub_id, {"status": "queued", "attempts": 0, "error": "",
                                                    "scheduled_at": slot.isoformat()})
            if post["status"] != "published":
                self.db.update("posts", post["id"], {"status": "scheduled"})
        elif action == "drop":
            self.db.update("publications", pub_id, {"status": "cancelled"})
        else:
            raise ValueError("action must be live, requeue or drop")
        self.db.log(f"publication.resolved_{action}", "publication", pub_id, {"url": url}, actor=actor)

    # ------------------------------------------------------------------ analytics
    def collect_metrics(self) -> int:
        from .publish import get_publisher
        pubs = self.db.query("SELECT p.*, s.brand FROM publications p JOIN posts s ON s.id = p.post_id "
                             "WHERE p.status = 'published' AND p.remote_id != ''")
        n = 0
        for pub in pubs:
            try:
                snap = get_publisher(pub["platform"], self.settings.for_brand(pub["brand"]),
                                     dry_run=False).fetch_metrics(pub["remote_id"])
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
