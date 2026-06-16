"""
Wrapper de compatibilité historique pour la validation scientifique du corpus.

Ce module préserve les commandes historiques :

    python3 ontology_integration_test_harness.py
    python3 -m ontology_integration_test_harness

Il délègue l'exécution à validation.main.main().
"""

from __future__ import annotations

from validation.main import main


if __name__ == "__main__":
    main()