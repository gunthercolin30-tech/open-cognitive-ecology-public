"""
Unit tests for VALUE_FORMATION.
"""

from ontology.value_formation import (
    ValueFormation,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_metadata():
    assert PRIMITIVE_NAME == "VALUE_FORMATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ValueFormation()
    result = primitive.evaluate()
    assert abs(result["value_formation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "VALUE_FORMATION"


def test_nominal_case():
    primitive = ValueFormation()
    result = primitive.evaluate(
        preference=0.85,
        intentionality=0.80,
        self_determination=0.75,
        autonomy=0.90,
    )
    assert 0.0 <= result["value_formation_index"] <= 1.0
    assert result["value_formation_index"] > 0.0


def test_negative_case():
    primitive = ValueFormation()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["value_formation_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = ValueFormation()
    result = primitive.evaluate(
        preference=2.0,
        intentionality=-1.0,
        self_determination=10.0,
        autonomy=5.0,
    )
    assert 0.0 <= result["importance_assignment"] <= 1.0
    assert 0.0 <= result["criterion_stability"] <= 1.0
    assert 0.0 <= result["valuation_coherence"] <= 1.0
    assert 0.0 <= result["value_formation_index"] <= 1.0


def test_step_consistency():
    primitive = ValueFormation()
    kwargs = dict(
        preference=0.7,
        intentionality=0.8,
        self_determination=0.6,
        autonomy=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)
    assert abs(
        evaluated["value_formation_index"] - stepped["value_formation_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ValueFormation()
    kwargs = dict(
        preference=0.7,
        intentionality=0.8,
        self_determination=0.6,
        autonomy=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)
    assert validated["valid"] == (evaluated["value_formation_index"] > 0.0)
    assert abs(
        evaluated["value_formation_index"] - validated["value_formation_index"]
    ) < 1e-12
