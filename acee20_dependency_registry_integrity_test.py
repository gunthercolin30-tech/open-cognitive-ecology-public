#!/usr/bin/env python3
from dependency_registry import DEPENDENCY_REGISTRY as ROOT_REGISTRY
from ontology.dependency_registry import (
    DEPENDENCY_REGISTRY as ONTOLOGY_REGISTRY,
)


EXPECTED = [
    "performance_improvement_planner",
    "self_parameter_optimization_engine",
    "trajectory_simulation",
    "trajectory_reversibility",
    "trajectory_validation",
    "acee_longitudinal_tracker",
    "acee_best_architecture_archive",
]


def main():
    assert ROOT_REGISTRY["acee_prediction_engine"] == EXPECTED
    assert ONTOLOGY_REGISTRY["acee_prediction_engine"] == EXPECTED

    for registry in (ROOT_REGISTRY, ONTOLOGY_REGISTRY):
        assert "acee_meta_analysis" in registry
        assert "acee_final_certifier" in registry

    print("ACEE20_DEPENDENCY_REGISTRY_INTEGRITY_OK")


if __name__ == "__main__":
    main()
