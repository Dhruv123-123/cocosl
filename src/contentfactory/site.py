"""Bundle every public page into one folder you can drag onto Netlify, Cloudflare Pages or GitHub Pages.

    factory site export --out site/ --base-url https://factory.example.com

Layout:
    index.html                    tiny index of what's inside (noindex)
    <brand>/index.html            link-in-bio page
    <brand>/<product>.html        one sales page per product with a checkout URL
    studio/index.html             the ad studio website (launch/ugc-service/index.html)
    studio/portfolio/...          sample-ads portfolio (posters; copy videos/ next to it)

Sign-up forms and /go/ affiliate links point at --base-url (your running
factory, PUBLIC_BASE_URL), so double opt-in, click tracking and webhooks keep
working while the pages themselves sit on free static hosting.
"""
from __future__ import annotations

import html
import shutil
from pathlib import Path

from .pipeline import Factory

REPO_ROOT = Path(__file__).resolve().parents[2]


def _launch_dir(factory: Factory) -> Path | None:
    for cand in (Path.cwd() / "launch", REPO_ROOT / "launch"):
        if cand.is_dir():
            return cand
    return None


def export_site(factory: Factory, out_dir: str | Path, *, base_url: str | None = None,
                brands: list[str] | None = None) -> dict:
    from .funnel.linkpage import build_link_page
    from .funnel.salespage import build_all_sales_pages

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pages: list[str] = []
    for slug, brand in factory.brands().items():
        if brands and slug not in brands:
            continue
        dest = out / slug
        dest.mkdir(exist_ok=True)
        link = build_link_page(factory.settings, brand, factory.db, base_url=base_url, llm=factory.llm)
        shutil.copy2(link, dest / "index.html")
        pages.append(f"{slug}/index.html")
        for page in build_all_sales_pages(factory.settings, factory.db, brand, base_url=base_url):
            shutil.copy2(page, dest / page.name)
            pages.append(f"{slug}/{page.name}")
        for extra in link.parent.iterdir():  # lead magnet etc. built next to the link page
            if extra.is_file() and extra.suffix in {".pdf", ".png", ".jpg", ".css"} and not (dest / extra.name).exists():
                shutil.copy2(extra, dest / extra.name)

    launch = _launch_dir(factory)
    if launch and (launch / "ugc-service" / "index.html").exists():
        studio = out / "studio"
        studio.mkdir(exist_ok=True)
        shutil.copy2(launch / "ugc-service" / "index.html", studio / "index.html")
        pages.append("studio/index.html")
        port = launch / "ugc-service" / "portfolio"
        if port.is_dir():
            shutil.copytree(port, studio / "portfolio", dirs_exist_ok=True)
            pages.append("studio/portfolio/portfolio.html")

    items = "".join(f'<li><a href="{html.escape(p)}">{html.escape(p)}</a></li>' for p in pages)
    (out / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex"><title>Pages</title>'
        '<body style="font:16px system-ui;max-width:640px;margin:40px auto;padding:0 16px">'
        f"<h1>Published pages</h1><ul>{items}</ul></body>")
    (out / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
                                  "/index.html\n  X-Robots-Tag: noindex\n")
    factory.db.log("site.export", "", None, {"out": str(out), "pages": len(pages)})
    return {"out": str(out), "pages": pages}


def register(sub, factory_fn) -> None:
    s = sub.add_parser("site", help="export all public pages as a static site")
    ssub = s.add_subparsers(dest="site_cmd", required=True)
    e = ssub.add_parser("export", help="link pages, sales pages, studio site and portfolio in one folder")
    e.add_argument("--out", default="site")
    e.add_argument("--base-url", help="your running factory (defaults to PUBLIC_BASE_URL)")
    e.add_argument("--brand", action="append", help="limit to these brands (repeatable)")

    def run(a):
        res = export_site(factory_fn(a), a.out, base_url=a.base_url, brands=a.brand)
        print(f"{len(res['pages'])} pages in {res['out']}/")
        for p in res["pages"]:
            print(f"  {p}")
    e.set_defaults(func=run)
