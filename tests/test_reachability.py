"""
tests/test_reachability.py
"""

from ontology.reachability import (
    Reachability,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "REACHABILITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Reachability()
    result = primitive.evaluate()

    assert abs(result["trajectory_existence"] - 0.0) < 1e-12
    assert abs(result["path_viability"] - 0.0) < 1e-12
    assert abs(result["target_connectivity"] - 0.0) < 1e-12
    assert abs(result["reachability_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Reachability(
        trajectory_existence=0.9,
        path_viability=0.6,
        target_connectivity=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["reachability_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Reachability(
        trajectory_existence=-1.0,
        path_viability=-2.0,
        target_connectivity=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["reachability_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Reachability(
        trajectory_existence=2.0,
        path_viability=1.5,
        target_connectivity=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["trajectory_existence"] - 1.0) < 1e-12
    assert abs(result["path_viability"] - 1.0) < 1e-12
    assert abs(result["target_connectivity"] - 1.0) < 1e-12
    assert abs(result["reachability_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Reachability(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["reachability_index"]
        - result_step["reachability_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Reachability(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["reachability_index"]
        - result["reachability_index"]
    ) < 1e-12
