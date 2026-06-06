from ontology.epistemic_infrastructure import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    EpistemicInfrastructure,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EPISTEMIC_INFRASTRUCTURE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = EpistemicInfrastructure()
    result = primitive.evaluate({})
    assert abs(result["epistemic_infrastructure_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = EpistemicInfrastructure()
    state = {
        "research_capacity": 0.8,
        "peer_review_integrity": 0.6,
        "archive_accessibility": 0.9,
        "communication_reach": 0.7,
    }

    result = primitive.evaluate(state)

    expected_dissemination = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(
        result["knowledge_production_capacity"] - 0.8
    ) < 1e-12
    assert abs(result["validation_reliability"] - 0.6) < 1e-12
    assert abs(
        result["dissemination_efficiency"] - expected_dissemination
    ) < 1e-12
    assert abs(
        result["epistemic_infrastructure_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = EpistemicInfrastructure()
    state = {
        "research_capacity": 0.1,
        "peer_review_integrity": 0.0,
        "archive_accessibility": 0.1,
        "communication_reach": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["epistemic_infrastructure_index"] < 0.5


def test_bounding():
    primitive = EpistemicInfrastructure()
    state = {
        "research_capacity": 5.0,
        "peer_review_integrity": -2.0,
        "archive_accessibility": 10.0,
        "communication_reach": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "knowledge_production_capacity",
        "validation_reliability",
        "dissemination_efficiency",
        "epistemic_infrastructure_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = EpistemicInfrastructure()
    state = {
        "research_capacity": 0.7,
        "peer_review_integrity": 0.8,
        "archive_accessibility": 0.6,
        "communication_reach": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["epistemic_infrastructure_index"]
        - step_result["epistemic_infrastructure_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = EpistemicInfrastructure()
    state = {
        "research_capacity": 0.9,
        "peer_review_integrity": 0.9,
        "archive_accessibility": 0.9,
        "communication_reach": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["epistemic_infrastructure_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
