from __future__ import annotations

"""Semantic Translation Engine.

Wrapper around Argos Translate when available.
Falls back to the original text if translation is unavailable.
"""

from typing import Optional


class SemanticTranslationEngine:
    primitive = "SEMANTIC_TRANSLATION_ENGINE"

    def __init__(self) -> None:
        self._translator = None
        self._load_argos()

    def _load_argos(self) -> None:
        try:
            import argostranslate.translate as translate
            self._translator = translate
        except Exception:
            self._translator = None

    def available(self) -> bool:
        return self._translator is not None

    def translate(self, text: str, from_lang: str = "en", to_lang: str = "fr") -> str:
        if not isinstance(text, str) or not text.strip():
            return text

        if self._translator is None:
            return text

        try:
            languages = self._translator.get_installed_languages()
            source = next((lang for lang in languages if lang.code == from_lang), None)
            target = next((lang for lang in languages if lang.code == to_lang), None)

            if source is None or target is None:
                return text

            translation = source.get_translation(target)
            return translation.translate(text)
        except Exception:
            return text

    def step(self, text: str, from_lang: str = "en", to_lang: str = "fr") -> dict:
        translated = self.translate(text, from_lang=from_lang, to_lang=to_lang)
        return {
            "primitive": self.primitive,
            "available": self.available(),
            "source_language": from_lang,
            "target_language": to_lang,
            "input_text": text,
            "translated_text": translated,
            "translation_performed": translated != text,
        }
