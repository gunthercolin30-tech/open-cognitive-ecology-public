from ontology.contradiction_detection_system import (
    DEPENDENCIES as CONTRADICTION_DEPENDENCIES,
)
from ontology.knowledge_integration_engine import (
    DEPENDENCIES as INTEGRATION_DEPENDENCIES,
)


def test_semantic_memory_consumers_declare_canonical_variant():
    for dependencies in (CONTRADICTION_DEPENDENCIES, INTEGRATION_DEPENDENCIES):
        assert "general_semantic_memory_unified" in dependencies
        assert "general_semantic_memory_unified_v3" not in dependencies
