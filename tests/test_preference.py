"""
Unit tests for PREFERENCE.
"""

from ontology.preference import Preference, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "PREFERENCE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Preference()
    result = primitive.evaluate()
    assert abs(result["preference_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "PREFERENCE"


def test_nominal_case():
    primitive = Preference()
    result = primitive.evaluate(
        decision_making=0.85,
        choice=0.80,
        intentionality=0.75,
        goal_directedness=0.90,
    )
    assert 0.0 <= result["preference_index"] <= 1.0
    assert result["preference_index"] > 0.0


def test_negative_case():
    primitive = Preference()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["preference_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Preference()
    result = primitive.evaluate(
        decision_making=2.0,
        choice=-1.0,
        intentionality=10.0,
        goal_directedness=5.0,
    )
    assert 0.0 <= result["comparative_valuation"] <= 1.0
    assert 0.0 <= result["ranking_stability"] <= 1.0
    assert 0.0 <= result["selection_bias"] <= 1.0
    assert 0.0 <= result["preference_index"] <= 1.0


def test_step_consistency():
    primitive = Preference()
    kwargs = dict(
        decision_making=0.7,
        choice=0.8,
        intentionality=0.6,
        goal_directedness=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)
    assert abs(evaluated["preference_index"] - stepped["preference_index"]) < 1e-12


def test_validate_consistency():
    primitive = Preference()
    kwargs = dict(
        decision_making=0.7,
        choice=0.8,
        intentionality=0.6,
        goal_directedness=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)
    assert validated["valid"] == (evaluated["preference_index"] > 0.0)
    assert abs(evaluated["preference_index"] - validated["preference_index"]) < 1e-12
