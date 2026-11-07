"""`factory whitelabel <brand> --client config.json`: a brand's content batch, rebranded for a client.

Generalises the credit-union alert builder (PR #13) from one product to any brand's posts:

    factory whitelabel money-made-simple --client clients/acme-cu.json            # approved/scheduled/published
    factory whitelabel money-made-simple --client clients/acme-cu.json --posts 12,14,15 --no-render

Client config (JSON):
    {"slug": "acme-cu", "name": "Acme Community Credit Union", "short": "Acme CU",
     "handle": "@acmecu", "website": "https://www.acmecu.org", "phone": "(555) 010-0142",
     "palette": ["#0f2a44", "#f7f4ec", "#1f7ae0", "#f2b134"]   # or "color" + "accent" like PR #13
     "font": "Inter", "logo": "acme-logo.png",                   # path relative to the config file
     "cta": "Questions? Call Acme CU at (555) 010-0142.",
     "ai_disclosure": "", "footer_lines": ["Federally insured by NCUA."],
     "signature": {"device": "stripe"}, "tokens": {"BRANCH_HOURS": "Mon-Fri 9-5"},
     "replace": {"our members": "Acme members"}, "credit_line": ""}

For each post it swaps our brand name, handles, brand hashtag, CTA and links (link page, products,
affiliate /go/ links: our affiliate deals never go into a client's content) for the client's, fills
{{TOKENS}}, then re-renders the media in the client's colours, font, watermark and signature. The
AI disclosure always stays (the client's wording if given, ours otherwise). Like the PR #13 build, it
fails if any of our brand or an unfilled {{TOKEN}} is left anywhere.

Output: output/whitelabel/<client>/<YYYY-MM-DD>/ with posts/NN-<format>/ (media, caption.txt, script.md),
sources.md (every claim the client's compliance team should check), manifest.json, README.md, and a zip.
Nothing is posted or added to the review queue.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, Field

TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")


class ClientConfig(BaseModel):
    slug: str
    name: str
    short: str = ""
    handle: str = ""
    website: str = ""
    phone: str = ""
    palette: list[str] = Field(default_factory=list)
    color: str = ""
    accent: str = ""
    font: str = ""
    logo: str = ""
    cta: str = ""
    ai_disclosure: str = ""
    footer_lines: list[str] = Field(default_factory=list)
    signature: dict = Field(default_factory=lambda: {"device": "none"})
    tokens: dict[str, str] = Field(default_factory=dict)
    replace: dict[str, str] = Field(default_factory=dict)
    credit_line: str = ""
    hashtag: str = ""

    def colours(self) -> list[str]:
        if self.palette:
            return self.palette
        if self.color:
            return [self.color, "#f7f6f2", *([self.accent] if self.accent else [])]
        return []


def load_client(path: Path) -> ClientConfig:
    cfg = ClientConfig.model_validate(json.loads(Path(path).read_text()))
    if not re.match(r"^[a-z0-9][a-z0-9-]{1,60}$", cfg.slug):
        raise ValueError("client slug: lowercase letters, digits and dashes")
    return cfg


def client_brand(source, cfg: ClientConfig):
    """A BrandProfile for rendering: the source brand's voice and formats, the client's look and links."""
    b = source.model_copy(deep=True)
    b.slug, b.name = cfg.slug, cfg.name
    b.cta = cfg.cta or (f"Questions? Visit {cfg.website}" if cfg.website else "")
    b.link_in_bio = cfg.website
    b.hashtags = [cfg.hashtag or re.sub(r"[^a-z0-9]", "", cfg.slug)]
    b.ai_disclosure = cfg.ai_disclosure or source.ai_disclosure
    b.products, b.affiliates, b.accounts = [], [], []
    if cfg.colours():
        b.visual.palette = cfg.colours()
    if cfg.font:
        b.visual.font = cfg.font
    b.visual.watermark = cfg.handle or (urlsplit(cfg.website).netloc.removeprefix("www.") if cfg.website else cfg.short)
    b.visual.mascot = ""
    from .config import SignatureVisual
    b.visual.signature = SignatureVisual.model_validate({"device": "none", **cfg.signature})
    return b


def _ours(source) -> dict:
    """Strings that identify our brand, mapped to the token they become."""
    handles = {source.visual.watermark} | {a.handle for a in source.accounts if a.handle}
    return {"name": source.name, "slug": source.slug, "tag": source.slug.replace("-", ""),
            "handles": sorted(h for h in handles if h), "urls": sorted(
                {u for u in [source.link_in_bio, *(p.get("url", "") for p in source.products),
                             *(a.url for a in source.affiliates)] if u}),
            "domains": sorted({urlsplit(u).netloc.removeprefix("www.") for u in
                               [source.link_in_bio, *(p.get("url", "") for p in source.products)] if u and
                               "example" not in u and "gumroad" not in u})}


def rewrite(text: str, source, cfg: ClientConfig, ours: dict) -> str:
    if not text:
        return text
    out = text
    if source.cta and cfg.cta:
        out = out.replace(source.cta, cfg.cta)
    for url in URL_RE.findall(out):
        clean = url.rstrip(".,;:!?")
        host = urlsplit(clean).netloc.removeprefix("www.")
        if clean in ours["urls"] or "/go/" in clean or host in ours["domains"]:
            out = out.replace(clean, cfg.website or "")
    out = re.sub(re.escape(source.name), cfg.name, out, flags=re.I)  # the name first: some handles are the name
    for h in ours["handles"]:
        if h.lower() != source.name.lower():
            out = re.sub(re.escape(h), cfg.handle or cfg.short or cfg.name, out, flags=re.I)
    out = re.sub(rf"#{re.escape(ours['tag'])}\b", "#" + (cfg.hashtag or re.sub(r"[^a-z0-9]", "", cfg.slug)), out, flags=re.I)
    tokens = {"CLIENT_NAME": cfg.name, "CLIENT_SHORT": cfg.short or cfg.name, "CLIENT_PHONE": cfg.phone,
              "CLIENT_WEBSITE": cfg.website, "CU_NAME": cfg.name, "CU_SHORT": cfg.short or cfg.name,
              "CU_PHONE": cfg.phone, "CU_WEBSITE": cfg.website, **cfg.tokens}
    for k, v in tokens.items():
        if v:
            out = out.replace("{{" + k + "}}", v)
    for a, b in cfg.replace.items():
        out = out.replace(a, b)
    out = re.sub(r"[ \t]+\n", "\n", re.sub(r"  +", " ", out))
    return out


def _walk(obj, fn):
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, list):
        return [_walk(x, fn) for x in obj]
    if isinstance(obj, dict):
        return {k: _walk(v, fn) for k, v in obj.items()}
    return obj


def leftovers(text: str, source, ours: dict) -> list[str]:
    bad = []
    low = text.lower()
    for needle in [source.name, *ours["handles"], *ours["domains"], f"#{ours['tag']}"]:
        if needle and needle.lower() in low:
            bad.append(needle)
    if re.search(rf"\b{re.escape(ours['tag'])}\b", low):
        bad.append(ours["tag"])
    bad += TOKEN_RE.findall(text)
    if "/go/" in text:
        bad.append("an affiliate /go/ link")
    return sorted(set(bad))


def _stamp_logo(img_path: Path, logo: Path) -> None:
    from PIL import Image

    from .media.util import save_png_and_jpeg
    base = Image.open(img_path).convert("RGBA")
    mark = Image.open(logo).convert("RGBA")
    h = max(24, int(base.height * 0.08))
    mark = mark.resize((max(1, int(mark.width * h / mark.height)), h), Image.LANCZOS)
    pad = int(base.height * 0.035)
    right = int(base.width * 0.07)  # clear of an edge stripe or corner signature
    base.alpha_composite(mark, (base.width - mark.width - right, base.height - mark.height - pad))
    save_png_and_jpeg(base, img_path)


def export(factory, brand_slug: str, client_path: Path, post_ids: list[int] | None = None,
           statuses: tuple[str, ...] = ("approved", "scheduled", "published"), limit: int = 50,
           render: bool = True, out_root: Path | None = None) -> dict:
    from .guardrails import script_text
    source = factory.brand(brand_slug)
    cfg = load_client(client_path)
    brand = client_brand(source, cfg)
    ours = _ours(source)
    if post_ids:
        posts = [p for p in (factory.db.get("posts", i) for i in post_ids) if p and p["brand"] == brand_slug]
    else:
        marks = ",".join("?" * len(statuses))
        posts = factory.db.query(f"SELECT * FROM posts WHERE brand = ? AND status IN ({marks}) ORDER BY id LIMIT ?",
                                 [brand_slug, *statuses, limit])
    posts = [p for p in posts if not (p.get("meta") or {}).get("challenge")] or posts
    if not posts:
        raise ValueError(f"No {'/'.join(statuses)} posts for {brand_slug} (or pass --posts)")
    batch = (out_root or factory.settings.output_dir / "whitelabel") / cfg.slug / date.today().isoformat()
    shutil.rmtree(batch, ignore_errors=True)
    (batch / "posts").mkdir(parents=True)
    logo = (Path(client_path).parent / cfg.logo) if cfg.logo else None
    if logo and not logo.is_file():
        raise FileNotFoundError(f"logo not found: {logo}")
    settings = copy.copy(factory.settings)
    settings.output_dir = batch
    fn = lambda s: rewrite(s, source, cfg, ours)  # noqa: E731
    manifest, sources, problems = [], [], {}
    for n, post in enumerate(posts, start=1):
        script = _walk(copy.deepcopy(post.get("script") or {}), fn)
        caption = fn(post.get("caption") or "")
        tags = [cfg.hashtag or re.sub(r"[^a-z0-9]", "", cfg.slug) if t.lower() == ours["tag"] else t
                for t in post.get("hashtags") or []]
        sub = f"posts/{n:02d}-{post['format']}"
        disclosure = brand.ai_disclosure
        full_caption = "\n\n".join(x for x in [caption, disclosure, " ".join("#" + t for t in tags),
                                                cfg.credit_line] if x)
        text = "\n".join([script_text(script), script.get("description", ""), full_caption,
                          json.dumps(script.get("segments") or [])])
        bad = leftovers(text, source, ours)
        if bad:
            problems[post["id"]] = bad
            continue
        d = batch / sub
        d.mkdir(parents=True, exist_ok=True)
        assets = {}
        if render:
            assets = factory_render(settings, brand, {"id": f"wl-{n}", "format": post["format"], "script": script,
                                                       "meta": {"output_subdir": sub}})
            if logo:
                for rel in [assets.get("thumbnail"), *(assets.get("slides") or [])[:1]]:
                    if rel:
                        _stamp_logo(batch / rel, logo)
        (d / "caption.txt").write_text(full_caption + "\n")
        (d / "script.md").write_text(f"# {script.get('title', '')}\n\n" + "\n\n".join(
            f"## {s.get('heading', '')}\n\n{s.get('narration', '')}\n\n_On screen: {s.get('on_screen_text', '')}_"
            for s in script.get("segments") or []) + "\n")
        claims = script.get("claims_to_verify") or []
        if claims or script.get("sources"):
            sources.append(f"## {n:02d}. {script.get('title', '')}\n" + "".join(f"- [ ] {c}\n" for c in claims)
                           + "".join(f"- source: {s}\n" for s in script.get("sources") or []))
        manifest.append({"n": n, "source_post": post["id"], "format": post["format"], "title": script.get("title", ""),
                         "dir": sub, "files": sorted(p.relative_to(batch).as_posix() for p in d.rglob("*") if p.is_file())})
    if problems:
        shutil.rmtree(batch, ignore_errors=True)
        raise ValueError("our brand is still in: " + "; ".join(f"post #{k}: {', '.join(v)}" for k, v in problems.items())
                         + ". Add a `replace` entry to the client config or edit the post.")
    if logo:
        shutil.copy2(logo, batch / f"logo{logo.suffix}")
    (batch / "sources.md").write_text(f"# Facts to check before {cfg.name} publishes\n\n" + ("\n".join(sources) or
                                      "No flagged claims; still read every post before it goes out.\n"))
    (batch / "manifest.json").write_text(json.dumps({"client": cfg.slug, "source_brand": brand_slug,
                                                     "date": date.today().isoformat(), "posts": manifest}, indent=2))
    footer = "\n".join(f"- {x}" for x in cfg.footer_lines)
    (batch / "README.md").write_text(
        f"# {cfg.name}: content batch {date.today().isoformat()}\n\n{len(manifest)} posts in posts/, each with its media, "
        "caption.txt (ready to paste) and script.md.\n\n"
        "- Read every post and check the claims in sources.md before publishing.\n"
        "- Keep the AI disclosure in each caption, and turn on each platform's AI label.\n"
        "- Post from your own accounts; nothing here posts automatically.\n"
        + (f"\nFooter lines to add where your compliance team requires them:\n{footer}\n" if footer else ""))
    zpath = batch.with_suffix(".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(batch.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(batch.parent).as_posix())
    factory.db.log("whitelabel.exported", "", None, {"client": cfg.slug, "posts": [m["source_post"] for m in manifest]})
    return {"dir": batch, "zip": zpath, "posts": manifest}


def factory_render(settings, brand, post: dict) -> dict:
    from .media import render_post
    return render_post(settings, brand, post)


def register(sub, factory_fn) -> None:
    s = sub.add_parser("whitelabel", help="rebrand a content batch for a client (B2B): their name, colours, links")
    s.add_argument("brand")
    s.add_argument("--client", required=True, type=Path, help="client config JSON")
    s.add_argument("--posts", default="", help="comma-separated post ids (default: approved/scheduled/published)")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--no-render", action="store_true", help="text only (captions and scripts)")

    def cmd(a):
        ids = [int(x) for x in a.posts.split(",") if x.strip()] or None
        res = export(factory_fn(a), a.brand, a.client, ids, limit=a.limit, render=not a.no_render)
        print(f"{len(res['posts'])} posts -> {res['dir']}\n{res['zip']}")
    s.set_defaults(func=cmd)
