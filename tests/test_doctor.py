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
