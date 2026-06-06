from ontology.long_term_coordination import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    LongTermCoordination,
)


def test_metadata():
    assert PRIMITIVE_NAME == "LONG_TERM_COORDINATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = LongTermCoordination()
    result = primitive.evaluate({})
    assert abs(result["long_term_coordination_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = LongTermCoordination()
    state = {
        "agreement_durability": 0.8,
        "succession_fidelity": 0.6,
        "strategic_consistency": 0.9,
        "institutional_follow_through": 0.7,
    }

    result = primitive.evaluate(state)

    expected_continuity = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(result["commitment_stability"] - 0.8) < 1e-12
    assert abs(result["intergenerational_alignment"] - 0.6) < 1e-12
    assert abs(result["planning_continuity"] - expected_continuity) < 1e-12
    assert abs(
        result["long_term_coordination_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = LongTermCoordination()
    state = {
        "agreement_durability": 0.1,
        "succession_fidelity": 0.0,
        "strategic_consistency": 0.1,
        "institutional_follow_through": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["long_term_coordination_index"] < 0.5


def test_bounding():
    primitive = LongTermCoordination()
    state = {
        "agreement_durability": 5.0,
        "succession_fidelity": -2.0,
        "strategic_consistency": 10.0,
        "institutional_follow_through": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "commitment_stability",
        "intergenerational_alignment",
        "planning_continuity",
        "long_term_coordination_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = LongTermCoordination()
    state = {
        "agreement_durability": 0.7,
        "succession_fidelity": 0.8,
        "strategic_consistency": 0.6,
        "institutional_follow_through": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["long_term_coordination_index"]
        - step_result["long_term_coordination_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = LongTermCoordination()
    state = {
        "agreement_durability": 0.9,
        "succession_fidelity": 0.9,
        "strategic_consistency": 0.9,
        "institutional_follow_through": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["long_term_coordination_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
