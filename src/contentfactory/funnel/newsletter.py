"""Outbound email: double opt-in confirmations and the weekly digest.

* `send_confirmation` goes out right after a signup (SMTP if configured,
  otherwise an .eml file in output/<slug>/newsletter/outbox/).
* `draft_digest` writes a weekly email from that week's published posts plus
  one product or affiliate mention (with disclosure) and stores it as a draft.
* `send_digest` goes only to confirmed subscribers. Default is a dry run that
  writes one .eml per recipient; real sending needs `confirm=True`, SMTP
  settings and BUSINESS_ADDRESS (CAN-SPAM postal address).
* `export_subscribers_csv` produces an import file for Beehiiv / ConvertKit
  (Kit) / Mailchimp if you'd rather send from one of those.
"""
from __future__ import annotations

import csv
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from ..config import BrandProfile
from ..db import DB, now_iso
from . import mailer, store
from .linkpage import AFFILIATE_NOTE, products, public_env, slugify, sync_affiliate_links, theme

ADDRESS_PLACEHOLDER = "%%BUSINESS_ADDRESS%%"
MISSING_ADDRESS = "[set BUSINESS_ADDRESS before sending]"


class DigestItemCopy(BaseModel):
    title: str = Field(description="The post title, lightly edited for email (under 80 chars)")
    blurb: str = Field(description="1-2 sentences on what the reader learns; no hype")


class DigestCopy(BaseModel):
    subject: str = Field(description="Email subject under 60 characters, specific, no clickbait")
    preheader: str = Field(description="Preview text under 100 characters")
    intro: str = Field(description="2-3 sentence friendly opener in the brand voice")
    items: list[DigestItemCopy] = Field(description="One entry per post, same order as given")
    spotlight: str = Field(description="1-2 sentences introducing the product/tool mention; honest, no fake "
                                       "personal testimonial, empty string if there is no mention")
    signoff: str = Field(description="One-line sign-off")


# ---------------------------------------------------------------- helpers
def _brand(factory, brand) -> BrandProfile:
    return brand if isinstance(brand, BrandProfile) else factory.brand(brand)


def _newsletter_dir(factory, brand: BrandProfile) -> Path:
    d = factory.settings.output_dir / brand.slug / "newsletter"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _email_theme(brand: BrandProfile) -> dict:
    from ..brandkit.draw import contrast, hex_to_rgb
    t = theme(brand)
    white = (255, 255, 255)
    t["link"] = t["accent"] if contrast(hex_to_rgb(t["accent"]), white) >= 4.5 else t["dark"]
    return t


