import re

import pytest

from contentfactory import guardrails, hooks
from contentfactory.config import Settings, load_brand
from contentfactory.writer import write_script


@pytest.fixture
def lib():
    return hooks.load_library()


def test_library_has_30_unique_templates_with_consistent_slots(lib):
    assert len(lib.templates) == 30
    assert len({t.id for t in lib.templates}) == 30
    for t in lib.templates:
        assert set(t.slots) == set(hooks.SLOT_RE.findall(t.pattern)), t.id
        assert t.formats and t.topics and t.example and t.mechanic
        assert set(t.formats) <= {"short", "long", "carousel", "image"}


def test_templates_pass_the_content_guardrails(lib):
    patterns = guardrails.HYPE_PATTERNS + guardrails.ENGAGEMENT_BAIT + guardrails.TESTIMONIAL_PATTERNS
    for t in lib.templates:
        for text in (t.pattern, t.example):
            hits = [p for p in patterns if re.search(p, text, re.I)]
            assert not hits, (t.id, hits)


def test_render_fills_slots_and_reports_missing(lib):
    t = lib.get("stop-doing")
    assert t.render(common_habit="budgeting monthly", better_habit="budgeting by paycheck") == \
        "Stop budgeting monthly. Do budgeting by paycheck instead."
    with pytest.raises(KeyError):
        t.render(common_habit="x")


def test_suggest_matches_topic_and_format_deterministically(lib):
    a = lib.suggest("How to spot a fake bank fraud call", "short", k=4, seed="mms")
    assert a == lib.suggest("How to spot a fake bank fraud call", "short", k=4, seed="mms")
    assert len(a) == 4 and all("short" in t.formats for t in a)
    assert "scams" in a[0].topics
    assert len({t.mechanic for t in a}) == 4
    carousel = lib.suggest("Roth IRA basics", "carousel", k=3)
    assert all("carousel" in t.formats for t in carousel)


def test_prompt_block_only_for_matching_brands(home, monkeypatch):
    settings = Settings.load(home)
    money = load_brand(settings.brands_dir, "money-made-simple")
    history = load_brand(settings.brands_dir, "tiny-histories")
    block = hooks.prompt_block(money, "Freeze your credit for free", "short")
    assert block.startswith("Hook patterns") and block.count("\n- [") == 4
    assert hooks.prompt_block(history, "Why forks have four tines", "short") == ""
    monkeypatch.setenv("FACTORY_HOOK_LIBRARY", "0")
    assert hooks.prompt_block(money, "Freeze your credit for free", "short") == ""


def test_writer_prompt_includes_hook_patterns(home):
    settings = Settings.load(home)
    brand = load_brand(settings.brands_dir, "money-made-simple")
    seen = {}

    class SpyLLM:
        def structured(self, model, system, prompt, purpose, offline):
            seen["prompt"] = prompt
            return offline()

    write_script(SpyLLM(), brand, "Avalanche vs snowball with real math", "pay highest APR first", "short")
    assert "Hook patterns that work in this niche" in seen["prompt"]
