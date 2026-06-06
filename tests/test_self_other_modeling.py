
from ontology.self_other_modeling import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    SelfOtherModeling,
)


def test_metadata():
    assert PRIMITIVE_NAME == "SELF_OTHER_MODELING"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SelfOtherModeling()
    result = primitive.evaluate({})
    assert abs(result["self_other_modeling_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = SelfOtherModeling()
    state = {
        "self_other_boundary": 0.8,
        "intention_inference": 0.6,
        "belief_inference": 0.8,
        "perspective_switching": 0.7,
    }

    result = primitive.evaluate(state)

    expected_attribution = 0.7
    expected_index = (0.8 + 0.7 + 0.7) / 3.0

    assert abs(result["agent_differentiation"] - 0.8) < 1e-12
    assert abs(result["mental_state_attribution"] - expected_attribution) < 1e-12
    assert abs(result["perspective_projection"] - 0.7) < 1e-12
    assert abs(result["self_other_modeling_index"] - expected_index) < 1e-12


def test_negative_case():
    primitive = SelfOtherModeling()
    state = {
        "self_other_boundary": 0.1,
        "intention_inference": 0.0,
        "belief_inference": 0.0,
        "perspective_switching": 0.1,
    }

    result = primitive.evaluate(state)
    assert result["self_other_modeling_index"] < 0.5


def test_bounding():
    primitive = SelfOtherModeling()
    state = {
        "self_other_boundary": 2.0,
        "intention_inference": -1.0,
        "belief_inference": 4.0,
        "perspective_switching": 10.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "agent_differentiation",
        "mental_state_attribution",
        "perspective_projection",
        "self_other_modeling_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = SelfOtherModeling()
    state = {
        "self_other_boundary": 0.7,
        "intention_inference": 0.6,
        "belief_inference": 0.9,
        "perspective_switching": 0.8,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["self_other_modeling_index"]
        - step_result["self_other_modeling_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = SelfOtherModeling()
    state = {
        "self_other_boundary": 0.9,
        "intention_inference": 0.9,
        "belief_inference": 0.9,
        "perspective_switching": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["self_other_modeling_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
