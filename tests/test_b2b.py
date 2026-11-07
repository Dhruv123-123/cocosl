"""The B2B white-label packs in launch/b2b: issue data, the builder, deliver.py, outreach dates and paperwork.

Everything runs against a copy of launch/b2b in tmp_path, with images off (no node or Playwright needed),
so nothing in the repo is written to.
"""
import csv
import datetime as dt
import importlib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
B2B = REPO / "launch" / "b2b"
FIX = Path(__file__).parent / "fixtures" / "b2b"
PRODUCTS = sorted(p.parent for p in list(B2B.glob("*/product.json")) + list(B2B.glob("*/[a-z][a-z]/product.json")))


def _ids(paths):
    return [str(p.relative_to(B2B)) for p in paths]


@pytest.fixture
def b2b(tmp_path, monkeypatch):
    """A scratch copy of launch/b2b (without built output) with build, deliver, outreach_dates and paperwork
    imported from it, and the image renderer switched off."""
    root = tmp_path / "b2b"
    shutil.copytree(B2B, root, ignore=shutil.ignore_patterns("out", "clients", "dist", "node_modules", "*.zip", "*.pdf"))
    monkeypatch.syspath_prepend(str(root))
    mods = {}
    for name in ("build", "deliver", "outreach_dates", "paperwork"):
        sys.modules.pop(name, None)
        mods[name] = importlib.import_module(name)
    monkeypatch.setattr(mods["build"], "have_renderer", lambda: False)
    yield root, mods
    for name in mods:
        sys.modules.pop(name, None)


# ------------------------------------------------------------------ issue data

@pytest.mark.parametrize("pdir", PRODUCTS, ids=_ids(PRODUCTS))
def test_issues_are_well_formed(pdir):
    prod = json.loads((pdir / "product.json").read_text())
    issues = json.loads((pdir / "issues.json").read_text())["issues"]
    assert issues
    ids = [i["id"] for i in issues]
    assert len(ids) == len(set(ids)), "issue ids must be unique"
    assert [i["n"] for i in issues] == list(range(1, len(issues) + 1))
    for i in issues:
        send, due = dt.date.fromisoformat(i["send_date"]), dt.date.fromisoformat(i["deliver_by"])
        assert due < send, f"{i['id']}: deliver_by must come before send_date"
        assert len(i["sources"]) >= 2, f"{i['id']}: every issue needs at least 2 sources"
        for s in i["sources"]:
            assert s["name"] and re.match(r"https://", s["url"]), f"{i['id']}: bad source {s}"
        for key in ("subject", "headline", "explain", "tell", "steps", "job", "lobby", "social", "brief"):
            assert i.get(key), f"{i['id']}: missing {key}"
        tokens = set(re.findall(r"\{\{([A-Z_]+)\}\}", json.dumps(i)))
        assert tokens <= set(t.strip("{}") for t in prod["tokens"]) | {"UNSUBSCRIBE_LINK"}, \
            f"{i['id']}: uses tokens the product doesn't declare: {tokens}"


@pytest.mark.parametrize("pdir", PRODUCTS, ids=_ids(PRODUCTS))
def test_send_dates_are_in_order(pdir):
    dates = [i["send_date"] for i in json.loads((pdir / "issues.json").read_text())["issues"]]
    assert dates == sorted(dates)


def test_ncpw_package_matches_consumer_protection_week():
    issues = json.loads((B2B / "ncpw-sponsor/issues.json").read_text())["issues"]
    assert [i["send_date"] for i in issues] == [f"2027-03-0{d}" for d in range(1, 6)]
    assert all(i["deliver_by"] <= "2027-02-15" for i in issues)
    text = json.dumps(issues)
    assert "Never pay upfront for a refund or help with a refund" in text
    assert "will never call you to demand money" in text
    # client copy never names the sister brand (the internal "source" note may)
    client = [{k: v for k, v in i.items() if k != "source"} for i in issues]
    assert "Scam Decoded" not in json.dumps(client)


# ------------------------------------------------------------------ builder

def test_disclosure_default_and_override(b2b):
    _, m = b2b
    prod = {"disclaimer": "General information only.", "lang": "en"}
    assert m["build"].with_disclosure(prod, {})["disclaimer"].endswith("Drafted with AI help and fact-checked by a person.")
    assert m["build"].with_disclosure(prod, {"ai_disclosure": "  "})["disclaimer"].endswith("by a person.")
    assert m["build"].with_disclosure(prod, {"ai_disclosure": "Written with AI, checked by staff."})[
        "disclaimer"].endswith("checked by staff.")
    es = m["build"].with_disclosure({"disclaimer": "x", "lang": "es"}, {})["disclaimer"]
    assert "IA" in es


@pytest.mark.parametrize("product", ["credit-union-alert", "employer-wellness", "community-scam-watch",
                                     "freelancer-client-letter", "schools", "ncpw-sponsor"])
