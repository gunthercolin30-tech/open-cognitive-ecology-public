"""
Unit tests for COMMITMENT.
"""

from ontology.commitment import Commitment, PRIMITIVE_NAME, MATURITY_LEVEL


def test_metadata():
    assert PRIMITIVE_NAME == "COMMITMENT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Commitment()
    result = primitive.evaluate()
    assert abs(result["commitment_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == "COMMITMENT"


def test_nominal_case():
    primitive = Commitment()
    result = primitive.evaluate(
        choice=0.85,
        volition=0.80,
        goal_directedness=0.90,
        structural_continuity=0.75,
    )
    assert 0.0 <= result["commitment_index"] <= 1.0
    assert result["commitment_index"] > 0.0


def test_negative_case():
    primitive = Commitment()
    result = primitive.validate()
    assert result["valid"] is False
    assert abs(result["commitment_index"] - 0.0) < 1e-12


def test_clamping():
    primitive = Commitment()
    result = primitive.evaluate(
        choice=2.0,
        volition=-1.0,
        goal_directedness=10.0,
        structural_continuity=5.0,
    )
    assert 0.0 <= result["decision_lock_in"] <= 1.0
    assert 0.0 <= result["trajectory_persistence"] <= 1.0
    assert 0.0 <= result["resistance_to_reversal"] <= 1.0
    assert 0.0 <= result["commitment_index"] <= 1.0


def test_step_consistency():
    primitive = Commitment()
    kwargs = dict(
        choice=0.7,
        volition=0.8,
        goal_directedness=0.6,
        structural_continuity=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    stepped = primitive.step(**kwargs)
    assert abs(evaluated["commitment_index"] - stepped["commitment_index"]) < 1e-12


def test_validate_consistency():
    primitive = Commitment()
    kwargs = dict(
        choice=0.7,
        volition=0.8,
        goal_directedness=0.6,
        structural_continuity=0.9,
    )
    evaluated = primitive.evaluate(**kwargs)
    validated = primitive.validate(**kwargs)
    assert validated["valid"] == (evaluated["commitment_index"] > 0.0)
    assert abs(evaluated["commitment_index"] - validated["commitment_index"]) < 1e-12
