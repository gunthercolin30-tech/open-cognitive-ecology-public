from ontology.intersubjective_alignment import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    IntersubjectiveAlignment,
)


def test_metadata():
    assert PRIMITIVE_NAME == "INTERSUBJECTIVE_ALIGNMENT"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = IntersubjectiveAlignment()
    result = primitive.evaluate({})
    assert abs(result["intersubjective_alignment_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = IntersubjectiveAlignment()
    state = {
        "model_similarity": 0.8,
        "semantic_overlap": 0.6,
        "expectation_matching": 0.9,
        "reference_consistency": 0.7,
    }

    result = primitive.evaluate(state)

    expected_overlap = 0.7
    expected_index = (0.7 + 0.9 + 0.7) / 3.0

    assert abs(result["representational_overlap"] - expected_overlap) < 1e-12
    assert abs(result["expectation_coordination"] - 0.9) < 1e-12
    assert abs(result["shared_reference_stability"] - 0.7) < 1e-12
    assert abs(
        result["intersubjective_alignment_index"] - expected_index
    ) < 1e-12


def test_negative_case():
    primitive = IntersubjectiveAlignment()
    state = {
        "model_similarity": 0.1,
        "semantic_overlap": 0.0,
        "expectation_matching": 0.1,
        "reference_consistency": 0.0,
    }

    result = primitive.evaluate(state)
    assert result["intersubjective_alignment_index"] < 0.5


def test_bounding():
    primitive = IntersubjectiveAlignment()
    state = {
        "model_similarity": 5.0,
        "semantic_overlap": -2.0,
        "expectation_matching": 10.0,
        "reference_consistency": -1.0,
    }

    result = primitive.evaluate(state)

    for key in (
        "representational_overlap",
        "expectation_coordination",
        "shared_reference_stability",
        "intersubjective_alignment_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = IntersubjectiveAlignment()
    state = {
        "model_similarity": 0.7,
        "semantic_overlap": 0.8,
        "expectation_matching": 0.6,
        "reference_consistency": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert abs(
        evaluate_result["intersubjective_alignment_index"]
        - step_result["intersubjective_alignment_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = IntersubjectiveAlignment()
    state = {
        "model_similarity": 0.9,
        "semantic_overlap": 0.9,
        "expectation_matching": 0.9,
        "reference_consistency": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert abs(
        evaluate_result["intersubjective_alignment_index"]
        - validate_result["value"]
    ) < 1e-12
    assert validate_result["is_valid"] is True