def _first_sentences(text: str, n: int = 2, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", re.sub(r"#\w+", "", text or "")).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(parts[:n]).strip()
    return out if len(out) <= limit else out[: limit - 1].rsplit(" ", 1)[0] + "…"


PLATFORM_ORDER = {"youtube": 0, "instagram": 1, "tiktok": 2, "threads": 3, "facebook": 4}


def week_posts(db: DB, brand: str, since: str, until: str, limit: int = 8) -> list[dict]:
    """Posts with at least one published URL in [since, until), one row per post."""
    rows = db.query(
        "SELECT p.id, p.title, p.caption, pub.platform, pub.url, pub.published_at FROM publications pub "
        "JOIN posts p ON p.id = pub.post_id WHERE p.brand = ? AND pub.status = 'published' "
        "AND COALESCE(pub.published_at, pub.created_at) >= ? AND COALESCE(pub.published_at, pub.created_at) <= ? "
        "ORDER BY COALESCE(pub.published_at, pub.created_at)", [brand, since, until])
    posts: dict[int, dict] = {}
    for r in rows:
        cur = posts.get(r["id"])
        better = cur is None or (r["url"] and PLATFORM_ORDER.get(r["platform"], 9) < PLATFORM_ORDER.get(cur["platform"], 9))
        if better or (cur and not cur["url"]):
            posts[r["id"]] = {"id": r["id"], "title": r["title"], "caption": r["caption"] or "",
                              "platform": r["platform"], "url": r["url"] or ""}
    return list(posts.values())[:limit]


def pick_mention(db: DB, brand: BrandProfile, base_url: str, when: datetime, settings=None) -> dict | None:
    """Rotate weekly through the brand's products and affiliate offers.
    Links carry utm_source=newsletter, utm_medium=email, utm_campaign=digest-<yyyy-mm-dd>."""
    from .attribution import with_utm
    campaign = f"digest-{when.date().isoformat()}"
    utm = {"source": "newsletter", "medium": "email", "campaign": campaign}
    options: list[dict] = []
    for p in products(db, brand, settings=settings, base_url=base_url, utm=utm):
        options.append({"kind": "product", "name": p["name"], "url": p["page_url"], "cta": f"Get {p['name']}"[:60],
                        "disclosure": "This is my own product; buying it supports the newsletter."})
    for a in sync_affiliate_links(db, brand):
        options.append({"kind": "affiliate", "name": a["name"],
                        "url": with_utm(f"{base_url}/go/{a['slug']}?s=email", **utm),
                        "cta": f"Check out {a['name']}"[:60], "disclosure": AFFILIATE_NOTE})
    if not options:
        return None
    return options[when.isocalendar()[1] % len(options)]


def offline_copy(brand: BrandProfile, posts: list[dict], mention: dict | None) -> DigestCopy:
    n = len(posts)
    subject = (f"{brand.name}: {n} new {'post' if n == 1 else 'posts'} this week" if n
               else f"{brand.name}: this week's note")
    first = posts[0]["title"] if posts else (brand.promise or brand.niche)
    intro = (f"Here's what went up this week, in one place. Start with “{first}” if you only have a minute."
             if posts else f"A quiet week on the channel, so here's one thing worth your time: {brand.promise or brand.niche}.")
    items = [DigestItemCopy(title=p["title"], blurb=_first_sentences(p["caption"]) or "Short and practical.")
             for p in posts]
    spotlight = ""
    if mention:
        spotlight = (f"If you want to go further, {mention['name']} is my own resource built for exactly this."
                     if mention["kind"] == "product"
                     else f"A tool some readers ask about: {mention['name']}. Compare it with alternatives before signing up.")
    return DigestCopy(subject=subject[:78], preheader=_first_sentences(intro, 1, 98), intro=intro, items=items,
                      spotlight=spotlight, signoff=brand.cta or "See you next week.")


def _prompt(brand: BrandProfile, posts: list[dict], mention: dict | None) -> str:
    lines = [f"Brand: {brand.name} ({brand.niche}). Audience: {brand.audience}. Tone: {brand.voice.tone}. "
             f"Persona: {brand.voice.persona}. Banned phrases: {', '.join(brand.voice.banned_phrases) or 'none'}.",
             "Write this week's newsletter digest. Posts (keep this order, one item each):"]
    for i, p in enumerate(posts, 1):
        lines.append(f"{i}. {p['title']}: {_first_sentences(p['caption'], 3, 400)}")
    if not posts:
        lines.append("(no posts this week: write a short note with one useful idea from the brand promise)")
    if mention:
        lines.append(f"Mention ({mention['kind']}): {mention['name']}. Write the spotlight honestly; the AI writer "
                     "must not claim to have personally used it. A disclosure line is added automatically.")
    return "\n".join(lines)


SYSTEM = ("You write a short weekly email for a small creator brand. Plain language, specific, warm, no hype, "
          "no income or results promises, no fake first-person testimonials. Return JSON matching the schema.")


# ---------------------------------------------------------------- draft
def upcoming_posts(db: DB, brand: str, since: str, until: str, limit: int = 8) -> list[dict]:
    """Before launch: posts scheduled (or approved) for [since, until), one row each, no URLs yet."""
    rows = db.query(
        "SELECT DISTINCT p.id, p.title, p.caption FROM posts p LEFT JOIN publications pub ON pub.post_id = p.id "
        "WHERE p.brand = ? AND p.format != 'image' AND (p.status = 'approved' OR (pub.status IN ('queued', 'published', "
        "'dry_run', 'manual') AND pub.scheduled_at >= ? AND pub.scheduled_at < ?)) ORDER BY p.id LIMIT ?",
        [brand, since, until, limit])
    return [{"id": r["id"], "title": r["title"], "caption": r["caption"] or "", "platform": "youtube", "url": ""}
            for r in rows]


def draft_digest(factory, brand, days: int = 7, *, base_url: str | None = None, upcoming: bool = False) -> int:
    """Build and store a digest draft for the last `days` days. Returns the draft id."""
    b = _brand(factory, brand)
    db: DB = factory.db
    store.ensure_schema(db)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    since = (now - timedelta(days=days)).isoformat()
    base = mailer.public_url(factory.settings, base_url or "")
    posts = upcoming_posts(db, b.slug, now.isoformat(), (now + timedelta(days=days)).isoformat()) if upcoming \
        else week_posts(db, b.slug, since, now.isoformat())
    mention = pick_mention(db, b, base, now, factory.settings)
    copy = factory.llm.structured(DigestCopy, system=SYSTEM, prompt=_prompt(b, posts, mention),
                                  offline=lambda: offline_copy(b, posts, mention), purpose="funnel.digest",
                                  max_tokens=4000)
    fallback = offline_copy(b, posts, mention)
    if len(copy.items) != len(posts):
        copy.items = fallback.items
    if mention and not copy.spotlight.strip():
        copy.spotlight = fallback.spotlight
    items = [{"title": c.title or p["title"], "blurb": c.blurb, "url": p["url"],
              "platform": p["platform"].title() if p["platform"] != "youtube" else "YouTube"}
             for c, p in zip(copy.items, posts)]
    ctx = {"brand": b, "t": _email_theme(b), "copy": copy, "items": items, "mention": mention,
           "subject": copy.subject, "preheader": copy.preheader}
    html_body = public_env().get_template("email_digest.html").render(**ctx)
    text_body = render_text(b, copy, items, mention)
    draft_id = db.insert("newsletter_drafts", {
        "brand": b.slug, "subject": copy.subject, "preheader": copy.preheader, "html": html_body, "text": text_body,
        "status": "draft", "period_start": since, "period_end": now.isoformat(),
        "meta": {"posts": [p["id"] for p in posts], "mention": mention, "llm": factory.llm.provider},
    })
    out = _newsletter_dir(factory, b) / f"draft-{draft_id}.html"
    out.write_text(fill(html_body, "#unsubscribe", mailer.business_address() or MISSING_ADDRESS, html=True))
    db.log("funnel.digest_drafted", "newsletter_draft", draft_id, {"brand": b.slug, "posts": len(posts)})
    return draft_id


def render_text(brand: BrandProfile, copy: DigestCopy, items: list[dict], mention: dict | None) -> str:
    out = [brand.name, "=" * len(brand.name), "", copy.intro, ""]
    for it in items:
        out += [f"* {it['title']}", f"  {it['blurb']}"] + ([f"  {it['url']}"] if it["url"] else []) + [""]
    if mention:
        label = "SPONSORED / AFFILIATE" if mention["kind"] == "affiliate" else "FROM ME"
        out += [f"[{label}] {copy.spotlight}", mention["url"], mention["disclosure"], ""]
    out += [copy.signoff, "", "--", brand.ai_disclosure,
            f"You subscribed to {brand.name} and confirmed your email. Unsubscribe: {mailer.UNSUB_PLACEHOLDER}",
            f"{brand.name} · {ADDRESS_PLACEHOLDER}"]
    return "\n".join(out) + "\n"


def fill(body: str, unsubscribe_url: str, address: str, html: bool = False) -> str:
    import html as html_mod
    esc = (lambda s: html_mod.escape(s, quote=True)) if html else (lambda s: s)  # noqa: E731
    return body.replace(mailer.UNSUB_PLACEHOLDER, esc(unsubscribe_url)).replace(ADDRESS_PLACEHOLDER, esc(address))


def get_draft(db: DB, draft_id: int) -> dict:
    store.ensure_schema(db)
    d = db.get("newsletter_drafts", draft_id)
    if not d:
        raise KeyError(f"No newsletter draft #{draft_id}")
    return d


def list_drafts(db: DB, brand: str | None = None, limit: int = 20) -> list[dict]:
    store.ensure_schema(db)
    if brand:
        return db.query("SELECT * FROM newsletter_drafts WHERE brand = ? ORDER BY id DESC LIMIT ?", [brand, limit])
    return db.query("SELECT * FROM newsletter_drafts ORDER BY id DESC LIMIT ?", [limit])


# ---------------------------------------------------------------- send
def send_digest(factory, draft_id: int, *, confirm: bool = False, base_url: str | None = None) -> dict:
    """Send a draft to confirmed subscribers.

    confirm=False (default): dry run, one .eml per recipient under
    output/<slug>/newsletter/draft-<id>/dry-run/. confirm=True: real SMTP send
    (needs SMTP_* and BUSINESS_ADDRESS). Recipients already sent this draft
    are skipped, so a partial failure can be retried safely."""
    db: DB = factory.db
    draft = get_draft(db, draft_id)
    b = factory.brand(draft["brand"])
    base = mailer.public_url(factory.settings, base_url or "")
    address = mailer.business_address()
    cfg = None
    if confirm:
        if not address:
            raise ValueError("BUSINESS_ADDRESS is required before sending (CAN-SPAM needs a valid postal address)")
        cfg = mailer.require_smtp()
    recipients = store.list_subscribers(db, b.slug, "confirmed", limit=1_000_000)
    already = {r["subscriber_id"] for r in db.query(
        "SELECT subscriber_id FROM emails_sent WHERE draft_id = ? AND status = 'sent'", [draft_id])}
    todo = [r for r in recipients if r["id"] not in already]
    messages = []
    for sub in todo:
        unsub = f"{base}/unsubscribe/{sub['token']}"
        messages.append((sub, mailer.build_message(
            brand=b, to=sub["email"], subject=draft["subject"],
            text=fill(draft["text"], unsub, address or MISSING_ADDRESS),
            html_body=fill(draft["html"], unsub, address or MISSING_ADDRESS, html=True),
            unsubscribe_url=unsub, cfg=cfg)))
    result = {"draft_id": draft_id, "mode": "send" if confirm else "dry_run", "recipients": len(recipients),
              "skipped_already_sent": len(recipients) - len(todo), "sent": 0, "failed": 0, "files": []}
    if not confirm:
        folder = _newsletter_dir(factory, b) / f"draft-{draft_id}" / "dry-run"
        for sub, msg in messages:
            p = mailer.write_eml(msg, folder / f"{sub['id']:06d}-{mailer.safe_filename(sub['email'])}.eml")
            store.log_email(db, brand=b.slug, email=sub["email"], kind="digest", status="dry_run",
                            subscriber_id=sub["id"], draft_id=draft_id, path=str(p))
            result["files"].append(str(p))
        db.log("funnel.digest_dry_run", "newsletter_draft", draft_id, {"recipients": len(messages)})
        return result
    for start in range(0, len(messages), 50):
        batch = messages[start:start + 50]
        errors = mailer.smtp_send(cfg, [m for _, m in batch])
        for (sub, _), err in zip(batch, errors):
            store.log_email(db, brand=b.slug, email=sub["email"], kind="digest", status="failed" if err else "sent",
                            subscriber_id=sub["id"], draft_id=draft_id, error=err or "")
            result["failed" if err else "sent"] += 1
    db.execute("UPDATE newsletter_drafts SET status = 'sent', sent_at = ? WHERE id = ?", [now_iso(), draft_id])
    db.log("funnel.digest_sent", "newsletter_draft", draft_id, {k: result[k] for k in ("sent", "failed")},
           actor="human")
    return result


def send_confirmation(factory, brand: BrandProfile, subscriber: dict, *, base_url: str | None = None) -> dict:
    """Email the double opt-in link. Uses SMTP when SMTP_HOST is set (this is a
    transactional email the visitor just asked for), otherwise writes .eml."""
    db: DB = factory.db
    base = mailer.public_url(factory.settings, base_url or "")
    confirm_url = f"{base}/confirm/{subscriber['token']}"
    unsub = f"{base}/unsubscribe/{subscriber['token']}"
    from .linkpage import lead_magnet
    magnet = lead_magnet(brand, factory.settings)
    address = mailer.business_address() or MISSING_ADDRESS
    text = (f"Hi!\n\nPlease confirm you want emails from {brand.name}:\n\n{confirm_url}\n\n"
            f"Once confirmed you'll get {magnet['title']} right away.{magnet.get('after', '')}\n"
            f"If you didn't sign up, ignore this email and you won't hear from us again.\n\n"
            f"--\n{brand.name} · {address}\nUnsubscribe: {unsub}\n")
    t = _email_theme(brand)
    html_body = public_env().from_string(
        """<div style="font-family:Inter,Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;color:#18181b">
<h2 style="margin:0 0 12px">Confirm your email</h2>
<p>Tap the button to confirm you want emails from <b>{{ name }}</b>. You'll get <b>{{ magnet }}</b> straight away.</p>
<p><a href="{{ url }}" style="display:inline-block;background:{{ t.accent }};color:{{ t.accent_ink }};padding:12px 20px;
border-radius:8px;font-weight:700;text-decoration:none">Yes, subscribe me</a></p>
<p style="font-size:13px;color:#71717a">If you didn't sign up, ignore this email.</p>
<p style="font-size:12px;color:#71717a">{{ name }} · {{ address }} · <a href="{{ unsub }}" style="color:#71717a">Unsubscribe</a></p></div>"""
    ).render(name=brand.name, magnet=magnet["title"], url=confirm_url, t=t, address=address, unsub=unsub)
    cfg = mailer.SMTPConfig.from_env()
    msg = mailer.build_message(brand=brand, to=subscriber["email"], subject=f"Confirm your subscription to {brand.name}",
                               text=text, html_body=html_body, unsubscribe_url=unsub, cfg=cfg)
    if cfg and not cfg.missing():
        err = mailer.smtp_send(cfg, [msg])[0]
        store.log_email(db, brand=brand.slug, email=subscriber["email"], kind="confirm",
                        status="failed" if err else "sent", subscriber_id=subscriber["id"], error=err or "")
        return {"status": "failed" if err else "sent", "error": err}
    path = mailer.write_eml(msg, _newsletter_dir(factory, brand) / "outbox" /
                            f"confirm-{subscriber['id']:06d}-{mailer.safe_filename(subscriber['email'])}.eml")
    store.log_email(db, brand=brand.slug, email=subscriber["email"], kind="confirm", status="dry_run",
                    subscriber_id=subscriber["id"], path=str(path))
    return {"status": "dry_run", "path": str(path)}


# ---------------------------------------------------------------- export
def export_subscribers_csv(factory, brand, path: Path | None = None) -> Path:
    """Confirmed subscribers as CSV (email first; works with Beehiiv, Kit and
    Mailchimp importers). Pending and unsubscribed people are never exported."""
    b = _brand(factory, brand)
    rows = store.list_subscribers(factory.db, b.slug, "confirmed", limit=1_000_000)
    path = path or _newsletter_dir(factory, b) / f"subscribers-{b.slug}-{now_iso()[:10]}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["email", "status", "source", "subscribed_at", "confirmed_at", "tags"])
        for r in rows:
            w.writerow([r["email"], "subscribed", r["source"], r["created_at"], r["confirmed_at"] or "",
                        slugify(b.slug)])
    return path
