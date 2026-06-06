from ontology.free_energy_minimization import (
    PRIMITIVE_NAME,
    MATURITY_LEVEL,
    FreeEnergyMinimization,
)


def test_metadata():
    assert PRIMITIVE_NAME == "FREE_ENERGY_MINIMIZATION"
    assert MATURITY_LEVEL == "FOUNDATIONAL_COMPLETE"


def test_empty_input():
    primitive = FreeEnergyMinimization()
    result = primitive.evaluate(0.0, 0.0, 0.0)

    assert abs(
        result["free_energy_minimization_index"] - 0.0
    ) < 1e-12
    assert result["diagnostics"]["status"] == "empty_input"


def test_nominal_case():
    primitive = FreeEnergyMinimization()

    result = primitive.evaluate(
        0.9,
        0.8,
        0.7,
    )

    assert 0.0 <= result["prediction_accuracy"] <= 1.0
    assert 0.0 <= result["model_evidence"] <= 1.0
    assert 0.0 <= result["uncertainty_reduction"] <= 1.0
    assert 0.0 <= result["free_energy_minimization_index"] <= 1.0
    assert result["diagnostics"]["status"] == "evaluated"


def test_negative_case():
    primitive = FreeEnergyMinimization()

    result = primitive.evaluate(
        0.0,
        0.0,
        0.0,
    )

    assert abs(
        result["free_energy_minimization_index"] - 0.0
    ) < 1e-12


def test_bounding():
    primitive = FreeEnergyMinimization()

    result = primitive.evaluate(
        5.0,
        -2.0,
        3.0,
    )

    assert (
        0.0
        <= result["free_energy_minimization_index"]
        <= 1.0
    )


def test_step_consistency():
    primitive = FreeEnergyMinimization()

    a = primitive.evaluate(0.8, 0.7, 0.9)
    b = primitive.step(0.8, 0.7, 0.9)

    assert abs(
        a["free_energy_minimization_index"]
        - b["free_energy_minimization_index"]
    ) < 1e-12


def test_validate_consistency():
    primitive = FreeEnergyMinimization()

    evaluation = primitive.evaluate(0.8, 0.7, 0.9)
    validation = primitive.validate(0.8, 0.7, 0.9)

    assert abs(
        evaluation["free_energy_minimization_index"]
        - validation["free_energy_minimization_index"]
    ) < 1e-12
    assert validation["is_valid"] is True
