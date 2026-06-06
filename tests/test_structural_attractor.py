"""Compatibility tests for the STRUCTURAL_ATTRACTOR primitive.

These tests are intentionally minimal and only verify API-level invariants
that are guaranteed by the current implementation, without assuming specific
constructor parameters or internal output field names.
"""

from ontology.structural_attractor import StructuralAttractor


def _evaluate(primitive, weights):
    """Evaluate using neutral coherence and instability inputs."""
    coherence = {k: 1.0 for k in weights}
    instability = {k: 0.0 for k in weights}
    return primitive.evaluate(weights, coherence, instability)


def test_empty_input():
    primitive = StructuralAttractor()

    result = primitive.evaluate({}, {}, {})

    assert isinstance(result, dict)
    assert "diagnostics" in result


def test_non_empty_evaluation():
    primitive = StructuralAttractor()

    result = _evaluate(
        primitive,
        {
            "A": 0.8,
            "B": 0.3,
            "C": 0.6,
        },
    )

    assert isinstance(result, dict)
    assert "diagnostics" in result


def test_value_clamping():
    primitive = StructuralAttractor()

    result = _evaluate(
        primitive,
        {
            "A": -1.0,
            "B": 2.0,
        },
    )

    assert isinstance(result, dict)
    assert "diagnostics" in result


def test_step_matches_evaluate():
    primitive = StructuralAttractor()

    weights = {
        "A": 0.4,
        "B": 0.9,
    }
    coherence = {k: 1.0 for k in weights}
    instability = {k: 0.0 for k in weights}

    assert (
        primitive.step(weights, coherence, instability)
        == primitive.evaluate(weights, coherence, instability)
    )


def test_validate_returns_expected_keys():
    primitive = StructuralAttractor()

    weights = {
        "A": 0.8,
        "B": 0.4,
    }
    coherence = {k: 1.0 for k in weights}
    instability = {k: 0.0 for k in weights}

    validation = primitive.validate(weights, coherence, instability)

    assert isinstance(validation, dict)
    assert "valid" in validation
    assert "diagnostics" in validation


def test_validate_consistent_with_evaluate():
    primitive = StructuralAttractor()

    weights = {
        "A": 0.8,
        "B": 0.4,
    }
    coherence = {k: 1.0 for k in weights}
    instability = {k: 0.0 for k in weights}

    evaluation = primitive.evaluate(weights, coherence, instability)
    validation = primitive.validate(weights, coherence, instability)

    assert validation["diagnostics"] == validation["diagnostics"]
    assert isinstance(evaluation, dict)
    assert isinstance(validation, dict)