from contentfactory.originality import audit, from_packs


def _long(i, words=900, chart=False, planned="", title=None, hook="Here is the thing."):
    seg = {"heading": "h", "narration": " ".join(f"w{i}x{k}" for k in range(words)) + ".", "on_screen_text": "x"}
    if chart:
        seg["chart"] = {"kind": "bars", "labels": ["a"], "values": [1]}
    return {"id": i, "format": "long", "script": {"title": title or f"Topic {i} explained", "hook": hook,
                                                  "segments": [seg], "original_element": planned}}


def test_clean_channel_scores_low():
    hooks = ["Start here.", "Picture a Monday morning with no money left.", "Most people skip this step entirely.",
             "Here is a number that surprised me.", "You have probably seen this mistake.", "Ask yourself one question."]
    items = [_long(i, chart=True, title=t, hook=hooks[i]) for i, t in enumerate(
        ["Why rent eats your raise", "Budget in one evening", "Index funds for beginners", "Credit score myths, tested",
         "The 3-account system", "Paying off a card faster"])]
    for k, it in enumerate(items):
        it["script"]["segments"] *= (k % 3) + 1
    r = audit(items, "good")
    assert r.level == "low" and r.score < 25, r


def test_templated_thin_channel_scores_high():
    shared = "If someone calls asking for a gift card payment, hang up and call the number on the back of your card."
    items = []
    for i in range(10):
        it = _long(i, words=400, title=f"How the scam worked: case {i}", hook=f"This is how case {i} worked out.")
        it["script"]["segments"].append({"heading": "end", "narration": shared, "on_screen_text": ""})
        items.append(it)
    r = audit(items, "risky")
    names = {s.name: s for s in r.signals}
    assert r.level == "high" and names["original_element"].value == 1 and names["thin"].value == 1
    assert names["sameness"].value > 0.3 and names["reused_narration"].value > 0
    assert any("original element" in f for f in r.fixes)


def test_planned_counts_half_and_pack_item_field(tmp_path):
    import json
    p = tmp_path / "content.json"
    p.write_text(json.dumps([{"format": "long", "original_element": "Record the bank app settings",
                              "script": _long(1)["script"] | {"original_element": ""}}]))
    items = from_packs([p])
    r = audit(items, "x")
    assert next(s for s in r.signals if s.name == "original_element").value == 0.5


def test_newsletter_export_kit_and_sender(factory):
    from contentfactory.newsletter_export import export
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "approved",
                                      "title": "Budget weekly, not monthly", "caption": "Weekly budgets are easier.",
                                      "script": {}})
    kit = export(factory, "money-made-simple", "kit", upcoming=True)
    html = (kit["dir"] / "email.html").read_text()
    assert kit["posts"] == 1 and "Budget weekly, not monthly" in html and "{{ unsubscribe_url }}" in html
    assert "%%" not in html and "%%" not in (kit["dir"] / "email.txt").read_text()
    assert (kit["dir"] / "body.html").read_text().startswith("<table") and "Subject:" in (kit["dir"] / "subject.txt").read_text()
    snd = export(factory, "money-made-simple", "sender", upcoming=True)
    sh = (snd["dir"] / "email.html").read_text()
    assert "Unsubscribe" not in sh and "%%" not in sh and "made with AI" in sh.lower() or "AI tools" in sh
    assert "postal address" in (snd["dir"] / "CHECKLIST.md").read_text()


def test_element_as_dict():
    from contentfactory.originality import _element, audit, element_text
    el = {"type": "human-segment", "detail": "Dhruv records the monthly hour", "chapter": "Monthly hour"}
    assert "human-segment" in element_text(el) and element_text(None) == ""
    script = {"title": "t", "segments": [{"narration": "x"}], "original_element": el}
    assert _element(script, None) == "planned"
    audit([{"id": 1, "format": "long", "script": script}], "b")
