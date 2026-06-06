"""
Runtime activation layer for GENERAL_SEMANTIC_MEMORY_UNIFIED.

This patch monkey-patches store_statement() so that each input statement
is first analyzed through semantic_runtime_hook(), and the enrichment is
stored in self.last_semantic_enrichment for downstream use.
"""

from __future__ import annotations


def activate_general_semantic_runtime() -> bool:
    try:
        from ontology.general_semantic_memory_unified import (
            GeneralSemanticMemoryUnified,
        )
        from ontology.general_semantic_memory_unified_v3_runtime_hook import (
            semantic_runtime_hook,
        )
    except Exception:
        return False

    if getattr(
        GeneralSemanticMemoryUnified,
        "_general_semantic_runtime_activated",
        False,
    ):
        return True

    original_store_statement = GeneralSemanticMemoryUnified.store_statement

    def patched_store_statement(self, statement):
        try:
            self.last_semantic_enrichment = semantic_runtime_hook(statement)
        except Exception as exc:
            self.last_semantic_enrichment = {
                "text": statement,
                "status": "fallback",
                "error": str(exc),
                "features": {},
            }
        return original_store_statement(self, statement)

    GeneralSemanticMemoryUnified.store_statement = patched_store_statement
    GeneralSemanticMemoryUnified._general_semantic_runtime_activated = True
    return True


# Activate automatically at import time.
activate_general_semantic_runtime()
