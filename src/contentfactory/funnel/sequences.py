"""Email welcome sequence engine.

Steps live in brands/sequences/<brand>.yaml (see brandfunnel.py):

    name: welcome
    min_gap_hours: 20        # never two sequence emails to one person within this
    max_late_days: 3         # a step this overdue is skipped, not sent late
    steps:
      - day_offset: 0
        subject: "..."
        body_markdown: |
          ...
        cta_url_key: freebie        # freebie | link_page | product:<slug> | checkout:<slug>
        cta_label: Open the checklist   #   | affiliate:<slug> | a key in `links:` | https://...

`run_sequences(factory)` sends each confirmed subscriber the earliest step that
is due (confirmed_at + day_offset days), at most one email per subscriber per
run, never the same step twice (tracked in emails_sent, kind
`sequence:<name>:<day>`). Pending and unsubscribed people get nothing.

Default is a dry run: .eml files under output/<slug>/newsletter/sequences/
<name>/dry-run/. Real sending needs confirm=True AND FACTORY_DRY_RUN=0 AND
SMTP_* AND BUSINESS_ADDRESS. Dry runs never count as sent, so switching to
live later still delivers the steps that are due (older ones are skipped by
max_late_days rather than sent in a burst).

Body placeholders: {brand}, {signoff}, {link:<key>}, {freebie_url},
{affiliate_name:<slug>}, any key under `vars:` (e.g. {price}), and the launch
values {launch_price} {launch_code} {launch_ends_human}. Conditional blocks
`{if launch}...{/if}` and `{if no_launch}...{/if}` follow brandfunnel.launch_state,
so a launch price is only mentioned while it is true.
"""
from __future__ import annotations

import html as html_mod
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from ..config import BrandProfile
from ..db import DB
from ..publish.base import MissingCredentials
from . import attribution, mailer, store
from .brandfunnel import funnel_path, launch_state, load_funnel

KIND_PREFIX = "sequence"
DONE_LIVE = {"sent", "skipped"}
DONE_DRY = DONE_LIVE | {"dry_run", "dry_skipped"}
MAX_FAILURES = 3
MISSING_ADDRESS = "[set BUSINESS_ADDRESS before sending]"
DEFAULT_FOOTER = "Educational content, not financial advice. Written with help from AI tools and reviewed by a human."


