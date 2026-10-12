# -*- coding: utf-8 -*-
"""Compatibility shim for the unified general semantic memory implementation."""

from .general_semantic_memory_unified import GeneralSemanticMemoryUnified

# Backward-compatible public alias.  Keep a single implementation class so
# historical imports do not create a divergent semantic-memory runtime.
GeneralSemanticMemory = GeneralSemanticMemoryUnified

__all__ = [
    "GeneralSemanticMemoryUnified",
    "GeneralSemanticMemory",
]
