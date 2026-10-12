"""
MULTI_SOURCE_ENCYCLOPEDIC_INTEGRATION_ENGINE

Intégration générale de sources encyclopédiques publiques
(Wikidata, Wikipedia, DBpedia) en utilisant uniquement
la bibliothèque standard Python.
"""

from __future__ import annotations

import json
import urllib.parse
from ontology.governed_network_effector import GovernedNetworkEffector, GovernedNetworkRequest, UrllibTrustedTransport


class MultiSourceEncyclopedicIntegrationEngine:
    USER_AGENT = "OpenCognitiveEcology/1.0"

    def __init__(self, governed_network_context=None):
        self.governed_network_context = governed_network_context

    def set_governed_network_context(self, context):
        self.governed_network_context = context

    def _get_json(self, url: str):
        ctx = self.governed_network_context
        if not isinstance(ctx, dict) or ctx.get("handle") is None: raise PermissionError("governed_network_context_required")
        effector = ctx.get("effector") or GovernedNetworkEffector(transport=UrllibTrustedTransport(), credential_resolver=ctx.get("credential_resolver"))
        result = effector.execute(request=GovernedNetworkRequest("GET", url, {"User-Agent": self.USER_AGENT}, timeout_seconds=20.0, idempotent=True), handle=ctx.get("handle"), brokered_use=ctx.get("brokered_use"), adapter_id=ctx.get("adapter_id"), effector_id=ctx.get("effector_id"), now_iso=ctx.get("now_iso"))
        if result.get("status") != "EFFECT_CONFIRMED": raise PermissionError("governed_network_effect_blocked:"+str(result.get("reason")))
        payload=(result.get("transport_result") or {}).get("body")
        if not isinstance(payload,(bytes,bytearray)): raise RuntimeError("governed_network_response_body_missing")
        return json.loads(bytes(payload).decode("utf-8"))

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
