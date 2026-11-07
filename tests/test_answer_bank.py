import json
import re
from pathlib import Path

from contentfactory.guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS

BANK = Path(__file__).resolve().parents[1] / "launch" / "money-made-simple" / "community" / "answer-bank.json"


def test_answer_bank_is_link_free_and_safe():
    items = json.loads(BANK.read_text())
    assert len(items) == 40
    assert len({i["id"] for i in items}) == 40
    assert len({i["question"].lower() for i in items}) == 40
    for it in items:
        text = it["answer"]
        assert it["where"] and it["topic"]
        assert 120 <= len(text.split()) <= 380, it["id"]
        # communities ban links, Quora bans affiliate links: no URLs and no pointers to our own site
        assert not re.search(r"https?://|www\.|\]\(|netlify|moneymadesimple|money made simple", text, re.I), it["id"]
        assert not re.search(r"\bDM me\b|\bmessage me\b", text, re.I), it["id"]
        for pat in HYPE_PATTERNS + TESTIMONIAL_PATTERNS:
            assert not re.search(pat, text, re.I), (it["id"], pat)
