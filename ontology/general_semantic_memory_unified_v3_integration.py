
"""
Integration bridge between GENERAL_SEMANTIC_MEMORY_UNIFIED_V3 and
GENERAL_COMPLEX_QUERY_RESOLUTION_ENGINE_V4.
"""

from __future__ import annotations

from typing import Any, Dict


def enrich_with_general_complex_query_engine(memory, text: str) -> Dict[str, Any]:
    """Return enriched analysis using the general complex query engine if available."""
    try:
        from ontology.general_complex_query_resolution_engine_v4 import (
            GeneralComplexQueryResolutionEngineV4,
        )
        engine = GeneralComplexQueryResolutionEngineV4()
        return engine.analyze(text)
    except Exception as exc:
        return {
            "text": text,
            "status": "fallback",
            "error": str(exc),
            "features": {},
        }
