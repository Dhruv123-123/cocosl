from contentfactory.doctor import run_checks


def test_doctor_runs_offline_and_reports_levels(factory):
    results = {r.name: r for r in run_checks(factory, online=False, voice=True)}
    assert results["database"].level == "ok"
    assert results["output"].level in ("ok", "warn")
    assert results["voice"].level in ("ok", "warn")          # silent fallback in tests
    assert results["writing"].level == "warn"                # offline LLM
    assert results["dry run"].level == "ok"
    assert results["worker"].level == "warn"


def test_doctor_fails_live_instagram_without_media_url(factory):
    factory.settings.dry_run = False
    factory.settings.public_media_base_url = ""
    results = run_checks(factory, voice=False)
    assert any(r.name == "media URL" and r.level == "fail" for r in results)


def test_doctor_offline_never_touches_the_network(factory, monkeypatch):
    import socket

    from contentfactory.doctor import run_checks

    def no_network(*a, **k):
        raise AssertionError("offline doctor opened a network connection")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setenv("KOKORO_URL", "http://kokoro.invalid:8880")
    monkeypatch.setenv("FACTORY_TTS", "auto")
    (factory.settings.home / ".env").write_text("X=1\n")
    (factory.settings.home / ".env").chmod(0o644)
    results = {r.name: r for r in run_checks(factory, offline=True)}
    for name in ("python", "packages", "fonts", ".env", "db integrity"):
        assert name in results, name
    assert results[".env"].level == "warn" and "chmod 600" in results[".env"].message
    assert results["db integrity"].level == "ok" and results["packages"].level == "ok"
    import os
    assert os.environ["KOKORO_URL"] == "http://kokoro.invalid:8880"  # restored after the voice check
