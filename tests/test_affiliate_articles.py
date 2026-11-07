"""Affiliate-keyword articles in site/content/blog: front matter, disclosures, /go/ links, guardrails."""
import json
import re
from pathlib import Path

import pytest

from contentfactory.guardrails import ENGAGEMENT_BAIT, HYPE_PATTERNS, TESTIMONIAL_PATTERNS

SITE = Path(__file__).resolve().parents[1] / "site"
BLOG = SITE / "content" / "blog"
GO = json.loads((SITE / "go-links.json").read_text())["links"]
# Articles from the site PR that these link to; they live on another branch until it merges.
EXISTING = {"401k-match-explained", "budgeting-app-vs-spreadsheet", "debt-avalanche-vs-snowball",
            "expense-ratios-explained", "find-and-cancel-subscriptions", "how-credit-scores-work",
            "how-to-build-an-emergency-fund", "how-to-freeze-your-credit", "how-to-make-a-budget-you-will-keep",
            "how-to-start-investing-with-100-a-month", "is-my-savings-app-fdic-insured", "roth-vs-traditional-ira",
            "sinking-funds-explained"}
INVESTING_GO = {"betterment", "wealthfront", "acorns", "empower"}


def _articles():
    out = []
    for p in sorted(BLOG.glob("*.md")):
        text = p.read_text()
        head, body = text.split("---\n", 2)[1:]
        meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
        out.append((p.stem, meta, body))
    return out


AFFILIATE = [a for a in _articles() if "/go/" in a[2]]


def test_twenty_affiliate_articles():
    assert len(AFFILIATE) >= 20
    keywords = [m["keyword"] for _, m, _ in AFFILIATE]
    assert len(set(keywords)) == len(keywords), "one target keyword per article"


@pytest.mark.parametrize("slug,meta,body", AFFILIATE, ids=[a[0] for a in AFFILIATE])
def test_article(slug, meta, body):
    for key in ("title", "seo_title", "description", "date", "pillar", "keyword", "sources"):
        assert meta.get(key), f"{slug}: missing {key}"
    assert meta["pillar"] in {"budgeting", "investing", "credit-and-debt", "money-tools"}
    assert meta.get("affiliate") == "yes", f"{slug}: links to /go/ so must show the affiliate notice"
    assert len(meta["description"]) <= 200
    assert "## Common questions" in body and body.count("\n### ") >= 3  # FAQ structured data
    assert "{{signup}}" in body
    for go in re.findall(r"\(/go/([\w-]+)/\)", body):
        assert go in GO, f"{slug}: /go/{go}/ missing from site/go-links.json"
    known = EXISTING | {s for s, _, _ in _articles()}
    for ref in re.findall(r"\(/blog/([\w-]+)/\)", body):
        assert ref in known, f"{slug}: links to unknown article {ref}"
    for pats in (HYPE_PATTERNS, TESTIMONIAL_PATTERNS, ENGAGEMENT_BAIT):
        for pat in pats:
            assert not re.search(pat, body, re.I), f"{slug}: guardrail pattern {pat}"
    if set(re.findall(r"/go/([\w-]+)/", body)) & INVESTING_GO or meta["pillar"] == "investing":
        assert meta.get("compliance") == "review", f"{slug}: investing links need compliance review"
        assert "loss of principal" in body


def test_go_pages_match_registry(tmp_path):
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("make_go_links", SITE / "tools" / "make_go_links.py")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    (tmp_path / "go-links.json").write_text((SITE / "go-links.json").read_text())
    assert mod.build(tmp_path) == sorted(GO)
    for slug, link in GO.items():
        page = (tmp_path / "static" / "go" / slug / "index.html").read_text()
        committed = (SITE / "static" / "go" / slug / "index.html").read_text()
        assert page == committed, f"re-run site/tools/make_go_links.py ({slug})"
        assert "noindex" in page and (link.get("affiliate_url") or link["url"]) in page


def test_affiliate_application_kit(tmp_path):
    import subprocess
    import sys
    kit = Path(__file__).resolve().parents[1] / "launch" / "affiliates" / "kit.py"
    subprocess.run([sys.executable, str(kit), "--out", str(tmp_path)], check=True, capture_output=True)
    md = (tmp_path / "APPLICATIONS.md").read_text()
    for name in ("SoFi", "CIT Bank", "Rocket Money", "Aura", "FreshBooks", "Gusto", "Impact", "CJ Affiliate"):
        assert f"### {name}" in md
    rows = (tmp_path / "applications.csv").read_text().splitlines()
    assert len(rows) > 40 and all(",not applied," in r for r in rows[1:])
    assert (tmp_path / "applications.html").read_text().count("<details>") > 30
    for go in re.findall(r",(\w[\w-]*),$", "\n".join(rows[1:]), re.M):
        assert go in GO
