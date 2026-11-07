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
    assert [i["issue"] for i in issues] == list(range(1, 28))
    dates = [i["send_date"] for i in issues]
    assert dates == sorted(dates) and len(set(dates)) == 27
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


def test_breach_checklist_page_is_static_and_links_official_sites():
    import re
    html = (ROOT / "public" / "breached" / "index.html").read_text()
    scripts = re.findall(r"<script[^>]*>", html)
    assert all("plausible.io" in s for s in scripts), "the breach page must not run its own scripts"
    assert "fetch(" not in html and "XMLHttpRequest" not in html
    for url in ("https://haveibeenpwned.com/", "https://www.identitytheft.gov/databreach",
                "https://www.annualcreditreport.com/", "get-an-identity-protection-pin"):
        assert url in html, url
    for bureau in ("equifax.com", "experian.com", "transunion.com"):
        assert bureau in html
    assert html.count('type="checkbox"') == 8
    assert '/breached/' in (ROOT / "public" / "checker" / "index.html").read_text()
    assert '/breached/' in (ROOT / "public" / "scams" / "index.html").read_text()


def test_how_we_make_money_lists_every_product_and_partner():
    import json
    cfg = json.loads((ROOT / "site.json").read_text())
    html = (ROOT / "public" / "how-we-make-money" / "index.html").read_text()
    for p in [cfg["product"], *cfg["ladder"]]:
        assert p["name"].replace("'", "&#x27;") in html and f"${p['price']:g}" in html, p["slug"]
    for a in cfg["affiliates"]:
        assert a["name"] in html, a["slug"]
    assert cfg["ai_disclosure"] in html and "never message you first" in html
    assert "/how-we-make-money/" in (ROOT / "public" / "index.html").read_text()
    assert "/how-we-make-money/" in (ROOT / "public" / "disclosures" / "index.html").read_text()


def test_breach_follow_up_explainer_and_checker_rule():
    import subprocess
    html = (ROOT / "public" / "scams" / "breach-follow-ups" / "index.html").read_text()
    assert "/breached/" in html and "haveibeenpwned.com" in html and "identitytheft.gov/databreach" in html
    assert "/scams/breach-follow-ups/" in (ROOT / "public" / "breached" / "index.html").read_text()
    js = ("const C=require(process.argv[1]);const r=C.analyze('You are owed $412 from the Acme data breach settlement. "
          "Pay a $25 processing fee to claim now.');console.log(r.level, r.articles.join(','))")
    out = subprocess.run(["node", "-e", js, str(ROOT / "static" / "checker.js")], capture_output=True, text=True).stdout
    assert out.startswith("high") and "breach-follow-ups" in out


def test_scam_of_the_week_alert_templates(tmp_path, monkeypatch):
    import sys
    mod, out = build(tmp_path, monkeypatch, SITE_URL="https://example.org")
    data = json.loads((out / "alerts" / "alerts.json").read_text())
    assert len(data) >= 3 and {a["severity"] for a in data} == set(mod.SEVERITY)
    for a in data:
        assert "{{" not in a["html"] and "[" not in a["subject"] and len(a["subject"]) <= 60
        hrefs = re.findall(r'href="([^"]+)"', a["html"])
        assert hrefs and all(h.startswith("https://") for h in hrefs), hrefs
        assert "https://example.org/checker/" in a["text"] and "fictional example" in a["text"]
        assert (out / "alerts" / a["slug"] / "index.html").exists()
        assert (out / "alerts" / a["slug"] / "email.txt").read_text() == a["text"]
    assert "Recent alerts" in (out / "alerts" / "index.html").read_text()
    # new_alert.py scaffolds the next numbered file; an unfilled one fails the build loudly
    spec = importlib.util.spec_from_file_location("new_alert", ROOT / "new_alert.py")
    na = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(na)
    tmp_alerts = tmp_path / "alerts"
    tmp_alerts.mkdir()
    (tmp_alerts / "_TEMPLATE.md").write_text((ROOT / "content" / "alerts" / "_TEMPLATE.md").read_text())
    (tmp_alerts / "04-x.md").write_text("---\n---\n")
    monkeypatch.setattr(na, "ALERTS", tmp_alerts)
    monkeypatch.setattr(sys, "argv", ["new_alert.py", "Fake jury duty calls", "--date", "2027-02-01", "--severity", "urgent"])
    dest = na.main()
    assert dest.name == "05-fake-jury-duty-calls.md"
    text = dest.read_text()
    assert "alert_date: 2027-02-01" in text and "severity: urgent" in text and "scam: Fake jury duty calls" in text
    import pytest
    content = tmp_path / "content"
    content.mkdir()
    (content / "alerts").symlink_to(tmp_alerts)
    monkeypatch.setattr(mod, "CONTENT", content)
    with pytest.raises(SystemExit, match="template text"):
        mod.alert_items()