def test_build_sample_brand_without_images(b2b, product):
    root, m = b2b
    pdir = root / product
    prod = json.loads((pdir / "product.json").read_text())
    issues = json.loads((pdir / "issues.json").read_text())["issues"]
    pack = m["build"].build(pdir, prod, pdir / "brands/example.json", issues, False, False)
    m["build"].finish([pack])
    slug = json.loads((pdir / "brands/example.json").read_text())["slug"]
    folders = sorted((pdir / "out" / slug).iterdir())
    assert len(folders) == len(issues)
    for d in folders:
        for f in ("email.html", "email.txt", "social.txt", "sources.md"):
            assert (d / f).exists(), f"{d.name} is missing {f}"
        txt = (d / "email.txt").read_text()
        assert "fact-checked by a person" in txt or "verificado por una persona" in txt
        assert not re.search(r"\{\{[A-Z_]+\}\}", txt)
    assert (pdir / "out" / f"{slug}.zip").exists()


def test_placeholders_brand_needs_allow_tokens(b2b):
    root, m = b2b
    pdir = root / "credit-union-alert"
    prod = json.loads((pdir / "product.json").read_text())
    issues = json.loads((pdir / "issues.json").read_text())["issues"][:1]
    with pytest.raises(SystemExit, match="unfilled tokens"):
        m["build"].build(pdir, prod, pdir / "brands/placeholders.json", issues, False, False)
    pack = m["build"].build(pdir, prod, pdir / "brands/placeholders.json", issues, True, False)
    assert pack[0]["skip"]


def test_essentials_tier_has_no_staff_brief(b2b):
    root, m = b2b
    pdir = root / "credit-union-alert"
    brand = json.loads((FIX / "client.json").read_text())
    brand["tier"] = "essentials"
    path = root / "essentials.json"
    path.write_text(json.dumps(brand))
    prod = json.loads((pdir / "product.json").read_text())
    issues = json.loads((pdir / "issues.json").read_text())["issues"][:1]
    m["build"].build(pdir, prod, path, issues, False, False)
    d = next((pdir / "out" / brand["slug"]).iterdir())
    assert (d / "email.txt").exists() and not (d / "brief.txt").exists()


def test_master_markdown_shows_slots(b2b):
    root, m = b2b
    pdir = root / "ncpw-sponsor"
    prod = m["build"].with_disclosure(json.loads((pdir / "product.json").read_text()), {})
    issue = json.loads((pdir / "issues.json").read_text())["issues"][0]
    md = m["build"].master_md(issue, prod)
    assert md.startswith("# Day 1: ")
    assert "{{CU_PHONE}}" in md and "## Sources" in md


def test_products_lists_every_folder(b2b):
    root, m = b2b
    names = {str(p.relative_to(root)) for p in m["build"].products()}
    assert {"credit-union-alert", "schools", "ncpw-sponsor", "credit-union-alert/es"} <= names


# ------------------------------------------------------------------ deliver.py

def _deliver(monkeypatch, m, *argv):
    monkeypatch.setattr(sys, "argv", ["deliver.py", *argv])
    m["deliver"].main()


def test_deliver_with_client_file(b2b, monkeypatch, capsys):
    root, m = b2b
    _deliver(monkeypatch, m, "credit-union-alert", "--client", str(FIX / "client.json"), "--month", "2027-02")
    zpath = root / "credit-union-alert/out/deliveries/test-river-cu-2027-02.zip"
    assert zpath.exists()
    issues = [i for i in json.loads((root / "credit-union-alert/issues.json").read_text())["issues"]
              if i["send_date"].startswith("2027-02")]
    folders = list((root / "credit-union-alert/out/deliveries/test-river-cu-2027-02").iterdir())
    assert len(folders) == len(issues) >= 4
    text = (folders[0] / "email.txt").read_text()
    assert "(406) 200-3000" in text and "555" not in text
    assert f"{len(issues)} issue(s) for Test River Credit Union" in capsys.readouterr().out


def test_deliver_quick_start_writes_client_file(b2b, monkeypatch):
    root, m = b2b
    _deliver(monkeypatch, m, "ncpw-sponsor", "--month", "2027-03", "--name", "Big Sky Credit Union",
             "--short", "Big Sky CU", "--set", "CU_PHONE=(406) 123-4567", "--set", "CU_WEBSITE=https://bigsky.test",
             "--promise", "Big Sky CU will never ask for your PIN.", "--footer", "Big Sky CU, Billings, MT")
    brand = json.loads((root / "ncpw-sponsor/clients/big-sky-cu.json").read_text())
    assert brand["tokens"]["CU_NAME"] == "Big Sky Credit Union" and brand["tokens"]["CU_SHORT"] == "Big Sky CU"
    assert brand["initials"] == "BSC"
    assert len(list((root / "ncpw-sponsor/out/deliveries/big-sky-cu-2027-03").iterdir())) == 5


