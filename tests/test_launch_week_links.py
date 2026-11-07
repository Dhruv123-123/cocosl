"""Every page that MMS's 14-day LAUNCH_WEEK.md, its link-in-bio and its first Pinterest pins (PR #5) point to is
live on launch Day 1 (Mon Nov 16 2026) and carries the right opt-in; the site's own pin schedule starts in week 3."""
import csv
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

SITE = Path(__file__).resolve().parents[1] / "site"
DAY1 = "2026-11-16"
# LAUNCH_WEEK.md "start with these site pins" + the articles PR #5's channel config links by keyword.
ARTICLES = ["how-to-freeze-your-credit", "401k-match-explained", "how-to-build-an-emergency-fund",
            "sinking-funds-explained", "find-and-cancel-subscriptions", "how-to-start-investing-with-100-a-month",
            "expense-ratios-explained", "roth-vs-traditional-ira", "is-my-savings-app-fdic-insured",
            "debt-avalanche-vs-snowball", "how-credit-scores-work", "budgeting-app-vs-spreadsheet",
            "how-to-make-a-budget-you-will-keep"]


def _build(tmp_path):
    out = tmp_path / "public"
    e = {**os.environ, "SITE_OUT": str(out), "SITE_URL": "https://moneymadesimple.netlify.app", "BUILD_DATE": DAY1}
    for k in ("URL", "BLOG_SHOW_SCHEDULED"):
        e.pop(k, None)
    subprocess.run([sys.executable, str(SITE / "build.py")], check=True, env=e, capture_output=True)
    return out


def _sources(html):
    return re.findall(r'name="source" value="([^"]+)"', html)


def test_launch_week_pages_are_live_on_day_one_with_an_opt_in(tmp_path):
    out = _build(tmp_path)
    for slug in ARTICLES:
        page = out / "blog" / slug / "index.html"
        assert page.exists(), f"/blog/{slug}/ isn't live on launch Day 1"
        assert any(s.startswith(("blog-", "plan-")) for s in _sources(page.read_text())), f"/blog/{slug}/ has no signup"
    assert "free-page" in _sources((out / "free" / "index.html").read_text())
    assert "quiz" in _sources((out / "quiz" / "index.html").read_text())
    product = (out / "products" / "the-20-minute-budget" / "index.html").read_text()
    assert "gumroad" in product.lower() or "buy" in product.lower()
    assert (out / "compare" / "best-high-yield-savings-accounts" / "index.html").exists()

    # Link in bio: the free reset signup, then the 20-Minute Budget, then the HYSA comparison, in that order.
    bio = (out / "links" / "index.html").read_text()
    i_form = bio.index('value="link-in-bio"')
    i_prod = bio.index('href="/products/the-20-minute-budget/"')
    i_hysa = bio.index('href="/compare/best-high-yield-savings-accounts/"')
    assert i_form < i_prod < i_hysa < bio.index('href="/quiz/"')


def test_site_pin_schedule_starts_week_three_with_the_launch_pins():
    rows = [r for r in csv.DictReader((SITE / "pins" / "schedule.csv").open()) if r["date"]]
    assert rows[0]["date"] == "2026-11-30"
    lead = ["/quiz/"] + [f"/blog/{s}/" for s in ARTICLES[:7]]
    assert [urlparse(r["link"]).path for r in rows[:8]] == lead
    last = {}
    for r in rows:
        path, d = urlparse(r["link"]).path, date.fromisoformat(r["date"])
        assert path not in last or (d - last[path]).days >= 7, f"{path} pinned twice within 7 days"
        last[path] = d
        assert not r["page_live"] or r["page_live"] <= r["date"], f"{r['file']} pinned before its page is live"
