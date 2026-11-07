import pytest

from contentfactory.numbercheck import as_check, check_script, compute, parse

pytest.importorskip("numpy_financial")


@pytest.mark.parametrize("text,kind,status", [
    ("A $25,000 car loan at 7.5% for 5 years costs about $501 a month.", "loan_payment", "ok"),
    ("A $25,000 car loan at 7.5% for 5 years costs $450 a month.", "loan_payment", "mismatch"),
    ("Pay $200 a month on $5,000 at 22% APR and it's gone in 34 months.", "payoff_months", "ok"),
    ("Pay $200 a month on $5,000 at 22% APR and it's gone in 24 months.", "payoff_months", "mismatch"),
    ("$4,000 at 24% APR, $275/month: about 18 months and ~$775 interest.", "payoff_months", "ok"),
    ("On a $300,000 mortgage at 6.5% over 30 years you pay $382,633 in interest.", "total_interest", "ok"),
    ("Invest $300 a month at 7% for 30 years and you'd have about $366,000.", "future_value", "ok"),
    ("Put $10,000 in at 8% for 10 years and it grows to $30,000.", "future_value", "mismatch"),
])
def test_parse_and_recompute(text, kind, status):
    f = compute(parse(text))
    assert (f.kind, f.status) == (kind, status), f


def test_plain_sentences_are_ignored():
    for t in ["Save $50 a month.", "Rates are around 4.5% right now.", "The $12 budget kit has 5 sheets."]:
        assert parse(t) is None


def test_minimum_payment_never_pays_off():
    f = compute(parse("Pay $50 a month on $5,000 at 24% APR and it's gone in 200 months."))
    assert f.status == "mismatch" and "never" in f.note


def test_declared_mismatch_blocks_parsed_mismatch_warns():
    declared = {"segments": [], "calcs": [{"kind": "loan_payment", "principal": 25000, "rate": 7.5, "years": 5,
                                            "claimed": 450}]}
    assert as_check(check_script(declared)).level == "block"
    parsed = {"segments": [{"narration": "A $25,000 car loan at 7.5% for 5 years costs $450 a month."}]}
    c = as_check(check_script(parsed))
    assert c.level == "warn" and "$500.95" in c.message
    assert as_check(check_script({"segments": [{"narration": "Hello."}]})) is None


def test_federal_tax_against_taxcalc():
    pytest.importorskip("taxcalc")
    ok = compute(parse("Federal income tax on a $75,000 salary (single, 2026) is about $7,670."))
    assert ok.status == "ok", ok
    bad = compute(parse("Federal income tax on a $75,000 salary (single, 2026) is $12,000."))
    assert bad.status == "mismatch"


def test_runs_in_review_checks(factory):
    from contentfactory.guardrails import run_content_checks
    post = {"id": 0, "format": "short", "caption": "", "script": {"title": "t", "segments": [
        {"narration": "A $25,000 car loan at 7.5% for 5 years costs about $501 a month."}]}}
    checks = {c.name: c for c in run_content_checks(factory.db, factory.brand("money-made-simple"), post)}
    assert checks["number_check"].level == "ok"
