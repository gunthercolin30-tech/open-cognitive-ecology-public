"""
Unit tests for SELF_DETERMINATION.
"""

from ontology.self_determination import (
    SelfDetermination,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_metadata():
    assert PRIMITIVE_NAME == "SELF_DETERMINATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SelfDetermination()
    result = primitive.evaluate()
    assert abs(result["self_determination_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = SelfDetermination()
    result = primitive.evaluate(
        autonomy=0.8,
        agency=0.7,
        reflexive_threshold=0.9,
        goal_directedness=0.85,
    )
    assert 0.0 <= result["self_determination_index"] <= 1.0
    assert result["self_determination_index"] > 0.0


def test_negative_case():
    primitive = SelfDetermination()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["self_determination_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = SelfDetermination()
    result = primitive.evaluate(
        autonomy=2.0,
        agency=-1.0,
        reflexive_threshold=10.0,
        goal_directedness=5.0,
    )
    assert 0.0 <= result["self_determination_index"] <= 1.0


def test_step_consistency():
    primitive = SelfDetermination()
    kwargs = dict(
        autonomy=0.7,
        agency=0.6,
        reflexive_threshold=0.8,
        goal_directedness=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.step(**kwargs)
    assert abs(a["self_determination_index"] - b["self_determination_index"]) < 1e-12


def test_validate_consistency():
    primitive = SelfDetermination()
    kwargs = dict(
        autonomy=0.7,
        agency=0.6,
        reflexive_threshold=0.8,
        goal_directedness=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.validate(**kwargs)
    assert b["valid"] == (a["self_determination_index"] > 0.0)
    assert abs(a["self_determination_index"] - b["self_determination_index"]) < 1e-12
