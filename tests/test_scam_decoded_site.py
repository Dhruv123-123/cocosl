import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "sites" / "scam-decoded"


def build(tmp_path, monkeypatch, **env):
    monkeypatch.setenv("SITE_OUT", str(tmp_path / "public"))
    for k in ("SITE_URL", "URL", "EMAIL_PROVIDER", "EMAIL_FORM_ACTION", "SCAM_CHECKER_URL", "PLAUSIBLE_DOMAIN", "PLAUSIBLE_SRC"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    spec = importlib.util.spec_from_file_location("scam_site_build", ROOT / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build()
    return mod, tmp_path / "public"


def test_pages_and_internal_links_resolve(tmp_path, monkeypatch):
    mod, out = build(tmp_path, monkeypatch)
    for page in ["index.html", "free/index.html", "free/thanks/index.html", "kit/index.html", "checker/index.html",
                 "privacy/index.html", "disclosures/index.html", "404.html", "sitemap.xml", "robots.txt",
                 "downloads/the-scam-proof-checklist.pdf"]:
        assert (out / page).exists(), page
    for html in out.rglob("*.html"):
        text = html.read_text()
        assert "{{" not in text, html
        for href in re.findall(r'(?:href|src)="(/[^"#]*)"', text):
            target = out / href.lstrip("/")
            assert target.exists() or (target / "index.html").exists(), f"{html}: {href}"
    # placeholder checker link is hidden and reported
    assert "REPLACE_ME" not in (out / "index.html").read_text()
    assert any("scam_checker" in w for w in mod.WARNINGS)


def test_seven_email_sequence_sells_the_kit(tmp_path, monkeypatch):
    _, out = build(tmp_path, monkeypatch)
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert [e["order"] for e in seq] == list(range(1, 8))
    assert [e["send_on_day"] for e in seq] == sorted(e["send_on_day"] for e in seq)
    assert all(e["subject"] and e["text"] and e["html"] for e in seq)
    assert sum("/kit/" in e["html"] for e in seq) >= 3
    assert "the-scam-proof-checklist.pdf" in seq[0]["html"]
    for e in seq:
        assert "{{" not in e["html"] and "{{" not in e["text"]
        assert not re.search(r'href="/', e["html"]), "email links must be absolute"
        assert not re.search(r"\bguarantee", e["text"], re.I)
    assert "noindex" in (out / "emails" / "index.html").read_text()


def test_provider_switch_and_checker_url(tmp_path, monkeypatch):
    _, out = build(tmp_path, monkeypatch, EMAIL_PROVIDER="kit", EMAIL_FORM_ACTION="https://app.kit.com/forms/1/subscriptions",
                   SCAM_CHECKER_URL="https://checker.example.org/", SITE_URL="https://example.org/scam")
    home = (out / "index.html").read_text()
    assert 'action="https://app.kit.com/forms/1/subscriptions"' in home
    assert 'name="email_address"' in home and "data-netlify" not in home
    assert 'href="https://checker.example.org/"' in home
    assert 'href="/scam/kit/"' in home
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert "https://checker.example.org/" in "".join(e["html"] for e in seq)


def test_product_ladder_pages_and_upsells(tmp_path, monkeypatch):
    mod, out = build(tmp_path, monkeypatch)
    parents = (out / "parents" / "index.html").read_text()
    teams = (out / "teams" / "index.html").read_text()
    assert "$29" in parents and "KITPARENTS" in parents
    assert "$99" in teams and "One organization" in teams
    assert 'href="/parents/"' in (out / "kit" / "index.html").read_text()
    assert any("parents buy_url" in w for w in mod.WARNINGS)
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert "/parents/" in seq[-1]["html"] and "/teams/" in seq[-1]["html"]
    sitemap = (out / "sitemap.xml").read_text()
    assert "/parents/" in sitemap and "/teams/" in sitemap


def test_plausible_snippet_and_click_tags(tmp_path, monkeypatch):
    _, out = build(tmp_path, monkeypatch)
    pages = [p for p in out.rglob("*.html") if p.name != "email.html"]
    snippet = ('<script defer data-domain="scamdecoded.netlify.app" '
               'src="https://plausible.io/js/script.outbound-links.tagged-events.js"></script>')
    for p in pages:
        assert snippet in p.read_text(), p
    for slug in ("kit", "parents", "teams"):
        html = (out / slug / "index.html").read_text()
        buttons = re.findall(r'<a class="button([^"]*)" href="https://example\.gumroad', html)
        assert buttons and all("plausible-event-name=Product+Click" in b for b in buttons), slug
    # email bodies never carry scripts
    assert not any("<script" in p.read_text() for p in out.rglob("email.html"))
    _, out2 = build(tmp_path / "b", monkeypatch, PLAUSIBLE_DOMAIN="")
    assert "plausible.io" not in (out2 / "index.html").read_text()


def test_weekly_scam_alert_newsletter_six_issues(tmp_path, monkeypatch):
    from contentfactory.guardrails import ENGAGEMENT_BAIT, HYPE_PATTERNS, check_patterns
    mod, out = build(tmp_path, monkeypatch)
    src = ROOT / "content" / "newsletter"
    assert (src / "TEMPLATE.md").exists() and (src / "README.md").exists()
    issues = json.loads((out / "newsletter" / "issues.json").read_text())
    assert [i["issue"] for i in issues] == list(range(1, 17))
    dates = [i["send_date"] for i in issues]
    assert dates == sorted(dates) and len(set(dates)) == 16
    sections = ["## This week's scam", "## The tell", "## What to do", "## Quick hits", "## Your 5-minute job"]
    for meta in mod.newsletter_issues():
        body = meta["body_md"]
        assert all(s in body for s in sections), meta["slug"]
        assert "fictional example" in body and "guarantee" not in body.lower()
        assert check_patterns(body, HYPE_PATTERNS + ENGAGEMENT_BAIT, "n", "warn", "Hype").level == "ok", meta["slug"]
        if "/compare/" in body:  # affiliate mentions carry the disclosure
            assert "affiliate links" in body
    for i in issues:
        d = out / "newsletter" / i["slug"]
        html = (d / "email.html").read_text()
        assert 'href="/' not in html and "{{" not in html and mod.esc(i["preheader"]) in html
        assert (d / "email.txt").read_text().strip() and (d / "index.html").exists()
    sitemap = (out / "sitemap.xml").read_text()
    assert "/newsletter/irs-season/" in sitemap and "template" not in sitemap.lower()
    assert "988" in (out / "newsletter" / "valentines" / "email.txt").read_text()


def test_affiliate_comparison_page(tmp_path, monkeypatch):
    mod, out = build(tmp_path, monkeypatch)
    page = (out / "compare" / "index.html").read_text()
    for name in ["Aura", "LifeLock", "Bitwarden", "1Password"]:
        assert name in page
    for a in mod.CFG["affiliates"]:
        assert a["url"] in page
        assert f'class="button plausible-event-name=Affiliate+Click" rel="sponsored nofollow" href="{a["url"]}"' in page
        assert any(a["slug"] in w for w in mod.WARNINGS)  # placeholders are reported
    assert "Affiliate disclosure" in page and "free by law" in page
    assert page.index("Affiliate disclosure") < page.index("Affiliate+Click")
    assert "$" not in re.sub(r"<script.*?</script>", "", page, flags=re.S)  # no unverified prices
    assert "/compare/" in (out / "sitemap.xml").read_text()


def test_page_copy_lives_in_content_files(tmp_path, monkeypatch):
    src = (ROOT / "build.py").read_text()
    for phrase in ("What's inside", "Honest notes", "Who it's for", "Kit or guide?", "Our take", "free by law"):
        assert phrase not in src, f"copy still hard-coded in build.py: {phrase}"
    assert sorted(p.stem for p in (ROOT / "content" / "products").glob("*.md")) == ["kit", "parents", "seniors", "teams"]
    for name in ("index", "thanks", "checker", "compare"):
        assert (ROOT / "content" / "pages" / f"{name}.md").exists()
    _, out = build(tmp_path, monkeypatch)
    assert (out / "free" / "index.html").exists() and '<ul class="inside">' in (out / "kit" / "index.html").read_text()
    assert "<table class=\"compare\">" in (out / "compare" / "index.html").read_text()
    assert "/free/</loc>" not in (out / "sitemap.xml").read_text()
    assert 'noindex' in (out / "free" / "thanks" / "index.html").read_text()


def test_in_browser_scam_checker_and_explainers(tmp_path, monkeypatch):
    import shutil
    import subprocess
    mod, out = build(tmp_path, monkeypatch)
    page = (out / "checker" / "index.html").read_text()
    assert 'id="sd-checker"' in page and 'src="/checker.js"' in page and "window.SD_ARTICLES" in page
    js = (out / "checker.js").read_text()
    for banned in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "localStorage", "sessionStorage", "import("):
        assert banned not in js, banned
    articles = sorted((ROOT / "content" / "articles").glob("*.md"))
    assert len(articles) >= 16
    slugs = {p.stem.split("-", 1)[1] for p in articles}
    for slug in slugs:
        html = (out / "scams" / slug / "index.html").read_text()
        assert "The tell" in html and "What to do" in html and "ftc.gov" in html, slug
    index = (out / "scams" / "index.html").read_text()
    assert all(f"/scams/{s}/" in index for s in slugs)
    # every rule that points at an article points at one that exists
    referenced = set(re.findall(r'article: "([a-z-]+)"', js)) | {"lookalike-links"}
    assert referenced <= slugs, referenced - slugs
    if not shutil.which("node"):
        return
    cases = {
        "TOLL SERVICES NOTICE: You owe $4.15. Pay by 11:59 PM today to avoid a late fee: https://toll-paycenter-help.top/pay": ("high", "toll-texts"),
        "USPS: Your package is on hold due to an incomplete address. Update within 12 hours: usps-redelivery.com/track": ("high", "package-delivery-texts"),
        "Hi Mom, I dropped my phone, this is my new number. Can you pay a bill for me? Don't tell Dad": ("high", "family-emergency-scams"),
        "I sent you a verification code by mistake, can you read it back to me?": ("high", "verification-code-scams"),
        "Buy 4 Google Play gift cards and send me the numbers on the back. Keep this between us.": ("high", "gift-card-scams"),
        "Help families in need this holiday! Donate today by gift card or Zelle.": ("high", "fake-charity-scams"),
        "The buyer paid $450 but the payment is pending until you upgrade to a business account.": ("high", "online-marketplace-scams"),
        "Hey, are we still on for dinner at 7? I'll bring the salad.": ("none", None),
        "Your order has shipped. Track it at https://www.amazon.com/gp/your-account/order-history": ("none", None),
        "http://paypa1.com.secure-login.xyz/verify": ("high", "lookalike-links"),
    }
    script = ("const c=require(process.argv[1]);const cases=JSON.parse(process.argv[2]);"
              "console.log(JSON.stringify(Object.keys(cases).map(k=>{const r=c.analyze(k);return [r.level,r.articles];})));")
    res = json.loads(subprocess.run(["node", "-e", script, str(out / "checker.js"), json.dumps(cases)],
                                    capture_output=True, text=True, check=True).stdout)
    for (text, (level, article)), (got, arts) in zip(cases.items(), res):
        assert got == level, (text, got)
        if article:
            assert article in arts, (text, arts)


def test_holiday_parents_guide_opt_in_and_seniors_upsell(tmp_path, monkeypatch):
    mod, out = build(tmp_path, monkeypatch)
    cfg = json.loads((ROOT / "site.json").read_text())
    pdf = out / "downloads" / cfg["holiday_guide"]["file"]
    assert pdf.exists() and pdf.read_bytes()[:4] == b"%PDF" and pdf.read_bytes().count(b"/Type /Page\n") in (0, 4)
    guide = (ROOT / "lead-magnet" / "holiday-parents-guide.html").read_text()
    assert guide.count('class="page"') == 4 and "$7" in guide
    assert cfg["url"].split("//")[1] + "/seniors/" in guide  # the PDF's upsell URL matches the live site
    landing = (out / "holiday" / "index.html").read_text()
    assert 'action="/holiday/thanks/"' in landing and 'value="holiday-guide"' in landing
    thanks = (out / "holiday" / "thanks" / "index.html").read_text()
    assert f'/downloads/{cfg["holiday_guide"]["file"]}' in thanks and 'href="/seniors/"' in thanks and "noindex" in thanks
    seniors = (out / "seniors" / "index.html").read_text()
    assert "$7" in seniors and "etsy" in seniors
    assert "/holiday/thanks/" in (out / "robots.txt").read_text()
    assert "/holiday/</loc>" in (out / "sitemap.xml").read_text()
