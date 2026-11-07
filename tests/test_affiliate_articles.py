"""Affiliate-keyword articles in site/content/blog: front matter, disclosures, aff: links, Compare links, guardrails."""
import json
import re
from pathlib import Path

import pytest

from contentfactory.guardrails import ENGAGEMENT_BAIT, HYPE_PATTERNS, TESTIMONIAL_PATTERNS

SITE = Path(__file__).resolve().parents[1] / "site"
BLOG = SITE / "content" / "blog"
# These live on the site PR's branch (#4) until it merges; keep in sync with its site.json > programs
# and site/content/{blog,compare}.
PROGRAMS = {"sofi", "cit", "ally", "marcus", "capital_one", "rocket_money", "ynab", "monarch", "copilot",
            "everydollar", "goodbudget", "discover", "chime", "self", "betterment", "wealthfront", "empower",
            "acorns", "schwab", "vanguard", "aura", "lifelock", "identity_guard", "experian", "nfcc"}
EXISTING = {"401k-match-explained", "budgeting-app-vs-spreadsheet", "debt-avalanche-vs-snowball",
            "expense-ratios-explained", "find-and-cancel-subscriptions", "how-credit-scores-work",
            "how-to-build-an-emergency-fund", "how-to-freeze-your-credit", "how-to-make-a-budget-you-will-keep",
            "how-to-start-investing-with-100-a-month", "is-my-savings-app-fdic-insured", "roth-vs-traditional-ira",
            "sinking-funds-explained"}
COMPARE = {"best-balance-transfer-cards", "best-bill-negotiation-services", "best-budgeting-apps",
           "best-credit-builder-cards", "best-high-yield-savings-accounts", "best-identity-theft-protection",
           "best-robo-advisors", "rocket-money-vs-ynab-vs-monarch"}
COMPARE_KEYWORDS = {"best high yield savings account", "best budgeting apps", "best robo advisors",
                    "best credit builder cards", "best identity theft protection", "best bill negotiation services",
                    "best balance transfer cards", "rocket money vs ynab vs monarch"}
INVESTING = {"betterment", "wealthfront", "acorns", "empower", "schwab", "vanguard"}


def _articles():
    out = []
    for p in sorted(BLOG.glob("*.md")):
        text = p.read_text()
        head, body = text.split("---\n", 2)[1:]
        meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
        out.append((p.stem, meta, body))
    return out


AFFILIATE = [a for a in _articles() if a[0] not in EXISTING]  # the site PR's own 13 have their own tests


def test_twenty_affiliate_articles():
    assert len(AFFILIATE) >= 20
    keywords = [m["keyword"] for _, m, _ in AFFILIATE]
    assert len(set(keywords)) == len(keywords), "one target keyword per article"
    assert not set(keywords) & COMPARE_KEYWORDS, "articles must not compete with a Compare page"
    linked = {c for _, _, b in AFFILIATE for c in re.findall(r"\(/compare/([\w-]+)/\)", b)}
    assert linked >= COMPARE - {"best-balance-transfer-cards"}, "each Compare page gets supporting articles"


@pytest.mark.parametrize("slug,meta,body", AFFILIATE, ids=[a[0] for a in AFFILIATE])
def test_article(slug, meta, body):
    for key in ("title", "seo_title", "description", "date", "pillar", "keyword", "sources"):
        assert meta.get(key), f"{slug}: missing {key}"
    assert meta["pillar"] in {"budgeting", "investing", "credit-and-debt", "money-tools"}
    aff = set(re.findall(r"\(aff:([\w-]+)\)", body))
    assert aff <= PROGRAMS, f"{slug}: unknown aff: program {aff - PROGRAMS} (add it to site.json > programs)"
    assert (meta.get("affiliate") == "yes") == bool(aff), f"{slug}: affiliate notice must match aff: links"
    assert "/go/" not in body
    assert len(meta["description"]) <= 200
    assert "## Common questions" in body and body.count("\n### ") >= 3  # FAQ structured data
    assert "{{signup}}" in body
    for ref in re.findall(r"\(/compare/([\w-]+)/\)", body):
        assert ref in COMPARE, f"{slug}: links to unknown compare page {ref}"
    known = EXISTING | {s for s, _, _ in _articles()}
    for ref in re.findall(r"\(/blog/([\w-]+)/\)", body):
        assert ref in known, f"{slug}: links to unknown article {ref}"
    for pats in (HYPE_PATTERNS, TESTIMONIAL_PATTERNS, ENGAGEMENT_BAIT):
        for pat in pats:
            assert not re.search(pat, body, re.I), f"{slug}: guardrail pattern {pat}"
    if aff & INVESTING or meta["pillar"] == "investing":
        assert meta.get("compliance") == "review", f"{slug}: investing links need compliance review"
        assert "loss of principal" in body


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
