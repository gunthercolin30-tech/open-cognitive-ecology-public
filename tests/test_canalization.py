from ontology.canalization import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    Canalization,
)


def test_metadata():
    assert PRIMITIVE_NAME == "CANALIZATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = Canalization()
    result = primitive.evaluate()

    assert abs(result["canalization_strength"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "labile"


def test_nominal_case():
    primitive = Canalization(
        perturbation_buffering=0.8,
        trajectory_guidance=0.6,
        developmental_robustness=0.7,
    )
    result = primitive.evaluate()

    expected = (0.8 + 0.6 + 0.7) / 3.0

    assert abs(result["canalization_strength"] - expected) < 1e-12
    assert result["diagnostics"]["status"] == "canalized"


def test_negative_inputs_are_clamped():
    primitive = Canalization(
        perturbation_buffering=-1.0,
        trajectory_guidance=-2.0,
        developmental_robustness=-3.0,
    )
    result = primitive.evaluate()

    assert abs(result["canalization_strength"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = Canalization(
        perturbation_buffering=10.0,
        trajectory_guidance=10.0,
        developmental_robustness=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "perturbation_buffering",
        "trajectory_guidance",
        "developmental_robustness",
        "canalization_strength",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = Canalization(
        perturbation_buffering=0.4,
        trajectory_guidance=0.5,
        developmental_robustness=0.9,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "perturbation_buffering",
        "trajectory_guidance",
        "developmental_robustness",
        "canalization_strength",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = Canalization(
        perturbation_buffering=0.7,
        trajectory_guidance=0.8,
        developmental_robustness=0.6,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["canalization_strength"]
            - evaluation["canalization_strength"]
        )
        < 1e-12
    )
