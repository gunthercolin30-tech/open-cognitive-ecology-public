"""
Ontology package for Open Cognitive Ecology.

Ce module expose explicitement les primitives fondamentales du corpus afin
de faciliter l'importation, l'introspection automatique et la validation
scientifique du projet.
"""

from .non_closure import NonClosurePrimitive
from .non_representability import NonRepresentabilityPrimitive

__all__ = [
    "NonClosurePrimitive",
    "NonRepresentabilityPrimitive",
]