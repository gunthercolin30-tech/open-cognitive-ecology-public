"""
Unit tests for AUTONOMY.
"""

from ontology.autonomy import Autonomy, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "AUTONOMY"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Autonomy()
    result = primitive.evaluate(external_dependence=1.0)
    assert abs(result["autonomy_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Autonomy()
    result = primitive.evaluate(
        agency=0.8,
        reflexive_threshold=0.7,
        indispensability_index=0.6,
        external_dependence=0.2,
        goal_directedness=0.9,
    )
    assert 0.0 <= result["autonomy_index"] <= 1.0
    assert result["autonomy_index"] > 0.0


def test_negative_case():
    primitive = Autonomy()
    result = primitive.validate(
        agency=0.0,
        reflexive_threshold=0.0,
        indispensability_index=0.0,
        external_dependence=1.0,
        goal_directedness=0.0,
    )
    assert result["valid"] is False
    assert abs(result["autonomy_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Autonomy()
    result = primitive.evaluate(
        agency=2.0,
        reflexive_threshold=-1.0,
        indispensability_index=3.0,
        external_dependence=-5.0,
        goal_directedness=10.0,
    )
    assert 0.0 <= result["autonomy_index"] <= 1.0


def test_step_consistency():
    primitive = Autonomy()
    kwargs = dict(
        agency=0.7,
        reflexive_threshold=0.8,
        indispensability_index=0.6,
        external_dependence=0.3,
        goal_directedness=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.step(**kwargs)
    assert abs(a["autonomy_index"] - b["autonomy_index"]) < 1e-12


def test_validate_consistency():
    primitive = Autonomy()
    kwargs = dict(
        agency=0.7,
        reflexive_threshold=0.8,
        indispensability_index=0.6,
        external_dependence=0.3,
        goal_directedness=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.validate(**kwargs)
    assert b["valid"] == (a["autonomy_index"] > 0.0)
    assert abs(a["autonomy_index"] - b["autonomy_index"]) < 1e-12
