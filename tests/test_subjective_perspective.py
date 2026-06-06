from ontology.subjective_perspective import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    SubjectivePerspective,
)


def test_metadata():
    assert PRIMITIVE_NAME == "SUBJECTIVE_PERSPECTIVE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SubjectivePerspective()
    result = primitive.evaluate({})
    assert abs(result["subjective_perspective_index"] - 0.0) < 1e-12
    assert result["diagnostics"]["primitive"] == PRIMITIVE_NAME


def test_nominal_case():
    primitive = SubjectivePerspective()
    state = {
        "self_model_coherence": 0.8,
        "conscious_access": 0.9,
        "self_world_boundary": 0.7,
        "experiential_binding": 0.6,
    }
    result = primitive.evaluate(state)

    expected_centering = 0.85
    expected_unity = 0.75
    expected_index = (0.85 + 0.7 + 0.75) / 3.0

    assert abs(result["perspective_centering"] - expected_centering) < 1e-12
    assert abs(result["experiential_unity"] - expected_unity) < 1e-12
    assert abs(result["subjective_perspective_index"] - expected_index) < 1e-12


def test_negative_case():
    primitive = SubjectivePerspective()
    state = {
        "self_model_coherence": 0.1,
        "conscious_access": 0.1,
        "self_world_boundary": 0.0,
        "experiential_binding": 0.0,
    }
    result = primitive.evaluate(state)
    assert result["subjective_perspective_index"] < 0.5


def test_bounding():
    primitive = SubjectivePerspective()
    state = {
        "self_model_coherence": 2.0,
        "conscious_access": -1.0,
        "self_world_boundary": 3.0,
        "experiential_binding": 5.0,
    }
    result = primitive.evaluate(state)

    for key in (
        "perspective_centering",
        "self_world_differentiation",
        "experiential_unity",
        "subjective_perspective_index",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_consistency():
    primitive = SubjectivePerspective()
    state = {
        "self_model_coherence": 0.7,
        "conscious_access": 0.8,
        "self_world_boundary": 0.9,
        "experiential_binding": 0.6,
    }
    evaluate_result = primitive.evaluate(state)
    step_result = primitive.step(state)

    assert (
        abs(
            evaluate_result["subjective_perspective_index"]
            - step_result["subjective_perspective_index"]
        )
        < 1e-12
    )


def test_validate_consistency():
    primitive = SubjectivePerspective()
    state = {
        "self_model_coherence": 0.9,
        "conscious_access": 0.9,
        "self_world_boundary": 0.9,
        "experiential_binding": 0.9,
    }

    evaluate_result = primitive.evaluate(state)
    validate_result = primitive.validate(state)

    assert (
        abs(
            evaluate_result["subjective_perspective_index"]
            - validate_result["value"]
        )
        < 1e-12
    )
    assert validate_result["is_valid"] is True
