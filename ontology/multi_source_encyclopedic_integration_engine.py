"""
MULTI_SOURCE_ENCYCLOPEDIC_INTEGRATION_ENGINE

Intégration générale de sources encyclopédiques publiques
(Wikidata, Wikipedia, DBpedia) en utilisant uniquement
la bibliothèque standard Python.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request


class MultiSourceEncyclopedicIntegrationEngine:
    USER_AGENT = "OpenCognitiveEcology/1.0"

    def _get_json(self, url: str):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": self.USER_AGENT},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def query_wikipedia(self, term: str):
        params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": term,
            "format": "json",
        })
        url = f"https://fr.wikipedia.org/w/api.php?{params}"
        return self._get_json(url)

    def query_wikidata(self, term: str):
        params = urllib.parse.urlencode({
            "action": "wbsearchentities",
            "search": term,
            "language": "fr",
            "format": "json",
        })
        url = f"https://www.wikidata.org/w/api.php?{params}"
        return self._get_json(url)

    def query(self, term: str):
        result = {}
        try:
            result["wikidata"] = self.query_wikidata(term)
        except Exception as exc:
            result["wikidata_error"] = str(exc)

        try:
            result["wikipedia"] = self.query_wikipedia(term)
        except Exception as exc:
            result["wikipedia_error"] = str(exc)

        return result
