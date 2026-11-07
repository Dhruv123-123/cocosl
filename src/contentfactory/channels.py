"""Repurpose finished content.json packs into other channels: Pinterest pins,
a weekly newsletter run and X / Threads text threads.

    factory channels export --brand money-made-simple \\
        --config launch/money-made-simple/channels/config.json --out channels/

The config names the source packs, the site's articles (slug, title, match
keywords), Pinterest boards, hand-written product pins and the newsletter
issues. Everything is plain text plus rendered pin images; nothing is posted.

* Pins: one 1000x1500 image per pin, a Pinterest bulk-upload CSV
  (title, board, description, link, publish date, keywords) and pins.json.
  Each carousel pin links to the closest site article (keyword match), or the
  free lead magnet when nothing fits. Carousels that mention a year are left
  out, because pins keep getting traffic for months.
* Threads: every carousel becomes an X thread (each post under 280, links
  counted as 23) and a Threads version (under 500, slides merged).
* Newsletter: one .md, .txt and .html per issue, built from the issue's
  hand-written intro plus a carousel ("money move"), an evergreen quick fact,
  an article link and one product spotlight.

All copy goes through the same text guardrails as posts (hype, testimonials,
engagement bait, banned phrases, AI and affiliate disclosure).
"""
from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from .guardrails import (AFFILIATE_DISCLOSURE, AI_DISCLOSURE, ENGAGEMENT_BAIT, HYPE_PATTERNS,
                         TESTIMONIAL_PATTERNS, check_banned, check_patterns)

PIN_SIZE = (1000, 1500)
X_LIMIT, THREADS_LIMIT, X_URL_LEN = 280, 500, 23
YEAR = re.compile(r"\b20[2-3]\d\b")
URL = re.compile(r"https?://\S+")
TEXT_AI_NOTE = "Drafted with AI tools and fact-checked by a human. Not financial advice."
PIN_AI_NOTE = "Image made with AI tools. Not financial advice."
SOCIAL_CTA = re.compile(r"\b(?:in (?:our|the|my) bio|link in bio|follow (?:for|us)|save this|comment\b)", re.I)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def load_items(sources: list[tuple[Path, str]]) -> list[dict]:
    """All items from the source packs, tagged with the pack's label; first title wins."""
    seen, out = set(), []
    for p, label in sources:
        for it in json.loads(Path(p).read_text()):
            t = it["script"]["title"]
            if t not in seen:
                seen.add(t)
                out.append({**it, "_source": label})
    return out


def check_text(brand, text: str, *, needs_ai: bool = True) -> list[dict]:
    """Text-only guardrails. Returns warn/block findings (empty list = clean)."""
    found = [check_patterns(text, TESTIMONIAL_PATTERNS, "fake_testimonial", "warn", "First-person product claims"),
             check_patterns(text, HYPE_PATTERNS, "claims", "warn", "Risky claims"),
             check_patterns(text, ENGAGEMENT_BAIT, "engagement_bait", "warn", "Engagement bait"),
             check_banned(brand, text)]
    out = [{"level": c.level, "name": c.name, "message": c.message} for c in found if c.level != "ok"]
    if needs_ai and not AI_DISCLOSURE.search(text):
        out.append({"level": "block", "name": "ai_label", "message": "No AI disclosure"})
    if any(a.url in text for a in brand.affiliates) and not AFFILIATE_DISCLOSURE.search(text):
        out.append({"level": "block", "name": "affiliate_disclosure", "message": "Affiliate link without disclosure"})
    return out


