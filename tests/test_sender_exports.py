import csv

from contentfactory import sequence_export as se


def test_sequence_export_for_sender(factory):
    out, rows = se.export(factory, "money-made-simple")
    assert [r[2] for r in rows][:2] == [rows[0][1], rows[1][1] - rows[0][1]]
    first = sorted(p for p in out.iterdir() if p.is_dir())[0]
    html = (first / "body.html").read_text() if (first / "body.html").exists() else (first / "launch" / "body.html").read_text()
    assert "You're getting this because" not in html and "/unsubscribe/" not in html
    seq_note = "not financial advice"
    assert seq_note in html.lower()
    assert (first / "DELAY.txt").exists()
    text = next(first.rglob("email.txt")).read_text()
    assert "Unsubscribe:" not in text
    check = (out / "CHECKLIST.md").read_text()
    assert "{$unsubscribe}" in check and "welcome_via: sender" in check
    if any(r[4] for r in rows):
        n = next(r for r in rows if r[4])[0]
        d = next(p for p in out.iterdir() if p.name.startswith(f"{n:02d}-"))
        a, b = (d / "launch" / "email.txt").read_text(), (d / "no-launch" / "email.txt").read_text()
        assert a != b


def test_subscribers_export_sender(factory):
    from contentfactory.db import now_iso
    from contentfactory.funnel import store
    from contentfactory.funnel.newsletter import export_subscribers_sender
    store.ensure_schema(factory.db)
    ids = []
    for k, email in enumerate(["a@x.com", "b@x.com", "c@x.com"]):
        ids.append(factory.db.insert("subscribers", {"brand": "money-made-simple", "email": email, "token": f"t{k}",
                                                    "status": "confirmed" if k < 2 else "pending", "source": "site",
                                                    "created_at": "2026-11-20T10:00:00+00:00",
                                                    "confirmed_at": "2026-11-20T10:05:00+00:00"}))
    factory.db.insert("emails_sent", {"brand": "money-made-simple", "subscriber_id": ids[0], "email": "a@x.com", "kind": "sequence:welcome:0",
                                      "status": "sent", "created_at": now_iso()})
    welcomed, rest = export_subscribers_sender(factory, "money-made-simple")
    w = list(csv.DictReader(welcomed.open()))
    r = list(csv.DictReader(rest.open()))
    assert [x["email"] for x in w] == ["a@x.com"] and [x["email"] for x in r] == ["b@x.com"]
    assert w[0]["subscribed_at"] == "2026-11-20 10:00:00" and list(w[0]) == ["email", "source", "subscribed_at", "confirmed_at"]


def test_welcome_via_sender_skips_worker(factory, monkeypatch):
    from contentfactory.funnel.sequences import run_sequences
    brand = factory.brand("money-made-simple")
    brand.welcome_via = "sender"
    monkeypatch.setattr(factory, "brands", lambda: {"money-made-simple": brand})
    res = run_sequences(factory)
    assert res["brands"]["money-made-simple"]["handled_by"] == "sender"