def test_weekly_scam_of_the_week_email_reuses_alerts(tmp_path, monkeypatch):
    import shutil
    import sys
    import pytest
    mod, out = build(tmp_path, monkeypatch, SITE_URL="https://example.org")
    data = json.loads((out / "weekly" / "weekly.json").read_text())
    assert data, "no weekly email built"
    alerts = {a["slug"]: a for a in json.loads((out / "alerts" / "alerts.json").read_text())}
    for w in data:
        assert w["lead"] in alerts and "[" not in w["subject"] and len(w["subject"]) <= 70
        hrefs = re.findall(r'href="([^"]+)"', w["html"])
        assert hrefs and all(h.startswith("https://") for h in hrefs), hrefs
        assert "https://example.org/checker/" in w["text"] and "fictional" in w["text"] and "3 TELLS" in w["text"]
        assert (out / "weekly" / w["slug"] / "email.txt").read_text() == w["text"]
        assert not (out / "weekly" / w["slug"] / "index.html").exists()  # email only; alerts have the pages
    first = data[0]
    assert "ALSO GOING AROUND" in first["text"] and "COULD YOU SPOT IT?" in first["text"]
    assert "/weekly/" in (out / "robots.txt").read_text()
    # new_weekly.py leads with the newest unused alert and skips quiz questions about the same scam
    spec = importlib.util.spec_from_file_location("new_weekly", ROOT / "new_weekly.py")
    nw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nw)
    content = tmp_path / "content"
    (content / "alerts").mkdir(parents=True)
    for f in ["_TEMPLATE.md", *(p.name for p in (ROOT / "content" / "alerts").glob("0[123]-*.md"))]:
        shutil.copy(ROOT / "content" / "alerts" / f, content / "alerts" / f)
    shutil.copy(ROOT / "content" / "quiz.json", content / "quiz.json")
    (content / "weekly").mkdir()
    shutil.copy(ROOT / "content" / "weekly" / "_TEMPLATE.md", content / "weekly" / "_TEMPLATE.md")
    monkeypatch.setattr(nw, "CONTENT", content)
    monkeypatch.setattr(nw, "WEEKLY", content / "weekly")
    monkeypatch.setattr(sys, "argv", ["new_weekly.py", "--date", "2027-01-20"])
    dest = nw.main()
    text = dest.read_text()
    assert dest.name == "01-week-of-2027-01-20.md" and "lead: unpaid-toll-texts" in text
    assert "also: breach-fraud-team-calls, holiday-delivery-texts" in text and "quiz: 2" in text  # q1 is a toll text
    assert 'subject: Scam of the week: "Unpaid toll" texts are back' in text
    monkeypatch.setattr(mod, "CONTENT", content)
    with pytest.raises(SystemExit, match="template text in intro"):
        mod.weekly_items()
    dest.write_text(text.replace("lead: unpaid-toll-texts", "lead: no-such-alert").replace(
        text.split("intro: ")[1].split("\n")[0], "Toll texts are back."))
    with pytest.raises(SystemExit, match="no alert called no-such-alert"):
        mod.weekly_items()


def test_scam_alert_of_the_day_cards(tmp_path, monkeypatch):
    import datetime as dt
    import sys
    import pytest
    from PIL import Image
    monkeypatch.syspath_prepend(str(ROOT))
    spec = importlib.util.spec_from_file_location("make_alert_cards", ROOT / "make_alert_cards.py")
    mc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mc)
    monkeypatch.setattr(mc, "OUT", tmp_path)
    paths = mc.main()
    alerts = mc.B.alert_items()
    assert len(paths) == len(alerts) >= 52 and all(a["flag_list"] for a in alerts)
    days = [dt.date.fromisoformat(str(a["alert_date"])) for a in alerts]
    assert len(set(days)) == len(days), "two alerts on one day"
    d, missing = dt.date(2026, 11, 16), []
    while d <= dt.date(2027, 1, 29):  # every weekday has a card, except Dec 24-25 and Jan 1
        if d.weekday() < 5 and d.strftime("%m-%d") not in ("12-24", "12-25", "01-01") and d not in days:
            missing.append(d)
        d += dt.timedelta(days=1)
    assert not missing, missing
    assert all(d.weekday() < 5 for d in days)
    for a in alerts:
        assert len(a["flag_list"]) == 3 and all(f in a["example"] for f in a["flag_list"])
        assert any(h in a["source_url"] for h in ("ftc.gov", "ic3.gov", "fbi.gov", "bbb.org", "irs.gov"))
        cap = mc.caption(a)
        assert cap.count("#") <= 5 and "made up" in cap and "guarantee" not in cap.lower()
    for p in paths:
        assert Image.open(p).size == (1080, 1350)
    md = (tmp_path / "CARDS.md").read_text()
    assert "08:30" in md and md.count("### ") == len(paths)
    content = tmp_path / "content"
    (content / "alerts").mkdir(parents=True)
    src = next((ROOT / "content" / "alerts").glob("01-*.md")).read_text()
    (content / "alerts" / "01-x.md").write_text(src.replace("flags: ", "flags: not in the example | ", 1))
    monkeypatch.setattr(mc.B, "CONTENT", content)
    with pytest.raises(SystemExit, match="flags must be up to 3 exact phrases"):
        mc.B.alert_items()
    big = dict(alerts[0], tell_1=" ".join(["word"] * 400))
    with pytest.raises(SystemExit, match="too much text"):
        mc.card(big)


