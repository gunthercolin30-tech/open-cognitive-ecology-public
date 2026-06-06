"""
Unit tests for INTENTIONALITY.
"""

from ontology.intentionality import (
    Intentionality,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_metadata():
    assert PRIMITIVE_NAME == "INTENTIONALITY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Intentionality()
    result = primitive.evaluate()
    assert abs(result["intentionality_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Intentionality()
    result = primitive.evaluate(
        volition=0.85,
        goal_directedness=0.90,
        observability=0.70,
        reflexive_threshold=0.80,
    )
    assert 0.0 <= result["intentionality_index"] <= 1.0
    assert result["intentionality_index"] > 0.0


def test_negative_case():
    primitive = Intentionality()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["intentionality_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Intentionality()
    result = primitive.evaluate(
        volition=2.0,
        goal_directedness=5.0,
        observability=-1.0,
        reflexive_threshold=10.0,
    )
    assert 0.0 <= result["intentionality_index"] <= 1.0


def test_step_consistency():
    primitive = Intentionality()
    kwargs = dict(
        volition=0.7,
        goal_directedness=0.8,
        observability=0.6,
        reflexive_threshold=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.step(**kwargs)
    assert abs(a["intentionality_index"] - b["intentionality_index"]) < 1e-12


def test_validate_consistency():
    primitive = Intentionality()
    kwargs = dict(
        volition=0.7,
        goal_directedness=0.8,
        observability=0.6,
        reflexive_threshold=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.validate(**kwargs)
    assert b["valid"] == (a["intentionality_index"] > 0.0)
    assert abs(a["intentionality_index"] - b["intentionality_index"]) < 1e-12