# ---------------------------------------------------------------- links
@dataclass
class Links:
    site: str
    articles: dict  # slug -> {title, keywords}
    products: dict  # slug -> {name, url}
    utm: str = "utm_source={src}&utm_medium=social&utm_campaign={camp}"
    min_score: int = 3
    free_path: str = "/free/"
    free_label: str = "The free download"

    def url(self, target: str, src: str, camp: str, medium: str = "social") -> str:
        kind, _, slug = target.partition(":")
        if kind == "article":
            base = self.site + self.articles[slug].get("path", f"/blog/{slug}/")
        elif kind == "product":
            base = self.products[slug]["url"]
        elif kind == "free":
            base = self.site + self.free_path
        else:
            base = target
        if not base.startswith(self.site):  # leave store links clean; Gumroad keeps its own stats
            return base
        return f"{base}?{self.utm.format(src=src, camp=camp).replace('medium=social', 'medium=' + medium)}"

    def label(self, target: str) -> str:
        kind, _, slug = target.partition(":")
        if kind == "article":
            return self.articles[slug]["title"]
        if kind == "product":
            return self.products[slug]["name"]
        return self.free_label

    def lead_in(self, target: str) -> str:
        """How a post introduces its link: a guide, a free download or a product."""
        kind, _, slug = target.partition(":")
        if kind == "article" and self.articles.get(slug, {}).get("lead_in"):
            return self.articles[slug]["lead_in"]
        return {"article": "Read the full guide", "product": "More"}.get(kind, "Free download")

    def match(self, item: dict) -> tuple[str, int]:
        """Closest article by keyword hits (title counts triple). Falls back to the lead magnet."""
        sc = item["script"]
        title, body = sc["title"].lower(), (sc["caption"] + " " + " ".join(s["narration"] for s in sc["segments"])).lower()
        best, score = "free", 0
        for slug, a in self.articles.items():
            s = sum(3 * title.count(k) + min(body.count(k), 3) for k in a["keywords"])
            if s > score:
                best, score = f"article:{slug}", s
        if score < self.min_score:  # a weak match reads as a bait-and-switch; send them to the free reset instead
            return "free", score
        return best, score


# ---------------------------------------------------------------- pins
@dataclass
class Pin:
    n: int
    title: str
    description: str
    link: str
    target: str
    board: str
    alt_text: str
    image_text: str
    kicker: str
    prompt: str
    keywords: list[str]
    publish_at: str = ""
    source: str = ""
    image: str = ""
    checks: list[dict] = field(default_factory=list)


