"""`factory launch-check`: one red / yellow / green answer to "can this go out?".

For every brand it checks, in one pass:
* links: every URL in the brand file (affiliates, products, link page...) and
  in posts going out in the next N days is well formed; placeholders
  (example.com, REPLACE_ME, ...) are listed. `--online` also asks each real
  URL whether it answers.
* UTM tags: utm_* values use only letters, digits, `-`, `_`, `.`, and a
  campaign comes with a source and medium.
* placeholders: nothing scheduled in the next N days (default 14) still
  contains REPLACE_ME or another placeholder; that is red.
* disclosures: affiliate posts say so (FTC), and every post has the AI label.
* caption limits per platform each post is queued for (Instagram 2,200 chars
  and 30 hashtags, TikTok 2,200, Threads 500, YouTube title 100 / description
  5,000 bytes). Over the limit is yellow: the publisher trims, but you should
  choose what goes.

Red = something would go out wrong. Yellow = fine for dry run, fix before
going live. Nothing is posted or changed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlsplit

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")
PLACEHOLDER_RE = re.compile(r"REPLACE[_-]?ME|YOUR[_-](?:LINK|URL|HANDLE|CODE|ID)|(?-i:\bTODO\b|\bTBD\b)|\{\{.*?\}\}|"
                            r"\bexample\.(?:com|org|net)\b|\bexample\.gumroad\.com\b|\blocalhost\b|(?-i:\bXXX+\b)", re.I)
UTM_VALUE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
CAPTION_LIMITS = {  # platform -> (max chars, max hashtags)
    "instagram": (2200, 30), "tiktok": (2200, None), "threads": (500, None), "facebook": (63206, None),
}
LEVELS = {"green": 0, "yellow": 1, "red": 2}


@dataclass
class Finding:
    level: str  # red | yellow
    brand: str
    where: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    checked: dict = field(default_factory=dict)

    def add(self, level: str, brand: str, where: str, message: str) -> None:
        self.findings.append(Finding(level, brand, where, message))

    @property
    def status(self) -> str:
        worst = max((LEVELS[f.level] for f in self.findings), default=0)
        return {0: "green", 1: "yellow", 2: "red"}[worst]


def _strings(obj, path: str = ""):
    """Every string inside nested dicts/lists, with a dotted path."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _strings(v, f"{path}[{i}]")


def check_url(url: str) -> list[tuple[str, str]]:
    """[(level, message)] for one URL."""
    out = []
    url = url.rstrip(".,;:!?")
    parts = urlsplit(url)
    if not parts.netloc or "." not in parts.netloc:
        out.append(("red", f"malformed link: {url}"))
        return out
    if PLACEHOLDER_RE.search(url):
        out.append(("yellow", f"placeholder link: {url}"))
    if parts.scheme == "http":
        out.append(("yellow", f"not HTTPS: {url}"))
    query = parse_qsl(parts.query, keep_blank_values=True)
    utm = {k: v for k, v in query if k.startswith("utm_")}
    for k, v in utm.items():
        if k not in ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"):
            out.append(("yellow", f"unknown UTM key {k} in {url}"))
        elif not v or not UTM_VALUE_RE.match(v):
            out.append(("red", f"bad UTM value {k}={v!r} in {url} (letters, digits, - _ . only)"))
    if "utm_campaign" in utm and not ({"utm_source", "utm_medium"} <= set(utm)):
        out.append(("yellow", f"utm_campaign without utm_source/utm_medium in {url}"))
    return out


def _online(urls: set[str]) -> dict[str, str]:
    import httpx
    bad = {}
    for url in sorted(urls):
        try:
            r = httpx.head(url, timeout=10, follow_redirects=True)
            if r.status_code == 405:
                r = httpx.get(url, timeout=10, follow_redirects=True)
            if r.status_code >= 400:
                bad[url] = f"answers {r.status_code}"
        except Exception as e:
            bad[url] = f"unreachable ({type(e).__name__})"
    return bad


