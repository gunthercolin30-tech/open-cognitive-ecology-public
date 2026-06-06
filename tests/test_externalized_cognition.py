from ontology.externalized_cognition import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    ExternalizedCognition,
)


def test_metadata():
    assert PRIMITIVE_NAME == "EXTERNALIZED_COGNITION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = ExternalizedCognition()
    result = primitive.evaluate({})
    assert abs(result["externalized_cognition_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = ExternalizedCognition()
    state = {
        "storage_reliance": 0.8,
        "inference_assistance": 0.6,
        "workflow_support": 0.9,
        "collaboration_enablement": 0.7,
    }

    result = primitive.evaluate(state)

    expected_coordination = 0.8
    expected_index = (0.8 + 0.6 + 0.8) / 3.0

    assert abs(result["memory_offloading"] - 0.8) < 1e-12
    assert abs(result["reasoning_delegation"] - 0.6) < 1e-12
    assert abs(result["coordination_support"] - expected_coordination) < 1e-12
    assert abs(
        result["externalized_cognition_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = ExternalizedCognition()
    state = {
        "storage_reliance": 0.1,
        "inference_assistance": 0.0,
        "workflow_support": 0.1,
        "collaboration_enablement": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["externalized_cognition_index"] < 0.5


def test_bounding():
    primitive = ExternalizedCognition()
    state = {
        "storage_reliance": 5.0,
        "inference_assistance": -2.0,
        "workflow_support": 10.0,
        "collaboration_enablement": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "memory_offloading",
        "reasoning_delegation",
        "coordination_support",
        "externalized_cognition_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = ExternalizedCognition()
    state = {
        "storage_reliance": 0.7,
        "inference_assistance": 0.8,
        "workflow_support": 0.6,
        "collaboration_enablement": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["externalized_cognition_index"]
        - step_result["externalized_cognition_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = ExternalizedCognition()
    state = {
        "storage_reliance": 0.9,
        "inference_assistance": 0.9,
        "workflow_support": 0.9,
        "collaboration_enablement": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["externalized_cognition_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