def test_new_alert_drafts_from_a_pasted_message(tmp_path, monkeypatch):
    import shutil
    import sys
    monkeypatch.syspath_prepend(str(ROOT))
    spec = importlib.util.spec_from_file_location("new_alert", ROOT / "new_alert.py")
    na = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(na)
    alerts = tmp_path / "alerts"
    shutil.copytree(ROOT / "content" / "alerts", alerts)
    monkeypatch.setattr(na, "ALERTS", alerts)
    import make_alert_cards
    monkeypatch.setattr(make_alert_cards, "OUT", tmp_path / "cards")
    msg = ("TOLL NOTICE: you owe $6.75 for unpaid tolls. Pay within 24 hours to avoid a $50 penalty: "
           "toll-paycenter-help.top/pay")
    monkeypatch.setattr(sys, "argv", ["new_alert.py", "--text", msg])
    dest = na.main()
    meta, _ = make_alert_cards.B.parse_front_matter(dest.read_text())
    assert meta["status"] == "draft" and meta["explainer"] == "toll-texts"
    assert meta["alert_date"] == "2027-02-01"  # next free weekday after the Jan 29 card
    flags = [f.strip() for f in meta["flags"].split("|")]
    assert len(flags) == 3 and all(f in msg for f in flags) and any(".top" in f for f in flags)
    assert meta["source_url"].startswith("https://") and meta["tell_1"] and meta["do_3"]
    assert list((tmp_path / "cards" / "drafts").glob("*.png"))
    # drafts never reach the site until someone deletes the status line
    monkeypatch.setattr(make_alert_cards.B, "CONTENT", tmp_path)
    assert all(a["slug"] != dest.stem.split("-", 1)[1] for a in make_alert_cards.B.alert_items())
    assert na.guess_type("Grandma it's me, I'm in jail, I need bail") == "family-emergency-scams"
    assert na.guess_type("Hey, are we still on for dinner?") == "lookalike-links"
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(na, "ALERTS", empty)
    assert na.next_free_weekday("2026-12-23") == "2026-12-28"  # skips Dec 24-25 and the weekend


def test_could_you_spot_it_quiz_and_share_cards(tmp_path, monkeypatch):
    import subprocess
    mod, out = build(tmp_path, monkeypatch, SITE_URL="https://example.org")
    q = json.loads((ROOT / "content" / "quiz.json").read_text())
    qs = q["questions"]
    assert len(qs) == 12 and {x["answer"] for x in qs} == {"scam", "legit"}
    assert sum(x["answer"] == "legit" for x in qs) >= 3
    for x in qs:
        assert x["tell"] and x["why"] and x["message"] and "guarantee" not in json.dumps(x).lower()
    page = (out / "quiz" / "index.html").read_text()
    assert "window.SD_QUIZ" in page and "/quiz.js" in page and "sd-quiz-after" in page
    assert '"site": "https://example.org"' in page
    for s in range(13):
        html = (out / "quiz" / "score" / str(s) / "index.html").read_text()
        assert f"https://example.org/img/quiz/score-{s}.png" in html and 'name="robots" content="noindex"' in html
        assert (ROOT / "static" / "img" / "quiz" / f"score-{s}.png").exists()
    assert "/quiz/score/" not in (out / "sitemap.xml").read_text() and "/quiz/" in (out / "sitemap.xml").read_text()
    js = ("const Q=require(process.argv[1]);const t=" + json.dumps(q["tiers"]) + ";"
          "console.log([12,11,10,9,7,6,0].map(s=>Q.tierFor(s,t).name).join('|'), Q.scoreUrl('https://x.org/',9))")
    res = subprocess.run(["node", "-e", js, str(ROOT / "static" / "quiz.js")], capture_output=True, text=True).stdout.strip()
    assert res == ("Scam-proof|Sharp eye|Sharp eye|Getting there|Getting there|Prime target|Prime target "
                   "https://x.org/quiz/score/9/")
    js_src = (ROOT / "static" / "quiz.js").read_text()
    assert "fetch(" not in js_src and "localStorage" not in js_src and "XMLHttpRequest" not in js_src