def run(factory, days: int = 14, online: bool = False, now: datetime | None = None) -> Report:
    from .guardrails import AFFILIATE_DISCLOSURE, AI_DISCLOSURE
    from .publish._text import utf8_len
    now = now or datetime.now(timezone.utc)
    horizon = (now + timedelta(days=days)).isoformat()
    rep = Report()
    real_urls: dict[str, tuple[str, str]] = {}
    brands = factory.brands()
    for slug, brand in brands.items():
        data = brand.model_dump()
        n_urls = 0
        for path, text in _strings(data):
            for url in URL_RE.findall(text):
                n_urls += 1
                for level, msg in check_url(url):
                    rep.add(level, slug, f"brand file: {path}", msg)
                if not PLACEHOLDER_RE.search(url):
                    real_urls.setdefault(url.rstrip(".,;:!?"), (slug, f"brand file: {path}"))
            if PLACEHOLDER_RE.search(text) and not URL_RE.search(text):
                rep.add("yellow", slug, f"brand file: {path}", f"placeholder text: {text[:80]}")
        rep.checked.setdefault(slug, {})["brand_links"] = n_urls

        pubs = factory.db.query(
            "SELECT s.*, pub.platform AS pub_platform, pub.scheduled_at AS pub_at FROM publications pub JOIN posts s ON s.id = pub.post_id "
            "WHERE s.brand = ? AND pub.status = 'queued' AND pub.scheduled_at <= ? ORDER BY pub.scheduled_at",
            [slug, horizon])
        rep.checked[slug]["scheduled"] = len(pubs)
        seen_posts: set[int] = set()
        for row in pubs:
            pid, platform = row["id"], row["pub_platform"]
            where = f"post #{pid} ({platform}, {row['pub_at'][:16].replace('T', ' ')} UTC)"
            req = factory.build_request(row, platform)
            caption = req.caption
            text_bits = {"caption": caption, "title": req.title, "description": req.description}
            if pid not in seen_posts:
                seen_posts.add(pid)
                for path, text in [*text_bits.items(), *_strings(row.get("script") or {}, "script")]:
                    m = PLACEHOLDER_RE.search(text or "")
                    if m:
                        rep.add("red", slug, where, f"placeholder left in {path}: …{text[max(0, m.start() - 30):m.end() + 30][:90]}…")
                    for url in URL_RE.findall(text or ""):
                        for level, msg in check_url(url):
                            rep.add("red" if level == "yellow" and "placeholder" in msg else level, slug, where, msg)
                        if not PLACEHOLDER_RE.search(url):
                            real_urls.setdefault(url.rstrip(".,;:!?"), (slug, where))
                has_affiliate = bool((row.get("meta") or {}).get("affiliate_slugs")) or any(
                    a.url and a.url in caption for a in brand.affiliates) or "/go/" in caption
                full = f"{caption}\n{req.description}"
                if has_affiliate and not AFFILIATE_DISCLOSURE.search(full):
                    rep.add("red", slug, where, "affiliate link without a disclosure (FTC): add 'affiliate link' or #ad")
                if not AI_DISCLOSURE.search(full):
                    rep.add("red" if brand.realistic_synthetic_media else "yellow", slug, where,
                            "no AI disclosure in the caption")
            limit = CAPTION_LIMITS.get(platform)
            if limit:
                chars, tags = limit
                n = len(caption.encode("utf-16-le")) // 2 if platform == "tiktok" else len(caption)
                if n > chars:
                    rep.add("yellow", slug, where, f"caption {n} chars, {platform} takes {chars}; it will be trimmed")
                ntags = len(re.findall(r"(?<!\w)#\w+", caption))
                if tags and ntags > tags:
                    rep.add("yellow", slug, where, f"{ntags} hashtags, {platform} takes {tags}; extras are dropped")
            if platform == "youtube":
                if len(req.title or "") > 100:
                    rep.add("yellow", slug, where, f"title {len(req.title)} chars, YouTube takes 100; it will be cut")
                if utf8_len(req.description or "") > 5000:
                    rep.add("yellow", slug, where, "description over 5,000 bytes; it will be trimmed")
                if re.search(r"[<>]", f"{req.title}{req.description}"):
                    rep.add("yellow", slug, where, "YouTube strips < and > from titles and descriptions")
    if online and real_urls:
        for url, problem in _online(set(real_urls)).items():
            slug, where = real_urls[url]
            rep.add("red", slug, where, f"{url} {problem}")
    return rep


def render_text(rep: Report, days: int) -> str:
    icon = {"green": "GREEN", "yellow": "YELLOW", "red": "RED"}[rep.status]
    lines = [f"Launch check: {icon}", ""]
    for slug, c in rep.checked.items():
        mine = [f for f in rep.findings if f.brand == slug]
        worst = max((LEVELS[f.level] for f in mine), default=0)
        lines.append(f"{slug}: {['green', 'yellow', 'red'][worst]} · {c.get('scheduled', 0)} publication(s) in the "
                     f"next {days} days · {c.get('brand_links', 0)} link(s) in the brand file")
        for level in ("red", "yellow"):
            for f in [f for f in mine if f.level == level]:
                lines.append(f"  [{level}] {f.where}: {f.message}")
    if rep.status == "green":
        lines += ["", "Everything scheduled is ready to go out."]
    elif rep.status == "yellow":
        lines += ["", "Fine for dry run. Fix the yellow items before FACTORY_DRY_RUN=0."]
    else:
        lines += ["", "Fix the red items before anything goes out."]
    return "\n".join(lines)


def register(sub, factory_fn) -> None:
    s = sub.add_parser("launch-check", help="one red/yellow/green report: links, UTM, placeholders, "
                                            "disclosures, caption limits (posts nothing)")
    s.add_argument("--days", type=int, default=14, help="how far ahead to check scheduled posts")
    s.add_argument("--online", action="store_true", help="also check that every real link answers")

    def cmd(a):
        rep = run(factory_fn(a), a.days, a.online)
        print(render_text(rep, a.days))
        if rep.status == "red":
            raise SystemExit(2)
    s.set_defaults(func=cmd)
