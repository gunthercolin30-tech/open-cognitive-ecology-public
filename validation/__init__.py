"""
Infrastructure modulaire de validation scientifique du corpus ontology.

Ce package regroupe :

- le harness scientifique d'intégration ;
- le point d'entrée principal de la validation ;
- les outils d'audit de couverture conceptuelle ;
- les outils de planification de complétude ontologique.

L'objectif est de :
1. vérifier l'exécution correcte de l'ontologie computationnelle ;
2. mesurer la couverture conceptuelle du corpus théorique ;
3. identifier les concepts manquants ou partiellement implémentés ;
4. recommander les actions minimales nécessaires :
   - keep_as_is
   - extend_existing_module
   - replace_module
   - merge_modules
   - delete_module
   - create_new_module
5. préparer la validation scientifique complète du corpus.
"""

from validation.main import main
from validation.scientific_harness import OntologyIntegrationTestHarness

# Outils d'audit conceptuel
from validation.constraint_table_loader import load_constraints
from validation.manuscript_concept_extractor import extract_concepts
from validation.ontology_inventory import inventory
from validation.semantic_constraint_matcher import match
from validation.ontology_completion_planner import recommend_action

__all__ = [
    # Point d'entrée principal
    "main",

    # Harness scientifique
    "OntologyIntegrationTestHarness",

    # Audit conceptuel
    "load_constraints",
    "extract_concepts",
    "inventory",
    "match",
    "recommend_action",
]