def _fit(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:·-")
    return cut + "…"


def pin_from_item(item: dict, links: Links, boards: dict, target: str, brand_name: str) -> Pin:
    sc = item["script"]
    segs = sc["segments"]
    points = [re.sub(r"^(?:#?\d+[.):]?|\d+[–-]\d+)\s+", "", s["on_screen_text"]) for s in segs[1:-1]
              if s.get("on_screen_text")][:6]
    dest = links.label(target)
    lead = segs[0]["narration"] or sc.get("hook", "")
    body = f"{lead} Inside: " + "; ".join(p.rstrip(".") for p in points) + "."
    tail = f" {links.lead_in(target)}: {dest}. {PIN_AI_NOTE}"
    description = _fit(body, 500 - len(tail)) + tail
    own = re.sub(r"[^a-z0-9]", "", brand_name.lower())
    keywords = [h.replace("#", "") for h in sc["hashtags"] if h.replace("#", "").lower() != own][:6]
    return Pin(0, _fit(sc["title"], 100), description, "", target, boards.get(item["pillar"], brand_name),
               _fit(f"Illustrated pin titled '{sc['title']}', a {len(points)}-point checklist from {brand_name}.", 500),
               sc["title"], item["pillar"].split(" (")[0], segs[0]["visual_prompt"], keywords,
               source=f"{item['_source']}: {sc['title']}")


def _pin_visible(item: dict) -> str:
    """The text a pin shows (title, lead line, on-screen points); a year here dates the pin."""
    sc = item["script"]
    return " ".join([sc["title"], sc["segments"][0]["narration"]] + [s.get("on_screen_text", "") for s in sc["segments"]])


def pick_items(items: list[dict], links: Links, count: int, per_target: int = 5,
               formats: tuple[str, ...] = ("carousel",), free_cap: int | None = None) -> list[tuple[dict, str]]:
    """Strongest article matches first (carousels before shorts), at most `per_target` pins per article and
    `free_cap` for the lead magnet, pillars interleaved."""
    pool = []
    for it in items:
        if (it["format"] not in formats or it.get("platforms") == ["tiktok"]  # TikTok cuts repeat a Short
                or YEAR.search(_pin_visible(it))):
            continue
        target, score = links.match(it)
        pool.append((score, it, target))
    pool.sort(key=lambda x: (-x[0], formats.index(x[1]["format"])))
    taken, used = [], {}
    firsts = []  # every article gets its best two before anyone gets a third
    for row in pool:
        if row[2] != "free" and sum(r[2] == row[2] for r in firsts) < 2:
            firsts.append(row)
    pool = firsts + [r for r in pool if r not in firsts]
    for score, it, target in pool:
        cap = per_target if target != "free" else (free_cap if free_cap is not None else per_target * 2)
        if used.get(target, 0) < cap:
            taken.append((it, target))
            used[target] = used.get(target, 0) + 1
        if len(taken) == count:
            break
    by_pillar: dict[str, list] = {}
    for it, t in taken:
        by_pillar.setdefault(it["pillar"], []).append((it, t))
    out, queues = [], list(by_pillar.values())
    while any(queues):
        for q in queues:
            if q:
                out.append(q.pop(0))
    return out


def render_pin(factory, brand, pin: Pin, dest: Path) -> Path:
    from PIL import Image, ImageDraw, ImageOps

    from .media import fonts
    from .media.carousel import scrim
    from .media.images import generate_images
    from .media.util import Palette

    w, h = PIN_SIZE
    pal = Palette.from_brand(brand)
    work = dest.parent / f"_art-{pin.n:02d}"
    art = generate_images(factory.settings, brand, [pin.prompt], PIN_SIZE, "2:3", work,
                          family=f"{brand.slug}:pin:{pin.title}")[0].path
    img = ImageOps.fit(Image.open(art).convert("RGB"), PIN_SIZE, Image.LANCZOS).convert("RGBA")
    img.alpha_composite(scrim(PIN_SIZE, pal.dark, 0.30, 0.62, 245, direction="down"))
    margin, accent = 70, pal.accent_on(pal.dark, 4.5)
    d = ImageDraw.Draw(img)
    kf = fonts.load(fonts.font_path(brand.visual.font, "bold"), 34)
    ky = int(h * 0.52)
    d.text((margin, ky), pin.kicker.upper(), font=kf, fill=(*accent, 255))
    block = fonts.fit(pin.image_text, fonts.font_path(brand.visual.font, "black"), w - 2 * margin, int(h * 0.30),
                      112, 54, leading=1.05, max_lines=5)
    fonts.draw_block(img, block, (margin, ky + 60), (*pal.light, 255), shadow=(0, 0, 0, 160), shadow_radius=10)
    pill = brand.visual.watermark or brand.name
    pf = fonts.load(fonts.font_path(brand.visual.font, "semibold"), 32)
    tw = int(pf.getlength(pill))
    y0 = h - 120
    d.rounded_rectangle((margin, y0, margin + tw + 56, y0 + 64), radius=32, fill=(*accent, 255))
    d.text((margin + 28, y0 + 32), pill, font=pf, fill=(*pal.dark, 255), anchor="lm")
    import shutil
    shutil.rmtree(work, ignore_errors=True)
    out = dest.with_suffix(".jpg")
    img.convert("RGB").save(out, quality=90, optimize=True, progressive=True)
    return out


def build_pins(brand, items, links: Links, cfg: dict) -> list[Pin]:
    boards = cfg.get("boards", {})
    hand = cfg.get("product_pins", [])
    picks = pick_items(items, links, cfg.get("count", 60) - len(hand), cfg.get("per_article", 5),
                       tuple(cfg.get("formats", ["carousel"])), cfg.get("free_cap"))
    pins = [pin_from_item(it, links, boards, t, brand.name) for it, t in picks]
    every = max(1, len(pins) // max(1, len(hand)) + 1)
    for i, hp in enumerate(hand):  # spread product pins through the schedule
        tail = f" {PIN_AI_NOTE}"
        p = Pin(0, _fit(hp["title"], 100), _fit(hp["description"], 500 - len(tail)) + tail, "", hp["target"],
                boards.get("products", f"{brand.name} Printables"), hp.get("alt_text", hp["title"]),
                hp.get("image_text", hp["title"]), hp.get("kicker", "Free + printable"), hp["prompt"],
                hp.get("keywords", []), source="hand-written")
        pins.insert(min(len(pins), (i + 1) * every - 1), p)
    start = date.fromisoformat(cfg["start"])
    times = cfg.get("times", ["10:00", "20:30"])
    for n, p in enumerate(pins, start=1):
        p.n = n
        day = start + timedelta(days=(n - 1) // len(times))
        p.publish_at = f"{day.isoformat()}T{times[(n - 1) % len(times)]}:00"
        p.link = links.url(p.target, "pinterest", "pin-" + slugify(p.title)[:40])
        p.checks = check_text(brand, f"{p.title}\n{p.description}")
    return pins


def write_pins(factory, brand, pins: list[Pin], out: Path, render: bool = True) -> None:
    d = out / "pinterest"
    (d / "images").mkdir(parents=True, exist_ok=True)
    for p in pins:
        if render:
            img = render_pin(factory, brand, p, d / "images" / f"{p.n:02d}-{slugify(p.title)}")
            p.image = f"images/{img.name}"
    with open(d / "pins.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
        for p in pins:
            wr.writerow([p.title, p.image, p.board, "", p.description, p.link, p.publish_at, ", ".join(p.keywords)])
    (d / "pins.json").write_text(json.dumps([asdict(p) for p in pins], indent=1, ensure_ascii=False))
    rows = ["# Pinterest pins", "", f"{len(pins)} pins, two a day. Upload images, then use pins.csv "
            "(Pinterest > Create > Bulk create pins). Replace the Media URL column with the hosted image URLs first.", "",
            "| # | Publish | Board | Title | Links to |", "|---|---|---|---|---|"]
    rows += [f"| {p.n} | {p.publish_at.replace('T', ' ')[:16]} | {p.board} | {p.title} | {p.target} |" for p in pins]
    (d / "PINS.md").write_text("\n".join(rows) + "\n")


# ---------------------------------------------------------------- threads
def x_len(text: str) -> int:
    return len(URL.sub("x" * X_URL_LEN, text))


def _split(text: str, limit: int, measure=len) -> list[str]:
    if measure(text) <= limit:
        return [text]
    parts, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text):
        cand = f"{cur} {s}".strip()
        if cur and measure(cand) > limit:
            parts.append(cur)
            cur = s
        else:
            cur = cand
    return parts + [cur] if cur else parts


def thread_posts(item: dict, link: str, label: str, platform: str, lead_in: str = "The full guide") -> list[str]:
    segs = item["script"]["segments"]
    limit, measure = (X_LIMIT - 8, x_len) if platform == "x" else (THREADS_LIMIT, len)
    body = [s["narration"] for s in segs]
    end = f"{lead_in}: {label}\n{link}\n\n{TEXT_AI_NOTE}"
    if platform == "threads":  # fewer, fuller posts
        merged, cur = [], ""
        for b in body[1:]:
            cand = f"{cur}\n\n{b}".strip()
            if cur and measure(cand) > limit:
                merged.append(cur)
                cur = b
            else:
                cur = cand
        body = [body[0]] + merged + ([cur] if cur else [])
    posts = []
    for b in body:
        posts += _split(b, limit, measure)
    posts.append(end)
    if platform == "x":
        n = len(posts)
        posts = [f"{p}\n\n{i}/{n}" if i < n else p for i, p in enumerate(posts, start=1)]
        posts[0] = posts[0].replace(f"\n\n1/{n}", f" 🧵\n\n1/{n}")
    return posts


def build_threads(brand, items, links: Links) -> list[dict]:
    out = []
    for it in items:
        if it["format"] != "carousel":
            continue
        target, _ = links.match(it)
        label = links.label(target)
        rec = {"title": it["script"]["title"], "source": it["_source"], "target": target}
        for plat in ("x", "threads"):
            link = links.url(target, plat, "thread-" + slugify(it["script"]["title"])[:40])
            posts = thread_posts(it, link, label, plat, links.lead_in(target))
            rec[plat] = posts
            rec[f"{plat}_checks"] = check_text(brand, "\n".join(posts))
        assert all(x_len(p) <= X_LIMIT for p in rec["x"]), rec["title"]
        assert all(len(p) <= THREADS_LIMIT for p in rec["threads"]), rec["title"]
        out.append(rec)
    return out


def write_threads(threads: list[dict], out: Path) -> None:
    d = out / "threads"
    d.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(threads, start=1):
        sub = d / t["source"]
        sub.mkdir(exist_ok=True)
        txt = [f"# {t['title']}", "", f"Links to: {t['target']}", "", "## X (one post per block, under 280 characters)", ""]
        for p in t["x"]:
            txt += [p, "", "---", ""]
        txt += ["## Threads (one post per block, under 500 characters)", ""]
        for p in t["threads"]:
            txt += [p, "", "---", ""]
        (sub / f"{i:03d}-{slugify(t['title'])}.md").write_text("\n".join(txt))
    (d / "threads.json").write_text(json.dumps(threads, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- newsletter
def _find(items: list[dict], title: str) -> dict:
    for it in items:
        if it["script"]["title"] == title:
            return it
    raise KeyError(f"No item titled {title!r} in the source packs")


def build_issue(brand, items, links: Links, issue: dict, n: int, day: date, products: dict) -> dict:
    move = _find(items, issue["move"])
    fact = _find(items, issue["fact"])
    read = issue.get("read")
    if read and ":" not in read and read != "free":
        read = f"article:{read}"
    fsegs = [s for s in fact["script"]["segments"] if not re.search(r"\bfollow\b", s["narration"], re.I)][:4]
    prod = products.get(issue.get("product") or "", {})
    camp = f"newsletter-{n:02d}"
    msegs = move["script"]["segments"]
    blocks = {
        "subject": issue["subject"], "preview": issue["preview"], "date": day.isoformat(), "n": n,
        "intro": issue["intro"],
        "move_title": move["script"]["title"],
        "move_lead": msegs[0]["narration"] or move["script"].get("hook", ""),
        "move_points": [s["narration"] for s in msegs[1:-1] if not SOCIAL_CTA.search(s["narration"])],
        "move_close": "" if SOCIAL_CTA.search(msegs[-1]["narration"]) else msegs[-1]["narration"],
        "fact_title": fact["script"]["title"],
        "fact": " ".join(s["narration"] for s in fsegs),
        "move_label": issue.get("move_label", "This week's money move"),
        "read_title": links.label(read) if read else "", "read_url": links.url(read, "newsletter", camp, "email") if read else "",
        "read_blurb": issue.get("read_blurb") or (links.articles[read[8:]].get("blurb", "") if read and read.startswith("article:") else ""),
        "product_name": prod.get("name", ""),
        "product_url": links.url(f"product:{issue['product']}", "newsletter", camp, "email") if prod else "",
        "product_blurb": prod.get("blurb", ""),
        "ps": issue.get("ps", ""),
        "sources": sorted(set(move["script"]["sources"] + fact["script"]["sources"])),
        "claims_to_verify": move["script"]["claims_to_verify"] + fact["script"]["claims_to_verify"],
    }
    blocks["text"] = issue_text(brand, blocks)
    blocks["checks"] = check_text(brand, blocks["text"])
    return blocks


FOOTER = ("You're getting this because you signed up for {site} emails. Unsubscribe: {{unsubscribe_url}}\n"
          "{{business_address}}\n\n"
          "{site} is education, not financial, tax or investment advice. Drafted with AI tools and fact-checked "
          "by a human. Product mentions are our own products unless marked as an affiliate link.")


def issue_text(brand, b: dict) -> str:
    lines = [f"Subject: {b['subject']}", f"Preview: {b['preview']}", "", b["intro"], "",
             f"{b['move_label'].upper()}: {b['move_title']}", "", b["move_lead"], ""]
    lines += [f"• {p}" for p in b["move_points"]]
    lines += (["", b["move_close"]] if b["move_close"] else []) + ["", f"QUICK FACT: {b['fact_title']}", "", b["fact"], ""]
    if b["read_url"]:
        lines += [f"WORTH READING: {b['read_title']}", b["read_blurb"], b["read_url"], ""]
    if b["product_url"]:
        lines += [f"FROM US: {b['product_name']}", b["product_blurb"], b["product_url"], ""]
    if b["ps"]:
        lines += [f"P.S. {b['ps']}", ""]
    lines += ["See you next Sunday,", brand.name, "", "—", FOOTER.replace("{site}", brand.name)]
    return "\n".join(lines)


def issue_html(brand, b: dict) -> str:
    from .media.util import Palette
    pal = Palette.from_brand(brand)
    hexc = lambda c: "#%02x%02x%02x" % c  # noqa: E731
    dark, accent = hexc(pal.dark), hexc(pal.accent_on(pal.light, 3.0))
    e = html.escape
    pts = "".join(f"<li style='margin:0 0 8px'>{e(p)}</li>" for p in b["move_points"])
    ps = f"<p><b>P.S.</b> {e(b['ps'])}</p>" if b["ps"] else ""
    btn = (f"display:inline-block;background:{dark};color:#fff;padding:10px 16px;border-radius:8px;"
           "text-decoration:none;font-weight:600")
    read = (f"<h3 style='margin:24px 0 6px'>Worth reading</h3><p><b>{e(b['read_title'])}</b><br>{e(b['read_blurb'])}</p>"
            f"<p><a href=\"{e(b['read_url'])}\" style=\"{btn}\">Read it</a></p>") if b["read_url"] else ""
    paper = hexc(pal.light)
    close = f"<p>{e(b['move_close'])}</p>" if b["move_close"] else ""
    prod = (f"<h3 style='margin:24px 0 6px'>From us: {e(b['product_name'])}</h3><p>{e(b['product_blurb'])}</p>"
            f"<p><a href=\"{e(b['product_url'])}\" style=\"color:{dark};font-weight:600\">Take a look →</a></p>"
            ) if b["product_url"] else ""
    foot = e(FOOTER.replace("{site}", brand.name)).replace("\n", "<br>")
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(b['subject'])}</title></head>
<body style="margin:0;background:{paper};font:16px/1.55 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1d2a22">
<span style="display:none;max-height:0;overflow:hidden">{e(b['preview'])}</span>
<div style="max-width:600px;margin:0 auto;padding:24px 16px">
<div style="background:{dark};color:{paper};padding:18px 22px;border-radius:12px 12px 0 0;font-weight:700">{e(brand.name)} · Issue {b['n']}</div>
<div style="background:#fff;padding:22px;border-radius:0 0 12px 12px">
<p>{e(b['intro'])}</p>
<h2 style="font-size:20px;margin:24px 0 8px;color:{dark}">{e(b['move_label'])}: {e(b['move_title'])}</h2>
<p>{e(b['move_lead'])}</p><ul style="padding-left:20px">{pts}</ul>{close}
<div style="background:{paper};border-left:4px solid {accent};padding:12px 16px;margin:20px 0;border-radius:6px">
<b>Quick fact: {e(b['fact_title'])}</b><br>{e(b['fact'])}</div>
{read}
{prod}
{ps}<p>See you next Sunday,<br>{e(brand.name)}</p></div>
<p style="font-size:12px;color:#5b665f;margin-top:16px">{foot}</p></div></body></html>"""


def build_newsletter(brand, items, links: Links, cfg: dict) -> list[dict]:
    start = date.fromisoformat(cfg["start"])
    products = cfg["products"]
    return [build_issue(brand, items, links, iss, n, start + timedelta(weeks=n - 1), products)
            for n, iss in enumerate(cfg["issues"], start=1)]


def write_newsletter(brand, issues: list[dict], out: Path) -> None:
    d = out / "newsletter"
    d.mkdir(parents=True, exist_ok=True)
    rows = ["# Newsletter run", "", "Send each issue on its Sunday. Paste the .html into your email tool (or the .txt "
            "for plain-text), fill {{unsubscribe_url}} and {{business_address}} (your tool usually does both), and tick "
            "the fact checks first.", "", "| # | Send | Subject | Main piece | Product |", "|---|---|---|---|---|"]
    for b in issues:
        stem = f"{b['n']:02d}-{b['date']}-{slugify(b['subject'])[:40]}"
        checks = "\n".join(f"[ ] {c}" for c in b["claims_to_verify"]) + "\n\nSources:\n" + "\n".join(b["sources"])
        (d / f"{stem}.txt").write_text(b["text"] + "\n\n--- CHECK BEFORE SENDING (delete this part) ---\n" + checks + "\n")
        (d / f"{stem}.html").write_text(issue_html(brand, b))
        rows.append(f"| {b['n']} | {b['date']} | {b['subject']} | {b['move_title']} | {b['product_name'] or '—'} |")
    (d / "ISSUES.md").write_text("\n".join(rows) + "\n")
    (d / "issues.json").write_text(json.dumps(issues, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- export
def load_config(path: Path) -> dict:
    cfg = json.loads(Path(path).read_text())
    base = Path(path).parent
    cfg["_sources"] = [((base / s[0]).resolve(), s[1]) if isinstance(s, list) else ((base / s).resolve(), Path(s).stem)
                       for s in cfg["sources"]]
    return cfg


def make_links(brand, cfg: dict) -> Links:
    products = {p.get("slug") or slugify(p["name"]): {"name": p["name"], "url": p["url"]} for p in brand.products}
    for slug, over in cfg.get("product_urls", {}).items():  # e.g. a product that has its own site page
        products.setdefault(slug, {"name": slug, "url": ""})["url"] = over.replace("{site}", cfg["site_url"])
    for slug, p in cfg.get("newsletter", {}).get("products", {}).items():
        products.setdefault(slug, {"name": p.get("name", slug), "url": ""})
        p.setdefault("name", products[slug]["name"])
    return Links(cfg["site_url"].rstrip("/"), cfg.get("articles", {}), products,
                 free_path=cfg.get("free_path", "/free/"), free_label=cfg.get("free_label", "The free download"))


def export(factory, brand_slug: str, config: Path, out: Path, render: bool = True) -> dict:
    brand = factory.brand(brand_slug)
    cfg = load_config(config)
    items = load_items(cfg["_sources"])
    links = make_links(brand, cfg)
    out.mkdir(parents=True, exist_ok=True)
    pins = build_pins(brand, items, links, cfg["pins"])
    write_pins(factory, brand, pins, out, render=render)
    threads = build_threads(brand, items, links)
    write_threads(threads, out)
    issues = build_newsletter(brand, items, links, cfg["newsletter"])
    write_newsletter(brand, issues, out)
    findings = ([("pin", p.title, c) for p in pins for c in p.checks]
                + [(f"thread:{k}", t["title"], c) for t in threads for k in ("x", "threads") for c in t[f"{k}_checks"]]
                + [("newsletter", b["subject"], c) for b in issues for c in b["checks"]])
    lines = ["# Channel guardrail results", "", f"{len(pins)} pins, {len(threads)} threads, {len(issues)} newsletter issues.", ""]
    lines += [f"- {kind} **{title}**: {c['level']}: {c['name']}: {c['message']}" for kind, title, c in findings] or ["No warnings or blocks."]
    (out / "CHECKS.md").write_text("\n".join(lines) + "\n")
    return {"pins": len(pins), "threads": len(threads), "issues": len(issues),
            "warn": sum(c["level"] == "warn" for *_, c in findings),
            "block": sum(c["level"] == "block" for *_, c in findings), "out": str(out)}


def register(sub, factory_fn) -> None:
    s = sub.add_parser("channels", help="repurpose content packs into Pinterest pins, newsletters and text threads")
    ssub = s.add_subparsers(dest="channels_cmd", required=True)
    e = ssub.add_parser("export", help="write pins (with images), newsletter issues and X/Threads threads")
    e.add_argument("--brand", required=True)
    e.add_argument("--config", required=True, help="channels config JSON")
    e.add_argument("--out", default="channels")
    e.add_argument("--no-images", action="store_true", help="skip rendering pin images")

    def run(a):
        res = export(factory_fn(a), a.brand, Path(a.config), Path(a.out), render=not a.no_images)
        print(json.dumps(res, indent=1))
    e.set_defaults(func=run)
