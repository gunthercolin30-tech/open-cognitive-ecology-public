"""
Unit tests for PRIORITIZATION.
"""

from ontology.prioritization import (
    Prioritization,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_metadata():
    assert PRIMITIVE_NAME == "PRIORITIZATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Prioritization()
    result = primitive.evaluate()
    assert abs(result["prioritization_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "PRIORITIZATION"


def test_nominal_case():
    primitive = Prioritization()
    result = primitive.evaluate(
        evaluation=0.85,
        preference=0.80,
        decision_making=0.75,
        commitment=0.90,
    )
    assert 0.0 <= result["prioritization_index"] <= 1.0
    assert result["prioritization_index"] > 0.0


def test_negative_case():
    primitive = Prioritization()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["prioritization_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Prioritization()
    result = primitive.evaluate(
        evaluation=2.0,
        preference=-1.0,
        decision_making=10.0,
        commitment=5.0,
    )
    assert 0.0 <= result["importance_ordering"] <= 1.0
    assert 0.0 <= result["resource_focus"] <= 1.0
    assert 0.0 <= result["ranking_commitment"] <= 1.0
    assert 0.0 <= result["prioritization_index"] <= 1.0


def test_step_consistency():
    primitive = Prioritization()
    kwargs = dict(
        evaluation=0.7,
        preference=0.8,
        decision_making=0.6,
        commitment=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)
    assert abs(
        evaluated["prioritization_index"] - stepped["prioritization_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = Prioritization()
    kwargs = dict(
        evaluation=0.7,
        preference=0.8,
        decision_making=0.6,
        commitment=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)
    assert validated["valid"] == (evaluated["prioritization_index"] > 0.0)
    assert abs(
        evaluated["prioritization_index"] - validated["prioritization_index"]
    ) < 1e-12
