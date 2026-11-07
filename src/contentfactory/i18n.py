"""Language support: the words the factory itself puts on screen and in bios.

A brand sets `language` (ISO 639-1, e.g. "es") and optionally `region`
(e.g. "US"). Script text comes from the writer in that language; this module
covers everything else the software adds on its own: carousel labels, banner
taglines, highlight names, fallback bios, the AI tag, LLM language
instructions, TTS voice defaults and trend-signal locales.

Machine-written copy in any language other than English must be reviewed by a
fluent speaker before it is posted. Guardrails warn on every non-English post
until `meta.native_review` records who checked it.
"""
from __future__ import annotations

from typing import Any

DEFAULT = "en"

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "swipe": "Swipe",
        "save_this": "SAVE THIS",
        "follow_for_more": "Follow for more.",
        "new_videos_weekly": "New videos every week",
        "new_shorts_daily": "New shorts most days",
        "ai_tag": "AI-assisted",
        "free_guide_below": "free guide below",
        "start_here": "Start here",
        "freebies": "Freebies",
        "faq": "FAQ",
        "videos": "Videos",
        "guides": "Guides",
        "about_made_for": "Made for {audience}. We cover {topics}.",
        "about_promise": "Every upload is specific and free of hype: one idea you can use, explained clearly.",
        "about_how_made": ("How this channel is made: {disclosure} Content is AI-assisted; a human chooses every "
                           "topic, checks the facts and approves each upload. No fake reviews, no AI testimonials."),
        "about_affiliate": ("Some links may be affiliate links; if you buy through them we may earn a commission "
                            "at no extra cost to you. Business enquiries via the link in the channel header."),
    },
    "es": {
        "swipe": "Desliza",
        "save_this": "GUÁRDALO",
        "follow_for_more": "Síguenos para más.",
        "new_videos_weekly": "Videos nuevos cada semana",
        "new_shorts_daily": "Shorts nuevos casi a diario",
        "ai_tag": "Con ayuda de IA",
        "free_guide_below": "guía gratis abajo",
        "start_here": "Empieza aquí",
        "freebies": "Gratis",
        "faq": "Preguntas",
        "videos": "Videos",
        "guides": "Guías",
        "about_made_for": "Para {audience}. Hablamos de {topics}.",
        "about_promise": "Cada video es concreto y sin exageraciones: una idea que puedes usar, bien explicada.",
        "about_how_made": ("Cómo lo hacemos: {disclosure} Una persona elige cada tema, revisa los datos y aprueba "
                           "cada video. Sin reseñas falsas ni testimonios hechos con IA."),
        "about_affiliate": ("Algunos enlaces son de afiliado: podríamos recibir una comisión sin costo extra para ti. "
                            "Para negocios, usa el enlace del canal."),
    },
}

# Language names as an LLM prompt should say them, plus the register to write in.
WRITING_RULES: dict[str, str] = {
    "es": ("Write every audience-facing field (title, hook, narration, on_screen_text, cta, caption, hashtags, "
           "description, thumbnail_text, variants) in natural, neutral Latin American Spanish for US Hispanic "
           "viewers: tú (not usted, not vosotros), everyday words a bilingual 25-year-old would use, no Spain-only "
           "terms (use 'carro', 'celular', 'cuenta de cheques'). Keep US financial product names in English "
           "where that is what people search for (401(k), Roth IRA, HYSA, FICO) and explain them once in Spanish. "
           "Do not translate idioms word for word. Write visual_prompt, sources and claims_to_verify in English "
           "so the operator can check them."),
}

# espeak-ng voice and Wikipedia/YouTube locale per language.
ESPEAK_VOICES = {"en": "en-us", "es": "es-419"}
SPEECH_ACCENTS = {"es": "Speak in natural Latin American Spanish with a neutral US Hispanic accent."}

# Words to drop when shortening a pillar to a ~15 character highlight title.
STOPWORDS = {
    "en": {"the", "a", "an", "of", "and", "that", "actually", "for", "to", "why", "they", "exist"},
    "es": {"el", "la", "los", "las", "un", "una", "de", "del", "y", "que", "en", "para", "por", "con", "tu",
           "tus", "su", "sus", "lo", "al", "realmente", "sí", "si"},
}


def lang_of(brand_or_code: Any) -> str:
    """'es' from a BrandProfile, 'es-US', 'es_419' or 'ES'; unknown → English."""
    code = getattr(brand_or_code, "language", brand_or_code) or DEFAULT
    base = str(code).replace("_", "-").split("-")[0].lower()
    return base if base in STRINGS else DEFAULT


def t(lang: Any, key: str, **kw: str) -> str:
    """Localised UI string; falls back to English for missing keys."""
    table = STRINGS[lang_of(lang)]
    text = table.get(key) or STRINGS[DEFAULT][key]
    return text.format(**kw) if kw else text


def locale_of(brand: Any) -> str:
    """BCP 47 tag for HTML lang attributes and platform metadata, e.g. 'es-US'."""
    lang = lang_of(brand)
    region = (getattr(brand, "region", "") or "").upper()
    return f"{lang}-{region}" if region else lang


def is_english(brand: Any) -> bool:
    return lang_of(brand) == DEFAULT


def writing_instruction(brand: Any) -> str:
    """Line to append to LLM prompts so copy comes back in the brand's language."""
    return WRITING_RULES.get(lang_of(brand), "")


def stopwords(lang: Any) -> set[str]:
    return STOPWORDS.get(lang_of(lang), STOPWORDS[DEFAULT])


def filler_labels(lang: Any) -> dict[str, str]:
    """Highlight filler label per icon name."""
    return {"star": t(lang, "start_here"), "gift": t(lang, "freebies"), "chat": t(lang, "faq"),
            "play": t(lang, "videos"), "book": t(lang, "guides")}
