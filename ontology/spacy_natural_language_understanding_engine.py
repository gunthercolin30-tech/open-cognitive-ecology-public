from __future__ import annotations


class SpacyNaturalLanguageUnderstandingEngine:
    DEFAULT_MODEL = "fr_core_news_md"
    FALLBACK_MODELS = [
        "fr_core_news_sm",
        "fr_core_news_lg",
        "fr_dep_news_trf",
    ]

    def __init__(self, model_name=None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.available = False
        self.loaded_model = None
        self.nlp = None
        self.load_attempts = []
        self._load_best_available_model()

    def _candidate_models(self):
        candidates = [self.model_name]
        for model in self.FALLBACK_MODELS:
            if model not in candidates:
                candidates.append(model)
        return candidates

    def _load_best_available_model(self):
        try:
            import spacy
        except Exception as exc:
            self.load_attempts.append({
                "model": None,
                "success": False,
                "reason": f"spacy_not_installed: {exc}",
            })
            return

        for model in self._candidate_models():
            try:
                self.nlp = spacy.load(model)
                self.available = True
                self.loaded_model = model
                self.load_attempts.append({
                    "model": model,
                    "success": True,
                })
                return
            except Exception as exc:
                self.load_attempts.append({
                    "model": model,
                    "success": False,
                    "reason": str(exc),
                })

    def parse(self, text):
        if not self.available:
            return {
                "available": False,
                "reason": "no_model_available",
                "load_attempts": self.load_attempts,
            }

        doc = self.nlp(text)

        return {
            "available": True,
            "model": self.loaded_model,
            "sentences": [sent.text.strip() for sent in doc.sents],
            "entities": [
                {"text": ent.text, "label": ent.label_}
                for ent in doc.ents
            ],
            "tokens": [
                {
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "dep": token.dep_,
                }
                for token in doc
            ],
        }

    def status(self):
        return {
            "primitive": "SPACY_NATURAL_LANGUAGE_UNDERSTANDING_ENGINE",
            "available": self.available,
            "requested_model": self.model_name,
            "loaded_model": self.loaded_model,
            "fallback_models": list(self.FALLBACK_MODELS),
            "load_attempts": self.load_attempts,
        }

    def step(self, inputs):
        if not isinstance(inputs, dict):
            return {
                "primitive": "SPACY_NATURAL_LANGUAGE_UNDERSTANDING_ENGINE",
                "error": "dict expected",
            }

        action = inputs.get("action", "status")

        if action == "status":
            return self.status()

        if action == "parse":
            result = self.parse(inputs.get("text", ""))
            result["primitive"] = (
                "SPACY_NATURAL_LANGUAGE_UNDERSTANDING_ENGINE"
            )
            return result

        return {
            "primitive": "SPACY_NATURAL_LANGUAGE_UNDERSTANDING_ENGINE",
            "error": "unknown_action",
            "action": action,
        }