class SequenceStep(BaseModel):
    day_offset: int = Field(ge=0, le=365)
    subject: str
    body_markdown: str
    cta_url_key: str = ""
    cta_label: str = ""
    preheader: str = ""
    max_late_days: float | None = None

    @field_validator("subject")
    @classmethod
    def _subject(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("subject is empty")
        return v.strip()


class Sequence(BaseModel):
    brand: str
    name: str = "welcome"
    min_gap_hours: float = 20
    max_late_days: float = 3
    footer_note: str = DEFAULT_FOOTER
    signoff: str = ""
    links: dict[str, str] = Field(default_factory=dict)
    vars: dict = Field(default_factory=dict)
    steps: list[SequenceStep] = Field(default_factory=list)

    def kind(self, step: SequenceStep) -> str:
        return f"{KIND_PREFIX}:{self.name}:{step.day_offset}"


# ---------------------------------------------------------------- loading
def course_path(settings, brand_slug: str, name: str) -> Path:
    """A brand's extra sequence (an email course): brands/sequences/<brand>.<name>.yaml."""
    return Path(settings.brands_dir) / "sequences" / f"{brand_slug}.{name}.yaml"


def load_sequence(settings, brand_slug: str, name: str = "") -> Sequence | None:
    """The brand's sequence, or None if it has no funnel file / no steps. With `name`, the extra sequence in
    brands/sequences/<brand>.<name>.yaml instead (same keys as the welcome part of the funnel file); those
    are exported for an email provider (`factory sequence-export --sequence <name>`), not sent by the worker."""
    if name:
        import yaml
        path = course_path(settings, brand_slug, name)
        cfg = (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}
        cfg.setdefault("name", name)
    else:
        cfg = load_funnel(settings, brand_slug)
    if not cfg.get("steps"):
        return None
    data = {k: cfg[k] for k in ("name", "min_gap_hours", "max_late_days", "footer_note", "signoff", "links",
                                "vars", "steps") if k in cfg and cfg[k] is not None}
    seq = Sequence.model_validate({"brand": brand_slug, **data})
    seq.steps = sorted(seq.steps, key=lambda s: s.day_offset)
    return seq


def _launch(settings, brand: BrandProfile, seq: Sequence, now: datetime) -> dict:
    cfg = load_funnel(settings, brand.slug)
    want = str(seq.vars.get("product", ""))
    entry = next((p for p in cfg.get("products") or [] if isinstance(p, dict) and (not want or p.get("slug") == want)),
                 {})
    keys = ("price", "launch_price", "launch_code", "launch_ends")
    info = {k: entry.get(k) for k in keys}
    info.update({k: seq.vars[k] for k in keys if seq.vars.get(k) not in (None, "")})
    return launch_state(info, now)


# ---------------------------------------------------------------- links
def resolve_link(key: str, *, settings, brand: BrandProfile, seq: Sequence, subscriber: dict, base: str,
                 utm: dict, launch: dict) -> str:
    """URL for a cta_url_key / {link:key}. Raises KeyError for unknown keys."""
    ref = seq.links.get(key, key).strip()
    if ref.startswith(("http://", "https://")):
        return attribution.tag_link(ref, **utm)
    kind, _, arg = ref.partition(":")
    if kind == "freebie":
        from .linkpage import lead_magnet
        url = lead_magnet(brand, settings).get("url") or f"{base}/freebie/{subscriber['token']}"
        return url
    if kind == "link_page":
        return attribution.with_utm(f"{base}/l/{brand.slug}", **utm)
    if kind == "product" and arg:
        return attribution.with_utm(f"{base}/p/{brand.slug}/{arg}", **utm)
    if kind == "checkout" and arg:
        from .salespage import buy_url, product_slug
        for p in brand.products:
            if product_slug(settings, brand, p) == arg and p.get("url"):
                return buy_url(p["url"], launch, {f"utm_{k}": v for k, v in utm.items()})
        raise KeyError(f"no product with slug '{arg}' in brand {brand.slug}")
    if kind == "affiliate" and arg:
        if not any((a.slug or "") == arg or a.name.lower() == arg for a in brand.affiliates):
            raise KeyError(f"no affiliate '{arg}' in brand {brand.slug}")
        return attribution.with_utm(f"{base}/go/{arg}?s=email", **utm)
    raise KeyError(f"unknown link key '{key}' (use freebie, link_page, product:<slug>, checkout:<slug>, "
                   "affiliate:<slug>, a key under links:, or a full URL)")


# ---------------------------------------------------------------- rendering
_IF_RE = re.compile(r"\{if (launch|no_launch)\}(.*?)\{/if\}", re.S)
_VAR_RE = re.compile(r"\{([a-z_]+)(?::([A-Za-z0-9_-]+))?\}")


def _conditionals(text: str, launch_active: bool) -> str:
    return _IF_RE.sub(lambda m: m.group(2) if (m.group(1) == "launch") == launch_active else "", text)


def fill_placeholders(text: str, *, values: dict, link) -> str:
    def sub(m: re.Match) -> str:
        name, arg = m.group(1), m.group(2)
        if name == "link" and arg:
            return link(arg)
        if name == "freebie_url":
            return link("freebie")
        if name == "affiliate_name" and arg:
            return values.get(f"affiliate_name:{arg}", m.group(0))
        if arg is None and name in values:
            return str(values[name])
        return m.group(0)
    return _VAR_RE.sub(sub, text)


_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def _inline_html(text: str, link_color: str) -> str:
    out, pos = [], 0
    for m in _LINK_RE.finditer(text):
        out.append(_fmt(html_mod.escape(text[pos:m.start()], quote=False)))
        out.append(f'<a href="{html_mod.escape(m.group(2), quote=True)}" style="color:{link_color};font-weight:600">'
                   f'{_fmt(html_mod.escape(m.group(1), quote=False))}</a>')
        pos = m.end()
    out.append(_fmt(html_mod.escape(text[pos:], quote=False)))
    return "".join(out)


def _fmt(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def markdown_to_html(md: str, link_color: str = "#0b5d3b") -> str:
    """Small Markdown subset for emails: paragraphs, ##/### headings, - and 1.
    lists, > quotes, **bold**, *italic*, `code`, [text](url)."""
    blocks = re.split(r"\n\s*\n", md.strip())
    out = []
    p_style = "margin:0 0 16px"
    for block in blocks:
        lines = [ln.rstrip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        if lines[0].startswith(("## ", "### ")) and len(lines) == 1:
            level = 2 if lines[0].startswith("## ") else 3
            size = 20 if level == 2 else 17
            out.append(f'<h{level} style="margin:24px 0 10px;font-size:{size}px;line-height:1.3">'
                       f'{_inline_html(lines[0].split(" ", 1)[1], link_color)}</h{level}>')
        elif all(re.match(r"^[-*] ", ln) for ln in lines):
            items = "".join(f'<li style="margin:0 0 8px">{_inline_html(ln[2:], link_color)}</li>' for ln in lines)
            out.append(f'<ul style="margin:0 0 16px;padding-left:22px">{items}</ul>')
        elif all(re.match(r"^\d+\. ", ln) for ln in lines):
            items = "".join(f'<li style="margin:0 0 8px">{_inline_html(ln.split(". ", 1)[1], link_color)}</li>'
                            for ln in lines)
            out.append(f'<ol style="margin:0 0 16px;padding-left:22px">{items}</ol>')
        elif all(ln.startswith(">") for ln in lines):
            inner = " ".join(ln.lstrip("> ").strip() for ln in lines)
            out.append(f'<blockquote style="margin:0 0 16px;padding:10px 14px;border-left:4px solid {link_color};'
                       f'background:#f4f4f5">{_inline_html(inner, link_color)}</blockquote>')
        else:
            out.append(f'<p style="{p_style}">' + "<br>".join(_inline_html(ln, link_color) for ln in lines) + "</p>")
    return "\n".join(out)


def markdown_to_text(md: str) -> str:
    text = _LINK_RE.sub(lambda m: m.group(1) if m.group(1) == m.group(2) else f"{m.group(1)} ({m.group(2)})", md)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^#{2,3} (.+)$", lambda m: m.group(1).upper(), text, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def render_step(settings, brand: BrandProfile, seq: Sequence, step: SequenceStep, subscriber: dict, *,
                base: str, now: datetime) -> dict:
    """{subject, preheader, text, html, links} for one subscriber. Unsubscribe URL
    and business address are filled in; the footer is always included."""
    from .newsletter import _email_theme
    launch = _launch(settings, brand, seq, now)
    utm = {"source": f"{seq.name}-sequence", "medium": "email", "campaign": f"{seq.name}-d{step.day_offset}"}
    used: list[str] = []

    def link(key: str) -> str:
        url = resolve_link(key, settings=settings, brand=brand, seq=seq, subscriber=subscriber, base=base, utm=utm,
                           launch=launch)
        used.append(url)
        return url

    values = {"brand": brand.name, "signoff": seq.signoff or f"— {brand.name}",
              **{k: v for k, v in seq.vars.items() if not isinstance(v, (dict, list))},
              "price": launch["price"] or seq.vars.get("price", ""), "launch_price": launch["launch_price"],
              "launch_code": launch["code"], "launch_ends_human": launch["ends_human"],
              **{f"affiliate_name:{a.slug or a.name.lower()}": a.name for a in brand.affiliates}}

    def prep(text: str) -> str:
        return fill_placeholders(_conditionals(text, launch["active"]), values=values, link=link)

    subject = re.sub(r"\s+", " ", prep(step.subject)).strip()
    preheader = re.sub(r"\s+", " ", prep(step.preheader)).strip()
    body = prep(step.body_markdown)
    cta_url = link(step.cta_url_key) if step.cta_url_key else ""
    cta_label = prep(step.cta_label) if step.cta_label else "Open"
    unsub = f"{base}/unsubscribe/{subscriber['token']}"
    address = mailer.business_address() or MISSING_ADDRESS
    footer_note = prep(seq.footer_note)
    t = _email_theme(brand)
    text = markdown_to_text(body)
    if cta_url and cta_url not in text:
        text += f"\n\n{cta_label}: {cta_url}"
    text += (f"\n\n--\n{footer_note}\nYou're getting this because you signed up for {brand.name} and confirmed "
             f"your email. Unsubscribe: {unsub}\n{brand.name} · {address}\n")
    from .linkpage import public_env
    html_body = public_env().get_template("email_sequence.html").render(
        brand=brand, t=t, subject=subject, preheader=preheader, body_html=markdown_to_html(body, t["link"]),
        cta_url=cta_url, cta_label=cta_label, footer_note=footer_note, unsub=unsub, address=address)
    return {"subject": subject, "preheader": preheader, "text": text, "html": html_body, "links": used + (
        [cta_url] if cta_url else []), "unsubscribe_url": unsub, "launch": launch}


def validate_sequence(settings, brand: BrandProfile, seq: Sequence | None = None) -> list[str]:
    """Problems that would break sending ([] when fine): unknown link keys,
    leftover placeholders, duplicate day offsets. Renders every step in both
    launch states with a fake subscriber."""
    seq = seq or load_sequence(settings, brand.slug)
    if seq is None:
        return [f"no steps in {funnel_path(settings, brand.slug)}"]
    problems = []
    days = [s.day_offset for s in seq.steps]
    if len(days) != len(set(days)):
        problems.append("two steps share a day_offset (each step needs its own day)")
    fake = {"id": 0, "token": "preview-token", "email": "preview@example.com"}
    today = datetime.now(timezone.utc)
    nows = [today]
    ends = _launch(settings, brand, seq, today).get("ends")
    if ends:  # check the copy both while the launch runs and after it ends
        end_dt = datetime.fromisoformat(ends).replace(hour=12, tzinfo=timezone.utc)
        nows = [end_dt - timedelta(days=1), end_dt + timedelta(days=1)]
    for now in nows:
        for step in seq.steps:
            try:
                r = render_step(settings, brand, seq, step, fake, base="https://example.com", now=now)
            except KeyError as e:
                problems.append(f"day {step.day_offset}: {e.args[0]}")
                continue
            leftover = [m.group(0) for m in _VAR_RE.finditer(r["subject"] + r["text"])]
            leftover += re.findall(r"\{/?if[^}]*\}", r["subject"] + r["text"])
            if leftover:
                problems.append(f"day {step.day_offset}: unfilled placeholders {sorted(set(leftover))}")
    return sorted(set(problems))


# ---------------------------------------------------------------- engine
def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def live_blockers(factory, confirm: bool) -> list[str]:
    """Why a run would not send for real (empty list = it will)."""
    reasons = []
    if not confirm:
        reasons.append("confirm=False (dry run by default)")
    if factory.settings.dry_run:
        reasons.append("FACTORY_DRY_RUN is on (set FACTORY_DRY_RUN=0 to send)")
    try:
        mailer.require_smtp()
    except MissingCredentials as e:
        reasons.append(f"SMTP not configured ({e})")
    if not mailer.business_address():
        reasons.append("BUSINESS_ADDRESS is not set (CAN-SPAM needs a postal address)")
    return reasons


def _history(db: DB, brand: str, name: str) -> dict[int, dict]:
    """{subscriber_id: {"steps": {day: [statuses]}, "last_live": dt, "last_dry": dt}}"""
    out: dict[int, dict] = {}
    prefix = f"{KIND_PREFIX}:{name}:"
    for r in db.query("SELECT subscriber_id, kind, status, created_at FROM emails_sent WHERE brand = ? AND kind LIKE ?",
                      [brand, prefix + "%"]):
        h = out.setdefault(r["subscriber_id"], {"steps": {}, "last_live": None, "last_dry": None})
        try:
            day = int(r["kind"][len(prefix):])
        except ValueError:
            continue
        h["steps"].setdefault(day, []).append(r["status"])
        ts = _parse_ts(r["created_at"])
        if ts and r["status"] == "sent" and (h["last_live"] is None or ts > h["last_live"]):
            h["last_live"] = ts
        if ts and r["status"] in ("sent", "dry_run") and (h["last_dry"] is None or ts > h["last_dry"]):
            h["last_dry"] = ts
    return out


def plan_for_subscriber(seq: Sequence, sub: dict, hist: dict | None, now: datetime, live: bool):
    """(step to send or None, [steps to mark skipped]). Pure: no I/O."""
    confirmed = _parse_ts(sub.get("confirmed_at"))
    if sub.get("status") != "confirmed" or confirmed is None:
        return None, []
    hist = hist or {"steps": {}, "last_live": None, "last_dry": None}
    last = hist["last_live"] if live else hist["last_dry"]
    if last and now - last < timedelta(hours=seq.min_gap_hours):
        return None, []
    done = DONE_LIVE if live else DONE_DRY
    skipped = []
    for step in seq.steps:
        statuses = hist["steps"].get(step.day_offset, [])
        if any(s in done for s in statuses) or statuses.count("failed") >= MAX_FAILURES:
            continue
        due = confirmed + timedelta(days=step.day_offset)
        if due > now:
            break
        max_late = step.max_late_days if step.max_late_days is not None else seq.max_late_days
        if now - due > timedelta(days=max_late):
            skipped.append(step)
            continue
        return step, skipped
    return None, skipped


def _record(db: DB, *, brand: str, sub: dict, kind: str, status: str, now: datetime, path: str = "",
            error: str = "") -> None:
    store.ensure_schema(db)
    db.insert("emails_sent", {"brand": brand, "subscriber_id": sub["id"], "email": sub["email"], "kind": kind,
                              "status": status, "path": path, "error": error[:1000], "created_at": _iso(now)})


def run_sequences(factory, now: datetime | None = None, confirm: bool = False, *, brand: str | None = None,
                  base_url: str | None = None, strict: bool = False, limit: int = 500,
                  subscriber_id: int | None = None) -> dict:
    """Send (or dry-run) every due welcome-sequence step, one per subscriber.

    Returns {mode, blocked, sent, failed, dry_run, skipped, files, brands}.
    confirm=True sends for real only when FACTORY_DRY_RUN=0, SMTP_* and
    BUSINESS_ADDRESS are set; otherwise it falls back to a dry run and lists
    the reasons in `blocked` (strict=True raises instead). `limit` caps emails
    per run; the rest go next run. `subscriber_id` restricts the run to one
    person (used right after they confirm)."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    db: DB = factory.db
    store.ensure_schema(db)
    blockers = live_blockers(factory, confirm)
    live = confirm and not blockers
    if confirm and blockers and strict:
        if any(b.startswith("SMTP") for b in blockers):
            mailer.require_smtp()
        raise ValueError("Not sending: " + "; ".join(blockers))
    cfg = mailer.require_smtp() if live else mailer.SMTPConfig.from_env()
    base = mailer.public_url(factory.settings, base_url or "")
    result = {"mode": "send" if live else "dry_run", "blocked": [] if live else blockers, "sent": 0, "failed": 0,
              "dry_run": 0, "skipped": 0, "files": [], "brands": {}}
    brands = factory.brands()
    slugs = [brand] if brand else list(brands)
    budget = max(0, int(limit))
    for slug in slugs:
        b = brands.get(slug) if isinstance(slug, str) else None
        if b is None:
            raise KeyError(f"Unknown brand '{slug}'")
        seq = load_sequence(factory.settings, b.slug)
        if seq is None:
            continue
        if getattr(b, "welcome_via", "factory") != "factory":  # built in Sender / Kit instead: never double-send
            result["brands"][b.slug] = {"sequence": seq.name, "handled_by": b.welcome_via}
            continue
        stats = result["brands"].setdefault(b.slug, {"sequence": seq.name, "due": 0, "sent": 0, "failed": 0,
                                                     "dry_run": 0, "skipped": 0})
        history = _history(db, b.slug, seq.name)
        subs = store.list_subscribers(db, b.slug, "confirmed", limit=1_000_000)
        if subscriber_id is not None:
            subs = [s for s in subs if s["id"] == subscriber_id]
        outbox: list[tuple[dict, SequenceStep, object]] = []
        for sub in sorted(subs, key=lambda s: s["id"]):
            step, skipped = plan_for_subscriber(seq, sub, history.get(sub["id"]), now, live)
            for s in skipped:
                _record(db, brand=b.slug, sub=sub, kind=seq.kind(s), status="skipped" if live else "dry_skipped",
                        now=now, error="more than max_late_days overdue")
                stats["skipped"] += 1
                result["skipped"] += 1
            if step is None:
                continue
            stats["due"] += 1
            if budget <= 0:
                continue
            budget -= 1
            r = render_step(factory.settings, b, seq, step, sub, base=base, now=now)
            msg = mailer.build_message(brand=b, to=sub["email"], subject=r["subject"], text=r["text"],
                                       html_body=r["html"], unsubscribe_url=r["unsubscribe_url"], cfg=cfg)
            outbox.append((sub, step, msg))
        if not live:
            folder = factory.settings.output_dir / b.slug / "newsletter" / "sequences" / seq.name / "dry-run"
            for sub, step, msg in outbox:
                p = mailer.write_eml(msg, folder / f"{sub['id']:06d}-d{step.day_offset:02d}-"
                                                   f"{mailer.safe_filename(sub['email'])}.eml")
                _record(db, brand=b.slug, sub=sub, kind=seq.kind(step), status="dry_run", now=now, path=str(p))
                result["files"].append(str(p))
                stats["dry_run"] += 1
                result["dry_run"] += 1
            continue
        for start in range(0, len(outbox), 50):
            batch = outbox[start:start + 50]
            errors = mailer.smtp_send(cfg, [m for _, _, m in batch])
            for (sub, step, _), err in zip(batch, errors):
                _record(db, brand=b.slug, sub=sub, kind=seq.kind(step), status="failed" if err else "sent", now=now,
                        error=err or "")
                key = "failed" if err else "sent"
                stats[key] += 1
                result[key] += 1
    if result["sent"] or result["failed"] or result["dry_run"]:
        db.log("funnel.sequence_run", "emails_sent", None,
               {k: result[k] for k in ("mode", "sent", "failed", "dry_run", "skipped")})
    return result


def preview_sequence(factory, brand: str, *, base_url: str | None = None, now: datetime | None = None,
                     out_dir: Path | None = None) -> list[Path]:
    """Render every step for a fake subscriber to .html + .eml files for review
    (nothing is recorded or sent). Returns the .html paths."""
    b = factory.brand(brand)
    seq = load_sequence(factory.settings, b.slug)
    if seq is None:
        raise KeyError(f"No sequence for {b.slug}: create {funnel_path(factory.settings, b.slug)}")
    now = now or datetime.now(timezone.utc)
    base = mailer.public_url(factory.settings, base_url or "")
    out_dir = out_dir or factory.settings.output_dir / b.slug / "newsletter" / "sequences" / seq.name / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    fake = {"id": 0, "token": "preview-token", "email": "you@example.com"}
    paths = []
    for step in seq.steps:
        r = render_step(factory.settings, b, seq, step, fake, base=base, now=now)
        stem = f"d{step.day_offset:02d}"
        (out_dir / f"{stem}.html").write_text(r["html"])
        mailer.write_eml(mailer.build_message(brand=b, to=fake["email"], subject=r["subject"], text=r["text"],
                                              html_body=r["html"], unsubscribe_url=r["unsubscribe_url"], cfg=None),
                         out_dir / f"{stem}.eml")
        paths.append(out_dir / f"{stem}.html")
    return paths


def sequence_status(factory, brand: str) -> dict:
    """{sequence, steps: [{day_offset, subject, sent, dry_run, skipped, failed}], confirmed}."""
    b = factory.brand(brand)
    seq = load_sequence(factory.settings, b.slug)
    store.ensure_schema(factory.db)
    if seq is None:
        return {"sequence": None, "steps": [], "confirmed": 0}
    counts: dict[tuple, int] = {}
    for r in factory.db.query("SELECT kind, status, COUNT(*) n FROM emails_sent WHERE brand = ? AND kind LIKE ? "
                              "GROUP BY kind, status", [b.slug, f"{KIND_PREFIX}:{seq.name}:%"]):
        counts[(r["kind"], r["status"])] = r["n"]
    steps = [{"day_offset": s.day_offset, "subject": s.subject,
              **{st: counts.get((seq.kind(s), st), 0) for st in ("sent", "dry_run", "skipped", "failed")}}
             for s in seq.steps]
    confirmed = store.counts(factory.db, b.slug).get(b.slug, {}).get("confirmed", 0)
    return {"sequence": seq.name, "steps": steps, "confirmed": confirmed}
