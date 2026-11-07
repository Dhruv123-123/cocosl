"""Write site/static/go/<slug>/index.html redirect pages from site/go-links.json.

Articles link to /go/<slug>/ (the site build marks those links rel="sponsored"). Each page sends the
reader to the program's tracking link once you have one ('affiliate_url'), otherwise to the company's
official page ('url'). Re-run after editing go-links.json:  python3 site/tools/make_go_links.py
"""
import html
import json
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer-when-downgrade">
<meta http-equiv="refresh" content="0; url={href}">
<title>Going to {name}</title>
<link rel="canonical" href="{href}">
</head><body style="font-family:system-ui,sans-serif;max-width:32rem;margin:3rem auto;padding:0 1rem">
<p>Taking you to <a href="{href}" rel="sponsored noopener">{name}</a>…</p>
<p style="color:#666;font-size:.9rem">Some of our outbound links are affiliate links: if you sign up we may earn a
commission at no extra cost to you. It never changes what we write.</p>
</body></html>
"""


def build(site: Path = SITE) -> list[str]:
    links = json.loads((site / "go-links.json").read_text())["links"]
    out = site / "static" / "go"
    if out.exists():
        shutil.rmtree(out)
    for slug, link in sorted(links.items()):
        href = link.get("affiliate_url") or link["url"]
        assert href.startswith("https://"), f"{slug}: link must be https"
        d = out / slug
        d.mkdir(parents=True)
        (d / "index.html").write_text(PAGE.format(href=html.escape(href), name=html.escape(link["name"])))
    return sorted(links)


if __name__ == "__main__":
    print(f"wrote {len(build())} /go/ pages")
