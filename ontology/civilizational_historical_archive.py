"""
Ontology bridge for civilizational_historical_archive.

This module exposes the cognition-level implementation as an ontology-level
primitive so dependency discovery and validation can resolve it uniformly.
"""

from __future__ import annotations

try:
    from cognition.civilizational_historical_archive import CivilizationalHistoricalArchive as _SourceClass
except Exception as exc:
    _IMPORT_ERROR = exc
    _SourceClass = None


PRIMITIVE = "civilizational_historical_archive"
DEPENDENCIES = [
    "distributed_civilizational_memory",
]


class CivilizationalHistoricalArchive(_SourceClass if _SourceClass is not None else object):

    def __init__(self, *args, **kwargs):
        if _SourceClass is None:
            self._bridge_import_error = repr(_IMPORT_ERROR)
        else:
            super().__init__(*args, **kwargs)
            self._bridge_import_error = None

    def step(self, state=None):
        if state is None:
            state = {}

        if self._bridge_import_error is not None:
            return {
                "primitive": PRIMITIVE,
                "bridge_ready": False,
                "source": "cognition.civilizational_historical_archive",
                "error": self._bridge_import_error,
            }

        if hasattr(super(), "evaluate"):
            result = super().evaluate(state)
        else:
            result = {}

        if not isinstance(result, dict):
            result = {"result": result}

        result = dict(result)
        result.setdefault("primitive", PRIMITIVE)
        result["bridge_ready"] = True
        result["source"] = "cognition.civilizational_historical_archive"
        return result


__all__ = [
    "CivilizationalHistoricalArchive",
    "PRIMITIVE",
    "DEPENDENCIES",
]
