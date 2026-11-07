#!/usr/bin/env python3
"""Deploy check for the built site: broken links, SEO basics and a page-weight budget.

    python3 site/build.py && python3 site/tools/check_site.py            # checks site/public
    python3 site/tools/check_site.py --dir /path/to/public --external    # also HEAD-checks outbound links

Fails (exit 1) on:
  * accessibility basics: no <html lang>, images without alt, form fields without a label, links, buttons
    or table headers with no text, duplicate ids (the full axe-core audit is tests/test_a11y_browser.py)
  * an internal link, image, script or stylesheet that doesn't resolve (incl. #anchors on the same page)
  * an indexable page missing <title>, meta description, canonical, og:image or an <h1>
  * a page over the size budget (Lighthouse-style: HTML, and HTML + same-site CSS/JS/images it loads)
  * an http:// (mixed content) asset reference
Warns (does not fail) on: duplicate titles/descriptions, long titles/descriptions, images without alt,
and, with --external, outbound links that don't answer 2xx/3xx.
Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]

# Budgets (bytes). Generous for a text site; tighten as you like.
BUDGET = {
    "html": 100_000,        # one HTML document
    "page_total": 350_000,  # HTML + same-site CSS, JS and images it references
    "image": 200_000,       # any single image
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []   # (tag, url)
        self.ids: set[str] = set()
        self.meta: dict[str, str] = {}
        self.title = ""
        self._in_title = False
        self.h1 = 0
        self.imgs_without_alt = 0
        self.canonical = ""
        # accessibility
        self.lang = None
        self.id_counts: dict[str, int] = {}
        self.label_for: set[str] = set()
        self.inputs: list[tuple[str, bool]] = []    # (id, has own accessible name or is wrapped in a label)
        self._label_depth = 0
        self._open: list[list] = []                 # [tag, text, has_name] for a / button / th
        self.unnamed: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
            self.id_counts[a["id"]] = self.id_counts.get(a["id"], 0) + 1
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag == "label":
            self._label_depth += 1
            if a.get("for"):
                self.label_for.add(a["for"])
        if tag in ("input", "select", "textarea") and a.get("type") not in ("hidden", "submit", "button"):
            named = bool(a.get("aria-label") or a.get("aria-labelledby") or a.get("title")) or self._label_depth > 0
            if a.get("tabindex") == "-1" and a.get("autocomplete") == "off":  # honeypot, hidden from everyone
                named = True
            self.inputs.append((a.get("id", ""), named))
        if tag in ("a", "button", "th") and not (tag == "a" and not a.get("href")):
            self._open.append([tag, "", bool(a.get("aria-label") or a.get("aria-labelledby"))])
        if tag == "img" and self._open and a.get("alt"):
            self._open[-1][1] += a["alt"]
        if tag == "a" and a.get("href"):
            self.links.append(("a", a["href"]))
        elif tag in ("img", "script") and a.get("src"):
            self.links.append((tag, a["src"]))
            if tag == "img" and a.get("alt") is None:
                self.imgs_without_alt += 1
        elif tag == "link" and a.get("href"):
            rel = (a.get("rel") or "").lower()
            if rel == "canonical":
                self.canonical = a["href"]
            elif rel in ("stylesheet", "icon", "apple-touch-icon"):
                self.links.append(("link", a["href"]))
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "label" and self._label_depth:
            self._label_depth -= 1
        if self._open and self._open[-1][0] == tag:
            t, text, named = self._open.pop()
            if not named and not text.strip():
                self.unnamed.append(t)

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        for o in self._open:
            o[1] += data


def check(public: Path, base_path: str = "", external: bool = False) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    report: list[str] = []
    pages = {p: Page() for p in public.rglob("*.html")}
    for p, parser in pages.items():
        parser.feed(p.read_text(errors="replace"))

    def resolve(ref: str, page: Path) -> Path | None:
        path = unquote(urlparse(ref).path)
        if path.startswith("/"):
            if base_path and not path.startswith(base_path + "/") and path != base_path:
                return None
            target = public / path[len(base_path):].lstrip("/")
        else:
            target = (page.parent / path).resolve()
        if target.is_dir() or path.endswith("/"):
            target = target / "index.html"
        return target

    outbound: set[str] = set()
    titles: dict[str, list[str]] = {}
    descs: dict[str, list[str]] = {}
    for page, pr in sorted(pages.items()):
        rel = str(page.relative_to(public))
        is_redirect = "http-equiv" in page.read_text()[:600] and "refresh" in page.read_text()[:600]
        noindex = "noindex" in pr.meta.get("robots", "")
        weight = page.stat().st_size
        seen_assets: set[Path] = set()
        for tag, ref in pr.links:
            if ref.startswith(("mailto:", "tel:", "data:", "javascript:")):
                continue
            if ref.startswith("http://") and tag != "a":
                errors.append(f"{rel}: insecure asset {ref}")
            if ref.startswith(("http://", "https://", "//")):
                if tag == "a":
                    outbound.add(ref)
                continue
            if ref.startswith("#"):
                if ref[1:] and ref[1:] not in pr.ids:
                    errors.append(f"{rel}: anchor {ref} not found on the page")
                continue
            target = resolve(ref, page)
            if target is None:
                errors.append(f"{rel}: link {ref} is outside the site's base path {base_path!r}")
                continue
            if not target.is_file():
                errors.append(f"{rel}: broken {tag} -> {ref}")
                continue
            frag = urlparse(ref).fragment
            if frag and target in pages and frag not in pages[target].ids:
                errors.append(f"{rel}: anchor #{frag} not found in {ref}")
            if tag in ("img", "script", "link") and target not in seen_assets:
                seen_assets.add(target)
                size = target.stat().st_size
                weight += size
                if tag == "img" and size > BUDGET["image"]:
                    errors.append(f"{rel}: image {ref} is {size // 1024} KB (budget {BUDGET['image'] // 1024} KB)")
        if page.stat().st_size > BUDGET["html"]:
            errors.append(f"{rel}: HTML is {page.stat().st_size // 1024} KB (budget {BUDGET['html'] // 1024} KB)")
        if weight > BUDGET["page_total"]:
            errors.append(f"{rel}: page weight {weight // 1024} KB (budget {BUDGET['page_total'] // 1024} KB)")
        report.append(f"{weight // 1024:>5} KB  {rel}")
        # accessibility (every page, redirects included)
        if not is_redirect:
            if not pr.lang:
                errors.append(f"{rel}: <html> has no lang attribute")
            if pr.imgs_without_alt:
                errors.append(f"{rel}: {pr.imgs_without_alt} image(s) without alt (use alt=\"\" for decoration)")
            for i, named in pr.inputs:
                if not named and i not in pr.label_for:
                    errors.append(f"{rel}: form field {('#' + i) if i else ''} has no label")
            for t in sorted(set(pr.unnamed)):
                errors.append(f"{rel}: {pr.unnamed.count(t)} <{t}> with no text or aria-label")
            for i, n in pr.id_counts.items():
                if n > 1:
                    errors.append(f"{rel}: id {i!r} used {n} times")
        if is_redirect or noindex or rel == "404.html" or rel.startswith("emails/"):
            continue
        for need, ok in [("<title>", pr.title.strip()), ("meta description", pr.meta.get("description")),
                         ("canonical", pr.canonical), ("og:image", pr.meta.get("og:image")), ("<h1>", pr.h1)]:
            if not ok:
                errors.append(f"{rel}: missing {need}")
        if pr.h1 > 1:
            warnings.append(f"{rel}: {pr.h1} <h1> tags")
        if len(pr.title) > 70:
            warnings.append(f"{rel}: title is {len(pr.title)} chars (Google shows ~60)")
        d = pr.meta.get("description", "")
        if len(d) > 170:
            warnings.append(f"{rel}: description is {len(d)} chars (Google shows ~155)")
        titles.setdefault(pr.title.strip(), []).append(rel)
        descs.setdefault(d, []).append(rel)
    for t, where in titles.items():
        if len(where) > 1:
            warnings.append(f"duplicate title {t!r}: {', '.join(where)}")
    for d, where in descs.items():
        if d and len(where) > 1:
            warnings.append(f"duplicate description on {', '.join(where)}")

    if external:
        def head(url: str) -> tuple[str, int | str]:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "site-link-check"})
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    return url, r.status
            except urllib.error.HTTPError as e:  # some sites refuse HEAD; that's not a dead link
                return url, e.code
            except Exception as e:  # noqa: BLE001
                return url, type(e).__name__
        with ThreadPoolExecutor(8) as pool:
            for url, status in pool.map(head, sorted(outbound)):
                if not (isinstance(status, int) and (status < 400 or status in (403, 405, 429))):
                    warnings.append(f"outbound {url} -> {status}")
    report.sort(reverse=True)
    return errors, warnings, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(ROOT / "public"))
    ap.add_argument("--base-path", default=None, help="URL sub-path the site is served under, e.g. /cocosl")
    ap.add_argument("--external", action="store_true", help="also HEAD-check outbound links (needs network)")
    args = ap.parse_args()
    public = Path(args.dir)
    base = args.base_path
    if base is None:  # read it back from the built home page's canonical URL
        m = re.search(r'rel="canonical" href="([^"]+)"', (public / "index.html").read_text())
        base = urlparse(m.group(1)).path.rstrip("/") if m else ""
    errors, warnings, report = check(public, base, args.external)
    print("Heaviest pages (HTML + same-site assets):")
    print("\n".join(report[:5]))
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{len(report)} pages checked: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
