"""
tests/test_buffering_capacity.py
"""

from ontology.buffering_capacity import (
    BufferingCapacity,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_constants():
    assert PRIMITIVE_NAME == "BUFFERING_CAPACITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = BufferingCapacity()
    result = primitive.evaluate()

    assert abs(result["absorption_capacity"] - 0.0) < 1e-12
    assert abs(result["delay_tolerance"] - 0.0) < 1e-12
    assert abs(result["stabilization_margin"] - 0.0) < 1e-12
    assert abs(result["buffering_capacity_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = BufferingCapacity(
        absorption_capacity=0.9,
        delay_tolerance=0.6,
        stabilization_margin=0.3,
    )
    result = primitive.evaluate()

    expected = (0.9 + 0.6 + 0.3) / 3.0
    assert abs(result["buffering_capacity_index"] - expected) < 1e-12


def test_negative_case():
    primitive = BufferingCapacity(
        absorption_capacity=-1.0,
        delay_tolerance=-2.0,
        stabilization_margin=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["buffering_capacity_index"] - 0.0) < 1e-12


def test_bounding():
    primitive = BufferingCapacity(
        absorption_capacity=2.0,
        delay_tolerance=1.5,
        stabilization_margin=10.0,
    )
    result = primitive.evaluate()

    assert abs(result["absorption_capacity"] - 1.0) < 1e-12
    assert abs(result["delay_tolerance"] - 1.0) < 1e-12
    assert abs(result["stabilization_margin"] - 1.0) < 1e-12
    assert abs(result["buffering_capacity_index"] - 1.0) < 1e-12


def test_step_matches_evaluate():
    primitive = BufferingCapacity(0.7, 0.8, 0.9)

    result_eval = primitive.evaluate()
    result_step = primitive.step()

    assert abs(
        result_eval["buffering_capacity_index"]
        - result_step["buffering_capacity_index"]
    ) < 1e-12


def test_validate_matches_evaluate():
    primitive = BufferingCapacity(0.2, 0.4, 0.6)

    result = primitive.evaluate()
    validation = primitive.validate()

    assert validation["is_valid"] is True
    assert abs(
        validation["buffering_capacity_index"]
        - result["buffering_capacity_index"]
    ) < 1e-12
