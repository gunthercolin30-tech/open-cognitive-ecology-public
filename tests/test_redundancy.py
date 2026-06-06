"""
tests/test_redundancy.py
"""

from ontology.redundancy import (
    Redundancy,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "REDUNDANCY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Redundancy()
    result = primitive.evaluate()

    assert abs(result["replication_level"] - 0.0) < 1e-12
    assert abs(result["backup_capacity"] - 0.0) < 1e-12
    assert abs(result["failure_coverage"] - 0.0) < 1e-12
    assert abs(result["redundancy_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Redundancy(
        replication_level=0.9,
        backup_capacity=0.6,
        failure_coverage=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["redundancy_index"] - expected) < 1e-12


def test_negative_case():
    primitive = Redundancy(
        replication_level=-1.0,
        backup_capacity=-2.0,
        failure_coverage=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["redundancy_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = Redundancy(
        replication_level=2.0,
        backup_capacity=1.5,
        failure_coverage=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["replication_level"] - 1.0) < 1e-12
    assert abs(result["backup_capacity"] - 1.0) < 1e-12
    assert abs(result["failure_coverage"] - 1.0) < 1e-12
    assert abs(result["redundancy_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = Redundancy(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["redundancy_index"]
        - result_step["redundancy_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = Redundancy(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["redundancy_index"]
        - result["redundancy_index"]
    ) < 1e-12
