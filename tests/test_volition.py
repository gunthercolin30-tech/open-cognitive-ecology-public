"""
Unit tests for VOLITION.
"""

from ontology.volition import Volition, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "VOLITION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Volition()
    result = primitive.evaluate()
    assert abs(result["volition_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Volition()
    result = primitive.evaluate(
        self_determination=0.85,
        autonomy=0.80,
        agency=0.75,
        goal_directedness=0.90,
    )
    assert 0.0 <= result["volition_index"] <= 1.0
    assert result["volition_index"] > 0.0


def test_negative_case():
    primitive = Volition()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["volition_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Volition()
    result = primitive.evaluate(
        self_determination=2.0,
        autonomy=-1.0,
        agency=10.0,
        goal_directedness=5.0,
    )
    assert 0.0 <= result["volition_index"] <= 1.0


def test_step_consistency():
    primitive = Volition()
    kwargs = dict(
        self_determination=0.7,
        autonomy=0.8,
        agency=0.6,
        goal_directedness=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.step(**kwargs)
    assert abs(a["volition_index"] - b["volition_index"]) < 1e-12


def test_validate_consistency():
    primitive = Volition()
    kwargs = dict(
        self_determination=0.7,
        autonomy=0.8,
        agency=0.6,
        goal_directedness=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.validate(**kwargs)
    assert b["valid"] == (a["volition_index"] > 0.0)
    assert abs(a["volition_index"] - b["volition_index"]) < 1e-12
