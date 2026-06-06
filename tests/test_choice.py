"""
Unit tests for CHOICE.
"""

from ontology.choice import Choice, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "CHOICE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Choice()
    result = primitive.evaluate()
    assert abs(result["choice_index"] - 0.0) < 1e-12


def test_nominal_case():
    primitive = Choice()
    result = primitive.evaluate(
        decision_making=0.85,
        volition=0.80,
        intentionality=0.75,
        reachability=0.90,
    )
    assert 0.0 <= result["choice_index"] <= 1.0
    assert result["choice_index"] > 0.0


def test_negative_case():
    primitive = Choice()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["choice_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Choice()
    result = primitive.evaluate(
        decision_making=2.0,
        volition=-1.0,
        intentionality=10.0,
        reachability=5.0,
    )
    assert 0.0 <= result["choice_index"] <= 1.0


def test_step_consistency():
    primitive = Choice()
    kwargs = dict(
        decision_making=0.7,
        volition=0.8,
        intentionality=0.6,
        reachability=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.step(**kwargs)
    assert abs(a["choice_index"] - b["choice_index"]) < 1e-12


def test_validate_consistency():
    primitive = Choice()
    kwargs = dict(
        decision_making=0.7,
        volition=0.8,
        intentionality=0.6,
        reachability=0.9,
    )
    a = primitive.evaluate(**kwargs)
    b = primitive.validate(**kwargs)
    assert b["valid"] == (a["choice_index"] > 0.0)
    assert abs(a["choice_index"] - b["choice_index"]) < 1e-12
