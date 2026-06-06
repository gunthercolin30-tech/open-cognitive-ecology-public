from ontology.selective_pressure import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    SelectivePressure,
)


def test_metadata():
    assert PRIMITIVE_NAME == "SELECTIVE_PRESSURE"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = SelectivePressure()
    result = primitive.evaluate()

    assert abs(result["selection_intensity"] - 0.0) < 1e-12
    assert abs(result["retention_probability"] - 0.0) < 1e-12
    assert result["diagnostics"]["status"] == "neutral"


def test_nominal_case():
    primitive = SelectivePressure(
        environmental_constraint=0.8,
        fitness_gradient=0.4,
        viability_margin=0.6,
    )
    result = primitive.evaluate()

    expected_selection = 0.6
    expected_retention = 0.6

    assert abs(result["selection_intensity"] - expected_selection) < 1e-12
    assert abs(result["retention_probability"] - expected_retention) < 1e-12
    assert abs(result["adaptive_bias"] - expected_selection) < 1e-12
    assert result["diagnostics"]["status"] == "selective"


def test_negative_inputs_are_clamped():
    primitive = SelectivePressure(
        environmental_constraint=-1.0,
        fitness_gradient=-1.0,
        viability_margin=-1.0,
    )
    result = primitive.evaluate()

    assert abs(result["selection_intensity"] - 0.0) < 1e-12
    assert abs(result["retention_probability"] - 0.0) < 1e-12


def test_values_are_bounded():
    primitive = SelectivePressure(
        environmental_constraint=10.0,
        fitness_gradient=10.0,
        viability_margin=10.0,
    )
    result = primitive.evaluate()

    for key in (
        "selection_intensity",
        "fitness_gradient",
        "retention_probability",
        "adaptive_bias",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_step_matches_evaluate():
    primitive = SelectivePressure(
        environmental_constraint=0.7,
        fitness_gradient=0.5,
        viability_margin=0.3,
    )

    evaluate_result = primitive.evaluate()
    step_result = primitive.step()

    for key in (
        "selection_intensity",
        "fitness_gradient",
        "retention_probability",
        "adaptive_bias",
    ):
        assert abs(step_result[key] - evaluate_result[key]) < 1e-12


def test_validate_consistency():
    primitive = SelectivePressure(
        environmental_constraint=0.9,
        fitness_gradient=0.2,
        viability_margin=0.8,
    )

    evaluation = primitive.evaluate()
    validation = primitive.validate()

    assert validation["valid"] is True
    assert (
        abs(
            validation["selection_intensity"]
            - evaluation["selection_intensity"]
        )
        < 1e-12
    )
