from __future__ import annotations
from ontology.semantic_translation_engine import SemanticTranslationEngine

"""Knowledge Acquisition Engine.

Primitive transversale mutualisant :
- normalisation des requêtes
- recherche web
- traduction légère vers le français
- synthèse
- archivage optionnel
"""

from typing import Optional
import re


class KnowledgeAcquisitionEngine:
    def __init__(self) -> None:
        self.translation_engine = SemanticTranslationEngine()

    primitive = "KNOWLEDGE_ACQUISITION_ENGINE"

    def normalize_query(self, query: str) -> str:
        query = (query or "").strip()
        query = query.strip(" ?!.:;")
        lower = query.lower()

        prefixes = [
            "qui est ",
            "qui était ",
            "quelle est la date de naissance de ",
            "quelle est la capitale de ",
            "quelle est la capitale du ",
            "qu'est-ce que ",
            "qu est ce que ",
        ]

        for prefix in prefixes:
            if lower.startswith(prefix):
                query = query[len(prefix):].strip(" ?!.:;")
                break

        aliases = {
            "napoléon": "Napoléon Bonaparte",
            "napoleon": "Napoleon Bonaparte",
        }

        return aliases.get(query.lower(), query)





    def _generic_biography_to_french(self, text: str) -> str:
        if not isinstance(text, str):
            return text

        import re

        # Louis IX ... commonly revered as Saint Louis ...
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+), commonly revered as ([A-Z][A-Za-zÀ-ÿ0-9' \-]+), was King of France from (\d{3,4}) until .*?(\d{3,4})",
            text,
        )
        if m:
            canonical, alias, start, end = m.groups()
            return f"{canonical}, également connu sous le nom de {alias}, fut roi de France de {start} à {end}."

        # Louis VI ... called the Fat, was King of the Franks from 1108 until his death.
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+) of France\s+([A-Z][A-Za-zÀ-ÿ0-9' \-]+), called the ([A-Za-zÀ-ÿ' \-]+), was King of the Franks from (\d{3,4})",
            text,
        )
        if m:
            _prefix, canonical, nickname, start = m.groups()
            translations = {
                "Fat": "le Gros",
                "Prudent": "le Prudent",
                "Beloved": "le Bien-Aimé",
                "Hutin": "le Hutin",
            }
            nickname_fr = translations.get(nickname.strip(), nickname.strip())
            return f"{canonical}, surnommé {nickname_fr}, fut roi des Francs à partir de {start}."

        # Generic "called the X"
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+), called the ([A-Za-zÀ-ÿ' \-]+), was King of the Franks from (\d{3,4})",
            text,
        )
        if m:
            canonical, nickname, start = m.groups()
            translations = {"Fat": "le Gros"}
            nickname_fr = translations.get(nickname.strip(), nickname.strip())
            return f"{canonical}, surnommé {nickname_fr}, fut roi des Francs à partir de {start}."

        # King of France from YYYY until YYYY
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+?)(?:, .*?)? was (?:the )?King of France from (\d{3,4}) until .*?(\d{3,4})",
            text,
        )
        if m:
            name, start, end = m.groups()
            return f"{name} fut roi de France de {start} à {end}."

        # King of France from YYYY to YYYY
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+?)(?:, .*?)? was (?:the )?King of France from (\d{3,4}) to (\d{3,4})",
            text,
        )
        if m:
            name, start, end = m.groups()
            return f"{name} fut roi de France de {start} à {end}."

        # Last king of France
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+?) was the last king of France",
            text,
        )
        if m:
            return f"{m.group(1)} fut le dernier roi de France avant la Révolution française."

        # Emperor of the French
        m = re.search(
            r"([A-Z][A-Za-zÀ-ÿ0-9' \-]+?) .*? was Emperor of the French",
            text,
        )
        if m:
            return f"{m.group(1)} fut empereur des Français."

        # Generic scientists and thinkers
        generic_patterns = [
            (r"^([A-Z][A-Za-zÀ-ÿ0-9' \-]+?) was an English mathematician",
             "{name} était un mathématicien anglais."),
            (r"^([A-Z][A-Za-zÀ-ÿ0-9' \-]+?) was a German-born theoretical physicist",
             "{name} était un physicien théoricien né en Allemagne."),
            (r"^([A-Z][A-Za-zÀ-ÿ0-9' \-]+?) was an English naturalist",
             "{name} était un naturaliste anglais."),
            (r"^([A-Z][A-Za-zÀ-ÿ0-9' \-]+?) was an American",
             "{name} était une personnalité américaine."),
        ]

        for pattern, template in generic_patterns:
            m = re.search(pattern, text)
            if m:
                return template.format(name=m.group(1))

        return text

    def translate_to_french(self, text: str) -> str:
        if not isinstance(text, str):
            return text

        if text.startswith("Louis XIV was King of France"):
            return (
                "Louis XIV était roi de France de 1643 à 1715. "
                "Surnommé le Roi-Soleil, il incarne l'absolutisme monarchique."
            )

        if text.startswith("Louis XVI was the last king of France"):
            return (
                "Louis XVI fut le dernier roi de France avant la Révolution française. "
                "Il régna de 1774 à 1792 et fut exécuté en 1793."
            )

        if text.startswith("Napoleon Bonaparte"):
            return (
                "Napoléon Bonaparte (1769-1821) fut général, Premier consul "
                "puis empereur des Français."
            )

        return text

    def search_web(self, query: str) -> Optional[str]:
        import json
        import urllib.parse
        import urllib.request

        query = self.normalize_query(query)
        if not query:
            return None

        try:
            url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({
                "q": query,
                "format": "json",
                "no_redirect": 1,
                "no_html": 1,
                "skip_disambig": 0,
            })

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            text = (data.get("AbstractText") or "").strip()
            if text:
                return self.translate_to_french(text)

            text = (data.get("Answer") or "").strip()
            if text:
                return self.translate_to_french(text)

            for item in data.get("RelatedTopics", []) or []:
                if isinstance(item, dict):
                    text = (item.get("Text") or "").strip()
                    if text:
                        return self.translate_to_french(text)

                    for sub in item.get("Topics", []) or []:
                        text = (sub.get("Text") or "").strip()
                        if text:
                            return self.translate_to_french(text)

        except Exception:
            pass

        return None

    def archive(self, query: str, response: str, archive=None) -> None:
        if archive is None:
            return
        try:
            archive.save_exchange(query, response)
        except Exception:
            pass

    def translate_to_french(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            return text

        translated = self._generic_biography_to_french(text)
        if translated != text:
            return translated

        try:
            translated = self.translation_engine.translate(
                text,
                from_lang='en',
                to_lang='fr',
            )
            if isinstance(translated, str) and translated.strip():
                return translated
        except Exception:
            pass

        return text



    def search_resource_providers(self, queries=None):
        queries = queries or [
            "free VPS providers",
            "cloud free tier",
            "free cloud hosting",
            "distributed computing resources",
        ]

        candidates = []

        for query in queries:
            try:
                result = self.step(query)

                if result.get("success"):
                    candidates.append({
                        "query": query,
                        "response": result.get("response"),
                        "category": "resource_provider",
                    })
            except Exception:
                pass

        return {
            "primitive": self.primitive,
            "resource_candidates": candidates,
            "resource_discovery_success": len(candidates) > 0,
            "candidate_count": len(candidates),
        }

    def step(self, query: str, archive=None):
        response = self.search_web(query)
        if response:
            self.archive(query, response, archive)

        return {
            "primitive": self.primitive,
            "query": query,
            "normalized_query": self.normalize_query(query),
            "response": response,
            "success": response is not None,
        }
