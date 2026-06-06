"""
Semantic enrichment application layer.

This module extends the runtime activation so that selected features from
last_semantic_enrichment are persisted directly into stored triples.
Current implementation activates negation markers and metadata propagation.
"""

from __future__ import annotations

from datetime import datetime


def activate_semantic_enrichment_application() -> bool:
    try:
        from ontology.general_semantic_memory_unified import (
            GeneralSemanticMemoryUnified,
        )
    except Exception:
        return False

    if getattr(
        GeneralSemanticMemoryUnified,
        "_semantic_enrichment_application_activated",
        False,
    ):
        return True

    original_store_statement = GeneralSemanticMemoryUnified.store_statement

    def patched_store_statement(self, statement):
        before = len(self.triples)
        result = original_store_statement(self, statement)

        enrichment = getattr(self, "last_semantic_enrichment", {}) or {}
        features = enrichment.get("features", {}) or {}

        # Simple heuristic negation detection based on standard French markers.
        normalized_text = str(statement).lower()
        neg_markers = [
            marker for marker in [" ne ", " n'", " pas", " plus", " jamais", " aucun", " rien"]
            if marker in (" " + normalized_text + " ")
        ]

        # Also incorporate future engine output if populated.
        engine_neg = features.get("negation", [])
        if isinstance(engine_neg, list):
            for marker in engine_neg:
                if marker and marker not in neg_markers:
                    neg_markers.append(marker)

        # Propagate enrichment metadata to newly created triples.
        for triple in self.triples[before:]:
            triple["semantic_enrichment_timestamp"] = (
                datetime.utcnow().isoformat() + "Z"
            )
            triple["semantic_status"] = enrichment.get("status", "unknown")

            if neg_markers:
                triple["negated"] = True
                triple["negation_markers"] = neg_markers
            else:
                triple["negated"] = False

            # Preserve extracted entities and dates if available.
            if features.get("entities"):
                triple["entities"] = features["entities"]
            if features.get("dates"):
                triple["dates"] = features["dates"]

        return result

    GeneralSemanticMemoryUnified.store_statement = patched_store_statement
    GeneralSemanticMemoryUnified._semantic_enrichment_application_activated = True
    return True


# Activate automatically at import time.
activate_semantic_enrichment_application()