def test_deliver_refuses_sample_details(b2b, monkeypatch):
    root, m = b2b
    # quick start without replacing the sample phone number
    with pytest.raises(SystemExit, match="sample details"):
        _deliver(monkeypatch, m, "credit-union-alert", "--month", "2027-02", "--name", "River CU")


@pytest.mark.parametrize("text,bad", [("(555) 010-0142", True), ("555-0199", True), ("https://www.example.org", True),
                                      ("Sample Community CU", True), ("(406) 555-1234", False),
                                      ("https://samplecu.org", False)])
def test_fictional_pattern(b2b, text, bad):
    _, m = b2b
    assert bool(m["deliver"].FICTIONAL.search(text)) is bad


def test_deliver_month_with_no_issues(b2b, monkeypatch):
    _, m = b2b
    with pytest.raises(SystemExit, match="no issues for 2030-01"):
        _deliver(monkeypatch, m, "credit-union-alert", "--client", str(FIX / "client.json"), "--month", "2030-01")
    with pytest.raises(SystemExit, match="--month must look like"):
        _deliver(monkeypatch, m, "credit-union-alert", "--client", str(FIX / "client.json"), "--month", "Feb")


def test_slugify(b2b):
    _, m = b2b
    assert m["deliver"].slugify("Big Sky Credit Union, Inc.") == "big-sky-credit-union-inc"


# ------------------------------------------------------------------ outreach dates

def test_outreach_dates_respect_shared_cap(b2b, monkeypatch):
    root, m = b2b
    od = m["outreach_dates"]
    cal = FIX / "ad_studio_calendar.md"
    monkeypatch.setattr(sys, "argv", ["outreach_dates.py", str(cal)])
    od.main()
    rows = list(csv.DictReader(open(root / "OUTREACH_DATES.csv", newline="")))
    assert len(rows) == len(od.prospects())
    used, new, _, _ = od.load_calendar(cal)
    total, firsts = dict(used), dict(new)
    b2b_total, b2b_new = {}, {}
    for r in rows:
        for key in ("email_1", "follow_up_1", "follow_up_2"):
            d = dt.date.fromisoformat(r[key])
            assert d.weekday() < 5 and d not in od.HOLIDAYS, f"{r['prospect']} {key} on {d}"
            total[d] = total.get(d, 0) + 1
            b2b_total[d] = b2b_total.get(d, 0) + 1
        d1 = dt.date.fromisoformat(r["email_1"])
        firsts[d1] = firsts.get(d1, 0) + 1
        b2b_new[d1] = b2b_new.get(d1, 0) + 1
        assert r["email_1"] < r["follow_up_1"] < r["follow_up_2"]
        if r["product"] == "freelancer-client-letter":
            for key in ("email_1", "follow_up_1", "follow_up_2"):
                assert not (od.TAX_BLACKOUT[0] <= dt.date.fromisoformat(r[key]) <= od.TAX_BLACKOUT[1])
    assert max(total.values()) <= od.CAP
    assert max(firsts.values()) <= od.NEW_CAP
    for d, n in b2b_total.items():
        if d >= od.SHARE_FROM:
            assert n <= od.B2B_CAP and b2b_new.get(d, 0) <= od.B2B_NEW
    # accounting firms go first from Dec 1
    first_dec = min(rows, key=lambda r: (r["email_1"], r["product"] != "freelancer-client-letter"))
    assert first_dec["product"] == "freelancer-client-letter"
    assert (root / "OUTREACH_DATES.md").exists()


def test_outreach_calendar_parser(b2b):
    _, m = b2b
    used, new, start, end = m["outreach_dates"].load_calendar(FIX / "ad_studio_calendar.md")
    assert start == dt.date(2026, 11, 10) and end == dt.date(2026, 12, 31)
    assert used[dt.date(2026, 11, 10)] == 5 and new[dt.date(2026, 11, 10)] == 3
    assert used[dt.date(2026, 12, 1)] == 6


# ------------------------------------------------------------------ paperwork

def test_paperwork_writes_agreement_and_invoice(b2b, monkeypatch):
    root, m = b2b
    for f in root.glob("*/onboarding/services-agreement.html"):
        f.unlink()
    m["paperwork"].main()
    for product in m["paperwork"].OFFERS:
        agreement = (root / product / "onboarding/services-agreement.html").read_text()
        invoice = (root / product / "onboarding/invoice.html").read_text()
        assert "lawyer" in agreement.lower()
        assert "{{PAYMENT_LINK" in invoice or "PAYMENT" in invoice
        assert not re.search(r"\{[a-z_]+\}", agreement), "an unformatted template field was left in"
