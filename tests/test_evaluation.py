"""
Unit tests for EVALUATION.
"""

from ontology.evaluation import Evaluation, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "EVALUATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Evaluation()
    result = primitive.evaluate()
    assert abs(result["evaluation_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "EVALUATION"


def test_nominal_case():
    primitive = Evaluation()
    result = primitive.evaluate(
        value_formation=0.85,
        preference=0.80,
        decision_making=0.75,
        intentionality=0.90,
    )
    assert 0.0 <= result["evaluation_index"] <= 1.0
    assert result["evaluation_index"] > 0.0


def test_negative_case():
    primitive = Evaluation()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["evaluation_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Evaluation()
    result = primitive.evaluate(
        value_formation=2.0,
        preference=-1.0,
        decision_making=10.0,
        intentionality=5.0,
    )
    assert 0.0 <= result["criterion_application"] <= 1.0
    assert 0.0 <= result["outcome_assessment"] <= 1.0
    assert 0.0 <= result["judgment_consistency"] <= 1.0
    assert 0.0 <= result["evaluation_index"] <= 1.0


def test_step_consistency():
    primitive = Evaluation()
    kwargs = dict(
        value_formation=0.7,
        preference=0.8,
        decision_making=0.6,
        intentionality=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)
    assert abs(evaluated["evaluation_index"] - stepped["evaluation_index"]) < 1e-12


def test_validate_consistency():
    primitive = Evaluation()
    kwargs = dict(
        value_formation=0.7,
        preference=0.8,
        decision_making=0.6,
        intentionality=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)
    assert validated["valid"] == (evaluated["evaluation_index"] > 0.0)
    assert abs(
        evaluated["evaluation_index"] - validated["evaluation_index"]
    ) < 1e-12
