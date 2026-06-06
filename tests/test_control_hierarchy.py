"""
tests/test_control_hierarchy.py
"""

from ontology.control_hierarchy import (
    ControlHierarchy,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "CONTROL_HIERARCHY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ControlHierarchy()
    result = primitive.evaluate()

    assert abs(result["hierarchical_depth"] - 0.0) < 1e-12
    assert abs(result["cross_level_coordination"] - 0.0) < 1e-12
    assert abs(result["meta_control_capacity"] - 0.0) < 1e-12
    assert abs(result["control_hierarchy_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = ControlHierarchy(
        hierarchical_depth=0.9,
        cross_level_coordination=0.6,
        meta_control_capacity=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["control_hierarchy_index"] - expected) < 1e-12


def test_negative_case():
    primitive = ControlHierarchy(
        hierarchical_depth=-1.0,
        cross_level_coordination=-2.0,
        meta_control_capacity=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["control_hierarchy_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = ControlHierarchy(
        hierarchical_depth=2.0,
        cross_level_coordination=1.5,
        meta_control_capacity=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["hierarchical_depth"] - 1.0) < 1e-12
    assert abs(result["cross_level_coordination"] - 1.0) < 1e-12
    assert abs(result["meta_control_capacity"] - 1.0) < 1e-12
    assert abs(result["control_hierarchy_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = ControlHierarchy(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["control_hierarchy_index"]
        - result_step["control_hierarchy_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = ControlHierarchy(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["control_hierarchy_index"]
        - result["control_hierarchy_index"]
    ) < 1e-12
