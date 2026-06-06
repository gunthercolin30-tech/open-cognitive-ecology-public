"""
Unit tests for DECISION_MAKING.
"""

from ontology.decision_making import (
    DecisionMaking,
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
)


def test_metadata():
    assert PRIMITIVE_NAME == "DECISION_MAKING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = DecisionMaking()
    result = primitive.evaluate()
    assert abs(result["decision_making_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = DecisionMaking()
    result = primitive.evaluate(
        intentionality=0.85,
        volition=0.80,
        agency=0.75,
        controllability=0.90,
    )
    assert 0.0 <= result["decision_making_index"] <= 1.0
    assert result["decision_making_index"] > 0.0


def test_negative_case():
    primitive = DecisionMaking()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["decision_making_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = DecisionMaking()
    result = primitive.evaluate(
        intentionality=2.0,
        volition=-1.0,
        agency=10.0,
        controllability=5.0,
    )
    assert 0.0 <= result["decision_making_index"] <= 1.0


def test_step_consistency():
    primitive = DecisionMaking()
    kwargs = dict(
        intentionality=0.7,
        volition=0.8,
        agency=0.6,
        controllability=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.step(**kwargs)
    assert abs(a["decision_making_index"] - b["decision_making_index"]) < 1e-12


def test_validate_consistency():
    primitive = DecisionMaking()
    kwargs = dict(
        intentionality=0.7,
        volition=0.8,
        agency=0.6,
        controllability=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.validate(**kwargs)
    assert b["valid"] == (a["decision_making_index"] > 0.0)
    assert abs(a["decision_making_index"] - b["decision_making_index"]) < 1e-12
