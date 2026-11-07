"""Language support: Spanish brand labels, bios, guardrails, TTS voice choice, pack export."""
import json
from pathlib import Path

from contentfactory import i18n
from contentfactory.brandkit.bios import enforce_limits, offline_bios, write_bios
from contentfactory.brandkit.kit import highlight_titles, pillar_labels, short_label
from contentfactory.config import BrandProfile
from contentfactory.guardrails import (
    AFFILIATE_DISCLOSURE,
    AI_DISCLOSURE,
    HYPE_PATTERNS,
    TESTIMONIAL_PATTERNS,
    check_patterns,
)

ROOT = Path(__file__).resolve().parents[1]


def _es(**kw):
    return BrandProfile(slug="ds", name="Dinero Simple", niche="finanzas", audience="latinos en EE. UU.",
                        language="es", region="US", promise="un paso con tu dinero cada semana",
                        cta="Síguenos para más.", **kw)


def test_lang_and_locale():
    assert i18n.lang_of("es-US") == "es" and i18n.lang_of("ES_419") == "es"
    assert i18n.lang_of("fr") == "en"  # unknown falls back to English
    assert i18n.locale_of(_es()) == "es-US"
    assert i18n.t("es", "swipe") == "Desliza"
    assert i18n.t("en", "swipe") == "Swipe"
    assert "Spanish" in i18n.writing_instruction(_es())
    assert i18n.writing_instruction(BrandProfile(slug="x", name="X", niche="n", audience="a")) == ""


def test_spanish_bios_carry_spanish_ai_tag():
    pack = enforce_limits(offline_bios(_es()), "es")
    for text in (pack.instagram, pack.tiktok, pack.x, pack.threads, pack.youtube_about):
        assert "IA" in text
    assert len(pack.instagram) <= 150 and len(pack.tiktok) <= 80 and len(pack.youtube_about) <= 1000
    assert "Hablamos de" in pack.youtube_about


def test_hand_written_bios_win():
    bios = {"instagram": "Hola", "tiktok": "Hola", "x": "Hola", "threads": "Hola", "youtube_about": "Hola"}
    pack = write_bios(None, _es(bios=bios))  # all five given: no LLM call
    assert pack.instagram == "Hola\nCon ayuda de IA"


def test_spanish_highlights():
    brand = _es(pillars=["presupuesto que sí funciona", "puntaje de crédito y deudas"])
    pairs = pillar_labels(brand)
    assert [icon for _, icon in pairs[:2]] == ["coin", "card"]
    assert "Empieza aquí" in [label for label, _ in pairs]
    assert short_label("presupuesto que sí funciona", lang="es") == "Presupuesto"
    assert highlight_titles(_es(highlights=["Ahorro"]), pairs)[0] == "Ahorro"


def test_spanish_guardrail_patterns():
    assert check_patterns("Lo he usado por un mes y me cambió la vida", TESTIMONIAL_PATTERNS, "t", "warn", "x").level == "warn"
    assert check_patterns("Rendimientos garantizados, dinero fácil", HYPE_PATTERNS, "c", "warn", "x").level == "warn"
    assert check_patterns("Abre una cuenta de ahorro", HYPE_PATTERNS, "c", "warn", "x").level == "ok"
    assert AI_DISCLOSURE.search("Imágenes y voz hechas con herramientas de IA.")
    assert AFFILIATE_DISCLOSURE.search("Es un enlace de afiliado.")


def test_language_review_gate(factory, fake_render):
    item = json.loads((ROOT / "launch" / "dinero-simple" / "content.json").read_text())[0]
    pid = factory.import_script("dinero-simple", item["script"], item["format"])
    checks = {c["name"]: c for c in factory.db.get("posts", pid)["checks"]["checks"]}
    assert checks["language_review"]["level"] == "warn"
    assert checks["ai_label"]["level"] == "ok"  # Spanish disclosure is recognised
    factory.mark_language_reviewed(pid, "Ana")
    checks = {c["name"]: c for c in factory.db.get("posts", pid)["checks"]["checks"]}
    assert checks["language_review"]["level"] == "ok"


def test_english_posts_have_no_language_check(factory, fake_render):
    item = json.loads((ROOT / "launch" / "money-made-simple" / "content.json").read_text())[0]
    pid = factory.import_script("money-made-simple", item["script"], item["format"])
    names = [c["name"] for c in factory.db.get("posts", pid)["checks"]["checks"]]
    assert "language_review" not in names


def test_tts_voice_follows_language(monkeypatch):
    from contentfactory.media.tts import Piper
    monkeypatch.setenv("PIPER_MODEL", "/voices/en_US.onnx")
    monkeypatch.delenv("PIPER_MODEL_ES", raising=False)
    assert Piper(None, _es()).model() == ""  # an English voice never reads Spanish
    monkeypatch.setenv("PIPER_MODEL_ES", "/voices/es_MX.onnx")
    assert Piper(None, _es()).model() == "/voices/es_MX.onnx"


def test_writer_prompt_asks_for_spanish():
    from contentfactory.writer import _brand_brief
    assert "Latin American Spanish" in _brand_brief(_es())


def test_pack_export_spanish_carousel(factory, tmp_path):
    from contentfactory.launchpack import export_pack
    items = json.loads((ROOT / "launch" / "dinero-simple" / "content.json").read_text())
    carousel = next(i for i in items if i["format"] == "carousel")
    short = items[0]
    folders = export_pack(factory.settings, factory.brand("dinero-simple"), [short, carousel], tmp_path)
    assert (folders[0] / "thumbnail.jpg").exists()
    assert len(list(folders[1].glob("slide-*.jpg"))) == len(carousel["script"]["segments"])
    caption = (folders[1] / "caption.txt").read_text()
    assert "fluent es-US speaker" in caption and "herramientas de IA" in caption


def test_spanish_content_matches_english_structure():
    es = json.loads((ROOT / "launch" / "dinero-simple" / "content.json").read_text())
    en = json.loads((ROOT / "launch" / "money-made-simple" / "content.json").read_text())
    assert len(es) == 24
    for item in es:
        src = en[item["source_index"]]
        assert item["format"] == src["format"]
        assert len(item["script"]["segments"]) == len(src["script"]["segments"])
        assert "green piggy" not in json.dumps(item)


def test_kokoro_uses_a_spanish_voice_for_a_spanish_brand(monkeypatch):
    from contentfactory.config import Settings
    from contentfactory.media import tts
    monkeypatch.setenv("KOKORO_VOICE", "am_michael")  # an English override must not leak into Spanish
    monkeypatch.delenv("KOKORO_VOICE_ES", raising=False)
    settings = Settings.load()
    assert tts.Kokoro(settings, _es())._voice() == "ef_dora"
    monkeypatch.setenv("KOKORO_VOICE_ES", "em_alex")
    assert tts.Kokoro(settings, _es())._voice() == "em_alex"
